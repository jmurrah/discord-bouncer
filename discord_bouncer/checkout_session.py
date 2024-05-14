import logging
import os
from datetime import date

import discord
import stripe
from dateutil.relativedelta import relativedelta

PAID_ROLE = "secret_chat"
ROLE_PRICE = 1000  # in cents = $5.00


def create_price(subscription: bool) -> stripe.Price:
    end_date = date.today() + relativedelta(months=1)

    description = (
        f"Subscription for Access to the {PAID_ROLE} Discord Role. Your subscription will auto-renew every month. The next payment will be on {end_date}."
        if subscription
        else f"Access to the {PAID_ROLE} Discord Role for 1 month. Your access will expire on {end_date}."
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
    price = create_price(subscription)

    payment_link = stripe.PaymentLink.create(
        line_items=[{"price": price.id, "quantity": 1}],
        metadata={
            "discord_id": customer.id,
            "discord_username": customer.name,
        },
    )

    return payment_link


def get_payment_link(customer: discord.Message.author, subscription: bool) -> str:
    # load_dotenv(override=True)
    stripe.api_key = os.getenv("STRIPE_TEST_KEY")
    # stripe.api_key = os.getenv("STRIPE_LIVE_KEY")
    payment_link = create_payment_link(customer, subscription)
    return payment_link.url
