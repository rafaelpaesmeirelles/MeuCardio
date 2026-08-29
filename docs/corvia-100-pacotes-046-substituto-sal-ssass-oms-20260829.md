# CorVIA 100 pacotes — 046/100 — Substituto de sal com potássio: SSaSS e segurança

Data: 29/08/2026  
Base auditada: `main` `59566e1196e0fa7f465df93516790ef454e1f565`

## Objetivo

Revisar adversarialmente o uso de substitutos de sal com menor sódio e maior potássio como estratégia de prevenção cardiovascular, preservando o benefício demonstrado no SSaSS sem extrapolá-lo para pessoas com risco de hipercalemia ou para contextos alimentares muito diferentes da população estudada.

## Evidência crítica verificada

- **SSaSS — Salt Substitute and Stroke Study** — Neal B et al. N Engl J Med. 2021;385:1067-1077. PMID `34459569`; DOI `10.1056/NEJMoa2105675`.
- Desenho: ensaio aberto, randomizado por conglomerados, 600 vilarejos rurais na China.
- População: 20.995 participantes; história de AVC ou idade ≥60 anos com hipertensão. Média de 65,4 anos; 72,6% tinham AVC prévio e 88,4% hipertensão.
- Intervenção: substituto contendo 75% NaCl + 25% KCl versus sal comum 100% NaCl.
- Seguimento médio: 4,74 anos.
- AVC: 29,14 vs 33,65 eventos/1000 pessoas-ano; rate ratio 0,86 (IC95% 0,77-0,96; p=0,006).
- Eventos cardiovasculares maiores: rate ratio 0,87 (IC95% 0,80-0,94; p<0,001).
- Morte por qualquer causa: rate ratio 0,88 (IC95% 0,82-0,95; p<0,001).
- Eventos adversos graves atribuídos a hipercalemia: rate ratio 1,04 (IC95% 0,80-1,37; p=0,76), sem aumento estatisticamente significativo no ensaio.
- **WHO guideline on lower-sodium salt substitutes, 2025** — ISBN `978-92-4-010559-1`.
  - A OMS mantém recomendação forte de reduzir sódio para <2 g/dia.
  - Se o adulto optar por usar sal de mesa, sugere substituir sal comum por substituto de menor sódio contendo potássio.
  - A recomendação é **condicional** e exclui crianças, gestantes e pessoas com comprometimento renal ou outras condições que possam prejudicar a excreção de potássio.

## Revisão adversarial independente

1. **SSaSS não é estudo de população geral irrestrita:** foi uma população rural chinesa, mais velha e de alto risco, com grande proporção de AVC prévio/hipertensão.
2. **Substituto não significa “adicionar potássio para todos”:** doença renal, hipercalemia, medicamentos e outras condições que reduzem excreção de potássio mudam o balanço risco-benefício.
3. **Segurança média do RCT não elimina risco individual:** ausência de aumento estatisticamente significativo de hipercalemia grave no SSaSS não autoriza dispensar avaliação em pessoas vulneráveis.
4. **Estratégia depende da fonte de sódio:** a aplicabilidade é maior onde sal discricionário de cozinha/mesa contribui fortemente para ingestão; sistemas alimentares dominados por ultraprocessados exigem medidas adicionais.
5. **Substituto não substitui redução global de sódio:** o objetivo continua sendo reduzir exposição a sódio; não promover produto como licença para manter alto consumo de sal.
6. **WHO 2025 delimita a população:** a exclusão de pessoas com comprometimento renal ou risco de retenção de potássio deve ser preservada em qualquer material educativo.

## Guardrails para CorVIA

- bloquear `sal light/com potássio é seguro para todos`;
- bloquear recomendação automática em DRC, hipercalemia ou condições que prejudiquem excreção de potássio;
- diferenciar substituição parcial de NaCl por KCl de suplementação farmacológica de potássio;
- contextualizar a população e o ambiente alimentar do SSaSS;
- não apagar a recomendação de reduzir sódio total;
- não converter resultado de cluster-RCT em prescrição individual sem triagem clínica de risco.

## Resultado

Gap de prevenção e segurança fechado: **o SSaSS mostrou redução de AVC, eventos cardiovasculares e mortalidade com substituição parcial de NaCl por KCl em população de alto risco, mas a OMS 2025 mantém a recomendação condicional e exclui pessoas com risco de comprometimento da excreção de potássio**.

Nenhum arquivo clínico, dose, regra determinística, slug, JSON ou schema foi alterado neste pacote.
