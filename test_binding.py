import contextlib
import io
import unittest
from fixed_binding import API, MODES, NAMES, Stop, perform, validate_context

class FakeAPI:
    def __init__(self, mode='seed', existing=None, fail=None):
        self.mode, self.existing, self.fail = mode, existing, fail
        self.calls, self.writes = [], []

    def call(self, method, path, body=None, missing=False):
        self.calls.append((method, path))
        _, repo, ident, prefix = MODES[self.mode]
        if path == '/installation/repositories':
            return {'total_count': 1, 'repositories': [{'id': ident, 'full_name': repo}]}
        name = path.rsplit('/', 1)[-1]
        if method == 'PUT':
            self.writes.append(name)
            if self.fail == name: raise RuntimeError('MUST_NEVER_LOG_SENTINEL_VALUE')
            return {}
        if name == 'public-key': return {'key': 'DUMMY_PUBLIC_KEY', 'key_id': 'dummy-id'}
        if name in self.writes or name == self.existing: return {'name': name}
        return None

def environment(mode='seed'):
    return {'GITHUB_REPOSITORY': MODES[mode][0], 'GITHUB_REF': 'refs/heads/main',
            'GITHUB_EVENT_NAME': 'workflow_dispatch', 'GITHUB_RUN_ATTEMPT': '1',
            'GITHUB_RUN_ID': '12345', **{n: 'DUMMY_SENTINEL_VALUE' for n in NAMES}}

class BindingTests(unittest.TestCase):
    def test_seed_destination_environment_not_repository(self):
        api, receipts = FakeAPI(), []
        r = perform('seed', environment(), api, lambda *_: 'DUMMY_CIPHERTEXT', receipts.append)
        self.assertEqual(api.writes, list(NAMES))
        self.assertFalse(r['value_equivalence_proven'])
        self.assertIn('/environments/secret-administration/secrets/', api.calls[-1][1])

    def test_china_fixed_destination(self):
        api = FakeAPI('china')
        perform('china', environment('china'), api, lambda *_: 'DUMMY_CIPHER', lambda _: None)
        self.assertEqual(api.writes, list(NAMES))

    def test_any_existing_secret_stops_all_writes(self):
        for name in NAMES:
            api = FakeAPI(existing=name)
            with self.assertRaises(Stop):
                perform('seed', environment(), api, lambda *_: 'DUMMY', lambda _: None)
            self.assertEqual(api.writes, [])

    def test_missing_source_stops_before_mutation(self):
        env, api = environment(), FakeAPI()
        env.pop(NAMES[-1])
        with self.assertRaises(Stop):
            perform('seed', env, api, lambda *_: 'DUMMY', lambda _: None)
        self.assertEqual(api.writes, [])

    def test_wrong_contexts_and_reruns_denied(self):
        for key, value in [('GITHUB_REF', 'refs/heads/evil'), ('GITHUB_EVENT_NAME', 'pull_request'),
                           ('GITHUB_RUN_ATTEMPT', '2'), ('GITHUB_REPOSITORY', MODES['china'][0]),
                           ('ACTIONS_STEP_DEBUG', 'true')]:
            env = environment()
            env[key] = value
            with self.assertRaises(Stop): validate_context('seed', env)

    def test_wrong_token_scope_denied(self):
        api = FakeAPI('china')
        with self.assertRaises(Stop):
            perform('seed', environment(), api, lambda *_: 'DUMMY', lambda _: None)
        self.assertEqual(api.writes, [])

    def test_unknown_write_stops_no_retry_and_no_value_output(self):
        api, receipts, out = FakeAPI(fail=NAMES[1]), [], io.StringIO()
        with contextlib.redirect_stdout(out), self.assertRaises(Stop):
            perform('seed', environment(), api, lambda *_: 'DUMMY_CIPHERTEXT', receipts.append)
        self.assertEqual(api.writes, list(NAMES[:2]))
        self.assertEqual(receipts[0]['state'], 'STOP_WRITES_READ_ONLY_RECONCILE')
        self.assertEqual(receipts[0]['metadata_names_present'], [NAMES[0]])
        self.assertNotIn('SENTINEL', str(receipts) + out.getvalue())
        self.assertNotIn('DUMMY_CIPHERTEXT', str(receipts) + out.getvalue())

    def test_encrypt_all_before_first_write(self):
        api = FakeAPI()
        def broken_seal(*_): raise ValueError('DUMMY')
        with self.assertRaises(Stop):
            perform('seed', environment(), api, broken_seal, lambda _: None)
        self.assertEqual(api.writes, [])

    def test_unapproved_api_never_opens_network(self):
        api = API('DUMMY_TOKEN', MODES['seed'][3])
        for method, path in [('DELETE', MODES['seed'][3] + NAMES[0]),
                             ('PUT', MODES['china'][3] + NAMES[0]),
                             ('GET', '/repos/arbitrary/target')]:
            with self.assertRaises(Stop): api.call(method, path)

if __name__ == '__main__': unittest.main()
