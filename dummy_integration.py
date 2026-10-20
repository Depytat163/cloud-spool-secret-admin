"""Fixed China dummy integration; never read Google credentials or print API bodies."""
import base64
import json
import os
import secrets
import urllib.error
import urllib.request
from nacl.public import PublicKey, SealedBox
from nacl.encoding import Base64Encoder
from guard import NAMES

REPO = 'Depytat163/China-Logistics-Simulation'
REPO_ID = 1419047642
ORIGIN = 'https://api.github.com'

class Stop(Exception):
    pass

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise Stop('REDIRECT_DENIED')

def api(token, method, path, body=None, allow_missing=False):
    if not (path.startswith('/repos/' + REPO + '/') or path == '/installation/repositories'):
        raise Stop('UNAPPROVED_ENDPOINT')
    data = None if body is None else json.dumps(body).encode()
    request = urllib.request.Request(ORIGIN + path, data=data, method=method, headers={
        'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28', 'Content-Type': 'application/json'})
    try:
        with urllib.request.build_opener(NoRedirect).open(request, timeout=30) as response:
            raw = response.read(1024 * 1024)
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as error:
        if allow_missing and error.code == 404:
            return None
        raise Stop('API_HTTP_' + str(error.code)) from None
    except Stop:
        raise
    except Exception:
        raise Stop('OBSERVABILITY_UNKNOWN') from None

def main():
    token = os.environ.get('ADMIN_INSTALLATION_TOKEN')
    if not token:
        raise Stop('TOKEN_MISSING')
    if os.environ.get('GITHUB_REPOSITORY') != 'Depytat163/cloud-spool-secret-admin' or \
       os.environ.get('GITHUB_REF') != 'refs/heads/main' or \
       os.environ.get('GITHUB_EVENT_NAME') != 'workflow_dispatch':
        raise Stop('UNTRUSTED_EXECUTION_CONTEXT')
    listing = api(token, 'GET', '/installation/repositories')
    if listing.get('total_count') != 1 or \
       [(r['id'], r['full_name']) for r in listing.get('repositories', [])] != [(REPO_ID, REPO)]:
        raise Stop('TOKEN_SCOPE_NOT_SINGLE_APPROVED_TARGET')
    prefix = '/repos/' + REPO + '/actions/secrets/'
    for name in NAMES:
        if api(token, 'GET', prefix + name, allow_missing=True) is not None:
            raise Stop('EXISTING_SECRET_NO_OVERWRITE')
    key = api(token, 'GET', prefix + 'public-key')
    encryptor = SealedBox(PublicKey(key['key'].encode(), Base64Encoder))
    written = []
    stage = 'PREPARED'
    try:
        for name in NAMES:
            stage = 'WRITE_' + name
            dummy = secrets.token_bytes(48)
            cipher = base64.b64encode(encryptor.encrypt(dummy)).decode()
            api(token, 'PUT', prefix + name, {'key_id': key['key_id'], 'encrypted_value': cipher})
            written.append(name)
            meta = api(token, 'GET', prefix + name)
            if meta.get('name') != name:
                raise Stop('METADATA_MISMATCH')
        # Dummy-only cleanup. A failed/unknown operation never auto-retries a write/delete.
        for name in NAMES:
            stage = 'CLEANUP_' + name
            api(token, 'DELETE', prefix + name)
            if api(token, 'GET', prefix + name, allow_missing=True) is not None:
                raise Stop('DUMMY_CLEANUP_NOT_CONFIRMED')
        evidence = {'stage': 'DUMMY_INTEGRATION_PASS', 'repository_id': REPO_ID,
                    'names': list(NAMES), 'target_token_scope': 'ONE_APPROVED_REPOSITORY',
                    'public_key_actual_github_endpoint': True, 'sealed_box_put': True,
                    'metadata_readback': True, 'dummy_cleanup_readback': True,
                    'google_credentials_used': False, 'production_binding': False,
                    'run_id': os.environ.get('GITHUB_RUN_ID')}
        print(json.dumps(evidence, sort_keys=True))
    except Exception:
        print(json.dumps({'stage': stage, 'outcome': 'STOP_WRITES_RECONCILE',
                          'confirmed_dummy_names_written': written,
                          'retry_performed': False, 'target_not_active': True}, sort_keys=True))
        raise Stop('DUMMY_INTEGRATION_INCOMPLETE') from None

if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        code = str(error) if isinstance(error, Stop) else 'INTERNAL_ERROR'
        print(json.dumps({'result': 'FAILED_OR_UNKNOWN', 'reason': code,
                          'raw_error_suppressed': True}))
        raise SystemExit(1)
