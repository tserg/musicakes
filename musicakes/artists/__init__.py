from flask import Blueprint

bp = Blueprint('artists', __name__,
    template_folder='templates')

from . import routes
