from flask import session

from .models import User

def get_user_data(return_user_id=False):

    """
    Helper function to obtain user data and User model object for rendering of page
    """

    try:

        logged_in = session.get('token', None)

        auth_id = session['jwt_payload']['sub'][6:]
        user = User.query.filter(User.auth_id==auth_id).one_or_none()

        data = user.short_private()

    except:

        """
        Key error is thrown if user is not logged in
        """

        if return_user_id:

            return None, None

        else:

            return None

    else:

        if return_user_id:

            return user, data

        else:

            return data
