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
	TextAreaField,
	HiddenField
)

from wtforms.widgets import (
	html5,
	TextInput,
	TextArea
)

from wtforms.fields.html5 import URLField

from wtforms.validators import (
	DataRequired,
	AnyOf,
	URL,
	Optional,
	Length,
	NoneOf,
	ValidationError
)

from werkzeug.utils import secure_filename
import pycountry

def flash_validation_errors(form):
	"""	
		Helper function to show form errors
	"""

	for field, errors in form.errors.items():
		for error in errors:
			flash(u"Error in the %s field - %s" % (
				getattr(form, field).label.text,
				error),
			'error')

def check_punctuation(form, field):
	for i in field.data:
		if i in string.punctuation:
			raise ValidationError("Username cannot contain special characters")

class UserForm(FlaskForm):

	username = StringField('username', validators=[
		DataRequired(),
		Length(1, 100, "Username must be between %(min)d to %(max)d characters."),
		check_punctuation]
	)

class ArtistForm(FlaskForm):

	artist_name = StringField('artist_name', validators=[DataRequired(),
		Length(1, 100, "Username must be between %(min)d to %(max)d characters."),
		check_punctuation]
	)

	artist_country = SelectField(
			'artist_country', validators=[DataRequired()],
			choices = sorted([(country.name, country.name) for country in pycountry.countries])
		)

	artist_soundcloud_url = URLField(
		validators=[URL(), Optional()]
	)

	artist_facebook_url = URLField(validators=[
		URL(), Optional()]
	)

	artist_instagram_url = URLField(validators=[
		URL(), Optional()]
	)

class EditUserForm(FlaskForm):
	profile_picture = FileField('Profile Picture', validators=[
		FileRequired(),
		FileAllowed(['jpg', 'jpeg', 'png'], 'Image only!')
	])

class EditArtistForm(FlaskForm):

	artist_wallet_address = StringField('Wallet Address',
		validators=[Length(0, 42, "You have provided an invalid Ethereum address.")],
		render_kw={
			'placeholder': '0x'
		}
	)
	
	artist_soundcloud_url = URLField(
		validators=[URL(), Optional()]
	)

	artist_facebook_url = URLField(validators=[
		URL(), Optional()]
	)

	artist_instagram_url = URLField(validators = [
		URL(), Optional()]
	)


class TrackForm(FlaskForm):

	track_id = HiddenField('Track ID')

	track_name = StringField('Track Name', validators=[DataRequired(),
		Length(1, 100, "Track name must be between %(min)d to %(max)d characters.")]
	)

	track_price = IntegerField('Price of track',
		default=1, 
		validators=[DataRequired()],
		widget=html5.NumberInput(min=1, max=100)
	)

	track_youtube_url = URLField(
		'YouTube URL (e.g. https://youtu.be/obe02lLwyps)',
		validators=[URL(), Optional()]
	)


class ReleasePresubmissionForm(FlaskForm):

	track_count = IntegerField('Number of Tracks',
		default=1, 
		validators=[DataRequired()],
		widget=html5.NumberInput(min=1,max=100)
	)

class EditReleaseForm(FlaskForm):

	release_name = StringField('release_name', validators=[DataRequired(),
		Length(1, 100, "Release name must be between %(min)d to %(max)d characters.")]
	)

	release_price = IntegerField('Price of release',
		default=1, 
		validators=[DataRequired()],
		widget=html5.NumberInput(min=1,max=100),
	)

	release_description = TextAreaField('Description of release',
			widget=TextArea(),
			render_kw={
				'class': 'release-text-input form-control',
				'rows': 4
			}
		)

	tracks = FieldList(FormField(TrackForm))

class EditReleaseCoverArtForm(FlaskForm):
	release_cover_art = FileField('Cover Art', validators=[
		FileRequired(),
		FileAllowed(['jpg', 'jpeg', 'png'], 'Image only!')
	])


'''
class ReleaseForm(FlaskForm):

	release_name = StringField('Release Name', validators=[
		DataRequired(),
		Length(1, 100, "Release name must be between %(min)d to %(max)d characters.")],
		render_kw={'id': "release-name-field"}
	)

	release_cover_art = FileField('Cover Art', validators=[
		FileRequired(),
		FileAllowed(['jpg', 'png'], 'Image only!')],
		render_kw={'id': "release-cover-art-field"}
	)

	release_price = IntegerField('Price of release',
		default=1, 
		validators=[DataRequired()],
		widget=html5.NumberInput(min=1,max=100),
		render_kw={'id': "release-price-field"}
	)

	release_text = TextAreaField('release_text', render_kw=dict(id="release-text-field"))

	tracks = FieldList(FormField(TrackForm), min_entries=1)
'''