'''
Tests for the musicakes flask app
'''

import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db, Artist, Release, Track

class MusicakesTestCase(unittest.TestCase):

	"""This class represents the music store test case"""

	def setUp(self):
		"""Define test variables and initialise the app."""
		self.app = create_app()
		self.client = self.app.test_client
		self.database_name = "musicakes_test"
		self.database_path = "postgres://{}:{}@{}/{}".format('postgres', 'garytse17', 'localhost:5432', self.database_name)
		setup_db(self.app, self.database_path)

		# binds the app to the current context
		with self.app.app_context():
			self.db = SQLAlchemy()
			self.db.init_app(self.app)
			# create tables 
			self.db.create_all()

	def tearDown(self):
		pass

	def test_get_artists(self):

		res = self.client().get('/artists')

		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(len(data['artists']), 0)

if __name__ == "__main__":
	unittest.main()



'''

import os
import json
import pytest
import app

from app import create_app
from models import setup_db, Artist, Release, Track

@pytest.fixture
def client():

	client = app.APP.test_client()

	yield client

def test_get_artists(client):

	response = client.get('/artists')
	data = json.loads(response.data)

	assert response.status_code == 200
	assert len(response.data) == 0
'''