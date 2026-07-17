import uuid
import traceback
from datetime import datetime, timedelta
from google.cloud.firestore_v1 import FieldFilter
from firebase_admin import firestore
import stripe

try:
    from src.firebase_config import get_db
    from src.calendar_service import create_lesson_event
except ImportError:
    from firebase_config import get_db
    from calendar_service import create_lesson_event


class BookingService:
    def __init__(self):
        self.db = get_db()

    # ── Packages (from Stripe) ──

    def get_packages(self):
        import os
        pid = os.getenv("STRIPE_PRODUCT_ID")
        if not pid:
            return []
        prices = stripe.Price.list(product=pid, active=True, limit=20)
        packages = []
        for p in prices.data:
            try:
                meta = p.metadata.to_dict()
            except Exception:
                meta = {}
            session_count = int(meta.get("session_count", 1))
            packages.append({
                "id": p.id,
                "stripe_price_id": p.id,
                "name": p.nickname or f"{session_count} Session{'s' if session_count != 1 else ''}",
                "session_count": session_count,
                "price_cents": p.unit_amount,
                "currency": p.currency,
                "description": meta.get("description", ""),
            })
        packages.sort(key=lambda pkg: pkg["price_cents"])
        return packages

    # ── Availability (admin-defined recurring windows) ──
    # Each doc: { id, day_of_week (0=Mon..6=Sun), start_time, end_time, duration_minutes, active }

    def get_availability(self):
        docs = self.db.collection("availability").stream()
        items = [doc.to_dict() for doc in docs]
        items.sort(key=lambda a: (a.get("day_of_week", 0), a.get("start_time", "")))
        return items

    def get_active_availability(self):
        docs = (
            self.db.collection("availability")
            .where(filter=FieldFilter("active", "==", True))
            .stream()
        )
        items = [doc.to_dict() for doc in docs]
        items.sort(key=lambda a: (a.get("day_of_week", 0), a.get("start_time", "")))
        return items

    def create_availability(self, day_of_week, start_time, end_time, duration_minutes=60):
        avail_id = str(uuid.uuid4())
        avail = {
            "id": avail_id,
            "day_of_week": day_of_week,
            "start_time": start_time,
            "end_time": end_time,
            "duration_minutes": duration_minutes,
            "active": True,
            "created_at": firestore.SERVER_TIMESTAMP,
        }
        self.db.collection("availability").document(avail_id).set(avail)
        return avail

    def delete_availability(self, avail_id):
        self.db.collection("availability").document(avail_id).delete()

    # ── Generate available slots for a month from availability patterns ──

    def get_available_for_month(self, year, month):
        """Returns list of {date, start_time, end_time, duration_minutes, day_of_week}
        for days that have availability and are NOT fully booked."""
        availability = self.get_active_availability()
        if not availability:
            return []

        # Build a map: day_of_week -> list of time windows
        by_dow = {}
        for a in availability:
            dow = a["day_of_week"]
            if dow not in by_dow:
                by_dow[dow] = []
            by_dow[dow].append(a)

        # Generate all possible dates in the month
        first = datetime(year, month, 1)
        if month == 12:
            last = datetime(year + 1, 1, 1)
        else:
            last = datetime(year, month + 1, 1)

        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        slots = []
        current = first
        while current < last:
            if current >= today:
                dow = current.weekday()
                if dow in by_dow:
                    date_str = current.strftime("%Y-%m-%d")
                    for window in by_dow[dow]:
                        # Split window into individual lesson slots
                        for s_time, e_time in self._split_window(
                            window["start_time"], window["end_time"], window["duration_minutes"]
                        ):
                            slots.append({
                                "date": date_str,
                                "start_time": s_time,
                                "end_time": e_time,
                                "duration_minutes": window["duration_minutes"],
                                "day_of_week": dow,
                                "availability_id": window["id"],
                            })
            current += timedelta(days=1)

        # Remove already-booked slots
        booked = self._get_booked_dates_for_month(year, month)
        slots = [s for s in slots if (s["date"], s["start_time"]) not in booked]

        return slots

    @staticmethod
    def _split_window(start_time, end_time, duration_minutes):
        """Split a time window into individual lesson slots.
        e.g., 15:00-18:00 with 60min -> [(15:00,16:00), (16:00,17:00), (17:00,18:00)]
        """
        sh, sm = map(int, start_time.split(':'))
        eh, em = map(int, end_time.split(':'))
        start_min = sh * 60 + sm
        end_min = eh * 60 + em
        slots = []
        while start_min + duration_minutes <= end_min:
            s = f"{start_min // 60:02d}:{start_min % 60:02d}"
            e_min = start_min + duration_minutes
            e = f"{e_min // 60:02d}:{e_min % 60:02d}"
            slots.append((s, e))
            start_min = e_min
        return slots

    def _get_booked_dates_for_month(self, year, month):
        """Returns set of (date, start_time) that are booked."""
        start = f"{year}-{month:02d}-01"
        if month == 12:
            end = f"{year + 1}-01-01"
        else:
            end = f"{year}-{month + 1:02d}-01"

        docs = (
            self.db.collection("bookings")
            .where(filter=FieldFilter("status", "==", "confirmed"))
            .stream()
        )
        booked = set()
        for doc in docs:
            b = doc.to_dict()
            if start <= b.get("date", "") < end:
                booked.add((b["date"], b["start_time"]))
        return booked

    # ── Users ──

    def create_or_get_user(self, uid, email, display_name=""):
        user_ref = self.db.collection("users").document(uid)
        doc = user_ref.get()
        if doc.exists:
            return doc.to_dict()

        # Create Stripe customer
        stripe_customer_id = None
        try:
            customer = stripe.Customer.create(
                email=email,
                name=display_name or None,
                metadata={"firebase_uid": uid},
            )
            stripe_customer_id = customer.id
        except Exception:
            pass

        user = {
            "uid": uid,
            "email": email,
            "display_name": display_name,
            "stripe_customer_id": stripe_customer_id,
            "sessions_remaining": 0,
            "total_sessions_purchased": 0,
            "created_at": firestore.SERVER_TIMESTAMP,
        }
        user_ref.set(user)
        return user

    def get_user_profile(self, uid):
        doc = self.db.collection("users").document(uid).get()
        return doc.to_dict() if doc.exists else None

    # ── Booking ──

    def book_sessions(self, user_uid, start_time, end_time, duration_minutes, dates, note=""):
        """Book multiple sessions on specific dates at a given time.
        dates: list of date strings like ['2026-07-21', '2026-07-28', ...]
        Deducts len(dates) credits.
        """
        @firestore.transactional
        def _book(transaction, user_ref):
            user_doc = user_ref.get(transaction=transaction)
            if not user_doc.exists:
                raise ValueError("User not found")
            user = user_doc.to_dict()

            needed = len(dates)
            remaining = user.get("sessions_remaining", 0)
            if remaining < needed:
                raise ValueError(f"Not enough credits. Need {needed}, have {remaining}")

            # Check none are already booked
            for date in dates:
                existing = (
                    self.db.collection("bookings")
                    .where(filter=FieldFilter("date", "==", date))
                    .where(filter=FieldFilter("start_time", "==", start_time))
                    .where(filter=FieldFilter("status", "==", "confirmed"))
                    .limit(1)
                    .stream()
                )
                if next(existing, None):
                    raise ValueError(f"Slot on {date} at {start_time} is already booked")

            bookings = []
            for date in dates:
                booking_id = str(uuid.uuid4())
                booking = {
                    "id": booking_id,
                    "user_uid": user_uid,
                    "user_email": user.get("email", ""),
                    "date": date,
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration_minutes": duration_minutes,
                    "note": note,
                    "status": "confirmed",
                    "created_at": firestore.SERVER_TIMESTAMP,
                }
                transaction.set(
                    self.db.collection("bookings").document(booking_id), booking
                )
                bookings.append(booking)

            transaction.update(user_ref, {
                "sessions_remaining": firestore.Increment(-needed),
            })

            for b in bookings:
                b["created_at"] = None
            return bookings

        user_ref = self.db.collection("users").document(user_uid)
        transaction = self.db.transaction()
        bookings = _book(transaction, user_ref)

        # Create calendar events with Meet links (after transaction succeeds)
        user = self.get_user_profile(user_uid)
        email = user.get("email", "") if user else ""
        name = user.get("display_name", "") if user else ""

        for booking in bookings:
            try:
                result = create_lesson_event(
                    date=booking["date"],
                    start_time=booking["start_time"],
                    end_time=booking["end_time"],
                    student_email=email,
                    student_name=name,
                )
                if result:
                    self.db.collection("bookings").document(booking["id"]).update({
                        "meet_link": result.get("meet_link"),
                        "calendar_event_id": result.get("event_id"),
                        "calendar_html_link": result.get("html_link"),
                    })
                    booking["meet_link"] = result.get("meet_link")
            except Exception as e:
                # Don't fail the booking, but record why the calendar/Meet step
                # failed so it's diagnosable instead of silently missing.
                traceback.print_exc()
                try:
                    self.db.collection("bookings").document(booking["id"]).update({
                        "calendar_error": str(e),
                    })
                except Exception:
                    pass
                print(f"Calendar event creation failed for {booking['date']}: {e}")

        return bookings

    def cancel_booking(self, user_uid, booking_id):
        booking_ref = self.db.collection("bookings").document(booking_id)
        booking_doc = booking_ref.get()

        if not booking_doc.exists:
            raise ValueError("Booking not found")
        booking = booking_doc.to_dict()
        if booking["user_uid"] != user_uid:
            raise ValueError("Not your booking")
        if booking["status"] != "confirmed":
            raise ValueError("Booking cannot be cancelled")

        booking_ref.update({"status": "cancelled"})
        user_ref = self.db.collection("users").document(user_uid)
        user_ref.update({"sessions_remaining": firestore.Increment(1)})

    def get_user_bookings(self, user_uid):
        docs = (
            self.db.collection("bookings")
            .where(filter=FieldFilter("user_uid", "==", user_uid))
            .stream()
        )
        bookings = [doc.to_dict() for doc in docs]
        bookings.sort(key=lambda b: (b.get("date", ""), b.get("start_time", "")))
        return bookings

    def get_all_confirmed_bookings(self):
        today = datetime.utcnow().strftime("%Y-%m-%d")
        docs = (
            self.db.collection("bookings")
            .where(filter=FieldFilter("status", "==", "confirmed"))
            .stream()
        )
        bookings = [doc.to_dict() for doc in docs if doc.to_dict().get("date", "") >= today]
        bookings.sort(key=lambda b: (b.get("date", ""), b.get("start_time", "")))
        return bookings

    # ── Purchases ──

    def create_purchase(self, user_uid, user_email, package_id, session_count, amount_cents, currency, stripe_session_id):
        purchase_id = str(uuid.uuid4())
        purchase = {
            "id": purchase_id,
            "user_uid": user_uid,
            "user_email": user_email,
            "package_id": package_id,
            "session_count": session_count,
            "amount_cents": amount_cents,
            "currency": currency,
            "stripe_session_id": stripe_session_id,
            "stripe_payment_intent": None,
            "status": "pending",
            "created_at": firestore.SERVER_TIMESTAMP,
        }
        self.db.collection("purchases").document(purchase_id).set(purchase)
        return purchase

    def complete_purchase(self, stripe_session_id, payment_intent=None):
        docs = (
            self.db.collection("purchases")
            .where(filter=FieldFilter("stripe_session_id", "==", stripe_session_id))
            .where(filter=FieldFilter("status", "==", "pending"))
            .limit(1)
            .stream()
        )
        purchase_doc = next(docs, None)
        if not purchase_doc:
            return None

        purchase = purchase_doc.to_dict()
        purchase_ref = self.db.collection("purchases").document(purchase["id"])
        purchase_ref.update({
            "status": "completed",
            "stripe_payment_intent": payment_intent,
        })

        user_ref = self.db.collection("users").document(purchase["user_uid"])
        user_ref.update({
            "sessions_remaining": firestore.Increment(purchase["session_count"]),
            "total_sessions_purchased": firestore.Increment(purchase["session_count"]),
        })
        return purchase

    def get_user_purchases(self, user_uid):
        docs = (
            self.db.collection("purchases")
            .where(filter=FieldFilter("user_uid", "==", user_uid))
            .stream()
        )
        return [doc.to_dict() for doc in docs]
