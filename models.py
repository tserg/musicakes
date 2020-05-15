import os
# from dotenv import load_dotenv
from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import json

db = SQLAlchemy()

## Load environment variables from .env

# load_dotenv()

# database_path = os.getenv('DATABASE_PATH', 'Does not exist')

database_path = os.environ.get('DATABASE_URL')


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


class Artist(db.Model):
	__tablename__ = 'artists'

	id = Column(Integer, primary_key=True)
	name = Column(String, nullable=False)
	country = Column(String, nullable=False)
	releases = db.relationship('Release', backref='artist', cascade = 'all, delete', lazy=True)
	tracks = db.relationship('Track', backref='artist', cascade = 'all, delete', lazy = True)

	

	def insert(self):
		db.session.add(self)
		db.session.commit()

	def update(self):
		db.session.commit()

	def delete(self):
		db.session.delete(self)
		db.session.commit()

	def short(self):

		formatted_releases = [{"release_id": release.id, "release_name": release.name, 
								"release_price": release.price,
								"tracks": [{"track_name": track.name, "track_id": track.id, "track_price": track.price} for track in release.tracks]}
								for release in self.releases]

		return {
			'id': self.id,
			'name': self.name,
			'country': self.country,
			'releases': formatted_releases
		}


class Release(db.Model):
	__tablename__ = 'releases'

	id = db.Column(db.Integer, primary_key=True)
	artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))
	name = db.Column(db.String, nullable=False)
	price = db.Column(db.Integer, nullable=False)
	tracks = db.relationship('Track', backref='release', cascade='all, delete', lazy=True)

	def insert(self):
		db.session.add(self)
		db.session.commit()

	def update(self):
		db.session.commit()

	def delete(self):
		db.session.delete(self)
		db.session.commit()

	def short(self):

		formatted_tracks = [{"name": track.name, "track_id": track.id} for track in self.tracks]

		return {
			'id': self.id,
			'artist_id': self.artist_id,
			'artist_name': self.artist.name,
			'release_name': self.name,
			'price': self.price,
			'tracks': formatted_tracks
		}

class Track(db.Model):
	__tablename__ = 'tracks'

	id = db.Column(db.Integer, primary_key=True)
	artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))
	release_id = db.Column(db.Integer, db.ForeignKey('releases.id'))
	name = db.Column(db.String, nullable=False)
	price = db.Column(db.Integer, nullable=False)

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
			'artist_id': self.artist_id,
			'artist_name': self.artist.name,
			'release_id': self.release_id,
			'release_name': self.release.name,
			'track_name': self.name,
			'price': self.price
		}





