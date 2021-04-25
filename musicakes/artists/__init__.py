from flask import Blueprint

bp = Blueprint('artists', __name__)

from . import routes
