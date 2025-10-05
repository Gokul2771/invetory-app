from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, NumberRange

class ProductForm(FlaskForm):
    product_id = StringField("Product ID", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    description = TextAreaField("Description")
    submit = SubmitField("Save")

class LocationForm(FlaskForm):
    location_id = StringField("Location ID", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    description = TextAreaField("Description")
    submit = SubmitField("Save")

class MovementForm(FlaskForm):
    movement_id = StringField("Movement ID", validators=[DataRequired()])
    product = SelectField("Product", coerce=str, validators=[DataRequired()])
    from_location = SelectField("From (leave blank if incoming)", coerce=str, choices=[])
    to_location = SelectField("To (leave blank if outgoing)", coerce=str, choices=[])
    qty = IntegerField("Quantity", validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField("Save")
