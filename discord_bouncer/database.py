import logging
from datetime import date, datetime, time

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
        return date.today() <= access_end_date

    return False


def delete_expired_users() -> list[str]:
    db = firestore.Client()
    users = list(
        db.collection("customers")
        .where("access_end_date", "<", date.today().isoformat())
        .stream()
    )

    # for user in users:
    #     user.reference.delete()

    db.collection("recently_deleted_customers").document("customer_list").update(
        {
            "date_deleted": str(date.today()),
            "deleted_discord_ids": [user.id for user in users],
        }
    )


def get_recently_expired_users() -> list[str]:
    db = firestore.Client()
    doc = db.collection("recently_deleted_customers").document("customer_list").get()
    return doc.to_dict()["deleted_discord_ids"] if doc.exists else []
