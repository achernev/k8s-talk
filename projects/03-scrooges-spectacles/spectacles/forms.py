from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class NewStonkForm(FlaskForm):
    symbol = StringField('Symbol', validators=[DataRequired()])
    submit = SubmitField('Add')
