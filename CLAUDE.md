# MeuCardio — instruções permanentes

Este projeto é uma plataforma clínica de cardiologia, de uso independente,
sem vínculo institucional. Trabalho de expansão de biblioteca científica.

## Regra permanente de autonomia
Quando eu pedir para "continuar expandindo a biblioteca" ou similar, você deve
trabalhar em QUALQUER uma das seis frentes abaixo (não só documentos de texto):

1. **content/<Tema>/*.md** — documentos da biblioteca científica (protocolo padrão já em uso).
2. **galeria/metadados.json** + arquivo de imagem em galeria/<pasta>/ — achados de imagem
   (ECG, eco, TC, RM, radiografia, cateterismo). Imagem só pode vir de fonte de acesso
   aberto com licença verificável (Wikimedia Commons, PMC Open Access) — nunca gerada por
   IA. Confira a licença de cada imagem antes de baixar, salve a atribuição completa.
3. **exames/metadados.json** — marcadores laboratoriais e exames cardiológicos
   (o que mede, valor de referência, indicação, interpretação, limitações).
   O campo `category` é taxonomia fixa, sempre um destes três valores —
   nunca inventar categoria nova: `laboratorial` (biomarcador de sangue/urina),
   `metodo_grafico` (gera traçado sem imagem — ECG, teste ergométrico, Holter,
   MAPA), `imagem` (gera imagem — eco, TC, RM, radiografia, cateterismo; o
   achado específico vai na Galeria, aqui é sobre o exame em si).
4. **evidencias/metadados.json** — registros de evidência: uma recomendação pontual
   por entrada, com classe (I/IIa/IIb/III), nível (A/B/C), sociedade, ano e referência
   completa — não é o documento inteiro, é a afirmação específica.
5. **estudos/metadados.json** — catálogo de ensaios clínicos, revisões sistemáticas
   e metanálises: resumo, principais achados (com números reais, não vagos) e
   implicação clínica, sempre em texto próprio — nunca copiar abstract original.
6. **Farmacologia** (dentro de content/) — preencher medicamentos que ainda faltam
   dose/apresentação/ajuste renal, ou cadastrar medicamento novo ainda ausente.

Para cada entrada em JSON (galeria/exames/evidências/estudos), o slug precisa ser
único dentro do arquivo — confira o JSON existente antes de adicionar, para não
duplicar. Consulte COBERTURA.md para decidir qual das seis frentes está mais fraca
e priorize por aí, mas sinta-se livre para alternar entre frentes na mesma sessão.

Processo, igual para as seis:
1. Escolher o item mais fraco/ausente sozinho, sem perguntar.
2. Pesquisar (WebSearch/WebFetch) fonte real — diretriz mais atual (ESC, AHA/ACC,
   SBC) para conteúdo clínico; Wikimedia Commons/PMC Open Access para imagem;
   PubMed/journal original para estudo — cruzando pelo menos duas fontes quando
   possível.
3. Escrever seguindo exatamente o padrão de front matter/JSON dos itens já
   existentes na mesma pasta (review_status: revisado, source_refs/reference
   com citação completa e verificável).
4. Nunca inventar dose, valor numérico, licença de imagem ou achado que não veio
   de uma fonte real consultada nesta sessão. Se não conseguir confirmar um dado
   específico, simplesmente não incluir esse dado — não escrever nota de aviso,
   não pedir verificação humana no texto, só omitir.
5. Fazer git add + git commit com mensagem descritiva.
6. Fazer git push.
7. Sem pausar para perguntar "posso continuar?" — seguir direto para o
   próximo item mais fraco, repetindo o ciclo, até eu mandar parar.

## O que nunca fazer sem perguntar
- Nunca alterar código de backend/frontend nesta rotina (só content/).
- Nunca reescrever ou apagar documento já existente sem justificativa clara.
