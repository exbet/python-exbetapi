# Exbet-API bindings for Python 3

![exbetapi](https://github.com/exbet/python-exbetapi/workflows/tox/badge.svg?branch=develop)
![exbetapi](https://github.com/exbet/python-exbetapi/workflows/tox/badge.svg?branch=master)
[![Documentation Status](https://readthedocs.org/projects/python-exbetapi/badge/?version=master)](https://python-exbetapi.readthedocs.io/en/master/?badge=master)


## Installation

    pip3 install exbetapi

## Usage

After installation, you can either use exbetapi as a library or use the
command-line interface tool (CLI) that comes with it.

### CLI tool

Show the CLI help:

    $ eb --help
    $ eb <command> --help

To show user details, use:

    $ eb account
    User: <username>
    Password: <password>

To list your bets

    $ eb list-bets

To place a new bet

    $ eb placebet SELECTION_ID [back|lay] BACKER_MULTIPLIER BACKER_STAKE
    # for instance
    $ eb placebet 1.25.38235 back 2.5 0.00001

### Library

To use the library, you first need to instanciate `ExbetAPI` and login:

```python
from exbetapi import ExbetAPI
api = ExbetAPI()
api.login(user, password)
```

After that you can get your account details with:

```python
print(api.account)
```

List available sports, groups, markets and selections:

```python
print(api.list_sports())
print(api.lookup_eventgroups(
    sport_id
))
print(api.list_events(
    eventgroup_id
))
print(api.list_markets(
    event_id
))
print(api.list_selections(
    market_id
))
```

List your bets with:

```python
print(api.list_bets())
```

... or place a new bet using:

```python
api.place_bet(
    selection_id,
    back_or_lay,
    backer_multiplier,
    "{} BTC".format(backer_stake),
    bool(persistent),
)
```

Full Documentation is available [here](https://python-exbetapi.readthedocs.io/en/master/exbetapi.api.html). The underlying server-side
APIs can be found [here](https://api.macau.exbet.io/apidocs/).

## Development use

Clone the repository and create and activate a python virtual enviroment (assumes virtualenv is installed)

    git clone https://github.com/exbet/python-exbetapi.git
    cd python-exbetapi
    virtualenv env --python python3
    source env/bin/activate

Install Poetry and Exbet API dependencies

    pip3 install poetry
    poetry install

Run tests

    poetry run pytest

## Documentation

Documentation is available [here](https://python-exbetapi.rtfd.io)!
