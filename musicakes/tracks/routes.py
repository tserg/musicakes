import os

from flask import (
    request,
    abort,
    jsonify,
    render_template
)

from werkzeug.utils import secure_filename

from dotenv import load_dotenv

from . import bp

from ..models import (
    Artist,
    Release,
    Track,
    PaymentToken,
    PurchaseCeleryTask
)

from ..session_utils import (
    get_user_data
)

from ..decorators import (
    requires_log_in
)
'''
from ..tasks import (
    check_smart_contract_deployed,
    check_purchase_transaction_confirmed
)
'''
load_dotenv()

# Environment variables for Ethereum blockchain

ETHEREUM_CHAIN_ID = os.getenv('ETHEREUM_CHAIN_ID', 'Does not exist')

# Environment variable for AWS S3 location

S3_LOCATION = os.getenv('S3_LOCATION', 'Does not exist')

TRACKS_PER_PAGE = 10

@bp.route('/tracks', methods=['GET'])
def get_tracks():

    data = get_user_data()

    try:

        # page count

        page = request.args.get('page', 1, type=int)

        start = (page-1)*TRACKS_PER_PAGE
        end = start + TRACKS_PER_PAGE

        # Filter for releases that have been removed by artist

        all_tracks = Track.query.join(Track.release) \
            .filter(Release.is_removed == False) \
            .order_by(Track.created_on.desc()).all()

        formatted_all_tracks = [track.short_public() for track in all_tracks]

        tracks_count = len(formatted_all_tracks)

        if start + 1 <= tracks_count:

            return render_template('/pages/tracks.html', tracks=formatted_all_tracks[start:end], userinfo=data)

        else:
            abort(404)

    except:

        abort(404)

@bp.route('/tracks/<int:track_id>', methods=['GET'])
def show_track(track_id):

    user, data = get_user_data(True)

    try:

        current_track = Track.query.filter(Track.id==track_id).one_or_none()

        if current_track is None:

            abort(404)

        current_release = Release.query.filter(Release.id==current_track.release_id).one_or_none()

        if current_release is None:

            abort(404)

        formatted_track_data = current_track.short_public()

        payment_token_address = PaymentToken.query.get(1).smart_contract_address
        formatted_track_data['payment_token_address'] = payment_token_address

        formatted_track_data['purchasers'] = current_track.get_purchasers()

        # Checks if smart contract address is in db

        if formatted_track_data['smart_contract_address'] is None:
            formatted_track_data['smart_contract_address'] = "0x"

        # Get YouTube playlist URL

        if formatted_track_data['youtube_embed_url'] == 'https://youtube.com/embed/':
            formatted_track_data['youtube_embed_url'] = None

        # Retrieve artist data

        current_artist = Artist.query.filter(Artist.id==current_track.artist_id).one_or_none()

        if current_artist is None:
            abort(404)

        artist_data = current_artist.short()

        if data is not None:

            data['has_purchased'] = user.has_purchased_track(track_id, current_release.id)

            creator = (current_release.artist.user.id == user.id)

        else:
            creator = False

        return render_template('pages/show_track.html',
                                track=formatted_track_data,
                                userinfo=data,
                                creator=creator,
                                chain_id=ETHEREUM_CHAIN_ID,
                                artist=artist_data)

    except:

        abort(404)

@bp.route('/tracks/create', methods=['POST'])
@requires_log_in
def create_track():

    user, data = get_user_data(True)

    if user.artist is None:

        abort(404)

    try:

        track_name = request.get_json()['track_name']
        track_price = request.get_json()['track_price']
        track_release_id = request.get_json()['release_id']
        track_file_name = S3_LOCATION + user.auth_id + "/" + str(track_release_id) + "/" + secure_filename(request.get_json()['file_name'])

        # Create new release in database

        new_track = Track(
            artist_id = user.artist.id,
            release_id = track_release_id,
            name = track_name,
            price = track_price,
            download_url = track_file_name

        )

        new_track.insert()

        return jsonify({
            'success': True,
            'track_id': new_track.id
        })

    except Exception as e:
        print(e)
        return jsonify({
            'success': False
        })


@bp.route('/tracks/<int:track_id>/purchase', methods=['POST'])
@requires_log_in
def purchase_track(track_id):

    user, data = get_user_data(True)

    if data is None:

        abort(404)

    try:

        transaction_hash = request.get_json()['transaction_hash']
        wallet_address = request.get_json()['wallet_address']

        from ..tasks import check_purchase_transaction_confirmed

        task = check_purchase_transaction_confirmed.apply_async(
                    args=(transaction_hash,
                            user.id))

        purchase_description = Track.query.filter(Track.id == track_id).one_or_none().purchase_description()

        purchase_celery_task = PurchaseCeleryTask(
            task_id = task.id,
            user_id = user.id,
            purchase_description = purchase_description,
            purchase_type = 'track',
            purchase_type_id = track_id,
            wallet_address=wallet_address,
            transaction_hash = transaction_hash,
            is_confirmed = False
        )

        purchase_celery_task.insert()

        return jsonify({
            'success': True,
            'task_id': task.id,
            'completed': task.ready()
        })

    except Exception as e:
        print(e)
        return jsonify({
            'success': False
        })
