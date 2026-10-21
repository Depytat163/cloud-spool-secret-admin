# One-time central seed / OWNER approved 2026-10-21

App 5399991, control repository ID 1427369280, installation 173490820. Exact authorization is PRIMARY my-projects:project-management/cloud-spool-system/secret-admin-control-plane-preflight/OWNER_ONE_TIME_BOOTSTRAP_DECISION.md.

Before opening the window: reviewed code and offline/crypto CI PASS. No concurrent credential administration or China intake. OWNER manually dispatches the reviewed main workflow with debug OFF; no inputs. Existing working Google Secrets are not changed.

1. Remove China from App installation; read back only control repository selected.
2. Enable temporary Environments write; preserve Secrets write + Metadata read; no other grants. Approve updated installation if GitHub requires it, read back exact permissions.
3. OWNER generates a distinct temporary App key and provisions only Y360 ADMIN_APP_BOOTSTRAP_PRIVATE_KEY. Never copy central permanent key. Model does not handle PEM or seed values.
4. Execute Y360 manual Central Existing Set Bootstrap on reviewed main. Token requests control repo only and Environments write + Metadata read. Fixed environment secret-administration, three names only; no outputs except sanitized metadata receipt.
5. On success or failure/UNKNOWN, stop writes and reconcile metadata. Never infer value correctness from presence; never rerun automatically.
6. Revoke the distinct temporary key; delete its Y360 secret-copy; remove temporary workflow. Read back each. Keep permanent central key.
7. Remove Environments permission; confirm Secrets write + Metadata read only. Only then restore China alongside control repo. This order resolves the dependency in original transaction step 7: China cannot be bound while installation is control-only.
8. OWNER dispatches protected China Existing Set Binding and personally approves secret-administration. Token China only, Secrets write + Metadata read. Refuse any pre-existing GOOGLE_* name. No concurrent dummy/binding/China intake.
9. After actual binding, minimal China Cloud Spool acceptance; only functional proof establishes correct values. Metadata-only stage is NOT ACTIVE. Preserve run IDs, receipt and permission/key cleanup evidence before final ACTIVE.

UNKNOWN => no retry or rollback writes; preserve stage/confirmed names/run ID, read-only reconcile through approved UI/runtime. Three-secret update is not atomic. No secret values/hashes/ciphertext/PEM in evidence. Fixed API disallows redirect, arbitrary endpoint, name and DELETE. A concurrent human write cannot be prevented by GitHub Secret PUT (no create-only CAS); maintain the explicit exclusive administration window.

Y360 bootstrap copies fixed_binding.py, central_seed.py, test_binding.py and test_crypto.py under .github/secret-admin-bootstrap/. Its temporary workflow is manual-only/main-only/attempt 1. Remove that workflow after the attempt; support code contains no credentials.

Node20 pinned action deprecation remains debt, not an authorization to upgrade unreviewed code during the bootstrap window.
