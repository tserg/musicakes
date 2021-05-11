import os
import json
from dotenv import load_dotenv

from urllib.parse import urlencode

from flask import (
    Flask,
    request,
    render_template,
    redirect,
    url_for,
    session
)

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

from flask_cors import CORS
from flask_wtf import CSRFProtect

from werkzeug.urls import url_encode

from .models import (
    setup_db,
    User,
    Artist,
    Release,
    Track,
    Purchase
)

from authlib.integrations.flask_client import OAuth

# Import Celery

from celery import Celery

from .decorators import (
    requires_log_in
)

from .utils.session_utils import (
    get_user_data
)

from .config import (
    CeleryConfig,
    FlaskConfig
)

load_dotenv()

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

def make_celery(app=None):
    app = app or create_app()
    celery = Celery(
        app.import_name
    )
    celery.config_from_object(CeleryConfig)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

def create_app(test_config=None):

    # create and configure the app
    flask_app = Flask(__name__, instance_relative_config=True)

    from musicakes.errors import bp as errors_bp
    flask_app.register_blueprint(errors_bp)

    from musicakes.aws_s3 import bp as aws_s3_bp
    flask_app.register_blueprint(aws_s3_bp)

    from musicakes.boilerplate import bp as boilerplate_bp
    flask_app.register_blueprint(boilerplate_bp)

    from musicakes.users import bp as users_bp
    flask_app.register_blueprint(users_bp)

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

    flask_app.config.from_object(FlaskConfig)

    ###################################################

    # Template global functions

    ###################################################

    @flask_app.template_global()
    def scroll_previous_page():
        """
        Global template function to scroll to previous page
        Used in album display macro
        """

        args = request.args.copy()

        if args['page'] != None and args['page'] != 1:

            args['page'] = str(int(args['page'])-1)

        return '{}?{}'.format(request.path, url_encode(args))

    @flask_app.template_global()
    def scroll_next_page():
        """
        Global template function to scroll to next page
        Used in album display macro
        """

        args = request.args.copy()

        if len(args) == 0:

            args = {'page': '2'}

        else:

            args['page'] = str(int(args['page'])+1)

        return '{}?{}'.format(request.path, url_encode(args))

    ###################################################

    # Authentication

    ###################################################

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

    ###################################################

    # Landing pages

    ###################################################

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

            return redirect(url_for('users.create_user_form'))

        latest_releases = Release.query.join(Release.tracks) \
            .filter(Release.is_removed == False) \
            .having(func.count(Track.id) > 0) \
            .group_by(Release.id) \
            .order_by(Release.created_on.desc()).limit(5).all()

        latest_releases_data = [release.short_public() for release in latest_releases]

        return render_template('pages/home.html', userinfo=data, latest_releases=latest_releases_data)

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

    return flask_app

app = create_app()
celery_app = make_celery(app)
