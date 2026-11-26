from secrets import token_hex

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config.update(SECRET_KEY="change-this-demo-key-before-deployment", SQLALCHEMY_DATABASE_URI="sqlite:///shop.db", SQLALCHEMY_TRACK_MODIFICATIONS=False)
db = SQLAlchemy(app)
CSRFProtect(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(40), nullable=False)
    description = db.Column(db.String(220), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=10)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(12), unique=True, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(24), default="Received", nullable=False)

class OrderLine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Integer, nullable=False)

def seed_products():
    if Product.query.count() == 0:
        db.session.add_all([
            Product(name="Canvas Daypack", category="Carry", description="Everyday canvas bag with room for the essentials.", price=1890, stock=12),
            Product(name="Stoneware Mug", category="Home", description="A handmade-feel mug for a slower morning.", price=690, stock=18),
            Product(name="Field Notes Set", category="Stationery", description="Three pocket notebooks with recycled paper.", price=390, stock=30),
            Product(name="Cotton Throw", category="Home", description="Soft, breathable cotton for a quiet evening.", price=2490, stock=8),
            Product(name="Travel Pouch", category="Carry", description="A compact organiser for cables and small items.", price=790, stock=20),
            Product(name="Desk Planner", category="Stationery", description="Undated weekly planner with a clean layout.", price=550, stock=15),
        ])
        db.session.commit()

def cart_context():
    cart = session.get("cart", {})
    rows, total = [], 0
    for raw_id, qty in cart.items():
        product = db.session.get(Product, int(raw_id))
        if product and qty > 0:
            subtotal = product.price * qty
            rows.append({"product": product, "quantity": qty, "subtotal": subtotal})
            total += subtotal
    return rows, total

@app.route("/")
def home():
    seed_products()
    term, category = request.args.get("q", "").strip(), request.args.get("category", "")
    query = Product.query.filter(Product.stock > 0)
    if term:
        query = query.filter(Product.name.ilike(f"%{term}%") | Product.description.ilike(f"%{term}%"))
    if category:
        query = query.filter_by(category=category)
    rows, total = cart_context()
    return render_template("index.html", products=query.order_by(Product.name).all(), categories=[r[0] for r in db.session.query(Product.category).distinct()], term=term, category=category, cart=rows, cart_total=total, cart_count=sum(x["quantity"] for x in rows), show_cart=request.args.get("view") == "cart")

@app.post("/cart/add/<int:product_id>")
def add_to_cart(product_id):
    seed_products()
    product = db.get_or_404(Product, product_id)
    cart = session.get("cart", {})
    current = int(cart.get(str(product.id), 0))
    if current < product.stock:
        cart[str(product.id)] = current + 1
        session["cart"] = cart
        flash(f"{product.name} added to your bag.", "success")
    else:
        flash("That item has no more sample stock available.", "error")
    return redirect(url_for("home"))

@app.post("/cart/update")
def update_cart():
    cart = session.get("cart", {})
    for product in Product.query.all():
        try:
            qty = max(0, min(int(request.form.get(f"qty_{product.id}", "0")), product.stock))
        except ValueError:
            qty = 0
        if qty:
            cart[str(product.id)] = qty
        else:
            cart.pop(str(product.id), None)
    session["cart"] = cart
    return redirect(url_for("home", view="cart"))

@app.post("/checkout")
def checkout():
    rows, total = cart_context()
    if not rows:
        flash("Your bag is empty.", "error")
        return redirect(url_for("home"))
    for row in rows:
        if row["quantity"] > row["product"].stock:
            flash("Stock changed. Update your bag and try again.", "error")
            return redirect(url_for("home", view="cart"))
    order = Order(reference=token_hex(4).upper(), total=total)
    db.session.add(order)
    db.session.flush()
    for row in rows:
        product = row["product"]
        product.stock -= row["quantity"]
        db.session.add(OrderLine(order_id=order.id, product_name=product.name, quantity=row["quantity"], unit_price=product.price))
    db.session.commit()
    session["cart"] = {}
    flash(f"Demo order {order.reference} received. No payment was taken.", "success")
    return redirect(url_for("home"))

with app.app_context():
    db.create_all()
    seed_products()

if __name__ == "__main__":
    app.run(debug=True)
