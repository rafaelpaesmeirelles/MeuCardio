"""Provider receipts, quotes and uncertain usage; no network or database."""
from types import SimpleNamespace
from unittest.mock import Mock
import pytest
from app.services import ai_wallet
from app.services.ia import usage_control as u

@pytest.fixture(autouse=True)
def _banco_limpo():
    yield

@pytest.fixture(autouse=True)
def wallet(monkeypatch):
    fake = SimpleNamespace(reserve=Mock(return_value={"created": True}), settle=Mock(), mark_unknown=Mock())
    for name, value in vars(fake).items():
        monkeypatch.setattr(ai_wallet, name, value)
    monkeypatch.setattr(u.settings, 'ai_billing_usd_brl', 6)
    monkeypatch.setattr(u.settings, 'ai_model_prices_json', '{}')
    return fake

def request(model='gpt-5.6-sol', **kwargs):
    return dict(model=model, input='x' * 10000, max_output_tokens=2000, **kwargs)

@pytest.mark.parametrize('model,expected', [('gpt-5.6-sol', 13440), ('gpt-4o-mini', 666)])
def test_openai_cached_receipt_settles_discount_and_raw_tokens(wallet, model, expected):
    # 1000 input: 600 hit; Sol additionally 200 written. 10 output.
    details = {'cached_tokens': 600}
    if model == 'gpt-5.6-sol':
        details['cache_write_tokens'] = 200
    with u.ai_usage_scope(7):
        with u.paid_request('openai', request(model)) as meter:
            meter.finish({'input_tokens':1000, 'output_tokens':10, 'input_tokens_details':details})
    assert wallet.settle.call_args.kwargs['actual_cost_micros'] == expected
    assert wallet.settle.call_args.kwargs['tokens_input'] == 1000

@pytest.mark.parametrize('breakdown,expected', [({'ephemeral_5m_input_tokens':200,'ephemeral_1h_input_tokens':0},9120), ({'ephemeral_5m_input_tokens':0,'ephemeral_1h_input_tokens':200},10920), ({'ephemeral_5m_input_tokens':100,'ephemeral_1h_input_tokens':100},10020)])
def test_claude_write_ttl_and_read_categories(wallet, breakdown, expected):
    # Ordinary400 + write200 + read600, and10 output; $2/$10, FX6.
    with u.ai_usage_scope(7):
        with u.paid_request('anthropic', request('claude-sonnet-5')) as meter:
            meter.finish(dict(input_tokens=400, output_tokens=10, cache_creation_input_tokens=200,
                              cache_read_input_tokens=600, cache_creation=breakdown))
    assert wallet.settle.call_args.kwargs['actual_cost_micros'] == expected
    assert wallet.settle.call_args.kwargs['tokens_input'] == 1200

@pytest.mark.parametrize('ttl,expected', [('5m',3000),('1h',4800)])
def test_unambiguous_request_ttl_can_resolve_older_receipt(wallet, ttl, expected):
    with u.ai_usage_scope(7):
        with u.paid_request('anthropic',request('claude-sonnet-5',cache_control={'type':'ephemeral','ttl':ttl})) as meter:
            meter.finish(dict(input_tokens=0, output_tokens=0, cache_creation_input_tokens=200))
    assert wallet.settle.call_args.kwargs['actual_cost_micros'] == expected

@pytest.mark.parametrize('receipt', [
    {'input_tokens':10,'output_tokens':1,'cache_creation_input_tokens':200},
    {'input_tokens':10,'output_tokens':1,'cache_creation_input_tokens':200,'cache_creation':{'ephemeral_5m_input_tokens':199}},
    {'input_tokens':-1,'output_tokens':1},
    {'input_tokens':1.5,'output_tokens':1},
])
def test_ambiguous_usage_retains_reservation_and_blocks_next_call(wallet, receipt):
    with u.ai_usage_scope(7) as scope:
        with pytest.raises(u.AIUsageError):
            with u.paid_request('anthropic',request('claude-sonnet-5')) as meter:
                meter.finish(receipt)
        assert scope.unknown
        with pytest.raises(u.AIUsageError):
            with u.paid_request('anthropic',request('claude-sonnet-5')):
                pytest.fail('must not reach SDK')
    wallet.settle.assert_not_called()
    wallet.mark_unknown.assert_called_once()

@pytest.mark.parametrize('details', [{'cached_tokens':1001},{'cache_write_tokens':-1},'invalid receipt'])
def test_invalid_openai_cache_receipt_is_not_settled(wallet, details):
    with pytest.raises(u.AIUsageError), u.ai_usage_scope(7):
        with u.paid_request('openai',request()) as meter:
            meter.finish(dict(input_tokens=1000,output_tokens=10,input_tokens_details=details))
    wallet.settle.assert_not_called()
    wallet.mark_unknown.assert_called_once()

def test_long_context_threshold_uses_raw_tokens():
    assert u.cost_micros('gpt-5.6-sol',272000,100,cache_write_tokens=272000) == 8172000
    assert u.cost_micros('gpt-5.6-sol',272001,100,cache_write_tokens=272001) == 16338060

@pytest.mark.parametrize('key',['max_tokens','max_completion_tokens','max_output_tokens'])
def test_round_quote_includes_output_limit_and_reprices_crossing_threshold(monkeypatch,key):
    monkeypatch.setattr(u.settings,'ai_journey_budgets_json','{"clinical_ai":100000000}')
    monkeypatch.setattr(u,'input_token_bound',lambda *args:270000-256)
    with u.quote_scope(7,'clinical_ai'):
        amount=u.plan_rounds('openai',{'model':'gpt-5.6-sol',key:2000},2,tool_result_bytes=20000)
    # round1:270k input at write$5 +2k output$20; round2:293024 at$10 +2k at$30
    assert amount == 26281440

def test_reservation_covers_cache_writes_and_preserves_ceiling(wallet):
    req=request()
    estimate=u.estimate_request('openai',req)
    bound=u.input_token_bound(req,req['model'])+256
    assert estimate == u.cost_micros(req['model'],bound,2000,cache_write_tokens=bound)
    with pytest.raises(u.AIUsageError),u.ai_usage_scope(7):
        with u.paid_request('openai',request(input_extra='x'*500000)):
            pytest.fail('over-budget SDK call')
    wallet.reserve.assert_not_called()

def test_nullable_json_schema_can_be_estimated():
    assert u.estimate_request('openai',request(text={'format':{'schema':{'type':['string','null']}}})) > 0

@pytest.mark.parametrize('model',['gpt-4o-mini-transcribe','gpt-4o-transcribe'])
def test_transcription_quotes_documented_output_limit_and_settles_tokens(monkeypatch,wallet,model):
    monkeypatch.setattr(u,'audio_duration',lambda *args:10)
    result=SimpleNamespace(usage={'input_tokens':100,'output_tokens':20})
    create=Mock(return_value=result)
    client=SimpleNamespace(audio=SimpleNamespace(transcriptions=SimpleNamespace(create=create)))
    with u.ai_usage_scope(7,feature='whatsapp_ai'):
        assert u.metered_transcription(client,model=model,content=b'audio',filename='audio.ogg',media_type='audio/ogg') is result
    expected=u.estimate_request('openai',{'model':model,'input':'x'*2024,'max_output_tokens':2000})
    assert wallet.reserve.call_args.kwargs['max_cost_micros']==expected
    assert wallet.settle.call_args.kwargs['actual_cost_micros']==u.cost_micros(model,100,20)
    assert set(create.call_args.kwargs)=={'model','file'}


def test_large_heart_team_plan_still_requires_wallet_balance(wallet):
    # Raising a technical journey ceiling never grants prepaid user credit.
    req = {'model':'gpt-5.6-sol','input':'x'*300000,'max_output_tokens':8192}
    assert 10_000_000 < u.estimate_request('openai',req) < 100_000_000
    wallet.reserve.side_effect = u.AIUsageError('Saldo insuficiente',409)
    with pytest.raises(u.AIUsageError),u.ai_usage_scope(7,feature='heart_team'):
        with u.paid_request('openai',req):
            pytest.fail('Insufficient balance must stop before provider egress')
    wallet.reserve.assert_called_once()
    wallet.settle.assert_not_called()
    wallet.mark_unknown.assert_not_called()
