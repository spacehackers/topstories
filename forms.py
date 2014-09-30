from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired

class SpaceProbeForm(Form):
    probe_name = StringField('probe_name', validators=[DataRequired()])
    title = StringField('title', validators=[DataRequired()])
    url = StringField('url', validators=[DataRequired()])
    date = StringField('date', validators=[DataRequired()])