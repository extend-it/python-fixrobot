"""
Wait helpers for fixrobot tests: replace fixed time.sleep() calls with bounded polling.

Drop this file into fixrobot/tests/ and import it relatively:
    from .fix_waits import wait_logged_on, send_and_expect, expect_message

Why "new message" and not "any message":
fixrobot keeps only the LAST incoming app/admin message per session (fromApp()
clears the deque before appending, and receiveMessage() reads it without
consuming it). So "the deque is non-empty" can still be the previous message.
The helpers record the last incoming MsgSeqNum (34) before an action, and wait
until a message with a higher sequence number arrives.
"""

# Added 26 September 2026 by Vladimir Filipescu (co-authored with Claude Opus 5.5).
# Fork: https://github.com/extend-it/python-fixrobot
# Changes:
#   - new module: bounded-polling wait helpers that replace fixed time.sleep() calls in the tests

import time

import quickfix as fix

DEFAULT_TIMEOUT = 5.0   # seconds; generous for localhost, fails fast compared to hanging
POLL_INTERVAL = 0.05    # seconds between checks


def wait_until(predicate, timeout=DEFAULT_TIMEOUT, interval=POLL_INTERVAL, description="condition"):
    """Poll predicate() until it returns a truthy value or the timeout expires.

    Returns the truthy value; raises TimeoutError with a readable description otherwise.
    """
    deadline = time.monotonic() + timeout
    while True:
        result = predicate()
        if result:
            return result
        if time.monotonic() >= deadline:
            raise TimeoutError(f"Timed out after {timeout:.1f}s waiting for {description}")
        time.sleep(interval)


def _incoming(conn, kind):
    app = conn.application
    if kind == "app":
        return app.incomingFIXRobotAppMessageDeque
    if kind == "admin":
        return app.incomingFIXRobotAdminMessageDeque
    raise ValueError("kind must be 'app' or 'admin'")


def last_incoming_seq(conn, kind="app"):
    """MsgSeqNum (34) of the last incoming message on this connection, 0 if none."""
    try:
        return int(_incoming(conn, kind)[-1].getHeader().getField(34))
    except Exception:  # empty deque, or cleared by the QuickFIX thread mid-read
        return 0


def is_logged_on(conn):
    session = fix.Session.lookupSession(conn.application.sessID)
    return session is not None and session.isLoggedOn()


def wait_logged_on(conn, timeout=10.0):
    """Replace the sleeps after startInitiator()/startAcceptor()."""
    wait_until(lambda: is_logged_on(conn), timeout,
               description=f"logon of session {conn.application.sessID}")


def wait_logged_off(conn, timeout=10.0):
    """Replace the sleeps after stopInitiator()/stopAcceptor()."""
    wait_until(lambda: not is_logged_on(conn), timeout,
               description=f"logout of session {conn.application.sessID}")


def expect_message(conn, *template, after_seq, kind="app", timeout=DEFAULT_TIMEOUT):
    """Wait for a NEW incoming message (seq > after_seq), then validate it once.

    *template is what fixrobot's receiveMessage() takes: a template name from
    DEFAULTMESSAGES.ini, or (msg_type_name, message_string).
    Validation runs once, after arrival, so a wrong message fails immediately
    instead of being retried until the timeout.
    """
    wait_until(lambda: last_incoming_seq(conn, kind) > after_seq, timeout,
               description=f"{template[0]} on session {conn.application.sessID} "
                           f"(new {kind} message after seq {after_seq})")
    try:
        return conn.receiveMessage(*template)
    except Exception:
        raise AssertionError(
            f"{template[0]}: received message differs from expected "
            f"(field-by-field diff in fixrobot.log)") from None


def send_and_expect(sender, receiver, *template, timeout=DEFAULT_TIMEOUT):
    """Send a message from one side and wait until the other side has received it.

    Returns (sent_message, received_message).
    """
    mark = last_incoming_seq(receiver)
    sent = sender.sendMessage(*template)
    received = expect_message(receiver, *template, after_seq=mark, timeout=timeout)
    return sent, received