# Musicakes

This is an application for artists to list their music for sale, and for fans to buy music from artists.

## Getting Started

### Prerequisites & Installation

### Testing

Auth0 login URL: `https://fsndgt.au.auth0.com/authorize?audience=dev&response_type=token&client_id=k0UiQ1k69kaVYwB7Os4lep8kHQRTj1do&redirect_uri=http://127.0.0.1:5000/artists`


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

#### GET /artists
* General
  * Gets information of all artists
* Sample: `curl http://127.0.0.1:5000/artists`

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
* Sample: `curl http://127.0.0.1:5000/releases`

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
* Sample: `curl http://127.0.0.1:5000/tracks`

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
* Sample: `curl -X POST -H "Content-Type: application/json" -d '{ "name": "shampoo", "country": "UK" }' http://127.0.0.1:5000/artists`

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
* Sample: `curl -X POST -H "Content-Type: application/json" -d '{ "name": "Forgotten Times", "artist_id": 1, "price": 5 }' http://127.0.0.1:5000/releases`

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
* Sample: `curl -X POST -H "Content-Type: application/json" -d '{ "name": "Forgotten Past", "release_id": 1, "artist_id": 1, "price": 1 }' http://127.0.0.1:5000/tracks`

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
* Sample: `curl -X PATCH -H "Content-Type: application/json" -d '{ "name": "Tsergggy", "country": "Tuvalu" }' http://127.0.0.1:5000/artists/1`

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
* Sample: `curl -X PATCH -H "Content-Type: application/json" -d '{ "name": "Forgotten Times 2", "price": 10, "artist_id": 3 }' http://127.0.0.1:5000/releases/1`

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
* Sample: `curl -X PATCH -H "Content-Type: application/json" -d '{ "name": "Forgotten Now", "price": 2, "release_id": 2, "artist_id": 3 }' http://127.0.0.1:5000/tracks/1`

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
* Sample: `curl -X DELETE http://127.0.0.1:5000/artists/1`

```
{
  "success": true
}
```

#### DELETE /releases/<int:id>
* General
  * Deletes a release and all tracks in that release
* Sample: `curl -X DELETE http://127.0.0.1:5000/releases/2`

```
{
  "success": true
}
```

#### DELETE /tracks/<int:id>
* General
  * Deletes a track
* Sample: `curl -X DELETE http://127.0.0.1:5000/tracks/5`

```
{
  "success": true
}
```
