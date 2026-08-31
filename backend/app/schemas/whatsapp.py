from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field, field_validator

PERMISSION_KEYS = frozenset({"read_agenda","read_tasks","search_science","create_reminder","create_appointment","create_draft","external_communication","heart_team_draft"})
def _permissions(v):
    if set(v or {}) - PERMISSION_KEYS: raise ValueError("Permissão desconhecida")
    return v or {}
class PairingCreate(BaseModel):
    retention_days:int=Field(30,ge=1,le=180); permissions:dict[str,bool]=Field(default_factory=dict); pin:str|None=Field(None,min_length=6,max_length=32); consent:bool
    @field_validator("permissions")
    @classmethod
    def valid(cls,v): return _permissions(v)
class PairingComplete(BaseModel): code:str=Field(pattern=r"^\d{8}$"); phone:str=Field(min_length=8,max_length=30)
class LinkUpdate(BaseModel):
    retention_days:int|None=Field(None,ge=1,le=180); permissions:dict[str,bool]|None=None; pin:str|None=Field(None,min_length=6,max_length=32)
    @field_validator("permissions")
    @classmethod
    def valid(cls,v): return None if v is None else _permissions(v)
class CommandCreate(BaseModel):
    text:str=Field(min_length=1,max_length=30000); idempotency_key:str=Field(min_length=8,max_length=180); source:Literal["app","sandbox"]="app"; kind:str|None=None; arguments:dict[str,Any]=Field(default_factory=dict)
class CommandConfirm(BaseModel): token:str=Field(min_length=16,max_length=256); pin:str|None=Field(None,min_length=6,max_length=32)
class CommandUndo(BaseModel): token:str=Field(min_length=16,max_length=256)
class RetentionDeleteIn(BaseModel): confirm:bool
class TranscriptReview(BaseModel): text:str=Field(min_length=1,max_length=8000); confirmed:bool
class PIIReview(BaseModel): confirmed:bool; anonymize:bool=True
class MediaReview(BaseModel): confirmed:bool; action:Literal["store_only","summarize","heart_team","reject"]="store_only"; contains_no_identifiers:bool=False; question:str|None=None
class SandboxInbound(BaseModel):
    phone:str; message_id:str; message_type:Literal["text","audio","image","document","interactive"]="text"; text:str|None=None; media_id:str|None=None; mime_type:str|None=None; interactive:dict[str,Any]|None=None; timestamp:datetime|None=None
    @field_validator("phone")
    @classmethod
    def phone_digits(cls,v):
        d="".join(c for c in v if c.isdigit())
        if not 8<=len(d)<=15: raise ValueError("Telefone inválido")
        return d
class RecipientOptInCreate(BaseModel): phone:str; purpose:str=Field(min_length=3,max_length=160); source:Literal["written","web_form","recorded_call","in_person"]; confirm:bool
class RecipientOptOutCreate(BaseModel): phone:str; confirm:bool
class CommandOut(BaseModel):
    id:int; status:str; kind:str; level:int; requires_confirmation:bool=False; requires_in_app:bool=False; confirmation_token:str|None=None; undo_token:str|None=None; message:str; result:dict[str,Any]|None=None
