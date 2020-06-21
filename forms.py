import string
from datetime import datetime
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired

from wtforms import (
	StringField,
	SelectField,
	SelectMultipleField,
	DateTimeField,
	BooleanField,
	IntegerField,
	FloatField,
	FormField,
	FieldList,
	TextAreaField
)

from wtforms.widgets import html5

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
		Length(6, 100, "Username must be between %(min)d to %(max)d characters."),
		check_punctuation]
	)

class ArtistForm(FlaskForm):

	artist_name = StringField('artist_name', validators=[DataRequired(),
		Length(6, 100, "Username must be between %(min)d to %(max)d characters."),
		check_punctuation]
	)

	artist_country = SelectField(
			'artist_country', validators=[DataRequired()],
			choices = [(country.name, country.name) for country in pycountry.countries]
		)

class EditUserForm(FlaskForm):
	profile_picture = FileField('Profile Picture', validators=[
		FileRequired(),
		FileAllowed(['jpg', 'png'], 'Image only!')
	])

class TrackForm(FlaskForm):

	track_name = StringField('Track Name', validators=[DataRequired(),
		Length(1, 100, "Track name must be between %(min)d to %(max)d characters.")]
	)

	track_file = FileField('Track WAV file', validators=[
		FileRequired(),
		FileAllowed(['wav'], 'WAV files only!')
	])

	track_price = IntegerField('Price of track',
		default=1, 
		validators=[DataRequired()],
		widget=html5.NumberInput(min=1,max=100)
	)

class ReleasePresubmissionForm(FlaskForm):

	track_count = IntegerField('Number of Tracks',
		default=1, 
		validators=[DataRequired()],
		widget=html5.NumberInput(min=1,max=100)
	)

class ReleaseForm(FlaskForm):

	release_name = StringField('Release Name', validators=[
		DataRequired(),
		Length(1, 100, "Release name must be between %(min)d to %(max)d characters.")
	])

	release_cover_art = FileField('Cover Art', validators=[
		FileRequired(),
		FileAllowed(['jpg', 'png'], 'Image only!')
	])

	release_price = IntegerField('Price of release',
		default=1, 
		validators=[DataRequired()],
		widget=html5.NumberInput(min=1,max=100)
	)

	release_text = TextAreaField('release_text', render_kw=dict(id="release-textbox"))

	tracks = FieldList(FormField(TrackForm), min_entries=1)

