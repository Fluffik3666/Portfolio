import os
import functools
from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
import stripe

try:
    from src.firebase_config import verify_token, ADMIN_EMAIL, FIREBASE_WEB_CONFIG
    from src.booking_service import BookingService
except ImportError:
    from firebase_config import verify_token, ADMIN_EMAIL, FIREBASE_WEB_CONFIG
    from booking_service import BookingService

blueprint = Blueprint(
    "stripe_bluprnt", __name__,
    url_prefix="/tutoring",
    template_folder="../src/templates",
    static_folder="../src/static",
)

STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")


def get_booking_service():
    return BookingService()


def require_auth(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if "user_uid" not in session:
            if request.is_json or request.path.startswith("/tutoring/api/"):
                return jsonify({"error": "Authentication required"}), 401
            return redirect(url_for("stripe_bluprnt.auth_page"))
        return f(*args, **kwargs)
    return wrapper


def require_admin(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if "user_uid" not in session:
            return jsonify({"error": "Authentication required"}), 401
        if session.get("user_email") != ADMIN_EMAIL:
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return wrapper


def _user_context():
    return {
        "logged_in": "user_uid" in session,
        "user_email": session.get("user_email"),
        "is_admin": session.get("user_email") == ADMIN_EMAIL,
        "firebase_config": FIREBASE_WEB_CONFIG,
        "stripe_publishable_key": STRIPE_PUBLISHABLE_KEY,
    }


# ── Page Routes ──

@blueprint.route("/book")
def book():
    svc = get_booking_service()
    ctx = _user_context()
    packages = svc.get_packages()
    user_profile = None
    if ctx["logged_in"]:
        user_profile = svc.get_user_profile(session["user_uid"])
    return render_template("tutoring_book.html", packages=packages, user_profile=user_profile, **ctx)


@blueprint.route("/account")
@require_auth
def account():
    svc = get_booking_service()
    ctx = _user_context()
    user_profile = svc.get_user_profile(session["user_uid"])
    bookings = svc.get_user_bookings(session["user_uid"])
    purchases = svc.get_user_purchases(session["user_uid"])
    return render_template("tutoring_account.html", user_profile=user_profile, bookings=bookings, purchases=purchases, **ctx)


@blueprint.route("/auth")
def auth_page():
    return render_template("tutoring_auth.html", **_user_context())


@blueprint.route("/admin")
@require_admin
def admin_page():
    svc = get_booking_service()
    availability = svc.get_availability()
    bookings = svc.get_all_confirmed_bookings()
    return render_template("tutoring_admin.html", availability=availability, bookings=bookings, **_user_context())


# ── Auth API ──

@blueprint.route("/api/session-verify", methods=["POST"])
def session_verify():
    data = request.get_json()
    id_token = data.get("id_token")
    if not id_token:
        return jsonify({"error": "Missing id_token"}), 400
    try:
        decoded = verify_token(id_token)
        uid = decoded["uid"]
        email = decoded.get("email", "")
        name = decoded.get("name", "")
        svc = get_booking_service()
        svc.create_or_get_user(uid, email, name)
        session["user_uid"] = uid
        session["user_email"] = email
        return jsonify({"ok": True, "uid": uid, "email": email})
    except Exception as e:
        return jsonify({"error": str(e)}), 401


@blueprint.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"ok": True})


# ── Slots API ──

@blueprint.route("/api/slots")
def api_slots():
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)
    if not year or not month:
        from datetime import datetime
        now = datetime.utcnow()
        year = year or now.year
        month = month or now.month
    svc = get_booking_service()
    slots = svc.get_available_for_month(year, month)
    return jsonify({"slots": slots})


@blueprint.route("/api/book", methods=["POST"])
@require_auth
def api_book():
    data = request.get_json()
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    duration = data.get("duration_minutes", 60)
    dates = data.get("dates", [])
    note = data.get("note", "").strip()[:500]

    if not start_time or not end_time or not dates:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        svc = get_booking_service()
        bookings = svc.book_sessions(session["user_uid"], start_time, end_time, duration, dates, note)
        return jsonify({"ok": True, "count": len(bookings)})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@blueprint.route("/api/cancel-booking", methods=["POST"])
@require_auth
def api_cancel_booking():
    data = request.get_json()
    booking_id = data.get("booking_id")
    if not booking_id:
        return jsonify({"error": "Missing booking_id"}), 400
    try:
        svc = get_booking_service()
        svc.cancel_booking(session["user_uid"], booking_id)
        return jsonify({"ok": True})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


# ── Packages API ──

@blueprint.route("/api/packages")
def api_packages():
    svc = get_booking_service()
    return jsonify({"packages": svc.get_packages()})


# ── Stripe Checkout ──

@blueprint.route("/checkout", methods=["POST"])
@require_auth
def checkout():
    data = request.get_json()
    package_id = data.get("package_id")
    if not package_id:
        return jsonify({"error": "Missing package_id"}), 400

    svc = get_booking_service()
    packages = svc.get_packages()
    package = next((p for p in packages if p["id"] == package_id), None)
    if not package:
        return jsonify({"error": "Package not found"}), 404

    success_url = os.getenv("STRIPE_SUCCESS_URL") or (request.host_url + "tutoring/account?purchase=success")
    cancel_url = os.getenv("STRIPE_FAILURE_URL") or (request.host_url + "tutoring/book?purchase=cancelled")

    try:
        # Get Stripe customer ID if available
        user_profile = svc.get_user_profile(session["user_uid"])
        stripe_customer_id = user_profile.get("stripe_customer_id") if user_profile else None

        checkout_kwargs = {
            "payment_method_types": ["card"],
            "line_items": [{"price": package["stripe_price_id"], "quantity": 1}],
            "mode": "payment",
            "success_url": success_url,
            "cancel_url": cancel_url,
            "metadata": {
                "user_uid": session["user_uid"],
                "user_email": session.get("user_email", ""),
                "package_id": package["id"],
                "session_count": str(package["session_count"]),
            },
        }
        if stripe_customer_id:
            checkout_kwargs["customer"] = stripe_customer_id

        checkout_session = stripe.checkout.Session.create(**checkout_kwargs)
        svc.create_purchase(
            user_uid=session["user_uid"],
            user_email=session.get("user_email", ""),
            package_id=package["id"],
            session_count=package["session_count"],
            amount_cents=package["price_cents"],
            currency=package["currency"],
            stripe_session_id=checkout_session.id,
        )
        return jsonify({"checkout_url": checkout_session.url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Stripe Webhook ──

@blueprint.route("/webhook", methods=["POST"])
def webhook():
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError):
        return jsonify({"error": "Invalid signature"}), 400

    if event["type"] == "checkout.session.completed":
        cs = event["data"]["object"]
        payment_intent = getattr(cs, "payment_intent", None)
        svc = get_booking_service()
        svc.complete_purchase(cs["id"], payment_intent)

    return jsonify({"ok": True}), 200


# ── Admin API ──

@blueprint.route("/admin/availability", methods=["POST"])
@require_admin
def admin_create_availability():
    data = request.get_json()
    days = data.get("days_of_week", [])
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    duration = data.get("duration_minutes", 60)

    if not days or not start_time or not end_time:
        return jsonify({"error": "Missing fields"}), 400

    svc = get_booking_service()
    created = []
    for dow in days:
        a = svc.create_availability(dow, start_time, end_time, duration)
        created.append(a)
    return jsonify({"ok": True, "count": len(created)})


@blueprint.route("/admin/availability/<avail_id>", methods=["DELETE"])
@require_admin
def admin_delete_availability(avail_id):
    svc = get_booking_service()
    svc.delete_availability(avail_id)
    return jsonify({"ok": True})
