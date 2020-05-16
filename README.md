# Musicakes

This is an application for artists to list their music for sale, and for fans to buy music from artists. Artists can post their releases and tracks for sale. Every track must have a release, but a release can have a single track or multiple tracks.

Anyone can view information on all artists, releases and tracks.

There are two roles, Manager and Assistant.
* An Assistant has permission to create and update artists, releases and tracks. An Assistant does not have permission to delete artists, releases or tracks.
* A Manager has permission to create, update and delete artists, releases and tracks.

The application has been deployed at `https://musicakes.herokuapp.com`, which currently displays "Welcome to Musicakes!"

## Getting Started

For local deployment, please follow the steps below.

### Prerequisites & Installation

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by running:
```bash
pip install -r requirements.txt
```
This will install all of the required packages we selected within the `requirements.txt` file.

### Local Development

#### Database Setup

First, create the database in your psql terminal

Run:
```
createdb musicakes
```

For Windows:
```
CREATE DATABASE musicakes;
```

#### Backend Setup

Replace <<USERNAME>> and <<PASSWORD>> with your username and password for DATABASE_PATH in .env to connect to your local database:
```
DATABASE_PATH = postgres://<<USERNAME>>:<<PASSWORD>>@localhost:5432/musicakes
```

To run the server, execute:

```bash
export FLASK_APP=app
export FLASK_ENV=development
flask run
```

For Windows, navigate to the flaskr directory and execute:

```
set FLASK_APP=app.py
set FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `app` directs flask to use the `app.py` application. 

### Testing

#### Heroku Deployment

The application has already been deployed at `https://musicakes.herokuapp.com`.

To obtain a Manager or Assistant access token:
1. Navigate to Auth0 login URL: `https://fsndgt.au.auth0.com/authorize?audience=dev&response_type=token&client_id=k0UiQ1k69kaVYwB7Os4lep8kHQRTj1do&redirect_uri=http://127.0.0.1:5000/artists`
2. Log in using the following credentials and copy the respective tokens from the URL:
  * Manager
    * Email: manager@udacity.com
    * Password: Manager2020@
  * Assistant
    * Email: assistant@udacity.com
    * Password: Assistant2020@
3. To test the API endpoints, refer to the API Reference below.

#### Local Environment

1. Set the environment variables for Flask then run `flask run`
For Linux:
```
export FLASK_APP=app.py
```
For Windows:
```
set FLASK_APP=app.py
```
2. Navigate to Auth0 login URL: `https://fsndgt.au.auth0.com/authorize?audience=dev&response_type=token&client_id=k0UiQ1k69kaVYwB7Os4lep8kHQRTj1do&redirect_uri=http://127.0.0.1:5000/artists`
3. Log in using the following credentials and copy the respective tokens from the URL:
  * Manager
    * Email: manager@udacity.com
    * Password: Manager2020@
  * Assistant
    * Email: assistant@udacity.com
    * Password: Assistant2020@
4. Paste the respective tokens into MANAGER_TOKEN and ASSISTANT_TOKEN in .env
5. Create the database in psql by running:
For Linux:
```
createdb musicakes_test
```

For Windows:
```
CREATE DATABASE musicakes_test;
```
6. Change the database path for TEST_DATABASE_PATH in .env to your test database path.
7. Run `python test_app.py`

## API Reference

### Getting Started

### Error Handling
Errors are returned as JSON objects in the following format:
```
{
    'success': False,
    'error': 400',
    'message': 'bad request'

}
```

The API will return the following error types when requests fail:
* 400: Bad request
* 404: Resource not found
* 405: Method not allowed
* 422: Unprocessable
* 500: Internal server error
* 503: Service unavailable
* AuthError: [AuthError['description']]

### Endpoints

For local testing, please replace `https://musicakes.herokuapp.com` with your local host address.

#### GET /artists
* General
  * Gets information of all artists
* Sample: `curl https://musicakes.herokuapp.com/artists`

```
{
  "artists": [
    {
      "country": "UK",
      "id": 3,
      "name": "shampoo",
      "releases": [
        {
          "release_id": 2,
          "release_name": "Half Sick",
          "release_price": 7,
          "tracks": [
            {
              "track_id": 1,
              "track_name": "Forgotten Now",
              "track_price": 2
            }
          ]
        },
        {
          "release_id": 1,
          "release_name": "Forgotten Times 2",
          "release_price": 10,
          "tracks": [
            {
              "track_id": 3,
              "track_name": "Again",
              "track_price": 2
            }
          ]
        }
      ]
    }
  ],
  "success": true
}
```

#### GET /releases
* General
  * Gets information of all releases
* Sample: `curl https://musicakes.herokuapp.com/releases`

```
{
  "releases": [
    {
      "artist_id": 3,
      "artist_name": "shampoo",
      "id": 2,
      "price": 7,
      "release_name": "Half Sick",
      "tracks": [
        {
          "name": "Forgotten Now",
          "track_id": 1
        }
      ]
    },
    {
      "artist_id": 3,
      "artist_name": "shampoo",
      "id": 1,
      "price": 10,
      "release_name": "Forgotten Times 2",
      "tracks": [
        {
          "name": "Again",
          "track_id": 3
        },
        {
          "name": "Before",
          "track_id": 5
        }
      ]
    }
  ],
  "success": true
}
```

#### GET /tracks
* General
  * Gets information of all tracks
* Sample: `curl https://musicakes.herokuapp.com/tracks`

```
{
  "success": true,
  "tracks": [
    {
      "artist_id": 3,
      "artist_name": "shampoo",
      "id": 1,
      "price": 2,
      "release_id": 2,
      "release_name": "Half Sick",
      "track_name": "Forgotten Now"
    },
    {
      "artist_id": 1,
      "artist_name": "Tsergggy",
      "id": 2,
      "price": 1,
      "release_id": 3,
      "release_name": "Test",
      "track_name": "End Of An Era"
    },
    {
      "artist_id": 3,
      "artist_name": "shampoo",
      "id": 3,
      "price": 2,
      "release_id": 1,
      "release_name": "Forgotten Times 2",
      "track_name": "Again"
    },
    {
      "artist_id": 3,
      "artist_name": "shampoo",
      "id": 5,
      "price": 2,
      "release_id": 1,
      "release_name": "Forgotten Times 2",
      "track_name": "Before"
    }
  ]
}
```


#### POST /artists
* General
  * Creates an artist with the following request arguments: name, country
* Sample: `curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer <<MANAGER_TOKEN or ASSISTANT_TOKEN>>" -d '{ "name": "shampoo", "country": "UK" }' https://musicakes.herokuapp.com/artists` - replace "<<MANAGER_TOKEN or ASSISTANT_TOKEN>>" with MANAGER_TOKEN or ASSISTANT_TOKEN

```
{
  "country": "UK",
  "name": "shampoo",
  "success": true
}
```

#### POST /releases
* General
  * Creates a release with the following request arguments: name, artist_id, price
* Sample: `curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer <<MANAGER_TOKEN or ASSISTANT_TOKEN>>" -d '{ "name": "Forgotten Times", "artist_id": 1, "price": 5 }' https://musicakes.herokuapp.com/releases` - replace "<<MANAGER_TOKEN or ASSISTANT_TOKEN>>" with MANAGER_TOKEN or ASSISTANT_TOKEN

```
{
  "artist_id": 1,
  "name": "Forgotten Times",
  "price": 5,
  "success": true
}
```

#### POST /tracks
* General
  * Creates a track with the following request arguments: name, release_id, artist_id, price
* Sample: `curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer <<MANAGER_TOKEN or ASSISTANT_TOKEN>>" -d '{ "name": "Forgotten Past", "release_id": 1, "artist_id": 1, "price": 1 }' https://musicakes.herokuapp.com/tracks` - replace "<<MANAGER_TOKEN or ASSISTANT_TOKEN>>" with MANAGER_TOKEN or ASSISTANT_TOKEN

```
{
  "artist_id": 1,
  "name": "Forgotten Past",
  "price": 1,
  "release_id": 1,
  "success": true
}
```

#### PATCH /artists/<int:id>
* General
  * Updates an artist's information
* Sample: `curl -X PATCH -H "Content-Type: application/json" -H "Authorization: Bearer <<MANAGER_TOKEN or ASSISTANT_TOKEN>>" -d '{ "name": "Tsergggy", "country": "Tuvalu" }' https://musicakes.herokuapp.com/artists/1` - replace "<<MANAGER_TOKEN or ASSISTANT_TOKEN>>" with MANAGER_TOKEN or ASSISTANT_TOKEN

```
{
  "country": "Tuvalu",
  "name": "Tsergggy",
  "success": true
}
```

#### PATCH /releases/<int:id>
* General
  * Updates a release's information
* Sample: `curl -X PATCH -H "Content-Type: application/json" -H "Authorization: Bearer <<MANAGER_TOKEN or ASSISTANT_TOKEN>>" -d '{ "name": "Forgotten Times 2", "price": 10, "artist_id": 3 }' https://musicakes.herokuapp.com/releases/1` - replace "<<MANAGER_TOKEN or ASSISTANT_TOKEN>>" with MANAGER_TOKEN or ASSISTANT_TOKEN

```
{
  "artist_id": 3,
  "name": "Forgotten Times 2",
  "price": 10,
  "success": true
}
```

#### PATCH /tracks/<int:id>
* General
  * Updates a track's information
* Sample: `curl -X PATCH -H "Content-Type: application/json" -H "Authorization: Bearer <<MANAGER_TOKEN or ASSISTANT_TOKEN>>" -d '{ "name": "Forgotten Now", "price": 2, "release_id": 2, "artist_id": 3 }' https://musicakes.herokuapp.com/tracks/1` - replace "<<MANAGER_TOKEN or ASSISTANT_TOKEN>>" with MANAGER_TOKEN or ASSISTANT_TOKEN

```
{
  "artist_id": 3,
  "name": "Forgotten Now",
  "price": 2,
  "release_id": 2,
  "success": true
}
```

#### DELETE /releases/<int:id>
* General
  * Deletes an artist, and all releases and tracks associated with that artist
* Sample: `curl -X DELETE -H "Authorization: Bearer <<MANAGER_TOKEN>>" https://musicakes.herokuapp.com/artists/1` - replace "<<MANAGER_TOKEN>>" with MANAGER_TOKEN

```
{
  "success": true
}
```

#### DELETE /releases/<int:id>
* General
  * Deletes a release and all tracks in that release
* Sample: `curl -X DELETE -H "Authorization: Bearer <<MANAGER_TOKEN>>" https://musicakes.herokuapp.com/releases/2` - replace "<<MANAGER_TOKEN>>" with MANAGER_TOKEN

```
{
  "success": true
}
```

#### DELETE /tracks/<int:id>
* General
  * Deletes a track
* Sample: `curl -X DELETE -H "Authorization: Bearer <<MANAGER_TOKEN>>" https://musicakes.herokuapp.com/tracks/5` - replace "<<MANAGER_TOKEN>>" with MANAGER_TOKEN

```
{
  "success": true
}
```

## Authors

Gary Tse

## Acknowledgements

Introduction, Getting Started and API Reference adapted from Udacity's default READMEs.