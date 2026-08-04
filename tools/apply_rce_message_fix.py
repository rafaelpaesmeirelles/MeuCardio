#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "backend/app/api/receituario.py"
source = path.read_text(encoding="utf-8")
old = '''        bloqueios.append(
            f"O tipo {doc.tipo_codigo} permanece indisponível sem numeração oficial "
            "ou integração SNCR aplicável; nenhum número será simulado."
        )
'''
new = '''        bloqueios.append(
            f"O tipo {doc.tipo_codigo} permanece indisponível sem numeração oficial "
            "ou integração SNCR aplicável; nenhum número será simulado. "
            "Não depende mais da assinatura digital: o bloqueio é regulatório "
            "e de numeração oficial."
        )
'''
if source.count(old) != 1:
    raise SystemExit(f"Trecho encontrado {source.count(old)} vezes; nenhuma alteração aplicada.")
path.write_text(source.replace(old, new, 1), encoding="utf-8")
Path(__file__).unlink()
print("Mensagem regulatória da RCE corrigida.")
