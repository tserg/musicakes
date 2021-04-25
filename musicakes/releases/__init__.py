from flask import Blueprint

bp = Blueprint('releases', __name__)

from . import routes
