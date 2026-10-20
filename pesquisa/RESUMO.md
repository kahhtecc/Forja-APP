# Forja: resumo da pesquisa

## O que foi entregue

| Arquivo | Conteúdo |
|---|---|
| `diretrizes.md` | Diretrizes em PT-BR com fonte `[id]` em cada afirmação. Cobre musculação (variáveis por objetivo, volume, frequência, divisões, progressão, deload), emagrecimento, saúde e 50+, corrida (80/20, zonas por fala/RPE, progressão, C25K, planos de 5k a 42k, taper), ciclismo (zonas de Coggan, FTP 20 min, treinos, semana), luta, atletas (periodização, pliometria, FIFA 11+, Nordic), HIIT/Tabata, mobilidade, RAMP, PAR-Q+ (7 perguntas em PT-BR e regras), sinais de alerta, adaptações para joelho/lombar/ombro e gestação (só alertas). São 46 fontes com link. |
| `parametros.json` | Os mesmos números em JSON válido. Cada bloco aponta para ids em `fontes` (46 entradas, todas referenciadas, nenhuma faltando). Os blocos `limitacoes.*.evitar/substituir_por` e `luta.potencia.exemplos` usam os slugs de `lista-exercicios.tsv` (todos validados). O campo `origem: "convencao"` marca valores que são prática de treinadores, e não número fixado por estudo. |
| `videos.json` | 154 de 154 slugs cobertos: 127 vídeos em PT e 27 em EN, sem IDs repetidos, todos com ID de 11 caracteres tirado de URL real de resultado de busca. |

## Vídeos: o que significa `verificado: true`

- Os 154 estão marcados `verificado: true`. Neste caso, isso quer dizer que **o título que aparece no resultado de busca do YouTube corresponde ao exercício**.
- A checagem por oEmbed **não foi possível**: o WebFetch falhou em todos os hosts (erro de DNS), e o proxy do container bloqueia youtube.com (403).
- Canais identificados pelo título ou pela descrição: Fisioprev (Guilherme Stellbrink, fisioterapeuta, 31 vídeos), Treino Correto (11), Smart Fit (6), YouFisio (3), RTF (2), Nuffield Health, GCN, Catalyst Athletics, Mark Wildman, Viking Strength Systems, Reebok CrossFit ONE, Minha Bike Life Style e outros.
- **Em 81 vídeos o canal está como "não identificado"**, porque o resultado de busca não mostrava o canal. A didática deles não foi avaliada. Sugestão: antes de publicar, conferir esses vídeos no app (ou com `oembed` num ambiente com acesso ao YouTube) e trocar os fracos.
- Correspondências aproximadas: `desenvolvimento-halteres` (versão alternada), `passada-andando` (passada com halteres), `rosca-direta` (barra W), `flexao-inclinada` (mãos no banco), `ponte-pescoco` (bridge & roll de BJJ), `rolo-quadriceps` ("região anterior de pernas") e `alongamento-peito` (peitoral menor).

## Limitações das diretrizes

- Sem leitura de páginas, os números foram conferidos pelos abstracts e trechos que as buscas retornaram e por referências clássicas (NSCA *Essentials*, Allen & Coggan). Alguns pontos não foram lidos no texto integral e estão sinalizados no `diretrizes.md`:
  - doses de alongamento do ACSM (Garber 2011);
  - lista de sinais de alerta do ACOG 804;
  - o posicionamento ACSM 2026, conhecido só pela cobertura de imprensa.
- As estruturas de planos de corrida (semanas, longão) e de luta (rounds, pescoço) são **convenção de treinadores**, coerente com as fontes, e não números de estudo.
- As 7 perguntas do PAR-Q+ são tradução livre da versão oficial em inglês. Existe versão brasileira validada (Schwartz 2021), mas o texto dela não foi obtido.
- As adaptações por lesão são conservadoras e não diagnósticas.
