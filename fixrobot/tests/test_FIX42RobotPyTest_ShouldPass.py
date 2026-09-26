"""
### fixrobot FIX42 pytest positive testcases
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
#   - tests moved out of Test_Class; each test gets its own sessions via the fix42_session fixture
#   - fixed time.sleep() calls replaced by bounded polling (see fix_waits.py)
#   - duplicate test_NewOrderSingleFilled_AsNames_ShouldPass removed

import sys
import os
import time
from contextlib import contextmanager
import quickfix as fix

import pytest

sys.path.append(os.path.join(os.path.dirname(
    os.path.realpath(__file__)), os.pardir))
from fixrobot.fixrobot.fixrobot import *

from .conftest import _exchange_and_client
from .fix_waits import send_and_expect, last_incoming_seq, expect_message, wait_until

#Positive testcase for NewOrderSingle and Fill where fix message arguments are passed as strings.
#Runs on its own exchange/client sessions, so it lives outside Test_Class: the class-scoped
#setUpFIX42ClientAndExchange fixture holds the same FIX42 ports for as long as the class runs.
@pytest.mark.fix42positiveimproved
def test_NewOrderSingleFilled_AsStrings_ShouldPass(fix42_session):
    exch, client = fix42_session
    # clearMessageStore() only empties local deques, so it is done when it returns
    assert exch.clearMessageStore() == True
    assert client.clearMessageStore() == True

    # send_and_expect() waits until the receiver has the new message, then validates it
    sent, received = send_and_expect(client, exch,
        "NewOrderSingle", "|35=D|$setField( ClOrdID )|21=1|55=MSFT|54=1|$setField( SendingTime )|$setField(TransactTime)|40=2|38=100|44=10.50|59=0|")
    assert sent.getHeader().getField(35) == "D"
    assert received.getHeader().getField(35) == "D"

    sent, received = send_and_expect(exch, client,
        "ExecutionReport", "|35=8|$setField( ClOrdID,  IN, ClOrdID )|$setField( OrderID )|$setField( ExecID )|20=0|150=0|39=0|55=MSFT|38=100|54=1|44=10.50|151=100|14=0|6=0.0|")
    assert sent.getHeader().getField(35) == "8"
    assert received.getHeader().getField(35) == "8"

    sent, received = send_and_expect(exch, client,
        "ExecutionReport", "|35=8|$setField( ClOrdID,  IN, ClOrdID )|$setField( OrderID )|$setField( ExecID )|20=0|150=2|39=2|55=MSFT|38=100|54=1|44=10.50|32=100|31=10.50|151=0|14=100|6=10.50|")
    assert sent.getHeader().getField(35) == "8"
    assert received.getHeader().getField(35) == "8"

#Positive testcase for NewOrderSingle and Filled where fix message arguments are passed as template names.
@pytest.mark.fix42positiveimproved
def test_NewOrderSingleFilled_AsNames_ShouldPass():
    with contextmanager(_exchange_and_client)("EXCHANGEFIX42", "CLIENTFIX42") as (exch, client):
        # clearMessageStore() only empties local deques, so it is done when it returns
        assert exch.clearMessageStore() == True
        assert client.clearMessageStore() == True

        # send_and_expect() waits until the receiver has the new message, then validates it
        sent, received = send_and_expect(client, exch, "NewOrderSinglePass")
        assert sent.getHeader().getField(35) == "D"
        assert received.getHeader().getField(35) == "D"

        sent, received = send_and_expect(exch, client, "ExecutionReportAckPass")
        assert sent.getHeader().getField(35) == "8"
        assert received.getHeader().getField(35) == "8"

        sent, received = send_and_expect(exch, client, "ExecutionReportFillPass")
        assert sent.getHeader().getField(35) == "8"
        assert received.getHeader().getField(35) == "8"

        # logDumpMessageStore() only writes to the log, so it is done when it returns
        assert exch.logDumpMessageStore() == True

#Positive testcase for NewOrderSingle and CancelRequest where fix message arguments are passed as template names.
@pytest.mark.fix42positiveimproved
def test_NewOrderSingleOrderCancelRequest_AsNames_ShouldPass(fix42_session):
    exch, client = fix42_session
    # clearMessageStore() only empties local deques, so it is done when it returns
    assert exch.clearMessageStore() == True
    assert client.clearMessageStore() == True

    # 1. Client sends NewOrderSinglePass to the exchange (checked as D on both sides)
    sent, received = send_and_expect(client, exch, "NewOrderSinglePass")
    assert sent.getHeader().getField(35) == "D"
    assert received.getHeader().getField(35) == "D"

    # 2. Exchange sends ExecutionReportAckPass to the client (8)
    sent, received = send_and_expect(exch, client, "ExecutionReportAckPass")
    assert sent.getHeader().getField(35) == "8"
    assert received.getHeader().getField(35) == "8"

    # 3. Client sends OrderCancelRequestPass to the exchange (F)
    sent, received = send_and_expect(client, exch, "OrderCancelRequestPass")
    assert sent.getHeader().getField(35) == "F"
    assert received.getHeader().getField(35) == "F"

    # 4. Exchange sends ExecutionReportCancelledPass to the client (8)
    sent, received = send_and_expect(exch, client, "ExecutionReportCancelledPass")
    assert sent.getHeader().getField(35) == "8"
    assert received.getHeader().getField(35) == "8"

#Positive testcase for NewOrderSingle and CancelReplaceRequest where fix message arguments are passed as template names.
@pytest.mark.fix42positiveimproved
def test_NewOrderSingleOrderCancelReplaceRequest_AsNames_ShouldPass(fix42_session):
    exch, client = fix42_session
    # clearMessageStore() only empties local deques, so it is done when it returns
    assert exch.clearMessageStore() == True
    assert client.clearMessageStore() == True
    
    # 1. Client sends NewOrderSinglePass to the exchange (checked as D on both sides)
    sent, received = send_and_expect(client, exch, "NewOrderSinglePass")
    assert sent.getHeader().getField(35) == "D"
    assert received.getHeader().getField(35) == "D"
    
    # 2. Exchange sends ExecutionReportAckPass to the client (8)
    sent, received = send_and_expect(exch, client, "ExecutionReportAckPass")
    assert sent.getHeader().getField(35) == "8"
    assert received.getHeader().getField(35) == "8"
    
    # 3. Client sends OrderCancelReplaceRequestPass to the exchange (G)
    sent, received = send_and_expect(client, exch, "OrderCancelReplaceRequestPass")
    assert sent.getHeader().getField(35) == "G"
    assert received.getHeader().getField(35) == "G"
    
    # 4. Exchange sends ExecutionReportReplacedPass to the client (8)
    sent, received = send_and_expect(exch, client, "ExecutionReportReplacedPass")
    assert sent.getHeader().getField(35) == "8"
    assert received.getHeader().getField(35) == "8"

#Positive testcase for TestRequest and Heartbeat where fix message arguments are passed as template names.
@pytest.mark.fix42positiveimproved
def test_TestRequestHeartBeat_AsNames_ShouldPass(fix42_session):
    exch, client = fix42_session
    # clearMessageStore() only empties local deques, so it is done when it returns
    assert exch.clearMessageStore() == True
    assert client.clearMessageStore() == True
    
    # TestRequest and Heartbeat are admin messages: wait on the admin deque, not the app one.
    # Take both marks before sending, because the exchange's engine answers with a Heartbeat by itself.
    exch_mark = last_incoming_seq(exch, "admin")
    client_mark = last_incoming_seq(client, "admin")
    
    # 1. Client sends TestRequestPass to the exchange (1)
    sent = client.sendMessage("TestRequestPass")
    assert sent.getHeader().getField(35) == "1"
    received = expect_message(exch, "TestRequestPass", after_seq=exch_mark, kind="admin")
    assert received.getHeader().getField(35) == "1"
    
    # 2. Exchange's engine replies automatically with a Heartbeat carrying the TestReqID (0)
    received = expect_message(client, "HeartbeatPass", after_seq=client_mark, kind="admin")
    assert received.getHeader().getField(35) == "0"
    
# Positive testcase for OrderList and Fill where fix message arguments are passed as template names.
@pytest.mark.fix42positiveimproved
def test_OrderListAckFill_AsNames_ShouldPass(fix42_session):
    exch, client = fix42_session
    # clearMessageStore() only empties local deques, so it is done when it returns
    assert exch.clearMessageStore() == True
    assert client.clearMessageStore() == True
    
    # 1. Client sends NewOrderListNewPass to the exchange (checked as E on both sides)
    sent, received = send_and_expect(client, exch, "NewOrderListNewPass")
    assert sent.getHeader().getField(35) == "E"
    assert received.getHeader().getField(35) == "E"
    
    # 2. Exchange sends ExecutionReportListFill1Pass to the client (8)
    sent, received = send_and_expect(exch, client, "ExecutionReportListFill1Pass")
    assert sent.getHeader().getField(35) == "8"
    assert received.getHeader().getField(35) == "8"
    
    # 3. Exchange sends ExecutionReportListFill2Pass to the client (8)
    sent, received = send_and_expect(exch, client, "ExecutionReportListFill2Pass")
    assert sent.getHeader().getField(35) == "8"
    assert received.getHeader().getField(35) == "8"
    
    # 4. Exchange sends ExecutionReportListFill3Pass to the client (8)
    sent, received = send_and_expect(exch, client, "ExecutionReportListFill3Pass")
    assert sent.getHeader().getField(35) == "8"
    assert received.getHeader().getField(35) == "8"
    
    # 5. Exchange sends ExecutionReportListFill4Pass to the client (8)
    sent, received = send_and_expect(exch, client, "ExecutionReportListFill4Pass")
    assert sent.getHeader().getField(35) == "8"
    assert received.getHeader().getField(35) == "8"

# #Positive testcase for OrderList and Fill reverse flow where fix message arguments are passed as template names.
@pytest.mark.fix42positiveimproved
def test_OrderListAckFillReverse_AsNames_ShouldPass(fix42_session):
    exch, client = fix42_session
    # clearMessageStore() only empties local deques, so it is done when it returns
    assert exch.clearMessageStore() == True
    assert client.clearMessageStore() == True
    
    # 1. Exchange sends NewOrderListNewPass to the client (checked as E on both sides)
    sent, received = send_and_expect(exch, client, "NewOrderListNewPass")
    assert sent.getHeader().getField(35) == "E"
    assert received.getHeader().getField(35) == "E"
    
    # 2. Client sends ExecutionReportListFill1Pass to the exchange (8)
    sent, received = send_and_expect(client, exch, "ExecutionReportListFill1Pass")
    assert sent.getHeader().getField(35) == "8"
    assert received.getHeader().getField(35) == "8"
    
    # 3. Client sends ExecutionReportListFill2Pass to the exchange (8)
    sent, received = send_and_expect(client, exch, "ExecutionReportListFill2Pass")
    assert sent.getHeader().getField(35) == "8"
    assert received.getHeader().getField(35) == "8"
    
    # 4. Client sends ExecutionReportListFill3Pass to the exchange (8)
    sent, received = send_and_expect(client, exch, "ExecutionReportListFill3Pass")
    assert sent.getHeader().getField(35) == "8"
    assert received.getHeader().getField(35) == "8"
    
    # 5. Client sends ExecutionReportListFill4Pass to the exchange (8)
    sent, received = send_and_expect(client, exch, "ExecutionReportListFill4Pass")
    assert sent.getHeader().getField(35) == "8"
    assert received.getHeader().getField(35) == "8"

#Positive testcase for TestRequest and Heartbeat in reverse flow where fix message arguments are passed as template names.
@pytest.mark.fix42positiveimproved
def test_TestRequestHeartBeatReverse_AsNames_ShouldPass(fix42_session):
    exch, client = fix42_session
    # clearMessageStore() only empties local deques, so it is done when it returns
    assert exch.clearMessageStore() == True
    assert client.clearMessageStore() == True
    
    # TestRequest and Heartbeat are admin messages: wait on the admin deque, not the app one.
    # Take both marks before sending, because the client's engine answers with a Heartbeat by itself.
    exch_mark = last_incoming_seq(exch, "admin")
    client_mark = last_incoming_seq(client, "admin")
    
    # 1. Exchange sends TestRequestPass to the client (1)
    sent = exch.sendMessage("TestRequestPass")
    assert sent.getHeader().getField(35) == "1"
    received = expect_message(client, "TestRequestPass", after_seq=client_mark, kind="admin")
    assert received.getHeader().getField(35) == "1"
    
    # 2. Client's engine replies automatically with a Heartbeat carrying the TestReqID (0)
    received = expect_message(exch, "HeartbeatPass", after_seq=exch_mark, kind="admin")
    assert received.getHeader().getField(35) == "0"

#Positive testcase for get sender and target message sequence number.
@pytest.mark.fix42positiveimproved
def test_getSenderAndTargetMsgSeqNum_ShouldPass(fix42_session):
    exch, client = fix42_session
    
    senderValue = client.getExpectedSenderNum()
    targetValue = client.getExpectedTargetNum()
    
    # After logon each side has sent and received at least the Logon message
    assert isinstance(senderValue, int) and senderValue >= 2
    assert isinstance(targetValue, int) and targetValue >= 2
    
    # What the client sends next is what the exchange expects next
    assert senderValue == exch.getExpectedTargetNum()

#Positive testcase for ResendRequest where fix message arguments are passed as template names.
@pytest.mark.fix42positiveimproved
def test_ResendRequest_AsNames_ShouldPass(fix42_session):
    exch, client = fix42_session
    # clearMessageStore() only empties local deques, so it is done when it returns
    assert exch.clearMessageStore() == True
    assert client.clearMessageStore() == True
    
    # 1. Client sends NewOrderSinglePass to the exchange (checked as D on both sides)
    sent, received = send_and_expect(client, exch, "NewOrderSinglePass")
    assert sent.getHeader().getField(35) == "D"
    assert received.getHeader().getField(35) == "D"
    
    # 2. Exchange sends ExecutionReportAckPass to the client (8)
    sent, received = send_and_expect(exch, client, "ExecutionReportAckPass")
    assert sent.getHeader().getField(35) == "8"
    assert received.getHeader().getField(35) == "8"
    
    # 3. Exchange sends ExecutionReportFillPass to the client (8)
    sent, received = send_and_expect(exch, client, "ExecutionReportFillPass")
    assert sent.getHeader().getField(35) == "8"
    assert received.getHeader().getField(35) == "8"
    
    # 4. clearMessageStore() once again
    assert exch.clearMessageStore() == True
    assert client.clearMessageStore() == True

    # 5. Make the client "forget" the last 2 messages (Ack and Fill): it now expects 2 below what the exchange sends next.
    #    setNextTargetMsgSeqNum() only changes local session state, so it is done when it returns
    targetValue = client.getExpectedTargetNum()
    assert client.setNextTargetMsgSeqNum(targetValue - 2) == True

    # 6. Client sends TestRequestPass. The exchange's Heartbeat reply arrives with a sequence number 2 higher than
    #    the client expects, so the client's engine sends a ResendRequest and the exchange resends Ack and Fill
    #    with PossDupFlag (43=Y)
    sent = client.sendMessage("TestRequestPass")
    assert sent.getHeader().getField(35) == "1"

    # 7. Wait until the resend is complete: the client again expects exactly what the exchange sends next.
    #    The engine updates the sequence number after fromApp()/fromAdmin(), so all resent messages are stored by then
    wait_until(lambda: client.getExpectedTargetNum() == exch.getExpectedSenderNum(),
               description="client to catch up with the exchange after the ResendRequest")

    # 8. Check the messages each side received. receiveMessage() rotates the deque instead of consuming it,
    #    and fixrobot keeps every PossDup message, so the client's app deque holds both resent reports in order
    received = client.receiveMessage("HeartbeatPass")
    assert received.getHeader().getField(35) == "0"

    received = exch.receiveMessage("ResendRequestPass")
    assert received.getHeader().getField(35) == "2"

    # logDumpMessageStore() only writes to the log, so it is done when it returns
    assert client.logDumpMessageStore() == True

    received = client.receiveMessage("ExecutionReportAckResentPass")
    assert received.getHeader().getField(35) == "8"

    received = client.receiveMessage("ExecutionReportFillResentPass")
    assert received.getHeader().getField(35) == "8"
