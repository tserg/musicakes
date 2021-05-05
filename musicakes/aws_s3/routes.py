from flask import render_template, request
from werkzeug.utils import secure_filename

from . import bp

from ..decorators import requires_log_in
from ..models import Track

from .s3_utils import (
    generate_s3_presigned_upload,
    generate_s3_presigned_download
)
from ..utils.session_utils import (
    get_user_data
)

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
