from flask import render_template, request, session
from werkzeug.utils import secure_filename

from . import bp

from .s3_utils import *

from ..decorators import requires_log_in
from ..models import Track, User

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

@bp.route('/sign_s3_upload', methods=['GET'])
@requires_log_in
def sign_s3_upload():

    user, data = get_user_data(True)

    if data is None:

        abort(404)

    file_name = secure_filename(request.args.get('file_name'))

    file_type = request.args.get('file_type')

    release_id = request.args.get('release_id')

    if release_id == None:

        key = user.auth_id + "/" + file_name

    else:

        key = user.auth_id + "/" + release_id + "/" + file_name

    json_data = generate_s3_presigned_upload(key, file_type, file_name)

    return json_data

@bp.route('/sign_s3_download', methods=['GET'])
@requires_log_in
def sign_s3_download_track():

    track_id = request.args.get('track_id')

    track = Track.query.filter(Track.id==track_id).one_or_none()

    if track is None:

        abort(404)

    url_components = track.download_url.rsplit('/')
    print(url_components)

    filename = secure_filename(url_components[-1])

    key = url_components[-3] + "/" + url_components[-2] + "/" + filename

    json_data = generate_s3_presigned_download(key, filename)

    return json_data
