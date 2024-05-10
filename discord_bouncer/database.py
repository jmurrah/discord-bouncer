from datetime import datetime, date
import logging

from google.cloud import firestore


def store_user(discord_id: str, access_end_date: date) -> None:
    db = firestore.Client()
    user_ref = db.collection("customers").document(discord_id)
    user_ref.set({"access_end_date": access_end_date})


def access_date_active(discord_id: str) -> bool:
    db = firestore.Client()
    user_ref = db.collection("customers").document(str(discord_id))
    user = user_ref.get()
    logging.info(f"User: {user.to_dict()}")
    if user.exists:
        access_end_date = datetime.strptime(
            user.to_dict()["access_end_date"], "%Y-%m-%d"
        ).date()
        return access_end_date >= date.today()

    return False


def delete_expired_users() -> list[str]:
    db = firestore.Client()
    users = (
        db.collection("customers")
        .where("access_end_date", "<", datetime.date.today())
        .stream()
    )
    user_discord_ids = [user.discord_id for user in users]

    for user in users:
        user.reference.delete()

    return user_discord_ids
