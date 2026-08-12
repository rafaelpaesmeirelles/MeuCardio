# CorVIA Clinical Command Center — Launch V1

## Princípio de produto

O CorVIA começa pela necessidade do médico, não pelo paciente.

A Home deve permitir, em poucos segundos:

1. **Buscar** conhecimento, condição, medicamento, exame, guideline, estudo ou outro conteúdo.
2. **Perguntar** ao CorVIA quando a necessidade exige raciocínio/explicação.
3. **Agir**: prescrever, solicitar exames, emitir documentos, calcular, abrir emergência e demais fluxos.
4. **Retomar contexto** sem presumir uma rotina clínica específica.
5. **Organizar a rotina profissional** por meio do Assistente Pessoal, incluindo agenda, deslocamento e comunicação quando os dados reais e as permissões estiverem disponíveis.

## Camadas distintas

- **CorVIA Intelligence**: contexto científico/clínico automático e conhecimento conectado.
- **Assistente Pessoal**: continuidade da rotina profissional, agenda, deslocamento, comunicação e organização.
- **Clinical Command Bar**: entrada universal para buscar, perguntar e agir.
- **Knowledge Graph / Tudo com Tudo**: relações reais entre entidades, sem transformar toda a interface em um grafo.

## Regra de dados

A interface não deve inventar guideline, alerta, contagem, trânsito, compromisso, mensagem ou conteúdo. Estados vazios devem ser explícitos e dados externos só aparecem quando a integração real estiver disponível.

## Escopo desta branch

- nova Home universal;
- novo visual de lançamento da Home;
- navegação por intenção do médico;
- rail CorVIA Intelligence / Assistente Pessoal;
- Radar Clínico;
- Ações Rápidas;
- retomada de contexto local por usuário/browser;
- exploração por área;
- dock móvel de Ação + Assistente Pessoal;
- preservação das rotas e módulos existentes.

Nenhum deploy em produção é autorizado por este documento.
