from flask import Blueprint

bp = Blueprint('users', __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/users/static')

from . import routes
