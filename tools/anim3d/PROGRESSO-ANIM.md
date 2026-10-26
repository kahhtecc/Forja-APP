# Progresso: animações 3D profissionais (ANIMADOR)

Referência: `pesquisa/animacao-3d-profissional.md`. Scratch: `<scratchpad>/an/` (base = antes, folhas de contato).

## Etapas
- [x] 1. Motor: curvas (tangentes, easing, amostragem uniforme, atraso, vida, slerp dos braços, balística)
- [x] 2. Motor: pops (barra_modo, plantar, livre contínuo, dedos dos pés, apoio explícito)
- [x] 3. Motor: câmera por família, chão com marcas, piso rolante, motion blur/30 fps, pontilhado fixo, encode
- [x] 4. Aparelhos: alavancas rígidas, kettlebell em pêndulo, enquadramento sem torres
- [x] 5. qa.py criado (também no CI, só avisa); rodadas completas: <scratch>/an/tools/qa_all.sh <tag>
- [x] 6. Dados (rodadas 1 e 2, ver commits): face-pull, monster-walk, supino-maquina, salto-distancia e famílias
- [x] 7. Revisão visual dos 175 (rodadas 1 e 2 completas com folhas de contato)
- [x] 8. Render de produção no CI (run 40152840974, juntar e0fad20: 175 MP4 h264/yuv420p/faststart 720px, 141 a 24 fps e 34 a 30 fps, conteudo2 versão 5) e folhas de contato dos 175 conferidas

## Notas
- IK refinado (ossos intermediários não colineares davam até 6 cm de erro: era a causa de pés/mãos escorregando).
- FK preguiçosa (só recalcula a cadeia que mudou): QA ~10 s/exercício.
- Âncora única por apoio contínuo (antepé/pegada fixos), assentar_apoios por quadro, polo do joelho/cotovelo contínuo.
- Ângulos sem desenrolar (como a prévia 2D): braço de -45 a 150 passa pela frente.
- Dados já corrigidos: face-pull, monster-walk, supino-maquina (cam), crucifixo, peck-deck, alongamento-triceps, salto-distancia (volta andando).
- Dados: um exercício por linha (tools/anim/dados/*.json); helper em <scratch>/an/tools/dados.py.
- Desfoque: 4 subquadros pré-multiplicados (2 subquadros davam "fantasma" e chuvisco).
- QA motor antigo (bea8da2): 81 erros, 44 avisos, 50 limpos (233 skate, 88 pop, 59 flutua, 28 barra, 26 congelado, 24 chão, 19 idênticas, 8 rosto).
- plantar re-chamado (alcançar/sem_atravessar) acumulava o peso 1-(1-w)^n: agora mistura da pose livre guardada (box-jump 4,6 cm resolvido).
- QA motor novo final (q8): 1 erro (inchworm), 9 avisos (congelados em isometrias, flutuação ≤1,3 cm), 165 limpos.
- Pendências conhecidas: inchworm (mãos andam num passo longo por trecho; skate 3,4 mm/quadro); corda ainda parece aro; alternância de mãos no motor testada e revertida (piorou o QA).

## Rodada 7 — motor (especialista do motor)
Entrada: pesquisa/auditoria-lote{1,2,3}.md (falhas sistêmicas S1…S12). Campos novos documentados no docstring de humano.py.
Ferramentas no scratchpad (`<scratch>/m7/`): zoom.py (render de perto de mão/pé/corpo num instante), smoke.py (175 sem render),
sondas de pegada/barra/tronco, qa_ids.sh.

### Feito no motor (commits 5f2aa76 … rodada 7)
1. Pegada real: curvatura de cada dedo calibrada para o raio do implemento (corda 0,10 … pegador 0,25), centro da pegada =
   centro do túnel dos dedos médio/anelar (prega da base dos dedos), polegar fechando por cima, eixo do implemento = linha dos
   nós dos dedos; punho desvia no máx. ~12° e o resto vira cabo na diagonal da palma. Barra fixa: mãos presas em todo quadro,
   corpo sobe se os braços não alcançam, cabeça passa por trás da barra. IK das duas mãos: kettlebell pela alça, bola entre as
   palmas abertas (convergem até o diâmetro), halter único (francês), triângulo, corda, puxador, guidão, alças do elíptico,
   corrimão da escada, postes do trenó, manoplas da roda, pegadores de leg press/cadeiras/abdutora/mesa flexora/panturrilha
   sentado/hack. Implemento sempre preso à mão. Bola com "voo" (soltura, parábola, quique e retomada).
2. Mãos livres: estados "rel" (relaxada, levemente fechada), "semi" (corrida/saltos), "punho" (lutas), automáticos por id ou
   por "maos"; punho independente ("puf/put", "pdf/pdt", limites AAOS); mão apoiada com giro ("dedos": "tras"…); "segura"
   (mão presa a pé, canela, joelho, coxa, cotovelo, cintura, nuca por IK).
3. Apoio do tronco: "apoio" aceita pelve/gluteo/costas/cabeca/lado/joelho/cotovelo; detecção automática de deitado
   (pelve+costas+cabeça) e sentado (glúteo); o corpo assenta na superfície real (assento, banco, chão) nas chaves e em todo
   quadro (peso contínuo); cabeça encosta no banco; pés/mãos declarados descem até a superfície (rol, tronco apoiado); dedos do
   pé dobram antes do apoio e o pivô é a base dos dedos (sem pé de bailarina).
4. Limites anatômicos suaves: joelho 160 (no plano), cotovelo 150 (3D), quadril (extensão/abdução), coluna, pescoço, punho;
   clavícula limitada a ~13° com braços acima da cabeça (pescoço visível).
5. Colisão: cabeça x barra fixa, halter x coxa/tronco (mão se afasta), cabos e elásticos contornam o corpo (polilinha empurrada
   para fora da pele), alavancas do supino máquina por fora do braço, peck-deck na altura da mão, coluna do Scott, paralelas
   largas, anilha não atravessa o chão no hip thrust, bancos com "z"/"larg".
6. Aparelhos: roda abdominal (gira), elíptico (coluna e console à frente, pedais e alças), escada (degraus sob os pés,
   corrimãos), trenó (postes + anilhas), remo (assento desliza sob os ísquios), leg press (placa centrada nos dois pés e
   orientada, trilhos por fora, pegadores), rolo da mesa flexora sobre o tendão, almofada da cadeira flexora, almofada da
   panturrilha sentado, rolo do tornozelo na hiperextensão, crossover com torres a ±13, triângulo, laço da barra assistida,
   halter único no francês, corda de pular girando (1 volta por salto, embaixo só no pico), corda naval com ondas, polia que
   acompanha a torre (abdominal na polia), alças nos elásticos, elástico sob o arco do pé.
7. Câmera: cam < 0 vira 3/4 da frente (rosto visível) salvo "cam_tras": true.
8. Passos de mão: mãos andam alternadas em passos de até ~26 cm, paradas no chão entre os passos (inchworm chega à prancha).

### Para os animadores (dados; campos novos no docstring de humano.py)
Geral: declarar "apoio" nos quadros com troca de apoio/voo; trocar cam negativas só se a vista de costas for necessária
("cam_tras": true); usar "maos"/"segura"/"dedos"/"puf" onde indicado; conferir com zoom.py e qa.py.
- lote1: agachamento-elastico (bf [-20,150], bt [-23,147], bfa 10, afa -20); agachamento-goblet (bf [10,155], bfa -4, afa -12;
  q2/q3 bf [-12,140]; pfa constante 15); agachamento-frontal (bf [85,200], bfa 25, afa 10); leg-press (encosto inclinado
  {"tipo":"banco","x":-3.2,"w":4.4,"h":2.3,"inc":45,"enc":7} ou t -135; cam 0); hack (w 5.9); cadeira-extensora/flexora e
  abdutora (maquina.x -2.4, banco x -2.4, t 176–178; abdutora pf [88,10,100]); mesa-flexora (banco x -4.9 w 11.2; bf [100,170]);
  afundo/afundo-halteres/passada (pt[2] 50–55; pta -6 pfa 6); step-up (q1 pt [5,-30,60]; cam 0); terra (t 130, c 150,
  pf [80,-22,90], x -2.6; cam 15); ponte-gluteo/ponte-unilateral ("apoio" com as duas mãos, bf [100,100]); elevacao-quadril
  (banco x -9.6, q0 x 0.2 y 2.3 t -112, q1/q2 y 4.0 t -92, "apoio":["costas","pe_f","pe_t"]); panturrilha-pe (pf[2] 52; degrau
  opcional); panturrilha-sentado (bloco só sob o antepé x 3.4 w 2.0; pf[2] 125/70); panturrilha-elastico (bf como agachamento
  elástico, pf[2] 52); superman (pf [-86,-86,-60], bf [88,88]); hiperextensao (bf [-15,100], afa -30); prancha-lateral
  (rol 88, t 160, bt [90,90], bta 0, "apoio":["cotovelo_t","pe_f","pe_t"]); abdominal (sem y ou apoio pelve; mãos no peito
  bf [-95,-5], afa -45); abdominal-bicicleta (bf [-160,20], bfa 60, afa -60 + "segura" nuca opcional); elevacao-pernas-barra
  (barra y 25.5, quadril y 15.1; cam 40); roda-abdominal (trocar "bola" por {"tipo":"roda","em":"maos"}, bfa 0);
  abdominal-polia (ate [6.5, 18.5]); pallof (cam 90); box-jump (caixa x 4.0); salto-distancia (encurtar volta); arremesso-
  rotacional (mesmos ângulos nos dois braços com tr; "voo"/"quica" na bola); ponte-pescoco (rol 0, trp 30, tr -25, inc 10,
  "apoio" pés + costas/cabeca); fuga-quadril (rol ±80 com pé de cima em "apoio", x -1.5 por fuga; cam 0); educativos-corrida
  (pé de apoio [-6,-10,70]); bike-subida (ângulos das pernas no círculo do pedal); dead-bug, mountain-climber, bound-lateral,
  russian-twist (ajustes leves do relatório).
- lote2: flexao-pliometrica ("fixo":"pes", "apoio" em todos os quadros); flexao-diamante (bfa -14/-6, afa -28/-34);
  supino-reto (q2 bf [52,182]); supino-inclinado(-barra) (enc 9; bf [24,166]; cam 50); supino-maquina e peck-deck
  (banco h 4.4, t 184); barra-fixa/supinada/assistida (q1 x -0.3, t 196, c 196; supinada cam 30); puxada-frente/triangulo
  (banco h 4.5; ate [2.2,21.5]; t 196; cam 30); remada-baixa (ate [9.5,4.6], q0 bf [78,90]); remada-curvada (q1 bf [-72,18]);
  remada-unilateral (banco x -4.8 w 13.4 h 4.1 z -1.8 larg 3.0, pfa 12, pt [0,-90,-170], "apoio" com "joelho_t");
  remada-elastico (ate [12,12.6]); pulldown-elastico (bf [178,160], bfa 150); pullover-polia (bfa 4); face-pull (q2/q3
  bf [80,180], bfa 85, afa -10; cam -60 + cam_tras ou 60); band-pull-apart (bfa 76); encolhimento (bfa 14);
  desenvolvimento-elastico (pfa/pta 10); elevacao-lateral (bfa 10); crucifixo (cam 90, cam_el 35); crossover (pfa/pta 6,
  q2/q3 bfa -24 afa -34); crucifixo-inverso/desenvolvimento-barra (cam positiva); arnold (q0 bfa 18); rotacao-externa
  (elastico "de":"mao_f", "maos":"f"); triceps-polia (ate [5.0,19.5]); triceps-elastico (pt [-20,-20,90], ate [-3.5,0.3],
  bf [186,…]); isometria-pescoco (quadro intermediário bf [100,200] bfa 40; "segura" {"mao_f":"cabeca"} + "rosto_ok");
  passe-medicine ("voo" opcional); paralelas (bfa 12).
- lote3: burpee/sprawl (quadro de voo com "apoio":["mao_f","mao_t"], ay 0.5; tempos mais lentos); corda (ok com o motor;
  conferir picos "ay"); swing (bfa/bta -8); thruster (2 kettlebells "maos":"f"/"t" ou mãos juntas; rack bf [20,150] bfa 25);
  power-clean (rack bf [95,215], bfa 18; quadro intermediário na volta bf [15,100]); arremesso-medicine ("voo":[1,2],
  "quica": true; bfa/bta -6 afa -10); battle-rope (ok); sled-push (pés no chão: pt [-40,-45,60], pf [55,-20,90], "apoio"
  alternando; tempos 0.42; o trenó é automático); turkish-getup (mão livre no chão bt [-40,-20] bta 40 + "apoio"; quadro de
  ponte e leg sweep; pt [-6,-90,-92]); inchworm (t 35, c 30, pf [12,-10,90]; o motor já dá passos de mão); sombra/saco (punho
  automático; saco x 6.6); bear-crawl (pf [80,-40,-100], pt [70,-50,-100], t 95; balanço [60,-30,-90]); eliptico/escada
  (aparelhos automáticos; conferir pés e mãos); remo-ergometro (y constante ~1.5); caminhada-corrida (bloco de caminhada);
  maior-alongamento (pt [-35,-75,-60]); gato-camelo (cfl -30, pel 20, c 160); flexor-quadril (x 2.4, pel -8);
  alongamento-quadriceps ("segura" {"mao_f":"pe_f"}); rolo-quadriceps/panturrilha/it (amplitude x; rolo-it pf [60,-20,-90]
  pfa 10, pt [-85,-85,-10], "apoio":["mao_t","pe_f","lado"]); alongamento-peito (bta 90); rotacao-toracica (deitado de lado:
  bt [90,90] bta 0, pf [90,0,90], pt [92,2,90], "apoio":["lado"], "trt" no lugar de tr); alongamento-adutores ("segura" pés,
  cfa -50 pfa 60); balanco-pernas ({"tipo":"parede","mao":"t"}); circulos-quadril (z ±0.6, x ±0.5; "segura" cintura);
  circulos-punho (antebraço parado bf [22,100] + puf/pdf ±60/±25); circulos-ombro (pro ±0.7, cam 20); circulos-joelho
  ("segura" {"mao_f":"joelho_f","mao_t":"joelho_t"}); carioca (z crescente); alongamento-gluteo ("segura" coxa_t nas duas
  mãos; Q1 pf [130,40,150] pfa 45 cfa -60); abraco-joelhos (pf [228,140,170]; "segura" canela_f/canela_t); alongamento-triceps
  ("segura" {"mao_t":"cotovelo_f"}); alongamento-antebraco ("dedos":"tras"); torcao-coluna (pfa -30, cfa 10; "segura"
  {"mao_t":"joelho_f"}, mão de trás "apoio"); alongamento-dorsal (bfa/bta -12); moinho (t 100 no 2º lado);
  circulos-tornozelo (pe 50 no Q0).
