# -*- coding: utf-8 -*-
import unittest
import pytest
import requests
from exbetapi import ExbetAPI
from exbetapi.api import ExbetAPIAuth
from exbetapi.exceptions import AlreadyLoggedinException
from functools import wraps


def API_POST(d):
    return unittest.mock.patch("exbetapi.ExbetAPI._post", return_value=d)


def API_GET(d):
    return unittest.mock.patch("exbetapi.ExbetAPI._get", return_value=d)


def API_PROPERTY(prop, d):
    return unittest.mock.patch(
        "exbetapi.ExbetAPI." + prop,
        new_callable=unittest.mock.PropertyMock,
        return_value=d,
    )


@pytest.fixture(scope="session")
@API_POST(dict(access_token="a", refresh_token="b", username="u"))
def api(mockery):
    """This api instance will be logged in (fake)"""
    a = ExbetAPI()
    a.login("", "")
    mockery.assert_called_once_with("login", dict(username="", password=""))
    return a


def test_init():
    """Ensure we can instantiate the API"""
    ExbetAPI()


def test_request_contains_version(api):
    from exbetapi import __version__

    assert isinstance(api._requests, requests.Session)
    assert api._requests.headers.get("User-Agent") == "python/exbetapi-" + __version__


def test_request_contains_auth(api):
    assert isinstance(api._requests.auth, ExbetAPIAuth)
    r = requests.Request()
    api._requests.auth(r)
    assert r.headers.get("Authorization") == "Bearer a"


def test_login(api):
    """Test that we are logged in"""
    assert api.is_loggedin()


def test_parse_stake(api):
    assert api._parse_stake("1 BTC") == dict(amount=1, symbol="BTC")
    assert api._parse_stake(dict(amount=1, symbol="BTC")) == dict(
        amount=1, symbol="BTC"
    )


def test_relogin(api):
    with pytest.raises(AlreadyLoggedinException):
        api.login("", "")


def test_reset(api):
    assert api.is_loggedin()
    api.reset()
    assert not api.is_loggedin()


@API_GET(dict(foo="bar"))
def test_account(mock, api):
    assert api.account == dict(foo="bar")
    mock.assert_called_once_with("account")


@API_GET(dict(foo="bar"))
def test_info(mock, api):
    assert api.info == dict(foo="bar")
    mock.assert_called_once_with("info")


@API_GET(dict(balances=[dict(amount=10, symbol="BTC")]))
def test_balance(mock, api):
    assert api.balance == dict(BTC=10)
    mock.assert_called_once_with("balance")


@API_GET(dict(foo="bar"))
def test_session(mock, api):
    assert api.session == dict(foo="bar")
    mock.assert_called_once_with("session")


@API_GET(dict(roles=["foobar"]))
def test_roles(mock, api):
    assert api.roles == ["foobar"]
    mock.assert_called_once_with("account")


@API_GET(dict(matched=[], unmatched=[]))
def test_list_bets(mock, api):
    assert api.list_bets() == dict(matched=[], unmatched=[])
    mock.assert_called_once_with("bet/list")

@API_GET(dict(recognized_ids=[]))
def find_recognized_selection(mock, api):
    assert api.find_recognized_selection() == dict(recognized_ids=[])
    mock.assert_called_once_with("find/selections/recognized")

@API_POST(dict(matched=[]))
def test_list_matched(mock, api):
    assert api.list_matched() == dict(matched=[])
    mock.assert_called_once_with("bet/list_matched")

@API_POST(dict(unmatched=[]))
def test_list_unmatched(mock, api):
    assert api.list_unmatched() == dict(unmatched=[])
    mock.assert_called_once_with("bet/list_unmatched")

@API_POST(dict())
def test_many_actions(mock, api):
    many_actions = {
        "cancel": [
            {
            "bet_id": "string"
            }
        ],
        "edit": [
            {
            "bet_id": "1.26.8911",
            "current_backer_multiplier": 1.02,
            "current_backer_stake_amount": 1,
            "current_persistent": True,
            "new_backer_multiplier": 1.03,
            "new_backer_stake_amount": 1.01,
            "new_persistent": True
            }
        ],
        "place": [
            {
            "back_or_lay": "back",
            "backer_multiplier": 1.02,
            "backer_stake": {
                "amount": 0,
                "symbol": "string"
            },
            "expiration_time": "2022-05-17T07:33:14Z",
            "persistent": True,
            "selection_id": "1.25.8911"
            }
        ]
    }
    api.many_actions(many_actions)
    mock.assert_called_once_with("bet/many_actions", many_actions)

@API_POST(dict())
def test_edit_bet(mock, api):
    new_bet = {
        "bet_id": "1.26.8911",
        "current_backer_multiplier": 1.02,
        "current_backer_stake_amount": 1,
        "current_persistent": True,
        "new_backer_multiplier": 1.03,
        "new_backer_stake_amount": 1.01,
        "new_persistent": True
    }
    api.edit_bet(new_bet)
    mock.assert_called_once_with("bet/edit", new_bet)

@API_POST(dict())
def test_edit_bets(mock, api):
    new_bets = {
        "edit_bets": [
            {
                "bet_id": "1.26.8911",
                "current_backer_multiplier": 1.02,
                "current_backer_stake_amount": 1,
                "current_persistent": True,
                "new_backer_multiplier": 1.03,
                "new_backer_stake_amount": 1.01,
                "new_persistent": True
            }
        ]
    }
    api.edit_bets(new_bets)
    mock.assert_called_once_with("bet/edit_many", new_bets)

@API_POST(dict())
def test_modify_unmatched(mock, api):
    bets_to_modify = {
        "bets": [
            {
            "backs": [
                {
                    "backer_multiplier": 1.02,
                    "backer_stake": {
                        "amount": 0,
                        "symbol": "string"
                    }
                }
            ],
            "lays": [
                {
                    "backer_multiplier": 1.02,
                    "backer_stake": {
                        "amount": 0,
                        "symbol": "string"
                    }
                }
            ]
            }
        ],
        "expiration_time": "2021-02-05T09:58:53Z",
        "market_id": "1.24.8911",
        "persistent": True,
        "require_bmg_status": "string"
    }
    api.modify_unmatched(bets_to_modify)
    mock.assert_called_once_with("bet/modify_unmatched", bets_to_modify)

@API_POST(dict())
def test_modify_unmatched(mock, api):
    many_bets_to_modify = {
        "markets": [
            {
            "bets": [
                {
                "backs": [
                    {
                    "backer_multiplier": 1.02,
                    "backer_stake": {
                        "amount": 0,
                        "symbol": "string"
                    }
                    }
                ],
                "lays": [
                    {
                    "backer_multiplier": 1.02,
                    "backer_stake": {
                        "amount": 0,
                        "symbol": "string"
                    }
                    }
                ]
                }
            ],
            "expiration_time": "2021-02-05T09:58:53Z",
            "market_id": "1.24.8911",
            "persistent": True,
            "require_bmg_status": "string"
            }
        ]
    }
    api.modify_unmatched_many(many_bets_to_modify)
    mock.assert_called_once_with("bet/modify_unmatched_many", many_bets_to_modify)

@API_POST(dict(sports=["foobar"]))
def test_lookup_sports(mock, api):
    assert api.lookup_sports() == ["foobar"]
    mock.assert_called_once_with("lookup/sports", dict())


@API_POST(dict(eventgroups=["foobar"]))
def test_lookup_eventgroups(mock, api):
    _id = "1.20.0"
    assert api.lookup_eventgroups(_id) == ["foobar"]
    mock.assert_called_once_with("lookup/eventgroups", dict(sport_id=_id))


@API_POST(dict(events=["foobar"]))
def test_lookup_events(mock, api):
    _id = "1.21.0"
    assert api.lookup_events(_id) == ["foobar"]
    mock.assert_called_once_with("lookup/events", dict(eventgroup_id=_id))


@API_POST(dict(foo="bar"))
def test_lookup_event(mock, api):
    _id = "1.22.0"
    assert api.lookup_event(_id) == dict(foo="bar")
    mock.assert_called_once_with("lookup/event", dict(event_id=_id))


@API_POST(dict(markets=["foobar"]))
def test_lookup_markets(mock, api):
    _id = "1.22.0"
    assert api.lookup_markets(_id) == ["foobar"]
    mock.assert_called_once_with("lookup/markets", dict(event_id=_id))


@API_POST(dict(foo="bar"))
def test_lookup_market(mock, api):
    _id = "1.24.0"
    assert api.lookup_market(_id) == dict(foo="bar")
    mock.assert_called_once_with("lookup/market", dict(market_id=_id))


@API_POST(dict(selections=["foobar"]))
def test_lookup_selections(mock, api):
    _id = "1.24.0"
    assert api.lookup_selections(_id) == ["foobar"]
    mock.assert_called_once_with("lookup/selections", dict(market_id=_id))


@API_POST(dict(foo="bar"))
def test_lookup_selection(mock, api):
    _id = "1.25.0"
    assert api.lookup_selection(_id) == dict(foo="bar")
    mock.assert_called_once_with("lookup/selection", dict(selection_id=_id))

@API_POST(dict(events=[]))
def test_lookup_upcoming_events(mock, api):
    event_parameters = {
        "add_details": True,
        "add_markets": False,
        "add_prices": False,
        "limit": 100,
        "offset": 0,
        "sport_id": ""
    }
    assert api.lookup_upcoming_events(event_parameters) == dict(events=[])
    mock.assert_called_once_with("lookup/events_upcoming", event_parameters)


@API_POST(dict(aggregated_back_bets=[], aggregated_lay_bets=[]))
def test_orderbook(mock, api):
    _id = "1.25.0"
    assert api.orderbook(_id) == dict(aggregated_back_bets=[], aggregated_lay_bets=[])
    mock.assert_called_once_with("lookup/orderbook", dict(selection_id=_id))


@API_POST(dict(markets=[dict(market_id="", selections=[dict(aggregated_back_bets=[], aggregated_lay_bets=[])])]))
def test_orderbooks(mock, api):
    market_ids = {"market_ids": ["1.24.0"]}
    expected_response = {
        "markets": [
            {
                "market_id": "",
                "selections": [
                    {
                        "aggregated_back_bets": [],
                        "aggregated_lay_bets": []
                    }
                ]
            },
        ]
    }
    assert api.orderbooks(market_ids) == expected_response
    mock.assert_called_once_with("lookup/orderbook_many", market_ids)


@API_POST(dict())
def test_placebet(mock, api):
    api.place_bet("1.25.50449", "lay", 1.65, "0.01 BTC")
    mock.assert_called_once_with(
        "bet/place",
        dict(
            back_or_lay="lay",
            selection_id="1.25.50449",
            backer_multiplier=1.65,
            persistent=True,
            backer_stake=dict(amount=0.01, symbol="BTC"),
        ),
    )


@API_POST(dict())
def test_placebets(mock, api):
    api.place_bets(
        [
            ("1.25.50449", "lay", 1.65, "0.01 BTC"),
            ("1.25.50449", "back", 1.75, "0.01 BTC"),
        ]
    )
    mock.assert_called_once_with(
        "bet/place_many",
        {
            "place_bets": [
                {
                    "selection_id": "1.25.50449",
                    "back_or_lay": "lay",
                    "backer_multiplier": 1.65,
                    "backer_stake": {"amount": 0.01, "symbol": "BTC"},
                    "persistent": True,
                },
                {
                    "selection_id": "1.25.50449",
                    "back_or_lay": "back",
                    "backer_multiplier": 1.75,
                    "backer_stake": {"amount": 0.01, "symbol": "BTC"},
                    "persistent": True,
                },
            ]
        },
    )


@API_POST(dict())
def test_placebet_nonpersistent(mock, api):
    api.place_bet("1.25.50449", "lay", 1.65, "0.01 BTC", False)
    mock.assert_called_once_with(
        "bet/place",
        dict(
            back_or_lay="lay",
            selection_id="1.25.50449",
            backer_multiplier=1.65,
            persistent=False,
            backer_stake=dict(amount=0.01, symbol="BTC"),
        ),
    )


@API_POST(dict())
def test_placebets_nonpersistent(mock, api):
    api.place_bets(
        [
            ("1.25.50449", "lay", 1.65, "0.01 BTC", False),
            ("1.25.50449", "back", 1.75, "0.01 BTC", False),
        ]
    )
    mock.assert_called_once_with(
        "bet/place_many",
        {
            "place_bets": [
                {
                    "selection_id": "1.25.50449",
                    "back_or_lay": "lay",
                    "backer_multiplier": 1.65,
                    "backer_stake": {"amount": 0.01, "symbol": "BTC"},
                    "persistent": False,
                },
                {
                    "selection_id": "1.25.50449",
                    "back_or_lay": "back",
                    "backer_multiplier": 1.75,
                    "backer_stake": {"amount": 0.01, "symbol": "BTC"},
                    "persistent": False,
                },
            ]
        },
    )


@API_POST(dict())
def test_cancelbet(mock, api):
    api.cancel_bet("1.26.171197")
    mock.assert_called_once_with("bet/cancel", {"bet_id": "1.26.171197"})


@API_POST(dict())
def test_cancelbets(mock, api):
    api.cancel_bets(["1.26.171196", "1.26.171195"])
    mock.assert_called_once_with(
        "bet/cancel_many",
        {"bets_to_cancel": [{"bet_id": "1.26.171196"}, {"bet_id": "1.26.171195"}]},
    )


@API_POST(dict())
def test_get_task(mock, api):
    api._get_task("asfasf")
    mock.assert_called_once_with("task", {"task_id": "asfasf"})


@API_POST(dict())
def test_find_selection(mock, api):
    api.find_selection("Sport", "Eventgroup", ["team1", "team2"], "market", "selection")
    mock.assert_called_once_with(
        "find/selections",
        {
            "sport": "Sport",
            "event_group": "Eventgroup",
            "teams": ["team1", "team2"],
            "market": "market",
            "selection": "selection",
        },
    )


if __name__ == "__main__":
    unittest.main()
