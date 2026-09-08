# Correções de findings antigos — checkpoint 2026-09-08

Escopo desta etapa: PRs 700, 715–719 e 723. Foram confrontadas as regras efetivamente compostas na release, não apenas comentários de revisão. O estado anterior ainda reproduzia os problemas clínicos abaixo apesar de `revisado`.

- AL: investigação não realizada não tranquiliza; tipagem indeterminada com clonalidade alterada ganha encaminhamento; AL confirmada exige tratamento em todos os estágios; Mayo IV não equivale a AL-ISS IIIC; retirada de rendimento indevidamente atribuído a cada sítio de biópsia e de venetoclax genérico.
- IAo: intervenção por regurgitação exige grau grave; risco cirúrgico categórico; Classe I e IIb separadas; Marfan com/sem fatores adicionais separado de outras aortopatias.
- ACM: modelos ARVC 2019/2021 e seus desfechos separados; referências pediátricas registradas, limitações explícitas; terapia de IC separada de antiarrítmicos; restrição esportiva condicionada a doença/variante causal; achados elétricos não pontuam automaticamente critérios.
- Sarcoidose: biópsia não universal, alternativa JCS um maior/dois menores, respostas histológicas completas; fluxos de urgência; AHA 2024 com corrigendum e primer 2026.
- QT adquirido: causas sem fármaco reconhecidas; Ray restrito ao subgrupo correto; Tisdale e seus limites explícitos; total manual conferido não é cálculo automático; TV polimórfica tem fluxo imediato; QTc inválido rejeitado; QTc isolado não força PS.
- Prótese mecânica: tamanho/embolia/persistência separados; fibrinólise exige ausência explícita de contraindicação; preferência não supera impossibilidade de AVK; idade e posição participam; INR inadequado também na via aguda; PROACT Xa incluído.
- EAo: risco procedural e FEVE nos caminhos de intervenção precoce; discordância não presume baixo fluxo; idade/modo de intervenção dependem de indicação; EA moderada com cirurgia concomitante contemplada.

Validação: 46 cenários no motor real, incluindo respostas representativas do renderer (select envia strings), passaram. A composição atual de doenças foi usada pelos testes. Os gates de inventário/editorial globais ainda aguardam o fechamento de todo o corpus; este documento não certifica que todos os demais PRs antigos estejam resolvidos.

Fontes: ESC/EACTS VHD2025, erratum EHJ2026 ehag625 (NYHA II–IV, sem mudança de trombo); ESC aorta2024; estudos primários ARVC30915475/33296238 e pediátricos34998950/37781308; AL41353737/38095141; AHA sarcoidose1240/corrigendum1275, primer42475441; Tisdale23716032, AHA ALS2025; PROACT Xa38320162. Identidades bibliográficas e fontes estão nos registros compostos.
