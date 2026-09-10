"""Internal preview guard; no production write is authorized by AI verification."""
from contextlib import contextmanager
from contextvars import ContextVar
_PREVIEW = ContextVar("clinical_change_preview", default=False)

@contextmanager
def preview_only():
    token = _PREVIEW.set(True)
    try:
        yield
    finally:
        _PREVIEW.reset(token)

def require_preview_session(db):
    if not _PREVIEW.get() or not getattr(db, "clinical_preview_only", False):
        raise PermissionError("Alterações clínicas exigem proposta exata aprovada pelo proprietário.")
