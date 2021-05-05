import string

from wtforms.validators import (
	ValidationError
)

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

def check_hex_string(form, field):
	"""
	Helper function to check if the field contains hexadecimal digits only
	"""

	address = field.data

	if all(c in string.hexdigits for c in address[2:]) is False:
		raise ValidationError("Address contains non-hexadecimal digits")
