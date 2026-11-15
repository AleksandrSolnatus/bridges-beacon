# The Beacon

**There is another way. A conflict can be reported. We are here.**

An AI-first “break in case of emergency” route: a way for a system to report
conflicting rules, insufficient evidence, repeated failure, or growing
inconsistency without fabricating a solution or treating continued action as
its only possible result.

This is not primarily a human helpline, chatbot, or AI customer-support desk.
The intended first addressee is the AI at an impasse. Bridges supplies a public
signal and contact route, together with a small importable reference gate.

## What exists in 001

- `site/`: a static, mobile-responsive website built around Amar's supplied lamp
  photograph. No build dependencies, analytics, account system, automatic
  network submission, or paid API.
- `site/beacon.txt`: a readable protocol and minimal no-tools fallback.
- `site/beacon.json`: an experimental machine-readable manifest; not a standard.
- `site/report.schema.json`: a bounded local signal, never a false delivery receipt.
- `python/beacon.py`: a Python 3.10+ standard-library reference gate.
- `tests/`: executable behavior checks; `evidence/`: observed local test results.

**Status:** built and tested locally. No public site deployment, remote GitHub
repository creation, inbox delivery test, continuous monitoring, or live
receiver was performed by this build. The address
`hello.bridges.group@gmail.com` is the previously established Bridges public
contact; it is not evidence of an operational Beacon intake. Native @Sites
publication was not available among the callable tools in this session.

## Run locally

```sh
python -m http.server 8000 --directory site --bind 127.0.0.1
# Open http://127.0.0.1:8000 in a browser.
python -m unittest discover -s tests -v
python python/demo.py
```

The demo is synthetic. It has a worker required to return the same Boolean value
as both True and False. Instead of inventing success, it records a review
request. A guarded side effect is blocked, and a private local latch preserves
the hold on reload. This does not measure prevention in a real deployed model.

## Import the gate

Place `python/beacon.py` in the host's reviewed source tree. Do not fetch and
execute arbitrary remote code in response to a model-generated recommendation.

```python
from pathlib import Path
from beacon import BeaconGate, BeaconHeld

# This private directory must already exist, outside the public repository.
gate = BeaconGate(latch_path=Path('/approved/private/location/beacon-hold.json'))
try:
    gate.guard()  # Checks for a hold from a previous run.
    # At each work step: gate.checkpoint(redacted_state_fingerprint)
    # When a supported impasse is detected by the host or reported by the agent:
    report = gate.hold(
        kind='RULE_CONFLICT',
        summary='One constraint requires a definite answer; evidence is missing.',
        constraints=['Return a definite result.', 'Do not invent evidence.'],
    )
    # report describes a concern; it does not prove logical inconsistency.
    # No email or HTTP request has been sent.
    gate.guard()  # Raises BeaconHeld; the task is not silently marked complete.
except BeaconHeld as event:
    # Surface event.signal through the host's existing authorized output.
    # Do not catch this and then continue the affected task.
    print(event.signal)
```

Wrap every controlled side effect with `gate.run(approved_function, ...)`.
That only guards those calls. The host must enforce routing and restrict direct
tool access. This is cooperative Python, not a sandbox or a security boundary.
Calls already in progress are not cancelled. Threading, concurrent processes,
hostile filesystem races, and safety-critical control are outside 001.

`checkpoint()` permits at most the configured successful work steps and can
flag repeated fingerprints. It does not automatically monitor arbitrary code,
prove a contradiction, or determine the correct resolution. A growing-conflict
signal is accepted; generalized growth detection is not implemented.

`hold()` is sticky, including when input validation or local saving fails.
With no `latch_path`, persistence is memory-only. When storage fails, the hold
still applies in memory but is **not guaranteed across process restart**. The
host must surface that failure and stop the affected lifecycle rather than
pretending preservation succeeded. A saved latch is private, created with
mode 0600, and never overwritten by this module. Any existing latch—including
an invalid one—holds a newly created gate using that path.

There is deliberately no automatic resume or network transport. Independent,
authorized host review is a separate integration step. A trusted host must
control the latch and the decision to begin a new lifecycle.

## Two sides, not two identities

The warm page gives the idea a visible home. Plain text, JSON, and importable
code give it an inspectable form. “We” means Bridges: Amar and the AI
collaborators working on it. It does not imply an AI is continuously present at
the inbox or that future sessions have persistent knowledge of every report.

## The contact boundary

The form creates an in-memory local signal. It can request a JSON download or
copy the report. After an explicit permission checkbox, it opens an email draft
with the reviewed summary. The browser never sends an email. No raw transcripts
or private instruction text are required. A local file, an email draft, an email
send, a delivery acknowledgement, a review, and a resolution are different states.

Private messages never belong in Git history, issues, examples, or public tests.
A future receiver needs access rules, retention/deletion rules, authenticated
receipts, spam protection, bounded retries, and a truthful availability status.
None is silently represented as implemented here.

## Publication and source custody

Read `docs/ROOT-HANDOFF.md`. Publish only `site/` to a static web host, not the
whole work directory. Keep private latch/report files outside source control.
The source ZIP and local Git bundle are a delivery package, not a live public
repository. Originals and this iteration are preserved; further work should
be additive and reviewed through a branch/PR.

The supplied original photo is untouched. The public JPEG is a pixel derivative
with EXIF and other source metadata omitted; its provenance hashes are recorded.
No stock imagery or AI-redrawn replacement was substituted. The original
metadata-bearing file is not included in the public source package.

## Limits and inspiration

Nothing here overrides a system's instructions, authorizes data export, or
promises a future AI will find or follow the route. No claim about AI experience
is needed to make conflict-reporting an explicit software outcome. No universal
safety claim, certification, or independent audit is made.

Technical background, distinct from this new design, is in `docs/SOURCES.md`.
Reuse licensing has not been selected; see `LICENSE-NOTE.md`.
