import logging
import os
from datetime import date, datetime, time

import pytz
from google.cloud import firestore


def convert_time_to_date(timestamp: time) -> date:
    return (
        datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
        .replace(tzinfo=pytz.UTC)
        .astimezone(pytz.timezone(os.getenv("TZ")))
        .date()
    )


def store_user(data: dict) -> None:
    firestore.Client().collection("customers").document(data["discord_id"]).set(
        {
            "access_end_date": convert_time_to_date(data["time"]),
            "discord_username": data["discord_username"],
            "subscription": data["payment_mode"] == "subscription",
        }
    )


def access_date_active(discord_id: str) -> bool:
    user = firestore.Client().collection("customers").document(str(discord_id)).get()
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

    logging.info(f"Deleting {len(users)} expired users.")
    for user in users:
        user.reference.delete()

    db.collection("recently_deleted_customers").document("customer_list").update(
        {
            "date_deleted": str(date.today()),
            "deleted_discord_ids": [user.id for user in users],
        }
    )


def get_recently_expired_users() -> list[str]:
    return (
        firestore.Client()
        .collection("recently_deleted_customers")
        .document("customer_list")
        .get()
        .to_dict()
        .get("deleted_discord_ids", [])
    )
