from flask import Blueprint

bp = Blueprint('tracks', __name__,
    template_folder='templates')

from . import routes
