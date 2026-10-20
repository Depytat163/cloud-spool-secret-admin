import copy
import json
import unittest
from pathlib import Path
from guard import Denied, validate, reconcile, lint_bundle, NAMES

class SecurityTests(unittest.TestCase):
    def setUp(self):
        self.registry = json.loads(Path('targets.json').read_text())
        self.request = {'operation_id': 'dummy-01', 'target_repository_id': 1419047642,
            'target_repository': 'Depytat163/China-Logistics-Simulation',
            'action': 'bind-existing-set', 'credential_set': 'existing-google-drive',
            'credential_version': 'existing-v1'}

    def test_approved_target(self):
        self.assertEqual(validate(self.request, self.registry), self.request)

    def test_unapproved_target(self):
        self.request['target_repository_id'] = 1
        with self.assertRaises(Denied): validate(self.request, self.registry)

    def test_wrong_name(self):
        self.request['secret_name'] = 'ARBITRARY'
        with self.assertRaises(Denied): validate(self.request, self.registry)

    def test_arbitrary_plaintext(self):
        self.request['value'] = 'DUMMY_NOT_A_REAL_CREDENTIAL'
        with self.assertRaises(Denied): validate(self.request, self.registry)

    def test_shell_payload(self):
        self.request['operation_id'] = '$(exit 1)'
        with self.assertRaises(Denied): validate(self.request, self.registry)

    def test_wrong_repository_name_with_approved_id(self):
        self.request['target_repository'] = 'https://example.invalid/target'
        with self.assertRaises(Denied): validate(self.request, self.registry)

    def test_boolean_is_not_repository_id(self):
        self.request['target_repository_id'] = True
        with self.assertRaises(Denied): validate(self.request, self.registry)

    def test_missing_fields(self):
        del self.request['credential_version']
        with self.assertRaises(Denied): validate(self.request, self.registry)

    def test_partial_write_never_resumes_automatically(self):
        result = reconcile({'state': 'PARTIAL'}, {NAMES[0]: {'updated_at': 'dummy'}})
        self.assertFalse(result['writes_allowed'])
        self.assertFalse(result['value_equivalence_proven'])

    def test_unknown_metadata_not_value_proof(self):
        result = reconcile({'state': 'UNKNOWN'}, {x: {} for x in NAMES})
        self.assertEqual(result['state'], 'RECONCILIATION_REQUIRED')
        self.assertFalse(result['writes_allowed'])

    def test_accepted_replay_does_not_write(self):
        self.assertFalse(reconcile({'state': 'ACCEPTED'}, {})['writes_allowed'])

    def test_bundle_lint(self):
        self.assertTrue(lint_bundle())

if __name__ == '__main__':
    unittest.main()
