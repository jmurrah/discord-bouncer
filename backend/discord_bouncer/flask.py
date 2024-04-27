from flask import Flask, jsonify, render_template

app = Flask(__name__)


@app.route("/checkout/cancel", methods=["GET"])
def handle_cancel():
    return render_template(".html")


@app.route("/checkout/success", methods=["GET"])
def handle_success():
    return render_template("success.html")


@app.route("/", methods=["GET"])
def handle_home():
    return jsonify("test, World!")


def main():
    app.run(host="0.0.0.0", debug=True)


if __name__ == "__main__":
    main()