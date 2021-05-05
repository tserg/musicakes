from flask_wtf import FlaskForm

from wtforms import (
	StringField
)

from wtforms.validators import (
	DataRequired,
	Length
)

from ..utils.forms_utils import check_punctuation


class UserForm(FlaskForm):

	username = StringField('username', validators=[
		DataRequired(),
		Length(1, 100, "Username must be between %(min)d to %(max)d characters."),
		check_punctuation]
	)
