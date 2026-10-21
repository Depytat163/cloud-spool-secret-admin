import unittest
import base64
from nacl.public import PrivateKey, SealedBox
from nacl.exceptions import CryptoError
from fixed_binding import encrypt

class EncryptionTests(unittest.TestCase):
    def test_round_trip(self):
        key = PrivateKey.generate()
        value = b'NON_AUTHORIZING_DUMMY'
        encrypted = base64.b64decode(encrypt(value, base64.b64encode(bytes(key.public_key)).decode()))
        self.assertNotIn(value, encrypted)
        self.assertEqual(SealedBox(key).decrypt(encrypted), value)

    def test_wrong_target_key_denied(self):
        first, second = PrivateKey.generate(), PrivateKey.generate()
        encrypted = base64.b64decode(encrypt(b'NON_AUTHORIZING_DUMMY', base64.b64encode(bytes(first.public_key)).decode()))
        with self.assertRaises(CryptoError):
            SealedBox(second).decrypt(encrypted)
