from google.cloud import firestore
from datetime import date


def is_paid_user(discord_id: str) -> bool:
    return False
    db = firestore.Client()
    user_ref = db.collection("customers").document(discord_id)
    user = user_ref.get()

    if user.exists:
        return user.to_dict()["access_end_date"] >= date.today()

    return False
