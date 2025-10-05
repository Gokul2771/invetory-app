import random
from datetime import datetime, timedelta, timezone
from app import create_app, db
from app.models import Product, Location, ProductMovement

# Initialize Flask app and DB context
app = create_app()

with app.app_context():
    db.create_all()

    # --- Create Products ---
    products = [
        Product(product_id="P-A", name="Product A", description="Sample A"),
        Product(product_id="P-B", name="Product B", description="Sample B"),
        Product(product_id="P-C", name="Product C", description="Sample C"),
    ]

    for p in products:
        # Safe lookup using SQLAlchemy 2.x style
        if not db.session.get(Product, p.product_id):
            db.session.add(p)

    # --- Create Locations ---
    locations = [
        Location(location_id="L-X", name="Warehouse X", description="Main storage"),
        Location(location_id="L-Y", name="Warehouse Y", description="Backup unit"),
        Location(location_id="L-Z", name="Warehouse Z", description="Regional center"),
    ]

    for l in locations:
        if not db.session.get(Location, l.location_id):
            db.session.add(l)

    db.session.commit()

    # --- Create 20 random Product Movements ---
    all_products = Product.query.all()
    all_locations = Location.query.all()

    def create_movement(mid, product, from_loc, to_loc, qty, ts):
        mv = ProductMovement(
            movement_id=mid,
            product_id=product.product_id,
            from_location_id=(from_loc.location_id if from_loc else None),
            to_location_id=(to_loc.location_id if to_loc else None),
            qty=qty,
            timestamp=ts,
        )
        db.session.add(mv)

    # Use timezone-aware UTC timestamps
    base_time = datetime.now(timezone.utc)

    for i in range(1, 21):
        mid = f"M{i:03d}"
        p = random.choice(all_products)
        mode = random.choice(["in", "out", "transfer"])
        qty = random.randint(1, 50)
        ts = base_time - timedelta(days=random.randint(0, 10), hours=random.randint(0, 23))

        if mode == "in":
            # incoming to a random location
            to_loc = random.choice(all_locations)
            create_movement(mid, p, None, to_loc, qty, ts)
        elif mode == "out":
            # outgoing from a random location
            from_loc = random.choice(all_locations)
            create_movement(mid, p, from_loc, None, qty, ts)
        else:
            # transfer between two different locations
            a, b = random.sample(all_locations, 2)
            create_movement(mid, p, a, b, qty, ts)

    db.session.commit()
    print("✅ Seeded database with products, locations, and 20 random movements.")
