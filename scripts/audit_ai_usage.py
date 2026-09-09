#!/usr/bin/env python3
"""Read-only aggregate AI usage audit; never returns clinical text or user IDs.

Run in the backend environment. No provider API call is made. Counts represent
retained records, not necessarily complete provider billing.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve()
backend = HERE.parent.parent / "backend"
if backend.is_dir():
    sys.path.insert(0, str(backend))

from sqlalchemy import text
from app.core.config import settings
from app.core.db import SessionLocal

SAFE_SETTINGS = (
    "ai_enabled", "ai_provider", "ai_embedding_provider", "ai_daily_limit",
    "ai_max_output_tokens", "ai_top_k", "ai_max_context_chars",
    "ai_assistant_tools_enabled", "ai_clinical_multimodal_enabled",
    "ai_ecg_model", "ai_cardiovascular_exam_model",
    "openai_model", "openai_embedding_model", "embedding_dim", "anthropic_model",
    "heart_team_enabled", "heart_team_clinical_model",
    "heart_team_max_output_tokens", "heart_team_source_limit",
    "heart_team_cache_ttl_seconds", "heart_team_monthly_cost_ceiling_micros",
    "heart_team_daily_case_limit", "heart_team_monthly_case_limit",
    "heart_team_input_token_cost_micros", "heart_team_output_token_cost_micros",
    "whatsapp_enabled", "whatsapp_daily_command_limit",
    "whatsapp_monthly_command_limit", "whatsapp_monthly_cost_ceiling_microunits",
    "whatsapp_meta_message_cost_microunits", "whatsapp_transcription_cost_microunits",
    "whatsapp_scientific_summary_cost_microunits", "whatsapp_transcription_model",
    "subscriptions_enabled",
)

# Each tuple contains a fixed table, grouping columns, additive numeric columns.
SPECS = {
    "chat": ("ai_messages", ("modelo",), ("tokens_entrada", "tokens_saida")),
    "round": ("patient_ai_suggestions", ("model",), ()),
    "ecg_and_quick_exam": (
        "patient_clinical_ai_suggestions", ("mode", "provider", "model", "status"),
        ("tokens_input", "tokens_output"),
    ),
    "longitudinal_multimodal": (
        "patient_multimodal_ai_suggestions", ("provider", "model", "status"),
        ("tokens_input", "tokens_output"),
    ),
    "heart_team_cases": (
        "heart_team_cases", ("status",),
        ("tokens_input", "tokens_output", "estimated_cost_micros", "reserved_cost_micros"),
    ),
    "heart_team_ledger": (
        "heart_team_cost_ledger", ("phase", "model_name"),
        ("tokens_input", "tokens_output", "actual_micros", "reserved_micros"),
    ),
    "whatsapp": (
        "whatsapp_usage_metrics", ("operation", "provider", "model", "success"),
        ("input_units", "output_units", "estimated_cost_microunits"),
    ),
    "whatsapp_messages": (
        "whatsapp_messages", ("direction", "message_type", "status"),
        ("estimated_cost_microunits",),
    ),
    "whatsapp_outbox": (
        "whatsapp_outbound_outbox", ("status",),
        ("estimated_cost_microunits",),
    ),
    "private_scientific_documents": (
        "scientific_user_documents", ("analysis_status",), (),
    ),
}
AUDIT_ACTIONS = (
    "perguntar", "ai_assist_round", "ai_ecg_transfer_attempt",
    "ai_clinical_exam_transfer_attempt", "ai_ecg_generated",
    "analyze_private_scientific_document",
    "analyze_private_scientific_document_failed",
)

def json_default(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return int(value) if value == value.to_integral_value() else float(value)
    raise TypeError(type(value).__name__)

def table_columns(db, name):
    return set(db.execute(text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema = 'public' AND table_name = :name"
    ), {"name": name}).scalars())

def collect(db, *, days=30):
    if not 1 <= days <= 366:
        raise ValueError("days must be between 1 and 366")
    db.execute(text("SET TRANSACTION READ ONLY"))
    db.execute(text("SET LOCAL statement_timeout = '20s'"))
    db.execute(text("SET LOCAL TIME ZONE 'UTC'"))
    result = {
        "generated_at": db.execute(text("SELECT now()")).scalar_one(),
        "period_days": days,
        "period_timezone": "UTC",
        "scope": "Aggregate retained records only; no clinical text, personal identifiers, or paid calls.",
        "runtime_settings": {name: getattr(settings, name, None) for name in SAFE_SETTINGS},
        "groups": {},
        "limitations": [
            "Counts and token sums cover retained local records, not the full provider invoice.",
            "Deleted chat conversations also delete usage-bearing messages.",
            "Embedding provider usage is not persisted; it cannot be priced from chunk counts.",
            "Round and private scientific document processing discard provider token usage.",
            "Web-search tool charges and some failures after provider consumption are not captured.",
            "Heart Team case totals and ledger totals overlap and must not be added together.",
            "WhatsApp message/outbox/usage records can overlap; totals are not an invoice.",
            "Configured micro-unit tariffs are estimates with no currency field; not verified provider prices.",
            "Private document created_at is upload time; audit actions count processing attempts separately.",
            "Technical synthetic probes may be included; no user identifiers were accessed to classify them.",
        ],
    }
    for key, (table, group_cols, numeric_cols) in SPECS.items():
        available = table_columns(db, table)
        needed = {"created_at", *group_cols, *numeric_cols}
        if key == "chat":
            needed.add("papel")
        if not needed <= available:
            result["groups"][key] = {"unavailable": True, "missing_columns": sorted(needed - available)}
            continue
        # Identifiers originate exclusively in the hard-coded SPECS allowlist.
        fields = ["date(created_at) AS day", *group_cols, "count(*) AS records"]
        fields += [f"coalesce(sum({col}), 0) AS {col}" for col in numeric_cols]
        conditions = ["created_at >= now() - (:days * interval '1 day')"]
        if key == "chat":
            conditions.append("papel = 'assistant'")
        grouping = ", ".join(["date(created_at)", *group_cols])
        query = (
            f"SELECT {', '.join(fields)} FROM {table} "
            f"WHERE {' AND '.join(conditions)} GROUP BY {grouping} ORDER BY {grouping}"
        )
        rows = [dict(row) for row in db.execute(text(query), {"days": days}).mappings()]
        result["groups"][key] = {
            "records": sum(row["records"] for row in rows),
            "sums": {col: sum(row[col] for row in rows) for col in numeric_cols},
            "by_day_and_dimensions": rows,
        }
    conversation_cols = table_columns(db, "ai_conversations")
    message_cols = table_columns(db, "ai_messages")
    if {"id", "modo"} <= conversation_cols and {
        "conversation_id", "modelo", "papel", "created_at",
        "tokens_entrada", "tokens_saida",
    } <= message_cols:
        rows = db.execute(text(
            "SELECT date(m.created_at) AS day, c.modo AS mode, m.modelo AS model, "
            "count(*) AS records, coalesce(sum(m.tokens_entrada),0) AS tokens_input, "
            "coalesce(sum(m.tokens_saida),0) AS tokens_output "
            "FROM ai_messages m JOIN ai_conversations c ON c.id=m.conversation_id "
            "WHERE m.papel='assistant' "
            "AND m.created_at >= now() - (:days * interval '1 day') "
            "GROUP BY date(m.created_at), c.modo, m.modelo "
            "ORDER BY date(m.created_at), c.modo, m.modelo"
        ), {"days": days}).mappings()
        result["chat_by_mode_model"] = [dict(row) for row in rows]
    audit_columns = table_columns(db, "audit_logs")
    if {"created_at", "action"} <= audit_columns:
        rows = db.execute(text(
            "SELECT date(created_at) AS day, action, count(*) AS records "
            "FROM audit_logs WHERE created_at >= now() - (:days * interval '1 day') "
            "AND action = ANY(:actions) GROUP BY date(created_at), action "
            "ORDER BY date(created_at), action"
        ), {"days": days, "actions": list(AUDIT_ACTIONS)}).mappings()
        result["audit_event_counts"] = [dict(row) for row in rows]
    else:
        result["audit_event_counts"] = {"unavailable": True}
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    with SessionLocal() as db:
        report = collect(db, days=args.days)
        db.rollback()
    rendered = json.dumps(report, ensure_ascii=False, indent=2, default=json_default)
    if args.output:
        args.output.write_text(rendered + "\n")
    else:
        print(rendered)

if __name__ == "__main__":
    main()
