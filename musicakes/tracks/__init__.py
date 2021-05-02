from flask import Blueprint

bp = Blueprint('tracks', __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/tracks-static')

from . import routes
