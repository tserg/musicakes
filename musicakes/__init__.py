import os
import json
from urllib.parse import urlencode

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

from werkzeug.utils import secure_filename

from .tasks import make_celery
from .forms import (
    UserForm
)

from .models import (
    setup_db,
    User,
    Artist,
    Release,
    Track,
    Purchase,
    PurchaseCeleryTask,
    DeployCeleryTask
)

from authlib.integrations.flask_client import OAuth

# Import Celery

from celery import Celery
from celery.app.control import Control

# Import web3.py

from web3 import Web3

from dotenv import load_dotenv

# Import utils

from .aws_s3.s3_utils import (
    upload_file,
    download_track,
    delete_files
)

from .decorators import (
    requires_log_in
)

from .web3_utils import (
    check_transaction_receipt
)

from .session_utils import (
    get_user_data
)

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


def create_app(test_config=None):

    # create and configure the app
    flask_app = Flask(__name__, instance_relative_config=True)

    from musicakes.errors import bp as errors_bp
    flask_app.register_blueprint(errors_bp)

    from musicakes.aws_s3 import bp as aws_s3_bp
    flask_app.register_blueprint(aws_s3_bp)

    from musicakes.boilerplate import bp as boilerplate_bp
    flask_app.register_blueprint(boilerplate_bp)

    from musicakes.artists import bp as artists_bp
    flask_app.register_blueprint(artists_bp)

    from musicakes.tracks import bp as tracks_bp
    flask_app.register_blueprint(tracks_bp)

    from musicakes.releases import bp as releases_bp
    flask_app.register_blueprint(releases_bp)

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
            .filter(Release.is_removed == False) \
            .having(func.count(Track.id) > 0) \
            .group_by(Release.id) \
            .order_by(Release.created_on.desc()).limit(5).all()

        latest_releases_data = [release.short_public() for release in latest_releases]

        return render_template('pages/home.html', userinfo=data, latest_releases=latest_releases_data)

    ###################################################

    # Celery

    ###################################################

    @celery.task(bind=True)
    def check_smart_contract_deployed(self, _transactionHash, _releaseId):

        receipt = check_transaction_receipt(ETHEREUM_CHAIN_ID, _transactionHash)

        if receipt:
            print("deploy celery task receipt")
            print(receipt)
            print("logs")
            print(receipt.logs[0].address)

            transactionHash = receipt.transactionHash.hex()
            smart_contract_address = receipt.logs[0].address

            task_id = self.request.id

            deploy_celery_task = DeployCeleryTask.query.filter(DeployCeleryTask.task_id==task_id).one_or_none()

            deploy_celery_task.is_confirmed = True
            deploy_celery_task.update()

            release = Release.query.get(_releaseId)
            release.smart_contract_address = smart_contract_address
            release.update()

        return True

    @celery.task(bind=True)
    def check_purchase_transaction_confirmed(self, _transactionHash, _userId):

        receipt = check_transaction_receipt(ETHEREUM_CHAIN_ID, _transactionHash)

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

    @flask_app.route('/search', methods=['GET'])
    def search():

        data = get_user_data()
        search_term = request.args.get('query')

        if search_term == '':

            return render_template(
                'pages/search_results.html',
                userinfo=data,
                users_results=None,
                artists_results=None,
                releases_results=None,
                tracks_results=None
            )

        try:

            users_search_results = User.query.filter(User.username.ilike('%' + search_term + '%')) \
                                    .all()

            artists_search_results = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')) \
                                        .order_by(Artist.created_on.desc()) \
                                        .all()

            # Filter for releases that have been removed by artists

            releases_search_results = Release.query.filter(
                Release.name.ilike('%' + search_term + '%'),
                Release.is_removed == False
                ) \
                .order_by(Release.created_on.desc()) \
                .all()

            tracks_search_results = Track.query.join(Track.release). \
                filter(
                Track.name.ilike('%' + search_term + '%'),
                Release.is_removed == False
                ) \
                .order_by(Track.created_on.desc()) \
                .all()

            formatted_artist_search_results = [artist.short() for artist in artists_search_results]
            formatted_releases_search_results = [release.short_public() for release in releases_search_results]
            formatted_tracks_search_results = [track.short_public() for track in tracks_search_results]
            formatted_users_search_results = [user.short_public() for user in users_search_results]

            return render_template(
                'pages/search_results.html',
                userinfo=data,
                users_results=formatted_users_search_results,
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
                                .order_by(PurchaseCeleryTask.started_on.desc()).limit(5).all()

        transaction_history = PurchaseCeleryTask.query.filter(PurchaseCeleryTask.user_id==user.id) \
                                .filter(PurchaseCeleryTask.is_confirmed==True) \
                                .filter(PurchaseCeleryTask.is_visible==True) \
                                .order_by(PurchaseCeleryTask.started_on.desc()).limit(5).all()


        pending_deployments = DeployCeleryTask.query.filter(
                                DeployCeleryTask.user_id == user.id) \
                                .filter(DeployCeleryTask.is_confirmed == False) \
                                .filter(DeployCeleryTask.is_visible == True) \
                                .order_by(DeployCeleryTask.started_on.desc()) \
                                .limit(5).all()

        deployment_history = DeployCeleryTask.query.filter(DeployCeleryTask.user_id==user.id) \
                                .filter(DeployCeleryTask.is_confirmed==True) \
                                .filter(DeployCeleryTask.is_visible==True) \
                                .order_by(DeployCeleryTask.started_on.desc()).limit(5).all()

        return render_template(
            'pages/show_account.html',
            userinfo=data,
            transaction_history = transaction_history,
            pending_transactions = pending_transactions,
            deployment_history = [deployment.short() for deployment in deployment_history],
            pending_deployments = [pending_deployment.short() for pending_deployment in pending_deployments]
        )

    @flask_app.route('/users/<int:user_id>/update_profile_picture', methods=['PUT'])
    @requires_log_in
    def edit_profile_picture(user_id):

        user, data = get_user_data(True)

        try:

            profile_picture_file_name = S3_LOCATION + user.auth_id + "/" +secure_filename(request.get_json()['file_name'])
            user.profile_picture = profile_picture_file_name
            user.update()

            return jsonify({
                'success': True,
            })

        except Exception as e:
            print(e)
            return jsonify({
                'success': False
            })

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

            pending_deployments = DeployCeleryTask.query.filter(
                                            DeployCeleryTask.user_id == user.id) \
                                            .filter(DeployCeleryTask.is_confirmed == False) \
                                            .filter(DeployCeleryTask.is_visible == True) \
                                            .order_by(DeployCeleryTask.started_on.desc()) \
                                            .all()

            pending_purchases_formatted = [pending_purchase.short() for pending_purchase in pending_purchases]
            pending_deployments_formatted = [pending_deployment.short() for pending_deployment in pending_deployments]

            return jsonify({
                'success': True,
                'chain_id': ETHEREUM_CHAIN_ID,
                'pending_purchases': pending_purchases_formatted,
                'pending_deployments': pending_deployments_formatted
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

            if not current_task:
                current_task = DeployCeleryTask.query.filter(DeployCeleryTask.transaction_hash==transaction_hash).one_or_none()

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

                new_task = check_purchase_transaction_confirmed.apply_async(
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

            else:

                current_task = DeployCeleryTask.query.filter(DeployCeleryTask.transaction_hash==transaction_hash).one_or_none()

                if current_task:

                    wallet_address = current_task.wallet_address
                    transaction_hash = current_task.transaction_hash
                    release_id = current_task.release_id

                    celery_control.revoke(current_task.task_id, terminate=True)
                    current_task.delete()

                    new_task = check_smart_contract_deployed.apply_async(
                                args=(current_task.transaction_hash,
                                        release_id))

                    deploy_celery_task = DeployCeleryTask(
                        task_id = new_task.id,
                        user_id = user.id,
                        release_id = release_id,
                        wallet_address=wallet_address,
                        transaction_hash = transaction_hash,
                        is_confirmed = False
                    )

                    deploy_celery_task.insert()

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

            data = current_user.short_public()

            data['purchases'] = current_user.get_purchases()

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

    # Purchases

    ###################################################

    @flask_app.route('/account/purchases', methods=['GET'])
    @requires_log_in
    def show_purchases():

        user, data = get_user_data(True)

        if data is None:

            abort(404)

        data['purchases'] =  user.get_purchases()

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

    @flask_app.route('/tracks/<int:track_id>/purchase', methods=['POST'])
    @requires_log_in
    def purchase_track(track_id):

        user, data = get_user_data(True)

        if data is None:

            abort(404)

        try:

            transaction_hash = request.get_json()['transaction_hash']
            wallet_address = request.get_json()['wallet_address']

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

        track_purchase = user.has_purchased_track(track.id, release.id)

        release_purchase = user.has_purchased_release(release.id)

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

    return flask_app

app = create_app()
celery = make_celery(app)
