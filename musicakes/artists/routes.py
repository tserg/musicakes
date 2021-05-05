import os

from flask import (
    flash,
    request,
    abort,
    jsonify,
    render_template,
    redirect,
    url_for
)

from werkzeug.utils import secure_filename

from dotenv import load_dotenv

from . import bp

from ..models import (
    Artist,
    Release,
    Track,
    PaymentToken
)

from ..utils.session_utils import (
    get_user_data
)

from ..decorators import (
    requires_log_in
)

from .forms import (
    ArtistForm,
    EditArtistForm
)

load_dotenv()

# Environment variables for Ethereum blockchain

ETHEREUM_CHAIN_ID = os.getenv('ETHEREUM_CHAIN_ID', 'Does not exist')

ARTISTS_PER_PAGE = 10

@bp.route('/artists', methods=['GET'])
def get_artists():

    data = get_user_data()

    try:

        # page count

        page = request.args.get('page', 1, type=int)

        start = (page-1)*ARTISTS_PER_PAGE
        end = start + ARTISTS_PER_PAGE

        all_artists = Artist.query.order_by(Artist.created_on.desc()).all()

        formatted_all_artists = [artist.short() for artist in all_artists]

        artists_count = len(formatted_all_artists)

        if start + 1 <= artists_count:

            return render_template('artists/artists.html', artists=formatted_all_artists[start:end], userinfo=data)

        else:

            abort(404)

    except Exception as e:
        print(e)
        abort(404)

    return redirect('/')

@bp.route('/artists/<int:artist_id>', methods=['GET'])
def show_artist(artist_id):

    user, data = get_user_data(True)

    if user:

        creator = (user.artist.id == artist_id)

    else:

        creator = False

    try:

        current_artist = Artist.query.filter(Artist.id==artist_id).one_or_none()
        if current_artist is None:
            abort(404)

        artist_data = current_artist.short()

        payment_token_address = PaymentToken.query.get(1).smart_contract_address

        return render_template('artists/show_artist.html',
                                artist=artist_data,
                                userinfo=data,
                                creator=creator,
                                chain_id=ETHEREUM_CHAIN_ID,
                                payment_token_address=payment_token_address)

    except Exception as e:
        print(e)
        abort(404)

    return redirect('/')

@bp.route('/artists/create', methods=['GET'])
@requires_log_in
def create_artist_form():

    user, data = get_user_data(True)

    artist = Artist.query.filter(Artist.user_id==user.id).one_or_none()

    if artist:

        data['artist_name'] = artist.name

    else:

        data['artist_name'] = None

    form = ArtistForm()

    return render_template('forms/new_artist.html', form=form, userinfo=data)

@bp.route('/artists/create', methods=['POST'])
@requires_log_in
def create_artist():

    form = ArtistForm(request.form)

    user, data = get_user_data(True)

    try:

        if form.validate():

            # Split soundcloud url to get username in order to input into widget

            artist_soundcloud_url = str(form.artist_soundcloud_url.data).split("/")[-1]

            new_artist = Artist(
                name = form.artist_name.data,
                country = form.artist_country.data,
                user_id = user.id,
                soundcloud_url = artist_soundcloud_url,
                facebook_url = form.artist_facebook_url.data
            )

            new_artist.insert()
            return redirect(url_for('edit_artist', artist_id=new_artist.id))

        else:

            errors = [error[0] for field, error in form.errors.items()]
            for error in errors:
                flash(error)
            return redirect(url_for('create_artist_form'))

    except Exception as e:

        print(e)
        flash('Your artist profile could not be created.')
        return redirect(url_for('create_artist_form'))

    return redirect(url_for('create_artist_form'))

@bp.route('/artists/<int:artist_id>/edit', methods=['GET'])
@requires_log_in
def edit_artist(artist_id):

    user, data = get_user_data(True)

    if user.artist.id != artist_id:
        abort(401)

    try:

        current_artist = Artist.query.filter(Artist.id==artist_id).one_or_none()
        if current_artist is None:
            abort(404)

        artist_data = current_artist.short()
        form = EditArtistForm()

        # Populate form with external links if available

        if current_artist.soundcloud_url is not None:
            form.artist_soundcloud_url.data = "https://soundcloud.com/" + current_artist.soundcloud_url
        if current_artist.facebook_url is not None:
            form.artist_facebook_url.data = current_artist.facebook_url
        if current_artist.instagram_url is not None:
            form.artist_instagram_url.data = current_artist.instagram_url
        if current_artist.wallet_address is not None:
            form.artist_wallet_address.data = current_artist.wallet_address

        form.artist_country.data = current_artist.country

        return render_template('forms/edit_artist.html', form=form, artist=artist_data, userinfo=data)

    except Exception as e:
        print(e)
        abort(404)

    return redirect('/')

@bp.route('/artists/<int:artist_id>/edit', methods=['PUT'])
@requires_log_in
def edit_artist_picture(artist_id):

    user, data = get_user_data(True)

    if user.artist is None:

        abort(404)

    if user.artist.id != artist_id:

        abort(401)

    try:

        current_artist = Artist.query.filter(Artist.id==artist_id).one_or_none()
        if current_artist is None:
            abort(404)

        artist_picture_file_name = S3_LOCATION + user.auth_id + "/" + secure_filename(request.get_json()['file_name'])

        current_artist.artist_picture = artist_picture_file_name
        current_artist.update()

        return jsonify({
            'success': True,
        })

    except Exception as e:
        print(e)
        return jsonify({
            'success': False
        })

@bp.route('/artists/<int:artist_id>/edit_2', methods=['POST'])
@requires_log_in
def edit_artist_details(artist_id):
    form = EditArtistForm(request.form)

    user, data = get_user_data(True)

    if user.artist is None:

        abort(404)

    if user.artist.id != artist_id:

        abort(401)

    try:

        current_artist = Artist.query.filter(Artist.id==artist_id).one_or_none()
        if current_artist is None:
            abort(404)

        if form.validate():

            wallet_address = form.artist_wallet_address.data

            print(wallet_address)

            soundcloud_url = form.artist_soundcloud_url.data
            facebook_url = form.artist_facebook_url.data
            instagram_url = form.artist_instagram_url.data
            artist_country = form.artist_country.data

            # Split soundcloud url to get username in order to input into widget

            soundcloud_url_processed = str(soundcloud_url).split("/")[-1]

            current_artist.soundcloud_url = soundcloud_url_processed
            current_artist.facebook_url = facebook_url
            current_artist.instagram_url = instagram_url
            current_artist.wallet_address = wallet_address
            current_artist.country = artist_country
            current_artist.update()

            return redirect(url_for('artists.edit_artist', artist_id=artist_id))

        else:

            errors = [error[0] for field, error in form.errors.items()]
            for error in errors:
                flash(error)
            return redirect(url_for('artists.edit_artist', artist_id=artist_id))

    except Exception as e:
        print(e)
        abort(404)

    return redirect('/')
