# -*- coding: utf-8 -*-
""" API module for Exbet Market Making API
"""
import time
import requests
from .exceptions import (
    JsonDecodingFailedException,
    AlreadyLoggedinException,
    ExecutionError,
    APIError,
)


class ExbetAPI:
    """ API Class for Market Making
    """

    BASEURL = "https://mm.api.everett.exbet.io/v2/"
    ACCESS_TOKEN = None

    _SLEEPTIME = 0.2
    _BLOCKTIME = 1

    def _headers(self):
        """ Provides header for POST and GET requests
        """
        headers = dict()
        if self.ACCESS_TOKEN:
            headers["Authorization"] = "Bearer {}".format(self.ACCESS_TOKEN)
        return headers

    def _post(self, endpoint: str, payload: dict) -> dict:
        """ Private method to send a POST request with payload to the API
        """
        assert isinstance(payload, dict)
        resp = requests.post(
            self.BASEURL + endpoint, json=payload, headers=self._headers()
        )
        resp.raise_for_status()
        try:
            ret = resp.json()
        except Exception:  # pragma: no cover
            raise JsonDecodingFailedException("Decoding API response failed!")
        ret = self._parse_response(ret)
        return ret

    def _get(self, endpoint: str) -> dict:
        """ Private method to send a GET from API resource
        """
        resp = requests.get(self.BASEURL + endpoint, headers=self._headers())
        resp.raise_for_status()
        try:
            ret = resp.json()
        except Exception:  # pragma: no cover
            raise JsonDecodingFailedException("Decoding API response failed!")
        ret = self._parse_response(ret)
        return ret

    @staticmethod
    def _parse_response(ret):
        """ We parse the response for exceptions/errors that the API returns
        """
        if "error" in ret:  # pragma: no cover
            raise APIError([x["message"] for x in ret["errors"]])
        return ret

    @staticmethod
    def _require_dict_keys(resp: dict, attributes: list) -> None:
        """ Internal test for required dict keys
        """
        assert all([x in resp for x in attributes])

    def _get_task(self, task_id: str) -> dict:
        """ Obtain a task from the API
        """
        return self._post("task", dict(task_id=task_id))

    def _wait_for_task(self, task_id: str) -> dict:  # pragma: no cover
        """ Wait for a task to complete
        """
        cnt = 0
        while True:
            task = self._get_task(task_id)
            if (
                task.get("ready")
                and task.get("state") == "SUCCESS"
                and task.get("info")
            ):
                task["info"] = eval(task.get("info", "{}"))
                return task
            time.sleep(self._SLEEPTIME)
            cnt += 1
            if cnt > 3 * self._BLOCKTIME / self._SLEEPTIME:
                raise ExecutionError("Inform admins")

    @staticmethod
    def _obtain_task_results(task):  # pragma: no cover
        """ A task contains information about the operations performed. Extract
            those
        """
        results = task["info"].get("operation_results")
        if results:
            return [x[1] for x in results]
        return []

    @staticmethod
    def _parse_stake(stake):
        """ Stake cane be provided as string and dictionary. Unified here.
        """
        if isinstance(stake, str) and " " in stake:
            amount, symbol = stake.split(" ")
            return dict(amount=float(amount), symbol=symbol)
        if isinstance(stake, dict) and "amount" in stake and "symbol" in stake:
            return dict(amount=float(stake["amount"]), symbol=stake["symbol"])
        raise ValueError("Invalid stake format")  # pragma: no cover

    #
    # Public methods
    #
    def reset(self):
        """ Reset instance
        """
        self.ACCESS_TOKEN = None

    def login(self, username: str, password: str) -> None:
        """ Obtain and store session for user
        """
        if self.ACCESS_TOKEN is not None:
            raise AlreadyLoggedinException("Reset instance with .reset()")
        resp = self._post("login", dict(username=username, password=password))
        self._require_dict_keys(resp, ["access_token", "refresh_token", "username"])
        self.ACCESS_TOKEN = resp["access_token"]

    #
    # General information
    #
    def is_loggedin(self) -> bool:
        """ Am i logged in?
        """
        return bool(self.ACCESS_TOKEN)

    @property
    def info(self) -> dict:
        """ Obtain general information from the API
        """
        return self._get("info")

    @property
    def session(self) -> dict:
        """ Obtain session information
        """
        return self._get("session")

    #
    # Account information
    #
    @property
    def account(self) -> dict:
        """ Obtain account details
        """
        return self._get("account")

    @property
    def balance(self) -> dict:
        """ Obtain account balance from api
        """
        balances = self._get("balance").get("balances")
        ret = dict()
        for b in balances:
            ret[b["symbol"]] = b["amount"]
        return ret

    @property
    def roles(self) -> list:
        """ Provide roles of the account
        """
        return self.account.get("roles")

    #
    # Bets
    #
    def get_bet(self, bet_id: str) -> dict:
        """ Obtain details of a placed bet

        :param str bet_id: Bet of the form ``1.26.xxxxxxx``
        """
        return self._post("bet/get", dict(bet_id=bet_id))

    def list_bets(self) -> dict:
        """ List account's bets, sorted for matched and unmatched
        """
        return self._get("bet/list")

    def cancel_bet(self, bet_id: str, wait=False) -> None:
        """
        :param str bet_id: Bet of the form ``1.26.xxxxxxx``
        :param bool wait: Wait/Block until action has been confirmed
        """
        resp = self._post("bet/cancel", dict(bet_id=bet_id))
        if wait:  # pragma: no cover
            self._wait_for_task(resp.get("task_id"))
            return
        return

    def cancel_bets(self, bet_ids: list, wait=False) -> None:
        """
        :param list bet_ids: List of bets of the form ``1.26.xxxxxxx``
        :param bool wait: Wait/Block until action has been confirmed
        """
        resp = self._post(
            "bet/cancel_many",
            dict(bets_to_cancel=[dict(bet_id=bet_id) for bet_id in bet_ids]),
        )
        if wait:  # pragma: no cover
            self._wait_for_task(resp.get("task_id"))
            return
        return

    def edit_bet(self, *args, **kwargs):
        """ Not yet implemented!
        """
        raise NotImplementedError

    def edit_bets(self, *args, **kwargs):
        """ Not yet implemented!
        """
        raise NotImplementedError

    def place_bet(
        self,
        betting_market_id: str,
        back_or_lay: str,
        backer_multiplier: float,
        stake: dict,
        persistent=True,
        wait=False,
    ) -> dict:
        """ Place a bet

        :param str betting_market_id: The betting market id to place the bet in (1.25.xxxx)
        :param option back_or_lay: Either 'back' or 'lay' the bet
        :param float backer_multiplier: Odds
        :param str stake: Stake as ``amount symbol``
        :param bool persistent: Make the bet persistent over status change from
            upcoming to in_progress
        :param bool wait: Wait for confirmation of the database (if `true`
            returns `bet_id`, else returns `None`).

        Example:::

            bet_id = api.place_bet("1.25.50449", "lay", 1.65, "0.01 BTC", wait=True)

        """
        stake = self._parse_stake(stake)
        resp = self._post(
            "bet/place",
            dict(
                back_or_lay=back_or_lay,
                betting_market_id=betting_market_id,
                backer_multiplier=backer_multiplier,
                persistent=persistent,
                stake=stake,
            ),
        )
        if wait:  # pragma: no cover
            return self._obtain_task_results(self._wait_for_task(resp.get("task_id")))[
                0
            ]
        return None

    def place_bets(self, bets: list, wait=False) -> list:
        """ place multiple bets


        :param list bets: This is a list in the form of `place_bet` arguments.
        :param bool wait: Wait for confirmation of the database (if `true`
                returns `bet_id`, else returns `None`).

        Example:::

            api.place_bets(
                [
                    ("1.25.50449", "lay", 1.65, "0.01 BTC"),
                    ("1.25.50449", "back", 1.75, "0.01 BTC"),
                ],
                wait=True,
            )

        """
        parsed_bets = list()
        for bet in bets:
            b = dict(
                betting_market_id=bet[0],
                back_or_lay=bet[1],
                backer_multiplier=bet[2],
                stake=self._parse_stake(bet[3]),
                persistent=True,
            )
            if len(bet) > 4:
                b["persistent"] = bet[4]
            parsed_bets.append(b)
        resp = self._post("bet/place_many", dict(place_bets=parsed_bets))
        if wait:  # pragma: no cover
            return self._obtain_task_results(self._wait_for_task(resp.get("task_id")))
        return None

    #
    # Find
    #
    def find_betting_market(
        self, sport: str, event_group: str, teams: dict, group: str, market: str
    ):
        """ Find a betting market id provided sufficient information

        :param str sport: Sports name (e.g. Basketball)
        :param str event_group: Name of the event group (e.g. NBA)
        :param dict teams: dictionary in the form of ``{"home": "xx", "away": "yy"}``
        :param str group: Betting Market Group name (e.g. Moneyline)
        :param str market: The individual market name (e.g. "xx" for Team xx)

        """
        return self._post(
            "find/bettingmarket",
            dict(
                sport=sport,
                event_group=event_group,
                teams=teams,
                group=group,
                market=market,
            ),
        )

    #
    # Lookup
    #
    def lookup_bettingmarket(self, bettingmarket_id: str) -> dict:
        """ Provides information about a betting market

        :param str bettingmarket_id: The betting market id (1.25.xxx)
        """
        return self._post(
            "lookup/bettingmarket", dict(bettingmarket_id=bettingmarket_id)
        )

    def lookup_bettingmarkets(self, bettingmarketgroup_id: str) -> dict:
        """
        Provides a list of betting markets in a betting market group

        :param str bettingmarketgroup_id: Betting Market Group id (1.24.xxxx)
        """
        return self._post(
            "lookup/bettingmarkets", dict(bettingmarketgroup_id=bettingmarketgroup_id),
        ).get("bettingmarkets")

    def lookup_bettingmarketgroup(self, bettingmarketgroup_id: str) -> dict:
        """ Provides information about a betting market group

        :param str bettingmarketgroup_id: Betting Market Group id (1.24.xxxx)
        """
        return self._post(
            "lookup/bettingmarketgroup",
            dict(bettingmarketgroup_id=bettingmarketgroup_id),
        )

    def lookup_bettingmarketgroups(self, event_id: str) -> list:
        """
        List betting market groups of an event

        :param str event_id: Event id (1.22.xxx)
        """
        return self._post("lookup/bettingmarketgroups", dict(event_id=event_id)).get(
            "bettingmarketgroups"
        )

    def lookup_event(self, event_id: str) -> dict:
        """ Provide information about an event

        :param str event_id: Event id (1.22.xxx)

        """
        return self._post("lookup/event", dict(event_id=event_id))

    def lookup_events(self, eventgroup_id: str) -> list:
        """ List events within an event group

        :param str eventgroup_id: Event Group id (1.21.xxx)
        """
        return self._post("lookup/events", dict(eventgroup_id=eventgroup_id)).get(
            "events"
        )

    def lookup_eventgroups(self, sport_id: str) -> list:
        """ List event groups with a sport

        :param str sport_id: Sport id (1.20.xxx)
        """
        return self._post("lookup/eventgroups", dict(sport_id=sport_id)).get(
            "eventgroups"
        )

    def lookup_sports(self) -> list:
        """ List all sports
        """
        return self._post("lookup/sports", dict()).get("sports")

    #
    # Orderbook
    #
    def orderbook(self, bettingmarket_id: str) -> dict:
        """ Provide (consolidated) order book of a betting market

        :param str bettingmarket_id: The betting market id (1.25.xxx)
        """
        return self._post("lookup/orderbook", dict(bettingmarket_id=bettingmarket_id))
