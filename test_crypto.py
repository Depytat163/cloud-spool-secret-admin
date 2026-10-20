import unittest
from nacl.public import PrivateKey, SealedBox
from nacl.exceptions import CryptoError

class EncryptionTests(unittest.TestCase):
    def test_round_trip(self):
        key = PrivateKey.generate()
        value = b'NON_AUTHORIZING_DUMMY'
        encrypted = SealedBox(key.public_key).encrypt(value)
        self.assertNotIn(value, encrypted)
        self.assertEqual(SealedBox(key).decrypt(encrypted), value)

    def test_wrong_target_key_denied(self):
        first, second = PrivateKey.generate(), PrivateKey.generate()
        encrypted = SealedBox(first.public_key).encrypt(b'NON_AUTHORIZING_DUMMY')
        with self.assertRaises(CryptoError):
            SealedBox(second).decrypt(encrypted)
