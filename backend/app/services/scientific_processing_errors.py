"""Bounded scientific-worker diagnostics: never persist exception text or URLs."""
PROVIDER_CODES = frozenset({
    'insufficient_quota', 'rate_limit_exceeded', 'server_error', 'invalid_api_key',
    'permission_denied', 'model_not_found', 'invalid_request_error',
    'context_length_exceeded', 'billing_hard_limit_reached',
    'organization_deactivated', 'billing_not_active',
})
ERROR_TYPES = frozenset({
    'HTTPStatusError', 'RateLimitError', 'APIStatusError', 'AuthenticationError',
    'PermissionDeniedError', 'BadRequestError', 'InternalServerError',
    'ReadTimeout', 'ConnectTimeout', 'WriteTimeout', 'PoolTimeout', 'ConnectError',
    'ReadError', 'RemoteProtocolError', 'APITimeoutError', 'APIConnectionError',
    'TimeoutError', 'ConnectionError', 'JSONDecodeError', 'ParseError',
    'ValueError', 'TypeError', 'KeyError', 'OSError', 'FileNotFoundError',
    'PermissionError', 'RuntimeError', 'AIUsageError', 'AIWalletError',
    'SourceUnavailable', 'InvalidToken',
})
# Matches the existing metering policy. 402/409/5xx do not prove zero billing.
NONBILLED_REJECTIONS = frozenset({400, 401, 403, 404, 422, 429})


def http_status(error):
    for value in (getattr(error, 'status_code', None),
                  getattr(getattr(error, 'response', None), 'status_code', None)):
        if isinstance(value, int) and not isinstance(value, bool) and 100 <= value <= 599:
            return value
    return None


def safe_error_diagnostic(error):
    response = getattr(error, 'response', None)
    body = getattr(error, 'body', None)
    if not isinstance(body, dict) and response is not None:
        try:
            # Only parse the already buffered response, never read from a stream.
            if len(response.content) <= 16384:
                body = response.json()
        except Exception:
            body = None
    payload = body.get('error', body) if isinstance(body, dict) else {}
    code = payload.get('code') if isinstance(payload, dict) else None
    if not isinstance(code, str) or code not in PROVIDER_CODES:
        code = getattr(error, 'code', None)
    if not isinstance(code, str) or code not in PROVIDER_CODES:
        code = None
    name = type(error).__name__
    return {'http_status': http_status(error), 'provider_code': code,
            'error_type': name if name in ERROR_TYPES else 'OtherError'}


def failure_status(*, processing_ai, financial_state, status, budget_error=False):
    """A current HTTP rejection never erases earlier possible charges."""
    if processing_ai:
        if financial_state not in {'settled_zero', 'not_started'}:
            return 'cost_unknown'
        if budget_error or status in {401, 403, 429}:
            return 'budget_wait'
    return 'failed'
