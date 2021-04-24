from flask import Blueprint

bp = Blueprint('tracks', __name__)

from . import routes
