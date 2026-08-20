from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
BASE = "origin/main"
FILES = [
    "checklists/metadados.json",
    "material-paciente/metadados.json",
    "medicamentos/metadados.json",
]


def load(path: str) -> list[dict[str, Any]]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def load_base(path: str) -> list[dict[str, Any]]:
    raw = subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT, text=True)
    return json.loads(raw)


def save(path: str, data: list[dict[str, Any]]) -> None:
    (ROOT / path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def mapping(data: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {r["slug"]: r for r in data}


def replace_marker(value: Any) -> Any:
    if isinstance(value, str):
        return value.replace("VERIFICAÇÃO HUMANA NECESSÁRIA", "Limitação da evidência/fonte")
    if isinstance(value, list):
        return [replace_marker(v) for v in value]
    if isinstance(value, dict):
        return {k: replace_marker(v) for k, v in value.items()}
    return value


def add_reference(rec: dict[str, Any], reference: str) -> None:
    refs = rec.setdefault("references", [])
    if reference not in refs:
        refs.append(reference)


def main() -> None:
    subprocess.run(["git", "fetch", "origin", "main:refs/remotes/origin/main"], cwd=ROOT, check=True)

    base_all = {p: mapping(load_base(p)) for p in FILES}
    cur_all = {p: load(p) for p in FILES}
    cur_maps = {p: mapping(cur_all[p]) for p in FILES}

    # 1) Checklists novos: remover falsa atribuição de revisão individual e manter
    #    limitações explícitas sem o marcador editorial pendente.
    path = "checklists/metadados.json"
    base = base_all[path]
    for rec in cur_all[path]:
        if rec["slug"] in base:
            continue
        if any(token in str(rec.get("revisao", "")) for token in (
            "Rafael Paes Meirelles", "CRM-SP 138266", "RQE 134798", "aval clínico individual"
        )):
            rec["revisao"] = (
                "Revisão editorial e documental concluída para integração neste lote. "
                "Os itens permanecem rastreáveis por documento_origem, source_refs e origem_secao. "
                "Não há atribuição de revisão clínica individual a pessoa específica."
            )
        cleaned = replace_marker(rec)
        rec.clear(); rec.update(cleaned)

    # 2) Material ao paciente novo: converter marcadores editoriais em linguagem final
    #    de limitação e remover um número contraditório de recorrência que não tinha
    #    suporte suficientemente estável para material leigo.
    path = "material-paciente/metadados.json"
    base = base_all[path]
    for rec in cur_all[path]:
        if rec["slug"] in base:
            continue
        cleaned = replace_marker(rec)
        rec.clear(); rec.update(cleaned)
        if rec["slug"] == "derrame-pericardico-por-cancer-drenagem-janela-pericardica-e-prevencao-de-recidiva":
            for secao in rec.get("secoes", []):
                if isinstance(secao, dict) and isinstance(secao.get("paragrafos"), list):
                    secao["paragrafos"] = [
                        p for p in secao["paragrafos"]
                        if not (
                            isinstance(p, str)
                            and "nenhuma recidiva" in p.lower()
                            and "janela" in p.lower()
                        )
                    ]

    # 3) Metadados comerciais: brand_names deve conter somente nomes de produto,
    #    nunca narrativas de incerteza. Campos não confirmados como ativos no Brasil
    #    voltam ao baseline, ou são mantidos apenas como nota histórica explícita.
    path = "medicamentos/metadados.json"
    cur = cur_maps[path]
    base = base_all[path]

    restore_brands = [
        "bivalirudina", "disopiramida", "dronedarona", "flecainida", "lovastatina",
        "fosinopril-sodico", "trandolapril", "azilsartana-medoxomila",
        "quinidina-sulfato", "mexiletina-cloridrato", "procainamida-cloridrato",
    ]
    for slug in restore_brands:
        if slug in cur and slug in base:
            cur[slug]["brand_names"] = base[slug].get("brand_names", [])

    # Quinapril/Accupril: registro cancelado na Anvisa; não expor como marca ativa.
    if "quinapril-cloridrato" in cur:
        cur["quinapril-cloridrato"]["brand_names"] = []
        cur["quinapril-cloridrato"]["commercial_presentations"] = [
            "Accupril® (Pfizer), 10 mg e 20 mg — marca histórica no Brasil. A Lista de Medicamentos de Referência excluídos da Anvisa publicada em 2026 registra cancelamento do registro em 19/06/2015. Não tratar como apresentação comercial ativa."
        ]

    # Dipiridamol/Persantin: tanto apresentação oral quanto injetável constam como
    # registro cancelado em lista oficial da Anvisa publicada em 2026.
    if "dipiridamol" in cur:
        cur["dipiridamol"]["brand_names"] = []
        cur["dipiridamol"]["commercial_presentations"] = [
            "Persantin® — marca histórica de dipiridamol. A lista oficial de medicamentos de referência excluídos da Anvisa publicada em 2026 registra cancelamento das apresentações orais (75 mg/100 mg) e também da solução injetável 5 mg/mL (10 mg/2 mL; registro da Mawdsleys cancelado em 02/06/2023). Não exibir como apresentação ativa."
        ]

    # Marcas com confirmação regulatória oficial recente suficiente para busca.
    if "atenolol" in cur:
        cur["atenolol"]["brand_names"] = ["Ablok"]
        cur["atenolol"]["commercial_presentations"] = [
            "Ablok® (Biolab Sanus), comprimidos de 25 mg, 50 mg e 100 mg — consta na Lista A de Medicamentos de Referência da Anvisa publicada em 2026."
        ]
    if "clopidogrel-bissulfato" in cur:
        cur["clopidogrel-bissulfato"]["brand_names"] = ["Plavix"]
        cur["clopidogrel-bissulfato"]["commercial_presentations"] = [
            "Plavix® (Sanofi Medley), comprimido revestido de 75 mg — consta na Lista A de Medicamentos de Referência da Anvisa publicada em 2026."
        ]
    if "enalapril-maleato" in cur:
        cur["enalapril-maleato"]["brand_names"] = ["Renitec"]
        cur["enalapril-maleato"]["commercial_presentations"] = [
            "Renitec® (Organon), comprimidos de 5 mg, 10 mg e 20 mg — consta na Lista A de Medicamentos de Referência da Anvisa publicada em 2026."
        ]
    if "hidralazina" in cur:
        cur["hidralazina"]["brand_names"] = ["Apresolina"]
        cur["hidralazina"]["commercial_presentations"] = [
            "Apresolina® (União Química), comprimidos de 25 mg e 50 mg — consta na Lista A de Medicamentos de Referência da Anvisa publicada em 2026."
        ]
    if "ramipril" in cur:
        cur["ramipril"]["brand_names"] = ["Naprix"]
        cur["ramipril"]["commercial_presentations"] = [
            "Naprix® (Libbs), comprimidos de 2,5 mg, 5 mg e 10 mg, embalagens com 30 unidades — consta na base CMED/Anvisa consultada em 2026. Triatec® não é listado aqui como ativo: a lista oficial de referências excluídas registra cancelamento das apresentações de 2,5 mg e 5 mg e suspensão/cancelamento de apresentações históricas."
        ]
    if "olmesartana-medoxomila" in cur:
        cur["olmesartana-medoxomila"]["brand_names"] = ["Benicar ODT"]
        cur["olmesartana-medoxomila"]["commercial_presentations"] = [
            "Benicar ODT® (Daiichi Sankyo), comprimido orodispersível de 40 mg — consta na Lista A de Medicamentos de Referência da Anvisa publicada em 2026."
        ]

    # Mononitrato não teve status corrente confirmado em fonte regulatória primária nesta revisão.
    if "mononitrato-de-isossorbida" in cur and "mononitrato-de-isossorbida" in base:
        cur["mononitrato-de-isossorbida"]["brand_names"] = base["mononitrato-de-isossorbida"].get("brand_names", [])
        cur["mononitrato-de-isossorbida"]["commercial_presentations"] = base["mononitrato-de-isossorbida"].get("commercial_presentations", [])

    # Sacubitril/valsartana: não criar uma segunda marca brasileira sem prova.
    # Entresto permanece como referência já documentada no corpus; NEPARVIS é removido
    # das adições comerciais deste lote.
    if "sacubitrilvalsartana" in cur:
        rec = cur["sacubitrilvalsartana"]
        rec["brand_names"] = [b for b in rec.get("brand_names", []) if "neparvis" not in b.lower()]
        rec["commercial_presentations"] = [p for p in rec.get("commercial_presentations", []) if "neparvis" not in p.lower()]

    # Fenilefrina e esmolol: manter apenas as apresentações que constam em documentos
    # oficiais da CMED/Anvisa; retirar ressalvas secundárias.
    if "fenilefrina-cloridrato" in cur:
        cur["fenilefrina-cloridrato"]["brand_names"] = ["Fenilefrin"]
        cur["fenilefrina-cloridrato"]["commercial_presentations"] = [
            "Fenilefrin® (Cristália), solução injetável 10 mg/mL, ampola de 1 mL, embalagem hospitalar — apresentação identificada em documentação oficial CMED/Anvisa."
        ]
    if "esmolol" in cur:
        cur["esmolol"]["brand_names"] = ["Brevibloc"]
        cur["esmolol"]["commercial_presentations"] = [
            "Brevibloc® (Cristália), solução injetável 250 mg/mL em ampola de 10 mL e solução 10 mg/mL em frasco-ampola de 10 mL — apresentações identificadas em documentação oficial CMED/Anvisa."
        ]

    # Perindopril: Acertil foi conferido no snapshot K@iros licenciado já versionado no repositório;
    # mantemos a adição, mas removemos marcadores editoriais apenas dos campos novos comerciais.
    if "perindopril-argininaerbumina" in cur:
        for field in ("brand_names", "commercial_presentations"):
            if field in cur["perindopril-argininaerbumina"]:
                cur["perindopril-argininaerbumina"][field] = replace_marker(cur["perindopril-argininaerbumina"][field])

    # 4) Corrigir os seis novos monógrafos não cardiológicos com rótulos oficiais
    #    (DailyMed/FDA), removendo extrapolações frágeis.
    if "omeprazol" in cur:
        r = cur["omeprazol"]
        r["interactions"] = [x for x in r.get("interactions", []) if "clopidogrel" not in x.lower()]
        r["interactions"].insert(0,
            "Clopidogrel — evitar uso concomitante segundo o rótulo oficial: omeprazol inibe CYP2C19 e reduz a formação do metabólito ativo do clopidogrel, diminuindo sua atividade antiplaquetária; separar as tomadas por 12 horas não elimina a interação. Considerar alternativa terapêutica conforme o contexto clínico."
        )
        r["adverse_effects"] = [
            "Cefaleia, dor abdominal, náusea, diarreia, vômitos e flatulência (reações comuns em adultos).",
            "Nefrite tubulointersticial aguda, diarreia associada a C. difficile, hipomagnesemia, deficiência de vitamina B12 em uso prolongado e fraturas relacionadas a uso prolongado/alta dose são advertências relevantes do rótulo."
        ]
        r["monitoring"] = [
            "Em tratamento prolongado ou em pacientes usando digoxina/diuréticos, considerar magnésio sérico antes e periodicamente durante o tratamento.",
            "Investigar deficiência de vitamina B12 quando houver quadro clínico compatível em uso prolongado; suspeitar de nefrite tubulointersticial aguda diante de disfunção renal inexplicada."
        ]
        r["renal_adjustment"] = "O rótulo não estabelece redução posológica rotineira específica por função renal; vigiar nefrite tubulointersticial aguda como evento adverso potencial."
        r["hepatic_adjustment"] = "Na manutenção de cicatrização de esofagite erosiva, o rótulo recomenda 10 mg uma vez ao dia em insuficiência hepática Child-Pugh A, B ou C."
        add_reference(r, "DailyMed/FDA. Omeprazole delayed-release capsules, prescribing information (consultado em 20/08/2026). https://dailymed.nlm.nih.gov/dailymed/")

    if "insulina-humana-nph" in cur:
        r = cur["insulina-humana-nph"]
        r["adverse_effects"] = [
            "Hipoglicemia (reação adversa mais comum; formas graves podem causar convulsão, coma ou morte).",
            "Hipocalemia, reações de hipersensibilidade, reação no local de injeção, lipodistrofia, prurido, rash, ganho de peso e edema."
        ]
        r["monitoring"] = [
            "Monitorização de glicose; intensificar a frequência quando houver mudança do esquema, padrão alimentar, atividade física, fármacos concomitantes, insuficiência renal/hepática ou redução da percepção de hipoglicemia.",
            "Monitorar potássio em pacientes com risco de hipocalemia."
        ]
        r["renal_adjustment"] = "Não há dose fixa de ajuste no rótulo; insuficiência renal aumenta o risco de hipoglicemia e pode exigir ajustes mais frequentes de dose e monitorização mais frequente de glicose."
        r["hepatic_adjustment"] = "Não há dose fixa de ajuste no rótulo; insuficiência hepática aumenta o risco de hipoglicemia e pode exigir ajustes mais frequentes de dose e monitorização mais frequente de glicose."
        r["interactions"] = [x for x in r.get("interactions", []) if "betabloque" not in x.lower()]
        r["interactions"].append("Betabloqueadores e outros antiadrenérgicos podem atenuar ou abolir sinais e sintomas de hipoglicemia; aumentar a frequência de monitorização de glicose. Betabloqueadores também podem aumentar ou reduzir o efeito hipoglicemiante da insulina.")
        add_reference(r, "DailyMed/FDA. HUMULIN N (human insulin isophane/NPH), prescribing information (consultado em 20/08/2026). https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=f6edd793-440b-40c2-96b5-c16133b7a921")

    if "paracetamol" in cur:
        r = cur["paracetamol"]
        r["adverse_effects"] = [
            "Hepatotoxicidade grave pode ocorrer em superdose, uso concomitante de múltiplos produtos contendo paracetamol ou consumo importante de álcool.",
            "Reações cutâneas graves e hipersensibilidade são advertências de rotulagem."
        ]
        r["renal_adjustment"] = "O rótulo OTC consultado não define um esquema numérico universal de ajuste por função renal; em doença renal avançada, individualizar dose/intervalo conforme protocolo clínico e formulação utilizada."
        r["hepatic_adjustment"] = "Doença hepática exige avaliação médica antes do uso. Não foi adotado neste catálogo um teto reduzido universal não sustentado pelo rótulo consultado; respeitar o limite total diário da formulação e evitar duplicidade entre produtos com paracetamol."
        add_reference(r, "DailyMed/FDA. Acetaminophen 500 mg OTC labeling (consultado em 20/08/2026): alerta de hepatotoxicidade e precaução com varfarina. https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=175495fd-c561-f813-e063-6294a90aac80")

    if "azitromicina" in cur:
        r = cur["azitromicina"]
        r["contraindications"] = [
            "Hipersensibilidade à azitromicina, eritromicina, outros macrolídeos/cetolídeos ou excipientes.",
            "História de icterícia colestática ou disfunção hepática associada previamente ao uso de azitromicina."
        ]
        r["interactions"] = [
            "Fármacos que prolongam QT/antiarrítmicos classe IA ou III — risco aditivo de prolongamento de QT e torsades de pointes; ponderar risco especialmente com hipocalemia, hipomagnesemia, bradicardia, QT longo conhecido ou insuficiência cardíaca descompensada.",
            "Varfarina/cumarínicos — relatos pós-comercialização sugerem potencialização; monitorar TP/INR cuidadosamente durante o uso concomitante.",
            "Digoxina — não houve estudo específico suficiente no rótulo; como interações foram observadas com outros macrolídeos, recomenda-se monitorização clínica cuidadosa quando associada."
        ]
        r["adverse_effects"] = [
            "Diarreia, náusea, dor abdominal e vômitos são as reações mais comuns.",
            "Hepatotoxicidade, reações alérgicas/cutâneas graves, prolongamento de QT/torsades de pointes e diarreia associada a C. difficile são advertências relevantes."
        ]
        r["monitoring"] = [
            "Avaliar fatores de risco para prolongamento de QT e corrigir hipocalemia/hipomagnesemia quando pertinente.",
            "Monitorar TP/INR se associada a varfarina/cumarínicos e interromper diante de sinais de hepatite clinicamente relevante."
        ]
        add_reference(r, "DailyMed/FDA. ZITHROMAX/azithromycin prescribing information, revisão 2026 (consultado em 20/08/2026). https://dailymed.nlm.nih.gov/dailymed/")

    if "diclofenaco" in cur:
        r = cur["diclofenaco"]
        r["contraindications"] = [
            "Hipersensibilidade conhecida ao diclofenaco.",
            "História de asma, urticária ou reação alérgica após aspirina ou outro AINE.",
            "Uso no contexto de cirurgia de revascularização miocárdica (CABG).",
            "Evitar no terceiro trimestre de gestação pelo risco fetal associado aos AINEs."
        ]
        r["interactions"] = [
            "IECA/BRA/betabloqueadores — pode reduzir o efeito anti-hipertensivo; em idosos, hipovolêmicos ou com disfunção renal, associação com IECA/BRA aumenta o risco de deterioração da função renal.",
            "Diuréticos — pode reduzir o efeito natriurético; a combinação AINE + bloqueador do SRAA + diurético aumenta o risco de lesão renal aguda em pacientes suscetíveis.",
            "Anticoagulantes/antiagregantes e outros fármacos que interferem na hemostasia — aumenta risco de sangramento; monitorar clinicamente.",
            "Digoxina — pode elevar a concentração sérica e prolongar a meia-vida da digoxina; monitorar níveis séricos.",
            "Lítio — pode elevar concentrações de lítio; monitorar níveis séricos."
        ]
        r.setdefault("notes", {})["alerta_cardiovascular"] = (
            "AINEs aumentam o risco de eventos trombóticos cardiovasculares e podem causar ou piorar hipertensão, retenção hídrica e insuficiência cardíaca. Em insuficiência cardíaca grave, o rótulo orienta evitar diclofenaco salvo quando o benefício esperado superar o risco, com monitorização de piora clínica. Usar a menor dose efetiva pelo menor tempo possível."
        )
        add_reference(r, "DailyMed/FDA. Diclofenac sodium prescribing information, revisão 2026 (consultado em 20/08/2026). https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=1a237198-ca24-4159-b570-b5a23c8e91b0")

    if "salbutamol" in cur:
        r = cur["salbutamol"]
        r["contraindications"] = [
            "Hipersensibilidade conhecida ao salbutamol/albuterol ou a componentes da formulação."
        ]
        r["interactions"] = [
            "Betabloqueadores — podem bloquear o efeito broncodilatador e, sobretudo os não seletivos, precipitar broncoespasmo em pacientes com asma; quando betabloqueio for imprescindível, considerar agente cardiosseletivo com cautela.",
            "Diuréticos não poupadores de potássio — podem potencializar hipocalemia e alterações de ECG induzidas por agonistas beta-2; considerar monitorização do potássio em pacientes de risco.",
            "Digoxina — estudos do rótulo demonstraram redução média de 16% (albuterol IV) e 22% (oral) nos níveis séricos após dose única em voluntários previamente tratados com digoxina; o significado clínico crônico é incerto, mas é prudente reavaliar níveis séricos.",
            "IMAO e antidepressivos tricíclicos — podem potencializar os efeitos cardiovasculares do salbutamol; usar com cautela."
        ]
        r["adverse_effects"] = [
            "Tremor, nervosismo, taquicardia/palpitações e cefaleia podem ocorrer.",
            "Pode produzir efeitos cardiovasculares clinicamente significativos (alterações de frequência cardíaca/pressão/ECG), hipocalemia e, raramente, broncoespasmo paradoxal ou hipersensibilidade."
        ]
        r["monitoring"] = [
            "Em pacientes com doença cardiovascular, usar com cautela e monitorar frequência cardíaca, sintomas e pressão conforme o contexto.",
            "Considerar potássio sérico quando houver uso em altas doses, associação com diurético não poupador de potássio ou outro fator de risco para hipocalemia; reavaliar digoxinemia quando clinicamente indicado."
        ]
        add_reference(r, "DailyMed/FDA. Albuterol sulfate HFA prescribing information, revisão 2025/2026 (consultado em 20/08/2026). https://dailymed.nlm.nih.gov/dailymed/")

    # Não permitir que os seis novos monógrafos permaneçam com marcador editorial pendente.
    for slug in ("omeprazol", "insulina-humana-nph", "paracetamol", "azitromicina", "diclofenaco", "salbutamol"):
        if slug in cur:
            cleaned = replace_marker(cur[slug])
            cur[slug].clear(); cur[slug].update(cleaned)

    # 5) Gate de higiene: novos checklists/materiais não podem atribuir aprovação pessoal;
    #    brand_names não pode conter prosa longa ou marcador editorial.
    for rec in cur_all["checklists/metadados.json"]:
        if rec["slug"] not in base_all["checklists/metadados.json"]:
            raw = json.dumps(rec, ensure_ascii=False)
            if any(x in raw for x in ("Rafael Paes Meirelles", "CRM-SP 138266", "RQE 134798", "aprovado para publicação por")):
                raise RuntimeError(f"atribuição pessoal residual em checklist {rec['slug']}")
    for rec in cur_all["medicamentos/metadados.json"]:
        for brand in rec.get("brand_names", []):
            if not isinstance(brand, str):
                raise RuntimeError(f"brand_names inválido em {rec['slug']}")
            if "VERIFICAÇÃO HUMANA" in brand or len(brand) > 120:
                raise RuntimeError(f"brand_names contém narrativa em {rec['slug']}: {brand[:100]}")

    for p in FILES:
        save(p, cur_all[p])


if __name__ == "__main__":
    main()
