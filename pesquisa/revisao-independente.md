# Revisão visual independente das animações 3D (175 exercícios)

Revisor independente (não participou da produção). Critérios: (a) mãos segurando de verdade; (b) apoios reais (nada flutuando nem apoiado no vazio);
(c) pose humanamente possível e movimento reconhecível; (d) interpenetração corpo×corpo e corpo×aparelho; (e) aparelho correto e no lugar.

Método: tira de 6 quadros do ciclo (360 px, `humano.py --tira 6`) de cada exercício, mais zoom das duas mãos em 4 instantes (0, 0,25, 0,5, 0,75 do ciclo; `zoom.py`)
e zoom de corpo inteiro de outros ângulos nos suspeitos. Ordem: turkish-getup, os 88 com aviso do QA (por gravidade), depois os 86 limpos.
Nada foi corrigido: só revisão. Gravidade: **grave** = defeito que o usuário vê na hora (mão vazia, apoio no vazio, atravessar corpo/aparelho grande, pose impossível);
**média** = visível ao prestar atenção; **leve** = detalhe.

Revisados: 49 de 175 — APROVADO 41, REPROVADO 8.

| # | exercício | veredito | gravidade | defeito visto | fase/quadro | causa provável |
|---|---|---|---|---|---|---|
| 2 | postura-crianca | APROVADO |  | sem defeito visível (ajoelhado → criança → volta; mãos no chão) | — | — |
| 3 | flexao-diamante | APROVADO |  | mãos juntas no chão, corpo em prancha, descida coerente | — | — |
| 4 | prancha | APROVADO |  | prancha em antebraços estável, apoios no chão | — | — |
| 5 | superman | APROVADO | leve | amplitude exagerada (pernas e braços altos demais, arco forte), mas possível | 0,3–0,7 | dados (amplitude) |
| 6 | remada-invertida | APROVADO |  | mãos fechadas na barra, pés no chão, peito sobe até a barra | — | — |
| 7 | mesa-flexora | APROVADO |  | mãos nos pegadores, rolo no tendão, flexão de joelho coerente | — | — |
| 8 | hack | REPROVADO | grave | uma das mãos fica fechada no ar, sem pegador (só a outra segura); mãos na altura das coxas e não nos pegadores dos ombros | todo o ciclo (zoom mão t 0–0,75) | motor (pegador do hack só para uma mão / "maos":1) + dados |
| 9 | flexao | APROVADO |  | sem defeito visível | — | — |
| 10 | torcao-coluna | REPROVADO | grave | a mão que deveria segurar o joelho fica aberta, dedos espalhados, flutuando ao lado do joelho (não há "segura" nos dados) | 0,25–1,0 (torção) | dados (falta "segura" mao_t→joelho_f) |
| 11 | prancha-lateral | REPROVADO | grave | apoio declarado no cotovelo, mas o corpo está apoiado num punho fechado com o antebraço vertical (cotovelo no ar): prancha lateral "sobre o soco", não existe assim | ciclo inteiro | dados ("maos": {"t":"punho"} + bt [0,90] com rol 70) / motor (cotovelo_t não desce ao chão) |
| 13 | alongamento-gluteo | APROVADO | leve | braços cruzam perto da coxa (mãos atrás da coxa ok); antebraço roça o tronco | 0,5–0,8 | dados |
| 14 | remo-ergometro | APROVADO |  | duas mãos fechadas no puxador, carro e pés coerentes | — | — |
| 15 | arremesso-rotacional | REPROVADO | média | na preparação a bola entra no quadril/abdômen (metade da bola dentro do corpo) e o antebraço de trás atravessa o tronco | 0–0,2 e 0,9–1,0 (carga) | dados (bola muito colada ao quadril; tr/bf da carga) |
| 16 | abdominal | APROVADO | leve | antebraços pairando ~3 cm acima do chão no início (parecem apoiados) | 0 | dados |
| 18 | elevacao-quadril | APROVADO | leve | barra encosta/entra um pouco nas coxas no fundo; mãos seguram a barra | 0 | motor (colisão barra×coxa) |
| 19 | russian-twist | APROVADO | leve | mãos abertas soltas (normalmente unidas/segurando peso); antebraço roça o tronco nas viradas | 0,1 e 0,9 | dados |
| 20 | rosca-scott | APROVADO |  | cotovelos no apoio (vista de trás confirma), pegada fechada | — | — |
| 21 | paralelas | APROVADO |  | mãos nas barras, joelhos dobrados, descida e subida coerentes | — | — |
| 22 | hiperextensao | APROVADO | leve | flexão do tronco no fundo muito profunda (cabeça quase no piso do aparelho), possível | 0,5–0,7 | dados |
| 23 | pallof | APROVADO | leve | vista frontal: a prensa (empurrar para a frente) quase não se lê; mãos seguram o pegador | ciclo | dados (câmera) |
| 24 | alongamento-panturrilha | REPROVADO | grave | as mãos atravessam o espaldar: degraus passam por dentro da palma/pulso, braços do outro lado das barras (não apoia nem segura) | todo o ciclo | dados (distância do corpo ao espaldar / mãos) + motor (sem colisão mão×degrau) |
| 25 | mountain-climber | APROVADO |  | mãos no chão, troca de pernas coerente | — | — |
| 26 | nordico | APROVADO |  | tornozelos presos, queda controlada com amparo das mãos | — | — |
| 27 | abdominal-bicicleta | REPROVADO | média | mãos "atrás da cabeça" com dedos abertos esticados no ar e a mão entrando no crânio | 0,25–0,75 | motor ("segura" nuca sem mão espalmada) / dados |
| 28 | maior-alongamento | APROVADO |  | afundo com mão no chão, rotação com braço para cima, isquiotibiais; coerente | — | — |
| 30 | agachamento-goblet | APROVADO |  | duas mãos nas alças do kettlebell, agachamento profundo coerente | — | — |
| 31 | roda-abdominal | APROVADO |  | mãos nas manoplas, roda no chão, joelhos apoiados | — | — |
| 33 | circulos-quadril | APROVADO | leve | círculo do quadril pequeno, pouco visível | ciclo | dados (amplitude) |
| 34 | flexao-joelhos | APROVADO |  | sem defeito visível | — | — |
| 36 | power-clean | APROVADO |  | chão → quadril → rack frontal → volta; pegada fechada | — | — |
| 37 | escada | REPROVADO | grave | mãos abertas por baixo do corrimão, sem segurar; corrimão atravessa punho/antebraço; degraus parecem um bloco ao lado das pernas | todo o ciclo | motor (corrimão da escada x IK da mão) + aparelho |
| 38 | triceps-banco | APROVADO |  | mãos espalmadas na borda do banco, pés no chão | — | — |
| 39 | bike-subida | APROVADO |  | em pé nos pedais, mãos nas manoplas | — | — |
| 40 | agachamento-barra | APROVADO |  | vista de trás: pegada larga na barra apoiada no trapézio, agachamento correto | — | — |
| 43 | alongamento-lateral | APROVADO |  | mão na cintura, braço por cima, inclinação lateral coerente | — | — |
| 46 | pike-pushup | APROVADO |  | mãos no chão, quadril alto, cabeça desce entre as mãos | — | — |
| 47 | cadeira-flexora | APROVADO |  | mãos nos pegadores, rolo atrás dos tornozelos, flexão coerente | — | — |
| 48 | afundo | APROVADO |  | sem defeito visível | — | — |
| 49 | barra-supinada | APROVADO | leve | subida termina com a barra na testa (queixo não passa da barra) | 0,4–0,6 | dados (amplitude) |
| 50 | rosca-direta | APROVADO |  | pegada fechada, cotovelo junto ao corpo | — | — |
| 51 | tempo-run | REPROVADO | média | no balanço dos braços a mão/antebraço passa por dentro do corrimão lateral da esteira | 0,25–0,5 (cada passada) | dados (largura/altura do balanço) + motor (sem colisão mão×corrimão) |
| 52 | rolo-quadriceps | APROVADO |  | coxas no rolo, antebraços no chão | — | — |
| 53 | barra-fixa | APROVADO | leve | subida termina com a barra na altura dos olhos (queixo não passa da barra) | 0,4–0,6 | dados (amplitude) |
| 54 | abdutora | APROVADO | leve | joelhos encostam um pouco dentro do estofado (≈2 cm) | ciclo | motor (colisão perna×estofado) |
| 55 | ponte-unilateral | APROVADO |  | sem defeito visível | — | — |
| 56 | swing | APROVADO |  | duas mãos na alça, kettlebell entre as pernas e até a altura do ombro | — | — |
| 57 | abdominal-infra | APROVADO |  | sem defeito visível | — | — |
| 59 | ponte-gluteo | APROVADO |  | sem defeito visível | — | — |
| 60 | terra | APROVADO |  | barra do chão ao quadril junto às pernas | — | — |
