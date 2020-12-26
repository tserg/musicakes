from functools import wraps
from flask import session


def requires_log_in(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'token' not in session:
            return redirect('/')
        return f(*args, **kwargs)
    return decorated
