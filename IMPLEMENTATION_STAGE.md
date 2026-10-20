# Stage 1: single-owner protection / noncredential tests

OWNER decision 2026-10-20 supersedes independent PR approval requirement. PR-only path remains; no admin bypass, force push or deletion. Environment secret-administration is main-only, required reviewer Depytat163, no administrator bypass. Administrative values must exist only in that protected environment.

This PR adds only noncredential policy/schema validation and an isolated environment canary proof, not production distribution capability. No App registration/key, Google value or real target write. Local request/recovery tests do not constitute live GitHub encryption/PUT, token-scope or end-to-end security suite PASS.

Before merging: run Control Plane Security/security and make it a required strict status check; failed/pending check must block merge. No direct push to main. Environment gate proof is manual workflow_dispatch only, fixed main condition, no arbitrary inputs, pinned checkout with credential persistence disabled. Owner must personally dispatch/approve it; the agent must not click deployment approval as if it were a human event.

CONTROL_PLANE_TEST_CANARY is a disposable non-authorizing dummy marker, environment-only. It must be provisioned via trusted admin UI and must not be a real credential. Ordinary job expects it absent; protected job expects it present, without printing it. Waiting job alone proves job-start gating, not canary delivery; full canary success requires post-approval execution and log read-back. No production key/Google Secrets until this test and the remaining dummy integration suite PASS.

Threat boundary does not protect against compromised OWNER account. Agent/connector identity may coincide with OWNER; a browser click by the agent is not acceptable human security approval. Preserve requested separation: reviewed code/checks vs explicit human capability release.

Open integration tests: actual repository public key/Libsodium PUT/metadata; dummy partial recovery/UNKNOWN; restricted installation token; App permission scope; PR/fork/alternate-ref runtime denial and leak checks. These require narrow App bootstrap and dummy fixture. None is marked PASS by these offline tests.
