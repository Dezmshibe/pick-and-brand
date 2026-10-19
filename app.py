import csv
from datetime import datetime
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = "change-this-before-deploying"

MESSAGES_FILE = Path(__file__).parent / "messages.csv"

# Example prices for the concept. Replace with your real price list.
PRODUCTS = {
    "cards":   {"name": "Business cards (per card)", "price": 2.50},
    "posters": {"name": "A3 poster (per poster)",    "price": 35.00},
    "stickers": {"name": "Sticker, 5 cm (per sticker)", "price": 4.50},
    "zines":   {"name": "Zine, 24 pages (per copy)", "price": 65.00},
}

SERVICES = [
    ("Cards and stationery", "Business cards, letterheads and notepads on uncoated, silk or recycled stock."),
    ("Posters and flyers", "A3 to A0 prints, flyers and menus. Same-day pickup on orders under 200 sheets."),
    ("Packaging and labels", "Boxes, stickers and labels, die-cut to your shape with matte or gloss finish."),
    ("Books and zines", "Saddle-stitched or perfect-bound, from 10 copies up to 2,000."),
]


def volume_discount(qty):
    if qty >= 1000:
        return 0.25
    if qty >= 500:
        return 0.15
    if qty >= 100:
        return 0.05
    return 0.0


@app.route("/")
def index():
    return render_template("index.html", services=SERVICES)


@app.route("/services")
def services():
    return render_template("services.html", services=SERVICES)


@app.route("/quote", methods=["GET", "POST"])
def quote():
    result = None
    if request.method == "POST":
        key = request.form.get("product", "cards")
        try:
            qty = max(1, int(request.form.get("qty", "1")))
        except ValueError:
            qty = 1
        product = PRODUCTS.get(key, PRODUCTS["cards"])
        discount = volume_discount(qty)
        result = {
            "key": key,
            "qty": qty,
            "name": product["name"],
            "discount": int(discount * 100),
            "total": qty * product["price"] * (1 - discount),
        }
    return render_template("quote.html", products=PRODUCTS, result=result)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()
        if not (name and email and message):
            flash("Please fill in every field.", "error")
            return render_template("contact.html", form=request.form)
        new_file = not MESSAGES_FILE.exists()
        with MESSAGES_FILE.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if new_file:
                writer.writerow(["time", "name", "email", "message"])
            writer.writerow([datetime.now().isoformat(timespec="seconds"), name, email, message])
        flash("Request sent. We'll reply within one working day.", "ok")
        return redirect(url_for("contact"))
    return render_template("contact.html", form={})


if __name__ == "__main__":
    app.run(debug=True)
