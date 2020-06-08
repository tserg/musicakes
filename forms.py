from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField, IntegerField
from wtforms.validators import DataRequired, AnyOf, URL, Optional
import pycountry

class UserForm(FlaskForm):

	username = StringField('username', validators=[DataRequired()])

class ArtistForm(FlaskForm):

	artist_name = StringField('artist_name', validators=[DataRequired()])

	artist_country = SelectField(
			'artist_country', validators=[DataRequired()],
			choices = [country.name for country in pycountry.countries]
		)
