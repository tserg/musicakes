from flask import Blueprint

bp = Blueprint('releases', __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/releases-static')

from . import routes
