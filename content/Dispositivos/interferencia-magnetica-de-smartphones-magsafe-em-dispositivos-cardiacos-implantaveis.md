---
title: "Interferência Magnética de Smartphones (MagSafe) em Dispositivos Cardíacos Implantáveis"
slug: interferencia-magnetica-de-smartphones-magsafe-em-dispositivos-cardiacos-implantaveis
theme: "Dispositivos"
kind: estudo
review_status: revisado
source_refs: ["Wegner FK, Korthals D, Kreimer F, Wolfes J, Ellermann C, Martinovic M, et al. Preventing smartphone induction of magnet mode in cardiac implantable electronic devices. Europace. 2025;27(8):euaf170. DOI: 10.1093/europace/euaf170. PMID: 40795264. PMCID: PMC12396591", "Censi F, Boriani G. Magnetic interference from consumer devices: a renewed challenge for the safety of cardiac implantable electronic devices [editorial]. Europace. 2025;27(8):euaf165. DOI: 10.1093/europace/euaf165. PMID: 40759607", "Nadeem F, Nunez Garcia A, Thach Tran C, Wu M. Magnetic Interference on Cardiac Implantable Electronic Devices From Apple iPhone MagSafe Technology. J Am Heart Assoc. 2021;10(12):e020818. DOI: 10.1161/JAHA.121.020818. PMID: 34074132. PMCID: PMC8477860"]
legacy_source: "Documento novo, escrito em 09/09/2026. O tema Dispositivos já cobre interferência eletromagnética em cenários médicos controlados (ressonância magnética não condicional, radioterapia, cirurgia com bisturi elétrico), mas não a interferência de um objeto de uso diário e crescente no bolso do paciente — o smartphone com carregamento sem fio por ímã."
---

# Interferência Magnética de Smartphones (MagSafe) em Dispositivos Cardíacos Implantáveis

## Por que isto é diferente da interferência já conhecida
O sistema já documenta interferência eletromagnética em cenários **controlados e médicos**: ressonância magnética em dispositivo não condicional, radioterapia oncológica, bisturi elétrico em cirurgia. Nesses cenários há equipe treinada, protocolo e, em geral, tempo para programar o dispositivo antes da exposição.

O smartphone é diferente por três razões práticas: **o paciente carrega o objeto o dia inteiro, encostado no próprio corpo, sem nenhuma equipe médica por perto**; a tecnologia de ímã para carregamento sem fio (Apple MagSafe, lançada em 2020 no iPhone 12) **se espalhou para toda a linha do fabricante e para acessórios de terceiros** (capinhas magnéticas, carteiras magnéticas, suportes veiculares); e o campo magnético gerado — mais de 50 gauss no arranjo do MagSafe — **é da mesma ordem de grandeza usada propositalmente para acionar o modo magnético (reversão) dos próprios dispositivos** em ambiente hospitalar.

## O que é o "modo magnético" e por que ele existe
Todo marcapasso e cardiodesfibrilador implantável (CDI) tem um sensor magnético (reed switch ou sensor Hall) desenhado para responder a um ímã de intensidade suficiente colocado sobre o gerador — é o recurso que a equipe médica usa, de propósito, para suspender temporariamente a terapia durante procedimento com bisturi elétrico ou para interrogar o dispositivo. A resposta muda por tipo de dispositivo:
- **No CDI**: o modo magnético **inibe as terapias de taquiarritmia** (choque e ATP) — o dispositivo continua monitorando, mas não trata.
- **No marcapasso**: o modo magnético costuma levar à **estimulação assíncrona em frequência fixa** (não sincronizada ao ritmo próprio do paciente).

O problema de segurança não é o ímã em si — é ele ser acionado **sem intenção, por um objeto do dia a dia**, num paciente que depende da terapia do CDI estar ativa.

## O achado original, em pacientes reais: Nadeem et al., 2021
O primeiro estudo a demonstrar o problema com o iPhone 12 Pro Max (Nadeem F et al., J Am Heart Assoc. 2021;10(12):e020818, PMID 34074132) teve componente **in vivo** e **ex vivo**:
- **In vivo**: o iPhone 12 Pro Max foi colocado diretamente sobre a pele, no bolso do gerador, em pacientes consecutivos com CIED já implantado, e o efeito foi verificado por interrogação do dispositivo. **Interferência magnética clinicamente identificável em 3 de 3 pacientes (100%)**.
- **Ex vivo**: dispositivos das principais fabricantes, ainda na embalagem fechada, testados contra o mesmo aparelho — interferência em **8 de 11 dispositivos (72,7%)**.

Os autores concluíram que a tecnologia MagSafe do iPhone 12 Pro Max **pode causar interferência magnética em CIED com potencial de inibir terapia salvadora de vida** — é a frase que motivou toda a linha de pesquisa seguinte.

## O estudo mais recente e mais amplo: Wegner et al., 2025
Wegner FK et al. (Europace. 2025;27(8):euaf170, PMID 40795264, PMCID PMC12396591), da Universidade de Münster, testaram a hipótese de que uma barreira de blindagem magnética simples evitaria a interação — e ampliaram o desenho para comparar fabricantes de smartphone e posição de implante.

**Método**: 16 CIED (6 marcapassos e 10 CDI) de todos os principais fabricantes, implantados consecutivamente em posição **subcutânea** e **submuscular** num tórax porcino isolado, conectados a um simulador cardíaco interativo. Dois smartphones (Apple iPhone 14 e Google Pixel 8 Pro) foram posicionados sobre o local do implante, com e sem capinha magnética, e registrado se o modo magnético era induzido.

**Resultados, número a número**:
- **iPhone 14 sobre implante subcutâneo: induziu modo magnético em 7 de 16 dispositivos (44%)**
- **iPhone 14 dentro de capinha magnética, sobre implante subcutâneo: 6 de 16 dispositivos (38%)** — a capinha magnética adicional não aumentou o risco além do próprio ímã do MagSafe
- **Uma placa de aço fino de 1 mm colocada na parte de trás do smartphone preveniu a indução em 100% dos casos testados**
- **Google Pixel 8 Pro (padrão Qi, sem MagSafe): 0 de 16 dispositivos**, mesmo com capinha magnética
- **Implante em posição submuscular: nenhuma indução de modo magnético por nenhum dos dois smartphones**, em nenhum caso
- Todos os dispositivos continuaram interrogáveis normalmente e responderam ao ímã dedicado de CIED depois do teste, ou seja, o sensor magnético em si não foi danificado

**Conclusão dos autores**: o iPhone induz modo magnético em quase metade dos CIED implantados de forma subcutânea, por causa do ímã do MagSafe — nem o smartphone com padrão Qi puro, nem a capinha magnética isolada, carregam o mesmo risco. Posição submuscular do gerador ou blindagem com placa de aço evitam a indução. **Os autores alertam que o futuro padrão Qi2.0** (que a indústria está migrando a adotar de forma mais ampla, inclusive fora do ecossistema Apple) **pode agravar o risco de interação**, ao incorporar array de ímãs semelhante ao MagSafe em mais fabricantes.

## O editorial que acompanha o estudo
Censi F, Boriani G (Europace. 2025;27(8):euaf165, PMID 40759607) comentam o estudo de Wegner et al. e reforçam o ponto estrutural do problema: **fabricantes de eletrônica de consumo, em geral, não projetam seus produtos considerando implante médico, e o fabricante do dispositivo médico não tem como prever toda tendência tecnológica futura**. Os autores defendem que fechar essa lacuna exige colaboração contínua entre engenheiros, médicos, fabricantes dos dois lados e órgãos regulatórios — não é um problema que se resolve de uma vez.

## O que muda na prática clínica
- **Orientar o paciente a não carregar o smartphone no bolso da camisa ou próximo ao gerador**, especialmente aparelhos Apple com MagSafe — a orientação vale mesmo sem capinha magnética adicional, porque o ímã que interfere é o do próprio telefone, não da capa.
- **Posição de implante submuscular** (quando essa for uma opção clínica razoável para o caso) reduziu a indução a zero nos ensaios ex vivo — um fator a mais na decisão de profundidade do implante em paciente com hábito conhecido de manter o telefone perto do bolso do gerador.
- **Blindagem física** (placa fina de aço na parte de trás da capa do telefone) é uma medida de baixo custo e demonstrada eficaz nesse modelo experimental, para quem não pode ou não quer trocar o hábito de uso.
- **A interferência é reversível e não danifica o dispositivo** — não é motivo de pânico, e sim de orientação simples de uso, análoga à orientação já dada para detectores de metal e fones de ouvido com ímã.
- **Esta não é uma contraindicação a nenhum smartphone específico** — é uma característica física conhecida do arranjo de ímãs do MagSafe, documentada por fabricante e por modelo de dispositivo cardíaco nos próprios estudos.

## Limitações que a leitura precisa levar em conta
- O estudo de Wegner et al. é **ex vivo**, em tórax porcino isolado com simulador cardíaco — reproduz a geometria de implante e a resposta do sensor magnético, mas **não mede desfecho clínico em paciente vivo, com movimento e variação postural do dia a dia**.
- O estudo de Nadeem et al. tem componente in vivo, porém com **amostra pequena** (3 pacientes) — suficiente para demonstrar o fenômeno, insuficiente para estimar a frequência real do problema na população de portadores de CIED.
- **VERIFICAÇÃO HUMANA NECESSÁRIA**: nenhum dos dois estudos relata caso real de choque omitido ou terapia inibida com desfecho clínico adverso atribuído especificamente à interferência do MagSafe fora do ambiente experimental — a preocupação é de segurança teórica bem demonstrada em modelo, não (ainda) de série de eventos clínicos publicada.
