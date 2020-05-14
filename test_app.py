'''
Tests for the musicakes flask app
'''

import os
import unittest
import json
import http.client
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

from app import create_app
from models import setup_db, Artist, Release, Track

## Load environment variables from .env

load_dotenv()

TEST_DATABASE_PATH = os.getenv('TEST_DATABASE_PATH', 'Does not exist')

AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN', 'Does not exist')
ALGORITHMS = os.getenv('ALGORITHMS', 'Does not exist')
API_AUDIENCE = os.getenv('API_AUDIENCE', 'Does not exist')
MANAGER_TOKEN = os.getenv('MANAGER_TOKEN', 'Does not exist')
ASSISTANT_TOKEN = os.getenv('ASSISTANT_TOKEN', 'Does not exist')

unittest.TestLoader.sortTestMethodUsing = None


class MusicakesTestCase(unittest.TestCase):

	"""This class represents the music store test case"""

	def setUp(self):
		"""Define test variables and initialise the app."""
		self.app = create_app()
		self.client = self.app.test_client
		
		self.database_path = TEST_DATABASE_PATH
		setup_db(self.app, self.database_path)

		# binds the app to the current context
		with self.app.app_context():
			self.db = SQLAlchemy()
			self.db.init_app(self.app)
			# create tables 
			self.db.create_all()


	def tearDown(self):
		pass

	def test_001_get_artists(self):

		"""
			Test get_artists() for empty table
		"""

		res = self.client().get('/artists')

		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success'], True)

	def test_002_get_releases(self):

		"""
			Test get_releases() for empty table
		"""

		res = self.client().get('/releases')

		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success'], True)

	def test_003_get_tracks(self):

		"""
			Test get_tracks() for empty table
		"""

		res = self.client().get('/tracks')

		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success'], True)


	def test_004_manager_create_artist(self):

		"""
			Test create_artist() with Manager role
		"""

		res = self.client().post(
				'/artists', 
				headers = {
					"Authorization": f"Bearer {MANAGER_TOKEN}"
				},
				json = {
					"name": "Nicolas Jaar",
					"country": "US"
				},
				follow_redirects=True
			)

		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success'], True)
		self.assertEqual(data['name'], "Nicolas Jaar")

	def test_005_manager_create_artist_insufficient_info(self):

		"""
			Test create_artist() with Manager role and insufficient input
		"""

		res = self.client().post(
				'/artists', 
				headers = {
					"Authorization": f"Bearer {MANAGER_TOKEN}"
				},
				json = {
					"name": "Jeff Mills",
				},
				follow_redirects=True
			)

		data = json.loads(res.data)

		self.assertEqual(res.status_code, 422)
		self.assertEqual(data['success'], False)

	def test_006_public_create_artist(self):
		"""
			Test create_artist() as a public with no permission to do so
		"""

		res = self.client().post(
				'/artists', 

				json = {
					"name": "Jeff Mills",
					"country": "US"
				}
			)

		data = json.loads(res.data)

		self.assertEqual(res.status_code, 401)
		self.assertEqual(data['success'], False)

	def test_007_assistant_create_release(self):

		"""
			Test create_release() with Assistant role
		"""

		res = self.client().post(
				'/releases', 
				headers = {
					"Authorization": f"Bearer {ASSISTANT_TOKEN}"
				},
				json = {
					"artist_id": 1,
					"name": "Sirens",
					"price": 15
				},
				follow_redirects=True
			)

		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['name'], "Sirens")
		self.assertEqual(data['price'], 15)

	def test_008_assistant_create_release_insufficient(self):
		"""
			Test create_release() with Assistant role and insufficient input
		"""

		res = self.client().post(
				'/releases', 
				headers = {
					"Authorization": f"Bearer {ASSISTANT_TOKEN}"
				},
				json = {
					"artist_id": 1,
					"name": "Space Is Only Noise",
				},
				follow_redirects=True
			)

		data = json.loads(res.data)

		self.assertEqual(res.status_code, 422)
		self.assertEqual(data['success'], False)


	def test_009_create_track_public(self):

		"""
			Test create_track() as a public with no permission to do so
		"""

		res = self.client().post(
				'/tracks', 

				json = {
					"name": "Killing Time",
					"price": 2,
					"artist_id": 1,
					"release_id": 1
				}
			)

		data = json.loads(res.data)

		self.assertEqual(res.status_code, 401)
		self.assertEqual(data['success'], False)


	def test_010_create_track(self):

		"""
			Test create_track() as a Manager
		"""
		res = self.client().post(
				'/tracks', 
				headers = {
					"Authorization": f"Bearer {MANAGER_TOKEN}"
				},
				json = {
					"name": "Killing Time",
					"price": 2,
					"artist_id": 1,
					"release_id": 1
				},
				follow_redirects=True
			)

		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['name'], "Killing Time")
		self.assertEqual(data['artist_id'], 1)
		self.assertEqual(data['release_id'], 1)

	def test_011_create_track_manager_artist_error(self):

		"""
			Test create_track() as a Manager with non-existent artist
		"""
		res = self.client().post(
				'/tracks', 
				headers = {
					"Authorization": f"Bearer {MANAGER_TOKEN}"
				},
				json = {
					"name": "Killing Time",
					"price": 2,
					"artist_id": 50,
					"release_id": 1
				},
				follow_redirects=True
			)

		data = json.loads(res.data)

		self.assertEqual(res.status_code, 422)
		self.assertEqual(data['success'], False)

	def test_012_update_artist_nonexistent(self):

		"""
			Test update_artist() as an Assistant with non-existent artist
		"""
		res = self.client().patch(
				'/artists/100', 
				headers = {
					"Authorization": f"Bearer {ASSISTANT_TOKEN}"
				},
				json = {
					"name": "Call Super",
				},
				follow_redirects=True
			)

		data = json.loads(res.data)

		self.assertEqual(res.status_code, 400)
		self.assertEqual(data['success'], False)

	def test_013_update_artist_public(self):

		"""
			Test update_artist() as a public with no permission to do so
		"""

		res = self.client().patch(
				'/artists/1', 

				json = {
					"name": "Call Super"
				}
			)

		data = json.loads(res.data)

		self.assertEqual(res.status_code, 401)
		self.assertEqual(data['success'], False)

	def test_014_update_artist(self):

		"""
			Test update_artist() as an Assistant
		"""
		res = self.client().patch(
				'/artists/1', 
				headers = {
					"Authorization": f"Bearer {ASSISTANT_TOKEN}"
				},
				json = {
					"name": "Call Super",
				},
				follow_redirects=True
			)

		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['name'], "Call Super")

	def test_015_update_release_nonexistent(self):

		"""
			Test update_release() as an Assistant with non-existent artist
		"""
		res = self.client().patch(
				'/releases/100', 
				headers = {
					"Authorization": f"Bearer {ASSISTANT_TOKEN}"
				},
				json = {
					"name": "Comfortably Numb",
				},
				follow_redirects=True
			)

		data = json.loads(res.data)

		self.assertEqual(res.status_code, 400)
		self.assertEqual(data['success'], False)

	def test_016_update_release_public(self):

		"""
			Test update_release() as a public with no permission to do so
		"""

		res = self.client().patch(
				'/releases/1', 

				json = {
					"name": "Pomegranates"
				}
			)

		data = json.loads(res.data)

		self.assertEqual(res.status_code, 401)
		self.assertEqual(data['success'], False)

	def test_017_update_release(self):

		"""
			Test update_release() as an Assistant
		"""
		res = self.client().patch(
				'/releases/1', 
				headers = {
					"Authorization": f"Bearer {ASSISTANT_TOKEN}"
				},
				json = {
					"price": 40,
				},
				follow_redirects=True
			)

		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['price'], 40)

	def test_018_update_track_nonexistent(self):

		"""
			Test update_track() as an Assistant with non-existent track
		"""
		res = self.client().patch(
				'/track/100', 
				headers = {
					"Authorization": f"Bearer {ASSISTANT_TOKEN}"
				},
				json = {
					"name": "Parallaxis",
				},
				follow_redirects=True
			)

		data = json.loads(res.data)

		self.assertEqual(res.status_code, 404)
		self.assertEqual(data['success'], False)

	def test_019_update_track_public(self):

		"""
			Test update_track() as a public with no permission to do so
		"""

		res = self.client().patch(
				'/tracks/1', 

				json = {
					"name": "Three Flags"
				}
			)

		data = json.loads(res.data)

		self.assertEqual(res.status_code, 401)
		self.assertEqual(data['success'], False)

	def test_020_update_track(self):

		"""
			Test update_track() as a Manager
		"""
		res = self.client().patch(
				'/tracks/1', 
				headers = {
					"Authorization": f"Bearer {MANAGER_TOKEN}"
				},
				json = {
					"name": "Three Flags",
					"price": 4
				},
				follow_redirects=True
			)

		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['price'], 4)
		self.assertEqual(data['name'], "Three Flags")

	def test_021_delete_track_assistant(self):
		"""
			Test delete_track() as an Assistant with no permission
		"""

		res = self.client().delete(
				'/tracks/1', 
				headers = {
					"Authorization": f"Bearer {ASSISTANT_TOKEN}"
				},
				follow_redirects=True
			)


		data = json.loads(res.data)

		self.assertEqual(res.status_code, 401)
		self.assertEqual(data['success'], False)

	def test_022_delete_track_nonexistent(self):
		"""
			Test delete_track() as a Manager for non-existent track
		"""

		res = self.client().delete(
				'/tracks/100', 
				headers = {
					"Authorization": f"Bearer {MANAGER_TOKEN}"
				},
				follow_redirects=True
			)

		data = json.loads(res.data)

		self.assertEqual(res.status_code, 422)
		self.assertEqual(data['success'], False)

	def test_023_delete_track(self):
		"""
			Test delete_track() as a Manager
		"""

		res = self.client().delete(
				'/tracks/1', 
				headers = {
					"Authorization": f"Bearer {MANAGER_TOKEN}"
				},
				follow_redirects=True
			)

		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success'], True)

	def test_024_delete_release_assistant(self):
		"""
			Test delete_release() as an Assistant with no permission
		"""

		res = self.client().delete(
				'/releases/1', 
				headers = {
					"Authorization": f"Bearer {ASSISTANT_TOKEN}"
				},
				follow_redirects=True
			)

		data = json.loads(res.data)

		self.assertEqual(res.status_code, 401)
		self.assertEqual(data['success'], False)

	def test_025_delete_release_nonexistent(self):
		"""
			Test delete_release() as a Manager for non-existent release
		"""

		res = self.client().delete(
				'/releases/100', 
				headers = {
					"Authorization": f"Bearer {MANAGER_TOKEN}"
				},
				follow_redirects=True
			)

		data = json.loads(res.data)

		self.assertEqual(res.status_code, 422)
		self.assertEqual(data['success'], False)

	def test_026_delete_release(self):
		"""
			Test delete_release() as a Manager
		"""

		res = self.client().delete(
				'/releases/1', 
				headers = {
					"Authorization": f"Bearer {MANAGER_TOKEN}"
				},
				follow_redirects=True
			)

		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success'], True)

	def test_027_delete_artist_assistant(self):
		"""
			Test delete_artist() as an Assistant with no permission
		"""

		res = self.client().delete(
				'/artists/1', 
				headers = {
					"Authorization": f"Bearer {ASSISTANT_TOKEN}"
				},
				follow_redirects=True
			)

		data = json.loads(res.data)

		self.assertEqual(res.status_code, 401)
		self.assertEqual(data['success'], False)

	def test_028_delete_artist_nonexistent(self):
		"""
			Test delete_artist() as a Manager for non-existent release
		"""

		res = self.client().delete(
				'/artists/100', 
				headers = {
					"Authorization": f"Bearer {MANAGER_TOKEN}"
				},
				follow_redirects=True
			)

		data = json.loads(res.data)

		self.assertEqual(res.status_code, 422)
		self.assertEqual(data['success'], False)

	def test_029_delete_artist(self):
		"""
			Test delete_artist() as a Manager
		"""

		res = self.client().delete(
				'/artists/1', 
				headers = {
					"Authorization": f"Bearer {MANAGER_TOKEN}"
				},
				follow_redirects=True
			)

		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success'], True)


if __name__ == "__main__":
	unittest.main()
