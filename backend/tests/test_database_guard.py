"""URL checks only: these tests never open a database or import the application."""
import unittest
from types import SimpleNamespace

import pytest

from _database_guard import assert_isolated_test_database


@pytest.fixture(autouse=True)
def _banco_limpo():
    yield  # Deliberately overrides the integration suite's destructive fixture.


class DatabaseGuardTests(unittest.TestCase):
    def setUp(self):
        self.env = {'ENVIRONMENT': 'test', 'POSTGRES_HOST': 'localhost', 'POSTGRES_PORT': '5432',
                    'POSTGRES_USER': 'meucardio_test', 'POSTGRES_DB': 'meucardio_test'}
        self.url = 'postgresql+psycopg://meucardio_test:unused@localhost:5432/meucardio_test'

    def test_exact_ci_database_is_accepted(self):
        assert_isolated_test_database(self.url, self.env)
        assert_isolated_test_database(SimpleNamespace(drivername='postgresql+psycopg', host='localhost',
            port=5432, database='meucardio_test', username='meucardio_test', query={}), self.env)

    def test_previous_explicit_local_namespaces_remain_guarded(self):
        for database in ('corvia_editorial_20260910_qa', 'corvia_clinical_approval_qa'):
            assert_isolated_test_database(self.url.rsplit('/', 1)[0] + '/' + database,
                {**self.env, 'POSTGRES_DB': database})

    def test_production_remote_driver_and_query_overrides_are_rejected(self):
        candidates = (
            self.url.rsplit('/', 1)[0] + '/meucardio',
            self.url.rsplit('/', 1)[0] + '/another_test',
            self.url.replace('@localhost', '@database.example.test'),
            self.url.replace('postgresql+psycopg', 'sqlite'),
            self.url + '?host=production.example.test',
            self.url.replace('meucardio_test:unused', 'application:unused'),
        )
        for candidate in candidates:
            with self.subTest(candidate=candidate), self.assertRaises(AssertionError):
                assert_isolated_test_database(candidate, self.env)

    def test_declared_test_environment_cannot_mask_a_different_effective_url(self):
        for key, value in (('ENVIRONMENT', 'production'), ('ENVIRONMENT', ''), ('POSTGRES_DB', 'meucardio'),
                           ('POSTGRES_HOST', '127.0.0.1'), ('POSTGRES_USER', 'postgres'), ('POSTGRES_PORT', '5433')):
            with self.subTest(key=key), self.assertRaises(AssertionError):
                assert_isolated_test_database(self.url, {**self.env, key: value})


if __name__ == '__main__':
    unittest.main()
