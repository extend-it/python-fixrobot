"""
### fixrobot conftest.py for pytest test fixtures
"""
__author__ = "Anand P. Subramanian (quickfixrobot@gmail.com)"
__date__ = "23 July 2016 - Till Date"
__copyright__ = "fixrobot  Copyright (C) 2023  Anand P. Subramanian."
__license__ = "1.1"
__version__ = "License: GGPLv3+ GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>."
__credits__ = "Anand P. Subramanian"
__URL__ = "https://github.com/quickfixrobot/FIXRobot/"

# Modified 26 September 2026 by Vladimir Filipescu (co-authored with Claude Opus 5.5).
# Fork: https://github.com/extend-it/python-fixrobot
# Changes:
#   - fixed time.sleep() calls replaced by bounded polling on session state (see fix_waits.py)
#   - FIX42 and FIX50 fixtures share one setup/teardown generator
#   - sessions are always stopped, even if logon fails (no port left bound for the next test)

import os
import sys

import pytest

sys.path.append(os.path.join(os.path.dirname(
    os.path.realpath(__file__)), os.pardir))
from fixrobot.fixrobot.fixrobot import *  # provides the fixrobot class

from .fix_waits import wait_logged_on, wait_logged_off

# Repo root: env/ and spec/ are resolved relative to it
FIXROBOTPATH = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _exchange_and_client(exch_conn_name, client_conn_name):
    """Start acceptor (exchange) + initiator (client), wait for logon, yield, then shut down."""
    os.environ["FIXROBOTPATH"] = FIXROBOTPATH
    exch = fixrobot()
    client = fixrobot()

    exch.startAcceptor(exch_conn_name)      # listening socket is bound when start() returns
    try:
        client.startInitiator(client_conn_name)
        try:
            wait_logged_on(client)
            wait_logged_on(exch)
            yield exch, client
        finally:
            client.stopInitiator()          # sends Logout and waits for the reply
        wait_logged_off(client)
    finally:
        exch.stopAcceptor()


@pytest.fixture(scope="class")
def setUpFIX50ClientAndExchange():
    yield from _exchange_and_client("EXCHANGEFIX50", "CLIENTFIX50")


@pytest.fixture(scope="class")
def setUpFIX42ClientAndExchange():
    yield from _exchange_and_client("EXCHANGEFIX42", "CLIENTFIX42")
    
@pytest.fixture
def fix42_session():
    yield from _exchange_and_client("EXCHANGEFIX42", "CLIENTFIX42")
    
@pytest.fixture
def fix50_session():
    yield from _exchange_and_client("EXCHANGEFIX50", "CLIENTFIX50")
