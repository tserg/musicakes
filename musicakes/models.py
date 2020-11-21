import os
import datetime
from dotenv import load_dotenv

from sqlalchemy import (
    Column, 
    String, 
    Integer, 
    Float,
    Boolean,
    create_engine, 
    DateTime, 
    UniqueConstraint, 
    CheckConstraint
)

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import json

db = SQLAlchemy()

# Load environment variables from .env

load_dotenv()

database_path = os.getenv('DATABASE_URL', 'Does not exist')


def setup_db(app, database_path=database_path):
    '''
            binds a flask application and a SQLAlchemy service
    '''
    app.config['SQLALCHEMY_DATABASE_URI'] = database_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)
    db.create_all()
    migrate = Migrate(app, db)


class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    auth_id = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    artist = db.relationship('Artist', uselist=False, back_populates='user')
    profile_picture = Column(String, unique=False, nullable=True)
    created_on = Column(DateTime, server_default=db.func.now(), nullable=False)
    
    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def short_private(self):

        artist_info = None

        if self.artist is not None:

            artist_info = self.artist.id

        return {
            'id': self.id,
            'username': self.username,
            'artist_id': artist_info,
            'profile_picture': self.profile_picture,
            'created_on': self.created_on.strftime('%#d %B %Y')
        }

    def short_public(self):

        return {
            'id': self.id,
            'username': self.username,
            'profile_picture': self.profile_picture,
            'created_on': self.created_on.strftime('%#d %B %Y')
        }

    def get_purchases(self):

        """
        Helper function to retrieve information of all purchases of user
        """

        purchased_releases = Purchase.query.filter(Purchase.user_id==self.id). \
                    join(Release).all()

        purchased_tracks = Purchase.query.filter(Purchase.user_id==self.id). \
                            join(Track).all()


        formatted_purchased_releases=[]

        for purchased_release in purchased_releases:
            release = Release.query.get(purchased_release.release_id)
            temp_dict = {}

            if release.name not in formatted_purchased_releases:
                temp_dict['release_id'] = release.id
                temp_dict['release_name'] = release.name
                temp_dict['release_cover_art'] = release.cover_art
                formatted_purchased_releases.append(temp_dict)

        formatted_purchased_tracks = []

        for purchased_track in purchased_tracks:
            track = Track.query.get(purchased_track.track_id)
            temp_dict = {}

            if track.name not in formatted_purchased_tracks:
                temp_dict['track_id'] = track.id
                temp_dict['track_name'] = track.name
                temp_dict['release_cover_art'] = track.release.cover_art
                formatted_purchased_tracks.append(temp_dict)

        return formatted_purchased_releases, formatted_purchased_tracks

class Artist(db.Model):
    __tablename__ = 'artists'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    artist_picture = Column(String, unique=False, nullable=True)
    releases = db.relationship(
        'Release', backref='artist', cascade='all, delete', lazy=True)
    tracks = db.relationship('Track', backref='artist',
                             cascade='all, delete', lazy=True)
    user_id = Column(Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    user = db.relationship('User', back_populates='artist')
    wallet_address = Column(String, unique=False, nullable=True)

    # External links

    soundcloud_url = Column(String, nullable=True)
    facebook_url = Column(String, nullable=True)
    instagram_url = Column(String, nullable=True)

    created_on = Column(DateTime, server_default=db.func.now(), nullable=False)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def short(self):

        formatted_releases = [{"release_id": release.id,
                               "release_name": release.name,
                               "release_price": release.price,
                               "release_cover_art": release.cover_art,
                               "created_on": release.created_on,
                               "tracks": [{"track_name": track.name,
                                           "track_id": track.id,
                                           "track_price": track.price}
                                          for track in release.tracks]}
                              for release in self.releases]

        # Checks if external link is null, and replace with empty string if null for 
        # rendering in jinja

        if self.soundcloud_url is None:
            soundcloud_url = ""
        else:
            soundcloud_url = self.soundcloud_url

        if self.facebook_url is None:
            facebook_url = ""
        else:
            facebook_url = self.facebook_url

        if self.instagram_url is None:
            instagram_url = ""
        else:
            instagram_url = self.instagram_url

        return {
            'id': self.id,
            'user': self.user_id,
            'name': self.name,
            'country': self.country,
            'artist_picture': self.artist_picture,
            'soundcloud_url': soundcloud_url,
            'facebook_url': facebook_url,
            'instagram_url': instagram_url,
            'releases': formatted_releases
        }


class Release(db.Model):
    __tablename__ = 'releases'

    id = Column(Integer, primary_key=True)
    artist_id = Column(Integer, db.ForeignKey('artists.id'))
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    tracks = db.relationship('Track', backref='release',
                             cascade='all, delete', lazy=True)
    cover_art = Column(String, unique=True, nullable=True)
    description = Column(String, nullable=True)
    created_on = Column(DateTime, server_default=db.func.now(), nullable=False)
    smart_contract_address=Column(String, unique=True, nullable=True)


    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def purchase_description(self):

        description = self.artist.name + " - " + self.name

        return description

    def short_public(self):

        formatted_tracks = [{"name": track.name,
                             "track_id": track.id} for track in self.tracks]

            # Get YouTube playlist URL from tracks' YouTube URL

        youtube_embed_url = 'https://youtube.com/embed/'
        added_track_count = 0

        for i in range(len(self.tracks)):

            current_track = self.tracks[i]
            if current_track.youtube_url is not None:

                track_youtube_id = current_track.youtube_url.rsplit('/')[-1]

                if added_track_count == 0:

                    youtube_embed_url += track_youtube_id
                    added_track_count += 1
                    print(track_youtube_id)

                elif added_track_count == 1:
                    youtube_embed_url += '?playlist='
                    youtube_embed_url += track_youtube_id
                    youtube_embed_url += ','
                    added_track_count += 1

                else:
                    youtube_embed_url += track_youtube_id
                    youtube_embed_url += ','

        return {
            'id': self.id,
            'artist_id': self.artist_id,
            'artist_name': self.artist.name,
            'release_name': self.name,
            'cover_art': self.cover_art,
            'description': self.description,
            'price': self.price,
            'tracks': formatted_tracks,
            'created_on': self.created_on,
            'smart_contract_address': self.smart_contract_address,
            'youtube_embed_url': youtube_embed_url
        }

    def short_private(self):

        formatted_tracks = [{"name": track.name,
                             "track_id": track.id,
                             "track_download_url": track.download_url} for track in self.tracks]

        return {
            'id': self.id,
            'artist_id': self.artist_id,
            'artist_name': self.artist.name,
            'release_name': self.name,
            'cover_art': self.cover_art,
            'description': self.description,
            'price': self.price,
            'tracks': formatted_tracks,
            'created_on': self.created_on.strftime('%#d %B %Y'),
            'smart_contract_address': self.smart_contract_address
        }

    def get_purchasers(self):

        purchases = Purchase.query.filter(Purchase.release_id==self.id)

        result = []

        for purchase in purchases:

            purchaser_name = User.query.get(purchase.user_id).username

            if purchaser_name not in result:
                temp_dict = {}
                temp_dict['user_id'] = purchase.user_id
                temp_dict['username'] = purchaser_name
                temp_dict['profile_picture'] = User.query.get(purchase.user_id).profile_picture
                result.append(temp_dict)

        return result

class Track(db.Model):
    __tablename__ = 'tracks'

    id = Column(Integer, primary_key=True)
    artist_id = Column(Integer, db.ForeignKey('artists.id'))
    release_id = Column(Integer, db.ForeignKey('releases.id'))
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    created_on = Column(DateTime, server_default=db.func.now(), nullable=False)
    download_url = Column(String, unique=True, nullable=True)
    youtube_url = Column(String, unique=True, nullable=True)

    __table_args__ = (UniqueConstraint('artist_id', 'release_id', 'name', name='unique_track_name'), )

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def purchase_description(self):

        description = self.artist.name + " - " + self.name

        return description

    def short_public(self):

        youtube_embed_url = 'https://youtube.com/embed/'

        if self.youtube_url is not None:
            track_youtube_id = self.youtube_url.rsplit('/')[-1]
            youtube_embed_url += track_youtube_id

        return {
            'id': self.id,
            'artist_id': self.artist_id,
            'artist_name': self.artist.name,
            'release_id': self.release_id,
            'release_name': self.release.name,
            'release_cover_art': self.release.cover_art,
            'track_name': self.name,
            'created_on': self.created_on,
            'smart_contract_address': self.release.smart_contract_address,
            'price': self.price,
            'youtube_url': self.youtube_url,
            'youtube_embed_url': youtube_embed_url
        }

    def get_purchasers(self):

        purchases = Purchase.query.filter(Purchase.track_id==self.id)

        result = []

        for purchase in purchases:
            
            purchaser_name = User.query.get(purchase.user_id).username

            if purchaser_name not in result:
                temp_dict = {}
                temp_dict['user_id'] = purchase.user_id
                temp_dict['username'] = purchaser_name
                temp_dict['profile_picture'] = User.query.get(purchase.user_id).profile_picture
                result.append(temp_dict)

        return result

class Purchase(db.Model):
    __tablename__ = 'purchases'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey('users.id'))
    release_id = Column(Integer, db.ForeignKey('releases.id'), nullable=True)
    track_id = Column(Integer, db.ForeignKey('tracks.id'), nullable=True)
    paid = Column(Float, nullable=False)
    purchased_on = Column(DateTime, server_default=db.func.now(), nullable=False)
    transaction_hash = Column(String, unique=True, nullable=False)
    wallet_address = Column(String, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'release_id', name='unique_release_purchase'), 
        CheckConstraint('NOT(release_id IS NULL and track_id IS NULL)', name ='release_or_track_id_defined'),
        CheckConstraint('NOT(release_id IS NOT NULL and track_id IS NOT NULL)', name = 'only_release_or_track_id_defined'),
        )

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def short(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'release_id': self.release_id,
            'paid': self.paid,
            'purchased_on': self.purchased_on.strftime('%#d %B %Y')
        }

class MusicakesContractFactory(db.Model):

    id = Column(Integer, primary_key=True)
    smart_contract_address=Column(String, unique=True, nullable=False)
    description=Column(String, nullable=True)

    def short(self):
        return {
            'id': self.id,
            'smart_contract_address': self.smart_contract_address,
            'description': self.description
        }

class PurchaseCeleryTask(db.Model):

    task_id = Column(String, primary_key=True)
    user_id = Column(Integer, db.ForeignKey('users.id'), nullable=False)
    wallet_address = Column(String, nullable=False)
    transaction_hash = Column(String, unique=True, nullable=False)
    purchase_description = Column(String, nullable=False)
    purchase_type = Column(String, nullable=False)
    purchase_type_id = Column(Integer, nullable=False)
    started_on = Column(DateTime, server_default=db.func.now(), nullable=False)
    is_confirmed = Column(Boolean, default=False, nullable=False)
    is_visible = Column(Boolean, default=True, nullable=False)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def short(self):
        return {
            'task_id': self.task_id,
            'user_id': self.user_id,
            'wallet_address': self.wallet_address,
            'transaction_hash': self.transaction_hash,
            'purchase_description': self.purchase_description,
            'purchase_type': self.purchase_type,
            'purchase_type_id': self.purchase_type_id,
            'is_confirmed': self.is_confirmed,
            'is_visible': self.is_visible
        }

class PaymentToken(db.Model):

    id = Column(Integer, primary_key=True)
    smart_contract_address = Column(String, unique=True, nullable=False)
    ticker = Column(String, unique=False, nullable=False)

    def short(self):
        return {
            'id': self.id,
            'smart_contract_address': self.smart_contract_address,
            'ticker': self.ticker
        }