import stripe
from dotenv import load_dotenv
import os
from datetime import date
from dateutil.relativedelta import relativedelta
import discord

PAID_ROLE = "secret_chat"
ROLE_PRICE = 500  # in cents = $5.00


def get_role_access_dates() -> tuple[date, date]:
    today = date.today()
    return today, today + relativedelta(months=1)


def create_price(subscription: bool) -> stripe.Price:
    # end_date

    description = (
        f"Subscription for Access to the {PAID_ROLE} Discord Role. Your subscription will auto-renew every month. The next payment will be on {get_role_access_dates()[1]}."
        if subscription
        else f"Access to the {PAID_ROLE} Discord Role for 1 month."
    )

    product = stripe.Product.create(
        name=f"{PAID_ROLE} Discord Role", description=description
    )

    return stripe.Price.create(
        unit_amount=ROLE_PRICE,
        currency="usd",
        product=product.id,
        recurring={"interval": "month"} if subscription else None,
    )


def create_payment_link(
    customer: discord.Message.author, subscription: bool
) -> stripe.PaymentLink:
    start_date, end_date = get_role_access_dates()

    price = create_price(subscription)

    payment_link = stripe.PaymentLink.create(
        line_items=[{"price": price.id, "quantity": 1}],
        metadata={
            "discord_id": customer.id,
            "discord_name": customer.name,
        },
    )

    return payment_link


def get_payment_link(customer: discord.Message.author, subscription: bool) -> str:
    load_dotenv()
    stripe.api_key = os.getenv("STRIPE_KEY")
    payment_link = create_payment_link(customer, subscription)

    return payment_link.url
