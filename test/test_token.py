"""Token storage tests"""

import os
from tempfile import TemporaryFile, NamedTemporaryFile
import unittest
from hmrc.auth.token import HmrcTokenStorage, HmrcTokenFileStorage


class TokenStorageTest(unittest.TestCase):
    """Token storage tests"""

    Storage = HmrcTokenStorage

    def storage(self, *args, **kwargs):
        """Construct token storage"""
        return self.Storage(*args, **kwargs)

    def test_explicit_save_reload(self):
        """Test explicit save and reload"""
        storage = self.storage()
        storage.save({'access_token': '42'})
        self.assertEqual(storage.token['access_token'], '42')
        loaded = storage.load()
        self.assertIs(loaded, storage.token)
        self.assertEqual(storage.token['access_token'], '42')
        storage.close()

    def test_implicit_save_reload(self):
        """Test implicit save and reload"""
        storage = self.storage({'access_token': '54'})
        self.assertEqual(storage.token['access_token'], '54')
        storage.save()
        self.assertEqual(storage.token['access_token'], '54')
        loaded = storage.load()
        self.assertIs(loaded, storage.token)
        self.assertEqual(storage.token['access_token'], '54')
        storage.close()


class TokenFileStorageTest(TokenStorageTest):
    """Token file storage tests"""

    Storage = HmrcTokenFileStorage


class TokenExplicitFileStorageTest(TokenFileStorageTest):
    """Token file storage tests"""

    def setUp(self):
        self.file = TemporaryFile(mode='w+t')

    def storage(self, *args, **kwargs):
        return super().storage(*args, file=self.file, **kwargs)


class TokenNamedFileStorageTest(TokenFileStorageTest):
    """Token named file storage tests"""

    @classmethod
    def setUpClass(cls):
        file = NamedTemporaryFile(mode='w+t', delete=False)
        file.close()
        cls.path = file.name

    @classmethod
    def tearDownClass(cls):
        os.unlink(cls.path)

    def storage(self, *args, **kwargs):
        return super().storage(*args, path=self.path, **kwargs)

    def test_reload_from_file(self):
        """Test ability to reload after closing and reopening the file"""
        first = self.storage({'access_token': 'mice'})
        first.save()
        first.close()
        second = self.storage()
        self.assertEqual(second.token['access_token'], 'mice')
        second.close()