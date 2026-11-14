# Aprimoramento final das animações 3D

Entrada: revisão independente (19 reprovados), relatórios do motor e do animador pós-revisão, QA dos 175 de 135b0c1
(88 limpos, 86 avisos, 1 erro). Commits pequenos, um por melhoria (7f5ca6d … ). Método: antes/depois com o motor de
135b0c1 (cópia em `<scratch>/ap/head`) e o atual, zoom de 2 a 3 ângulos (`<scratch>/pr/ab.sh`), sondas numéricas
(`<scratch>/ap/pen2.py`: mão dentro da cabeça pelo teste de interior do QA; `sola2.py`; `joelho.py`) e QA um a um
(`<scratch>/ap/qa_ids.sh` + `cmp.py`, comparação achado a achado com `pesquisa/qa-resultado.json` anterior).

## 1. Bugs do motor (todos os cinco do animador)

| Bug | Correção | Medida antes → depois |
|---|---|---|
| "segura" na cabeça: palma 2–7 cm dentro do crânio, mão girando só 75 % | Distância da pele pelo ponto mais externo num cilindro estreito em volta da reta da palma (antes: percentil 80 dos pontos a < 1 dm); 88 % de giro atrás da cabeça; o polegar (que em repouso sai do plano da palma para o lado dela) afasta só até sair da pele; alvo novo "testa" | mão dentro da cabeça (teste de 24 vizinhos do QA): abdominal-bicicleta 2,0 → 0 cm, isometria-pescoco 1,7 → 0 cm. Visual: as mãos envolvem a nuca (antes os dedos ficavam no ar) |
| "segura" fecha sempre em 0,55 | Cada dedo fecha para o lado da palma até encostar na pele do alvo, sem atravessar (varredura + busca binária com KD-tree); sem contato, para onde passa mais perto; na cabeça no máx. 0,45 | alongamento-quadriceps: dedos fechados em volta do tornozelo (antes abertos); borboleta: mãos fechadas nos pés |
| Pé não gira em torno da canela | Campo `pgf`/`pgt` (giro do pé no eixo longo, + = sola para dentro), interpolado como os outros ângulos | borboleta com 75: sola esq. (0,15, −0,31, −0,94) → (−0,7, −0,62, −0,34) (para dentro) |
| (achado) joelho "em ponta" na borboleta | Com a canela fora do plano da coxa (`cfa` ≠ `pfa`) a metade de baixo do fêmur gira até o joelho dobrar no plano coxa-canela (dobradiça), também na IK da perna | ângulo dobra do fêmur × canela −145° → −29°; joelho arredondado; abdutora: canelas fora do estofado (aviso → limpo) |
| `nivelar_de_lado` só com todas as chaves de lado | Nivelamento em cada chave com "lado" | fuga-quadril alternando os lados com o quadril no chão nas duas fugas |
| Pegada da barra fixa depende do braço FK | Com os pés no chão o corpo gira em torno dos pés até a pegada JÁ resolvida pela IK (chaves e quadros) | remada-invertida com os braços quase esticados no fundo: barra fora do túnel 8,7 cm (erro) → 1,7 cm (aviso) |

Dados refeitos: **borboleta** (`pgf`/`pgt` 75: solas para dentro, mãos fechadas nos pés, joelhos redondos),
**fuga-quadril** (de costas → camarão para um lado → de costas → camarão para o outro; aviso de pernas 5,4 cm/12 quadros →
4,7 cm/2 quadros), **abdominal-bicicleta** e **isometria-pescoco** sem mudar os dados (o motor tirou a mão do crânio).

## 2. Conferência das 10 correções de motor da rodada pós-revisão
Tiras de 6 quadros com o motor atual: rosca-direta, rosca-halteres, rosca-martelo, rosca-elastico (cotovelos junto ao
corpo na câmera 75), supino-maquina (alavanca com pivô no alto, braços se movem), eliptico (alça visível nas duas mãos),
escada (mãos no corrimão), hack (pegadores laterais), corda (arco em C, passa sob os pés), alongamento-panturrilha (mãos
nos degraus do espaldar). Todas conferem; nenhum defeito novo.

## 3. Turkish-getup
Testada variante com menos extensão do quadril de trás nas chaves 3/7 (`pt` −40 → −30): piorou (pop de 8 cm no
antebraço, pele abaixo do chão, base do joelho). Ficou como estava: único erro do QA, aprovado na revisão visual com
ressalva; o que falta está em motor-pendencias.md (rodadas r10/r11).

## 4. Avisos
- Falso positivo ajustado no QA (`apoio/pousada`): membros (coxa, joelho, antebraço) parados a mais de 7 cm de uma superfície
  estão claramente no ar — coxas e joelhos na prancha/flexão (11–12 cm), joelhos abertos na borboleta (9 cm). Na tela de
  720 px 1 cm ≈ 3 px: acima de 7 cm o vão é óbvio; o defeito "apoiado em lugar invisível" é o vão de 3 a 7 cm. O tronco
  (pelve/costas/cabeça) continua até 15 cm.
- Reais eliminados pelo motor: abdutora (canelas no estofado), remada-invertida (sem a rotação interna do ombro quando os
  braços mudam), mão no crânio (bicicleta/isometria).
- Restantes: penetração rasa em aparelhos (1–1,5 cm), braço encostando no tronco (teste satura, já documentado como só
  aviso), ROM de antebraço/punho em pegadas (ligado ao achado abaixo).

## 5. Naturalidade
O motor já aplica: excêntrica mais lenta (ease "exc" automático em trechos ≥ 1,3 s, "con" de 0,5 a 1,3 s), pescoço e
cabeça com atraso (follow-through), respiração/peso/olhar na camada "vida" (1 em isometria e mobilidade, 0,4 em força),
balística nos voos. Nesta rodada não houve mudança global de ritmo (qualquer ease global piorava o QA nas rodadas
anteriores, ver motor-pendencias.md).

## Achado grande em aberto: dedos em hiperextensão nas pegadas
O eixo de flexão dos dedos leva a ponta para o lado oposto da palma (conferido: mão espalmada no chão, palma para baixo e
unhas para cima; o estado "pegada" levanta a ponta do dedo acima do punho). As pegadas parecem certas de longe porque o
túnel é medido nos dedos como eles dobram, mas de perto a mão envolve o cabo com as unhas para dentro. Inverter o eixo
para todos deu pegadas anatômicas na barra fixa, mas 7 erros novos em 107 exercícios (polegar, túnel 1,2–1,8 cm fora,
rosto coberto na puxada, punho) e foi revertido. O "segura" já usa o sentido anatômico. Próximo passo descrito em
motor-pendencias.md.

## QA dos 175 (antes → depois)
| | Limpos | Só aviso | Com erro | Avisos (total) | Erros (total) |
|---|---|---|---|---|---|
| Antes (135b0c1) | 88 | 86 | 1 | 224 | 6 |
| Depois do motor e dos dados (qa.py antigo) | 89 | 85 | 1 | — | — |
| Depois, com o critério de "pousada" ajustado | **94** | **80** | **1** | **190** | **5** |

Comparação exercício a exercício (`<scratch>/ap/cmp.py`): nenhuma regressão de status. De aviso para limpo: abdutora
(motor: canelas fora do estofado) e, pelo critério de pousada, roda-abdominal, flexao, abdominal, afundo, prancha.
O único erro continua o turkish-getup (5 verificações; antes 6, mesmas medidas).
