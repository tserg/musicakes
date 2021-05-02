from flask import Blueprint

bp = Blueprint('artists', __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/artists-static')

from . import routes
