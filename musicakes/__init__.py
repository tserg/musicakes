import os
import time
import json
from urllib.parse import urlencode

from .decorators import *

from flask import (
    Flask,
    request,
    abort,
    jsonify,
    flash,
    render_template,
    redirect,
    url_for,
    session,
    send_file
)

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_cors import CORS
from flask_wtf import (
    Form,
    CSRFProtect
)

from datetime import timedelta

from .tasks import *
from .forms import *

from .models import (
    setup_db,
    User,
    Artist,
    Release,
    Track,
    Purchase,
    MusicakesContractFactory,
    PaymentToken,
    PurchaseCeleryTask
)

from urllib.request import urlopen
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode

# Import Celery

from celery import Celery
from celery.app.control import Control

# Import web3.py

from web3 import Web3, HTTPProvider
from web3.exceptions import TransactionNotFound

from dotenv import load_dotenv

load_dotenv()

# Secret key

SECRET_KEY = os.getenv('SECRET_KEY', 'Does not exist')

# Environment variables for Auth0

AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN', 'Does not exist')
AUTH0_ACCESS_TOKEN_URL = os.getenv('AUTH0_ACCESS_TOKEN_URL', 'Does not exist')
AUTH0_AUTHORIZE_URL = os.getenv('AUTH0_AUTHORIZE_URL', 'Does not exist')
AUTH0_CLIENT_ID = os.getenv('CLIENT_ID', 'Does not exist')
AUTH0_CLIENT_SECRET = os.getenv('CLIENT_SECRET', 'Does not exist')
AUTH0_USER_INFO_URL = os.getenv('AUTH0_USER_INFO_URL', 'Does not exist')
ALGORITHMS = os.getenv('ALGORITHMS', 'Does not exist')
API_AUDIENCE = os.getenv('API_AUDIENCE', 'Does not exist')
REDIRECT_URL = os.getenv('REDIRECT_URL', 'Does not exist')

# Environment variable for AWS S3 location

S3_LOCATION = os.getenv('S3_LOCATION', 'Does not exist')

# Environment variables for Ethereum blockchain

ETHEREUM_CHAIN_ID = os.getenv('ETHEREUM_CHAIN_ID', 'Does not exist')

# Environment variables for Celery and Redies

CELERY_BROKER_URL = os.getenv('REDIS_URL', 'Does not exist')
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'Does not exist')

# Environment variables for Infura

WEB3_INFURA_PROJECT_ID = os.getenv('WEB3_INFURA_PROJECT_ID', 'Does not exist')
WEB3_INFURA_API_SECRET = os.getenv('WEB3_INFURA_API_SECRET', 'Does not exist')
#WEB3_PROVIDER_URI = os.getenv('WEB3_PROVIDER_URI', 'Does not exist')

# Environment variables for app

RELEASES_PER_PAGE = 10
TRACKS_PER_PAGE = 10
ARTISTS_PER_PAGE = 10

def create_app(test_config=None):

    # create and configure the app
    flask_app = Flask(__name__, instance_relative_config=True)

    from musicakes.errors import bp as errors_bp
    flask_app.register_blueprint(errors_bp)

    from musicakes.aws_s3 import bp as aws_s3_bp
    flask_app.register_blueprint(aws_s3_bp)

    try:
        os.makedirs(flask_app.instance_path)
    except OSError:
        pass

    flask_app.config['SECRET_KEY'] = SECRET_KEY
    flask_app.config['CELERY_BROKER_URL'] = CELERY_BROKER_URL
    flask_app.config['CELERY_RESULT_BACKEND'] = CELERY_RESULT_BACKEND
    flask_app.config['CELERY_SEND_EVENTS'] = True

    celery = make_celery(flask_app)
    celery_control = Control(celery)

    csrf = CSRFProtect()
    csrf.init_app(flask_app)

    db=SQLAlchemy()

    setup_db(flask_app)

    CORS(flask_app, resources={r"/*": {"origins": "http://localhost:5000"}})

    oauth = OAuth(flask_app)

    auth0 = oauth.register(
        'auth0',
        client_id=AUTH0_CLIENT_ID,
        client_secret=AUTH0_CLIENT_SECRET,
        api_base_url=AUTH0_DOMAIN,
        access_token_url=AUTH0_ACCESS_TOKEN_URL,
        authorize_url=AUTH0_AUTHORIZE_URL,
        client_kwargs={
            'scope': 'openid profile email',
        },
    )
    ###################################################

    # Auth

    ###################################################

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

    def has_purchased_track(_userId, _trackId, _releaseId):

        purchased_current_track = Purchase.query.filter(Purchase.track_id==_trackId). \
                filter(Purchase.user_id==_userId). \
                join(Release).one_or_none()

        purchased_release_with_current_track = Purchase.query.filter(Purchase.release_id==_releaseId). \
                filter(Purchase.user_id==_userId). \
                join(Release).one_or_none()

        if purchased_current_track or purchased_release_with_current_track:
            return True

        return False

    def has_purchased_release(_userId, _releaseId):

        purchased_current_release = Purchase.query.filter(Purchase.release_id==_releaseId). \
                filter(Purchase.user_id==_userId). \
                join(Release).one_or_none()

        if purchased_current_release is not None:
            return True

        return False

    ###################################################

    # Routes

    ###################################################


    # /server.py

    # Here we're using the /callback route.
    @flask_app.route('/callback')
    def callback_handling():
        # Handles response from token endpoint
        token = auth0.authorize_access_token()
        print(token)
        print(token['access_token'])
        resp = auth0.get(AUTH0_USER_INFO_URL)
        print(resp)
        userinfo = resp.json()
        print(userinfo)

        # Store the user information in flask session.
        session['token'] = token
        session['jwt_payload'] = userinfo
        session['profile'] = {
            'user_id': userinfo['sub'],
            'name': userinfo['name'],
            'picture': userinfo['picture']
        }
        return redirect('/home')

    @flask_app.route('/login')
    def login():
        return auth0.authorize_redirect(redirect_uri=REDIRECT_URL,
                                        audience=API_AUDIENCE)

    @flask_app.route('/logout')
    def logout():
        # Clear session stored data
        session.clear()
        # Redirect user to logout endpoint
        params = {'returnTo': url_for('index', _external=True), 'client_id': AUTH0_CLIENT_ID}
        return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

    @flask_app.route('/')
    def index():

        data = get_user_data()

        if data is not None:

            return redirect(url_for('home'))

        return render_template('pages/index.html', userinfo=data)


    # after logging in

    @flask_app.route('/home', methods=['GET'])
    @requires_log_in
    def home():

        data = get_user_data()

        if data is None:

            return redirect(url_for('create_user_form'))

        latest_releases = Release.query.join(Release.tracks) \
                            .having(func.count(Track.id) > 0) \
                            .group_by(Release.id) \
                            .order_by(Release.created_on.desc()).limit(5).all()

        latest_releases_data = [release.short_public() for release in latest_releases]

        return render_template('pages/home.html', userinfo=data, latest_releases=latest_releases_data)

    ###################################################

    # Celery

    ###################################################

    @celery.task(bind=True)
    def check_transaction_hash_confirmed(self, _transactionHash, _userId):

        if ETHEREUM_CHAIN_ID == 1:
            from web3.auto.infura import w3
        else:
            from web3.auto.infura.ropsten import w3

        print(_transactionHash)

        print("w3 connection: ")
        print(w3.isConnected())

        current_check = 0
        check_duration = 30

        # Checks for 15 minutes based on 30 intervals of 30 seconds each

        while current_check < check_duration:

            try:
                receipt = w3.eth.getTransactionReceipt(_transactionHash)

            except TransactionNotFound as e:

                # Retries after 30 seconds if transaction is not found

                time.sleep(30)
                current_check += 1
                continue

            except Exception as o:
                print(o)
                continue

            break

        if receipt:

            print(receipt)

            transactionHash = receipt.transactionHash.hex()
            paid = Web3.fromWei(Web3.toInt(hexstr=receipt.logs[0].data), 'ether')
            walletAddress = receipt['from']

            # Checks if wallet address matches

            task_id = self.request.id

            purchase_celery_task = PurchaseCeleryTask.query.filter(PurchaseCeleryTask.task_id==task_id).one_or_none()

            # Checks if wallet address is same as when transaction hash was first submitted

            if str(walletAddress).lower() == purchase_celery_task.wallet_address:

                # Update the task status to confirmed

                purchase_celery_task.is_confirmed = True

                purchase_celery_task.update()

                # Add the purchase depending on whether it is a track or release

                if purchase_celery_task.purchase_type == 'release':

                    purchase = Purchase(
                            user_id = _userId,
                            release_id = purchase_celery_task.purchase_type_id,
                            paid = paid,
                            wallet_address = walletAddress,
                            transaction_hash = transactionHash
                        )

                    purchase.insert()

                elif purchase_celery_task.purchase_type == 'track':

                    purchase = Purchase(
                            user_id = _userId,
                            track_id = purchase_celery_task.purchase_type_id,
                            paid = paid,
                            wallet_address = walletAddress,
                            transaction_hash = transactionHash
                        )

                    purchase.insert()

        return True

    ###################################################

    # General

    ###################################################

    @flask_app.route('/about', methods=['GET'])
    def show_about_us():

        data = get_user_data()

        return render_template('pages/about.html', userinfo=data)


    @flask_app.route('/faq', methods=['GET'])
    def show_faq():

        data = get_user_data()

        return render_template('pages/faq.html', userinfo=data)

    @flask_app.route('/terms', methods=['GET'])
    def show_terms_of_use():

        data = get_user_data()

        return render_template('pages/terms.html', userinfo=data)

    @flask_app.route('/privacy', methods=['GET'])
    def show_privacy_policy():

        data = get_user_data()

        return render_template('pages/privacy.html', userinfo=data)

    @flask_app.route('/search', methods=['GET'])
    def search():

        data = get_user_data()
        search_term = request.args.get('query')

        if search_term == '':

            return render_template(
                'pages/search_results.html',
                userinfo=data,
                artists_results=None,
                releases_results=None,
                tracks_results=None
            )

        try:

            artists_search_results = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')) \
                                        .order_by(Artist.created_on.desc()) \
                                        .all()

            releases_search_results = Release.query.filter(Release.name.ilike('%' + search_term + '%')) \
                                        .order_by(Release.created_on.desc()) \
                                        .all()

            tracks_search_results = Track.query.filter(Track.name.ilike('%' + search_term + '%')) \
                                        .order_by(Track.created_on.desc()) \
                                        .all()

            formatted_artist_search_results = [artist.short() for artist in artists_search_results]
            formatted_releases_search_results = [release.short_public() for release in releases_search_results]
            formatted_tracks_search_results = [track.short_public() for track in tracks_search_results]

            return render_template(
                'pages/search_results.html',
                userinfo=data,
                artists_results=formatted_artist_search_results,
                releases_results=formatted_releases_search_results,
                tracks_results=formatted_tracks_search_results
            )

        except Exception as e:
            print(e)

        return render_template('pages/search_results.html', userinfo=data)


    ###################################################

    # Account

    ###################################################

    @flask_app.route('/account', methods=['GET'])
    @requires_log_in
    def show_account():

        user, data = get_user_data(True)

        if data is None:

            abort(404)

        artist = Artist.query.filter(Artist.user_id==user.id).one_or_none()

        if artist:

            data['artist_name'] = artist.name

        else:

            data['artist_name'] = None

        pending_transactions = PurchaseCeleryTask.query.filter(PurchaseCeleryTask.user_id==user.id) \
                                .filter(PurchaseCeleryTask.is_confirmed==False) \
                                .filter(PurchaseCeleryTask.is_visible==True) \
                                .order_by(PurchaseCeleryTask.started_on.desc()).limit(10).all()

        transaction_history = PurchaseCeleryTask.query.filter(PurchaseCeleryTask.user_id==user.id) \
                                .filter(PurchaseCeleryTask.is_confirmed==True) \
                                .filter(PurchaseCeleryTask.is_visible==True) \
                                .order_by(PurchaseCeleryTask.started_on.desc()).limit(10).all()

        return render_template(
            'pages/show_account.html',
            userinfo=data,
            transaction_history = transaction_history,
            pending_transactions = pending_transactions
        )

    @flask_app.route('/account/edit', methods=['GET'])
    @requires_log_in
    def edit_user_form():

        data = get_user_data()

        if data is None:

            abort(404)

        form = EditUserForm()

        return render_template('forms/edit_user.html',
                                form=form,
                                userinfo=data)

    @flask_app.route('/account/edit', methods=['POST'])
    @requires_log_in
    def edit_user_submission():

        user, data = get_user_data(True)

        form = EditUserForm()

        if not user:

            abort(404)

        try:

            if form.validate():

                f = form.profile_picture.data

                filename = "profile_picture." + f.filename.split(".")[-1]

                modified_filename = user.auth_id + "/" + filename

                upload_file(f, modified_filename)

                file_url = S3_LOCATION + modified_filename
                user.profile_picture = file_url
                user.update()

                flash('Your profile has been updated.')

        except Exception as e:

            print(e)
            flash('Your profile could not be updated.')

        return redirect(url_for('show_account'))


    @flask_app.route('/pending_transactions', methods=['GET'])
    def get_pending_transactions():


        """
        Retrieves a list of pending transactions when user clicks on notifications button
        """

        user, data = get_user_data(True)

        if data is None:

            abort(404)

        try:

            pending_purchases = PurchaseCeleryTask.query.filter(
                                            PurchaseCeleryTask.user_id == user.id) \
                                            .filter(PurchaseCeleryTask.is_confirmed == False) \
                                            .filter(PurchaseCeleryTask.is_visible == True) \
                                            .order_by(PurchaseCeleryTask.started_on.desc()) \
                                            .all()

            pending_purchases_formatted = [pending_purchase.short() for pending_purchase in pending_purchases]

            return jsonify({
                'success': True,
                'chain_id': ETHEREUM_CHAIN_ID,
                'data': pending_purchases_formatted
            })

        except:
            return jsonify({
                'success': False
            })

    @flask_app.route('/transactions/<string:transaction_hash>/hide', methods=['POST'])
    def hide_transaction(transaction_hash):

        """
        Hides a transaction from a user's transaction history
        """

        data = get_user_data()

        if data is None:

            abort(404)

        try:
            current_task = PurchaseCeleryTask.query.filter(PurchaseCeleryTask.transaction_hash==transaction_hash).one_or_none()

            if current_task:
                current_task.is_visible=False
                current_task.update()

            return jsonify({
                'success': True
            })


        except Exception as e:
            print(e)
            return jsonify({
                'success': False
            })

    @flask_app.route('/transactions/<string:transaction_hash>/update', methods=['POST'])
    def update_transaction(transaction_hash):
        """
        Updates a pending transaction's status
        """

        user, data = get_user_data(True)

        if data is None:

            abort(404)

        try:

            current_task = PurchaseCeleryTask.query.filter(PurchaseCeleryTask.transaction_hash==transaction_hash).one_or_none()

            if current_task:

                purchase_description = current_task.purchase_description
                purchase_type = current_task.purchase_type
                purchase_type_id = current_task.purchase_type_id
                wallet_address = current_task.wallet_address
                transaction_hash = current_task.transaction_hash


                celery_control.revoke(current_task.task_id, terminate=True)
                current_task.delete()

                new_task = check_transaction_hash_confirmed.apply_async(
                            args=(current_task.transaction_hash,
                                    user.id))

                purchase_celery_task = PurchaseCeleryTask(
                    task_id = new_task.id,
                    user_id = user.id,
                    purchase_description = purchase_description,
                    purchase_type = purchase_type,
                    purchase_type_id = purchase_type_id,
                    wallet_address=wallet_address,
                    transaction_hash = transaction_hash,
                    is_confirmed = False
                )

                purchase_celery_task.insert()

                return jsonify({
                    'success': True
                })


        except Exception as e:
            print(e)
            return jsonify({
                'success': False
            })

    ###################################################

    # Users

    ###################################################

    @flask_app.route('/users/<int:user_id>', methods=['GET'])
    def show_user(user_id):
        try:
            user_data = get_user_data()

            current_user = User.query.get(user_id)
            if current_user is None:
                abort(404)

            data = current_user.short_private()

            data['purchased_releases'], data['purchased_tracks'] = current_user.get_purchases()

            return render_template('pages/show_user.html', user=data, userinfo=user_data)

        except Exception as e:
            print(e)
            abort(404)

    @flask_app.route('/users/create', methods=['GET'])
    @requires_log_in
    def create_user_form():
        form = UserForm()

        return render_template('forms/new_user.html', form=form)


    @flask_app.route('/users/create', methods=['POST'])
    @requires_log_in
    def create_user_submission():
        form = UserForm(request.form)

        auth_id = session['profile']['user_id'][6:]

        try:

            if form.validate():

                new_username = form.username.data.lower()

                if User.query.filter(User.username==new_username).one_or_none():

                    flash('The username has been taken. Please choose another username.')

                    return redirect(url_for('create_user_form'))

                new_user = User(
                    auth_id = auth_id,
                    username = new_username
                )

                new_user.insert()

                flash('Your account has been successfully created.')

                return redirect(url_for('show_account'))

        except Exception as e:

            print(e)
            flash('Your account could not be created.')

            return redirect(url_for('create_user_form'))

    ###################################################

    # Artists

    ###################################################

    @flask_app.route('/artists', methods=['GET'])
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

                return render_template('pages/artists.html', artists=formatted_all_artists[start:end], userinfo=data)

            else:

                abort(404)

        except Exception as e:
            print(e)
            abort(404)

        return redirect('/')

    @flask_app.route('/artists/<int:artist_id>', methods=['GET'])
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

            return render_template('pages/show_artist.html',
                                    artist=artist_data,
                                    userinfo=data,
                                    creator=creator,
                                    chain_id=ETHEREUM_CHAIN_ID,
                                    payment_token_address=payment_token_address)

        except Exception as e:
            print(e)
            abort(404)

        return redirect('/')

    @flask_app.route('/artists/create', methods=['GET'])
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

    @flask_app.route('/artists/create', methods=['POST'])
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

    @flask_app.route('/artists/<int:artist_id>/edit', methods=['GET'])
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

            return render_template('forms/edit_artist.html', form=form, artist=artist_data, userinfo=data)

        except Exception as e:
            print(e)
            abort(404)

        return redirect('/')

    @flask_app.route('/artists/<int:artist_id>/edit', methods=['PUT'])
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

    @flask_app.route('/artists/<int:artist_id>/edit_2', methods=['POST'])
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

                # Split soundcloud url to get username in order to input into widget

                soundcloud_url_processed = str(soundcloud_url).split("/")[-1]

                current_artist.soundcloud_url = soundcloud_url_processed
                current_artist.facebook_url = facebook_url
                current_artist.instagram_url = instagram_url
                current_artist.wallet_address = wallet_address
                current_artist.update()

                return redirect(url_for('edit_artist', artist_id=artist_id))

            else:

                errors = [error[0] for field, error in form.errors.items()]
                for error in errors:
                    flash(error)
                return redirect(url_for('edit_artist', artist_id=artist_id))

        except Exception as e:
            print(e)
            abort(404)

        return redirect('/')

    ###################################################

    # Purchases

    ###################################################

    @flask_app.route('/account/purchases', methods=['GET'])
    @requires_log_in
    def show_purchases():

        user, data = get_user_data(True)

        if data is None:

            abort(404)

        data['purchased_releases'], data['purchased_tracks'] =  user.get_purchases()

        return render_template('pages/show_purchases.html', userinfo=data)

    @flask_app.route('/releases/<int:release_id>/purchase', methods=['POST'])
    @requires_log_in
    def purchase_release(release_id):

        user, data = get_user_data(True)

        if data is None:

            abort(404)

        try:

            transaction_hash = request.get_json()['transaction_hash']
            wallet_address = request.get_json()['wallet_address']

            task = check_transaction_hash_confirmed.apply_async(
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

    @flask_app.route('/tracks/<int:track_id>/purchase', methods=['POST'])
    @requires_log_in
    def purchase_track(track_id):

        user, data = get_user_data(True)

        if data is None:

            abort(404)

        try:

            transaction_hash = request.get_json()['transaction_hash']
            wallet_address = request.get_json()['wallet_address']

            task = check_transaction_hash_confirmed.apply_async(
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
            return jsonify({
                'success': False
            })

    @flask_app.route('/tracks/<int:track_id>/download', methods=['GET'])
    @requires_log_in
    def download_purchased_track(track_id):

        user, data = get_user_data(True)

        if data is None:

            abort(404)

        # checks if user has purchased the current track

        track = Track.query.filter(Track.id==track_id).one_or_none()
        release = Release.query.filter(Release.id==track.release_id).one_or_none()

        if track is None or release is None:

            abort(404)

        track_purchase = has_purchased_track(user.id, track.id, release.id)

        release_purchase = has_purchased_release(user.id, release.id)

        if track_purchase is False and release_purchase is False:

            abort(404)

        # download file

        artist_user = Artist.query.filter(Artist.id==release.artist_id).one_or_none()

        url_components = track.download_url.rsplit('/')

        filename = secure_filename(url_components[-1])

        key = url_components[-2] + "/" + filename

        try:

            output = download_track(key, filename)

            return send_file(output, as_attachment=True)

        except Exception as e:

            print(e)
            flash('Unable to download file.')

        return redirect(url_for('show_purchases'))

    """

    # Not in use due to lack of server

    @flask_app.route('/releases/<int:release_id>/download', methods=['GET'])
    @requires_log_in
    def download_purchased_release(release_id):

        user, data = get_user_data(True)

        if data is None:

            abort(404)

        # checks if user has purchased the current release

        release = Release.query.filter(Release.id==release_id).one_or_none()

        if release is None:

            abort(404)

        release_purchase = has_purchased_release(user.id, release.id)

        if release_purchase is False:

            abort(404)

        # download files

        artist_user = Artist.query.filter(Artist.id==release.artist_id).one_or_none()

        keys = []
        filenames = []

        for track in release.tracks:

            filename = track.download_url.rsplit('/', 1)[-1]

            key = artist_user.user.auth_id + "/" + filename

            keys.append(key)
            filenames.append(filename)

        zip_file_name = str(release.artist.name) + "_" + str(release.name)

        try:

            output = download_release(keys, filenames, zip_file_name)

            return send_file(output, as_attachment=True)

        except Exception as e:

            print(e)
            flash('Unable to download file.')

        return redirect(url_for('show_purchases'))

    """

    ###################################################

    # Releases

    ###################################################

    @flask_app.route('/releases', methods=['GET'])
    def get_releases():

        data = get_user_data()

        try:

            # page count

            page = request.args.get('page', 1, type=int)

            start = (page-1)*RELEASES_PER_PAGE
            end = start + RELEASES_PER_PAGE

            all_releases = Release.query.join(Release.tracks) \
                            .having(func.count(Track.id) > 0) \
                            .group_by(Release.id) \
                            .order_by(Release.created_on.desc()).all()

            formatted_all_releases = [release.short_public()
                                      for release in all_releases]

            releases_count = len(formatted_all_releases)

            if start + 1 <= releases_count:

                return render_template('pages/releases.html', releases=formatted_all_releases[start:end], userinfo=data)

            else:
                abort(404)

        except Exception as e:
            print(e)
            abort(404)

    @flask_app.route('/releases/<int:release_id>', methods=['GET'])
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

                data['has_purchased'] = has_purchased_release(user.id, release_id)

                creator = (current_release.artist.user.id == user.id)

            else:
                creator = False

            return render_template('pages/show_release.html',
                                    release=release_data,
                                    userinfo=data,
                                    creator=creator,
                                    chain_id=ETHEREUM_CHAIN_ID,
                                    artist=artist_data)

        except Exception as e:
            print(e)
            abort(404)

        return redirect('/')

    @flask_app.route('/releases/create', methods=['GET'])
    @requires_log_in
    def create_release_presubmission_form():

        user, data = get_user_data(True)

        if user.artist is None:

            abort(404)

        form = ReleasePresubmissionForm()

        return render_template('forms/new_release_presubmission.html', form=form, userinfo=data)

    @flask_app.route('/releases/create', methods=['POST'])
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

    @flask_app.route('/releases/create_2', methods=['POST'])
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

    @flask_app.route('/releases/<int:release_id>/update_cover_art', methods=['POST'])
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

    @flask_app.route('/releases/<int:release_id>/deploy', methods=['GET'])
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

                return render_template('pages/deploy_release.html',
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


    @flask_app.route('/releases/<int:release_id>/deploy', methods=['POST'])
    @requires_log_in
    def deploy_release_smart_contract(release_id):

        user, data = get_user_data(True)

        if user.artist is None:

            abort(404)

        try:

            smart_contract_address = request.get_json()['smart_contract_address']

            release = Release.query.filter(Release.id==release_id).one_or_none()

            if release is None:

                abort(404)

            if user.artist.id != release.artist_id:
                abort(401)

            release.smart_contract_address = smart_contract_address
            release.update()

            return jsonify({
                'success': True,
                'release_id': release.id,
                'smart_contract_address': release.smart_contract_address
            })

        except Exception as e:
            print(e)
            return jsonify({
                'success': False
            })

    @flask_app.route('/releases/<int:release_id>/edit', methods=['GET'])
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

    @flask_app.route('/releases/<int:release_id>/edit', methods=['POST'])
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

        return redirect(url_for('edit_release_form', release_id=release_id))

    @flask_app.route('/releases/<int:release_id>/edit_cover_art', methods=['GET'])
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

    @flask_app.route('/releases/<int:release_id>/edit_cover_art', methods=['POST'])
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

        return redirect(url_for('edit_release_cover_art_form', release_id=release_id))

    @flask_app.route('/releases/<int:release_id>/download', methods=['GET'])
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

    @flask_app.route('/releases/<int:release_id>/delete', methods=['POST'])
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

            # Delete files

            delete_files(file_dict_list)

            # Delete entry

            current_release.delete()

            return jsonify({
                'success': True,
            })

        except Exception as e:
            print("error while deleting")
            print(e)
            return jsonify({
                'success': False
            })


    ###################################################

    # Tracks

    ###################################################

    @flask_app.route('/tracks', methods=['GET'])
    def get_tracks():

        data = get_user_data()

        try:

            # page count

            page = request.args.get('page', 1, type=int)

            start = (page-1)*TRACKS_PER_PAGE
            end = start + TRACKS_PER_PAGE

            all_tracks = Track.query.order_by(Track.created_on.desc()).all()

            formatted_all_tracks = [track.short_public() for track in all_tracks]

            tracks_count = len(formatted_all_tracks)

            if start + 1 <= tracks_count:

                return render_template('/pages/tracks.html', tracks=formatted_all_tracks[start:end], userinfo=data)

            else:
                abort(404)

        except:

            abort(404)

    @flask_app.route('/tracks/<int:track_id>', methods=['GET'])
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

                data['has_purchased'] = has_purchased_track(user.id, track_id, current_release.id)

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

    @flask_app.route('/tracks/create', methods=['POST'])
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

    return flask_app

app = create_app()
celery = make_celery(app)
