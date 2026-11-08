# Animador — rodada de dados r8 (erros restantes do QA dos 175)

Entrada: QA de 16839d9 (84 limpos, 82 avisos, 9 erros) e o diagnóstico do especialista do motor. Só dados mudaram
(`tools/anim/dados/lote1.json`, `lote3.json`); o motor ficou como estava. Achados que não saem com dados foram para
`pesquisa/motor-pendencias.md` (seção "Rodada de dados r8").

Método: sondas no scratchpad (`r8/rom.py` ROM por instante, `r8/grade.py` grade de ângulos numa chave, `r8/fig4d.py`
geometria da figura 4, `r8/chaves.py` âncoras de pés/mãos por chave, `r8/pen.py` qual peça o corpo atravessa,
`r8/pes.py` antepé quadro a quadro), qa.py do exercício a cada variante e conferência visual (tiras e zoom de 2–4
ângulos) de cada exercício alterado.

## O que mudou

| Exercício | Antes (qa) | Depois (qa) | Mudança nos dados |
|---|---|---|---|
| abdominal-bicicleta | erro: desvio ulnar 51° nos dois punhos | aviso (46–47°) | Na chave de rotação de cada lado, o braço de baixo fica mais baixo e aberto (`bt` [-115,-128], `bta` 70, `ata` −55; espelhado em `bf`/`bfa`/`afa` na chave 2). Mãos continuam presas na nuca ("segura"). |
| alongamento-triceps | erro: rotação do ombro 180° | aviso (só braço encostando na cabeça) | O braço que segura sobe mais (`bt` [165,280], `bta` 0) e a mão fica sobre o cotovelo de cima; chaves novas de subida e descida com o braço que segura aberto pelo lado (a mão não passa na frente do rosto; sem elas o qa acusava rosto coberto 27%). Tempos [0,8, 0,7, 2,6, 0,7, 0,8]. |
| rotacao-toracica | erro: CM fora da base, pelve/costas/joelho "pousados" | aviso | As pernas estavam com o quadril a ~155° (com `t` 90 a coxa em 90 fica paralela ao tronco). Agora 90/90 de verdade: `pf` [0,−90,0], `pt` [2,−88,2], joelho de cima apoiado no de baixo (`pfa` −10); braço de baixo à frente no chão (`bt` [0,0]), o de cima abre como antes (livro aberto). |
| balanco-pernas | aviso: palma virada para baixo | aviso (os mesmos de quadril) | Punho em extensão (`put` −60): a palma fica espalmada na parede, dedos para cima. |
| alongamento-gluteo | erro: rotação externa do quadril 93° | aviso (67°) | Figura 4 refeita pela geometria: tornozelo cruzado apoiado na face da frente/fora da coxa de baixo, logo abaixo do joelho; coxa cruzada com flexão ~110° e abdução ~15° (`pf` [207,4, 90,3, 150], `pfa` 19,6, `cfa` −66,8). Chaves de entrada com joelhos a 104–121° (antes 156°). Os braços continuam ao lado do corpo no chão (abaixá-los levantava o tronco e tirava o CM da base). |
| afundo-halteres | erro: CM fora da base em 3 trechos | limpo | Nas chaves de apoio simples o quadril vai sobre o pé de apoio (`z` ±0,8); chave nova de "empurrar de volta" (pose de pouso com `x` 2,6, `z` ±0,6 para o pé de trás, tronco 3° à frente) antes de o pé da frente voltar. |
| remo-ergometro | erro: abdômen 1,8 cm dentro da "estrutura" | aviso | A peça atravessada era o monotrilho fixo (z 0,43–0,78) — o corpo sentava no topo do banco do dado (h 0,6). Banco h 1,0: o assento fica acima do trilho. Pegada menos profunda (coxa 130, tronco 165, `x` −2,9): flexão do quadril 164° → 150°. |

## Não resolvidos (ver motor-pendencias.md)
- **inchworm**: testadas uma chave por passo de mão (27 chaves, mãos e pés presos nas âncoras), chaves com a mão no ar
  e passos mais lentos; os saltos do antebraço (5–10 cm) continuam porque o motor mistura o braço com a pose livre no
  meio de cada passo de mão. Dados mantidos.
- **maior-alongamento**: o passo de 2 dm do pé de trás na passagem para o posterior é geométrico (12,8 dm entre os pés:
  com o pé de trás fixo ele não alcança o chão; com passada menor as mãos saem do chão). Precisa ser refeito com outra
  variante; dados mantidos.
- **turkish-getup**: não retrabalhado (10 verificações com erro; o kettlebell em pêndulo cai sobre o antebraço — nota
  para o motor).

## Resultado do QA dos 175
qa.py completo (4 processos, 24 fps) depois das mudanças: **85 limpos, 87 só com aviso, 3 com erro** (antes 84 / 82 / 9).
Comparação exercício a exercício com o QA anterior (`pesquisa/qa-resultado.json` de 16839d9): nenhum exercício piorou
(categoria ou gravidade); mudaram só os sete alterados — afundo-halteres erro → limpo; abdominal-bicicleta,
remo-ergometro, rotacao-toracica, alongamento-gluteo e alongamento-triceps erro → aviso; balanco-pernas segue com os
mesmos avisos de quadril (a palma agora está na parede). Erros restantes: turkish-getup, inchworm, maior-alongamento.
