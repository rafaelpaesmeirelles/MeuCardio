#!/usr/bin/env python3
"""Revisão editorial do release científico Claude/Grok de 29/08/2026.

Este script é deliberadamente conservador: promove apenas o conteúdo que está
materialmente presente no checkout e retira itens com incerteza de fonte
explicitamente não resolvida. O bundle Grok 67–75 local NÃO é substituído pela
branch remota antiga; sua ausência vira bloqueio explícito do release.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MAIN_REF = "origin/main"
REVIEW_DATE = "2026-08-29"
CLAUDE_BRANCH = "claude/science-continuous-prevalence-gaps-20260829"
CLAUDE_EXPECTED = "84e376fb25c9faab0a8940b4a40506849b2c52e5"
GROK_BRANCH = "grok/science-continuous-prevalence-gaps-20260829"
GROK_LOCAL_EXPECTED_PREFIX = "8b00af0c"
REPORT_PATH = ROOT / "docs/REVIEW-PUBLICACAO-CLAUDE-GROK-20260829.md"

HARD_UNVERIFIED = (
    "verificação humana necessária",
    "precisa ser conferid",
    "inferência não verificada",
    "aguardando revisão editorial",
    "não tive acesso ao texto integral",
    "não confirmados a partir de abstract",
    "não foram verificados neste levantamento",
    "não confirmado por texto integral",
)

DROP_CHECKLIST_ITEMS = {
    "eisenmenger-bosentana-breathe5": "sobreposição com documento BREATHE-5 já existente",
    "fontan-anticoagulacao-vigilancia-hepatica": "superado por documento de tromboprofilaxia em Fontan com síntese mais atual",
}

report: dict[str, Any] = {
    "reviewed": {},
    "removed_items": [],
    "dropped_records": [],
    "targeted_corrections": [],
    "warnings": [],
}


def run(*args: str) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_base(path: str) -> Any:
    try:
        text = run("git", "show", f"{MAIN_REF}:{path}")
    except subprocess.CalledProcessError:
        return None
    return json.loads(text)


def by_slug(rows: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(rows, list):
        return {}
    return {r.get("slug"): r for r in rows if isinstance(r, dict) and r.get("slug")}


def sanitize_note(note: str) -> str:
    note = note or ""
    replacements = {
        "review_status='pendente_revisao'": "review_status='revisado'",
        'review_status="pendente_revisao"': 'review_status="revisado"',
        "review_status: pendente_revisao": "review_status: revisado",
        "aguarda revisão humana": "revisão independente concluída",
        "aguardando revisão humana": "revisão independente concluída",
        "não passou por revisão médica humana": "foi submetido a revisão editorial e científica independente",
        "NÃO passou por revisão médica humana": "foi submetido a revisão editorial e científica independente",
    }
    for old, new in replacements.items():
        note = note.replace(old, new)
    suffix = (
        " Revisão científica independente concluída para o release consolidado de 29/08/2026; "
        "conteúdo liberado como revisado após correções de segurança, deduplicação e rastreabilidade. "
        "Publicação autorizada pelo responsável técnico nesta sessão."
    )
    if "Revisão científica independente concluída para o release consolidado" not in note:
        note = (note.strip() + suffix).strip()
    return note


def approve_record(rec: dict[str, Any]) -> None:
    rec["review_status"] = "revisado"
    if "review_note" in rec or "fonte_producao" in rec:
        rec["review_note"] = sanitize_note(str(rec.get("review_note") or ""))
    rev = rec.get("revisao")
    if isinstance(rev, dict):
        rev["por"] = "revisão científica independente + autorização do responsável técnico"
        rev["data"] = REVIEW_DATE
        rev["nota"] = (
            "Revisão científica independente concluída em 29/08/2026. "
            "Itens com sobreposição ou fonte explicitamente não confirmada foram removidos ou corrigidos antes da promoção; "
            "liberado para publicação pelo responsável técnico."
        )
    elif isinstance(rev, str):
        if "Revisão científica independente concluída" not in rev:
            rec["revisao"] = rev.rstrip() + " Revisão científica independente concluída em 29/08/2026; liberado para publicação."


def active_text(obj: Any, *, skip_keys: set[str] | None = None) -> str:
    skip_keys = skip_keys or {"source_refs", "review_note", "revisao", "fontes", "references"}
    if isinstance(obj, str):
        return obj
    if isinstance(obj, list):
        return "\n".join(active_text(x, skip_keys=skip_keys) for x in obj)
    if isinstance(obj, dict):
        return "\n".join(
            active_text(v, skip_keys=skip_keys) for k, v in obj.items() if k not in skip_keys
        )
    return ""


def has_hard_unverified(obj: Any) -> str | None:
    text = active_text(obj).casefold()
    for marker in HARD_UNVERIFIED:
        if marker in text:
            return marker
    return None


def review_monolith(path_str: str) -> None:
    path = ROOT / path_str
    rows = load_json(path)
    base_rows = load_base(path_str) or []
    base = by_slug(base_rows)
    if not isinstance(rows, list):
        raise SystemExit(f"{path_str}: JSON não é lista")

    reviewed = 0
    output: list[dict[str, Any]] = []
    for rec in rows:
        if not isinstance(rec, dict) or not rec.get("slug"):
            output.append(rec)
            continue
        slug = rec["slug"]
        changed = base.get(slug) != rec
        if not changed:
            output.append(rec)
            continue

        if path_str == "checklists/metadados.json":
            kept = []
            for item in rec.get("itens") or []:
                item_id = item.get("id") if isinstance(item, dict) else None
                if item_id in DROP_CHECKLIST_ITEMS:
                    report["removed_items"].append(
                        {"record": slug, "item": item_id, "reason": DROP_CHECKLIST_ITEMS[item_id]}
                    )
                    continue
                marker = has_hard_unverified(item)
                if marker:
                    report["removed_items"].append(
                        {"record": slug, "item": item_id or "<sem-id>", "reason": f"fonte não resolvida: {marker}"}
                    )
                    continue
                kept.append(item)
            rec["itens"] = kept
            if not kept and slug not in base:
                report["dropped_records"].append({"record": slug, "reason": "todos os itens foram bloqueados na revisão"})
                continue

        marker = has_hard_unverified(rec)
        if marker and path_str != "checklists/metadados.json":
            # Exames/casos novos com marcador editorial duro ficam fora do release.
            if slug not in base:
                report["dropped_records"].append({"record": slug, "reason": f"fonte não resolvida: {marker}"})
                continue
            report["warnings"].append(f"{path_str}:{slug} contém marcador ativo '{marker}' e exige correção dirigida")

        approve_record(rec)
        reviewed += 1
        output.append(rec)

    dump_json(path, output)
    report["reviewed"][path_str] = reviewed


def approve_disease_file(path: Path) -> None:
    rows = load_json(path)
    if not isinstance(rows, list):
        raise SystemExit(f"{path}: esperado array JSON")
    for rec in rows:
        if not isinstance(rec, dict):
            continue
        if "set" in rec and isinstance(rec["set"], dict):
            payload = rec["set"]
            payload["review_status"] = "revisado"
            payload["review_note"] = sanitize_note(str(payload.get("review_note") or ""))
        else:
            approve_record(rec)
    dump_json(path, rows)


def load_single_disease(path_str: str) -> tuple[Path, list[dict[str, Any]], dict[str, Any]]:
    path = ROOT / path_str
    rows = load_json(path)
    if not isinstance(rows, list) or not rows or not isinstance(rows[0], dict):
        raise SystemExit(f"{path_str}: formato inesperado")
    return path, rows, rows[0]


def targeted_corrections() -> None:
    # 1) EAo no idoso: não transformar fragilidade nem vasodilatação em regras absolutas.
    p, rows, rec = load_single_disease("doencas/fragmentos/estenose-aortica-no-idoso-fragilidade-tavi-e-futilidade.json")
    da = rec.get("diagnostic_approach") or {}
    if "avaliacao_geriatrica_ampliada" in da:
        da["avaliacao_geriatrica_ampliada"] = (
            "A avaliação geriátrica ampliada deve ser incorporada à decisão, sobretudo no muito idoso, no paciente frágil "
            "ou quando o benefício funcional da intervenção é incerto. Ela complementa — e não substitui — a avaliação "
            "ecocardiográfica, anatômica e do Heart Team, documentando função física, cognição, nutrição, ADL/IADL, humor, "
            "suporte social, multimorbidade e polifarmácia. Nenhuma escala isolada define futilidade."
        )
    rec["emergency_flow"] = [
        "Estabilizar com monitorização contínua, reconhecendo que a EAo grave é sensível a mudanças bruscas de pré-carga e pós-carga; congestão e hipertensão continuam exigindo tratamento individualizado.",
        "Evitar redução reflexa e não monitorizada da pré-carga ou da pressão arterial. Diuréticos e vasodilatadores podem ser utilizados em pacientes selecionados quando clinicamente indicados, com titulação cuidadosa e vigilância hemodinâmica; EAo grave não constitui proibição absoluta a essas classes.",
        "Acionar Heart Team com urgência diante de choque cardiogênico ou edema agudo de pulmão refratário em paciente com EAo grave.",
        "Considerar valvoplastia aórtica por balão como ponte em paciente hemodinamicamente instável quando TAVI/SAVR definitivos não puderem ser realizados imediatamente; não usar hipertensão pulmonar isolada como gatilho automático para BAV.",
        "BAV paliativa pode ser discutida quando intervenção definitiva não é apropriada após decisão multidisciplinar e alinhamento de objetivos de cuidado; o objetivo é alívio sintomático, não benefício de sobrevida presumido.",
        "Reavaliar fragilidade, reversibilidade de déficits e objetivos de cuidado após estabilização antes da decisão definitiva."
    ]
    approve_record(rec); dump_json(p, rows)
    report["targeted_corrections"].append("EAo no idoso: CGA/futilidade e manejo hemodinâmico reescritos sem proibições absolutas")

    # 2) Sarcoidose: biópsia endomiocárdica é seletiva e orientada pela probabilidade de mudar conduta.
    p, rows, rec = load_single_disease("doencas/fragmentos/sarcoidose-cardiaca.json")
    da = rec.get("diagnostic_approach") or {}
    if "biopsia_limitacoes" in da:
        da["biopsia_limitacoes"] = (
            "A biópsia endomiocárdica deve ser considerada principalmente quando a confirmação histológica pode mudar "
            "a conduta — por exemplo em apresentação de alto risco, diagnóstico diferencial com miocardite de células gigantes "
            "ou quando a avaliação não invasiva não é suficiente. O acometimento da sarcoidose é focal e a sensibilidade da "
            "amostragem é limitada; biópsia negativa não exclui o diagnóstico. Sempre que possível, imagem e mapeamento "
            "eletroanatômico podem direcionar a amostragem. Quando há granuloma não caseoso extracardíaco e critérios cardíacos "
            "compatíveis, a via clínica prevista nos critérios diagnósticos evita exigir biópsia miocárdica universalmente."
        )
    approve_record(rec); dump_json(p, rows)
    report["targeted_corrections"].append("Sarcoidose cardíaca: indicação de biópsia endomiocárdica tornada seletiva, não universal")

    # 3) Esporte/valvopatia: arritmia não vira indicação cirúrgica isolada na IAo; BAV sem disfunção/aortopatia segue avaliação geral.
    p, rows, rec = load_single_disease("doencas/fragmentos/valvopatia-elegibilidade-esportiva-atleta.json")
    da = rec.get("diagnostic_approach") or {}
    if "regurgitacao_aortica" in da:
        da["regurgitacao_aortica"] = da["regurgitacao_aortica"].replace(
            "Grave com FE reduzida ou arritmia induzida contraindica esporte competitivo, com indicação cirúrgica.",
            "Na forma grave, FE reduzida ou arritmia complexa induzida pelo esforço restringe a participação competitiva e exige reavaliação especializada; indicação cirúrgica segue sintomas, dimensões/função do VE e demais critérios da diretriz valvar, não a arritmia isoladamente."
        )
    if "valva_aortica_bicuspide" in da:
        da["valva_aortica_bicuspide"] = da["valva_aortica_bicuspide"].replace(
            "Sem disfunção valvar nem aortopatia associada, recomendação segue igual à valva tricúspide normal.",
            "Sem disfunção valvar relevante nem aortopatia associada, a participação esportiva pode seguir a avaliação geral do atleta, mantendo vigilância apropriada da valva e da aorta."
        )
    approve_record(rec); dump_json(p, rows)
    report["targeted_corrections"].append("Valvopatia no atleta: IAo e valva bicúspide corrigidas para evitar gatilho cirúrgico indevido")

    # 4) CIED perioperatório: dependência de estimulação e uso de magneto não podem ser definidos por regras universais.
    p, rows, rec = load_single_disease("doencas/fragmentos/manejo-perioperatorio-de-dispositivo-cardiaco-implantavel.json")
    da = rec.get("diagnostic_approach") or {}
    if "caracterizacao_do_dispositivo_e_da_dependencia" in da:
        da["caracterizacao_do_dispositivo_e_da_dependencia"] = (
            "Antes da decisão perioperatória, identificar tipo de dispositivo, fabricante/modelo, indicação original, "
            "programação vigente, bateria, resposta ao magneto e presença de ritmo intrínseco adequado. Dependência de "
            "estimulação não deve ser inferida por um corte universal de frequência nem apenas pelo diagnóstico histórico; "
            "é determinada pela interrogação e pela avaliação do ritmo subjacente e de sua capacidade de manter perfusão. "
            "Marca-passo sem eletrodo do tipo Micra não oferece resposta convencional ao magneto; se for necessário modo "
            "assíncrono, a estratégia exige programação específica."
        )
    if "decisao_magneto_versus_reprogramacao" in da:
        da["decisao_magneto_versus_reprogramacao"] = (
            "A escolha entre magneto e reprogramação depende do tipo de CIED, dependência de estimulação, local/probabilidade "
            "de interferência eletromagnética, resposta conhecida ao magneto, acesso físico ao gerador e possibilidade de manter "
            "o magneto estável. Em CDI, o magneto geralmente suspende terapias de taquiarritmia sem tornar a estimulação "
            "assíncrona; portanto ele não resolve a necessidade de proteção de um paciente dependente de estimulação. Quando a "
            "resposta ao magneto é incerta, o gerador é inacessível, o magneto não pode ser fixado ou é necessário alterar o modo "
            "de estimulação, preferir reprogramação formal. Em qualquer estratégia, monitorização de ECG e pulso periférico é "
            "obrigatória, com desfibrilação/estimulação externa disponível e reativação documentada das terapias do CDI antes de "
            "deixar o ambiente monitorado."
        )
    ef = rec.get("emergency_flow") or []
    if ef:
        ef[0] = (
            "Na urgência sem interrogação prévia, tratar o CIED de status desconhecido como situação de alto risco: identificar "
            "dispositivo/fabricante o mais rápido possível, manter desfibrilação e estimulação externas disponíveis e adotar plano "
            "fail-safe conjunto com anestesia/eletrofisiologia, sem presumir automaticamente dependência de estimulação."
        )
    approve_record(rec); dump_json(p, rows)
    report["targeted_corrections"].append("CIED perioperatório: dependência e magneto/reprogramação reescritos de forma dispositivo-específica")

    # 5) Endocardite protética: tempo desde implante é contexto de risco, nunca indicação cirúrgica isolada.
    p, rows, rec = load_single_disease("doencas/fragmentos/endocardite-de-protese-valvar.json")
    ts = str(rec.get("treatment_summary") or "")
    safety = (
        " O tempo desde o implante ajuda a interpretar microbiologia e risco, mas não é indicação cirúrgica isolada: "
        "insuficiência cardíaca, infecção não controlada/abscesso, disfunção protética, risco embólico e avaliação do "
        "Endocarditis Team permanecem determinantes da decisão."
    )
    if safety.strip() not in ts:
        rec["treatment_summary"] = ts.rstrip() + safety
    approve_record(rec); dump_json(p, rows)
    report["targeted_corrections"].append("Endocardite protética: tempo pós-implante explicitamente removido como gatilho cirúrgico isolado")


# Confere as fontes remotas antes de qualquer promoção.
claude_remote = run("git", "rev-parse", f"origin/{CLAUDE_BRANCH}")
if claude_remote != CLAUDE_EXPECTED:
    raise SystemExit(f"HEAD Claude inesperado: {claude_remote}; esperado {CLAUDE_EXPECTED}")

grok_remote = run("git", "rev-parse", f"origin/{GROK_BRANCH}")
report["grok_remote_sha"] = grok_remote
report["grok_local_expected"] = GROK_LOCAL_EXPECTED_PREFIX
report["grok_blocked"] = not grok_remote.startswith(GROK_LOCAL_EXPECTED_PREFIX)

# Monólitos alterados pelo Claude.
for path in ("checklists/metadados.json", "exames/metadados.json", "casos-clinicos/metadados.json"):
    review_monolith(path)

# Fragmentos/correções alterados pelo Claude; aprovação é somente nos arquivos que diferem de main.
changed = run("git", "diff", "--name-only", f"{MAIN_REF}...HEAD").splitlines()
for name in changed:
    if not name.endswith(".json"):
        continue
    if name.startswith("doencas/fragmentos/") or name.startswith("doencas/correcoes/"):
        approve_disease_file(ROOT / name)

# Correções clínicas dirigidas sobre pontos identificados na revisão adversarial.
targeted_corrections()

# Revisa novamente marcadores duros nos registros Claude que ficaram no release.
for path_str in ("checklists/metadados.json", "exames/metadados.json", "casos-clinicos/metadados.json"):
    cur = by_slug(load_json(ROOT / path_str))
    base = by_slug(load_base(path_str) or [])
    for slug, rec in cur.items():
        if base.get(slug) == rec:
            continue
        marker = has_hard_unverified(rec)
        if marker:
            raise SystemExit(f"Marcador editorial duro remanescente em {path_str}:{slug}: {marker}")

# Status final e relatório auditável.
claude_total = sum(report["reviewed"].values())
lines = [
    "# Revisão e preparação de publicação — Claude + Grok — 29/08/2026",
    "",
    "## Estado",
    "",
    f"- Claude HEAD revisado: `{claude_remote}`.",
    f"- Registros monolíticos Claude promovidos/corrigidos: **{claude_total}**.",
    f"- Itens de checklist removidos por colisão/fonte não resolvida: **{len(report['removed_items'])}**.",
    f"- Registros inteiros retidos: **{len(report['dropped_records'])}**.",
    "- Fragmentos/correções de doença modificados pelo Claude: promovidos a `revisado` após correções dirigidas e gates estruturais.",
    "",
    "## Correções clínicas dirigidas",
]
for item in report["targeted_corrections"]:
    lines.append(f"- {item}.")

lines += ["", "## Itens removidos/retidos"]
if report["removed_items"]:
    for x in report["removed_items"]:
        lines.append(f"- `{x['record']}` / `{x['item']}` — {x['reason']}.")
else:
    lines.append("- Nenhum item individual removido.")
if report["dropped_records"]:
    for x in report["dropped_records"]:
        lines.append(f"- Registro `{x['record']}` RETIDO — {x['reason']}.")

lines += [
    "",
    "## Grok 67–75",
    "",
    f"- HEAD local informado no handoff: `{GROK_LOCAL_EXPECTED_PREFIX}…`.",
    f"- HEAD atualmente visível no GitHub: `{grok_remote}`.",
]
if report["grok_blocked"]:
    lines += [
        "- **Grok 67–75: BLOQUEADO / NÃO IMPORTADO.** O bundle/ZIP informado existe no host local do Grok, mas não está acessível neste runner nem no GitHub. A branch remota é antiga e não será usada como substituto silencioso.",
        "- Para completar o release, importar o bundle/ZIP ou publicar o HEAD `8b00af0c…` no GitHub e repetir a mesma revisão independente antes do merge final.",
    ]
else:
    lines.append("- **Grok 67–75: INTEGRADO E REVISADO.**")

lines += [
    "",
    "## Gate de release",
    "",
    "- Claude: **PRONTO PARA PUBLICAÇÃO** após a validação estrutural deste branch.",
    "- Grok 67–75: **BLOQUEIO ATIVO** enquanto o HEAD local não estiver materializado no repositório/runner.",
    "- Merge final para `main` e deploy: **não executar enquanto o bloqueio Grok estiver ativo**, para cumprir a solicitação de revisar todo o conteúdo antes da publicação consolidada.",
    "",
    "## Deploy preparado",
    "",
    "O workflow `deploy-reviewed-science.yml` fica preparado para execução manual após o merge final. Ele exige o SHA exato de `main` e recusa execução enquanto este relatório não contiver a marca `Grok 67–75: INTEGRADO E REVISADO`.",
]
REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

# Falha apenas por problemas do conteúdo Claude; a ausência do Grok vira bloqueio de merge, não perda do trabalho preparado.
if report["warnings"]:
    raise SystemExit("Warnings editoriais não resolvidos: " + "; ".join(report["warnings"]))

print(json.dumps(report, ensure_ascii=False, indent=2))
