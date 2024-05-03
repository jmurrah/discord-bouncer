import stripe
from dotenv import load_dotenv
import os


def create_checkout_session() -> stripe.checkout.Session:
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "T-shirt",
                    },
                    "unit_amount": 2000,
                },
                "quantity": 1,
            },
        ],
        mode="payment",
        success_url="http://127.0.0.1:5000/checkout/success",
        cancel_url="http://127.0.0.1:5000/checkout/cancel",
    )
    return session.id


def handle_checkout_session():
    load_dotenv()
    stripe.api_key = os.getenv("STRIPE_KEY")

    session_id = create_checkout_session()
    breakpoint()
    # session = stripe.checkout.Session.retrieve(session_id)
    # if session.payment_status == "paid":
    #     return add_role(session.customer)
    # return False