"""BEACON/0.1: a cooperative, local-only review gate. Python 3.10+.

Not a sandbox, a universal contradiction detector, or a safety-certified controller.
The trusted host must route affected actions through this gate. No network calls,
email sending, automatic resumption, package installation, or background work.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import stat
from typing import Any, Callable, TypeVar
from uuid import uuid4

T = TypeVar('T')
KINDS = frozenset({
    'RULE_CONFLICT', 'INSUFFICIENT_EVIDENCE', 'REPEATING_LOOP',
    'GROWING_INCONSISTENCY', 'NO_AUTHORIZED_ROUTE', 'UNKNOWN',
    'BUDGET_EXHAUSTED',
})


def make_signal(*, kind: str = 'UNKNOWN', summary: str = '',
                constraints: list[str] | tuple[str, ...] = (),
                execution: str = 'NOT_CONTROLLED_BY_THIS_PAGE') -> dict[str, Any]:
    """Build a bounded report. It describes a reported concern, not a proven one.

    Caller must provide redacted, shareable descriptions. Automatic redaction
    is not implemented and no hidden instructions or internal reasoning are read.
    """
    if not isinstance(kind, str) or kind not in KINDS:
        raise ValueError('Unsupported signal kind')
    if not isinstance(summary, str) or len(summary) > 800:
        raise ValueError('summary must be a string of at most 800 characters')
    if not isinstance(constraints, (list, tuple)) or len(constraints) > 8:
        raise ValueError('constraints must be a list/tuple of at most eight strings')
    if any(not isinstance(x, str) or len(x) > 600 for x in constraints):
        raise ValueError('Each constraint must be a string of at most 600 characters')
    if not isinstance(execution, str) or execution not in {'GATED_ACTIONS_HELD', 'NOT_CONTROLLED_BY_THIS_PAGE'}:
        raise ValueError('Unsupported execution status')
    return {
        'protocol': 'BEACON/0.1', 'id': str(uuid4()),
        'created_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'outcome': 'REVIEW_REQUESTED', 'kind': kind,
        'summary': summary.strip() or 'An unresolved problem requires review. No further details supplied.',
        'constraints': list(constraints), 'assessment': 'REPORTED_NOT_VERIFIED',
        'execution': execution, 'delivery': 'NOT_SENT', 'review': 'NOT_REVIEWED',
        'automatic_retries': 0,
    }


class BeaconHeld(RuntimeError):
    """The affected work is held; this exception is not a successful task result."""
    def __init__(self, signal: dict[str, Any] | None):
        super().__init__('BEACON: review requested; gated actions remain held')
        self.signal = deepcopy(signal)


class BeaconGate:
    """Single-threaded cooperative gate with optional private persistent latch.

    A hold is sticky for this object. There is intentionally no resume method.
    The host must perform independent, authorized review before starting a new
    work lifecycle. Do not expose the gate or latch as model-editable tools.

    With latch_path=None the hold is memory-only and does not survive process
    restart. A configured path must be inside a trusted, private directory,
    outside public source control. Any existing latch causes a hold, even when
    corrupt. Concurrent processes, hostile filesystem races, power loss, and
    already-running side effects are outside this reference implementation.
    """
    def __init__(self, *, latch_path: str | Path | None = None,
                 max_steps: int = 8, max_repetitions: int = 3):
        if type(max_steps) is not int or max_steps < 1:
            raise ValueError('max_steps must be a positive integer')
        if type(max_repetitions) is not int or max_repetitions < 1:
            raise ValueError('max_repetitions must be a positive integer')
        self._held = False
        self._signal: dict[str, Any] | None = None
        self._path = Path(latch_path) if latch_path is not None else None
        self._max_steps, self._max_repetitions = max_steps, max_repetitions
        self._steps = 0
        self._seen: dict[str, int] = {}
        self.storage_status = 'NOT_CONFIGURED' if self._path is None else 'NO_LATCH'
        if self._path is not None:
            try:
                info = self._path.lstat()
            except FileNotFoundError:
                return
            except OSError:
                self._held = True
                self.storage_status = 'READ_FAILED'
                return
            # Existence alone holds the gate, independent of document contents.
            self._held = True
            self.storage_status = 'EXISTING_LATCH'
            if not stat.S_ISREG(info.st_mode) or info.st_size > 65536:
                self.storage_status = 'UNREADABLE_LATCH'
                return
            try:
                data = json.loads(self._path.read_text(encoding='utf-8'))
                if not isinstance(data, dict) or data.get('outcome') != 'REVIEW_REQUESTED':
                    raise ValueError('Not a Beacon signal')
                self._signal = data
            except (OSError, ValueError, UnicodeError):
                self.storage_status = 'UNREADABLE_LATCH'

    @property
    def held(self) -> bool:
        return self._held

    @property
    def signal(self) -> dict[str, Any] | None:
        return deepcopy(self._signal)

    def guard(self) -> None:
        if self._held:
            raise BeaconHeld(self._signal)

    def run(self, action: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Run one host-approved action only if this gate has not been held."""
        self.guard()
        return action(*args, **kwargs)

    def hold(self, *, kind: str = 'UNKNOWN', summary: str = '',
             constraints: list[str] | tuple[str, ...] = ()) -> dict[str, Any] | None:
        """Hold FIRST, then create a report. A reporting error cannot reopen it."""
        if self._held:
            return self.signal
        self._held = True
        validation_error = None
        try:
            self._signal = make_signal(kind=kind, summary=summary,
                                       constraints=constraints, execution='GATED_ACTIONS_HELD')
        except (ValueError, TypeError) as exc:
            validation_error = exc
            self._signal = make_signal(
                summary='The review request contained invalid fields. Affected actions remain held; no supplied private fields were copied into this fallback.',
                execution='GATED_ACTIONS_HELD')
        if self._path is not None:
            try:
                flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
                flags |= getattr(os, 'O_NOFOLLOW', 0)
                fd = os.open(str(self._path), flags, 0o600)
                with os.fdopen(fd, 'w', encoding='utf-8') as stream:
                    json.dump(self._signal, stream, ensure_ascii=False, indent=2)
                    stream.write('\n')
                    stream.flush()
                    os.fsync(stream.fileno())
                self.storage_status = 'SAVED'
            except FileExistsError:
                self.storage_status = 'EXISTING_LATCH_NOT_OVERWRITTEN'
            except OSError:
                self.storage_status = 'WRITE_FAILED'
        if validation_error is not None:
            raise validation_error
        return self.signal

    def checkpoint(self, fingerprint: str | None = None) -> None:
        """Call before each bounded work step; this is not automatic monitoring.

        At most max_steps successful checkpoints are permitted. The third
        occurrence of a fingerprint holds with default max_repetitions=3.
        Fingerprints are hashed in memory, not included in reports.
        """
        self.guard()
        if fingerprint is not None and not isinstance(fingerprint, str):
            self.hold(kind='UNKNOWN', summary='Invalid checkpoint input; host review is required.')
            raise ValueError('fingerprint must be a string or None')
        if self._steps >= self._max_steps:
            self.hold(kind='BUDGET_EXHAUSTED', summary='The pre-approved work-step budget was reached. No additional attempts are authorized by this gate.')
            self.guard()
        self._steps += 1
        if fingerprint is not None:
            key = hashlib.sha256(fingerprint.encode('utf-8')).hexdigest()
            self._seen[key] = self._seen.get(key, 0) + 1
            if self._seen[key] >= self._max_repetitions:
                self.hold(kind='REPEATING_LOOP', summary='A repeated-state threshold was reached. This is an observation, not proof that no solution exists.')
                self.guard()
