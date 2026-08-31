# Ambiente Ciência & Ensino

O terceiro ambiente do CorVIA Cardiology Spaces organiza as superfícies científicas e educacionais já existentes sem duplicar backend, conteúdo, permissões ou rotas. Ele é oferecido na decisão de cada novo login e no seletor superior da Home.

## Contrato de navegação

- Completo e Essencial continuam iniciando no **Consultório**.
- Ciência & Ensino inicia em **Descobrir**.
- Trocar de jornada por mouse, teclado ou toque atualiza imediatamente as três camadas funcionais.
- Todas as jornadas mantêm o catálogo integral em **Todas as funções**.
- A identidade usa o coração canônico, o logotipo Cardiology Spaces e o tratamento profissional cadastrado do assinante.

## Cinco jornadas, 21 superfícies reais

| Jornada | Objetivo | Superfícies principais |
|---|---|---|
| Descobrir | Encontrar e relacionar conhecimento | Tudo com Tudo, Biblioteca, Busca, Doenças, Medicamentos, Exames, Calculadoras, Fluxogramas, Diretrizes, Favoritos |
| Evidências | Revisar fontes e fundamento científico | Evidências, Estudos, Diretrizes, Documento científico IA, Biblioteca, Busca, Timeline, Casos, Calculadoras, Exportação |
| Aprender | Estudar de forma contínua e aplicada | Cursos, Trilhas, Casos clínicos, Doenças, Exames, Calculadoras, Diretrizes, Evidências, Galeria, Timeline |
| Ensinar | Preparar educação profissional e ao paciente | Apresentação, Material ao paciente, Casos, Exportação, Documento científico IA, Galeria, Biblioteca, Diretrizes, Trilhas, Favoritos |
| Produzir | Criar conteúdo com rastreabilidade | Documento científico IA, Apresentação, Exportação, Biblioteca, Tudo com Tudo, Evidências, Estudos, Diretrizes, Material ao paciente, Favoritos |

As 21 superfícies protegidas pelo contrato são: `/biblioteca`, `/busca`, `/busca?modo=tudo-com-tudo`, `/documentos-cientificos-ia`, `/diretrizes`, `/evidencias`, `/estudos`, `/doencas`, `/medicamentos`, `/exames`, `/calculadoras`, `/fluxogramas`, `/casos-clinicos`, `/trilhas`, `/trilhas/timeline`, `/material-paciente`, `/cursos`, `/apresentacao`, `/exportar`, `/galeria` e `/favoritos`.

## Comportamento visual e responsivo

- A jornada selecionada permanece iluminada; em desktop, `hover` e foco de teclado iluminam provisoriamente outra jornada e atualizam suas ações, voltando à seleção anterior ao sair.
- As três camadas — **Agora**, **Aprofundar** e **Conexões do conhecimento** — preenchem a área útil sem criar indicadores ou conteúdos fictícios.
- No mobile, o conteúdo importante permanece disponível, o dock é rolável e os rótulos não são comprimidos abaixo de 11 px.
- O tour Cardiology Spaces v2 apresenta o ambiente científico em uma etapa própria.

## Verificação focada

```bash
cd frontend
npm run test:scientific-environment-contract
npm run build
```

O fluxo RC2 também captura o ambiente científico em desktop e mobile e valida as cinco jornadas, o overflow e os atalhos principais.
