"""Fixed administration request boundary. No credential or network access."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NAMES = ('GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'GOOGLE_REFRESH_TOKEN')
FIELDS = frozenset(('operation_id', 'target_repository_id', 'target_repository',
                    'action', 'credential_set', 'credential_version'))

class Denied(Exception):
    pass

def validate(request, registry):
    if not isinstance(request, dict) or set(request) != FIELDS:
        raise Denied('INVALID_FIELDS')
    if request['action'] != 'bind-existing-set' or request['credential_set'] != 'existing-google-drive':
        raise Denied('INVALID_ACTION_OR_SET')
    if type(request['target_repository_id']) is not int:
        raise Denied('INVALID_TARGET_ID')
    if not isinstance(request['target_repository'], str):
        raise Denied('INVALID_TARGET_NAME')
    for field in ('operation_id', 'credential_version'):
        if not isinstance(request[field], str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,79}', request[field]):
            raise Denied('INVALID_IDENTIFIER')
    pair = (request['target_repository_id'], request['target_repository'])
    allowed = {(x['repository_id'], x['repository']) for x in registry['targets']}
    if pair not in allowed:
        raise Denied('UNAPPROVED_TARGET')
    return dict(request)

def reconcile(journal, observed):
    """Never infer value identity from metadata; never produce write instructions."""
    if set(observed) - set(NAMES):
        raise Denied('INVALID_METADATA')
    if journal.get('state') in ('UNKNOWN', 'PARTIAL', 'PREPARED'):
        return {'state': 'RECONCILIATION_REQUIRED', 'writes_allowed': False,
                'metadata_names_present': [x for x in NAMES if x in observed],
                'value_equivalence_proven': False}
    if journal.get('state') == 'ACCEPTED':
        return {'state': 'ACCEPTED', 'writes_allowed': False}
    raise Denied('UNRECOGNIZED_OPERATION_STATE')

def lint_bundle(root=ROOT):
    policy = json.loads((root / 'policy.json').read_text())
    registry = json.loads((root / 'targets.json').read_text())
    manifest = json.loads((root / 'app-manifest.template.json').read_text())
    assert tuple(policy['secret_names']) == NAMES
    assert set(policy['request_fields']) == FIELDS
    assert manifest['default_permissions'] == {'secrets': 'write', 'metadata': 'read'}
    assert manifest['hook_attributes']['active'] is False
    ids = [x['repository_id'] for x in registry['targets']]
    assert len(ids) == len(set(ids))
    admin = (root / '.github/workflows/environment-gate-proof.yml').read_text()
    assert 'workflow_dispatch:' in admin and 'environment: secret-administration' in admin
    assert 'persist-credentials: false' in admin
    assert 'pull_request_target' not in admin and 'push:' not in admin and 'pull_request:' not in admin
    assert 'secrets.' not in (root / '.github/workflows/security.yml').read_text()
    return True
