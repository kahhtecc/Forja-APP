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
