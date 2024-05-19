import logging
from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pytest

from discord_bouncer import checkout_session


class MockDate(date):
    @classmethod
    def today(cls):
        return date(2024, 1, 1)


@patch("discord_bouncer.checkout_session.date", new=MockDate)
def test_create_price(mock_stripe_product_create, mock_stripe_price_create):
    mock_stripe_product_create.return_value = MagicMock(id="prod_test")
    mock_stripe_price_create.return_value = {"id": "price_test"}

    result = checkout_session.create_price()

    mock_stripe_product_create.assert_called_once()
    mock_stripe_price_create.assert_called_once_with(
        unit_amount=checkout_session.ROLE_PRICE,
        currency="usd",
        product="prod_test",
    )
    assert result == ({"id": "price_test"}, "1706767200.0")


def test_create_payment_link(
    mock_stripe_product_retrieve, mock_create_price, mock_stripe_payment_link_create
):
    mock_customer = MagicMock(id="customer_id")
    mock_customer.name = "customer_name"

    mock_product = MagicMock(metadata={"end_date": "01234"})
    mock_stripe_product_retrieve.return_value = mock_product

    mock_create_price.return_value = (MagicMock(id="price_id"), "01234")
    mock_stripe_payment_link_create.return_value = {"id": "payment_link_id"}

    result = checkout_session.create_payment_link(mock_customer)

    mock_create_price.assert_called_once()
    mock_stripe_payment_link_create.assert_called_once_with(
        line_items=[{"price": "price_id", "quantity": 1}],
        metadata={
            "discord_id": "customer_id",
            "discord_username": "customer_name",
            "end_date": "01234",
        },
    )
    assert result == {"id": "payment_link_id"}


def test_get_payment_link(mock_create_payment_link, caplog):
    caplog.set_level(logging.INFO)
    mock_customer = MagicMock(id="customer_id")
    mock_customer.name = "customer_name"
    mock_create_payment_link.return_value = MagicMock(url="payment_link_url")

    result = checkout_session.get_payment_link(mock_customer)

    assert result == "payment_link_url"
    assert "Payment Link created: payment_link_url" in caplog.text


@pytest.fixture
def mock_stripe_product_create():
    with patch("stripe.Product.create") as mock_product_create:
        yield mock_product_create


@pytest.fixture
def mock_stripe_price_create():
    with patch("stripe.Price.create") as mock_price_create:
        yield mock_price_create


@pytest.fixture
def mock_stripe_product_retrieve():
    with patch("stripe.Product.retrieve") as mock_product_retrieve:
        yield mock_product_retrieve


@pytest.fixture
def mock_create_price():
    with patch("discord_bouncer.checkout_session.create_price") as mock_create_price:
        yield mock_create_price


@pytest.fixture
def mock_stripe_payment_link_create():
    with patch(
        "discord_bouncer.checkout_session.stripe.PaymentLink.create"
    ) as mock_payment_link_create:
        yield mock_payment_link_create


@pytest.fixture
def mock_create_payment_link():
    with patch(
        "discord_bouncer.checkout_session.create_payment_link"
    ) as mock_create_payment_link:
        yield mock_create_payment_link
