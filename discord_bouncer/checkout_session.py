import logging
import os
from datetime import date, datetime

import discord
import stripe
from dateutil.relativedelta import relativedelta

PAID_ROLE = "Trusted Trader"
ROLE_PRICE = 50  # in cents = $5.00


def create_price() -> tuple[stripe.Price, str]:
    end_date = date.today() + relativedelta(months=1)
    product = stripe.Product.create(
        name=f"{PAID_ROLE} Discord Role",
        description=f"Access to the {PAID_ROLE} Discord Role for 1 month. Your access will expire on {end_date}.",
    )
    unix_timestamp = str(datetime(end_date.year, end_date.month, end_date.day).timestamp())

    return (
        stripe.Price.create(
            unit_amount=ROLE_PRICE,
            currency="usd",
            product=product.id,
        ),
        unix_timestamp,
    )


def create_payment_link(customer: discord.Message.author) -> stripe.PaymentLink:
    price, end_timestamp = create_price()
    payment_link = stripe.PaymentLink.create(
        line_items=[{"price": price.id, "quantity": 1}],
        metadata={
            "discord_id": customer.id,
            "discord_username": customer.name,
            "end_date": end_timestamp,
        },
    )

    return payment_link


def get_payment_link(customer: discord.Message.author) -> str:
    stripe.api_key = os.getenv("STRIPE_LIVE_KEY")
    payment_link = create_payment_link(customer)
    logging.info(f"Payment Link created: {payment_link.url}")
    return payment_link.url
