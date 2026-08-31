import hashlib,hmac,json,re,secrets,threading,time
from collections import defaultdict,deque
from datetime import datetime,timezone
from redis import Redis
from redis.exceptions import RedisError
from app.core.config import settings
from app.core.runtime import ambiente_atual

def utcnow(): return datetime.now(timezone.utc)
def canonical_json(v): return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(",",":"),default=str)
def token_hash(v,purpose=""): return hashlib.sha256(f"{purpose}:{v}".encode()).hexdigest()
def random_token(): return secrets.token_urlsafe(32)
def random_pairing_code(): return f"{secrets.randbelow(100_000_000):08d}"
def phone_hash(phone): return token_hash("".join(c for c in phone if c.isdigit()),"phone")
def mask_phone(phone):
    d="".join(c for c in phone if c.isdigit()); return f"***{d[-4:]}"
def payload_hash(v): return hashlib.sha256(v).hexdigest()
def verify_meta_signature(body,signature):
    if not signature or not settings.whatsapp_meta_app_secret: return False
    expected="sha256="+hmac.new(settings.whatsapp_meta_app_secret.encode(),body,hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected,signature)
def detect_pii(text):
    found=[]
    if re.search(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b",text or ""): found.append("cpf")
    if re.search(r"(?<!\d)\+?\d[\d ()-]{7,20}\d(?!\d)",text or ""): found.append("telefone")
    if re.search(r"[\w.+-]+@[\w.-]+",text or ""): found.append("email")
    if re.search(r"\b(?:rua|avenida|av\.|alameda|travessa)\b",text or "",re.I): found.append("endereco")
    if re.search(r"\b\d{5}-?\d{3}\b",text or ""):found.append("cep")
    if re.search(r"\b(?:CNS|cart[aã]o\s+nacional\s+de\s+sa[uú]de)\s*[:#-]?\s*\d{15}\b|\b\d{15}\b",text or "",re.I):found.append("cns")
    if re.search(r"\bRG\s*[:#-]?\s*[A-Z0-9.-]{5,20}\b",text or "",re.I):found.append("rg")
    if re.search(r"\b(?:data\s+de\s+nascimento|nasc(?:imento)?\.?|dob)\s*[:#]?\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",text or "",re.I):found.append("data_nascimento")
    if re.search(r"\b(?:Nome|Paciente|Patient)\s*[:#-]?\s+[A-ZÀ-ÖØ-Ý][A-Za-zÀ-ÖØ-öø-ÿ'-]+(?:\s+[A-ZÀ-ÖØ-Ý][A-Za-zÀ-ÖØ-öø-ÿ'-]+){1,5}\b",text or "",re.I):found.append("nome")
    return found
def anonymize_text(text):
    kinds=detect_pii(text); out=text
    out=re.sub(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b","[CPF REMOVIDO]",out)
    out=re.sub(r"(?<!\d)\+?\d[\d ()-]{7,20}\d(?!\d)","[TELEFONE REMOVIDO]",out)
    out=re.sub(r"[\w.+-]+@[\w.-]+","[EMAIL REMOVIDO]",out)
    out=re.sub(r"\b(?:rua|avenida|av\.|alameda|travessa)\s+[^\n;]{2,160}","[ENDEREÇO REMOVIDO]",out,flags=re.I)
    out=re.sub(r"\b\d{5}-?\d{3}\b","[CEP REMOVIDO]",out)
    out=re.sub(r"\b(?:CNS|cart[aã]o\s+nacional\s+de\s+sa[uú]de)\s*[:#-]?\s*\d{15}\b|\b\d{15}\b","[CNS REMOVIDO]",out,flags=re.I)
    out=re.sub(r"\bRG\s*[:#-]?\s*[A-Z0-9.-]{5,20}\b","[RG REMOVIDO]",out,flags=re.I)
    out=re.sub(r"\b(?:data\s+de\s+nascimento|nasc(?:imento)?\.?|dob)\s*[:#]?\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b","[DATA REMOVIDA]",out,flags=re.I)
    out=re.sub(r"\b(?:Nome|Paciente|Patient)\s*[:#-]?\s+[A-ZÀ-ÖØ-Ý][A-Za-zÀ-ÖØ-öø-ÿ'-]+(?:\s+[A-ZÀ-ÖØ-Ý][A-Za-zÀ-ÖØ-öø-ÿ'-]+){1,5}\b","[NOME REMOVIDO]",out,flags=re.I)
    return out,kinds

_rate_lock=threading.Lock()
_rate_buckets=defaultdict(deque)
_redis_rate_client=None
def _distributed_rate(key,maximum,window_seconds):
    global _redis_rate_client
    if _redis_rate_client is None:_redis_rate_client=Redis.from_url(settings.redis_url,decode_responses=True,socket_connect_timeout=1,socket_timeout=1)
    hashed=token_hash(str(key),"rate");redis_key=f"corvia:whatsapp:rate:{hashed}"
    script="local n=redis.call('INCR',KEYS[1]); if n==1 then redis.call('EXPIRE',KEYS[1],ARGV[1]) end; return n"
    return int(_redis_rate_client.eval(script,1,redis_key,int(window_seconds)))<=maximum
def allow_rate(key,limit=None,window_seconds=60):
    """Distributed in production; local fallback is intentionally test/dev only."""
    maximum=int(limit or settings.whatsapp_rate_limit_per_minute);now=time.monotonic()
    try:return _distributed_rate(key,maximum,window_seconds)
    except RedisError:
        if ambiente_atual()=="production":return False
    with _rate_lock:
        bucket=_rate_buckets[token_hash(str(key),"rate")]
        while bucket and bucket[0]<=now-window_seconds:bucket.popleft()
        if len(bucket)>=maximum:return False
        bucket.append(now);return True

_UNDO_ID=re.compile(r"^corvia:undo:(\d+):([A-Za-z0-9_-]{16,256})$")
_STATIC_INTERACTIVE={
    "corvia:menu:agenda":"consultar agenda",
    "corvia:menu:tarefas":"consultar tarefas",
    "corvia:menu:status":"consultar status",
}
def trusted_interactive(reply_id):
    value=str(reply_id or "")
    match=_UNDO_ID.fullmatch(value)
    if match:return {"action":"undo","command_id":int(match.group(1)),"token":match.group(2)}
    if value in _STATIC_INTERACTIVE:return {"action":"text","text":_STATIC_INTERACTIVE[value]}
    return None
