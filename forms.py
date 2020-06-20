import string
from datetime import datetime
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired

from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField, IntegerField, FloatField
from wtforms.validators import DataRequired, AnyOf, URL, Optional, Length, NoneOf

from werkzeug.utils import secure_filename
import pycountry

def check_punctuation(form, field):
	for i in field.data:
		if i in string.punctuation:
			raise ValidationError("Username cannot contain special characters")

class UserForm(FlaskForm):

	username = StringField('username', validators=[
		DataRequired(),
		Length(6, 20, "Username must be between %(min)d to %(max)d characters."),
		check_punctuation]
	)

class ArtistForm(FlaskForm):

	artist_name = StringField('artist_name', validators=[DataRequired()])

	artist_country = SelectField(
			'artist_country', validators=[DataRequired()],
			choices = [(country.name, country.name) for country in pycountry.countries]
		)

class EditUserForm(FlaskForm):
	profile_picture = FileField('profile_picture', validators=[
		FileRequired(),
		FileAllowed(['jpg', 'png'], 'Image only!')
	])
