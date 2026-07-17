"""
One-time script to seed the Firestore 'packages' collection with tutoring pricing tiers.

Before running:
1. Create the corresponding Stripe Prices in your Stripe Dashboard
2. Copy the Price IDs (price_xxx) into the stripe_price_id fields below
3. Ensure your .env file has the Firebase service account credentials

Usage:
    python scripts/seed_packages.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from firebase_config import initialize_firebase, get_db
from firebase_admin import firestore

initialize_firebase()
db = get_db()

PACKAGES = [
    {
        "id": "single",
        "name": "Single Session",
        "session_count": 1,
        "price_cents": 4000,  # £40.00
        "currency": "gbp",
        "stripe_price_id": "price_1TtwEIGpV62HglwDiEcyZb1b",
        "description": "One 60-minute coding session.",
        "active": True,
        "created_at": firestore.SERVER_TIMESTAMP,
    },
    {
        "id": "pack-5",
        "name": "5-Session Pack",
        "session_count": 5,
        "price_cents": 17500,  # £175.00 (£35/session)
        "currency": "gbp",
        "stripe_price_id": "price_1TtwEIGpV62HglwDp3DRMkt7",
        "description": "Five 60-minute sessions. Save £25.",
        "active": True,
        "created_at": firestore.SERVER_TIMESTAMP,
    },
    {
        "id": "pack-10",
        "name": "10-Session Pack",
        "session_count": 10,
        "price_cents": 30000,  # £300.00 (£30/session)
        "currency": "gbp",
        "stripe_price_id": "price_1TtwEJGpV62HglwDL6119qWn",
        "description": "Ten 60-minute sessions. Save £100.",
        "active": True,
        "created_at": firestore.SERVER_TIMESTAMP,
    },
]

if __name__ == "__main__":
    for pkg in PACKAGES:
        print(f"Seeding package: {pkg['name']} ({pkg['id']})")
        db.collection("packages").document(pkg["id"]).set(pkg)
    print("Done! Seeded", len(PACKAGES), "packages.")
