import stripe
from dotenv import load_dotenv
import os


def create_checkout_session():
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
    return f"https://checkout.stripe.com/pay/{session.id}"

def main():
    load_dotenv()
    stripe.api_key = os.getenv("STRIPE_KEY")
    print(create_checkout_session())
