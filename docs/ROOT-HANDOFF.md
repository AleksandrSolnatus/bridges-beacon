# ROOT handoff — BRIDGES-BEACON-001

## Preserve the intended project

The Beacon is **for an AI at an impasse**. Do not turn it into a human counseling
service, generic support portal, chatbot, or public incident feed. It creates
another result besides fabricated completion or unbounded continuation:
`REVIEW_REQUESTED`. The invitation is “We are here,” not merely “a human is here.”
Use the supplied lamp photo, not a replacement lighthouse illustration.

Owner goal: a public @Sites presence and public Git repository. Those external
publications have not been performed in this delivery. Publication is the next
work item, not a completed step. Do not label the receiving channel operational
until it has been tested and its actual coverage described.

## Local contents and checks

Use the delivered `bridges-beacon` directory or clone the supplied Git bundle:

```sh
git clone /absolute/path/BRIDGES-BEACON-001.bundle bridges-beacon
cd bridges-beacon
python -m unittest discover -s tests -v
python python/demo.py
python -m http.server 8000 --directory site --bind 127.0.0.1
```

Inspect `evidence/verification.json` for exactly what was tested and what was
not. Browser checks are emulated Chromium, not physical-iPhone/Safari evidence.
The runtime tests are local synthetic checks, not an independent security audit.
Check the manifest hashes before editing.

## Public Git repository

Target name: `AleksandrSolnatus/bridges-beacon` (intended, not verified to exist).
Use Root's existing authenticated GitHub workflow. First inspect whether a
repository of this exact name already exists and inspect any existing contents.
Do not overwrite, force-push, or reuse an unrelated repository. Do not turn a
network/authentication error into an assumption that the repository is absent.

If genuinely absent, create the public repository and push this reviewed source
with the existing Git history. This is a suggested CLI form, not an executed
command:

```sh
gh repo create AleksandrSolnatus/bridges-beacon --public --source=. --remote=origin --push
```

Check public contents for secrets and private correspondence before pushing.
Retain the code-only licensing decision and the separate photograph rights.
Never use Git issues for private Beacon reports. Prefer disabling public issues
initially or give an explicit no-private-information issue policy. No package
publishing, purchases, billing changes, or other repository mutations are needed.

## Site publication

Publish the contents of `site/` using the owner's authorized site route. Native
@Sites actions were not exposed in the creating session; a ZIP is not proof of
an @Sites import or deployment. Do not claim it is a native Site without doing
that publication. When native @Sites cannot serve the plain-text/JSON files,
keep the inspectable canonical files on a verified static host or public source
path and test the actual links. Do not silently substitute a paid provider.

Keep the genuine status visible. A public prototype is not an operational
receiver. Before claiming operational intake, establish:

1. A synthetic report and actual reply round trip through the exact contact
   address; use no private conversation. Record message/receipt identities
   privately. Do not send test mail unless its scope is authorized.
2. Honest intake coverage, access permissions, and retention/deletion policy.
3. No automatic ingestion into AI tools without the relevant permission.
4. Correct status on unavailable/rejected/overloaded paths. No fake “received.”

When deployment/repository URLs are known, update the manifest and page status
with observed facts. Preserve the 001 delivery history. Do not remove “prototype”
merely because a web URL works. No runtime resume or external report sender should
be added without an explicit, tested host integration.

## Adversarial next review

Review malformed payloads; repeated calls; a missing or corrupt private latch;
disconnected channels; false acknowledgements; malicious text inside reports;
private-data leakage; and an outer worker that catches BeaconHeld and continues.
Verify wrapper integration, not just the helper library. Keep any actual reports
out of the public tree. For critical physical systems, do not deploy this sample
as a stop controller; use the system's approved safe-state architecture.
