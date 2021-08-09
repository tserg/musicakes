# Musicakes

This is an application for artists to list their music for sale, and for fans to buy music from artists. Artists can post their releases and tracks for sale. Every track must have a release, but a release can have a single track or multiple tracks.

When an artist creates a release, the artist will also deploy a smart contract on the Ethereum blockchain. Payments are made using the DAI ERC-20 token on the Ethereum blockchain to a smart contract address. At the time of creation, the smart contract will also mint Musicakes tokens to the artist's wallet address, representing the right to claim payments from that specific smart contract.

Artists will have all 100 Musicakes tokens minted to their wallet addresses.

In the future, we may implement a 2% fee for artists with five or more tracks to cover AWS costs. This will be implemented by having 98 Musicakes tokens minted to their wallet address, and 2 Musicakes tokens minted to the platform, representing a 2% fee.

This application has been deployed at https://musicakes.herokuapp.com

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
export FLASK_APP=musicakes
export FLASK_ENV=development
flask run
```

For Windows, navigate to the flaskr directory and execute:

```
set FLASK_APP=musicakes
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
export FLASK_APP=musicakes
```
For Windows:
```
set FLASK_APP=musicakes
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

5. Add the DAI token into the `payment_token` table, and the Musicakes factory contract into the `musicakes_contract_factory` table. If you are on Ropsten, refer to the section below for the contract addresses.

6. Run the app by running:
```
flask run
```

7. In a new terminal, run the following command to start a Celery worker
```
celery -A musicakes.celery_app worker
```

#### Ropsten Testnet

DAI token address on Ropsten testnet is:
  * 0xad6d458402f60fd3bd25163575031acdce07538d

Contract factory addresses on Ropsten testnet are:
  * 0x8232d36c1dc9EACf5089Ac76cbbf37CDfB678D82 (100 tokens to creator)
  * 0xec67abe36b67afB03228101b7110A0a6155fdCdD (98 tokens to creator, 2 to project)

#### Mainnet

Contract factory addresses on mainnet are:
  * 0x6C56962D9952e78422bA12B7D36C725C953AF767 (100 tokens to creator)

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
