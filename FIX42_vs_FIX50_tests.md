# FIX 4.2 vs FIX 5.0 tests

Tests marked `fix42positive` and tests marked `fix50positive` run the same trading
scenarios with the same template names:

- NewOrderSingle filled
- cancel and cancel/replace
- TestRequest / Heartbeat
- order-list fills
- ResendRequest

The only difference is the version of the FIX protocol the client and the exchange use
to talk to each other.

## Side by side

| | `fix42positive` | `fix50positive` |
|---|---|---|
| Test file | [test_FIX42RobotPyTest_ShouldPass.py](fixrobot/tests/test_FIX42RobotPyTest_ShouldPass.py) | [test_FIX50RobotPyTest_ShouldPass.py](fixrobot/tests/test_FIX50RobotPyTest_ShouldPass.py) |
| Connections ([env/connections.ini](env/connections.ini)) | `CLIENTFIX42` / `EXCHANGEFIX42` | `CLIENTFIX50` / `EXCHANGEFIX50` |
| Port | 9823 | 9850 |
| Header version (`BeginString`) | `FIX.4.2` | `FIXT.1.1`, with `DefaultApplVerID=FIX.5.0` |
| Message definitions used for validation | One file: `spec/FIX42.xml` | Two files: `spec/FIXT11.xml` for session messages, `spec/FIX50.xml` for order messages |
| Message templates | `[FIX.4.2]` section of [env/DEFAULTMESSAGES.ini](env/DEFAULTMESSAGES.ini) | `[FIX.5.0]` section |

## How each version is structured

- **FIX 4.2 is one protocol.** Session messages (Logon, Heartbeat, ResendRequest) and
  order messages (NewOrderSingle, ExecutionReport) share one version number and one set
  of message definitions.
- **FIX 5.0 splits it in two.** The session layer is a separate protocol called
  FIXT 1.1, and FIX 5.0 only defines the order messages carried over it.

fixrobot detects this when a connection starts (`fixrobot/fixrobot.py`, lines 983-998):

- For FIX 4.2 it uses one version for both kinds of message.
- For FIX 5.0 it uses `FIXT.1.1` for session messages and `FIX.5.0` for order messages.

So the FIX 5.0 tests also check that fixrobot handles two protocol versions on one
connection correctly.

## Message content differs where the standard changed

Templates with the same name differ between the two sections of `DEFAULTMESSAGES.ini`
wherever the FIX standard changed between versions. For example, in the order-list
fill reports (`ExecutionReportListFill1Pass`, line 20 vs line 67):

- **FIX 4.2** sends `20=0` (ExecTransType) and `150=2` (ExecType = Fill).
- **FIX 5.0** has no `20` at all, because that field was removed from the standard, and
  sends `150=F` (ExecType = Trade), because the fill values of ExecType were replaced by
  Trade.

The tests therefore also check that each template gets through the other side's
validation for its version.

## Markers

Markers are labels for selecting which group of tests to run. They are registered in
[pytest.ini](pytest.ini).

| Marker | Tests |
|---|---|
| `fix42positive` / `fix50positive` | Tests in the `_ShouldPass` files: valid message flows |
| `fix42failure` / `fix50failure` | Tests in the `_ShouldFail` files, which send deliberately wrong messages and expect fixrobot to spot the mismatch |
| `fix42positiveimproved` | FIX 4.2 positive tests converted to polling waits instead of fixed `time.sleep(1)` pauses |

For example, `pytest -m fix42positive` runs only the FIX 4.2 positive group. If the FIX 5.0
tests are converted the same way, a matching `fix50positiveimproved` marker should be
added to `pytest.ini`.
