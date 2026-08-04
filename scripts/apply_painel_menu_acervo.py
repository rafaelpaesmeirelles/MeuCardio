from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(text: str, old: str, new: str, *, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: esperado 1 trecho, encontrados {count}")
    return text.replace(old, new, 1)


def regex_once(text: str, pattern: str, replacement: str, *, label: str) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f"{label}: esperado 1 trecho, encontrados {count}")
    return updated


# ---------------------------------------------------------------------------
# Menu lateral: Painel primeiro; indicadores/admin/conta no final.
shell_path = ROOT / "frontend/src/components/Shell.tsx"
shell = shell_path.read_text(encoding="utf-8")

shell = replace_once(
    shell,
    '  { to: "/indicadores", rotulo: "Meus indicadores", curto: "Indicadores" },\n'
    '  { to: "/", rotulo: "Painel", curto: "Painel", fim: true },\n',
    "",
    label="remove itens especiais da lista alfabética",
)

shell = replace_once(
    shell,
    "];\n\nexport default function Shell() {",
    "];\n\n"
    'const PAINEL: ItemNav = { to: "/", rotulo: "Painel", curto: "Painel", fim: true };\n'
    'const INDICADORES: ItemNav = { to: "/indicadores", rotulo: "Meus indicadores", curto: "Indicadores" };\n'
    'const CONTA: ItemNav = { to: "/minha-conta", rotulo: "Minha conta", curto: "Conta" };\n\n'
    "export default function Shell() {",
    label="insere itens fixos do menu",
)

shell = regex_once(
    shell,
    r'  const CONTA: ItemNav = \{.*?\n\n  const nav: ItemNav\[\] =.*?\n\n  return \(',
    '''  const ADMIN: ItemNav = {
    to: "/admin",
    rotulo: pendentes > 0 ? `Administração (${pendentes})` : "Administração",
    curto: pendentes > 0 ? `Admin (${pendentes})` : "Admin",
  };

  const nav: ItemNav[] = usuario?.role === "admin"
    ? [
        PAINEL,
        ...NAV_BASE,
        { to: "/fila-telediagnostico", rotulo: "Fila de telediagnóstico", curto: "Fila" },
        { to: "/admin/usuarios-online", rotulo: "Usuários online", curto: "Online" },
        INDICADORES,
        ADMIN,
        CONTA,
      ]
    : [PAINEL, ...NAV_BASE, INDICADORES, CONTA];

  return (''',
    label="reordena menu",
)

shell = regex_once(
    shell,
    r'(<button\n\s+className="emerg-atalho".*?>)\s*● Emergência\s*(</button>)',
    r'''\1
          <svg aria-hidden="true" viewBox="0 0 24 24" width="30" height="30">
            <path d="M9.5 3h5v6.5H21v5h-6.5V21h-5v-6.5H3v-5h6.5V3Z" fill="currentColor" />
          </svg>
          <span className="sr-only">Modo Emergência</span>
        \2''',
    label="restaura ícone de emergência",
)

shell_path.write_text(shell, encoding="utf-8")


# ---------------------------------------------------------------------------
# Painel: remove o alerta visual do inventário; a integridade continua exposta
# na API e validada pelo reconciliador/deploy.
painel_path = ROOT / "frontend/src/pages/Painel.tsx"
painel = painel_path.read_text(encoding="utf-8")
painel = regex_once(
    painel,
    r'type Catalogo = \{.*?\};',
    'type Catalogo = { total: number };',
    label="simplifica contrato do catálogo no painel",
)
painel = regex_once(
    painel,
    r'\n\s*\{usuario\?\.role === "admin" && catalogo\?\.integrity_ok === false && \(.*?\n\s*\)\}\n',
    "\n",
    label="remove notificação de inventário do painel",
)
painel_path.write_text(painel, encoding="utf-8")


# ---------------------------------------------------------------------------
# CSS: atalho de emergência circular ao lado do CorvIA Chat.
css_path = ROOT / "frontend/src/styles/shell.css"
css = css_path.read_text(encoding="utf-8")
marker = "/* Atalhos flutuantes: Emergência e CorvIA Chat */"
if marker in css:
    raise RuntimeError("estilos dos atalhos já existem")
css += '''

/* Atalhos flutuantes: Emergência e CorvIA Chat */
.emerg-atalho {
  position: fixed;
  right: 84px;
  bottom: 78px;
  z-index: 1199;
  width: 56px;
  height: 56px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  border: 2px solid var(--branco);
  border-radius: 50%;
  background: var(--acao);
  color: var(--branco);
  box-shadow: 0 4px 14px rgba(176, 0, 26, 0.34);
  cursor: pointer;
  transition: transform 0.12s ease, background 0.12s ease;
}
.emerg-atalho:hover {
  background: var(--acao-hover);
  transform: translateY(-1px);
}
.emerg-atalho:active { transform: translateY(0); }

.sr-only {
  position: absolute !important;
  width: 1px !important;
  height: 1px !important;
  padding: 0 !important;
  margin: -1px !important;
  overflow: hidden !important;
  clip: rect(0, 0, 0, 0) !important;
  white-space: nowrap !important;
  border: 0 !important;
}
'''
css_path.write_text(css, encoding="utf-8")


# ---------------------------------------------------------------------------
# Publicação idempotente de todo conteúdo preservado e revisado.
command_path = ROOT / "backend/app/commands/publish_preserved_content.py"
command_path.write_text('''"""Publica registros preservados que já passaram por revisão editorial.

O reconciliador mantém registros antigos no PostgreSQL para auditoria. Este
comando torna públicos todos os registros preservados com
``review_status == "revisado"`` e mantém rascunhos/pendências indisponíveis.
É idempotente e seguro para execução em todo deploy.
"""

from __future__ import annotations

import argparse
import json
from typing import Any

from sqlalchemy.orm import Session

from app.commands.reconcile_content import FRONTS
from app.core.db import SessionLocal


def publish_preserved_reviewed(db: Session, *, dry_run: bool = False) -> dict[str, Any]:
    by_front: dict[str, int] = {}
    total = 0
    try:
        for front, config in FRONTS.items():
            model = config["model"]
            query = db.query(model).filter(
                model.published.is_(False),
                model.review_status == "revisado",
            )
            changed = query.count() if dry_run else query.update(
                {model.published: True}, synchronize_session=False
            )
            by_front[front] = int(changed)
            total += int(changed)
        if dry_run:
            db.rollback()
        else:
            db.commit()
    except Exception:
        db.rollback()
        raise
    return {"published_total": total, "published_by_front": by_front, "dry_run": dry_run}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        result = publish_preserved_reviewed(db, dry_run=args.dry_run)
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"status": "error", "type": type(exc).__name__, "detail": str(exc)},
                         ensure_ascii=False, indent=2))
        return 1
    finally:
        db.close()

    print(json.dumps({"status": "ok", **result}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
''', encoding="utf-8")


# ---------------------------------------------------------------------------
# O deploy passa a republicar os preservados revisados depois da reconciliação.
deploy_path = ROOT / "deploy.sh"
deploy = deploy_path.read_text(encoding="utf-8")
deploy = replace_once(
    deploy,
    'backend_exec python -m app.commands.reconcile_content --publish-reviewed\n',
    'backend_exec python -m app.commands.reconcile_content --publish-reviewed\n'
    'log "Publicando todo conteúdo preservado que já está revisado."\n'
    'backend_exec python -m app.commands.publish_preserved_content\n',
    label="integra publicação preservada ao deploy",
)
deploy_path.write_text(deploy, encoding="utf-8")


# ---------------------------------------------------------------------------
# Testes de contrato e da rotina idempotente.
test_path = ROOT / "backend/tests/test_painel_menu_acervo.py"
test_path.write_text('''from pathlib import Path

from app.commands import publish_preserved_content as command


class _Field:
    def is_(self, value):
        return ("is", value)

    def __eq__(self, value):
        return ("eq", value)


class _Model:
    published = _Field()
    review_status = _Field()


class _Query:
    def __init__(self, amount):
        self.amount = amount
        self.filters = []
        self.updated = False

    def filter(self, *conditions):
        self.filters.extend(conditions)
        return self

    def count(self):
        return self.amount

    def update(self, values, synchronize_session=False):
        assert values == {_Model.published: True}
        assert synchronize_session is False
        self.updated = True
        return self.amount


class _Session:
    def __init__(self, amounts):
        self.amounts = iter(amounts)
        self.queries = []
        self.commits = 0
        self.rollbacks = 0

    def query(self, model):
        assert model is _Model
        query = _Query(next(self.amounts))
        self.queries.append(query)
        return query

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


def test_publica_preservados_revisados(monkeypatch):
    monkeypatch.setattr(command, "FRONTS", {
        "documentos": {"model": _Model},
        "evidencias": {"model": _Model},
    })
    db = _Session([3, 2])
    result = command.publish_preserved_reviewed(db)
    assert result["published_total"] == 5
    assert result["published_by_front"] == {"documentos": 3, "evidencias": 2}
    assert db.commits == 1
    assert db.rollbacks == 0
    assert all(query.updated for query in db.queries)


def test_dry_run_nao_altera_banco(monkeypatch):
    monkeypatch.setattr(command, "FRONTS", {"documentos": {"model": _Model}})
    db = _Session([4])
    result = command.publish_preserved_reviewed(db, dry_run=True)
    assert result["published_total"] == 4
    assert db.commits == 0
    assert db.rollbacks == 1
    assert not db.queries[0].updated


def test_ordem_do_menu_e_alerta_removido():
    root = Path(__file__).resolve().parents[2]
    shell = (root / "frontend/src/components/Shell.tsx").read_text(encoding="utf-8")
    painel = (root / "frontend/src/pages/Painel.tsx").read_text(encoding="utf-8")
    deploy = (root / "deploy.sh").read_text(encoding="utf-8")

    assert "[PAINEL, ...NAV_BASE, INDICADORES, CONTA]" in shell
    assert shell.index("INDICADORES,\n        ADMIN,\n        CONTA") > shell.index("...NAV_BASE")
    assert "Acervo de produção abaixo do inventário certificado" not in painel
    assert "app.commands.publish_preserved_content" in deploy
''', encoding="utf-8")


# Remove o aplicador: somente as alterações resultantes devem permanecer.
Path(__file__).unlink()
print("Patch de painel, menu e acervo aplicado com sucesso.")
