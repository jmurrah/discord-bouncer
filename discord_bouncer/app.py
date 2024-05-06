from flask import Flask, request, Response
import stripe

import logging

logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route("/", methods=["POST"])
def handle_stripe_post():
    payload = request.get_data(as_text=True)
    signature_header = request.headers.get("Stripe-Signature")
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_KEY")
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, signature_header, endpoint_secret
        )
    except ValueError as e:
        logging.error(e)
        return Response(status=400)
    except stripe.error.SignatureVerificationError as e:
        logging.error(e)
        return Response(status=400)

    return Response(status=200)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
