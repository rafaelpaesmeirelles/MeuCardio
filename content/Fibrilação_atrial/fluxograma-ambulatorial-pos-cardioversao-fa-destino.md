---
title: "Fluxograma ambulatorial: pós-cardioversão de FA — PS agora vs retorno precoce vs plano"
slug: fluxograma-ambulatorial-pos-cardioversao-fa-destino
theme: "Fibrilação atrial"
kind: fluxograma
fonte_producao: grok
summary: "Destino clínico individualizado e limites de segurança; critérios detalhados no protocolo e navegação canônica do pacote."
review_status: revisado
review_note: "Revisão científica/adversarial 08/09/2026: findings PR883 reconstruídos; urgência, bibliografia e limites revistos. Fonte grok preservada."
source_refs:
  - "Van Gelder IC, Rienstra M, Bunting KV, et al. 2024 ESC Guidelines for the management of atrial fibrillation developed in collaboration with the EACTS. Eur Heart J. 2024;45(36):3314-3414. DOI: 10.1093/eurheartj/ehae176. PMID: 39210723"
  - "Cintra FD, Pisani CF, Rezende AGS, et al. Diretriz Brasileira de Fibrilação Atrial – 2025. Arq Bras Cardiol. 2025;122(9):e20250618. DOI: 10.36660/abc.20250618. PMID: 41294177"
---

# Fluxograma ambulatorial: pós-cardioversão de FA — PS agora vs retorno precoce vs plano

```mermaid
flowchart TD
 A["Embolia, sangramento maior, instabilidade ou arritmia sintomática sustentada?"] -->|Sim| B["Emergência ou avaliação urgente monitorizada"]
 A -->|Não| C["ECG e avaliação da recorrência e precipitantes"]
 C --> D{"Recorrência leve com acesso seguro?"}
 D -->|Sim| E["Retorno individualizado e revisar plano de anticoagulação"]
 D -->|Não| F["Avaliação mais rápida; urgência se acesso insuficiente"]
```

Consulte o protocolo de sinalizadores do mesmo pacote para critérios e limites. Reavalie o destino após exames e diante de qualquer piora.


## Navegação

- [`sinalizadores-ambulatoriais-pos-cardioversao-fa-quando-voltar-ao-ps`](/biblioteca/sinalizadores-ambulatoriais-pos-cardioversao-fa-quando-voltar-ao-ps)
- [`recorrencia-leve-pos-cardioversao-fa-retorno-precoce-nao-ps`](/biblioteca/recorrencia-leve-pos-cardioversao-fa-retorno-precoce-nao-ps)
- [`fluxograma-cardioversao-eletiva-anticoagulacao-periprocedimento`](/biblioteca/fluxograma-cardioversao-eletiva-anticoagulacao-periprocedimento)
