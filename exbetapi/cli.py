#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" CLI Tools for exbetapi
"""

# -*- coding: utf-8 -*-

import json
import click
from exbetapi import ExbetAPI

api = ExbetAPI()


def dump(x):
    """ Dump json content
    """
    click.echo(json.dumps(x, indent=4))


@click.group()
@click.option("--user", prompt="User", required=True)
@click.option("--password", prompt="Password", hide_input=True)
def main(user, password):
    """ CLI tools for exbetapi
    """
    api.login(user, password)


@main.command()
def account():
    """ Show account details
    """
    dump(api.account)


@main.command()
def info():
    """ Show API infos
    """
    dump(api.info)


@main.command()
def balance():
    """ Show account balance
    """
    dump(api.balance)


@main.command()
def session():
    """ Show API session info
    """
    dump(api.session)


@main.command()
def roles():
    """ Show account roles
    """
    dump(api.roles)


@main.command()
def list_bets():
    """ List account's bets
    """
    dump(api.list_bets())


@main.command()
def lookup_sports():
    """ List Sports
    """
    dump(api.lookup_sports())


@main.command()
@click.argument("sport_id", default="1.20.0")
def lookup_eventgroups(sport_id):
    """ List event groups in a sport
    """
    dump(api.lookup_eventgroups(sport_id))


@main.command()
@click.argument("eventgroup_id", default="1.21.0")
def lookup_events(eventgroup_id):
    """ List events in an eventgroup
    """
    dump(api.lookup_events(eventgroup_id))


@main.command()
@click.argument("event_id", default="1.22.0")
def lookup_event(event_id):
    """ Get an event
    """
    dump(api.lookup_event(event_id))


@main.command()
@click.argument("event_id", default="1.22.0")
def lookup_bettingmarketgroups(event_id):
    """ List bettingmarketgroups within an event
    """
    dump(api.lookup_bettingmarketgroups(event_id))


@main.command()
@click.argument("bettingmarketgroup_id", default="1.24.0")
def lookup_bettingmarketgroup(bettingmarketgroup_id):
    """ Get bettingmarketgroup
    """
    dump(api.lookup_bettingmarketgroup(bettingmarketgroup_id))


@main.command()
@click.argument("bettingmarketgroup_id", default="1.24.0")
def lookup_bettingmarkets(bettingmarketgroup_id):
    """ List bettingmarkets from bettingmarketgroup id
    """
    dump(api.lookup_bettingmarkets(bettingmarketgroup_id))


@main.command()
@click.argument("bettingmarket_id", default="1.25.0")
def lookup_bettingmarket(bettingmarket_id):
    """ Get bettingmarket
    """
    dump(api.lookup_bettingmarket(bettingmarket_id))


@main.command()
@click.argument("bettingmarket_id", default="1.25.0")
def orderbook(bettingmarket_id):
    """ Show order book of a bettingmarket
    """
    dump(api.orderbook(bettingmarket_id))


@main.command()
@click.argument("bettingmarket_id")
@click.argument("back_or_lay", type=click.Choice(["back", "lay"]))
@click.argument("backer_multiplier", type=float)
@click.argument("backer_stake", type=float)
@click.option("--persistent", type=bool)
def placebet(
    bettingmarket_id, back_or_lay, backer_multiplier, backer_stake, persistent
):
    """ Place a single bet
    """
    dump(
        api.place_bet(
            bettingmarket_id,
            back_or_lay,
            backer_multiplier,
            "{} BTC".format(backer_stake),
            bool(persistent),
        )
    )


@main.command()
@click.argument("bettingmarket_id")
@click.argument("back_or_lay", type=click.Choice(["back", "lay"]))
@click.argument("total_backer_stake", type=float)
@click.argument("mulipliers", type=float, nargs=-1)
@click.option("--persistent", type=bool)
def placebets(
    persistent, bettingmarket_id, back_or_lay, total_backer_stake, mulipliers
):
    """ Place multiple bets at different odds for a total stake
    """
    bets = list()
    for m in mulipliers:
        bets.append(
            (
                bettingmarket_id,
                back_or_lay,
                m,
                "{} BTC".format(total_backer_stake / len(mulipliers)),
                bool(persistent),
            )
        )
    dump(api.place_bets(bets))


@main.command()
@click.argument("bet_id")
def cancelbet(bet_id):
    """ Cancel a single bet
    """
    dump(api.cancel_bet(bet_id))


@main.command()
@click.argument("bet_ids", nargs=-1)
def cancelbets(bet_ids):
    """ Cancel many bets
    """
    dump(api.cancel_bets(bet_ids))


@main.command()
@click.argument("task_id")
def get_task(task_id):
    """ Get the content of a task id
    """
    dump(api._get_task(task_id))


@main.command()
@click.argument("sport")
@click.argument("eventgroup")
@click.argument("hometeam")
@click.argument("awayteam")
@click.argument("bettingmarketgroup")
@click.argument("market")
def find_market(sport, eventgroup, hometeam, awayteam, bettingmarketgroup, market):
    """ Find a market
    """
    api.find_betting_market(
        sport,
        eventgroup,
        dict(home=hometeam, away=awayteam),
        bettingmarketgroup,
        market,
    )


if __name__ == "__main__":
    main()
