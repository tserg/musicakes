from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired

from wtforms import (
	StringField,
	BooleanField,
	IntegerField,
	FormField,
	FieldList,
	TextAreaField,
    HiddenField
)

from wtforms.widgets import (
	html5,
	TextArea
)

from wtforms.fields.html5 import URLField

from wtforms.validators import (
	DataRequired,
    URL,
	Optional,
	Length
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


'''
class EditReleaseCoverArtForm(FlaskForm):
	release_cover_art = FileField('Cover Art', validators=[
		FileRequired(),
		FileAllowed(['jpg', 'jpeg', 'png'], 'Image only!')
	])
'''


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
