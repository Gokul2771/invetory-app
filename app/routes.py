from flask import Blueprint, render_template, redirect, url_for, flash, request
from . import db
from .models import Product, Location, ProductMovement
from .forms import ProductForm, LocationForm, MovementForm
from sqlalchemy import func

bp = Blueprint("bp", __name__)

@bp.route("/")
def index():
    return redirect(url_for("bp.report"))

# ---------- Products ----------
@bp.route("/products")
def products():
    items = Product.query.order_by(Product.product_id).all()
    return render_template("products.html", products=items)

@bp.route("/products/add", methods=["GET", "POST"])
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        if Product.query.get(form.product_id.data):
            flash("Product ID already exists", "warning")
        else:
            p = Product(product_id=form.product_id.data.strip(), name=form.name.data.strip(), description=form.description.data)
            db.session.add(p)
            db.session.commit()
            flash("Product added", "success")
            return redirect(url_for("bp.products"))
    return render_template("product_form.html", form=form, action="Add")

@bp.route("/products/edit/<product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    p = Product.query.get_or_404(product_id)
    form = ProductForm(obj=p)
    # product_id should not be changed in edit; lock it
    form.product_id.render_kw = {"readonly": True}
    if form.validate_on_submit():
        p.name = form.name.data
        p.description = form.description.data
        db.session.commit()
        flash("Product updated", "success")
        return redirect(url_for("bp.products"))
    return render_template("product_form.html", form=form, action="Edit")

# ---------- Locations ----------
@bp.route("/locations")
def locations():
    items = Location.query.order_by(Location.location_id).all()
    return render_template("locations.html", locations=items)

@bp.route("/locations/add", methods=["GET", "POST"])
def add_location():
    form = LocationForm()
    if form.validate_on_submit():
        if Location.query.get(form.location_id.data):
            flash("Location ID already exists", "warning")
        else:
            loc = Location(location_id=form.location_id.data.strip(), name=form.name.data.strip(), description=form.description.data)
            db.session.add(loc)
            db.session.commit()
            flash("Location added", "success")
            return redirect(url_for("bp.locations"))
    return render_template("location_form.html", form=form, action="Add")

@bp.route("/locations/edit/<location_id>", methods=["GET", "POST"])
def edit_location(location_id):
    loc = Location.query.get_or_404(location_id)
    form = LocationForm(obj=loc)
    form.location_id.render_kw = {"readonly": True}
    if form.validate_on_submit():
        loc.name = form.name.data
        loc.description = form.description.data
        db.session.commit()
        flash("Location updated", "success")
        return redirect(url_for("bp.locations"))
    return render_template("location_form.html", form=form, action="Edit")

# ---------- Movements ----------
@bp.route("/movements")
def movements():
    items = ProductMovement.query.order_by(ProductMovement.timestamp.desc()).all()
    return render_template("movements.html", movements=items)

@bp.route("/movements/add", methods=["GET", "POST"])
def add_movement():
    form = MovementForm()
    # populate choices dynamically
    form.product.choices = [(p.product_id, f"{p.product_id} - {p.name}") for p in Product.query.order_by(Product.product_id)]
    loc_choices = [("", "--- none ---")] + [(l.location_id, f"{l.location_id} - {l.name}") for l in Location.query.order_by(Location.location_id)]
    form.from_location.choices = loc_choices
    form.to_location.choices = loc_choices

    if form.validate_on_submit():
        movement_id = form.movement_id.data.strip()
        if ProductMovement.query.get(movement_id):
            flash("Movement ID already exists", "warning")
            return render_template("movement_form.html", form=form, action="Add")
        # enforce: at least one of from/to must be provided
        from_loc = form.from_location.data or None
        to_loc = form.to_location.data or None
        if not from_loc and not to_loc:
            flash("At least one of From or To location must be specified", "danger")
            return render_template("movement_form.html", form=form, action="Add")
        mv = ProductMovement(
            movement_id=movement_id,
            product_id=form.product.data,
            from_location_id=from_loc,
            to_location_id=to_loc,
            qty=int(form.qty.data),
        )
        db.session.add(mv)
        db.session.commit()
        flash("Movement added", "success")
        return redirect(url_for("bp.movements"))
    return render_template("movement_form.html", form=form, action="Add")

# ---------- Report ----------
@bp.route("/report")
def report():
    products = Product.query.order_by(Product.product_id).all()
    locations = Location.query.order_by(Location.location_id).all()

    # Build a grid of (product, location, qty)
    rows = []
    for p in products:
        for l in locations:
            incoming = db.session.query(func.coalesce(func.sum(ProductMovement.qty), 0)).filter(
                ProductMovement.product_id == p.product_id, ProductMovement.to_location_id == l.location_id
            ).scalar() or 0
            outgoing = db.session.query(func.coalesce(func.sum(ProductMovement.qty), 0)).filter(
                ProductMovement.product_id == p.product_id, ProductMovement.from_location_id == l.location_id
            ).scalar() or 0
            qty = incoming - outgoing
            rows.append({"product": p, "location": l, "qty": qty})
    return render_template("report.html", rows=rows)
