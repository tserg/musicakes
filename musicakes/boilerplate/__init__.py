from flask import Blueprint

bp = Blueprint('boilerplate', __name__)

from . import routes
