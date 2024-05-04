import stripe
from dotenv import load_dotenv
import os
from datetime import date
from dateutil.relativedelta import relativedelta

PAID_ROLE = "secret_chat"
ROLE_PRICE = 500  # in cents = $5.00


def get_role_access_dates() -> tuple[date, date]:
    today = date.today()
    return today, today + relativedelta(months=1)


def create_payment_link() -> stripe.PaymentLink:
    start_date, end_date = get_role_access_dates()

    product = stripe.Product.create(
        name=f"{PAID_ROLE} Discord Role",
        description=(
            f"Access to the {PAID_ROLE} Discord Role for 1 month.\n"
            f"You will have access from {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}"
        )
    )
    breakpoint()
    price = stripe.Price.create(
        unit_amount=ROLE_PRICE, currency="usd", product_data=product.id
    )

    return stripe.PaymentLink.create(line_items=[{"price": price.id, "quantity": 1}])


def handle_checkout_session():
    load_dotenv()
    stripe.api_key = os.getenv("STRIPE_KEY")

    payment_link = create_payment_link()
    print(payment_link.url)
    # session = stripe.checkout.Session.retrieve(session_id)
    # if session.payment_status == "paid":
    #     return add_role(session.customer)
    # return False
