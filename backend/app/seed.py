"""Demo data. Run: python -m app.seed   (DEMO ONLY: do not use these passwords in production)."""

import os
import random
from datetime import date, timedelta

from sqlalchemy import select

from .database import SessionLocal
from .models import Taxpayer, Transaction, User
from .security import hash_password
from .services import calculate_tax

DEMO_PASSWORD = os.getenv("SEED_PASSWORD", "Demo#12345")
USERS = [
    ("admin", "System Admin", "admin"),
    ("officer", "Field Officer", "officer"),
    ("auditor", "Tax Auditor", "auditor"),
]
TAXPAYERS = [
    ("HTL000001", "Grand Melati Hotel", "hotel"),
    ("HTL000002", "Bukit Indah Inn", "hotel"),
    ("RST000001", "Warung Sari Rasa", "restoran"),
    ("RST000002", "Sate Pak Haji", "restoran"),
    ("RST000003", "Kopi Senja Cafe", "restoran"),
    ("HBR000001", "Nusantara Karaoke", "hiburan"),
    ("PKR000001", "Parkir Plaza Utama", "parkir"),
    ("PKR000002", "Parkir Stasiun Timur", "parkir"),
]
BASE = {"hotel": 4_000_000, "restoran": 1_200_000, "hiburan": 3_000_000, "parkir": 800_000}


def main() -> None:
    rng = random.Random(42)
    with SessionLocal() as db:
        if db.scalar(select(User).limit(1)):
            print("Database already seeded; nothing to do.")
            return
        for username, full_name, role in USERS:
            db.add(
                User(
                    username=username,
                    full_name=full_name,
                    role=role,
                    password_hash=hash_password(DEMO_PASSWORD),
                )
            )
        taxpayers = [
            Taxpayer(npwpd=n, name=nm, category=c, address="Demo address") for n, nm, c in TAXPAYERS
        ]
        db.add_all(taxpayers)
        db.flush()
        today = date.today()
        for tp in taxpayers:
            for day in range(180):
                amount = int(BASE[tp.category] * rng.uniform(0.6, 1.5))
                if rng.random() < 0.02:  # occasional spike -> flagged
                    amount *= 12
                db.add(
                    Transaction(
                        taxpayer_id=tp.id,
                        trx_date=today - timedelta(days=day),
                        amount=amount,
                        tax_amount=calculate_tax(tp.category, amount),
                        source="tapping_box",
                        is_flagged=amount >= 50_000_000,
                        flag_reason="above_threshold" if amount >= 50_000_000 else None,
                    )
                )
        db.commit()
        print(f"Seeded {len(USERS)} users, {len(taxpayers)} taxpayers. Password: {DEMO_PASSWORD}")


if __name__ == "__main__":
    main()
