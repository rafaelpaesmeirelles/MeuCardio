"""Pure, fail-closed guard for fixtures that commit or truncate test records."""
import os
import re
from urllib.parse import unquote, urlsplit


def _require(condition, message):
    # This protects destructive fixtures even when Python assertions are disabled.
    if not condition:
        raise AssertionError(message)


def assert_isolated_test_database(url, environment=None):
    env = os.environ if environment is None else environment
    if isinstance(url, str):
        parsed = urlsplit(url)
        driver, host = parsed.scheme, parsed.hostname
        database, username = unquote(parsed.path.removeprefix('/')), unquote(parsed.username or '')
        port, query = parsed.port or 5432, parsed.query
    else:
        driver, host = url.drivername, url.host
        database, username = url.database, url.username
        port, query = url.port or 5432, url.query
    _require(env.get('ENVIRONMENT') == 'test', 'Database fixture requires ENVIRONMENT=test')
    _require(driver in {'postgresql', 'postgresql+psycopg', 'postgresql+psycopg2'}, 'Only PostgreSQL test fixtures are supported')
    _require(host in {'localhost', '127.0.0.1', '::1'}, 'Database fixture requires an explicit loopback host')
    _require(not query, 'Connection query overrides are not allowed in destructive fixtures')
    _require(database == 'meucardio_test' or re.fullmatch(
        r'(?:corvia_editorial_20260910_|corvia_clinical_approval_)[a-zA-Z0-9_]+', database or ''
    ), 'Database name is not an explicitly isolated test namespace')
    _require(username in {'meucardio_test', 'postgres'}, 'Database fixture requires an explicit local test role')
    _require(env.get('POSTGRES_DB') == database, 'Effective database differs from the declared test database')
    _require(env.get('POSTGRES_HOST') == host, 'Effective host differs from the declared test host')
    _require(env.get('POSTGRES_USER') == username, 'Effective role differs from the declared test role')
    _require(str(env.get('POSTGRES_PORT', '5432')) == str(port), 'Effective port differs from the declared test port')
