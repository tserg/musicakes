import os
from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import json

db = SQLAlchemy()


def setup_db(app):

	'''
		binds a flask application and a SQLAlchemy service
	'''
	app.config.from_object('config')
	db.app = app
	db.init_app(app)
	db.create_all()
	migrate = Migrate(app, db)


class Artist(db.Model):
	__tablename__ = 'artists'

	id = Column(Integer, primary_key=True)
	name = Column(String, nullable=False)
	country = Column(String, nullable=False)


class Release(db.Model):
	__tablename__ = 'releases'

	id = db.Column(db.Integer, primary_key=True)
	artist = db.Column(db.Integer, db.ForeignKey('artists.id'))
	name = db.Column(db.String, nullable=False)
	price = db.Column(db.Integer, nullable=False)
	tracks = db.relationship('Track', backref='release', cascade='all, delete', lazy=True)

class Track(db.Model):
	__tablename__ = 'tracks'

	id = db.Column(db.Integer, primary_key=True)
	artist = db.Column(db.Integer, db.ForeignKey('artists.id'))
	release = db.Column(db.Integer, db.ForeignKey('releases.id'))
	name = db.Column(db.String, nullable=False)
	price = db.Column(db.Integer, nullable=False)
	



