import os
import json
from functools import wraps
from flask import Flask, request, abort, jsonify, flash, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_wtf import Form, CSRFProtect
from forms import *
from jose import jwt

from models import setup_db, User, Artist, Release, Track, Purchase

from urllib.request import urlopen
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode

from dotenv import load_dotenv

load_dotenv()

AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN', 'Does not exist')
ALGORITHMS = os.getenv('ALGORITHMS', 'Does not exist')
API_AUDIENCE = os.getenv('API_AUDIENCE', 'Does not exist')

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

    setup_db(app)

    CORS(app)

    oauth = OAuth(app)

    auth0 = oauth.register(
        'auth0',
        client_id='TYNrPQ3cGpX0P16gl9Q8zyEVUxxVlTkh',
        client_secret='8oYk_9RSrFUuqZ-6IhpiRG5irPLypPECaMMDT-qg0PQ7WWW4D9gfYwV5bDvmxIGk',
        api_base_url='https://musicakes.auth0.com',
        access_token_url='https://musicakes.auth0.com/oauth/token',
        authorize_url='https://musicakes.auth0.com/authorize',
        client_kwargs={
            'scope': 'openid profile email',
        },
    )



    '''
        @INPUTS
            permission: string permission (i.e. 'post:drink')
            payload: decoded jwt payload

        raises an AuthError if permissions are not included in the payload
        raises an AuthError if the requested permission string is not
        in the payload permissions array
        return true otherwise
    '''

    ###################################################

    # Auth

    ###################################################

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

                print("requires_auth printing for access token")
                print(token)

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
            if 'profile' not in session:
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
        resp = auth0.get('userinfo')
        userinfo = resp.json()

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
        return auth0.authorize_redirect(redirect_uri='http://localhost:5000/callback',
                                        audience=API_AUDIENCE)

    @app.route('/logout')
    def logout():
        # Clear session stored data
        session.clear()
        # Redirect user to logout endpoint
        params = {'returnTo': url_for('index', _external=True), 'client_id': 'TYNrPQ3cGpX0P16gl9Q8zyEVUxxVlTkh'}
        return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

    @app.route('/')
    def index():

        if 'jwt_payload' in session:

            auth_id = session['jwt_payload']['sub'][6:]

            user = User.query.filter(User.auth_id==auth_id).one_or_none()

            if user:
                data = user.short_public()

            else: 

                data = None

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
            data = user.short_public()

        else:

            data = None

        return render_template('pages/home.html', userinfo=data)

    '''
    @app.route('/users', methods=['GET'])
    def get_users():
        try:

            all_users = User.query.all()

            formatted_all_users = [user.short() for user in all_users]

            return jsonify({
                'success': True,
                'users': formatted_all_users
            })

        except Exception as e:
            print(e)
            abort(404)
    '''
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

        artist_name = Artist.query.filter(Artist.user_id==user.id).one_or_none().name

        data['artist_name'] = artist_name

        return render_template('pages/show_account.html', userinfo=data)


    ###################################################

    # Users

    ###################################################

    @app.route('/users/<int:user_id>', methods=['GET'])
    def show_user(user_id):
        try:

            auth_id = session['jwt_payload']['sub'][6:]

            user = User.query.filter(User.auth_id==auth_id).one_or_none()

            if user:
                user_data = user.short_public()

            else:

                user_data = None

            current_user = User.query.get(user_id)
            if current_user is None:
                abort(404)

            data = current_user.short_public()

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
    def create_user_submission():
        form = UserForm(request.form)

        auth_id = request.args.get('auth_id')

        try:

            if form.validate():

                new_user = User(
                    auth_id = auth_id,
                    username = form.username.data
                )

                new_user.insert()

                flash('Your account has been successfully created.')

        except Exception as e:

            print(e)
            flash('Your account could not be created.')

        return redirect(url_for('index'))

    ###################################################

    # Artists

    ###################################################

    @app.route('/artists', methods=['GET'])
    def get_artists():

        try:

            all_artists = Artist.query.all()

            formatted_all_artists = [artist.short() for artist in all_artists]

            if 'jwt_payload' in session:

                auth_id = session['jwt_payload']['sub'][6:]

                user = User.query.filter(User.auth_id==auth_id).one_or_none()

                if user:
                    data = user.short_public()

                else: 

                    data = None

            else:

                data = None

            return render_template('pages/artists.html', artists=formatted_all_artists, userinfo=data)

        except Exception as e:
            print(e)
            abort(404)

        return redirect('/')

    @app.route('/artists/<int:artist_id>', methods=['GET'])
    def show_artist(artist_id):
        try:

            current_artist = Artist.query.get(artist_id)
            if current_artist is None:
                abort(404)

            data = current_artist.short()

            return render_template('pages/show_artist.html', artist=data)

        except Exception as e:
            print(e)
            abort(404)

        return redirect('/')

    @app.route('/artists/create', methods=['GET'])
    @requires_log_in
    def create_artist_form():

        auth_id = session['jwt_payload']['sub'][6:]

        user = User.query.filter(User.auth_id==auth_id).one_or_none()

        if user:
            data = user.short_private()

        else:

            data = None

        artist_name = Artist.query.filter(Artist.user_id==user.id).one_or_none().name

        data['artist_name'] = artist_name

        form = ArtistForm()

        return render_template('forms/new_artist.html', form=form, userinfo=data)

    @app.route('/artists/create', methods=['POST'])
    @requires_log_in
    @requires_auth('create:artist')
    def create_artist(payload):

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

        purchased = Purchase.query.filter(Purchase.user_id==user.id). \
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

        return render_template('pages/show_purchases.html', userinfo=data)

    ###################################################

    # Releases

    ###################################################

    @app.route('/releases', methods=['GET'])
    def get_releases():

        try:

            all_releases = Release.query.all()

            formatted_all_releases = [release.short()
                                      for release in all_releases]

            if 'jwt_payload' in session:

                auth_id = session['jwt_payload']['sub'][6:]

                user = User.query.filter(User.auth_id==auth_id).one_or_none()

                if user:
                    data = user.short_public()

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
        try:

            current_release = Release.query.get(release_id)
            if current_release is None:
                abort(404)

            data = current_release.short()

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

            data['purchasers'] = temp

            return render_template('pages/show_release.html', release=data)

        except Exception as e:
            print(e)
            abort(404)

        return redirect('/')

    ###################################################

    # Tracks

    ###################################################

    @app.route('/tracks', methods=['GET'])
    def get_tracks():

        try:

            all_tracks = Track.query.all()

            formatted_all_tracks = [track.short() for track in all_tracks]

            if 'jwt_payload' in session:

                auth_id = session['jwt_payload']['sub'][6:]

                user = User.query.filter(User.auth_id==auth_id).one_or_none()

                if user:
                    data = user.short_public()

                else: 

                    data = None

            else:

                data = None

            return render_template('/pages/tracks.html', tracks=formatted_all_tracks, userinfo=data)

        except:

            abort(404)






    @app.route('/releases', methods=['POST'])
    @requires_auth('create:release')
    def create_release(payload):

        try:

            name = request.get_json()['name']
            artist_id = request.get_json()['artist_id']
            price = request.get_json()['price']

            new_release = Release(
                name=name,
                artist_id=artist_id,
                price=price
            )

            new_release.insert()

            return jsonify({
                'success': True,
                'name': new_release.name,
                'artist_id': new_release.artist_id,
                'price': new_release.price
            })

        except:

            abort(422)

    @app.route('/tracks', methods=['POST'])
    @requires_auth('create:track')
    def create_track(payload):

        try:

            name = request.get_json()['name']
            artist_id = request.get_json()['artist_id']
            release_id = request.get_json()['release_id']
            price = request.get_json()['price']

            new_track = Track(
                name=name,
                artist_id=artist_id,
                release_id=release_id,
                price=price
            )

            new_track.insert()

            return jsonify({
                'success': True,
                'name': new_track.name,
                'artist_id': new_track.artist_id,
                'release_id': new_track.release_id,
                'price': new_track.price
            })

        except:

            abort(422)

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

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found'
        }), 404

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

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'internal server error'
        }), 500

    """

    @app.errorhandler(AuthError)
    def auth_error(AuthError):
        return jsonify({
            'success': False,
            'error': AuthError.status_code,
            'message': AuthError.error['description']
        }), 401


    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(error):
        return render_template('errors/500.html'), 500


    return app


app = create_app()

if __name__ == '__main__':
    app.run()
