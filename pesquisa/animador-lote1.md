# Animador lote1 — andamento

Fonte dos defeitos: `pesquisa/auditoria-lote1.md`. QA: `tools/anim3d/qa.py` só no id. "ok" = qa sem erro e conferido visualmente (perfil/frente + zoom de mãos/pés).

| id | status | qa | observação |
|---|---|---|---|
| agachamento-livre | ok | 0 erros, 0 avisos | sem mudança (aprovado e conferido) |
| agachamento-elastico | ok | 0 erros, 0 avisos | mãos à frente dos ombros (bf [15,160], bfa 10, afa -20), alças fechadas na mão, elástico sob o arco do pé |
| cadeira-flexora | ok | 0 erros, 2 avisos | encosto (máquina x -2.4, t 176), coxa levemente para baixo; avisos: coxa 2,0–2,4 cm no estofado (almofada macia, abaixo do limite de erro) |
| agachamento-goblet | ok | 0 erros, 3 avisos | palmas nos chifres, kettlebell no esterno, cotovelos por dentro dos joelhos, pfa 15 constante; avisos: pronação 105–109° (pegada nos chifres) e antebraço 1,3 cm encostado no sino |
| agachamento-frontal | em andamento | 4 erros | desvio radial do punho no rack, braço x tronco |
| leg-press | ok | 0 erros, 4 avisos | encosto inclinado ao longo das costas (banco x -1.0, inc 29, enc 9), costas e cabeça no encosto, mãos nos pegadores, cam 0 (perfil: pés na placa visíveis); avisos: tórax 2,1 cm no estofado no fundo, cabeça 4,7 cm do encosto, pé 1,4 cm na estrutura |
| hack | em andamento | 3 erros | pés/mão x estrutura do aparelho |
| cadeira-extensora | ok | 0 erros, 3 avisos | costas no encosto (máquina x -2.4, t 176), pegadores; avisos: coxa 1,9 cm no estofado e parte distal da coxa 6 cm acima do assento (joelho na borda) |
| mesa-flexora | em andamento | 2 erros | mãos x estofado da cabeceira |
| abdutora | em andamento | 2 erros | perna x almofada |
| agachamento-salto | ok | 0 erros, 0 avisos | sem mudança (conferido) |
| agachamento-barra | ok | 0 erros, 4 avisos | cam 40 (mão e barra visíveis); avisos: rotação externa do ombro 110° e cotovelo torcido na pegada da barra nas costas (posição real do agachamento com barra baixa) |
| afundo | ok | 0 erros, 1 aviso | pé de trás na bola do pé (pt[2] 52), pés na largura do quadril (pfa 6 / pta -6); aviso: joelho de trás a 9 cm do chão no fundo (correto) |
| passada-andando | ok | 0 erros, 0 avisos | pé de trás na bola do pé (52) |
| bulgaro | ok | 0 erros, 1 aviso | banco 0,3 mais para trás; aviso: peito do pé 2,4 cm no estofado do banco (apoio real do pé no banco) |
| terra | ok | 0 erros, 2 avisos | posição inicial de terra (quadril entre joelho e ombro, t 130), cam 15 / el 8; avisos: barra 1,3–1,5 cm fora do túnel dos dedos em poucos quadros |
| stiff | ok | 0 erros, 1 aviso | cam 15 |
| stiff-halteres | ok | 0 erros, 0 avisos | cam 15 |
| abdutora | ok | 0 erros, 2 avisos | encosto (máquina x -2.4, t 178), pés fora do chão (pf [88,10,100]), abertura 34°; avisos: perna 1,8–1,9 cm na almofada (estofado) |
| ponte-gluteo | ok | 0 erros, 3 avisos | apoios declarados (pelve/costas/cabeça + pés + mãos + antebraços), palmas no chão, quadril alinhado (t -58), pescoço neutro; avisos: antebraço 3,3 cm (espessura) e quadros congelados da isometria no topo |
| ponte-unilateral | ok | 0 erros, 2 avisos | idem ponte-gluteo; aviso: antebraço 3,3 cm |
| coice-gluteo | ok | 0 erros, 0 avisos | joelhos declarados como apoio (antes a 7 cm do tapete) |
| terra-uma-perna | ok | 0 erros, 1 aviso | pé de apoio sob a linha do corpo (pfa -7) e quadril sobre o pé na descida (x -1.2): centro de massa dentro da base (antes 11 cm fora); aviso: braço 3,5 cm no tronco num quadro |
| monster-walk | pendente motor | 1 erro (4–6 quadros) | refeito com transferência de peso antes de cada passo (12+ chaves: desloca o quadril sobre o pé de apoio, depois passo de 18 cm): centro de massa fora da base caiu de 21 quadros/26 cm para 4–6 quadros/10 cm; o resto é o pé que pousa depois da chave (ver motor-pendencias) |
| panturrilha-sentado | ok | 0 erros, 0 avisos | banco h 4.3 com o glúteo assentado, bloco só sob o antepé (x 4.5), calcanhar desce abaixo da borda (pé 125) e sobe a 70; almofada da coxa e pegadores do motor |
| dead-bug | ok | 0 erros, 0 avisos | apoio pelve/costas/cabeça declarado (cabeça no tapete; antes 5 cm no ar), perna e braço estendidos param acima do tapete |
| panturrilha-pe | ok | 0 erros, 0 avisos | topo na bola do pé (pé 52, sem ponta de bailarina), pernas inclinadas 4° à frente para o centro de massa ficar sobre o antepé (antes 7 cm fora da base) |
| panturrilha-elastico | ok | 0 erros, 1 aviso | mãos à frente dos ombros segurando as alças, elástico sob o arco, pé 52 no topo, centro de massa sobre o antepé; aviso: pausa no topo (congelado, isometria) |
| superman | ok | 0 erros, 4 avisos | descanso com pernas e braços no tapete, subida mais alta (t 112); avisos: extensão lombar 42° (é o exercício) e peito/joelhos "pousados" acima do chão na contração (correto) |
| hiperextensao | ok | 0 erros, ~6 avisos | almofada estreita sob a dobra do quadril (x -1.1, w 0.5, h 5.0), rolo de Aquiles automático do motor, pés na placa, apoio só dos pés declarado (antes o motor deitava o peito na almofada); avisos: coxa 2,2–2,5 cm no estofado, braço 3,8 cm no tronco (braços cruzados) |
| prancha-lateral | ok | 0 erros, 3 avisos | refeita: rol 70, antebraço de baixo no chão com o cotovelo sob o ombro (bt [0,90] bta 88, punho fechado), pés empilhados (pfa/pta -6), apoio cotovelo_t + pe_t; avisos: pernas empilhadas se tocando 4 cm, coxa de baixo acima do chão (correto) |
| abdominal-infra | ok | 0 erros, 1 aviso | braços mais rentes ao chão; aviso: antebraço 4 cm acima do tapete |
| mountain-climber | ok | 0 erros, 4 avisos | perna que volta quase estendida e rente ao chão, quadril baixo (y 4.8, t 98), joelho que avança menos (pf [88,-50]); avisos: extensão do punho 89–90° (apoio nas mãos) e flexão do quadril 160° em 4 quadros |
| mesa-flexora | ok | 0 erros, 7 avisos | banco maior e mais estreito (x -4.2, w 11.5, larg 2.3) para as mãos alcançarem os pegadores sob a cabeceira sem entrar no estofado, tronco t 94 (pelve no banco); avisos: cotovelo torcido, mão 1,5 cm no estofado, joelho fora do banco (correto: joelho na borda) |
| abdominal | ok | 0 erros, 2 avisos | sem `y` (pelve e lombar no tapete, motor apoia), apoios declarados (pelve/costas/cabeça + pés no repouso, pelve + pés na subida), braços estendidos em direção aos joelhos (variante "mãos deslizando nas coxas": cruzadas no peito atravessavam o tórax e atrás da cabeça cobria o rosto); aviso: antebraços no ar na subida (correto) |
| roda-abdominal | ok | 0 erros, 2 avisos | roda abdominal de verdade ({"tipo":"roda"}), mãos fechadas nas manoplas (bfa 0); aviso: joelhos "pousados" 7 cm em 12 quadros (rolamento) |
| abdominal-polia | ok | 0 erros, 0 avisos | polia alta à frente (ate [6.5,18.5]), cabo da torre até a corda atrás da cabeça |
| ponte-pescoco | ok | 0 erros, 2 avisos | sem `rol` (pés plantados), ponte com trp 30 / tr -25 / inc 10 sobre o ombro, apoios pés + costas/cabeça; repouso com braços no chão; avisos: rotação da coluna 53° (é o rolamento), braço 3,7 cm no tronco num quadro |
| elevacao-pernas-barra | ok | 0 erros, 0 avisos | barra a 25.5 (pés longe do chão), mãos presas na barra, cam 40 (rosto visível) |
| educativos-corrida | ok | 0 erros, 0 avisos | pé de apoio no antepé (70) em vez de ponta |
| bound-lateral | ok | 0 erros, 0 avisos | pé de aterrissagem sob o corpo (pfa/pta -6: centro de massa na base), pernas no voo com a de impulso saindo para o lado |
| salto-tesoura | ok | 0 erros, 0 avisos | sem mudança (conferido) |
| tuck-jump | ok | 0 erros, 0 avisos | sem mudança (conferido) |
| canivete | ok | 0 erros, 1 aviso | sem mudança; aviso: coluna dobrada 27° num segmento em 12 quadros |
| bike-subida | ok | 0 erros, 4 avisos | sem mudança nos dados: o motor agora leva os pés aos pedais e as mãos ao guidão; avisos: pé 1,0–1,2 cm no pedal |
| sentar-levantar | ok | 0 erros, 0 avisos | sem mudança (conferido; centro de massa ok no qa atual) |
| russian-twist | ok | 0 erros, 4 avisos | sem mudança (bola nas mãos atravessava as coxas); avisos: braços 6 cm no tronco em 9 quadros nos extremos da rotação |
