"""Focal worker error tests: no database connection or provider request."""
from contextlib import contextmanager
from types import SimpleNamespace
import hashlib
import httpx
import pytest
from app.services import scientific_publication_library as library
from app.services.scientific_processing_errors import safe_error_diagnostic, http_status


class FakeDB:
    def __init__(self, receipt=None):
        self.receipt, self.commits = receipt, 0
    def query(self, *args): return self
    def filter(self, *args): return self
    def populate_existing(self): return self
    def one_or_none(self): return self.receipt
    def commit(self): self.commits += 1


def asset():
    return SimpleNamespace(id=12, doi='10.1000/test', status='ai_processing', attempts=0, retry_at=None,
        progress={'active_operation_key': 'publication:test',
                  'completed_chunks': [{'index': 0, 'storage_key': 'previous-chunk'}]})


def receipt(**overrides):
    values = dict(state='settled', actual_cost_micros=0, tokens_input=0, tokens_output=0)
    values.update(overrides)
    return SimpleNamespace(**values)


def rejection(code='insufficient_quota', status=429):
    response = httpx.Response(status, json={'error': {'code': code,
        'message': 'PRIVATE patient / key / account / request content must not persist'}},
        request=httpx.Request('POST', library.translator.RESPONSES_URL))
    try: response.raise_for_status()
    except httpx.HTTPStatusError as error: return error
    raise AssertionError('Expected rejection')


@pytest.mark.parametrize('code', ['insufficient_quota', 'rate_limit_exceeded', None])
def test_httpx_429_zero_receipt_retries_without_discarding_previous_chunks(code):
    item, db = asset(), FakeDB(receipt())
    before = list(item.progress['completed_chunks'])
    result = library._record_failure(db, item, rejection(code))
    assert result['status'] == 'budget_wait'
    assert result['diagnostic']['http_status'] == 429
    assert result['diagnostic']['provider_code'] == code
    assert item.progress['retry_generation'] == 1
    assert item.progress['completed_chunks'] == before
    assert 3500 < (item.retry_at - library.now()).total_seconds() <= 3600
    assert db.receipt.state == 'settled' and db.commits == 1
    assert 'PRIVATE' not in str(item.progress) and 'secret' not in str(item.progress)


def test_sdk_status_and_untrusted_diagnostic_fields():
    class RateLimitError(Exception): pass
    error = RateLimitError('secret')
    error.status_code = 429
    error.body = {'code': 'rate_limit_exceeded', 'message': 'secret'}
    assert http_status(error) == 429
    assert safe_error_diagnostic(error) == {
        'http_status': 429, 'provider_code': 'rate_limit_exceeded', 'error_type': 'RateLimitError'}
    error.body = {'error': {'code': 'patient@example.com'}}
    assert safe_error_diagnostic(error)['provider_code'] is None


@pytest.mark.parametrize('prior', [receipt(state='unknown'), receipt(actual_cost_micros=12), receipt(tokens_input=1)])
def test_rejection_never_resets_prior_charge_or_uncertain_operation(prior):
    item = asset()
    result = library._record_failure(FakeDB(prior), item, rejection())
    assert result['status'] == 'cost_unknown'
    assert 'retry_generation' not in item.progress
    assert item.retry_at is None
    assert item.progress['completed_chunks'][0]['storage_key'] == 'previous-chunk'


@pytest.mark.parametrize('local_status', [403, 409])
def test_zero_receipt_without_current_http_rejection_is_not_retry_proof(local_status):
    from app.services.ia.usage_control import AIUsageError
    item = asset()
    result = library._record_failure(FakeDB(receipt()), item, AIUsageError('Existing operation', local_status))
    assert result['status'] == 'cost_unknown'
    assert 'retry_generation' not in item.progress


def test_source_failure_retains_safe_type_and_existing_24h_backoff():
    item = asset(); item.status = 'pending'
    result = library._record_failure(FakeDB(), item, httpx.ReadTimeout('private-source-url'))
    assert result['status'] == 'failed'
    assert result['diagnostic']['error_type'] == 'ReadTimeout'
    assert result['diagnostic']['phase'] == 'source_processing'
    assert 86300 < (item.retry_at - library.now()).total_seconds() <= 86400
    assert 'private-source-url' not in str(item.progress)


def test_safe_retry_uses_new_key_for_same_chunk_and_keeps_completed_work(monkeypatch):
    item = asset()
    db = FakeDB(receipt())
    library._record_failure(db, item, rejection())
    item.original_storage_key = 'original'; item.source_sha256 = hashlib.sha256(b'xml').hexdigest()
    monkeypatch.setattr(library.cofre, 'ler', lambda *a, **k: b'xml')
    monkeypatch.setattr(library, 'parse_fulltext', lambda *a: {'text': 'article'})
    monkeypatch.setattr(library, '_segments', lambda *a: ['first part', 'second part'])
    monkeypatch.setattr(library, '_request_chunk', lambda text: {'model': 'test-model', 'input': text})
    monkeypatch.setattr(library, 'plan_requests', lambda *a: None)
    observed = []
    @contextmanager
    def scope(*a, **k):
        current = SimpleNamespace(operation_key=None)
        yield current
    monkeypatch.setattr(library, 'ai_usage_scope', scope)
    def refuse(request):
        observed.append((item.progress['active_operation_key'], request['input']))
        raise rejection()
    monkeypatch.setattr(library.translator, '_post_response', refuse)
    with pytest.raises(httpx.HTTPStatusError): library._process(db, item)
    assert observed[0][0].endswith(':retry:1')
    assert observed[0][1] == 'second part'
    assert item.progress['completed_chunks'] == [{'index': 0, 'storage_key': 'previous-chunk'}]
