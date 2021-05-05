from flask_wtf import FlaskForm

from wtforms import (
	StringField,
	SelectField
)

from wtforms.fields.html5 import URLField

from wtforms.validators import (
	DataRequired,
	URL,
	Optional,
	Length
)

import pycountry

from ..utils.forms_utils import (
    check_punctuation,
    check_hex_string
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

class EditArtistForm(FlaskForm):

	artist_wallet_address = StringField('Wallet Address',
		validators=[
			Length(0, 42, "You have provided an invalid Ethereum address."),
			check_hex_string
		],
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

	artist_country = SelectField(
			'artist_country', validators=[DataRequired()],
			choices = sorted([(country.name, country.name) for country in pycountry.countries])
		)
