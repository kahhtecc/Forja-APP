# Auditoria das animações 3D — lote2 (56 exercícios)

Auditor: biomecânica + animação técnica. Base: os 56 MP4 de produção (`app/src/main/assets/video3d/<id>.mp4`, 16 quadros cada),
renders extras de perfil (`cam 0`, os 56) e de frente (`cam 90`, nos exercícios com apoio/pegada duvidosos) e medições no motor
(sondas em `scratchpad/auditoria/lote2/tools/`: ângulos, posição das pegadas, distância pele↔barra/cabo/elástico, glúteo↔assento).

Provas: `/tmp/claude-0/-home-user-teste-3/400edce2-80ea-57f6-97f9-c6ff24db5c18/scratchpad/auditoria/lote2/`
- `folhas/<id>.jpg`: 16 quadros do MP4 de produção (número = quadro/total, 24 fps)
- `z_*.jpg`: recortes ampliados dos defeitos; `render/c0/<id>.jpg` (perfil) e `render/c90/<id>.jpg` (frente): 8 instantes do ciclo
- `folhas/c0_*.jpg`, `folhas/c90_a.jpg`: montagens de perfil/frente
Unidades do motor: 1 un. = 1 dm. "q" = quadro do MP4 de produção.

## Resumo

Contagem pelo PIOR defeito de cada exercício (S1 = pegada que não segura, crítico pelo pedido do usuário "mão que não segura"):

- **APROVADOS: 5** — flexao, flexao-joelhos, flexao-declinada, pike-pushup, triceps-banco (o qa.py novo acusa "pousada"
  de antebraço/joelho a 4–15 cm do chão no fundo da flexão; conferido no vídeo: é a posição normal, falso positivo).
- **Só defeitos leves: 2** — flexao-inclinada (dedos fora do banco; o qa.py acusa cotovelo torcido 88° no fundo — conferir), paralelas.
- **Com defeito crítico: 49** — todos os demais. Para **28** deles o ÚNICO crítico é a S1 (corrigida no motor):
  supino-halteres, supino-inclinado, crucifixo, crucifixo-elastico, elevacao-lateral, elevacao-lateral-elastico, elevacao-frontal,
  desenvolvimento-halteres, desenvolvimento-barra, crucifixo-inverso, arnold, rosca-halteres, rosca-martelo, rosca-elastico,
  triceps-testa, triceps-coice, remada-invertida, remada-curvada, rosca-direta, rosca-scott, triceps-polia, pulldown-elastico,
  remada-elastico, remada-baixa, desenvolvimento-elastico, rotacao-externa, triceps-frances, triceps-elastico
  (do remada-curvada em diante têm também defeitos médios/leves próprios, listados abaixo).
  **Críticos próprios (dados/motor, além da S1): 21** — flexao-pliometrica (joelho dobra 67°), flexao-diamante (mãos afastadas),
  supino-maquina (alavanca atravessa o braço + quadril 11 cm acima do assento), peck-deck (quadril 11 cm acima do assento),
  barra-fixa / barra-supinada / barra-assistida (cabeça atravessa a barra; mãos soltam a barra), puxada-frente (flutua + barra/cabo
  pela cabeça), puxada-triangulo (flutua), remada-unilateral (perna e halter atravessam o banco, pé no ar), pullover-polia (duas
  torres, sem puxador), face-pull (corda pela cabeça), band-pull-apart (elástico pelo peito), encolhimento, desenvolvimento-maquina,
  isometria-pescoco (mão atravessa pescoço/cabeça), passe-medicine (mão fora da bola), supino-reto, supino-elastico, crossover,
  supino-inclinado-barra.
- **Defeitos médios relevantes**: amplitude curta no supino (barra 9–11 cm acima do peito), cabeça pairando 5–14 cm acima do banco
  nos supinos (qa.py), remada-baixa (cabo inclinado), desenvolvimento-elastico / triceps-elastico (elástico atravessa o corpo),
  rotacao-externa (elástico na mão parada), triceps-frances (dois halteres colidindo), crossover (torres perto, mãos não se
  encontram), peck-deck (alavanca no braço).

## Falhas sistêmicas do motor (para o especialista)

**S1 — Pegada não fecha em volta do implemento (crítico, afeta ~40 dos 56).** Dedos curvam ~150–160° (`CURVA["peg"]`), mas o
centro da pegada (`Humano._preparar_maos`: `peg = punho + (f3 − punho)*0.62 + palma*0.22`) fica no MEIO da palma, perto do punho.
O cabo da barra/halter/pegador encosta na base da palma e os dedos se fecham no ar além dele: de um lado parece "garra", do outro
parece mão aberta sobre o halter (provas: `z_supino-halteres.jpg`, `z_supino-reto.jpg`, `z_peck.jpg`, `z_encol.jpg`, folhas de
desenvolvimento-maquina q10–q40). Correção: centro da pegada na prega dos dedos — `peg = punho + (f3 − punho)*0.95 + palma*0.38`
(≈ raio do cabo + espessura dos dedos) — e polegar fechando por cima (`CURVA["peg"]` do polegar `(45, 40, 30)`); conferir com
render de perto (cam a 30 cm da mão) em barra, halter e pegador vertical. Elásticos sem alça (remada/pulldown/rotação/rosca/
desenvolvimento) devem ganhar alça como em `_elastico_duplo`.

**S2 — Barra fixa: corpo sob a barra e IK das mãos desligado no topo (crítico).** A cabeça sobe exatamente sob a barra e a atravessa
(barra-fixa, supinada, assistida; distância pele-barra 0,01–0,05). E `segurar_barra` só roda quando a mão 2D da chave está a
< 1,6 da barra; com `bfa` alto (120°) a mão 2D sai do raio e a pegada sobe 7 cm acima da barra. Correção: chamar `segurar_barra`
em todo quadro com `barra_fixa` (não paralelas) e, nos dados, jogar o corpo para trás no topo (`x` −1,5, `t 196`, `c 196`).

**S3 — Bancos e assentos sempre centrados e com largura fixa (±3,2) (crítico).** Remada unilateral precisa de banco deslocado
para um lado (perna em pé atravessa o banco; halter atravessa o banco). Aceitar `"z"` e `"larg"` no prop banco em
`Contexto.superficies` e `aparelhos._blocos`.

**S4 — Altura do assento não verificada contra o quadril (crítico).** Puxada frente/triângulo: glúteo ~8 cm acima do assento.
O motor não "senta" o corpo no banco quando os pés estão no chão. Sugestão: em `apoiar_superficies`, se a pose 2D põe o quadril
sobre um banco (`_sobre_superficie_2d`), baixar até o glúteo tocar o topo (ou avisar no qa.py: novo teste "assento").

**S5 — Implementos atravessando o corpo sem teste no qa.py (crítico).** Alavancas do supino máquina, cabo da puxada, corda do
face pull, elástico do band-pull-apart/barra assistida/desenvolvimento/tríceps elástico, coluna do banco Scott. Sugestão: novo
teste em `qa.py` — distância entre a pele (proxy, sem mão/antebraço do próprio lado) e os segmentos do kit (barra entre as
pegadas, cabo polia→pegada, elástico mão→âncora, alavancas) < 0,15 un. = erro.

**S6 — Configuração automática de aparelho errada.** `_polia`: `dupla` (duas torres) dispara por distância entre mãos > 6,5
(pullover-polia); torres do crossover a ±8 (curtas); puxador sempre reto (triângulo). `_elastico`: com `ate` lista sempre liga as
duas mãos (rotação externa); "de maos ate pes" usado para barra assistida (deveria ser laço na barra). `halter` sempre um por mão
(tríceps francês precisa de um halter com as duas mãos). `bola`: mãos em punho e uma delas fora da bola.

**S7 — Quadros sem `"apoio"` em exercícios com voo/troca de apoio.** flexao-pliometrica: `ancorar_apoios` amarra os pés de chaves
com geometrias diferentes e o IK dobra o joelho 67°. Declarar `apoio` em todos os quadros desses exercícios.

**S8 — Câmera.** Câmeras por trás (`cam −25…−35`: barra-supinada, puxadas, face-pull, crucifixo-inverso, desenvolvimento-barra)
escondem o rosto; elevação alta com câmera em 3/4 faz braços simétricos parecerem assimétricos (crucifixo, face-pull).

## Exercícios

### flexao — APROVADO (só falha sistêmica S1 não se aplica: mãos espalmadas)
Mãos e pés plantados, corpo em linha, cotovelos ~45°, amplitude ok. Prova: `folhas/flexao.jpg`.

### flexao-pliometrica — DEFEITOS
1. **Crítico — joelhos dobram 67° na posição alta** (q0–q5 e q30–q38; o dado tem pernas retas `pf [-72.3,-72.3]`). Causa: quadros sem `"apoio"`; o quadro 2 (voo, `t 115.7`) é calculado com as mãos fixas (`fixo: maos`), então os pés ficam ~8 cm mais perto das mãos; `ancorar_apoios` liga os pés das chaves 2→3→0 numa âncora só e o IK encolhe a perna (sonda: joelho 67° em t=0).
2. **Médio — pés soltos e escorregando no fundo** (q8–q20): a chave 1 não detecta contato dos pés (`contato pe_f False`), peso 0, os pés andam 4 cm.
Correção: usar `"fixo": "pes"` (os quadros 0/1/3 já são geometricamente iguais aos da flexão), declarar `"apoio": ["mao_f","mao_t","pe_f","pe_t"]` nos quadros 0, 1, 3 e `"apoio": ["pe_f","pe_t"]` no quadro 2, e no quadro 2 subir as mãos com o corpo girando em torno dos pés (t 115.7 já faz isso com `fixo: pes`). Prova: `folhas/flexao-pliometrica.jpg`.

### supino-halteres — DEFEITOS
1. **Crítico — mão aberta/garra sem segurar o halter** (q0–q16, q49–q61, mão do lado longe): o cabo do halter fica no meio da palma e os dedos se curvam no ar, além do cabo. Falha sistêmica S1. Prova: `z_supino-halteres.jpg`.

### supino-reto — DEFEITOS
0. **Médio — cabeça pairando 5 cm acima do banco** o ciclo todo (qa.py `pousada cabeça`). Correção: `c −95` (cabeça encosta) ou `repousar` também na cabeça.
1. **Crítico — pegada não envolve a barra** (todo o ciclo): a barra passa pela base da palma, dedos curvados acima dela (S1). Prova: `z_supino-reto.jpg`.
2. **Médio — amplitude curta**: no fundo a barra para ~11 cm acima do peito (distância eixo-pele 1,09 un.). Correção: quadro 2 `bf [52, 182]` (≈ −6° no braço) até a barra tocar o esterno (distância ≤ 0,3).

### supino-maquina — DEFEITOS
0. **Crítico — sentado no ar**: qa.py mede pelve 11,4 cm acima do assento e costas 10 cm longe do encosto (S4). Correção: `banco h 4.4` e `t 184` com encosto encostado.
1. **Crítico — alavancas atravessam o corpo**: a alavanca do lado da câmera passa pelo peitoral/deltoide e a do outro lado por trás do pescoço (q0–q71). Causa: `aparelhos.preparar_alavancas` (tipo "supino") põe o pivô em `x = |ombro|+1.3, y = ombro+2.0, z = ombro+2.6` (atrás e acima do ombro) e `_bracos_maquina` liga a pegada ao pivô em linha reta, cortando ombro/braço abduzido 50°. Correção no motor: pivô lateral por fora do braço (`x = |ombro| + 3.2`), `y = ombro + 0.8`, `z = ombro − 1.0` (alavanca vem de baixo/lado, como no chest press real) e a ligação pegada→alavanca horizontal para fora; ou checar distância pele-alavanca > 0,4 e empurrar o pivô para fora. Prova: `z_supino-maquina.jpg`.
2. Crítico (S1) — mãos não fecham no pegador.

### crossover — DEFEITOS
1. **Médio — torres perto demais**: as torres ficam em x = ±8 (1,6 m entre elas) e a polia em ±7,1; com os braços abertos (`bfa 72`) a mão chega na coluna da torre (q41, q0). Causa: `aparelhos._polia` (`xc = s * 8.0`). Correção: `xc = s * 13`, polia em `xc − s*0.9`.
2. **Médio — base em linha (pernas parecem cruzadas)**: `pf [22,10]`, `pt [-16,-16]` sem abdução, pé da frente na mesma linha do de trás e joelhos se sobrepõem na vista de frente. Correção: `pfa 6`, `pta 6`. Prova: `z_crossover.jpg`.
3. **Médio — as mãos não se encontram na frente** no fechamento (vista de frente, `folhas/c90_a.jpg` linha 3): param ao lado das coxas, ±25 cm. Correção: quadros 2–3 `bfa −24`, `afa −34` (mãos se cruzam diante do quadril).
4. Crítico (S1) — pegada.

### peck-deck — DEFEITOS
0. **Crítico — sentado no ar**: pelve 11,6 cm acima do assento, costas 10 cm fora do encosto (qa.py). Mesma correção do supino-maquina (`banco h 4.4`).
1. **Crítico — mãos abertas ao lado do pegador** (q15: dedos esticados, pegador vertical encostado na palma): S1. Prova: `z_peck.jpg`.
2. **Médio — alavanca passa por dentro do braço no fechamento** (q0, q61–q76): o braço da máquina desce do pivô em cima e cruza o bíceps. Correção: `zarm` = pegada + 0,3 (alavanca horizontal na altura da mão) em `_bracos_maquina` tipo "peck", ou trocar por almofadas de antebraço.

### supino-elastico — DEFEITOS
1. **Médio — elástico atravessa o braço** (q30–q47): a curva "costas" passa por `lowerarm01 + tras*0.55` (dentro do braço). Correção em `aparelhos._elastico` (de "costas"): pontos de controle mão → axila (`upperarm01 + tras*1.1 − cima*0.5`) → escápulas → outra axila → outra mão, sem passar pelo cotovelo.
2. Crítico (S1) — mão em garra sem fechar no elástico. Prova: `z_supel.jpg`.

### crucifixo — DEFEITOS (leve)
1. **Leve — câmera**: com `cam 38` e elevação 24° o braço do lado da câmera parece descer abaixo do banco e o outro parece ficar vertical; numericamente é simétrico (mãos a ±7,8). Correção: `cam 90`, `cam_el 35`.
2. Crítico (S1) — pegada.

### crucifixo-elastico — APROVADO com S1
Elástico passa por fora do ombro (x ≈ 3,7 no plano do ombro), sem atravessar. Só a pegada (S1).

### flexao-diamante — DEFEITOS
1. **Crítico — não é flexão diamante**: de frente as mãos ficam na largura dos ombros (afastadas ~45 cm), sem formar o diamante sob o esterno, e no fundo os cotovelos abrem para fora. Causa: `bfa −3.1/2.7`, `afa −9.4/−15.9` (quase neutros). Correção: quadro 0 `bfa −14`, `afa −28`; quadros 1–2 `bfa −6`, `afa −34` (mãos se tocando sob o peito, cotovelos para trás junto ao tronco). Prova: `render/c90/flexao-diamante.jpg`.

### paralelas — DEFEITOS (leve)
Leve — barras estreitas: de frente, quadril e coxas raspam nas barras na descida (barras ≈ ±2,3, quadril ≈ ±2,0). Correção: barras ±2,8 (no motor, largura das paralelas em `_barra`/barra_fixa com "paralela"; nos dados `bfa 12`). Pegada neutra ok, inclinação do tronco ok. Prova: `folhas/c90_a.jpg` (linha 1), `render/c0/paralelas.jpg`.

### barra-fixa — DEFEITOS
1. **Crítico — a cabeça atravessa a barra** na subida/topo (t 17–67 % do ciclo: distância pele-eixo 0,01–0,05 un.; centro da cabeça no mesmo y da barra). Correção: no quadro 1 jogar o quadril para trás e inclinar: `x` = −0,3 (era 1.3), `t 196`, `c 196` (queixo passa por cima da barra, barra termina na frente do pescoço/alto do peito).
2. **Crítico — mãos soltam a barra no topo**: pegada sobe 7 cm acima da barra (z 21,5 × 20,8) e recua 7 cm. Causa: `segurar_barra` só roda quando as duas chaves têm `mao_f` a < 1,6 da barra em 2D; com `bfa 120.8` a mão 2D da chave 1 fica longe → sem IK. Correção no motor: com `barra_fixa` (não paralelas) chamar `segurar_barra` em todo quadro; nos dados, manter a mão 2D da chave 1 a < 1,6 do ponto da barra.

### barra-supinada — DEFEITOS
1. **Crítico — cabeça atravessa a barra** (t 17–58 %, distância 0,01–0,04). Mesma correção (`x` ≈ −0,4, `t 196`, `c 196` no quadro 1).
2. Leve — câmera por trás (`cam −30`) esconde o rosto: usar `cam 30`.

### barra-assistida — DEFEITOS
1. **Crítico — cabeça atravessa a barra** (t 17–67 %) e **mãos 7 cm acima da barra no topo** (mesmas causas da barra-fixa).
2. **Crítico — elástico errado e atravessando o corpo**: `"elastico" de maos ate pes` desenha duas tiras retas mão→pé que cortam braço, cabeça e coxa (distância 0,01–0,05). O certo é um laço preso no centro da barra, descendo até o pé/joelho apoiado. Correção no motor: novo modo `{"tipo":"elastico","de":"barra","ate":"pe_t"}` (duas tiras ±0,3 do centro da barra até o pé de trás, em U sob o pé).

### flexao-inclinada — DEFEITOS (leve)
1. **Leve — mão do lado longe com os dedos para fora da borda do banco** (q0–q60): o banco (`w 3.6`, largura lateral fixa 6,4 un.) é estreito para a pegada (`bfa 9`). Correção: banco com 7–8 un. de largura (motor: `Contexto.superficies` usa ±3,2 fixo; aceitar `"larg"` no prop) ou `bfa 5`. Prova: `z_flexinc.jpg`.

### flexao-joelhos — APROVADO
Joelhos no tapete, canelas elevadas, mãos plantadas (pés ~1 cm de deriva, imperceptível). Prova: `render/c0/flexao-joelhos.jpg`.

### flexao-declinada — APROVADO
Antepés no topo do banco, corpo alinhado, amplitude boa. Prova: `z_flexinc.jpg` (3º recorte), `render/c0/flexao-declinada.jpg`.

### supino-inclinado — DEFEITOS
0. **Médio — cabeça 13,6 cm acima do encosto** (encosto curto, `enc` padrão 7): `enc 9`. qa.py também acusa tórax/braço dentro do estofado (29 cm, 4 quadros, q2–q5) — provável quina do encosto; conferir em `aparelhos._blocos` (inclinado).
1. Crítico (S1) — mão do lado longe em garra, cabo do halter fora dos dedos (q0–q20, q49–q61).
2. Leve — mão de perto e halter cobrem o queixo no fundo (q28–q41) com `cam` padrão; `cam 50`, `cam_el 30`.

### supino-inclinado-barra — DEFEITOS
0. **Médio — cabeça 11 cm acima do encosto** (`enc 9`); qa.py: tórax dentro do estofado 25 cm em 3 quadros (mesma quina).
1. Crítico (S1) — pegada na barra.
2. **Médio — amplitude curta**: barra para ~9 cm do peito (distância 0,94). Quadro 2: `bf [24, 166]`.
3. Leve — anilha de perto cobre o rosto no fundo (q30–q43); `cam 50`.

### puxada-frente — DEFEITOS
1. **Crítico — glúteo flutuando acima do assento** (todo o ciclo): pele mais baixa do quadril em z 4,48, topo do banco em 3,66 → ~8 cm de vão. Causa: `banco h 3.7` mais baixo que a altura do quadril dada pelas pernas (`pf [86,4]`). Correção: `banco h 4.5` (ou `y` do quadril fixo e pés apoiados). Prova: `z_puxada.jpg`.
2. **Crítico — barra e cabo atravessam a cabeça** na descida/subida (t 12–19 % e 56–69 %: distância pele-barra 0,01–0,03 em z 11,5–13,4; cabo polia→barra 0,00–0,02 em z 12,3–13,3 no fundo). A polia está em `ate [0.4, 21.5]`, praticamente sobre a cabeça com o tronco inclinado para trás. Correção: `ate [2.2, 21.5]` (polia à frente) e no quadro 1 `t 196` com a barra descendo à frente do rosto (`bf [140, 150]`, `bfa 120`) até o alto do peito.
3. Crítico (S1) — pegada. Leve — câmera por trás (`cam −30`) esconde o rosto: `cam 30`.

### puxada-triangulo — DEFEITOS
1. **Crítico — glúteo flutuando ~8 cm acima do assento** (mesma causa, `banco h 3.7` → 4.5).
2. **Médio — puxador errado**: desenha barra reta (`_polia`, tipo "barra" com mínimo de 4,4 un.) em vez de triângulo/V com pegada neutra e mãos juntas. Correção no motor: id com "triangulo" → peça em V (duas alças paralelas a 15 cm) e eixo das mãos neutro.
3. Crítico (S1) — pegada.

### remada-baixa — DEFEITOS
1. **Médio — cabo sobe da polia baixa até as mãos na altura do ombro** na posição alongada (q0, q58–q72: `bf [67.9, 88.2]`), ângulo de ~40°; na remada sentada o cabo fica quase horizontal. Correção: polia `ate [9.5, 4.6]` e quadro 0 `bf [78, 90]` (mãos na altura do abdome/peito baixo).
2. Leve — puxador reto curto; o padrão é triângulo. Crítico (S1) — pegada.

### remada-curvada — DEFEITOS (leve)
1. **Leve — barra não chega ao tronco no topo** (distância 0,92 ≈ 9 cm do abdome). Quadro 1: `bf [-72, 18]`.
2. Crítico (S1) — pegada.

### remada-unilateral — DEFEITOS
1. **Crítico — perna de apoio atravessa o banco**: a perna em pé (`pf`) desce do quadril, passa pelo estofado e o pé fica embaixo do banco (todo o ciclo). Causa: o banco é sempre centrado no corpo (motor: `Contexto.superficies` ±3,2 em x; `_blocos` sem deslocamento lateral). Correção no motor: aceitar `"z"` (deslocamento lateral) e `"larg"` no prop banco; nos dados: `{"tipo":"banco","x":-4.8,"w":13.4,"h":4.1,"z":-1.8,"larg":3.0}` (banco só sob o joelho e a mão do lado "t") e `pfa 12` na perna em pé.
2. **Crítico — joelho no banco com a canela subindo no ar**: a canela de trás sobe ~30° e o pé fica flutuando ~30 cm acima do estofado (q0–q72). Correção: `pt [0, -90, -170]` (canela horizontal apoiada) e `"apoio"` incluindo o joelho de trás (motor: suportar `"joelho_t"` em `apoio`).
3. **Crítico — halter atravessa o banco** na posição baixa (q0, q58–q72: halter abaixo do topo do estofado). Corrigido junto com o item 1 (braço de trabalho por fora do banco). Prova: `folhas/remada-unilateral.jpg`, `render/c0/remada-unilateral.jpg`.

### remada-elastico — DEFEITOS (leve)
1. **Leve — elástico frouxo**: na posição alongada as mãos ficam a ~10 cm do poste (`ate [8.5, 12.6]`). Correção: `ate [12, 12.6]`.
2. Crítico (S1) — mãos em garra sem alça (desenhar alças como em `_elastico_duplo`).

### remada-invertida — APROVADO (S1 na pegada)
Corpo em prancha, calcanhares no chão, peito sobe até perto da barra. Prova: `render/c0/remada-invertida.jpg`.

### pulldown-elastico — DEFEITOS (leve)
1. Leve — amplitude: as mãos param na altura das orelhas; descer até a altura do ombro (`bf [178,160]`, `bfa 150`).
2. S1 — mãos em garra sem alça.

### pullover-polia — DEFEITOS
1. **Crítico — aparelho errado e mãos sem puxador**: aparecem DUAS torres (uma bem na frente do corpo) e um cabo por mão, sem barra. Causa: `aparelhos._polia` liga `dupla` quando a distância entre as mãos passa de 6,5 (aqui 6,6 com `bfa 8`) e então esconde o puxador. Correção no motor: `dupla` só para "crossover" (ou prop `"dupla": true`); nos dados `bfa 4`.
2. S1 — pegada.

### face-pull — DEFEITOS
1. **Crítico — corda/cabo atravessa a cabeça no fim** (t 38–50 %: distância 0,04–0,05 em z 17): o nó da corda fica no meio das mãos, que estão ao lado das orelhas (x ±5,7, y ≈ 0). Correção: quadro 2/3 `bf [80, 180]`, `bfa 85`, `afa −10` (mãos ±3,5 e ~15 cm à frente do rosto).
2. Médio — mãos ±57 cm no fim: uma corda de tríceps não abre tanto; resolvido pelo item 1.
3. Leve — câmera por trás (`cam −35`) faz um braço parecer erguido e o outro à frente; `cam −60`, `cam_el 10`.

### band-pull-apart — DEFEITOS
1. **Crítico — elástico atravessa o peito** na abertura (q14–q52): `bfa 94` leva as mãos para trás do plano dos ombros e o elástico reto entre as mãos corta o tórax. Correção: quadros 1 e 2 `bfa 76` (o elástico encosta no esterno sem entrar).

### encolhimento — DEFEITOS
1. **Crítico (S1) — mão aberta ao lado do halter** (dedos estendidos, cabo fora da mão; ver `z_encol.jpg`).
2. **Médio — cabeça do halter entra na coxa** quando os ombros sobem (q21–q57). Correção: `bfa 14`.

### desenvolvimento-halteres — DEFEITOS (S1)
Movimento correto; só a pegada (dedos abertos sobre o cabo, q10–q40).

### desenvolvimento-barra — DEFEITOS (leve)
1. Leve — câmera por trás (`cam −25`) e anilha cobrindo o rosto no início; `cam 35`.
2. S1 — pegada.

### desenvolvimento-maquina — DEFEITOS
1. **Crítico (S1) — mãos espalmadas com dedos abertos acima do pegador** (q10–q40, bem visível de frente).

### desenvolvimento-elastico — DEFEITOS
1. **Médio — elástico atravessa o deltoide/braço o tempo todo** (distância 0,00–0,09 em z 14–15,8). Correção: base mais larga (`pfa 10`, `pta 10`) e elástico preso no pé do mesmo lado por fora (`_elastico` "pes": usar o lado de fora da sola, `c + ESQ*lado*0.5`).
2. S1 — mãos em garra.

### elevacao-lateral — DEFEITOS (leve)
1. Leve — halter encosta na coxa embaixo (q0, q72–q83): `bfa 10`.
2. S1 — pegada.

### elevacao-lateral-elastico — APROVADO (S1 leve: mão em garra no elástico)

### elevacao-frontal — APROVADO (S1)
Pegada neutra, braços até a altura do ombro.

### crucifixo-inverso — DEFEITOS (leve)
Leve — câmera por trás (`cam −35`) esconde o rosto e deforma a abertura: `cam 20`. S1 — pegada.

### arnold — DEFEITOS (leve)
Leve — halter do lado longe cobre parte do rosto no início (q0, q67–q72): `bfa 18` no quadro 0. S1 — pegada.

### pike-pushup — APROVADO
Quadril alto, cabeça desce à frente das mãos, mãos e pés plantados.

### rotacao-externa — DEFEITOS
1. **Médio — dois elásticos**: além do braço que trabalha, a mão parada também fica ligada ao poste (q0–q69). Causa: `aparelhos._elastico` com `ate` lista sempre cria um segmento por mão. Correção no motor: respeitar `"maos": "f"` no prop; nos dados `{"tipo":"elastico","de":"mao_f","ate":[1.5,9.6,-5.0],"maos":"f"}`.

### rosca-direta — DEFEITOS (leve)
Leve — barra curta: as mãos encostam nos colares/anilhas (`raio_anilha` pequeno → barra "curta"); afastar as anilhas 10 cm. Pegada ok neste ângulo.

### rosca-halteres — APROVADO (S1)
### rosca-martelo — APROVADO (S1)
### rosca-elastico — APROVADO (S1 leve)

### rosca-scott — DEFEITOS (leve)
Leve — topo da coluna do banco Scott entra ~3 cm no peito (pele dentro da coluna em z 10,6–11,3). Correção em `_apoio_scott`: coluna até `centro − nrm*0.3 − d*1.0` (presa na metade de baixo da almofada).

### triceps-polia — DEFEITOS (leve)
Leve — cabo passa a ~3 cm da testa no fim (distância 0,30 em z 15,6): polia `ate [5.0, 19.5]`.

### triceps-frances — DEFEITOS
1. **Médio — dois halteres colidindo**: o francês usa UM halter seguro pelas duas mãos; o motor desenha um halter por mão e as pegadas ficam a 0,27–1,3 un. (cabeças dos halteres se interpenetram). Correção no motor: prop `{"tipo":"halter","em":"maos","unico":true}` → um halter vertical no ponto médio, mãos espalmadas sob a anilha de cima.

### triceps-testa — APROVADO (S1)
Braços verticais, barra desce até a testa (~4 cm), cabeça no banco.

### triceps-banco — APROVADO
Mãos espalmadas na borda, quadril à frente do banco, cotovelo ~90° no fundo.

### triceps-elastico — DEFEITOS
1. **Médio — elástico atravessa cabeça/costas** (t 38–50 %: distância 0,01–0,02 em z 13–16) e âncora é um anel solto no chão. Correção: base em passada (`pt [-20,-20,90]`) com o elástico sob o pé de trás (`ate [-3.5, 0.3]`) e braços em `bf [186, …]` (ligeiramente atrás da cabeça).

### triceps-coice — APROVADO (S1)
Braço paralelo ao tronco, extensão completa. (O halter do lado longe parece perto da cabeça por perspectiva; numericamente simétrico.)

### passe-medicine — DEFEITOS
1. **Crítico — mão do lado longe não toca a bola** (q0–q23: punho fechado acima da bola) e as duas mãos estão fechadas em punho. Correção no motor (`_bola`): bola no ponto médio das palmas com raio = metade da distância entre elas; mãos com dedos "rel"/espalmados (estado -0,5) em vez de punho.
2. Médio — a bola nunca sai das mãos (é um "empurra e volta", não um passe). Aceitável como demonstração; ideal: soltar a bola no quadro 1 e recebê-la no 2.

### isometria-pescoco — DEFEITOS
1. **Crítico — a mão atravessa o pescoço** na subida (q15, q94) e **afunda na cabeça com os dedos saindo por cima do crânio** no isométrico (q22–q87; distância 0,00–0,04). Causa: mão sem apoio declarado fica relaxada (garra) e a trajetória é interpolada em linha pelo pescoço. Correção: quadro intermediário com a mão por fora (`bf [100, 200]`, `bfa 40`) antes de encostar; mão espalmada na têmpora (motor: permitir `"apoio": ["mao_f"]` em superfície do corpo → `dedos −1` sem plantar no chão) e palma 1 cm fora da pele.


## QA automático (tools/anim3d/qa.py atual, parcial)

Rodado em `tools/anim/dados/lote2.json` (saída: `scratchpad/auditoria/lote2/qa.txt`). O processo foi interrompido depois de 22
exercícios (flexões, supinos, crucifixos, crossover, peck-deck, paralelas, barras, puxadas): **todos os 22 com ERRO**. Confirma os
achados acima (pegada "fora do túnel dos dedos" 4,5–9,3 cm em todos com implemento = S1; cabeça/pescoço dentro da barra fixa;
pelve flutuando 11–12 cm em supino-maquina, peck-deck e puxadas; elástico/cabo atravessando o corpo) e acrescenta:
pronação/supinação do antebraço além do limite (paralelas 179°, barra-supinada 178°, flexao-inclinada 153°, flexao-diamante 127°) —
**médio**: a mão espalmada/pegada gira o punho em vez de girar o ombro; corrigir em `mao_apoiada_rot` / `rot_pegada` limitando a
torção do antebraço a ±90° e passando o resto para a rotação do úmero. Os 34 restantes não chegaram a rodar no qa.py novo.
