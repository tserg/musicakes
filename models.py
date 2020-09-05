import os
from dotenv import load_dotenv
from sqlalchemy import Column, String, Integer, Float, create_engine, DateTime, UniqueConstraint, CheckConstraint
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
            'created_on': self.created_on
        }

    def short_public(self):

        return {
            'id': self.id,
            'username': self.username,
            'profile_picture': self.profile_picture,
            'created_on': self.created_on,
        }

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
                               "tracks": [{"track_name": track.name,
                                           "track_id": track.id,
                                           "track_price": track.price}
                                          for track in release.tracks]}
                              for release in self.releases]

        return {
            'id': self.id,
            'user': self.user_id,
            'name': self.name,
            'country': self.country,
            'artist_picture': self.artist_picture,
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

    def short_public(self):

        formatted_tracks = [{"name": track.name,
                             "track_id": track.id} for track in self.tracks]

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
            'smart_contract_address': self.smart_contract_address
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
            'created_on': self.created_on,
            'smart_contract_address': self.smart_contract_address
        }


class Track(db.Model):
    __tablename__ = 'tracks'

    id = Column(Integer, primary_key=True)
    artist_id = Column(Integer, db.ForeignKey('artists.id'))
    release_id = Column(Integer, db.ForeignKey('releases.id'))
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    created_on = Column(DateTime, server_default=db.func.now(), nullable=False)
    download_url = Column(String, unique=True, nullable=True)

    __table_args__ = (UniqueConstraint('artist_id', 'release_id', 'name', name='unique_track_name'), )

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def short_public(self):
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
            'price': self.price
        }

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
            'purchased_on': self.purchased_on
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