from datetime import date

from google.cloud import firestore


def store_user(discord_id: str, access_end_date: date) -> None:
    db = firestore.Client()
    user_ref = db.collection("customers").document(discord_id)
    user_ref.set({"access_end_date": access_end_date})


def user_has_access(discord_id: str) -> bool:
    return False
    db = firestore.Client()
    user_ref = db.collection("customers").document(discord_id)
    user = user_ref.get()

    if user.exists:
        return user.to_dict()["access_end_date"] >= date.today()

    return False


def get_expired_users() -> list[str]:
    db = firestore.Client()
    user_ref = db.collection("customers").document(discord_id)
    user = user_ref.get()

    if user.exists:
        return user.to_dict()["access_end_date"] < date.today()

    return ["list of expired discord ids"]
