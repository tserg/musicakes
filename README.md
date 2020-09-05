# Musicakes

This is an application for artists to list their music for sale, and for fans to buy music from artists. Artists can post their releases and tracks for sale. Every track must have a release, but a release can have a single track or multiple tracks.

When an artist creates a release, the artist will also deploy a smart contract on the Ethereum blockchain. Payments are made using the DAI ERC-20 token on the Ethereum blockchain to a smart contract address. At the time of creation, the smart contract will also mint Musicakes tokens to the artist's wallet address, representing the right to claim payments from that specific smart contract.

Artists with less than five tracks will have all 100 Musicakes tokens minted to their wallet addresses.

For artists with five or more tracks, 98 Musicakes tokens will be minted to their wallet address, and 2 Musicakes tokens will be minted to the platform, representing a 2% fee.

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

#### Staging Environment

The staging environment has been deployed at `https://musicakes-staging.herokuapp.com`.

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
2. Navigate to Auth0 login URL: "`http://localhost:5000`"
3. Create the database in psql by running:
For Linux:
```
createdb musicakes_test
```

For Windows:
```
CREATE DATABASE musicakes_test;
```
4. Change the database path for TEST_DATABASE_PATH in .env to your test database path.

#### Ropsten Testnet

Contract factory addresses on Ropsten testnet are:
  * 0x97107a1544361baF4865C882b24e8B0B9244d117 (100 tokens to creator)
  * 0xec67abe36b67afB03228101b7110A0a6155fdCdD (98 tokens to creator, 2 to project)

## API Reference

### Getting Started

### Error Handling

The server will return the following error types when requests fail:
* 400: Bad request
* 401: Unauthorized
* 404: Resource not found
* 405: Method not allowed
* 422: Unprocessable
* 500: Internal server error
* AuthError: [AuthError['description']]

## Authors

Gary Tse

## Acknowledgements

Introduction, Getting Started and API Reference adapted from Udacity's default READMEs.