from datetime import datetime, timezone
from . import db

class Product(db.Model):
    __tablename__ = "product"
    product_id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)

    def __repr__(self):
        return f"<Product {self.product_id} {self.name}>"

class Location(db.Model):
    __tablename__ = "location"
    location_id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<Location {self.location_id} {self.name}>"

class ProductMovement(db.Model):
    __tablename__ = "product_movement"
    movement_id = db.Column(db.String, primary_key=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    from_location_id = db.Column(db.String, db.ForeignKey("location.location_id"), nullable=True)
    to_location_id = db.Column(db.String, db.ForeignKey("location.location_id"), nullable=True)
    product_id = db.Column(db.String, db.ForeignKey("product.product_id"), nullable=False)
    qty = db.Column(db.Integer, nullable=False)

    product = db.relationship("Product", backref="movements")
    from_location = db.relationship("Location", foreign_keys=[from_location_id], backref="outgoing_movements")
    to_location = db.relationship("Location", foreign_keys=[to_location_id], backref="incoming_movements")

    def __repr__(self):
        return f"<Movement {self.movement_id} P:{self.product_id} Q:{self.qty} from:{self.from_location_id} to:{self.to_location_id}>"
