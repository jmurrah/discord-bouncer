import logging
import os
from datetime import date, datetime, time

import pytz
from google.cloud import firestore


def convert_time_to_date(timestamp: str) -> date:
    return str(
        datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
        .replace(tzinfo=pytz.UTC)
        .astimezone(pytz.timezone(os.getenv("TZ")))
        .date()
    )


def store_member(data: dict) -> None:
    firestore.Client().collection("customers").document(data["discord_id"]).set(
        {
            "access_end_date": convert_time_to_date(data["end_date"]),
            "discord_username": data["discord_username"],
            "subscription": data["payment_mode"] == "subscription",
        }
    )
    logging.info(f"Stored member: {data}")


def access_date_active(discord_id: str) -> bool:
    member = firestore.Client().collection("customers").document(str(discord_id)).get()

    if member.exists:
        access_end_date = datetime.strptime(
            member.to_dict()["access_end_date"], "%Y-%m-%d"
        ).date()
        return date.today() <= access_end_date

    return False


def delete_expired_members() -> list[str]:
    db = firestore.Client()
    members = list(
        db.collection("customers")
        .where("access_end_date", "<", date.today().isoformat())
        .stream()
    )

    logging.info(f"Deleting {len(members)} expired members.")
    for member in members:
        logging.info(f"Deleting member: {member.to_dict()}")
        member.reference.delete()

    db.collection("recently_deleted_customers").document("customer_list").update(
        {
            "date_deleted": str(date.today()),
            "deleted_discord_ids": [member.id for member in members],
        }
    )


def get_recently_expired_members() -> list[str]:
    return (
        firestore.Client()
        .collection("recently_deleted_customers")
        .document("customer_list")
        .get()
        .to_dict()
        .get("deleted_discord_ids", [])
    )
