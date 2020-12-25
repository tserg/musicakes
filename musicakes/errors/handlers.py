from flask import render_template
from ..auth import AuthError
from . import bp

@bp.app_errorhandler(AuthError)
def auth_error(AuthError):
    return render_template('errors/401.html'), 401

@bp.app_errorhandler(400)
def bad_request_error(error):
    return render_template('errors/400.html'), 400

@bp.app_errorhandler(401)
def unathorised_error(error):
    return render_template('errors/401.html'), 401

@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@bp.app_errorhandler(405)
def wrong_method(error):
    return render_template('errors/405.html'), 405

@bp.app_errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500
