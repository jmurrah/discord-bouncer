import logging
from datetime import date, datetime


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


def handle_snapshot(doc_snapshot, changes, read_time):
    for doc in doc_snapshot:
        logging.info(f"Received document snapshot: {doc.id}")
        logging.info(f"Document data: {doc.to_dict()}")


def delete_expired_users() -> list[str]:
    db = firestore.Client()
    users = (
        db.collection("customers").where("access_end_date", "<", date.today()).stream()
    )
    user_discord_ids = [user.discord_id for user in users]

    for user in users:
        user.reference.delete()

    db.collection("recently_deleted_customers").document("customer_list").update(
        {"date_deleted": date.today(), "discord_ids": user_discord_ids}
    )
