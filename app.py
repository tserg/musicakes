import os
import json

import boto3
from botocore.exceptions import ClientError
import zipfile

from functools import wraps
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
from flask_cors import CORS
from flask_wtf import (
    Form, 
    CSRFProtect
)

from wtforms import (
    FormField,
    FieldList
)
from forms import *
from jose import jwt

from models import (
    setup_db,
    User,
    Artist,
    Release,
    Track,
    Purchase
)

from urllib.request import urlopen
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode

from dotenv import load_dotenv

load_dotenv()

AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN', 'Does not exist')
AUTH0_ACCESS_TOKEN_URL = os.getenv('AUTH0_ACCESS_TOKEN_URL', 'Does not exist')
AUTH0_AUTHORIZE_URL = os.getenv('AUTH0_AUTHORIZE_URL', 'Does not exist')
AUTH0_CLIENT_ID = os.getenv('CLIENT_ID', 'Does not exist')
AUTH0_CLIENT_SECRET = os.getenv('CLIENT_SECRET', 'Does not exist')
AUTH0_USER_INFO_URL = os.getenv('AUTH0_USER_INFO_URL', 'Does not exist')
ALGORITHMS = os.getenv('ALGORITHMS', 'Does not exist')
API_AUDIENCE = os.getenv('API_AUDIENCE', 'Does not exist')
S3_BUCKET = os.getenv('S3_BUCKET_NAME', 'Does not exist')
S3_KEY = os.getenv('S3_KEY', 'Does not exist')
S3_SECRET = os.getenv('S3_SECRET', 'Does not exist')
S3_LOCATION = os.getenv('S3_LOCATION', 'Does not exist')
REDIRECT_URL = os.getenv('REDIRECT_URL', 'Does not exist')

class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

def create_app(test_config=None):

    # create and configure the app
    app = Flask(__name__)

    app.config.from_object('config')
    csrf = CSRFProtect()
    csrf.init_app(app)

    db=SQLAlchemy()

    setup_db(app)

    CORS(app, resources={r"/*": {"origins": "http://localhost:5000"}})

    oauth = OAuth(app)

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

    '''
        @INPUTS
            permission: string permission (i.e. 'create:artist')
            payload: decoded jwt payload

        raises an AuthError if permissions are not included in the payload
        raises an AuthError if the requested permission string is not
        in the payload permissions array
        return true otherwise
    '''

    def check_permissions(permission, payload):

        if 'permissions' not in payload:
            raise AuthError({
                'code': 'permissions_header_missing',
                'description': 'Permission header missing'
            }, 400)

        if permission not in payload['permissions']:
            raise AuthError({
                'code': 'no_permission',
                'description': 'No permission'
            }, 401)

        return True

    '''
        @INPUTS
            auth_id: string auth_id that is unique identifier of user
            payload: decoded jwt payload

        raises an AuthError if sub is not included in the payload
        raises an AuthError if the auth_id is not
        in the payload sub array
        return true otherwise
    '''

    def check_auth_id(auth_id, payload):

        if 'sub' not in payload: 
            raise AuthError({
                'code': 'sub_header_missing',
                'description': 'Sub header missing'
            }, 400)


        if auth_id not in payload['sub']:
            raise AuthError({
                'code': 'no_permission',
                'description': 'No permission'
            }, 401)

        return True


    '''
        @INPUTS
            token: a json web token for Auth0 with key id (string)

        verifies the token using Auth0 /.well-known/jwks.json
        decodes the payload from the token
        validates the claims
        return the decoded payload

    '''


    def verify_decode_jwt(token):
        jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
        jwks = json.loads(jsonurl.read())
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        if 'kid' not in unverified_header:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Authorization malformed.'
            }, 401)

        for key in jwks['keys']:
            if key['kid'] == unverified_header['kid']:
                rsa_key = {
                    'kty': key['kty'],
                    'kid': key['kid'],
                    'use': key['use'],
                    'n': key['n'],
                    'e': key['e']
                }
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=ALGORITHMS,
                    audience=API_AUDIENCE,
                    issuer='https://' + AUTH0_DOMAIN + '/'
                )

                return payload

            except jwt.ExpiredSignatureError:
                raise AuthError({
                    'code': 'token_expired',
                    'description': 'Token expired.'
                }, 401)

            except jwt.JWTClaimsError:
                raise AuthError({
                    'code': 'invalid_claims',
                    'description': 'Incorrect claims. \
                    Please, check the audience and issuer.'
                }, 401)
            except Exception:
                raise AuthError({
                    'code': 'invalid_header',
                    'description': 'Unable to parse authentication token.'
                }, 400)
        raise AuthError({
            'code': 'invalid_header',
                    'description': 'Unable to find the appropriate key.'
        }, 400)


    '''
        @INPUTS
            permission: string permission (i.e. 'post:drink')

        gets the access token from the Flask session
        uses the verify_decode_jwt method to decode the jwt
        uses the check_permissions method validate claims and
        check the requested permission
        return the decorator which passes the decoded payload
        to the decorated method
    '''

    def requires_auth(permission=''):
        def requires_auth_decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):

                token = session['token']['access_token']

                try:
                    payload = verify_decode_jwt(token)

                except:
                    abort(401)

                check_permissions(permission, payload)

                return f(payload, *args, **kwargs)

            return wrapper
        return requires_auth_decorator


    def requires_log_in(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'token' not in session:
                return redirect('/')
            return f(*args, **kwargs)
        return decorated

    # /server.py

    # Here we're using the /callback route.
    @app.route('/callback')
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

    @app.route('/login')
    def login():
        return auth0.authorize_redirect(redirect_uri=REDIRECT_URL,
                                        audience=API_AUDIENCE)

    @app.route('/logout')
    def logout():
        # Clear session stored data
        session.clear()
        # Redirect user to logout endpoint
        params = {'returnTo': url_for('index', _external=True), 'client_id': AUTH0_CLIENT_ID}
        return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

    @app.route('/')
    def index():

        if 'jwt_payload' in session:

            auth_id = session['jwt_payload']['sub'][6:]

            user = User.query.filter(User.auth_id==auth_id).one_or_none()

            if user:
                data = user.short_private()

            else: 

                data = None

            return redirect(url_for('home'))
        else:

            data = None

        return render_template('pages/index.html', userinfo=data)


    # after logging in

    @app.route('/home', methods=['GET'])
    @requires_log_in
    def home():

        auth_id = session['jwt_payload']['sub'][6:]

        user = User.query.filter(User.auth_id==auth_id).one_or_none()

        if user:
            data = user.short_private()

        else:

            return redirect(url_for('create_user_form'))

        latest_releases = Release.query.order_by(Release.created_on.desc()).limit(5).all()

        latest_releases_data = [release.short_public() for release in latest_releases]

        return render_template('pages/home.html', userinfo=data, latest_releases=latest_releases_data)


    ###################################################

    # AWS S3

    ###################################################

    def upload_profile_picture(file, key):
        """Upload a user's profile picture to an S3 bucket with public access

        :param file: File to upload
        :param key: Path name for the file
        :return: True if file was uploaded, else False
        """

        # If S3 object_name was not specified, use file_name

        # Upload the file
        s3_client = boto3.client('s3',
                                region_name='us-east-1',
                                endpoint_url=S3_LOCATION,
                                aws_access_key_id=S3_KEY,
                                aws_secret_access_key=S3_SECRET)


        try:

            s3_client.put_object(
                Body=file,
                Bucket=S3_BUCKET,
                Key=key,
                Tagging='public=yes'
            )

        except ClientError as e:
            print(e)
            return False

        return True

    def upload_release_picture(file, key):
        """Upload a release's cover art to an S3 bucket with public access

        :param file: File to upload
        :param key: Path name for the file
        :return: True if file was uploaded, else False
        """

        # If S3 object_name was not specified, use file_name

        # Upload the file
        s3_client = boto3.client('s3',
                                region_name='us-east-1',
                                endpoint_url=S3_LOCATION,
                                aws_access_key_id=S3_KEY,
                                aws_secret_access_key=S3_SECRET)


        try:

            s3_client.put_object(
                Body=file,
                Bucket=S3_BUCKET,
                Key=key,
                Tagging='public=yes'
            )

        except ClientError as e:
            print(e)
            return False

        return True

    def upload_release_file(file, key):
        """Upload a track file to an S3 bucket

        :param file: File to upload
        :param key: Path name for the file
        :return: True if file was uploaded, else False
        """

        # Upload the file
        s3_client = boto3.client('s3',
                                region_name='us-east-1',
                                endpoint_url=S3_LOCATION,
                                aws_access_key_id=S3_KEY,
                                aws_secret_access_key=S3_SECRET)


        try:

            s3_client.put_object(
                Body=file,
                Bucket=S3_BUCKET,
                Key=key,
            )

        except ClientError as e:
            print(e)
            return False

        return True


    def download_track(key, file_name):
        """
        Function to download a given track from an S3 bucket
        """
        s3_client = boto3.client('s3',
                                region_name='us-east-1',
                                endpoint_url=S3_LOCATION,
                                aws_access_key_id=S3_KEY,
                                aws_secret_access_key=S3_SECRET)

        output = file_name

        try:

            s3_client.download_file(
                Bucket=S3_BUCKET,
                Key=key,
                Filename=output
            )

        except ClientError as e:

            print(e)
            return False

        return output

    def download_release(keys, filenames, zip_file_name):
        """
        Function to download multiple tracks as zip from an S3 bucket
        """

        if len(keys) != len(filenames):
            return False

        s3_client = boto3.client('s3',
                                region_name='us-east-1',
                                endpoint_url=S3_LOCATION,
                                aws_access_key_id=S3_KEY,
                                aws_secret_access_key=S3_SECRET)

        for i in range(len(keys)):


            output = filenames[i]

            print(output)

            try:

                s3_client.download_file(
                    Bucket=S3_BUCKET,
                    Key=keys[i],
                    Filename=output
                )

            except ClientError as e:

                print(e)

        zf = zipfile.ZipFile(os.path.join(os.getcwd(), str(zip_file_name+".zip")), "w")

        for filename in filenames:
            zf.write(filename)

        zf.close()

        for filename in filenames:
            os.remove(filename)

        return str(zip_file_name + ".zip")

    @app.route('/sign_s3/')
    @requires_log_in
    def sign_s3():

        if 'jwt_payload' in session:

            auth_id = session['jwt_payload']['sub'][6:]

            user = User.query.filter(User.auth_id==auth_id).one_or_none()

            if user is None:

                abort(404)

        else:

            abort(404)


        print("sign_s3 triggered")
        S3_BUCKET = os.environ.get('S3_BUCKET')

        file_name = secure_filename(request.args.get('file_name'))
        file_type = request.args.get('file_type')

        s3_client = boto3.client('s3')

        key = user.auth_id + "/" + file_name

        presigned_post = s3_client.generate_presigned_post(
            Bucket = S3_BUCKET,
            Key = key,
            Fields = {"Content-Type": file_type},
            Conditions = [
            {"Content-Type": file_type}
            ],
            ExpiresIn = 3600
        )

        print(presigned_post)
        print(S3_LOCATION + "/" + S3_BUCKET + "/" + key)

        return json.dumps({
            'data': presigned_post,
            'url': S3_LOCATION + "/" + S3_BUCKET + "/" + key
        })

    ###################################################

    # General

    ###################################################

    @app.route('/about', methods=['GET'])
    def show_about_us():

        if 'jwt_payload' in session:

            auth_id = session['jwt_payload']['sub'][6:]

            user = User.query.filter(User.auth_id==auth_id).one_or_none()

            if user:
                data = user.short_private()

            else: 

                data = None

        else:

            data = None
            
        return render_template('pages/about.html', userinfo=data)


    @app.route('/faq', methods=['GET'])
    def show_faq():

        if 'jwt_payload' in session:

            auth_id = session['jwt_payload']['sub'][6:]

            user = User.query.filter(User.auth_id==auth_id).one_or_none()

            if user:
                data = user.short_private()

            else: 

                data = None

        else:

            data = None
            
        return render_template('pages/faq.html', userinfo=data)

    @app.route('/terms', methods=['GET'])
    def show_terms_of_use():

        if 'jwt_payload' in session:

            auth_id = session['jwt_payload']['sub'][6:]

            user = User.query.filter(User.auth_id==auth_id).one_or_none()

            if user:
                data = user.short_private()

            else: 

                data = None

        else:

            data = None
            
        return render_template('pages/terms.html', userinfo=data)

    @app.route('/privacy', methods=['GET'])
    def show_privacy_policy():

        if 'jwt_payload' in session:

            auth_id = session['jwt_payload']['sub'][6:]

            user = User.query.filter(User.auth_id==auth_id).one_or_none()

            if user:
                data = user.short_private()

            else: 

                data = None

        else:

            data = None
            
        return render_template('pages/privacy.html', userinfo=data)


    ###################################################

    # Account

    ###################################################

    @app.route('/account', methods=['GET'])
    @requires_log_in
    def show_account():

        auth_id = session['jwt_payload']['sub'][6:]

        user = User.query.filter(User.auth_id==auth_id).one_or_none()

        if user:
            data = user.short_private()

        else:

            abort(404)

        artist = Artist.query.filter(Artist.user_id==user.id).one_or_none()

        if artist:

            artist_name = artist.name

        else: 

            artist_name = None

        data['artist_name'] = artist_name

        return render_template('pages/show_account.html', userinfo=data)

    @app.route('/account/edit', methods=['GET'])
    @requires_log_in
    def edit_user_form():

        auth_id = session['jwt_payload']['sub'][6:]

        user = User.query.filter(User.auth_id==auth_id).one_or_none()

        if user:
            data = user.short_private()

        else:

            abort(404)

        form = EditUserForm()

        return render_template('forms/edit_user.html', form = form, userinfo=data)

    @app.route('/account/edit', methods=['POST'])
    @requires_log_in
    def edit_user_submission():

        auth_id = session['profile']['user_id'][6:]

        user = User.query.filter(User.auth_id==auth_id).one_or_none()

        form = EditUserForm()

        if not user:

            abort(404)

        try:

            if form.validate():

                f = form.profile_picture.data

                filename = secure_filename(f.filename)

                modified_filename = auth_id + "/" + filename

                upload_profile_picture(f, modified_filename)

                file_url = 'https://{}.s3.amazonaws.com/{}/{}'.format(S3_BUCKET, S3_BUCKET, modified_filename)

                user.profile_picture = file_url
                user.update()

                flash('Your profile has been updated.')

        except Exception as e:

            print(e)
            flash('Your profile could not be updated.')

        return redirect(url_for('show_account'))


    ###################################################

    # Users

    ###################################################

    @app.route('/users/<int:user_id>', methods=['GET'])
    def show_user(user_id):
        try:

            if 'jwt_payload' in session:



                auth_id = session['jwt_payload']['sub'][6:]

                user = User.query.filter(User.auth_id==auth_id).one_or_none()

                if user:
                    user_data = user.short_private()

                else:

                    user_data = None

            else:

                user_data=None

            current_user = User.query.get(user_id)
            if current_user is None:
                abort(404)

            data = current_user.short_private()

            purchased = Purchase.query.filter(Purchase.user_id==user_id). \
                        join(Release).all()

            temp=[]

            for purchase in purchased:
                release_name = Release.query.get(purchase.release_id).name
                temp_dict = {}

                if release_name not in temp:
                    temp_dict['release_id'] = purchase.release_id
                    temp_dict['release_name'] = release_name
                    temp.append(temp_dict)

            data['purchased_releases'] = temp

            return render_template('pages/show_user.html', user=data, userinfo=user_data)

        except Exception as e:
            print(e)
            abort(404)

    @app.route('/users/create', methods=['GET'])
    @requires_log_in
    def create_user_form():
        form = UserForm()

        return render_template('forms/new_user.html', form=form)


    @app.route('/users/create', methods=['POST'])
    @requires_log_in
    def create_user_submission():
        form = UserForm(request.form)

        auth_id = session['profile']['user_id'][6:]

        try:

            if form.validate():

                new_user = User(
                    auth_id = auth_id,
                    username = form.username.data
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

    @app.route('/artists', methods=['GET'])
    def get_artists():

        if 'jwt_payload' in session:

            auth_id = session['jwt_payload']['sub'][6:]

            user = User.query.filter(User.auth_id==auth_id).one_or_none()

            if user:
                data = user.short_private()

            else: 

                data = None

        else:

            data = None

        try:

            all_artists = Artist.query.all()

            formatted_all_artists = [artist.short() for artist in all_artists]

            return render_template('pages/artists.html', artists=formatted_all_artists, userinfo=data)

        except Exception as e:
            print(e)
            abort(404)

        return redirect('/')

    @app.route('/artists/<int:artist_id>', methods=['GET'])
    def show_artist(artist_id):

        if 'jwt_payload' in session:

            auth_id = session['jwt_payload']['sub'][6:]

            user = User.query.filter(User.auth_id==auth_id).one_or_none()

            if user:
                data = user.short_private()

            else: 

                data = None

        else:

            data = None

        try:

            current_artist = Artist.query.get(artist_id)
            if current_artist is None:
                abort(404)

            artist_data = current_artist.short()

            return render_template('pages/show_artist.html', artist=artist_data, userinfo=data)

        except Exception as e:
            print(e)
            abort(404)

        return redirect('/')

    @app.route('/artists/create', methods=['GET'])
    @requires_log_in
    def create_artist_form():

        if 'jwt_payload' in session:

            auth_id = session['jwt_payload']['sub'][6:]

            user = User.query.filter(User.auth_id==auth_id).one_or_none()

            if user:
                data = user.short_private()

            else:

                data = None

        else:

            data = None

        artist = Artist.query.filter(Artist.user_id==user.id).one_or_none()

        if artist:

            artist_name = artist.name

        else:

            artist_name = None

        data['artist_name'] = artist_name

        form = ArtistForm()

        return render_template('forms/new_artist.html', form=form, userinfo=data)

    @app.route('/artists/create', methods=['POST'])
    @requires_log_in
    def create_artist():

        form = ArtistForm(request.form)

        auth_id = session['jwt_payload']['sub'][6:]
        user = User.query.filter(User.auth_id==auth_id).one_or_none()
        user_id = user.id

        try:

            if form.validate():

                new_artist = Artist(
                    name = form.artist_name.data,
                    country = form.artist_country.data,
                    user_id = user_id
                )

                new_artist.insert()
                flash('Your artist profile has been successfully created.')

        except Exception as e:

            print(e)
            flash('Your artist profile could not be created.')

        return redirect(url_for('index'))

    ###################################################

    # Purchases

    ###################################################

    @app.route('/account/purchases', methods=['GET'])
    @requires_log_in
    def show_purchases():

        auth_id = session['jwt_payload']['sub'][6:]

        user = User.query.filter(User.auth_id==auth_id).one_or_none()

        if user:
            data = user.short_private()

        else:

            abort(404)

        purchased_releases = Purchase.query.filter(Purchase.user_id==user.id). \
                    join(Release).all()

        purchased_tracks = Purchase.query.filter(Purchase.user_id==user.id). \
                            join(Track).all()

        temp=[]

        for purchased_release in purchased_releases:
            release_name = Release.query.get(purchased_release.release_id).name
            temp_dict = {}

            if release_name not in temp:
                temp_dict['release_id'] = purchased_release.release_id
                temp_dict['release_name'] = release_name
                temp.append(temp_dict)

        data['purchased_releases'] = temp

        temp = []

        for purchased_track in purchased_tracks:
            track = Track.query.get(purchased_track.track_id)
            track_name = track.name
            temp_dict = {}

            if track_name not in temp:
                temp_dict['track_id'] = track.id
                temp_dict['track_name'] = track_name
                temp_dict['track_download_url'] = track.download_url
                temp.append(temp_dict)

        data['purchased_tracks'] = temp

        print(data)

        return render_template('pages/show_purchases.html', userinfo=data)

    @app.route('/releases/<int:release_id>/purchase', methods=['POST'])
    @requires_log_in
    def purchase_release(release_id):

        if 'jwt_payload' in session:

            auth_id = session['jwt_payload']['sub'][6:]

            user = User.query.filter(User.auth_id==auth_id).one_or_none()

            if user is None:

                abort(404)

        else:

            abort(404)

        try:

            transaction_hash = request.get_json()['transaction_hash']
            wallet_address = request.get_json()['wallet_address']
            paid = request.get_json()['paid']


            purchase = Purchase(
                    user_id = user.id,
                    release_id = release_id,
                    paid = paid,
                    wallet_address = wallet_address,
                    transaction_hash = transaction_hash
                )

            purchase.insert()

            return jsonify({
                'success': True,
                'release_id': purchase.release_id,
                'paid': purchase.paid,
                'wallet_address': purchase.wallet_address,
                'transaction_hash': purchase.transaction_hash
            })

        except Exception as e:
            print(e)

            abort(404)

    @app.route('/tracks/<int:track_id>/purchase', methods=['POST'])
    @requires_log_in
    def purchase_track(track_id):

        if 'jwt_payload' in session:

            auth_id = session['jwt_payload']['sub'][6:]

            user = User.query.filter(User.auth_id==auth_id).one_or_none()
            if user is None:

                abort(404)

        else:

            abort(404)

        try:

            transaction_hash = request.get_json()['transaction_hash']
            wallet_address = request.get_json()['wallet_address']
            paid = request.get_json()['paid']

            purchase = Purchase(
                    user_id = user.id,
                    track_id = track_id,
                    paid = paid,
                    wallet_address = wallet_address,
                    transaction_hash = transaction_hash
                )

            purchase.insert()

            return jsonify({
                'success': True,
                'track_id': purchase.track_id,
                'paid': purchase.paid,
                'wallet_address': purchase.wallet_address,
                'transaction_hash': purchase.transaction_hash
            })

        except Exception as e:
            print(e)

            abort(404)

    @app.route('/tracks/<int:track_id>/download', methods=['GET'])
    @requires_log_in
    def download_purchased_track(track_id):

        if 'jwt_payload' in session:

            auth_id = session['jwt_payload']['sub'][6:]

            user = User.query.filter(User.auth_id==auth_id).one_or_none()

            if user is None:

                abort(404)

        else:

            abort(404)

        # checks if user has purchased the current track

        track = Track.query.filter(Track.id==track_id).one_or_none()
        release = Release.query.filter(Release.id==track.release_id).one_or_none()

        if track is None or release is None:

            abort(404)

        track_purchase = Purchase.query.filter(Purchase.track_id==track.id). \
                            filter(Purchase.user_id==user.id). \
                            join(Track).all()

        release_purchase = Purchase.query.filter(Purchase.release_id==track.release_id). \
                            filter(Purchase.user_id==user.id). \
                            join(Release).all()

        if track_purchase is None and release_purchase is None:

            abort(404)

        # download file

        artist_user = Artist.query.filter(Artist.id==release.artist_id).one_or_none()

        key = artist_user.user.auth_id + "/" + track.download_url

        try:

            output = download_track(key, track.download_url)

            return send_file(output, as_attachment=True)

        except Exception as e:

            print(e)
            flash('Unable to download file.')

        return redirect(url_for('show_purchases'))

    @app.route('/releases/<int:release_id>/download', methods=['GET'])
    @requires_log_in
    def download_purchased_release(release_id):

        if 'jwt_payload' in session:

            auth_id = session['jwt_payload']['sub'][6:]

            user = User.query.filter(User.auth_id==auth_id).one_or_none()

            if user is None:

                abort(404)

        else:

            abort(404)

        # checks if user has purchased the current release

        release = Release.query.filter(Release.id==release_id).one_or_none()

        if release is None:

            abort(404)

        release_purchase = Purchase.query.filter(Purchase.release_id==release_id). \
                            filter(Purchase.user_id==user.id). \
                            join(Release).all()

        if release_purchase is None:

            abort(404)

        # download files

        artist_user = Artist.query.filter(Artist.id==release.artist_id).one_or_none()

        keys = [] 
        filenames = []

        for track in release.tracks:

            key = artist_user.user.auth_id + "/" + track.download_url
            filename = track.download_url

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

    ###################################################

    # Releases

    ###################################################

    @app.route('/releases', methods=['GET'])
    def get_releases():

        try:

            all_releases = Release.query.all()

            formatted_all_releases = [release.short_public()
                                      for release in all_releases]

            if 'jwt_payload' in session:

                auth_id = session['jwt_payload']['sub'][6:]

                user = User.query.filter(User.auth_id==auth_id).one_or_none()

                if user:
                    data = user.short_private()

                else: 

                    data = None

            else:

                data = None

            return render_template('pages/releases.html', releases=formatted_all_releases, userinfo=data)

        except Exception as e:
            print(e)
            abort(404)

    @app.route('/releases/<int:release_id>', methods=['GET'])
    def show_release(release_id):

        if 'jwt_payload' in session:

            auth_id = session['jwt_payload']['sub'][6:]

            user = User.query.filter(User.auth_id==auth_id).one_or_none()

            if user:

                data = user.short_private()

                purchased_current_release = Purchase.query.filter(Purchase.release_id==release_id). \
                        filter(Purchase.user_id==user.id). \
                        join(Release).one_or_none()

                data['purchased'] = purchased_current_release

            else:

                data = None
        else:
            data = None

        try:

            current_release = Release.query.get(release_id)
            if current_release is None:
                abort(404)

            release_data = current_release.short_public()

            purchases = Purchase.query.filter(Purchase.release_id==release_id). \
                        join(Release).all()

            temp=[]

            for purchase in purchases:
                purchaser_name = User.query.get(purchase.user_id).username
                temp_dict = {}

                if purchaser_name not in temp:
                    temp_dict['user_id'] = purchase.user_id
                    temp_dict['username'] = purchaser_name
                    temp.append(temp_dict)

            release_data['purchasers'] = temp

            return render_template('pages/show_release.html', release=release_data, userinfo=data)

        except Exception as e:
            print(e)
            abort(404)

        return redirect('/')

    @app.route('/releases/create', methods=['GET'])
    @requires_log_in
    def create_release_presubmission_form():
        if 'jwt_payload' in session:

            auth_id = session['jwt_payload']['sub'][6:]

            user = User.query.filter(User.auth_id==auth_id).one_or_none()

            if user.artist is None:

                abort(404)

            if user:
                data = user.short_private()

            else:

                data = None

        else:

            data = None

        form = ReleasePresubmissionForm()

        return render_template('forms/new_release_presubmission.html', form=form, userinfo=data)

    @app.route('/releases/create', methods=['POST'])
    @requires_log_in
    def create_release_presubmission():

        if 'jwt_payload' in session:

            auth_id = session['jwt_payload']['sub'][6:]

            user = User.query.filter(User.auth_id==auth_id).one_or_none()

            if user.artist is None:

                abort(404)

            if user:
                data = user.short_private()

            else:

                data = None

        else:

            data = None


        presubmission_form = ReleasePresubmissionForm(request.form)

        track_count = presubmission_form.track_count.data 

        if track_count >= 2:

            track_count_list = [n for n in range(2, track_count+1)]

        else:

            track_count_list = []

        print(track_count_list)

        return render_template('forms/new_release.html', track_count=track_count_list, userinfo=data)

    @app.route('/releases/create_2', methods=['POST'])
    @requires_log_in
    def create_release_submission():

        if 'jwt_payload' in session:

            auth_id = session['jwt_payload']['sub'][6:]

            user = User.query.filter(User.auth_id==auth_id).one_or_none()

            if user.artist is None:

                abort(404)

        print("create_release_submission")

        try:

            release_name = request.get_json()['release_name']
            release_price = request.get_json()['release_price']
            release_cover_art_file_name = request.get_json()['file_name']
            release_text = request.get_json()['release_text']

            print(release_name)
            print(release_price)
            print(release_cover_art_file_name)
            print(release_text)

            # Create new release in database

            new_release = Release(
                artist_id = user.artist.id,
                name=release_name,
                price=release_price,
                description=release_text,
                cover_art=release_cover_art_file_name
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



    '''

    @app.route('/releases/create_2', methods=['POST'])
    @requires_log_in
    def create_release_submission():

        if 'jwt_payload' in session:

            auth_id = session['jwt_payload']['sub'][6:]

            user = User.query.filter(User.auth_id==auth_id).one_or_none()

            if user.artist is None:

                abort(404)

        form = ReleaseForm()

        try:

            if form.validate():

                # Extract information for release

                release_name = form.release_name.data
                release_price = form.release_price.data
                release_text = form.release_text.data

                # Upload release cover art 

                f = form.release_cover_art.data

                filename = secure_filename(f.filename)

                modified_filename = auth_id + "/" + filename

                upload_release_picture(f, modified_filename)

                file_url = 'https://{}.s3.amazonaws.com/{}/{}'.format(S3_BUCKET, S3_BUCKET, modified_filename)

                # Create new release in database

                new_release = Release(
                    artist_id = user.artist.id,
                    name=release_name,
                    price=release_price,
                    description=release_text,
                    cover_art=file_url
                )

                new_release.insert()

                # Loop over tracks and create ne track in database

                for track in form.tracks.entries:

                    track_name = track.data['track_name']
                    track_price = track.data['track_price']

                    f1 = track.data['track_file']

                    filename = secure_filename(f1.filename)

                    modified_track_filename = auth_id + "/" + filename

                    upload_release_file(f1, modified_track_filename)

                    new_track = Track(
                        artist_id = user.artist.id,
                        release_id = new_release.id,
                        name = track_name,
                        price = track_price,
                        download_url = filename

                    )

                    new_track.insert()

                flash('Your release has been successfully created.')

            print(form.errors)
        
        except Exception as e:

            print(e)
            flash('Your release could not be created.')

        return redirect(url_for('get_releases'))

    '''


    ###################################################

    # Tracks

    ###################################################

    @app.route('/tracks', methods=['GET'])
    def get_tracks():

        try:

            all_tracks = Track.query.all()

            formatted_all_tracks = [track.short_public() for track in all_tracks]

            if 'jwt_payload' in session:

                auth_id = session['jwt_payload']['sub'][6:]

                user = User.query.filter(User.auth_id==auth_id).one_or_none()

                if user:
                    data = user.short_private()

                else: 

                    data = None

            else:

                data = None

            return render_template('/pages/tracks.html', tracks=formatted_all_tracks, userinfo=data)

        except:

            abort(404)

    @app.route('/tracks/<int:track_id>', methods=['GET'])
    def show_track(track_id):

        try:

            track = Track.query.get(track_id)

            formatted_track_data = track.short_public()

            if 'jwt_payload' in session:

                auth_id = session['jwt_payload']['sub'][6:]

                user = User.query.filter(User.auth_id==auth_id).one_or_none()

                if user:
                    data = user.short_private()

                else: 

                    data = None

            else:

                data = None

            purchases = Purchase.query.filter(Purchase.track_id==track_id). \
                        join(Track).all()

            temp=[]

            for purchase in purchases:
                purchaser_name = User.query.get(purchase.user_id).username
                temp_dict = {}

                if purchaser_name not in temp:
                    temp_dict['user_id'] = purchase.user_id
                    temp_dict['username'] = purchaser_name
                    temp.append(temp_dict)

            formatted_track_data['purchasers'] = temp

            return render_template('pages/show_track.html', track=formatted_track_data, userinfo=data)

        except:

            abort(404)

    @app.route('/tracks/create', methods=['POST'])
    @requires_log_in
    def create_track():

        if 'jwt_payload' in session:

            auth_id = session['jwt_payload']['sub'][6:]

            user = User.query.filter(User.auth_id==auth_id).one_or_none()

            if user.artist is None:

                abort(404)

        print("create_track")

        try:

            track_name = request.get_json()['track_name']
            track_price = request.get_json()['track_price']
            track_file_name = request.get_json()['file_name']
            track_release_id = request.get_json()['release_id']

            print(track_name)
            print(track_price)
            print(track_file_name)
            print(track_release_id)

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

    

    @app.route('/artists/<int:id>', methods=['PATCH'])
    @requires_auth('update:artist')
    def update_artist(payload, id):

        try:

            current_artist = Artist.query.get(id)

            if current_artist is None:

                abort(404)

            # authenticates if the artist corresponds to the user

            auth_id = current_artist.user.auth_id

            if auth_id is None:

                abort(401)

            elif check_auth_id(auth_id, payload) is not True:

                abort(401)

            # actual function continues here

            if 'name' in request.get_json():
                name = request.get_json()['name']
                current_artist.name = name

            if 'country' in request.get_json():
                country = request.get_json()['country']
                current_artist.country = country

            current_artist.update()

            return jsonify({
                'success': True,
                'name': current_artist.name,
                'country': current_artist.country
            })

        except:

            abort(400)

    @app.route('/releases/<int:id>', methods=['PATCH'])
    @requires_auth('update:release')
    def update_release(payload, id):

        try:

            current_release = Release.query.get(id)

            if current_release is None:

                abort(404)

            # authenticates if the artist corresponds to the user
            
            current_artist = Artist.query.get(current_release.artist_id)
            auth_id = current_artist.user.auth_id

            if auth_id is None:

                abort(401)

            elif check_auth_id(auth_id, payload) is not True:

                abort(401)

            # actual function continues here

            if 'name' in request.get_json():
                name = request.get_json()['name']
                current_release.name = name

            if 'artist_id' in request.get_json():
                artist_id = request.get_json()['artist_id']
                current_release.artist_id = artist_id

            if 'price' in request.get_json():
                price = request.get_json()['price']
                current_release.price = price

            current_release.update()

            return jsonify({
                'success': True,
                'name': current_release.name,
                'artist_id': current_release.artist_id,
                'price': current_release.price
            })

        except:

            abort(400)

    @app.route('/tracks/<int:id>', methods=['PATCH'])
    @requires_auth('update:track')
    def update_track(payload, id):

        try:

            current_track = Track.query.get(id)

            if current_track is None:

                abort(404)

            # authenticates if the artist corresponds to the user

            current_artist = Artist.query.get(current_track.release.artist_id)
            auth_id = current_artist.user.auth_id

            if auth_id is None:

                abort(401)

            elif check_auth_id(auth_id, payload) is not True:

                abort(401)

            # actual function continues here
            current_track = Track.query.get(id)

            if current_track is None:

                abort(404)

            if 'name' in request.get_json():
                name = request.get_json()['name']
                current_track.name = name

            if 'artist_id' in request.get_json():
                artist_id = request.get_json()['artist_id']
                current_track.artist_id = artist_id

            if 'release_id' in request.get_json():
                release_id = request.get_json()['release_id']
                current_track.release_id = release_id

            if 'price' in request.get_json():
                price = request.get_json()['price']
                current_track.price = price

            current_track.update()

            return jsonify({
                'success': True,
                'name': current_track.name,
                'artist_id': current_track.artist_id,
                'release_id': current_track.release_id,
                'price': current_track.price
            })

        except:

            abort(400)

    @app.route('/users/<int:id>', methods=['DELETE'])
    def delete_user(id):

        try:

            user = User.query.get(id)

            if user is None:

                abort(404)

            user.delete()

            return jsonify({
                'success': True
            })

        except Exception as e:
            print(e)

            abort(422)

    @app.route('/artists/<int:id>', methods=['DELETE'])
    @requires_auth('delete:artist')
    def delete_artist(payload, id):

        try:

            artist = Artist.query.get(id)

            if artist is None:

                abort(404)

            # authenticates if the artist corresponds to the user

            auth_id = artist.user.auth_id

            if auth_id is None:

                abort(401)

            elif check_auth_id(auth_id, payload) is not True:

                abort(401)

            # actual function continues here

            artist.delete()

            return jsonify({
                'success': True
            })

        except Exception as e:
            print(e)

            abort(422)

    @app.route('/releases/<int:id>', methods=['DELETE'])
    @requires_auth('delete:release')
    def delete_release(payload, id):

        try:

            release = Release.query.get(id)

            if release is None:

                abort(404)

            # authenticates if the artist corresponds to the user
            
            current_artist = Artist.query.get(release.artist_id)
            auth_id = current_artist.user.auth_id

            if auth_id is None:

                abort(401)

            elif check_auth_id(auth_id, payload) is not True:

                abort(401)

            # actual function continues here

            release.delete()

            return jsonify({
                'success': True
            })

        except:

            abort(422)

    @app.route('/tracks/<int:id>', methods=['DELETE'])
    @requires_auth('delete:track')
    def delete_track(payload, id):

        try:

            track = Track.query.get(id)

            if track is None:

                abort(404)

            # authenticates if the artist corresponds to the user

            current_artist = Artist.query.get(track.release.artist_id)
            auth_id = current_artist.user.auth_id

            if auth_id is None:

                abort(401)

            elif check_auth_id(auth_id, payload) is not True:

                abort(401)

            # function continues here

            track.delete()

            return jsonify({
                'success': True
            })

        except:

            abort(422)

    """
        Errors handling
    """

    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'bad request'
        }), 400

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'method not allowed'
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable'
        }), 422

    """

    @app.errorhandler(AuthError)
    def auth_error(AuthError):
        return render_template('errors/401.html'), 401

    @app.errorhandler(401)
    def not_found_error(error):
        return render_template('errors/401.html'), 401


    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(error):
        return render_template('errors/500.html'), 500


    return app


app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
