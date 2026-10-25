# Auditoria das animações 3D — lote1 (56 exercícios)

Auditor: biomecânica + animação técnica. Fonte: vídeos de produção `app/src/main/assets/video3d/<id>.mp4` (16 quadros por exercício + zoom nos contatos) e renders extras do motor atual (`tools/anim3d/humano.py`, 8 quadros por ciclo) de **frente (cam 90)** e de **perfil (cam 0)**.

Evidências (folhas de contato) em `/tmp/claude-0/-home-user-teste-3/400edce2-80ea-57f6-97f9-c6ff24db5c18/scratchpad/auditoria/lote1/`:
- `folhas/<id>.jpg` — 16 quadros do MP4 de produção (rótulo `fN/total` = número do quadro no vídeo);
- `folhas/*_z*.jpg` — recortes ampliados citados abaixo;
- `r_frente/<id>.jpg`, `r_perfil/<id>.jpg` — 8 quadros do ciclo (0, T/8, …, 7T/8) com a câmera de frente / de perfil; `folhas/frente_N.jpg` e `folhas/perfil_N.jpg` empilham 6 exercícios cada.

Convenção: quadros "fN" referem-se ao MP4 de produção (24 fps salvo indicação); "q0…q3" são os quadros-chave do JSON (`tools/anim/dados/lote1.json`); "tira k/8" é o k-ésimo quadro (0-based) das tiras de frente/perfil.

## RESUMO

**56 exercícios: 19 APROVADOS (9 sem nenhuma observação, 10 só com observação leve) e 37 com DEFEITOS** — 20 com pelo menos um defeito crítico, 13 com defeito médio (sem crítico) e 4 só com defeitos leves.

- Críticos (20): agachamento-elastico, agachamento-goblet, agachamento-frontal, leg-press, mesa-flexora, elevacao-quadril, panturrilha-pe, panturrilha-sentado, panturrilha-elastico, prancha-lateral, abdominal, abdominal-bicicleta, elevacao-pernas-barra, roda-abdominal, abdominal-polia, arremesso-rotacional, ponte-pescoco, fuga-quadril, educativos-corrida, bike-subida.
- Médios (13): hack, cadeira-extensora, cadeira-flexora, step-up, terra, ponte-gluteo, ponte-unilateral, abdutora, superman, hiperextensao, mountain-climber, pallof, salto-distancia.
- Só leves (4): afundo, afundo-halteres, passada-andando, box-jump.
- Aprovados (19): agachamento-livre, agachamento-salto, agachamento-barra, bulgaro, stiff, stiff-halteres, terra-uma-perna, coice-gluteo, monster-walk, prancha, abdominal-infra, dead-bug, russian-twist, canivete, bound-lateral, salto-tesoura, tuck-jump, nordico, sentar-levantar.

### Falhas sistêmicas do motor (para o especialista do motor)
- **S1 — Pé "na ponta" (en pointe).** Sempre que o calcanhar sobe, o pé fica quase vertical apoiado na ponta dos dedos, sem dobrar os dedos (afundo, afundo-halteres, passada-andando, panturrilha-pe/sentado/elastico, educativos-corrida). Causa: `humano.dedos_pes` só endireita os dedos quando a base deles está a < 0,5 da superfície e roda no fim de `finalizar`, depois de `sem_atravessar`/`assentar_apoios`/realinhamento já terem levantado o corpo pela ponta dos dedos; `plantar` usa o antepé (78% tornozelo→dedos) como pivô, mas o corpo é reapoiado pelo ponto mais baixo da pele (a ponta). Correção: (1) dobrar os dedos (`toeN-1` até ficarem paralelos ao chão) ANTES de qualquer apoio/encosto vertical; (2) pivô de apoio do pé = cabeça de `toe3-1` (articulação metatarsofalângica) no chão; (3) limitar a flexão plantar efetiva a ~50° e, se o dado pedir mais, girar só os dedos.
- **S2 — Corpo deitado/sentado flutua.** Os únicos contatos que o motor procura são mãos, pés e joelhos (`colocar_chave` passo 1, `ajuste_altura_dada`, `apoiar_superficies`); pelve, costas, escápulas, ombro, cabeça e glúteo sentado nunca são "apoio". Com `y` dado o corpo é encostado pelos pés e a pelve fica no ar (abdominal, ponte-gluteo, ponte-unilateral, ponte-pescoco, fuga-quadril, panturrilha-sentado, elevacao-quadril); sem `y`, o ponto mais baixo pode ser um braço aberto (abdominal-bicicleta). Correção: incluir partes de tronco (`px_partes["tronco"]` dividido em pelve/lombar/escápulas/cabeça) como candidatos de apoio: quando o tronco está a < 35° da horizontal ou a pelve 2D está a < 1,5 de uma superfície, encostar pelve/escápulas no chão/banco (girando em torno dos pés plantados, como o "nivelar" já faz para mãos×pés) e só então fazer IK de pés/mãos.
- **S3 — Mão que não segura.** Só a barra fixa recebe `rot_pegada` + IK (`segurar_barra`); elástico, cabo, kettlebell (goblet), barra em front rack, medicine ball, guidão da bike, pegadores de máquina e a própria barra fixa (palma acima da barra, item 40) ficam com a mão em garra aberta, no ar ou atravessada pelo implemento (agachamento-elastico, panturrilha-elastico, goblet, frontal, hack, abdutora, leg-press, mesa-flexora, roda-abdominal, arremesso-rotacional, bike-subida, elevacao-pernas-barra). Correção: função única "pegar(implemento, eixo, ponto)" chamada por todos os acessórios: IK do punho até o ponto de pegada, `rot_pegada` com o eixo do implemento, dedos=1 com curva "peg" que realmente fecha (≈(80,95,70)); para bola: IK das duas mãos a pontos opostos da superfície.
- **S4 — Máquinas sem pegadores/almofadas.** Leg press, cadeira extensora/flexora, mesa flexora, abdutora, hack e panturrilha sentado não têm pegadores (as mãos pendem ou espalmam no assento) e faltam almofada de coxa (flexora sentada, panturrilha sentado), rolo de tornozelo (hiperextensão) e pedais (abdutora). Correção: em `aparelhos._extras_maquina`, adicionar pegadores laterais por tipo + IK das mãos (S3), almofada de coxa e pedais.
- **S5 — `rol` gira o corpo inteiro, inclusive os pés plantados.** Ponte-pescoco e fuga-quadril ficam com as pernas no ar; prancha-lateral perde o apoio do braço. Correção: aplicar `rol` em torno do eixo que passa pelos apoios declarados (pés/antebraço) ou só da pelve para cima, preservando os apoios com IK; aceitar cotovelo/antebraço em `"apoio"`.
- **S6 — Geometria de aparelhos.** `_plataforma` centra a placa do leg press num só pé e não fixa a orientação; `_plataforma_movel` passa os trilhos pelas pernas; `_polia` desloca a torre sem deslocar a polia (cabo "saindo do nada" na abdominal-polia) e mede a folga pelo pescoço (cabeça encosta na torre); `_bola` deixa a bola no ponto médio das mãos mesmo com elas afastadas; `_kettlebell` não sabe a pegada goblet (chifres, bola no peito); `_barra` deixa a anilha atravessar o chão (hip thrust); `_elastico` com `ate:"pes"` termina na ponta dos dedos; não existe acessório "roda" abdominal.
- **S7 — Dedos das mãos livres em garra.** A curva "rel" (16,20,14)/(10,12,8) deixa as mãos soltas tensas e abertas em quase todos os exercícios; suavizar.
- **Padrão de dados (não é motor, mas repete):** cadeiras com `maquina` em x -3.7 e quadril em x 0 com `t` 186–192 deixam ~15–20 cm entre as costas e o encosto (extensora, flexora, abdutora); trocar por `maquina.x` -2.4 e `t` 176–178.


---

## 1. agachamento-livre — APROVADO (1 leve)
Evidência: `folhas/agachamento-livre.jpg`, `folhas/agl_loop.jpg`, `r_frente/agachamento-livre.jpg`, `r_perfil/agachamento-livre.jpg`.
- Técnica conferida: pés na largura dos ombros, quadril abaixo da paralela (coxa 98–99°), tronco ~37° à frente, calcanhares no chão, braços à frente como contrapeso, joelhos na linha dos pés (frente), loop sem salto (f1≈f84).
- [leve] Mãos com dedos "em garra" abertos durante todo o movimento (f34–f62). Causa: motor (`Humano.dedos` com v=0 → curva "rel"); pose de mão relaxada parece tensa. Correção (motor): curva "rel" mais suave para mãos livres à frente (ex.: (10,12,8)/(6,8,6)) ou dedos semiestendidos quando o braço está elevado.

## 2. agachamento-elastico — DEFEITOS (1 crítico, 2 médios)
Evidência: `folhas/agachamento-elastico.jpg`, `folhas/agel_z.jpg` (f1 e f45), `r_frente/agachamento-elastico.jpg`.
- [crítico] Mão não segura o elástico: punho dobrado para trás, dedos abertos em garra apontando para cima; o elástico termina no centro da palma e atravessa o antebraço (f1, f45; todos os quadros). Causa: motor — `aparelhos._elastico` (ramo `ate == "pes"`) liga `h.pegada()` ao pé, mas a orientação da mão nunca é ajustada ao eixo do elástico (não há `rot_pegada` para elástico/cabo; só `segurar_barra` usa). Correção (motor): para `elastico/cabo` com `de: maos`, aplicar `h.rot_pegada(sf, eixo=direção do elástico ⟂ antebraço)` e dedos=1 (punho fechado) antes de desenhar; o ponto de saída do elástico deve ser a borda inferior do punho fechado (entre mínimo e anelar), não o centro da palma.
- [médio] Posição das mãos errada: mãos acima dos ombros, na altura das orelhas e abertas para os lados em "goalpost" (frente: `r_frente` tira 0–7; bfa 22). No agachamento com elástico sob os pés as mãos ficam na frente dos ombros (posição de front rack) ou ao lado dos ombros com cotovelos à frente. Causa: dado — `bf [30,192] / bt [27,189]` (antebraço passando da vertical, mão atrás/acima do ombro) e `bfa 22`. Correção: q0/q1 `bf [-20,150], bt [-23,147], bfa 10, afa -20` (cotovelo baixo à frente, mão à frente do ombro); q2/q3 manter relação (antebraço ~150–160 com o tronco a 146).
- [médio] Elástico termina na ponta dos dedos do pé, não sob o meio do pé (f1, f45). Causa: motor — `_elastico` (`ate == "pes"`) usa o centróide dos vértices mais baixos de `pe_f/pe_t`, que com o pé plano cai no antepé/dedos. Correção (motor): âncora = ponto da sola sob o arco (entre `foot` e `toe3-1`, ~45% do comprimento) e z = chão + 0,02; desenhar o elástico passando sob a sola (dois segmentos: mão→borda medial do pé e sob a sola).

## 3. agachamento-salto — APROVADO
Evidência: `folhas/agachamento-salto.jpg`, `r_frente`/`r_perfil` agachamento-salto.
- Contramovimento com braços atrás, extensão tripla com braços acima, voo ~22 cm em parábola, aterrissagem com flexão de joelhos/quadril e retorno ao agachamento; joelhos alinhados (frente). Nada a corrigir.

## 4. agachamento-goblet — DEFEITOS (1 crítico, 2 médios)
Evidência: `folhas/agachamento-goblet.jpg`, `folhas/gob_z1.jpg` (f1), `folhas/gob_z2.jpg` (f52), `folhas/gob_perfil_z.jpg`, `r_frente/agachamento-goblet.jpg`.
- [crítico] Pegada irreal: as mãos ficam entrelaçadas com os dedos apontando para cima ("rezando em garra") acima do kettlebell; a alça do kettlebell some dentro das mãos e a bola fica pendurada abaixo, longe do peito (f1, f52). No goblet as palmas abraçam os "chifres" (laterais da alça) com a bola encostada no esterno. Causa: motor — `aparelhos._kettlebell` posiciona a alça no ponto médio das duas pegadas e pendura a bola por gravidade, sem orientar as mãos; dado — `afa/ata -38` cruzam os antebraços para dentro. Correção (motor): no modo `em: maos` com antebraços verticais (goblet), virar o kettlebell de cabeça para baixo ou com a bola encostada ao peito (direção bola = -frente do tronco + baixo) e aplicar `rot_pegada` com eixo vertical (cada palma numa lateral da alça, dedos fechados). Dado: `bf [10,155], bt [7,152], bfa -4, afa -12` para o kettlebell ficar ~8 cm à frente do esterno.
- [médio] Kettlebell longe do corpo (perfil: ~25 cm à frente do peito, `gob_perfil_z.jpg`) e, no fundo, apoiado/entrando na coxa da frente (f46–f63, `gob_z2.jpg`). Causa: dado q2/q3 `bf [2,128]` com tronco 158 → mãos baixas. Correção: q2/q3 `bf [-12,140], bt [-15,137]` e manter os cotovelos por dentro dos joelhos (`bfa -8`).
- [médio] Pés deslizam lateralmente durante a descida (frente: largura dos pés cresce ~30% entre q1 e q2; `r_frente` tira 0 vs 4). Causa: dado — `pfa` 8→19 aumenta a abdução da coxa e, como `fixo:"pes"` só trava o eixo x (sagital) do pé da frente, o pé de trás e a largura mudam. Correção: manter `pfa` constante (15 nos 4 quadros) e abrir os joelhos com rotação, ou (motor) travar também z dos dois pés quando `fixo:"pes"` (âncora 3D por pé em `ancorar_apoios`).

## 5. agachamento-barra — APROVADO (1 leve)
Evidência: `folhas/agachamento-barra.jpg`, `folhas/agb_z.jpg`, `folhas/agb_z2.jpg`, `folhas/agb_perfil_z.jpg`, `r_frente/agachamento-barra.jpg`.
- Barra no trapézio superior (perfil), pegada larga com as duas mãos na barra (frente), profundidade na paralela, tronco ~43°.
- [leve] Câmera 3/4: a mão da frente fica escondida atrás da anilha e a barra parece passar na altura da boca (perspectiva, `agb_z2.jpg`). Correção: `"cam": 40` (mais perfil) ou `cam_el` 18 para a barra aparecer abaixo da cabeça.

## 6. agachamento-frontal — DEFEITOS (1 crítico)
Evidência: `folhas/agachamento-frontal.jpg`, `folhas/agf_z.jpg`, `folhas/agf_frente_z.jpg`, `r_perfil/agachamento-frontal.jpg`.
- [crítico] Mãos não seguram a barra: dedos abertos em garra apontando para cima, atrás/acima da barra; a barra passa na frente das palmas sem contato (f1, f54; frente tira 0–1). Na posição de front rack os dedos ficam sob a barra (pegada clean) com cotovelos altos à frente, braço ~paralelo ao chão. Causa: motor — `segurar_barra`/`corrigir_barra` só fecham a mão em barra fixa; com `barra_modo "rack"` a barra é colocada nos ombros mas a mão não é orientada (sem `rot_pegada`, dedos=1 sem envolver). Dado — `bf [75,228]` deixa o antebraço quase vertical apontando para trás-cima, mão acima do ombro. Correção (motor): no modo rack, IK das mãos até a barra (pegada a ~1,2× largura dos ombros) com `rot_pegada(eixo da barra, supinada=True)` e dedos 0,6 (dedos sob a barra). Dado: `bf [85,200], bt [82,197], bfa 25, afa 10` (cotovelo à frente na altura do ombro).

## 7. leg-press — DEFEITOS (3 críticos, 1 médio)
Evidência: `folhas/leg-press.jpg`, `folhas/legpress_frente_z.jpg`, `folhas/legpress_perfil_z.jpg`, `r_frente/leg-press.jpg`, `r_perfil/leg-press.jpg`.
- [crítico] Pé fora da plataforma: a plataforma fica deslocada para o lado do pé de trás; o pé da frente fica inteiro fora da placa, empurrando o ar (frente, todas as tiras). Causa: motor — `aparelhos._plataforma` calcula o centro só com os vértices mais extremos da sola (`proj > lim - 0.25`), que pertencem a um único pé; e a rotação `(-n).to_track_quat(...)` não fixa o eixo lateral, então a placa 7×5 pode girar no próprio plano. Correção (motor): centro = média dos centróides das duas solas (por pé), e orientar a placa com eixo X = lateral do corpo (`ESQ` no mundo) e Y = projeção do eixo do trilho.
- [crítico] Costas apoiadas no ar: o tronco está reclinado ~26° (t -116) mas o encosto é um banco horizontal baixo; a parte superior das costas e a cabeça ficam ~20 cm acima do estofado (perfil). Causa: dado — segundo `banco` (x -7.2, h 4.0) sem `inc`. Correção: trocar por encosto inclinado ao longo do tronco: `{"tipo":"banco","x":-3.2,"y":0,"w":4.4,"h":2.3,"inc":45,"enc":7}` (encosto saindo da borda de trás do assento) e ajustar `t` para -135 (costas no encosto a 45°), ou manter t e usar `inc` 26.
- [crítico] Trilhos atravessam as coxas/canelas: as duas vigas diagonais passam por dentro das pernas no começo e no fim (perfil tira 0 e 7; produção f1, f86). Causa: motor — `_plataforma_movel` põe as vigas em x = ±3,2 sem considerar a largura das pernas e prolonga o trilho 3 unidades além do curso (`ext0/ext1`) passando pelo corpo. Correção (motor): vigas em x = ±(meia largura da placa + 0,4) = ±3,9 e não prolongar o trilho para o lado do assento (só para o lado de cima).
- [médio] Mãos abertas pendendo ao lado do assento, sem pegadores (f1–f86). Correção: adicionar pegadores laterais no assento (motor, `_plataforma_movel`/leg press) e IK das mãos neles com dedos=1.
- Câmera `cam 25`: a placa esconde os pés quase o tempo todo; usar `cam 0` (perfil puro).

## 8. hack — DEFEITOS (1 médio, 1 leve)
Evidência: `folhas/hack.jpg`, `folhas/hack_z.jpg` (f1, f54), `r_frente/hack.jpg`, `r_perfil/hack.jpg`.
- [médio] Mãos não seguram os pegadores: a máquina desenha pegadores na lateral do quadril, mas a mão da frente fica aberta ao lado dele e a de trás solta no ar (f1); no fundo as duas mãos vão para cima das coxas (f54). Causa: dado `bf [40,62]`/`bfa 20` + motor (`_hack` não faz IK das mãos aos pegadores). Correção (motor): IK das mãos até os pegadores do `_hack` (ou pegadores junto às ombreiras, como nas máquinas reais) com `rot_pegada` vertical e dedos=1 em todos os quadros.
- [leve] Pé de trás com o antepé passando da borda frontal da plataforma em f1 (`hack_z.jpg`). Correção: plataforma 0,5 unidade mais longa (`w` 5.9) ou `x` dos pés -0,3.

## 9. cadeira-extensora — DEFEITOS (1 médio, 1 leve)
Evidência: `folhas/cadeira-extensora.jpg`, `r_perfil/cadeira-extensora.jpg` (`folhas/perfil_2.jpg`, linha 3).
- [médio] Costas longe do encosto: o tronco fica ~20 cm à frente do encosto e ainda inclinado 10° para a frente (perfil, todos os quadros) — corpo sem apoio nas costas, e o quadril não encaixado no fundo do assento. Causa: dado — quadril em x 0 com encosto (`maquina` x -3.7, w 1.0) a 2,7 unidades e `t 190`. Correção: `maquina.x` -2.4 (face em -1.4), `banco` x -2.4 / w 6.0 (borda da frente em 3.6, joelho na borda), `t` 176 (encosto levemente reclinado: ou usar `banco` com `inc` 100 no lugar da `maquina`).
- [leve] Mãos espalmadas no assento sem pegadores (f1–f94). Correção: pegadores laterais no assento + IK das mãos (dedos=1).

## 10. cadeira-flexora — DEFEITOS (2 médios, 1 leve)
Evidência: `folhas/cadeira-flexora.jpg`, `r_perfil/cadeira-flexora.jpg` (`folhas/perfil_2.jpg`, linha 4).
- [médio] Costas sem encosto (mesmo problema da extensora: ~20 cm de vão, `t 192`). Correção: `maquina.x` -2.4, `banco` x -2.4 w 5.0, `t` 176.
- [médio] Falta o rolo/almofada das coxas (na cadeira flexora o apoio sobre as coxas logo acima do joelho impede o quadril de subir). Causa: motor — `cadeira-flexora` não ganha `_rolo_canela`/almofada de coxa. Correção (motor): adicionar almofada fixa sobre as coxas (como `_rolo_canela`, mas sobre a coxa distal) quando o id contém "flexora" e o exercício é sentado.
- [leve] Mãos espalmadas no assento sem pegadores. Correção como na extensora.

## 11. mesa-flexora — DEFEITOS (2 críticos, 1 médio)
Evidência: `folhas/mesa-flexora.jpg`, `folhas/mesa_z.jpg`, `folhas/mesa_z2.jpg`, `folhas/mesa_perfil_z.jpg`, `r_frente/mesa-flexora.jpg`.
- [crítico] Rolo do lado errado da perna: na posição inicial o rolo fica sob a canela/peito do pé (lado anterior, entre a perna e o chão), sustentando as pernas, e não sobre o tendão de Aquiles (f1, `mesa_z.jpg`, `mesa_perfil_z.jpg` esquerda). Assim a flexão "empurra" o rolo com a frente da canela — fisicamente impossível de gerar resistência para os isquiotibiais. Causa: motor — `_rolo_canela(..., frente=True)` usado também na mesa flexora (prona). Correção (motor): para `mesa-flexora` usar o rolo do lado posterior (acima do calcanhar, `frente=False` relativo ao corpo deitado de bruços) e o braço da alavanca girando em torno do joelho.
- [crítico] Mãos sem apoio real: o braço da frente pende até o chão com a palma espalmada no piso e o de trás abraça o pé do banco (f1–f86, `mesa_z2.jpg`); na mesa flexora as mãos seguram os pegadores na frente do banco. Causa: dado `bf [-16.7,123.1]` (braço para trás e antebraço para baixo/à frente) e motor sem pegadores. Correção: pegadores sob a cabeceira do banco (motor) e dado `bf [100,170]`, `bt [97,167]` (cotovelos dobrados, mãos à frente da cabeça segurando), com IK.
- [médio] Cabeça para fora do banco com o pescoço caído (f1, frente). Correção: banco 1 unidade mais longo para a frente (x -4.9, w 11.2) ou quadril x +1; `c` 95.

## 12. afundo — DEFEITOS (2 leves)
Evidência: `folhas/afundo.jpg`, `folhas/afundo_z.jpg`, `r_frente/afundo.jpg`, `r_perfil/afundo.jpg`.
- Técnica correta (afundo estacionário/split squat): canela da frente vertical, joelho de trás a ~10 cm do chão, tronco ereto.
- [leve] Pé de trás "na ponta" (en pointe): o pé fica quase vertical apoiado só na ponta dos dedos, sem dobrar os dedos (f1, f45, `afundo_z.jpg`). Humanos apoiam a bola do pé com os dedos estendidos no chão. Causa: motor — `dedos_pes` só endireita os dedos quando a base dos dedos está a <0,5 da superfície e é chamado no fim de `finalizar`, depois de `sem_atravessar`/`assentar_apoios` já terem levantado o corpo pela ponta dos dedos; dado `pt[2]=35`. Correção (motor): ver falha sistêmica S1. Dado: `pt[2]` 50–55.
- [leve] Pés em linha (base "na corda bamba"): na frente o pé de trás fica atrás do da frente na mesma linha (`r_frente` tira 4–5). Correção: `pta` -6 / `pfa` 6 (pés na largura do quadril).

## 13. afundo-halteres — DEFEITOS (1 leve)
Evidência: `folhas/afundo-halteres.jpg`, `folhas/afh_z.jpg`, `r_frente/afundo-halteres.jpg`, `r_perfil/afundo-halteres.jpg`.
- Afundo à frente com retorno, alternando as pernas; pegada neutra fechada nos halteres; joelho de trás quase no chão; ok.
- [leve] Pé de trás en pointe no fundo (f22, f78), mesma causa S1.

## 14. passada-andando — DEFEITOS (1 leve)
Evidência: `folhas/passada-andando.jpg`, `r_frente/passada-andando.jpg`, `r_perfil/passada-andando.jpg`.
- Passada com piso rolante, perna de trás passa à frente com o joelho elevado, alternância correta.
- [leve] Pé de trás en pointe no fundo (f1, f34, f72), causa S1.

## 15. bulgaro — APROVADO
Evidência: `folhas/bulgaro.jpg`, `folhas/bulg_z.jpg`, `r_frente/bulgaro.jpg`, `r_perfil/bulgaro.jpg`.
- Peito do pé de trás apoiado no banco, canela da frente quase vertical, descida até coxa ~paralela, halteres pendurados com pegada neutra; nada a corrigir.

## 16. step-up — DEFEITOS (1 médio, 1 leve)
Evidência: `folhas/step-up.jpg`, `r_frente/step-up.jpg`, `r_perfil/step-up.jpg`.
- [médio] Perna de trás dá um "coice": ao subir, a perna que sai do chão dobra o joelho ~105° e o pé sobe atrás até a altura do quadril (f6–f16), antes de vir à frente para o "knee drive". No step-up a perna de trás empurra e acompanha logo atrás/abaixo, subindo até a caixa ou ao joelho alto pela frente. Causa: dado q1 `pt [20,-85,50]`. Correção: q1 `pt [5,-30,60]` (pé deixa o chão quase sob o quadril) e q4 (descida) `pt [10,-40,60]`.
- [leve] Câmera `cam 28`: o pé de trás no chão fica escondido atrás da caixa em f1 e f59–f74. Correção: `cam 0` ou `cam 45` com a caixa à esquerda do corpo na imagem.

## 17. terra — DEFEITOS (1 médio, 1 leve)
Evidência: `folhas/terra.jpg`, `folhas/terra_z.jpg`, `r_frente/terra.jpg`, `r_perfil/terra.jpg` (`folhas/perfil_3.jpg`, linha 5).
- Pegada pronada fechada fora dos joelhos, barra sobe colada às pernas, bloqueio final ereto, barra volta ao chão; anilhas tocam o chão (perfil).
- [médio] Posição inicial parece stiff, não levantamento terra: tronco a ~24° da horizontal (t 114) com joelhos quase estendidos (flexão 82° só pelo ângulo da coxa a 66°) e quadril alto (perfil tira 0–1). No terra convencional o quadril fica entre joelho e ombro, tronco ~40–45° da horizontal, ombros sobre a barra. Correção: q0/q1 `t 130, c 150, pf [80,-22,90], pt [79,-23,90], x -2.6`; q2 `t 140, pf [55,-12,90]`.
- [leve] Câmera `cam 30`: as anilhas dominam o quadro e a de longe parece subir até o peito (perspectiva), figura pequena e escura. Correção: `cam 15`, `cam_el 8`.

## 18. stiff — APROVADO (1 leve)
Evidência: `folhas/stiff.jpg`, `r_frente/stiff.jpg`, `r_perfil/stiff.jpg`.
- Joelhos levemente flexionados e fixos, quadril vai para trás, barra desce rente às pernas até meia canela, coluna neutra.
- [leve] Mesma câmera `cam 30` do terra (figura pequena/escura). Correção: `cam 15`.

## 19. stiff-halteres — APROVADO
Evidência: `folhas/stiff-halteres.jpg`, `r_frente/stiff-halteres.jpg`, `r_perfil/stiff-halteres.jpg`.
- Halteres descem à frente das pernas até a canela, joelhos semiflexionados, coluna neutra; pegada fechada. Nada a corrigir.

## 20. terra-uma-perna — APROVADO
Evidência: `folhas/terra-uma-perna.jpg`, `folhas/tup_z.jpg`, `r_frente/terra-uma-perna.jpg`, `r_perfil/terra-uma-perna.jpg`.
- Kettlebell na mão contralateral à perna de apoio, tronco e perna livre chegam juntos à horizontal, joelho de apoio levemente flexionado, mão fechada na alça. Nada a corrigir.

## 21. ponte-gluteo — DEFEITOS (1 médio, 1 leve)
Evidência: `folhas/ponte-gluteo.jpg`, `folhas/ponte_z.jpg` (f1, f35), `folhas/ponte_perfil_z.jpg`, `r_frente/ponte-gluteo.jpg`.
- [médio] Mãos e antebraços flutuando: no topo (f12–f63) os braços ficam na horizontal com as palmas 5–10 cm acima do tapete (perfil `ponte_perfil_z.jpg` direita); na ponte as palmas ficam apoiadas no chão ao lado do corpo, ajudando a estabilizar. Causa: dado `bf [92,92]` constante enquanto o ombro sobe com o tronco (t -90 → -62); o braço deveria acompanhar o chão. Correção: declarar `"apoio":["pe_f","pe_t","mao_f","mao_t"]` nos três quadros (o motor espalma e encaixa as mãos) e q1/q2 `bf [100,100], bt [97,97]` (braço inclinado até o chão).
- [leve] Quadril ~2–3 cm acima do tapete na posição de repouso (f1, sombra separada em `ponte_z.jpg`). Causa: motor — com `y` dado, `ajuste_altura_dada` só encosta os pés; glúteo/costas não são considerados apoio (S2). Dado: q0 `y` 1.0.
- Amplitude: no topo ainda restam ~18° de flexão de quadril (coxa 100, tronco -62). Sugestão: q1/q2 `t -58` para alinhar joelho-quadril-ombro.

## 22. ponte-unilateral — DEFEITOS (1 médio, 1 leve)
Evidência: `folhas/ponte-unilateral.jpg`, `r_frente/ponte-unilateral.jpg`, `r_perfil/ponte-unilateral.jpg`.
- [médio] Mesmo problema dos braços flutuando no topo (f13–f67). Correção idêntica à ponte-gluteo (`apoio` com as duas mãos, `bf [100,100]`).
- [leve] Quadril levemente fora do tapete em f1 (S2). Correção: q0 `y` 1.0.
- Perna livre estendida e alinhada à coxa de apoio, sem rotação de pelve: correto.

## 23. elevacao-quadril (hip thrust) — DEFEITOS (2 críticos)
Evidência: `folhas/elevacao-quadril.jpg`, `folhas/hip_perfil_z.jpg`, `r_frente/elevacao-quadril.jpg`, `r_perfil/elevacao-quadril.jpg` (`folhas/perfil_4.jpg`, linha 5).
- [crítico] Na posição baixa as costas não tocam o banco: o tronco inclinado fica ~25 cm à frente da borda do banco e o glúteo também não toca o chão — corpo sustentado só pelos pés e pela barra (perfil tira 0, `hip_perfil_z.jpg` esquerda; produção f1, f80–f86). No hip thrust as escápulas ficam apoiadas na borda do banco o tempo todo (é o eixo do movimento). Causa: dado — q0 `x -0.83, y 1.8, t -128` coloca os ombros em x≈-4.9 e z≈5,0, mas o banco (x -10…-4.3) começa depois; a escápula precisa ficar na borda (x≈-4.3, z≈4.0). Correção: banco `x -9.6` (borda em -3.9) e q0 `x 0.2, y 1.6, t -112` (ombro na borda); q1/q2 `x 0.18, y 4.0, t -92` (tronco paralelo ao chão com a escápula ainda na borda). Motor: em `repousar` tratar também banco atrás das costas com o tronco inclinado (encostar a escápula na quina).
- [crítico] Anilhas atravessam o chão na posição baixa (perfil tira 0/7: borda inferior da anilha abaixo da linha dos pés). Causa: motor — `_barra` não limita a altura do centro da barra a ≥ raio da anilha; dado — barra no quadril com `y 1.8`. Correção (motor): em `corrigir_barra`/`_barra`, se `c.z < R`, subir o corpo (ou impedir a pose) — no hip thrust real a anilha toca o chão na posição baixa, então o quadril deve ficar com a barra a ≥ raio (22,5 cm) do chão: q0 `y` ≥ 2.3.

## 24. coice-gluteo — APROVADO
Evidência: `folhas/coice-gluteo.jpg`, `r_frente/coice-gluteo.jpg`, `r_perfil/coice-gluteo.jpg`.
- Quatro apoios com mãos sob os ombros e joelhos sob o quadril, joelho de trabalho mantido a ~90° enquanto o calcanhar sobe ao teto, coluna sem hiperextensão visível. Nada a corrigir.

## 25. abdutora — DEFEITOS (2 médios, 1 leve)
Evidência: `folhas/abdutora.jpg`, `folhas/abd_z.jpg`, `folhas/abd_perfil_z.jpg`, `r_perfil/abdutora.jpg`.
- [médio] Costas sem encosto (perfil: ~15 cm entre as costas e o encosto, `abd_perfil_z.jpg`). Correção: `maquina.x` -2.4 e `t` 178 (como na extensora).
- [médio] Pés arrastando no chão: com a abdução, os pés deslizam ~25 cm para fora sobre o piso (f1→f23; `abd_z.jpg`). Na cadeira abdutora os pés ficam em apoios (pedais) presos às alavancas e sobem com elas. Causa: motor — não há apoio para os pés na abdutora; os pés ficam no chão porque o quadril está a 4,6. Correção (motor): desenhar apoio de pé preso a cada almofada (`_almofadas_joelho`) e erguer os pés do chão (dado: `pf [90,-2,92]` → `pf [88,10,100]` para o pé ficar à frente, apoiado no pedal).
- [leve] Mãos pairando no ar ao lado do assento em f1 (dedos abertos, sem pegador), depois apoiadas na almofada. Correção: pegadores laterais + IK.

## 26. monster-walk — APROVADO (1 leve)
Evidência: `folhas/monster-walk.jpg`, `r_frente/monster-walk.jpg`, `r_perfil/monster-walk.jpg`.
- Semiagachamento, miniband nos tornozelos tensionando a cada passo lateral, alternância correta de pés.
- [leve] Mãos em garra com dedos abertos (f1–f96). Causa motor (curva "rel" dos dedos, ver item 1).

## 27. panturrilha-pe — DEFEITOS (1 crítico, 1 leve)
Evidência: `folhas/panturrilha-pe.jpg`, `folhas/pant_z.jpg` (f1, f43), `r_perfil/panturrilha-pe.jpg`.
- [crítico] No topo o atleta fica "na ponta" como bailarina: pé quase vertical, apoiado só na ponta dos dedos, sem a dobra dos dedos (f25–f67, `pant_z.jpg`). Na elevação de panturrilha o peso fica na bola do pé com os dedos estendidos no chão (articulações metatarsofalângicas a ~60° de extensão). Causa: motor — S1 (`dedos_pes`/`plantar`). Correção: S1; dado `pf[2]/pt[2]` 44 → 52 (≈38° de flexão plantar, valor típico com joelho estendido) e `apoio` já correto.
- [leve] Sem degrau: no chão a amplitude fica só concêntrica. Sugestão: `{"tipo":"banco","x":-0.5,"y":0,"w":2.2,"h":0.8}` sob o antepé com o calcanhar descendo abaixo da borda (ponto de partida com `pe` 105).

## 28. panturrilha-sentado — DEFEITOS (2 críticos, 1 médio)
Evidência: `folhas/panturrilha-sentado.jpg`, `folhas/pants_perfil_z.jpg`, `r_frente/panturrilha-sentado.jpg`.
- [crítico] Sentado no ar: o glúteo fica ~15 cm acima e à frente do banco em todos os quadros (perfil `pants_perfil_z.jpg`); o banco aparece atrás/abaixo, sem contato. Causa: motor — com `y` dado, `ajuste_altura_dada` sobe o corpo até os pés encostarem no bloco (h 1.2) sem considerar que o quadril precisa assentar no banco (S2); e o quadril (x 0) fica sobre a borda da frente do banco curto (x -3…1.6) na proporção 3D. Correção (dado): banco `x -2.4, w 4.6, h 4.3`; bloco `x 3.4, w 2.0, h 1.2` (só sob o antepé); quadril `x 0.2, y 5.2`. Correção (motor): quando o quadril 2D está sobre um banco, a altura final deve encostar o glúteo no assento (prioridade sobre os pés; pés que não alcançam viram IK).
- [crítico] Pés na ponta no topo (f25–f67) e, na posição baixa, o calcanhar fica pousado no bloco em vez de descer abaixo da borda (sem alongamento). Causa: S1 + bloco largo demais sob o pé inteiro. Correção: bloco só sob o antepé (acima) e q0/q1 `pf[2]` 125 (calcanhar abaixo da borda), q2/q3 `pf[2]` 70.
- [médio] Falta a almofada sobre as coxas (na panturrilha sentado a carga vem dela; aqui as mãos só repousam nos joelhos). Correção (motor): almofada de coxa (como `_rolo_canela`) presa a uma alavanca; mãos nos pegadores da alavanca.

## 29. panturrilha-elastico — DEFEITOS (1 crítico, 2 médios)
Evidência: `folhas/panturrilha-elastico.jpg`, `r_frente/panturrilha-elastico.jpg`, `r_perfil/panturrilha-elastico.jpg`.
- [crítico] Pés na ponta no topo (f24–f63), causa S1. Correção: S1 e `pf[2]` 36 → 52.
- [médio] Mão não segura o elástico (mesma falha do agachamento-elastico: punho aberto em garra, elástico saindo da palma) e as mãos ficam acima dos ombros, a mão da frente cobrindo o rosto (f1–f86). Correção: motor (pegada em elástico, item 2) e dado `bf [-20,150], bt [-23,147], bfa 10, afa -20`.
- [médio] Elástico termina na ponta dos dedos (deveria passar sob a bola do pé). Correção (motor): âncora do elástico sob o antepé (ver item 2).

## 30. superman — DEFEITOS (1 médio)
Evidência: `folhas/superman.jpg`, `folhas/sup_perfil_z.jpg`, `r_frente/superman.jpg`.
- [médio] Na fase de repouso as pernas não descansam no tapete: coxas e pés ficam 5–10 cm acima do chão (perfil tira 0, produção f1 e f96–f103 com sombra separada). Causa: dado — q0 `pf [-90,-90,-60]` com tronco 90 apoia o corpo pelo ponto mais baixo (peito/mãos); as pernas a -90 ficam acima do chão porque a pelve 3D é mais alta que o peito. Correção: q0 `pf [-86,-86,-60], pt [-88,-88,-62]` (pernas ligeiramente para baixo, encostam) e `bf [88,88]` (braços apoiados).
- Fase de subida/descida e contração de 2 s corretas.

## 31. hiperextensao — DEFEITOS (2 médios)
Evidência: `folhas/hiperextensao.jpg`, `folhas/hip_z.jpg` (f1, f46), `r_frente/hiperextensao.jpg`, `r_perfil/hiperextensao.jpg`.
- [médio] Falta o rolo que prende os tornozelos: os pés só pousam (de ponta) numa placa baixa; sem a trava o corpo cairia para a frente na descida (f1–f85). Causa: dado/motor — props sem `apoio_tornozelo`. Correção: adicionar `{"tipo":"apoio_tornozelo"}` (rolo sobre o tendão de Aquiles) e a placa sob a sola inteira (`banco` x -7.9, w 3.0, h 0.5, com `pf[2]` 135 para o pé ficar plano na placa a 45°).
- [médio] Mãos cruzadas no peito com os dedos abertos em leque e a mão de trás atravessando o peito/saindo por baixo do tórax como uma lâmina (f35–f63, `hip_z.jpg` direita). Causa: dado `afa/ata -55` cruzam demais os antebraços para dentro do tórax; motor sem colisão braço-tronco. Correção: `bf [-15,100], bt [-18,97], bfa -4, afa -30` (mãos nos ombros opostos, antebraços sobre o peito) e dedos semifechados.

## 32. prancha — APROVADO (1 leve)
Evidência: `folhas/prancha.jpg`, `folhas/prancha_z.jpg`, `folhas/prancha_perfil_z.jpg`, `r_frente/prancha.jpg`.
- Antebraços no tapete com cotovelos sob os ombros (perfil), corpo alinhado, pontas dos pés; respiração sutil.
- [leve] Dedos abertos em leque e antebraços paralelos com palmas para baixo; é aceitável, mas punhos levemente fechados/apontando ao centro é o padrão. Correção opcional: `afa/ata` 8 e dedos 0,3.

## 33. prancha-lateral — DEFEITOS (1 crítico)
Evidência: `folhas/prancha-lateral.jpg`, `folhas/pl_z.jpg` (f1), `r_frente/prancha-lateral.jpg`.
- [crítico] Corpo apoiado no ar: o braço de apoio pende reto para baixo com a mão solta, dedos para baixo, além da borda do tapete e sem tocar o chão; nenhum antebraço/cotovelo apoiado (f1–f86, `pl_z.jpg`); só os pés tocam o tapete. Na prancha lateral o antebraço fica no chão com o cotovelo sob o ombro (ou a palma espalmada com o braço estendido). Causa: dado — `rol 70` (o corpo deveria estar a ~90° para o lado e inclinado ~20° em relação ao chão), `bt [0,90], bta 72` pensado no plano sagital; motor — `rol` gira o corpo inteiro depois da pose e não existe IK/encosto para antebraço (`encaixar` só trata mãos e pés; `apoio` não aceita cotovelo). Correção: dado `rol 88`, `t 160` (corpo inclinado 20° a partir dos pés), `bt [90,90], bta 0` (braço vertical em relação ao chão, antebraço à frente), `"apoio":["mao_t","pe_f","pe_t"]`; motor: aceitar `"cotovelo_f/t"` em `apoio` e encostar o antebraço na superfície (IK de ombro) quando declarado.

## 34. abdominal — DEFEITOS (1 crítico, 1 médio)
Evidência: `folhas/abdominal.jpg`, `r_perfil/abdominal.jpg` (`folhas/perfil_6.jpg`, linha 4), `r_frente/abdominal.jpg`.
- [crítico] Corpo flutuando: o quadril e as costas ficam acima do tapete o tempo todo (sombra separada sob a pelve em f1–f66; perfil tira 0 com vão sob a lombar); no topo o corpo fica sustentado só pelos pés. No abdominal (crunch) a pelve e a lombar ficam no chão e só as escápulas sobem. Causa: dado — `y 1.0` fixo com t -90; motor — `ajuste_altura_dada` encosta só os pés (S2). Correção: remover `y` (deixar o motor apoiar) e declarar contatos de tronco (motor S2), ou `y 0.75`.
- [médio] Braços erguidos em "V" com dedos abertos acima da cabeça e depois estendidos para os joelhos (frente: mãos abertas para os lados); o padrão é mãos cruzadas no peito ou atrás da cabeça. Causa: dado `bf [150,152]` → `[118,120]`, `bfa 10`. Correção: mãos cruzadas no peito — q0 `bf [-95,-5], bt [-98,-8], bfa -10, afa -45`; q1/q2 somar a rotação do tronco (-32°): `bf [-127,-37], bt [-130,-40]`; conferir na tira de frente que as mãos ficam sobre os peitorais.

## 35. abdominal-infra — APROVADO
Evidência: `folhas/abdominal-infra.jpg`, `r_frente/abdominal-infra.jpg`, `r_perfil/abdominal-infra.jpg`.
- Pernas estendidas sobem até a vertical e descem até ~8° do chão sem tocar, lombar e mãos apoiadas. Nada a corrigir.

## 36. dead-bug — APROVADO (1 leve)
Evidência: `folhas/dead-bug.jpg`, `r_frente/dead-bug.jpg`, `r_perfil/dead-bug.jpg`.
- Braço e perna contralaterais estendem alternadamente, lombar no chão.
- [leve] O calcanhar da perna estendida e a mão estendida encostam no tapete (f22, f78); o padrão é parar 3–5 cm acima. Correção: perna estendida `[96,96,186]` → `[92,92,182]` e braço `264` → `258`.

## 37. mountain-climber — DEFEITOS (1 médio)
Evidência: `folhas/mountain-climber.jpg`, `r_perfil/mountain-climber.jpg` (`folhas/perfil_7.jpg`, linha 1).
- [médio] A perna que volta para trás dá um coice para cima: o joelho dobra ~80° e o pé sobe até a altura do quadril antes de pousar (f4–f6, f16–f19; perfil tira 1 e 6); o quadril também sobe ~8 cm a cada troca. No escalador a perna volta quase estendida, com o pé rente ao chão. Causa: dado q1/q3 `pf [-25,-105,-30]` (perna de trás) e `y 5.4` (vs 4.6). Correção: q1/q3 perna que recua `[-40,-60,0]`, perna que avança `[40,-70,10]`, `y 4.8`, `t 98`.

## 38. russian-twist — APROVADO (1 leve)
Evidência: `folhas/russian-twist.jpg`, `r_frente/russian-twist.jpg`, `r_perfil/russian-twist.jpg`.
- Tronco inclinado ~42° para trás, joelhos ~70°, rotação ±42° com cabeça acompanhando; calcanhares tocando o tapete (variação iniciante, válida).
- [leve] Mãos separadas com dedos abertos (frente); o padrão é mãos unidas (ou segurando uma bola). Correção: `bfa ±38.5` → `bfa 30/-30` com `afa` igual ao oposto para as mãos se tocarem à frente do umbigo, ou adicionar `bola em maos`.

## 39. abdominal-bicicleta — DEFEITOS (2 críticos)
Evidência: `folhas/abdominal-bicicleta.jpg`, `folhas/bic_z.jpg` (f1, f23), `r_frente/abdominal-bicicleta.jpg`, `r_perfil/abdominal-bicicleta.jpg`.
- [crítico] Corpo flutuando sobre o tapete com a pelve sem contato (sombra separada, f1–f43) e sustentado por um braço esticado que vai ao chão (`bic_z.jpg`). Causa: dado — sem `y` e `apoio []`, o motor apoia pelo ponto mais baixo (a mão/cotovelo do braço aberto); S2. Correção: braços corretos (abaixo) fazem a pelve virar o ponto mais baixo; motor S2.
- [crítico] Braços errados: na frente aparecem abertos como asas, mãos longe da cabeça (`r_frente` todas as tiras); no abdominal bicicleta as mãos ficam atrás da cabeça e o cotovelo vai ao joelho oposto. Causa: dado `bf [-155.1,-32.9], bfa 55` (braço para trás e antebraço para baixo/fora). Correção: `bf [-160,20], bt [-163,17], bfa 60, afa -60` (antebraço voltando para a nuca; conferir com `--tira` de frente que as mãos se encontram atrás da cabeça) e manter `tr ±40` com os cotovelos acompanhando.

## 40. elevacao-pernas-barra — DEFEITOS (2 críticos)
Evidência: `folhas/elevacao-pernas-barra.jpg`, `folhas/epb_z1.jpg`, `folhas/epb_z2.jpg`, `r_perfil/elevacao-pernas-barra.jpg` (`folhas/perfil_7.jpg`, linha 4), `r_frente/elevacao-pernas-barra.jpg`.
- [crítico] Mãos não seguram a barra: as mãos ficam acima da barra em garra aberta, a barra passa na altura do punho, sem os dedos envolverem (`epb_z1.jpg`). Causa: motor — `segurar_barra` posiciona `pegada()` na barra, mas o `off_peg`/`rot_pegada` resultam com a palma acima da barra (a pegada deve ficar com a barra no centro da mão fechada). Correção (motor): conferir `off_peg` (centro da pegada a 62% punho→dedo médio deixa a barra no meio dos dedos, não na palma) e fechar os dedos (`dedos=1`, curva "peg" maior: (80,95,70)) em volta da barra.
- [crítico] Pés tocam o chão na posição pendurada (perfil tira 0 e 7: pontas dos pés na base, `epb_z2.jpg` quase rente) — barra baixa demais para um homem pendurado de braços estendidos. Causa: dado `barra_fixa y 23.5`, quadril `y 13.1`. Correção: `barra_fixa y 25.5` e quadril `y 15.1` (pés ≥ 15 cm do chão).
- Câmera: a cabeça fica escondida entre os braços; `cam 40` mostra o rosto.

## 41. roda-abdominal — DEFEITOS (2 críticos)
Evidência: `folhas/roda-abdominal.jpg`, `r_frente/roda-abdominal.jpg` (`folhas/frente_7.jpg`, linha 5), `r_perfil/roda-abdominal.jpg`.
- [crítico] Implemento errado: é uma medicine ball laranja, não uma roda abdominal (roda com eixo e duas manoplas). Causa: dado — props `{"tipo":"bola","em":"maos"}`; motor — não existe acessório "roda". Correção (motor): novo acessório `roda` (disco Ø ~18 cm, largura 6 cm, eixo horizontal lateral com manoplas de 10 cm de cada lado) cujo centro fica sob as mãos, tocando o chão, e que gira conforme desloca (ângulo = deslocamento / raio); dado: `{"tipo":"roda","em":"maos"}`.
- [crítico] Mãos não seguram o implemento: a bola fica no chão entre as mãos (às vezes ao lado da mão da frente), com as mãos abertas apoiadas no chão ao lado dela (frente tiras 0–7; produção f1–f91). Causa: motor — `_bola` coloca a bola no ponto médio das pegadas sem IK das mãos sobre a superfície; as mãos estão separadas ~40 cm. Correção: com a roda, mãos fechadas nas manoplas (`rot_pegada` com eixo lateral, dedos=1), largura das mãos ~30 cm (`bfa/bta` 0) e a roda sempre tocando o chão (o 2D já leva as mãos ao chão: `x/y` corretos).

## 42. pallof — DEFEITOS (1 médio)
Evidência: `folhas/pallof.jpg`, `r_frente/pallof.jpg` (`folhas/frente_7.jpg`, linha 6), `r_perfil/pallof.jpg`.
- Técnica correta (confirmada de frente): polia lateral na altura do peito, pés afastados, mãos saem do peito e estendem à frente sem girar o tronco, sustentação de 2 s.
- [médio] Câmera enganosa: no vídeo (cam padrão 64) a torre aparece à frente do atleta e as mãos parecem empurrar o cabo em direção à polia (f22–f71), o que transmite a técnica errada (o cabo deveria ficar perpendicular ao braço). Correção: `"cam": 90` (de frente, torre ao lado, cabo perpendicular aos braços bem visível).

## 43. abdominal-polia — DEFEITOS (1 crítico, 1 médio)
Evidência: `folhas/abdominal-polia.jpg`, `folhas/pol_perfil_z.jpg`, `r_frente/abdominal-polia.jpg` (`folhas/frente_8.jpg`, linha 1).
- [crítico] Cabo saindo do nada: a torre está à frente do atleta, mas o cabo sai das mãos subindo para trás/para cima, para fora do quadro, sem passar por nenhuma polia (f1–f74; perfil `pol_perfil_z.jpg`). Causa: motor — `_polia` coloca a polia em `ate` (x 3.5, z 20) mas move a torre para `min(ys) - 2.6` (para não atravessar o corpo) sem mover a polia junto; o braço que liga a torre à polia só é desenhado se a distância for > 0,3 e fica fora do quadro; além disso o `x` de `ate` é relativo ao quadril 2D e, com o corpo 3D posicionado por `ref["quad"]`, acaba atrás da cabeça. Correção (motor): quando a torre é deslocada, deslocar também a polia para a coluna da torre (polia no topo da torre, no mesmo y) e conferir o sentido: polia alta à frente do ajoelhado, cabo descendo até as mãos atrás da cabeça. Dado: `ate [6.5, 18.5]` com o atleta a ~60 cm da torre.
- [médio] A cabeça fica a poucos cm da coluna da torre na flexão máxima (perfil tira 3; de frente a cabeça parece entrar no quadro de pesos). Causa: motor — a folga da torre usa `pesc` (pescoço) e não o topo da cabeça. Correção: incluir a cabeça (`pesc` + 1,7 unidade na direção da cabeça) em `ys` ou folga de 4,0.

## 44. canivete — APROVADO
Evidência: `folhas/canivete.jpg`, `r_frente/canivete.jpg`, `r_perfil/canivete.jpg`.
- Deitado com braços acima da cabeça, sobe tronco e pernas estendidas juntos e equilibra-se sobre os glúteos com as mãos nos pés; desce controlado. Nada a corrigir.

## 45. box-jump — DEFEITOS (1 leve)
Evidência: `folhas/box-jump.jpg`, `folhas/box_perfil_z.jpg`, `r_frente/box-jump.jpg`, `r_perfil/box-jump.jpg`.
- Contramovimento, salto, aterrissagem amortecida no topo da caixa, extensão completa e descida da caixa passo a passo: sequência correta; joelhos não atravessam a caixa (perfil).
- [leve] Começa colado à caixa: no contramovimento os joelhos ficam a ~5 cm da quina (perfil tira 1); no vídeo 3/4 parece que os joelhos entram na caixa (f7–f20). Correção: caixa `x` 3.1 → 4.0 (e ajustar q3/q4 `x` +0.9).

## 46. salto-distancia — DEFEITOS (1 médio)
Evidência: `folhas/salto-distancia.jpg`, `r_perfil/salto-distancia.jpg`, `r_frente/salto-distancia.jpg`.
- Salto horizontal com braços, voo e aterrissagem em agachamento corretos.
- [médio] A volta ao ponto de partida é feita andando de costas (f54–f115: o atleta olha para a frente e recua ~1 m em passos para trás) — padrão estranho, que ocupa metade do vídeo. Correção: ou cortar a volta (o vídeo termina na aterrissagem + estabilização e o laço reinicia com um corte), ou virar o corpo 180° e voltar andando de frente (`tr`/`rol` não servem; precisa de rotação de yaw do corpo, que o motor não tem — sugestão para o motor: campo `yaw` por quadro). Com o motor atual, a opção mais limpa é encurtar a volta para 2 passos curtos de costas com `tempos` 0.35.
- Distância do salto ~95 cm (x -2 → 7.38): curta para um adulto atlético (~1,8–2,2 m). Sugestão: q4 `x` 13 e q5 `x` 15 (ajustar a volta).

## 47. bound-lateral — APROVADO (1 leve)
Evidência: `folhas/bound-lateral.jpg`, `r_frente/bound-lateral.jpg`, `r_perfil/bound-lateral.jpg`.
- Impulso lateral numa perna, aterrissagem na outra com a perna livre cruzando atrás, braços contralaterais, alternância.
- [leve] No meio do voo as duas pernas ficam estendidas e paralelas sob o corpo ("boneco duro", f10–f16 e f35–f41). Correção: q1/q3 perna que impulsiona `[−10,−40,40]` (sai estendendo para o lado/atrás) e a que vai aterrissar `[25,−10,80]`.

## 48. salto-tesoura — APROVADO
Evidência: `folhas/salto-tesoura.jpg`, `folhas/tes_z.jpg`, `r_frente/salto-tesoura.jpg`, `r_perfil/salto-tesoura.jpg`.
- Afundo com troca de pernas no ar, braços contralaterais, joelho de trás perto do chão na aterrissagem. Nada a corrigir.

## 49. tuck-jump — APROVADO
Evidência: `folhas/tuck-jump.jpg`, `r_frente/tuck-jump.jpg`, `r_perfil/tuck-jump.jpg`.
- Contramovimento, extensão, joelhos ao peito no ápice (~42 cm de voo), aterrissagem amortecida. Nada a corrigir.

## 50. arremesso-rotacional — DEFEITOS (1 crítico, 1 médio)
Evidência: `folhas/arremesso-rotacional.jpg`, `folhas/arr_z.jpg` (f1, f26), `r_frente/arremesso-rotacional.jpg`, `r_perfil/arremesso-rotacional.jpg`.
- [crítico] A bola não está nas mãos: ela flutua no ponto médio entre as mãos, que ficam ~50 cm afastadas (uma mão ao lado da bola, a outra no peito ou atrás do quadril) — f1, f22–f32, `arr_z.jpg`. Causa: dado — `bfa +33/-33`, `-6/+6`, `-24/+24` com sinais opostos combinados ao `tr` afastam as mãos; motor — `_bola` só centraliza a bola entre as pegadas, sem IK das mãos à superfície da bola. Correção (motor): em `bola em maos`, IK das duas mãos até pontos opostos da bola (afastamento = diâmetro, ~25 cm) e dedos abertos sobre a superfície; dado: usar os mesmos ângulos nos dois braços com `tr` fazendo a rotação (ex.: q0 `bf [-40,40], bt [-43,37], bfa 10, bta -10`, `tr -55`; q2 `bf [60,90], bt [57,87], bfa 10, bta -10`, `tr 40`).
- [médio] Não há arremesso nem parede: a bola nunca sai das mãos e não há alvo; as dicas pedem "lateral à parede, arremessar e receber". Correção: adicionar parede (`_parede`) a ~2 m ao lado e soltar a bola no fim da rotação (o motor precisaria de bola livre com trajetória/retorno; alternativa simples: manter sem soltar e trocar o nome da fase para "rotação com medicine ball" — decisão de produto).
- Pés: o pé de trás deveria girar sobre a bola do pé (pivô) na rotação; hoje os dois pés ficam chapados. Leve: `pt[2]` 70 no fim da rotação com `apoio` mantido.

## 51. ponte-pescoco (bridge and roll / upa) — DEFEITOS (2 críticos)
Evidência: `folhas/ponte-pescoco.jpg`, `r_frente/ponte-pescoco.jpg` (`folhas/frente_9.jpg`, linha 3), `r_perfil/ponte-pescoco.jpg`.
- [crítico] Pernas soltas no ar: de frente, quando o corpo rola para o ombro, as duas pernas giram juntas com o tronco e sobem para o lado, um pé saindo do chão na altura do quadril (tiras 1–5); no upa os dois pés ficam plantados e só o quadril sobe e gira por cima do ombro. Causa: dado — `rol 32/40` gira o corpo inteiro (inclusive pernas) em torno do eixo frente-trás; motor — `rol` não preserva os apoios dos pés. Correção: usar `trp` (rotação da pelve) + `tr` em vez de `rol`, ou (motor) aplicar `rol` só da pelve para cima e manter os pés como apoio (IK) quando estiverem no chão no quadro anterior. Dado sugerido: q1/q2 `rol 0, trp 30, tr -25, inc 10`, pés com `apoio ["pe_f","pe_t"]`.
- [crítico] Corpo sem apoio na fase alta: no vídeo (f11–f30) só os pés tocam o tapete — ombro/cabeça ficam acima do chão (sombra separada); a ponte deve apoiar-se no ombro/trapézio do lado para o qual rola. Causa: dado `y 3.1` + S2. Correção: q1/q2 `y` 2.6 e motor S2 (contato de ombro/cabeça).
- [leve] Posição de repouso com quadril/costas 2–3 cm acima do tapete (f1), S2.

## 52. fuga-quadril (shrimp) — DEFEITOS (2 críticos)
Evidência: `folhas/fuga-quadril.jpg`, `r_frente/fuga-quadril.jpg` (`folhas/frente_9.jpg`, linha 4), `r_perfil/fuga-quadril.jpg`.
- [crítico] Movimento inexistente: o atleta rola de um lado para o outro no lugar, com as pernas girando junto e ficando no ar (frente tiras 1–3 e 5–7: pernas cruzadas suspensas), sem empurrar o chão e sem deslocar o quadril para trás. No shrimp: deitado de lado, o pé de cima empurra o chão, o quadril vai para trás (o corpo forma um "C") e o atleta se desloca pelo tatame. Causa: dado — `rol ±80` gira o corpo inteiro (pernas também) e não há deslocamento (`x`/`z`); motor — `rol` não mantém o pé de apoio. Correção: q1/q3 `rol ±80` com a perna de baixo estendida no chão e a de cima com o pé plantado (`apoio` do pé de cima) e `x` -1.5 a cada fuga (quadril recua); com `rolar` não serve (deslocamento lateral do corpo deitado) — sugerir deslocamento real em `x` e loop com corte, ou alternar lados voltando ao centro.
- [crítico] Corpo flutuando nas fases de barriga para cima (f1, f23–f36: quadril e costas sem contato, sombra separada). Causa: S2. Correção: motor S2; dado q0/q2 `y` 1.0.
- Câmera `cam 30` deixa o deslocamento invisível; usar `cam 0` com o corpo atravessando a tela.

## 53. nordico — APROVADO
Evidência: `folhas/nordico.jpg`, `r_frente/nordico.jpg`, `r_perfil/nordico.jpg`.
- Ajoelhado com rolo nos tornozelos, descida excêntrica com quadril estendido (joelho-quadril-ombro alinhados), mãos amortecem perto do chão, volta. Nada a corrigir (a volta concêntrica sem empurrão é a variante avançada, válida).

## 54. educativos-corrida (skipping) — DEFEITOS (1 crítico)
Evidência: `folhas/educativos-corrida.jpg`, `folhas/edu_z.jpg`, `r_perfil/educativos-corrida.jpg`.
- [crítico] Pé de apoio na ponta dos dedos, quase vertical (en pointe), sem a dobra dos dedos e com o calcanhar muito alto (f1, f9, f13; `edu_z.jpg`) — anatomicamente impossível como apoio. No skipping o contato é com o antepé, calcanhar levemente elevado (pé ~20–30° com o chão) e dedos estendidos no chão. Causa: dado `pt[2]=45/50/55` no apoio + S1. Correção: pé de apoio `[−6,−10,70]` / `[12,−6,72]` e S1.
- Coordenação braço-perna e joelho alto corretos.

## 55. bike-subida — DEFEITOS (2 críticos)
Evidência: `folhas/bike-subida.jpg`, `folhas/bike_z.jpg` (f1, f7, f13, f19), `folhas/bike_perfil_z.jpg`, `r_frente/bike-subida.jpg`.
- [crítico] Pés fora dos pedais: em boa parte do ciclo o pé pousa no tubo da base ou atrás/abaixo do pedivela, longe do pedal (f7: pé da frente na base; f19: pé atrás do movimento central; perfil tira 2: pé no tubo traseiro), enquanto o pedal gira sozinho. Causa: dado — os ângulos de coxa/canela dos 6 quadros não descrevem o círculo do pedal (raio 1,75) em torno de `eixo [2.5,2.7]` com o quadril em `x 1.7, y 10.4`; motor — `_bike`/`extras["pedais"]` desenha o pedal no pé, mas sem IK o pé não segue o círculo (na bike sentada o motor faz IK; na "em_pe" não). Correção (motor): para `bike` com `em_pe`, calcular a posição do pedal por ângulo de pedivela (6 quadros = 60° cada) e fazer IK de cada pé até o pedal (pé paralelo ao pedal, `pe` ≈ 80–100), com a pelve sobre o movimento central; dado: só tronco/braços e `x/y` do quadril.
- [crítico] Mãos não seguram o guidão: as mãos ficam abertas, pairando acima das manoplas (f1, `bike_z.jpg`). Causa: motor — sem IK de pegada no guidão. Correção: IK das mãos até as manoplas (`guidao`) com `rot_pegada` (eixo da manopla) e dedos=1.

## 56. sentar-levantar — APROVADO
Evidência: `folhas/sentar-levantar.jpg`, `folhas/sl_perfil_z.jpg`, `r_frente/sentar-levantar.jpg`, `r_perfil/sentar-levantar.jpg`.
- Desce controlado até sentar na borda do banco (glúteo toca o assento no quadro sentado, perfil), inclina o tronco à frente e levanta sem usar as mãos, braços à frente como contrapeso. Nada a corrigir.

