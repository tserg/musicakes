import os
import json

from flask import (
    flash,
    request,
    abort,
    jsonify,
    render_template,
    redirect,
    url_for
)

from flask_wtf import (
    Form
)

from sqlalchemy import or_
from sqlalchemy.sql import func

from werkzeug.utils import secure_filename

from dotenv import load_dotenv

from . import bp

from .forms import (
    ReleasePresubmissionForm,
    EditReleaseForm
)

from ..models import (
    Artist,
    Release,
    Track,
    Purchase,
    PaymentToken,
    MusicakesContractFactory,
    DeployCeleryTask,
    PurchaseCeleryTask
)

from ..utils.session_utils import (
    get_user_data
)

from ..decorators import (
    requires_log_in
)

from ..aws_s3.s3_utils import (
    upload_file,
    delete_files
)



load_dotenv()

# Environment variable for AWS S3 location

S3_LOCATION = os.getenv('S3_LOCATION', 'Does not exist')

# Environment variables for Ethereum blockchain

ETHEREUM_CHAIN_ID = os.getenv('ETHEREUM_CHAIN_ID', 'Does not exist')

# Environment variables for app

RELEASES_PER_PAGE = 10

@bp.route('/releases', methods=['GET'])
def get_releases():

    data = get_user_data()

    try:

        # page count

        page = request.args.get('page', 1, type=int)

        start = (page-1)*RELEASES_PER_PAGE
        end = start + RELEASES_PER_PAGE

        all_releases = Release.query.join(Release.tracks) \
            .filter(Release.is_removed == False) \
            .having(func.count(Track.id) > 0) \
            .group_by(Release.id) \
            .order_by(Release.created_on.desc()).all()

        formatted_all_releases = [release.short_public()
                                  for release in all_releases]

        releases_count = len(formatted_all_releases)

        if start + 1 <= releases_count:

            return render_template('releases/releases.html', releases=formatted_all_releases[start:end], userinfo=data)

        else:
            abort(404)

    except Exception as e:
        print(e)
        abort(404)

@bp.route('/releases/<int:release_id>', methods=['GET'])
def show_release(release_id):

    user, data = get_user_data(True)

    try:

        current_release = Release.query.filter(Release.id==release_id).one_or_none()
        if current_release is None:
            abort(404)

        release_data = current_release.short_public()

        payment_token_address = PaymentToken.query.get(1).smart_contract_address
        release_data['payment_token_address'] = payment_token_address

        release_data['purchasers'] = current_release.get_purchasers()

        # Checks if smart contract address is in db

        if current_release.smart_contract_address is None:
            release_data['smart_contract_address'] = "0x"

        # Get YouTube playlist URL

        if release_data['youtube_embed_url'] == 'https://youtube.com/embed/':
            release_data['youtube_embed_url'] = None

        current_artist = Artist.query.filter(Artist.id==current_release.artist_id).one_or_none()

        if current_artist is None:
            abort(404)

        artist_data = current_artist.short()

        if data is not None:

            data['has_purchased'] = user.has_purchased_release(release_id)

            creator = (current_release.artist.user.id == user.id)

        else:
            creator = False

        return render_template('releases/show_release.html',
                                release=release_data,
                                userinfo=data,
                                creator=creator,
                                chain_id=ETHEREUM_CHAIN_ID,
                                artist=artist_data)

    except Exception as e:
        print(e)
        abort(404)

    return redirect('/')

@bp.route('/releases/create', methods=['GET'])
@requires_log_in
def create_release_presubmission_form():

    user, data = get_user_data(True)

    if user.artist is None:

        abort(404)

    form = ReleasePresubmissionForm()

    return render_template('forms/new_release_presubmission.html', form=form, userinfo=data)

@bp.route('/releases/create', methods=['POST'])
@requires_log_in
def create_release_presubmission():

    user, data = get_user_data(True)

    if user.artist is None:

        abort(404)

    presubmission_form = ReleasePresubmissionForm(request.form)

    track_count = presubmission_form.track_count.data

    if track_count >= 2:

        track_count_list = [n for n in range(2, track_count+1)]

    else:

        track_count_list = []

    return render_template('forms/new_release.html', track_count=track_count_list, userinfo=data)

@bp.route('/releases/create_2', methods=['POST'])
@requires_log_in
def create_release_submission():

    user, data = get_user_data(True)

    if user.artist is None:

        abort(404)

    try:

        release_name = request.get_json()['release_name']
        release_price = request.get_json()['release_price']
        release_text = request.get_json()['release_text']

        # Create new release in database

        new_release = Release(
            artist_id = user.artist.id,
            name=release_name,
            price=release_price,
            description=release_text,
            #cover_art=release_cover_art_file_name
        )

        new_release.insert()

        return jsonify({
            'success': True,
            'release_id': new_release.id
        })

    except Exception as e:
        print(e)
        return jsonify({
            'success': False
        })

@bp.route('/releases/<int:release_id>/update_cover_art', methods=['POST'])
@requires_log_in
def update_release_cover_art(release_id):

    user, data = get_user_data(True)

    if user.artist is None:

        abort(404)
    try:

        current_release = Release.query.filter(Release.id==release_id).one_or_none()
        if current_release is None:
            abort(404)

        release_cover_art_file_name = S3_LOCATION + user.auth_id + "/" + str(release_id) + "/" + secure_filename(request.get_json()['file_name'])

        current_release.cover_art = release_cover_art_file_name

        current_release.update()

        return jsonify({
            'success': True,
        })

    except Exception as e:
        print(e)
        return jsonify({
            'success': False
        })

@bp.route('/releases/<int:release_id>/deploy', methods=['GET'])
@requires_log_in
def show_release_for_deployment(release_id):

    user, data = get_user_data(True)

    if user.artist is None:

        abort(404)

    try:

        current_release = Release.query.get(release_id)
        if current_release is None:
            abort(404)

        if user.artist.id != current_release.artist_id:
            abort(401)

        if current_release.smart_contract_address is None:

            release_data = current_release.short_public()

            user_track_count = len(Track.query.filter(Track.artist_id==user.artist.id).all())

            # Snippet to determine which smart contract factory address to use

            '''

            if user_track_count > 5:

                contract_factory_address = MusicakesContractFactory.query.get(2).smart_contract_address

            else:

                contract_factory_address = MusicakesContractFactory.query.get(1).smart_contract_address

            '''

            contract_factory_address = MusicakesContractFactory.query.get(1).smart_contract_address

            return render_template('releases/deploy_release.html',
                                    release=release_data,
                                    userinfo=data,
                                    contract_factory_address=contract_factory_address,
                                    chain_id=ETHEREUM_CHAIN_ID)

        else:

            abort(404)

    except Exception as e:
        print(e)
        abort(404)

    return redirect('/')


@bp.route('/releases/<int:release_id>/deploy', methods=['POST'])
@requires_log_in
def deploy_release_smart_contract(release_id):

    user, data = get_user_data(True)

    if user.artist is None:

        abort(404)

    try:

        transaction_hash = request.get_json()['transaction_hash']
        wallet_address = request.get_json()['wallet_address']

        from ..tasks import check_smart_contract_deployed

        task = check_smart_contract_deployed.apply_async(
                    args=(transaction_hash,
                            release_id))

        print("deploy contract task created")

        deploy_celery_task = DeployCeleryTask(
            task_id = task.id,
            user_id = user.id,
            release_id = release_id,
            wallet_address=wallet_address,
            transaction_hash = transaction_hash,
            is_confirmed = False
        )

        deploy_celery_task.insert()

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

@bp.route('/releases/<int:release_id>/edit', methods=['GET'])
@requires_log_in
def edit_release_form(release_id):

    user, data = get_user_data(True)

    if user.artist is None:

        abort(404)

    try:

        # Initialise form and populate with existing data
        release = Release.query.filter(Release.id==release_id).one_or_none()

        if user.artist.id != release.artist_id:
            abort(401)

        release_data = release.short_private()
        release_data['release_price'] = release.price
        release_data['release_description'] = release.description
        form = EditReleaseForm(data=release_data)

        # Get artist data

        artist = Artist.query.filter(Artist.user_id==user.id).one_or_none()
        artist_data = artist.short()

        # Get tracks data and populate form
        # Tracks need to be sorted so as to render in order based on track ID

        tracks = [track.short_public() for track in release.tracks]
        ordered_tracks = sorted(tracks, key=lambda track: track['id'])

        for i in range(len(tracks)):

            form.tracks[i].track_name.data = ordered_tracks[i]['track_name']
            form.tracks[i].track_price.data = ordered_tracks[i]['price']
            form.tracks[i].track_id.data = ordered_tracks[i]['id']
            form.tracks[i].track_youtube_url.data = ordered_tracks[i]['youtube_url']

        return render_template('forms/edit_release.html',
                                form=form,
                                artist=artist_data,
                                release=release_data,
                                userinfo=data)

    except Exception as e:
        print(e)
        abort(404)

@bp.route('/releases/<int:release_id>/edit', methods=['POST'])
@requires_log_in
def edit_release_form_submit(release_id):

    user, data = get_user_data(True)

    if user.artist is None:

        abort(404)

    release = Release.query.filter(Release.id==release_id).one_or_none()

    if release is None:

        abort(404)

    if user.artist.id != release.artist_id:
        abort(401)

    form = EditReleaseForm(request.form)

    try:

        if form.validate():

            # Get values from form

            release_name = form.release_name.data
            release_price = form.release_price.data
            release_description = form.release_description.data

            # Update release information


            release.name = release_name
            release.price = release_price
            release.description = release_description

            release.update()

            # Update tracks information

            for track_data in form.tracks.data:

                current_track_id = track_data['track_id']
                current_track = Track.query.filter(Track.id==current_track_id).one_or_none()

                current_track.name = track_data['track_name']
                current_track.price = track_data['track_price']

                if track_data['track_youtube_url'] == '':
                    current_track.youtube_url = None
                else:
                    current_track.youtube_url = track_data['track_youtube_url']

                current_track.update()

            flash('Your release information has been updated.')

        else:

            print(form.errors)

    except Exception as e:

        print(e)
        flash('Your release information could not be updated. Please try again.')

    return redirect(url_for('releases.edit_release_form', release_id=release_id))

@bp.route('/releases/<int:release_id>/edit_cover_art', methods=['GET'])
@requires_log_in
def edit_release_cover_art_form(release_id):

    user, data = get_user_data(True)

    if user.artist is None:

        abort(404)

    release = Release.query.filter(Release.id==release_id).one_or_none()
    release_data = release.short_private()

    form = EditReleaseCoverArtForm()

    return render_template('forms/edit_release_cover_art.html',
                            form=form,
                            userinfo=data,
                            release=release_data)

@bp.route('/releases/<int:release_id>/edit_cover_art', methods=['POST'])
@requires_log_in
def edit_release_cover_art_form_submit(release_id):

    user, data = get_user_data(True)

    if user.artist is None:

        abort(404)

    form = EditReleaseCoverArtForm()

    try:

        if form.validate():

            # Initialise form and populate with existing data
            release = Release.query.filter(Release.id==release_id).one_or_none()

            f = form.release_cover_art.data

            filename = "cover." + f.filename.split(".")[-1]

            modified_filename = user.auth_id + "/" + str(release_id) + "/" + filename

            upload_file(f, modified_filename)

            file_url = S3_LOCATION + modified_filename
            release.cover_art = file_url
            release.update()

            flash('The cover art has been updated.')

    except Exception as e:

        print(e)
        flash('The cover art could not be updated.')

    return redirect(url_for('releases.edit_release_cover_art_form', release_id=release_id))

@bp.route('/releases/<int:release_id>/download', methods=['GET'])
@requires_log_in
def download_release(release_id):

    release = Release.query.filter(Release.id==release_id).one_or_none()

    if release is None:

        abort(404)

    track_ids = [track.id for track in release.tracks]

    print(track_ids)

    return json.dumps({
        'track_ids': track_ids
    })

@bp.route('/releases/<int:release_id>/delete', methods=['POST'])
@requires_log_in
def delete_release(release_id):

    """
    Allow user to delete a release
    """

    user, data = get_user_data(True)

    if user.artist is None:

        abort(404)

    try:

        current_release = Release.query.filter(Release.id==release_id).one_or_none()

        # Extract S3 keys for files to be deleted and pass to delete_files()

        file_dict_list = []

        file_url_list = []

        file_url_list.append(current_release.cover_art)

        for track in current_release.tracks:
            file_url_list.append(track.download_url)

        for file_url in file_url_list:
            if file_url is not None:
                file_s3_path = file_url.split(S3_LOCATION)[-1]
                file_dict_list.append({'Key': file_s3_path})

        # Delete files if no purchases have been made

        tracks = Track.query.filter(Release.id==release_id)

        track_ids_list = [track.id for track in tracks]

        has_purchases = Purchase.query.filter(or_(Purchase.release_id==release_id, Purchase.track_id.in_(track_ids_list))). \
            join(Release). \
            join(Track).one_or_none()

        if has_purchases is None:

            delete_files(file_dict_list)

            # Delete entry

            current_release.delete()

        else:

            current_release.is_removed = True
            current_release.update()

            return jsonify({
                'success': True
            })

        return jsonify({
            'success': True,
        })

    except Exception as e:
        print("error while deleting")
        print(e)
        return jsonify({
            'success': False
        })


@bp.route('/releases/<int:release_id>/purchase', methods=['POST'])
@requires_log_in
def purchase_release(release_id):

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

        purchase_description = Release.query.filter(Release.id == release_id).one_or_none().purchase_description()

        purchase_celery_task = PurchaseCeleryTask(
            task_id = task.id,
            user_id = user.id,
            purchase_description = purchase_description,
            purchase_type = 'release',
            purchase_type_id = release_id,
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
