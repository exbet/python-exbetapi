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
def lookup_markets(event_id):
    """ List markets within an event
    """
    dump(api.lookup_markets(event_id))


@main.command()
@click.argument("market_id", default="1.24.0")
def lookup_market(market_id):
    """ Get market
    """
    dump(api.lookup_market(market_id))


@main.command()
@click.argument("market_id", default="1.24.0")
def lookup_selections(market_id):
    """ List all selections from a market
    """
    dump(api.lookup_selections(market_id))


@main.command()
@click.argument("selection_id", default="1.25.0")
def lookup_selection(selection_id):
    """ Get selection by id
    """
    dump(api.lookup_selection(selection_id))


@main.command()
@click.argument("selection_id", default="1.25.0")
def orderbook(selection_id):
    """ Show order book of a selection
    """
    dump(api.orderbook(selection_id))


@main.command()
@click.argument("selection_id")
@click.argument("back_or_lay", type=click.Choice(["back", "lay"]))
@click.argument("backer_multiplier", type=float)
@click.argument("backer_stake", type=float)
@click.option("--persistent", type=bool)
def placebet(
    selection_id, back_or_lay, backer_multiplier, backer_stake, persistent
):
    """ Place a single bet
    """
    dump(
        api.place_bet(
            selection_id,
            back_or_lay,
            backer_multiplier,
            "{} BTC".format(backer_stake),
            bool(persistent),
        )
    )


@main.command()
@click.argument("selection_id")
@click.argument("back_or_lay", type=click.Choice(["back", "lay"]))
@click.argument("total_backer_stake", type=float)
@click.argument("mulipliers", type=float, nargs=-1)
@click.option("--persistent", type=bool)
def placebets(
    persistent, selection_id, back_or_lay, total_backer_stake, mulipliers
):
    """ Place multiple bets at different odds for a total stake
    """
    bets = list()
    for m in mulipliers:
        bets.append(
            (
                selection_id,
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
@click.argument("market")
@click.argument("selection")
def find_market(sport, eventgroup, hometeam, awayteam, market, selection):
    """ Find a selection
    """
    api.find_selection(
        sport,
        eventgroup,
        dict(home=hometeam, away=awayteam),
        market,
        selection,
    )


if __name__ == "__main__":
    main()
