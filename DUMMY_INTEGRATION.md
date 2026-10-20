# Dummy integration — no production values

App 5399991 / installation 173490820 verified selected-only: China (1419047642), control-plane (1427369280). ADMIN_APP_PRIVATE_KEY presence verified in protected environment; value never accessed. Saved App permissions only Secrets write / Metadata read.

This manual workflow uses no inputs, dispatch only, main + OWNER environment approval, pinned checkout/App-token action. It requests one-repository token and checks actual installation listing before writes. No Contents/Admin/Environments permission requested. No Google credentials referenced or used.

Target fixed China; if ANY existing GOOGLE_* Secret metadata exists, stop without overwrite. Dummy random bytes in memory only → actual target public key → libsodium → PUT → metadata read-back → delete only dummy names → confirm absence. Cleanup is restricted to these newly created nonproduction dummy entries; no arbitrary delete. China stays NOT ACTIVE. A transport failure stops all writes and reports stage/names only; do not retry workflow until read-only reconciliation determines residual dummy state. Repo Secrets APIs lack a create-only CAS, so OWNER/other admin must not concurrently change these names during this controlled test window. Runtime does not claim metadata proves secret value equivalence.

Offline crypto tests verify recipient-key roundtrip and wrong-key denial; request/partial/UNKNOWN tests remain simulations and are labelled as such. Live repository PUT is distinct evidence. Success does not prove real Google auth or central environment bootstrap. Remaining tests include full unauthorized execution denial/leak review and actual token authority verification. No production binding until complete suite reviewed.

Central bootstrap gap remains: environment-secret writes require Environments:write (not provided). Changing protection settings separately requires Administration:write, which is not needed and must stay absent. No permission extension or temporary Y360 key is introduced here.
