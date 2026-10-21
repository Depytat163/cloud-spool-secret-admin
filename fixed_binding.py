"""Fixed secret replication: no value, API body or ciphertext logging."""
import base64
import json
import os
import urllib.error
import urllib.request

NAMES = ('GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'GOOGLE_REFRESH_TOKEN')
CONTROL = 'Depytat163/cloud-spool-secret-admin'
CHINA = 'Depytat163/China-Logistics-Simulation'
MODES = {
    'seed': ('Depytat163/y360-workspace', CONTROL, 1427369280,
             '/repos/' + CONTROL + '/environments/secret-administration/secrets/'),
    'china': (CONTROL, CHINA, 1419047642, '/repos/' + CHINA + '/actions/secrets/'),
}

class Stop(Exception):
    pass

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise Stop('REDIRECT_DENIED')

class API:
    def __init__(self, token, prefix):
        self.token, self.prefix = token, prefix

    def call(self, method, path, body=None, missing=False):
        allowed = {('GET', '/installation/repositories'), ('GET', self.prefix + 'public-key')}
        allowed.update((verb, self.prefix + name) for verb in ('GET', 'PUT') for name in NAMES)
        if (method, path) not in allowed:
            raise Stop('UNAPPROVED_ENDPOINT')
        data = None if body is None else json.dumps(body).encode()
        req = urllib.request.Request('https://api.github.com' + path, data=data, method=method,
            headers={'Authorization': 'Bearer ' + self.token,
                     'Accept': 'application/vnd.github+json',
                     'X-GitHub-Api-Version': '2022-11-28', 'Content-Type': 'application/json'})
        try:
            with urllib.request.build_opener(NoRedirect).open(req, timeout=30) as response:
                raw = response.read(1024 * 1024)
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as error:
            if method == 'GET' and missing and error.code == 404:
                return None
            raise Stop('API_HTTP_' + str(error.code)) from None
        except Stop:
            raise
        except Exception:
            raise Stop('OBSERVABILITY_UNKNOWN') from None

def encrypt(value, key):
    from nacl.public import PublicKey, SealedBox
    from nacl.encoding import Base64Encoder
    return base64.b64encode(SealedBox(PublicKey(key.encode(), Base64Encoder)).encrypt(value)).decode()

def validate_context(mode, env):
    if mode not in MODES:
        raise Stop('INVALID_MODE')
    source = MODES[mode][0]
    if (env.get('GITHUB_REPOSITORY') != source or env.get('GITHUB_REF') != 'refs/heads/main'
            or env.get('GITHUB_EVENT_NAME') != 'workflow_dispatch'
            or env.get('GITHUB_RUN_ATTEMPT') != '1'):
        raise Stop('UNTRUSTED_CONTEXT_OR_RERUN')
    if env.get('ACTIONS_STEP_DEBUG', '').lower() == 'true' or env.get('ACTIONS_RUNNER_DEBUG', '').lower() == 'true':
        raise Stop('DEBUG_DENIED')
    if not env.get('GITHUB_RUN_ID', '').isdigit():
        raise Stop('INVALID_RUN_ID')
    return MODES[mode]

def perform(mode, env, api, seal=encrypt, emit=lambda x: print(json.dumps(x, sort_keys=True))):
    _, target, target_id, prefix = validate_context(mode, env)
    stage, confirmed = 'PREFLIGHT', []
    receipt = {'operation': 'central-seed-v1' if mode == 'seed' else 'china-bind-existing-v1',
               'run_id': env['GITHUB_RUN_ID'], 'target_repository_id': target_id,
               'names': list(NAMES), 'value_equivalence_proven': False}
    try:
        listing = api.call('GET', '/installation/repositories')
        if listing.get('total_count') != 1 or [(r.get('id'), r.get('full_name')) for r in listing.get('repositories', [])] != [(target_id, target)]:
            raise Stop('TOKEN_SCOPE_NOT_SINGLE_APPROVED_TARGET')
        for name in NAMES:
            if api.call('GET', prefix + name, missing=True) is not None:
                raise Stop('EXISTING_OR_PARTIAL_SET_NO_OVERWRITE')
        if not all(isinstance(env.get(name), str) and env[name] for name in NAMES):
            raise Stop('SOURCE_SET_INCOMPLETE')
        key = api.call('GET', prefix + 'public-key')
        encrypted = [(name, seal(env[name].encode(), key['key'])) for name in NAMES]
        for name, cipher in encrypted:
            stage = 'PUT_' + name
            api.call('PUT', prefix + name, {'key_id': key['key_id'], 'encrypted_value': cipher})
            stage = 'READBACK_' + name
            meta = api.call('GET', prefix + name)
            if not isinstance(meta, dict) or meta.get('name') != name:
                raise Stop('METADATA_MISMATCH')
            confirmed.append(name)
        receipt.update(state='METADATA_VERIFIED_FUNCTIONAL_PROOF_PENDING',
                       metadata_names_present=confirmed, writes_complete=True)
        emit(receipt)
        return receipt
    except Exception:
        receipt.update(state='STOP_WRITES_READ_ONLY_RECONCILE' if stage != 'PREFLIGHT' else 'PREFLIGHT_DENIED',
                       mutation_stage=stage, metadata_names_present=confirmed, writes_complete=False)
        emit(receipt)
        raise Stop(receipt['state']) from None

def entry(mode):
    try:
        _, _, _, prefix = validate_context(mode, os.environ)
        token = os.environ.get('ADMIN_INSTALLATION_TOKEN')
        if not token:
            raise Stop('TOKEN_MISSING')
        perform(mode, os.environ, API(token, prefix))
    except Exception:
        print('FIXED_BINDING_STOP_NO_RETRY')
        return 1
    return 0
