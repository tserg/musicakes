import os
from flask import Flask, request, abort, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from jose import jwt

from models import setup_db, User, Artist, Release, Track
from auth import AuthError, requires_auth


def create_app(test_config=None):

    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app)

    @app.route('/')
    def index():

        return "Welcome to Musicakes!"


    @app.route('/users', methods=['GET'])
    def get_users():
        try:


            print(123)
            all_users = User.query.all()

            if all_users is None:
                print(234)
            formatted_all_users = [user.short() for user in all_users]

            return jsonify({
                'success': True,
                'users': formatted_all_users
            })

        except Exception as e:
            print(e)
            abort(404)

    @app.route('/artists', methods=['GET'])
    def get_artists():

        try:

            all_artists = Artist.query.all()

            formatted_all_artists = [artist.short() for artist in all_artists]

            return jsonify({
                'success': True,
                'artists': formatted_all_artists
            })

        except Exception as e:
            print(e)
            abort(404)

    @app.route('/releases', methods=['GET'])
    def get_releases():

        try:

            all_releases = Release.query.all()

            formatted_all_releases = [release.short()
                                      for release in all_releases]

            return jsonify({
                'success': True,
                'releases': formatted_all_releases
            })

        except:

            abort(404)

    @app.route('/tracks', methods=['GET'])
    def get_tracks():

        try:

            all_tracks = Track.query.all()

            formatted_all_tracks = [track.short() for track in all_tracks]

            return jsonify({
                'success': True,
                'tracks': formatted_all_tracks
            })

        except:

            abort(404)

    @app.route('/artists', methods=['POST'])
    @requires_auth('create:artist')
    def create_artist(payload):

        try:

            name = request.get_json()['name']
            country = request.get_json()['country']

            new_artist = Artist(
                name=name,
                country=country
            )

            new_artist.insert()

            return jsonify({
                'success': True,
                'name': new_artist.name,
                'country': new_artist.country
            })

        except:

            abort(422)

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

    @app.route('/artists/<int:id>', methods=['DELETE'])
    @requires_auth('delete:artist')
    def delete_artist(payload, id):

        try:

            artist = Artist.query.get(id)

            if artist is None:

                abort(404)

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

            track.delete()

            return jsonify({
                'success': True
            })

        except:

            abort(422)

    """
        Errors handling
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

    @app.errorhandler(AuthError)
    def auth_error(AuthError):
        return jsonify({
            'success': False,
            'error': AuthError.status_code,
            'message': AuthError.error['description']
        }), 401

    return app


app = create_app()

if __name__ == '__main__':
    app.run()
