# Musicakes

This is an application for artists to list their music for sale, and for fans to buy music from artists.

## Getting Started

### Prerequisites & Installation

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
