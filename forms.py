from flask_wtf import Form
from wtforms import StringField, ValidationError
from wtforms.validators import DataRequired, URL
import dateutil.parser as parser

class SpaceProbeForm(Form):
    probe_name = StringField('probe_name', validators=[DataRequired()])
    title = StringField('title', validators=[DataRequired()])
    url = StringField('url', validators=[DataRequired(), URL()])
    date = StringField('date', validators=[DataRequired()])

    def validate_date(form, field): 

        try:
            # try and convert input date into ISO date
            date = parser.parse(str(field.data))
            field.data = date.isoformat()  # set date to ISO here
        except:
            raise ValidationError("could not grock date format -- please try YYYY-MM-DD")



