"""Seed script: creates admin + sample pro user via Supabase Admin API."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from supabase import create_client

USERS = [
    {
        "email": "saiprakash@ideaforge.app",
        "password": "IdeaForge@2024!",
        "name": "Sai Prakash",
        "role": "admin",
        "tier": "enterprise",
    },
    {
        "email": "prouser@ideaforge.app",
        "password": "ProUser@2024!",
        "name": "Pro User",
        "role": "user",
        "tier": "pro",
    },
]


def seed():
    sb = create_client(settings.supabase_url, settings.supabase_service_role_key)

    for u in USERS:
        try:
            result = sb.auth.admin.create_user(
                {
                    "email": u["email"],
                    "password": u["password"],
                    "email_confirm": True,
                    "user_metadata": {"full_name": u["name"]},
                }
            )

            user_id = result.user.id
            print(f"Created user: {user_id} ({u['email']})")

            sb.table("profiles").update(
                {
                    "role": u["role"],
                    "tier": u["tier"],
                    "full_name": u["name"],
                }
            ).eq("id", user_id).execute()

            print(f"  -> role={u['role']}, tier={u['tier']}")

        except Exception as e:
            print(f"Skipping {u['email']}: {e}")

    print("\n--- Seed accounts ---")
    for u in USERS:
        print(f"  {u['role'].upper():>10}  {u['email']}  /  {u['password']}  (tier: {u['tier']})")
    print()


if __name__ == "__main__":
    seed()
