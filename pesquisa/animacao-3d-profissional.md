# Animação 3D profissional dos exercícios do Forja: pesquisa, diagnóstico e plano

Autor: agente PESQUISADOR. Destinatário: agente ANIMADOR.
Escopo: as 175 demonstrações em `app/src/main/assets/video3d/*.mp4`, geradas por `tools/anim3d/{humano,movimento,aparelhos,anatomia}.py` a partir de `tools/anim/dados/lote{1,2,3}.json`.

Como a auditoria foi feita:
- Revisei os **vídeos de produção** (720 px, 24 fps). Extraí os quadros com ffmpeg e montei folhas de contato com PIL.
- Ao todo, **60 exercícios** de todas as famílias foram revistos visualmente.
- Rodei duas métricas automáticas sobre os **175** vídeos:
  - energia de movimento quadro a quadro, que detecta "pops" (saltos de 1 quadro), congelamentos e emendas de loop;
  - bitrate de cada vídeo.
- Li o código do motor inteiro.
- Os scripts estão no scratchpad: `/tmp/claude-0/-home-user-teste-3/400edce2-80ea-57f6-97f9-c6ff24db5c18/scratchpad/pesq/frames.py` (folhas de contato) e `/tmp/claude-0/-home-user-teste-3/400edce2-80ea-57f6-97f9-c6ff24db5c18/scratchpad/pesq/energia.py` (métricas; o resultado fica em `energia.json`). A lista de pops está em `pops.txt`, na mesma pasta.

---

## A) Princípios e referências

### A1. Como os estúdios fazem
- **Bibliotecas comerciais de exercícios 3D** (pacotes de "gym animations" no Fab/Unreal, Envato, Gymvisual, Muscle&Motion) partem de **captura de movimento de pessoas reais** e depois fazem **limpeza manual** quadro a quadro:
  - travar os pés;
  - corrigir as mãos no implemento;
  - ajustar os arcos.
- O formato é sempre o mesmo:
  - câmera fixa e fundo neutro;
  - modelo cinza com os músculos-alvo destacados;
  - loops curtos e quadrados (1:1), feitos para app.
- Apps de vídeo real (Nike Training Club, Apple Fitness+, Fitbod, Freeletics) seguem as mesmas regras de leitura:
  - um único ângulo que mostra o plano do movimento;
  - o atleta ocupa 70–85 % da altura do quadro;
  - rosto e mãos sempre visíveis;
  - cadência real, com respiração e micro-ajustes visíveis nas isometrias.
- Sem mocap, o caminho profissional é **pose-to-pose com curvas de velocidade autorais**, não interpolação automática:
  - easing assimétrico;
  - overlap entre segmentos;
  - "camada de vida" (respiração e ruído), aplicada por cima.

### A2. Os 12 princípios aplicados a movimento humano realista
Fonte: Thomas & Johnston, *The Illusion of Life* (1981).

| Princípio | Como se aplica aqui |
|---|---|
| Timing | Durações reais por fase: excêntrica 2–3 s, concêntrica 1–1,5 s, pausas de 0,2–0,5 s, cardio no ritmo real (corrida ≈ 170–180 passos/min). |
| Slow in / slow out | O corpo acelera e desacelera, **mas de forma assimétrica**. A concêntrica acelera rápido e freia longo perto do topo. A excêntrica freia no fundo e tem um pequeno rebote (ciclo alongamento-encurtamento). Parar por completo em toda pose-chave é exatamente o "andar de robô". |
| Antecipação | Contramovimento antes de saltos, arremessos, swing e socos: o quadril desce e o braço recua, 0,1–0,25 s. |
| Arcos | Mãos, pés e implementos descrevem arcos limpos. Exemplos: elevação lateral num plano, kettlebell em pêndulo, barra do supino num leve "J". Interpolar ângulos de Euler independentes cria trajetórias tortas. |
| Follow-through / overlap | Partes distais chegam depois das proximais (cabeça, mãos, implementos 40–120 ms atrás). Kettlebell, corda, saco e elástico continuam a se mover. |
| Ação secundária | Respiração (2,5–4 s por ciclo), ajuste de pegada, olhar acompanhando o implemento. |
| Peso | Centro de massa (CM) sobre a base de apoio. Carga pesada = movimento mais lento e quadril compensando. Aterrissagens com amortecimento: joelho 30–60°, 0,15–0,25 s. |
| Staging | Câmera escolhida para o plano do movimento. Nada cobre o rosto ou as mãos. |
| Pose-to-pose | Poses-chave mais **breakdowns** (poses intermediárias), sempre que a interpolação direta passar por posições impossíveis. |
| Exagero | Mínimo (é demonstração técnica). No máximo, aumentar um pouco a amplitude dos micro-movimentos de vida para que sejam legíveis no celular. |
| Desenho sólido / apelo | Silhueta clara: os membros não ficam sobrepostos ao tronco na vista escolhida. |

### A3. Biomecânica de referência por família
Valores usados no plano (seção C3). Fontes: NSCA *Essentials*, guias NASM/NFPT de RDL e literatura de ritmo escápulo-umeral.

- **Ritmo escápulo-umeral**:
  - a relação clássica é **2:1** (úmero:escápula) acima de cerca de 30° de elevação, depois da fase de "setting";
  - medido por plano: 2,0 : 1 na abdução, 1,6 : 1 no plano escapular (scaption) e 1,1 : 1 na flexão;
  - aos 90° de abdução: cerca de 60° glenoumerais + 30° de rotação superior da escápula;
  - consequência para o motor: a clavícula e a escápula precisam subir de forma progressiva a partir de ~30° de elevação, não só depois de 75°.
- **Hinge (stiff/RDL/terra)**:
  - o quadril vai **para trás** e a coluna fica neutra;
  - a barra "raspa" coxas e canelas e fica **sobre o meio do pé** durante todo o movimento;
  - no RDL, o fundo fica entre o joelho e o meio da canela.

### A4. Fontes
- Twelve basic principles of animation (Thomas & Johnston): https://en.wikipedia.org/wiki/Twelve_basic_principles_of_animation ; https://www.studiobinder.com/blog/what-are-the-12-principles-of-animation/
- Muscle&Motion, "3D Animation in Fitness": https://www.muscleandmotion.com/?p=15194
- Pacote comercial de animações de academia (mocap + retoque manual): https://www.fab.com/listings/01ed03b7-121b-4e67-8121-406d7a685588
- Especificação típica de animação de exercício (fundo neutro, câmera fixa, destaque muscular, 1:1): https://www.freelancer.com/projects/blender/realistic-exercise-animations ; https://www.upwork.com/services/product/video-audio-premium-3d-workout-and-exercise-animations-with-anatomy-highlights-2011080495145043325
- Footskate cleanup (Kovar et al.): "aplicar IK em cada quadro de forma independente cria descontinuidades quando as restrições ligam e desligam": https://research.cs.wisc.edu/graphics/Gallery/kovar.vol/Cleanup
- Avaliação perceptual de footskate (Prażák, Hoyet, O'Sullivan, SCA 2011): https://diglib.eg.org/handle/10.2312/SCA.SCA11.287-294
- Unreal, travar os pés por velocidade (IK Retargeter): https://dev.epicgames.com/documentation/unreal-engine/fix-foot-sliding-with-ik-retargeter-in-unreal-engine
- Ritmo escápulo-umeral: https://pmc.ncbi.nlm.nih.gov/articles/PMC2841046 ; https://drmillett.com/wp-content/uploads/2017/03/effect-plane-arm-elevation-glenohumeral-kinematics.pdf
- RDL (barra no meio do pé, raspando as pernas, quadril para trás): https://blog.nasm.org/romanian-deadlift-basics ; https://nfpt.com/blog/how-to-do-a-romanian-deadlift
- Encode web e mobile (CRF, yuv420p, faststart): https://trac.ffmpeg.org/wiki/Encode/YouTube ; https://damieng.com/blog/2025/html5-video-cheatsheet/ ; https://transloadit.com/devtips/reducing-video-file-size-with-ffmpeg-for-web-optimization/

---

## B) Diagnóstico

### B1. Números da auditoria automática (175 vídeos)
- **Pops** (um quadro com mudança mais de 2,2× maior que os vizinhos): **17 exercícios**, 28 ocorrências (lista em `pops.txt`). Os piores:
  - spider: 4 pops de ~8 unidades;
  - turkish-getup;
  - supino-inclinado-barra;
  - triceps-testa;
  - panturrilha-pe (4);
  - rosca-scott (2);
  - power-clean, rosca-direta, elevacao-pernas-barra, alongamento-antebraco, box-jump, remada-unilateral, stiff, desenvolvimento-barra, postura-crianca, roda-abdominal, bike-subida.
- **Emenda do loop com salto**:
  - salto-distancia: o corpo **desliza 1 m para trás em 0,2 s**;
  - elevacao-pernas-barra: diferença na emenda 9,6× maior que nos vizinhos;
  - alongamento-antebraco: 6,4×;
  - rolo-it, rolo-quadriceps, prancha-lateral, gato-camelo, alongamento-gluteo: entre 3,7× e 5×.
- **Congelamento total** (sequências de quadros sem nenhum movimento):
  - **25 vídeos ficam parados ≥ 1 s** e 38 ficam parados ≥ 0,5 s;
  - casos extremos: prancha 85 de 86 quadros, alongamento-pescoco 71, isometria-pescoco 71, alongamento-peito 70, alongamento-dorsal, torcao-coluna, alongamento-triceps, postura-crianca, alongamento-adutores, superman, pallof (50), ponte-gluteo (30).
  - Esse é o principal motivo de "parece boneco": em uma pessoa real nunca há dois quadros idênticos.
- **Bitrate**: mediana de 575 kbps (de 269 a 1544 kbps; o máximo é "tiros"). Peso médio de 215 KB por vídeo, 40 MB no total.
  - O pontilhado aleatório que `compor()` aplica a cada quadro gera ruído temporal no fundo. Ele aparece como "movimento" de cerca de 0,06 nos quadros parados e gasta bits à toa.

### B2. Falhas sistêmicas do motor (causa no código)

**S1. Parada morta em toda pose-chave; velocidade simétrica.**
- Onde: `movimento.Trilha._tangentes`.
- Com `inversao = d0*d1 <= 0`, qualquer chave vizinha de uma chave igual (as "pausas" com 2 quadros idênticos) ou de uma inversão fica com tangente 0.
- Como quase todos os dados usam o padrão A → B → B(pausa) → A, **cada chave é uma parada total** com ease in/out simétrico (uma curva cúbica de Hermite com tangentes nulas equivale a um smoothstep).
- Resultado: movimento "pose-a-pose" robótico. Falta a concêntrica rápida e a excêntrica controlada com desaceleração longa, e a pausa é 100 % estática.

**S2. Trajetórias tortas por interpolar "ângulo sagital + abdução" como canais independentes.**
- Onde: `d2()` + `Trilha`.
- Exemplo medido, elevação lateral (bf 0→88, bfa 6→68). A componente frontal da direção do braço vale 0 → 0,35 → **0,56** → 0,56 → 0,37: o braço vai para a frente e depois "abre". Não é o arco plano do plano escapular.
- O mesmo acontece em crucifixo, peck-deck, face-pull, desenvolvimento, polichinelo e círculos.
- Os profissionais interpolam a **direção do segmento por slerp**, ou seja, um arco de círculo máximo.

**S3. Sem overlap nem follow-through.**
- Onde: `TrilhasPose` usa o mesmo relógio para todos os canais.
- Cabeça, mãos, antebraço e tronco começam e param juntos.
- Implementos são rígidos: kettlebell grudado na mão sem pêndulo, saco de pancada que não balança, corda e elástico sem inércia.

**S4. Correções binárias por quadro causam pops.** Este é o achado mais grave para a percepção de qualidade. Limiares do tipo liga/desliga:
- `corrigir_barra`:
  - com `rel.length < 3.2 and rel.dot(up_t) > -2.4`, a barra é **teletransportada** para a posição "nas costas" ou "no rack frontal";
  - é a causa dos pops em triceps-testa (a barra pula da testa para a nuca), supino-inclinado-barra (a barra fica atrás do pescoço no fundo e salta para os braços estendidos em 1 quadro), rosca-direta, rosca-scott, power-clean e desenvolvimento-barra;
  - no supino inclinado, o fundo do movimento mostra a barra **atrás da cabeça**.
- `corrigir_barra`, "não atravessar o corpo": empurra a barra para fora quando ela fica a menos de 0,42 da pele. No stiff, isso a afasta das coxas, e a barra acaba à frente dos pés (veja S8).
- `dedos_pes`: altura > 0,35 → os dedos "viram" de repente (seam do alongamento-antebraco, panturrilha-pe).
- `apoios_2d`: mão a menos de 0,45 da superfície vira apoio. `efetores_chave`: contato < 0,3.
- `plantar`:
  - quando as duas chaves têm contato mas o pé mudou ≥ 1,6 de lugar (sem `passos`), cai no ramo `elif a["contato"]`;
  - nesse ramo o peso vai a 0 no fim do trecho, e no início do trecho seguinte salta para 1 → **pop do pé/mão** (spider, turkish-getup, remada-unilateral).
- `finalizar`: a regra `livre` (realinhar ao chão só quando `not fixos`) liga e desliga conforme o conjunto de apoios, e o corpo dá um "degrau" vertical.
- É exatamente o que Kovar et al. descrevem: IK independente por quadro com restrições que ligam e desligam gera descontinuidade.

**S5. Detecção automática de apoio erra.**
- Onde: `apoios_2d`.
- No **abdominal**, as mãos atrás da cabeça ficam perto do tapete no quadro 0, são classificadas como "apoio" e ficam presas ao chão por IK. Resultado: braços esticados para trás no início e um movimento estranho.
- Pode acontecer em qualquer exercício deitado ou sentado.

**S6. Correções só nas chaves.**
- `encaixar`, `repousar`, `maos_na_borda` e `segurar_barra` (este parcialmente) rodam em `colocar_chave`.
- `quadro()` refaz a pose do zero com `posar()` e só recupera os contatos por `plantar`.
- Entre as chaves, costas × banco, mão × borda e pé × degrau podem flutuar ou penetrar. Isso aparece na panturrilha-pe (pops no degrau) e no búlgaro.

**S7. Locomoção sem deslocamento real = "moonwalk".**
- Exercícios afetados: farmer-walk, bear-crawl, carioca, passada-andando, educativos e sled-push.
- Todos são feitos no lugar, sem esteira: os pés apoiados precisam deslizar para trás, o que é foot-skating.
- O salto-distancia avança e **volta deslizando** em 0,2 s.
- O chão é só um "shadow catcher", sem nenhuma referência visual. O deslocamento lateral (monster-walk, carioca, bound-lateral) fica quase invisível.

**S8. Sem equilíbrio nem centro de massa.**
- `colocar_chave` ancora só `foot.L` em y.
- Nada garante que o CM (corpo + carga) fique sobre a base de apoio.
- Exemplo, stiff: o tronco desce, mas o quadril não recua o suficiente no corpo 3D (as proporções 2D ≠ 3D). A barra termina **à frente dos pés**, com os braços inclinados para a frente. O certo é a barra sobre o meio do pé, raspando as pernas.

**S9. Coluna sem canal de flexão/extensão.**
- A curvatura só sai de `t` e da flexão do quadril (ritmo lombopélvico automático).
- Por isso o **gato-camelo** varia só 7° de tronco: o movimento principal (arredondar e arquear a coluna) não aparece.
- Também faltam: inclinação pélvica controlável (ponte, hip thrust, prancha com retroversão), "peito aberto" e "costas arredondadas".

**S10. Escápula simplificada.**
- Elevação da clavícula só acima de 75° de elevação do braço (`(elev-75)/105*20`).
- Não há protração ao fim dos empurrões (serrátil no supino e na flexão "plus") nem depressão na puxada.
- A retração depende só da componente frontal do braço.
- Deveria seguir o ritmo 2:1 e ter os canais "protração" e "depressão".

**S11. Isometrias sem vida.**
- Duas chaves idênticas, ou quase, viram imagem congelada (veja B1).
- Não há respiração, micro-oscilação de peso nem tremor de esforço.

**S12. Saltos não balísticos.**
- `ay` é interpolado por spline. A fase de voo não é uma parábola (gravidade constante), então o tempo de voo e a altura não batem com a física. Isso aparece em tuck-jump, box-jump, agachamento-salto, polichinelo e burpee.

**S13. Amostragem não uniforme.**
- `TrilhasPose.instantes` arredonda cada trecho para um número inteiro de quadros.
- Trechos de 0,1–0,15 s (corrida, polichinelo, sombra) mudam até ±20 % de duração, e o passo de tempo entre quadros varia de trecho para trecho. Resultado: micro-engasgos no cardio.

**S14. Câmera e enquadramento.**
- Elevação fixa de 10°, câmera ortográfica e um único azimute por animação.
- `enquadrar` inclui **todos os aparelhos** no quadro:
  - a torre de polia (20 unidades de altura) encolhe o atleta para ~55 % da altura em face-pull, triceps-polia, puxada-frente e pallof;
  - nos exercícios no chão (prancha, flexão, abdominal) o corpo ocupa uma faixa estreita, com ~60 % do quadro vazio em cima.
- Não há regra que impeça mão ou implemento sobre o rosto: face-pull, supino-reto e supino-inclinado com a barra cruzando a cabeça.

**S15. Render e encode.**
- Sem motion blur. O rig é posado por `matrix_basis` sem keyframes, então o Cycles não tem vetor de movimento.
- 24 fps em movimentos rápidos (corrida, polichinelo, sombra, corda, battle rope) dá cerca de 9 quadros por passo e parece "picotado".
- Pontilhado aleatório a cada quadro (`rng` em `compor`) cria ruído temporal no fundo e custa bitrate.
- `-tune film` em vez de `-tune animation`, que serve melhor a CG limpo com áreas planas.
- O resto está bom: CRF 18, High@4.0, yuv420p, faststart, GOP igual ao loop, sem áudio.

**S16. Alavancas de máquina não rígidas.**
- `_alavancas_peito` e `_bracos_maquina` desenham cilindros da mão até um pivô fixo, e **o comprimento muda a cada quadro**.
- No supino-maquina, o pivô fica baixo, atrás do encosto, na altura do quadril, a ±3,7. A haste diagonal mão→pivô passa na frente do peito, do braço e da coxa na vista 3/4.
- Uma máquina real tem alavanca de comprimento fixo, girando em torno de um eixo, por fora da largura dos ombros.

**S17. Transições complexas sem breakdowns.**
- turkish-getup (quadro ~56 com o corpo "flutuando" sobre um pé), burpee, inchworm e spider.
- A interpolação em espaço de juntas passa por poses sem apoio físico.

### B3. Exercício por exercício
"Dados" significa problema no JSON; "Motor" significa problema no código.

| Exercício | O que está errado | Causa provável |
|---|---|---|
| **monster-walk** | De frente, as duas pernas abrem e fecham juntas (pfa 10→28 nas duas), como um polichinelo sem salto. A base chega a ~56° entre as pernas (exagerada). Vai 2 passos para a direita e volta. Sem referência no chão, o deslocamento lateral não é percebido. Mãos juntas na frente da cintura sem função. | Dados: abdução simultânea, sem pé de apoio. Motor: chão sem textura; câmera frontal com elevação de 10°. |
| **face-pull** | No fim, as mãos ficam **na frente do rosto**. A torre ocupa metade do quadro e o atleta fica pequeno. | Dados: `afa`/`ata` = −10 (antebraço para dentro) com o braço em 84° → mãos na linha média. Câmera 40 (3/4 frontal). Motor: `enquadrar` inclui a torre inteira. |
| **supino-maquina** | A haste da alavanca atravessa o tronco e a coxa na diagonal; o comprimento da alavanca varia. | Motor: `_alavancas_peito` (pivô em `zs+0.2`, atrás e embaixo; cilindro mão→pivô). |
| supino-inclinado-barra | No fundo, a barra fica atrás do pescoço; no quadro 42 pula para os braços estendidos. | Motor: limiar de `corrigir_barra` (S4). |
| triceps-testa | A barra salta da testa para a nuca (quadros 32 e 48). | Motor: o mesmo (S4). |
| rosca-direta, rosca-scott | No topo, a barra salta para a frente do rosto. | Motor: o mesmo (S4). |
| power-clean, desenvolvimento-barra | Salto da barra na entrada e na saída do rack. | Motor: o mesmo (S4); deve ser uma transição contínua. |
| stiff | A barra termina à frente dos pés, longe das pernas; os braços inclinam. | Motor: sem CM (S8) e "não atravessar" empurrando a barra. Dados: `x` −3,46 é pouco para o corpo 3D. |
| terra | Bom no geral. No início, a barra fica um pouco à frente das canelas; o tronco sobe antes do quadril no 2º quadro. | Dados mais S8. |
| crucifixo | No fundo, a abdução de 100° deixa os halteres abaixo do plano do banco (amplitude excessiva). Trajetória torta (S2). | Dados: bfa 100 → usar 80–85. Motor: S2. |
| peck-deck | Os braços abrem até 180° (atrás da linha dos ombros). | Dados: limitar ao alinhamento com o tronco, mais 10–15°. |
| elevacao-lateral | O braço passa à frente e depois abre. Corpo 100 % rígido. | Motor: S2 e S11. |
| abdominal | No início, os braços ficam esticados para trás, presos ao tapete. | Motor: S5. |
| gato-camelo | Mal se vê a mudança da coluna. Câmera 3/4 frontal. | Motor: S9. Dados: usar a câmera de perfil (cam 0). |
| prancha, prancha-lateral, pallof, alongamentos | Imagem congelada por 2–3 s. | Motor: S11. |
| salto-distancia | Depois de aterrissar, volta deslizando 1 m em 0,2 s. | Dados e motor: S7 e emenda do loop. |
| farmer-walk, bear-crawl, carioca, passada-andando | Andam no lugar com o pé apoiado deslizando; carioca em "T" rígido, sem rotação de quadril e ombro. | Motor: S7. Dados: falta contra-rotação (`tr` do tronco oposto à pelve). |
| polichinelo | Salto quase invisível (`ay` 0,6 = 6 cm só nas chaves intermediárias); os pés deslizam em `fixo: pes`. | Dados e motor: S12. |
| corrida-leve e cardio | 24 fps sem motion blur; tronco rígido; cabeça sem estabilização. | Motor: S13, S15 e S3. |
| sombra, saco-combinacoes | Base estreita, quase paralela, joelhos estendidos. Soco sem rotação de quadril (o `tr` gira só o tronco) e sem retorno rápido à guarda. Saco que não reage. | Dados: S3 (sequência proximal→distal). Motor: saco rígido. |
| swing | Aceitável. O kettlebell não faz pêndulo; falta o "snap" do quadril (o topo chega devagar). | Motor: S1 e S3. |
| turkish-getup | Pop no quadro 68; pose flutuante no quadro ~56. | Motor: S4. Dados: S17. |
| spider | 4 pops grandes (mãos e corpo saltam). | Motor: `plantar`, ramo contato→contato com dist ≥ 1,6 (S4). |
| panturrilha-pe | 4 pops no degrau. | Motor: S4 e S6 (degrau, dedos). |
| elevacao-pernas-barra | Salto na emenda; os pés quase tocam a base da barra. | Motor: S4. Dados: barra fixa baixa demais para as pernas estendidas. |
| box-jump | Giro brusco do corpo sobre a caixa (quadro 41). | Motor: nivelamento de "dois apoios" em `colocar_chave` só nas chaves, mais S4. |
| flexao, flexao-*, prancha | O corpo ocupa uma faixa estreita do quadro; mãos um pouco à frente dos ombros. | Motor: S14. Dados: mãos sob os ombros. |
| puxada-frente | Barra fina quase invisível, vista por trás; o puxador passa na frente do rosto. | Câmera (cam 40) e espessura do puxador. |
| russian-twist, dead-bug, remada-curvada, remada-baixa, desenvolvimento-halteres, leg-press, cadeira-extensora, afundo, búlgaro, burpee, tuck-jump | Corretos no essencial. Sofrem de S1 (paradas), S3 (sem overlap) e S11 (rigidez). | Motor. |

---

## C) Plano de correção (priorizado)

### Prioridade 0: eliminar pops e erros grosseiros (1–2 dias)

**C0.1 `corrigir_barra` (humano.py): trocar o limiar binário por um modo declarado mais uma mistura suave.**
- Novo campo opcional por animação: `"barra_modo": "maos" | "costas" | "rack"`. Padrão: `"maos"`.
- Inferência automática só para ids conhecidos: agachamento-barra → costas; agachamento-frontal → rack; o resto → mãos.
- Supino, triceps-testa e roscas devem **sempre** usar "maos".
- Para movimentos que entram e saem do rack (power-clean, desenvolvimento-barra), usar o peso `w = smoothstep(d0, d1, dist(barra_maos, ponto_rack))` e misturar `centro = lerp(centro_maos, centro_rack, w)`. Nunca trocar de um quadro para o outro.
- "Não atravessar": empurrar só na direção da normal local, também com peso suave. Para hinge, permitir contato com as coxas: folga de 0,12 em vez de 0,42 quando a barra está abaixo do quadril.

**C0.2 `plantar` (humano.py), caso "contato → contato com dist ≥ 1,6 sem passos".**
- Tratar como passo automático: arco baixo, com o pé descolando em `u ∈ [0,0.35]` e pousando em `u ∈ [0.65,1]`.
- Regra geral: `w(u=1)` do trecho i tem que ser igual a `w(u=0)` do trecho i+1 para todo efetor. Escrever um teste unitário disso.

**C0.3 Remover todos os limiares duros por quadro.**
- `dedos_pes`: usar `w = 1 - smoothstep(0.2, 0.5, altura)` e girar o dedo por `slerp(atual, chão, w)`.
- `finalizar/livre`: realinhar ao chão sempre com peso contínuo `w_livre = Π(1 - w_fixo_i)`, sem `if`.
- `sem_atravessar`: correção suave quando o gap fica entre −1,5 e 0,05, com `alvo = gap * smoothstep`.

**C0.4 Apoios explícitos.**
- Novo campo por quadro: `"apoio": ["pe_f","pe_t","mao_f",...]`. Quando presente, substitui `apoios_2d` e `efetores_chave`.
- Preencher nos exercícios deitados e sentados: abdominal, abdominal-infra, canivete, dead-bug, crucifixo, triceps-testa e russian-twist. No abdominal, as mãos **não** são apoio.

**C0.5 Correções em todo quadro, não só nas chaves.**
- Chamar `repousar`, `maos_na_borda` e o encaixe de pé em superfície (degrau, banco) também em `quadro()`/`finalizar()`.
- Usar pesos interpolados das chaves vizinhas (`w = lerp(w_a, w_b, smoothstep(u))`).

**C0.6 Três casos conhecidos (dados e aparelhos).**
- **face-pull** (pose final):
  - `bf: [90, 180]`, `bfa: 92` (um pouco atrás do plano frontal);
  - `afa: +15`, para as mãos ficarem ~12 cm por fora das orelhas, na altura das orelhas;
  - tronco ereto (`t: 180`, sem 182) e `oe: 0`;
  - no meio, uma chave de breakdown com `bfa 60`, `bf [95,150]`;
  - câmera: `cam: -35` (3/4 posterior, mostra o deltoide posterior e o trapézio, sem rosto coberto) com elevação de 15°;
  - recortar a torre (ver C2.2).
- **monster-walk**:
  - 8 chaves (2 passos para a direita, 2 para a esquerda, espelhados), 0,45–0,55 s por meio passo;
  - meio agachamento: joelho 35–45°, quadril 35–40°, `t` 155–160;
  - base parada em `pfa 9`. No passo, só a perna-guia abre até `pfa 18` com `ay` do pé de 0,3–0,5 (pé 3–5 cm acima do chão), enquanto a outra fica **plantada**;
  - em seguida, o quadril (`z`) se desloca sobre a perna-guia (atraso de 0,1 s em relação ao pé) e a perna de trás vem até `pfa 9`;
  - o elástico nunca relaxa por completo;
  - mãos na cintura ou à frente do peito em guarda;
  - câmera `cam: 70` (3/4 quase frontal) com elevação de 18°, mais as marcas no chão (C2.3).
- **supino-maquina** (aparelhos.py, `_alavancas_peito`):
  - alavanca **rígida**: pivô acima e atrás do ombro, `piv = (±(ombro_x + 1.3), y_encosto + 0.8, z_ombro + 2.6)`;
  - a haste de comprimento fixo L vai do pivô até um ponto ao lado da pegada, `g + X*sx*1.0`, e uma travessa curta e horizontal liga esse ponto ao pegador vertical;
  - a pose da mão vem do ângulo da alavanca: girar em torno do eixo do pivô e levar a mão por IK até o pegador, não o contrário;
  - garantia de projeto: |x da haste| ≥ ombro_x + 0,8 em toda a trajetória;
  - o mesmo princípio vale para o peck-deck, o desenvolvimento-maquina e as alavancas genéricas (`_bracos_maquina`): o comprimento é constante.

**C0.7 Emenda dos exercícios com deslocamento.**
- salto-distancia: saltar, aterrissar (amortecimento de 0,25 s), recuperar e **voltar caminhando de costas em 3 passos** com `passos: true` (≈ 1,2 s).
- Alternativa: renderizar com deslocamento e aplicar um crossfade de 6 quadros na emenda (ffmpeg `xfade` ou mistura no `compor`). A volta deslizando não pode ficar.

### Prioridade 1: curvas de movimento profissionais (motor, 2–3 dias)

**C1.1 Easing autoral por trecho (movimento.py).**
- Novo campo opcional `"ease"` por trecho, com o mesmo comprimento de `tempos`. Valores:
  - `"exc"` (excêntrica: entra moderada e freia longo);
  - `"con"` (concêntrica: acelera rápido, pico em ~35 % do trecho, freia nos 30 % finais);
  - `"io"` (smoothstep);
  - `"lin"` (cardio cíclico);
  - `"bal"` (balístico, ver C1.5);
  - `"pausa"`.
- Implementação: a Trilha continua sendo uma spline. O tempo dentro do trecho é remapeado, `u' = E(u)`, com E monotônica. Sugestões:
  - con: `E(u) = 1-(1-u)^2.2` misturada a smoothstep (α = 0,5);
  - exc: `E(u) = u^1.6` misturada a smoothstep (α = 0,6);
  - pausa: `E(u) = u` sobre valores quase iguais, com a camada de vida (C1.4).
- Padrão quando `ease` está ausente:
  - se a chave seguinte for "mais carregada" (fundo do agachamento, peito no supino), o trecho é exc;
  - se for a volta, con;
  - cardio com tempos iguais: lin.

**C1.2 Tangentes sem parada morta.**
- Em `_tangentes`, aplicar tangente 0 apenas em inversões **reais** (`d0*d1 < 0` com `|d0|,|d1| > eps`).
- Em chaves seguidas de pausa (d1 ≈ 0), usar `m = d0 * 0.15`. O corpo "assenta" e continua deslizando 1–2° na pausa, em vez de bater e congelar.
- Cardio cíclico: `AMORTECIMENTO = 1.0` (Catmull-Rom puro, velocidade contínua).

**C1.3 Overlap / atraso por canal.**
- Em `TrilhasPose.__call__(tau)`, cada canal é avaliado em `tau - atraso[k]`. Tabela sugerida, em segundos:
  - c / cr / cinc: 0,06
  - mãos (dedos, punho por slerp): 0,04
  - antebraço (2º elemento de bf/bt) em exercícios de tronco e pernas: 0,05
  - bf/bt em agachamento, terra e saltos: 0,03
  - pernas, tronco e quadril: 0
  - zerar o atraso dos segmentos que movem o implemento em isolados (rosca, elevação lateral), para a mão não "atrasar a carga".
- Golpes, arremessos e swing, sequência proximal→distal: quadril (tr da pelve) 0, tronco 0,03, ombro 0,05, cotovelo/mão 0,08 na ida. Na volta à guarda, o inverso, rápido.
- Como o atraso é periódico (avaliar em `tau mod T`), o loop continua sem emenda.

**C1.4 Camada de vida (micro-movimento) em todo exercício, obrigatória em isometrias.**
- Função `vida(tau, T, semente)` que soma senoides com **frequências harmônicas do período do loop**, `f = n/T` com n inteiro. Assim o loop fecha sem emenda.
- Canais e amplitudes:
  - respiração: período mais próximo de 3,2 s que divida T (n = round(T/3.2), mínimo 1);
  - tórax (spine03/spine02) com inclinação de ±0,8°;
  - ombros com `oe` ±0,03;
  - abdome: escala de 1–2 % no eixo frente-trás da região do abdome, se viável com shape key ou bone scale;
  - transferência de peso em pé: `z` ±0,08 unidade (8 mm), período = T ou T/2;
  - cabeça: c ±1,0°, cr ±1,5°, frequências diferentes;
  - tremor de esforço só em isometrias pesadas (prancha, prancha-lateral, wall-sit, segunda metade do nórdico): ±0,3° a 7–9 Hz (harmônico de T), amplitude modulada.
- Escalonamento: 100 % em isometrias e alongamentos, 40 % em isolados, 0 em cardio (o próprio movimento já é a vida).
- Dados: nas isometrias, **o segundo quadro deixa de ser cópia**. Usar a diferença de respiração descrita acima: `t` ±1°, quadril ±0,1.

**C1.5 Balística.**
- Trechos marcados `"bal"`: entre a decolagem (último quadro com pé no chão) e a aterrissagem, o deslocamento vertical do quadril segue `z(t) = z0 + v0 t − g t²/2`, com g = 9,81 m/s² convertido para unidades.
- Conversão: 1 unidade ≈ 0,1 m (k ≈ 0,1 m por unidade com o corpo de quadril a ~0,9 m); o ANIMADOR deve conferir pelo `k`.
- Regra de dados: com tempo de voo `t_f` (s), a altura do ápice é `h = 1,226 · t_f²` m, ou seja, `ay ≈ 12,3 · t_f²` unidades.
  - tuck-jump: t_f 0,5 s → ay ≈ 3,1;
  - polichinelo: t_f 0,2 s → ay ≈ 0,5.
- Horizontal em voo: velocidade constante.

**C1.6 Interpolar direções por slerp (humano.py `posar` / movimento.py).**
- Para cada segmento (braço, antebraço, coxa, canela), calcular nas chaves a direção 3D `d2(ang, abd)` e interpolar com **slerp de vetores** (arco de círculo máximo), em vez de interpolar ângulo e abdução separadamente.
- Para manter as curvas: aplicar `slerp(dA, dB, E(u))` dentro do trecho, com Squad (o equivalente de Catmull-Rom em quaternions) quando houver 3 chaves ou mais.
- Para movimentos circulares de propósito (círculos de braço e quadril, arnold), manter a interpolação angular ou acrescentar breakdowns.

**C1.7 Amostragem uniforme (movimento.py `instantes`).**
- `N = round(T*fps)`, `tau_j = j*T/N`. A duração total se ajusta em até ±1 quadro, sem distorcer os trechos curtos.
- Opcional: arredondar o T dos cardios para que `N` gere passos inteiros.

### Prioridade 2: rig, equilíbrio e contatos (2–3 dias)

**C2.1 Centro de massa.**
- Em `colocar_chave` e `quadro`, calcular o CM.
- Forma rápida: média ponderada da proxy, com pesos de Dempster/Winter (tronco 0,497, coxa 0,1, canela 0,0465, pé 0,0145, braço 0,028, antebraço 0,016, mão 0,006, cabeça 0,081) mais a carga do implemento (barra: 0,25 da massa corporal; halteres: 0,08).
- Em exercícios em pé, deslocar o quadril em y (frente-trás), com até ±1,5 unidade e peso suave, até a projeção do CM cair no **meio do pé**: 40–60 % entre calcanhar e ponta.
- Na passada e no búlgaro, usar o polígono dos dois pés.
- No hinge, a barra precisa terminar na vertical do meio do pé. Se não terminar, recuar o quadril e verticalizar os braços (`bf` ≈ −2…0 em relação à vertical do mundo).

**C2.2 Câmera por família** (campo `cam` mais os novos `cam_el`, elevação, e `cam_lente`).
- Trocar a ortográfica por **perspectiva de 50–70 mm equivalentes**, com a câmera longe (distorção mínima e profundidade natural). Ou manter a ortográfica, mas com elevação maior.
- `enquadrar`: calcular a caixa **só com o corpo, as mãos e o implemento nas mãos**. Torres, pórticos e esteira podem ser cortados pela borda.
- Alvo de enquadramento:
  - em pé: corpo com 75–82 % da altura do quadro;
  - deitado: 85–90 % da largura;
  - margem mínima de 5 %;
  - pés a 6–8 % da borda inferior.
- Tabela padrão (pode ser sobrescrita por animação):

| Família | Azimute (`cam`) | Elevação | Observação |
|---|---|---|---|
| Agachamento, hinge, terra, swing, lunges, step-up, búlgaro | 20–35 (perfil 3/4) | 8–12° | Mostra quadril × joelho × barra. |
| Supino, crucifixo e triceps-testa no banco | 50–64 | 22–30° | Câmera alta: a barra não cruza o rosto. |
| Flexão, prancha, mountain climber, abdominais no chão | 25–45 | 20–28° | Enquadramento horizontal apertado. |
| Remadas e puxadas | 30–45, ou −30 (posterior) para puxada/barra fixa | 10–15° | Dorsal visível; rosto livre. |
| Desenvolvimento, elevação lateral, abduções, polichinelo, monster-walk, carioca | 70–90 | 12–18° | Plano frontal. |
| Face-pull, crucifixo inverso, band-pull-apart, rotação externa | −30 a −45 (3/4 posterior) | 12–18° | Mãos não cobrem o rosto. |
| Roscas, tríceps na polia | 30–45 | 8–12° | |
| Corrida, bike, elíptico | 15–30 | 8–10° | Perfil. |
| Lutas (sombra, saco) | 35–55 | 10° | Mostra a rotação do quadril e a base escalonada. |
| Gato-camelo, ponte, superman, alongamentos sagitais | 0–15 (perfil) | 10–15° | |

- Verificação automática de "rosto livre" em C/D: projetar os pontos da cabeça e checar a sobreposição com mãos e implementos em cada quadro.

**C2.3 Chão com referência.**
- Disco de chão com um degradê muito sutil e **marcas** (linhas de 30 cm ou placas de borracha) em baixo contraste (luminância +3–5 % sobre o fundo).
- Torna visível o deslocamento de monster-walk, carioca, passada-andando, bound-lateral e salto-distancia, e dá contato visual (hoje o corpo parece flutuar).
- Em locomoção que deveria andar no lugar sem esteira: **adicionar deslocamento real** (root motion) mais vai-e-volta espelhado. Ou usar uma esteira ou piso que rola, deslocando a textura do chão na velocidade do pé apoiado; nesse caso o pé fica parado em relação ao chão visível.

**C2.4 Pole vectors e contra-rotação.**
- Joelho: em `ik`, o polo deve ser `FRENTE` rotacionado pela abdução da coxa (`pfa`) e pela rotação externa do pé (pontas 10–20° para fora). O joelho deve seguir a linha do 2º/3º dedo.
- Cotovelo:
  - polo para trás e para fora (já existe) quando o braço está ao lado do corpo;
  - para baixo nos empurrões horizontais, com os cotovelos a 45–60° do tronco no supino;
  - para fora na puxada.
- Contra-rotação na marcha e na corrida: tronco/ombros com `tr` oposto à pelve, de ±6–10° na corrida e ±4° na caminhada. Braços em oposição às pernas, cotovelo a ~90° na corrida e mãos cruzando levemente a linha média.
- Isso exige separar a rotação da pelve da do tórax. Hoje `tr` é distribuído de 0,2 a 1,0 a partir de root. Proposta: um novo canal `trp` (rotação da pelve).

**C2.5 Coluna e escápula.**
- Novos canais:
  - `cfl`: flexão (+) ou extensão (−) da coluna, ±30°, distribuída com mais peso na lombar (0,35/0,3/0,2/0,15);
  - `pel`: inclinação pélvica (+ antero, − retro);
  - `pro`: protração/retração (−1…1);
  - `dep`: depressão escapular.
- Escápula automática pelo ritmo 2:1:
  - rotação superior = `max(0, elev-30)/3`;
  - elevação da clavícula = `max(0, elev-60)*0.15`;
  - protração de +0,6 no fim de supino e flexão ("plus") e retração de 1,0 no fim das remadas.
- Gato-camelo: `cfl` +25 (gato) / −20 (camelo), `pel` −15/+15, cabeça acompanhando.

**C2.6 Implementos com física simples.**
- Kettlebell: a alça fica na mão, mas o corpo gira como um pêndulo amortecido em torno da pegada (alinhado com a resultante gravidade + aceleração da mão, ζ = 0,3).
- Saco de pancada: pêndulo com impulso no quadro do impacto.
- Corda de pular e battle rope: onda senoidal com fase atrasada ao longo do comprimento.
- Elástico: catenária curta e tensão (afinar o diâmetro em até 30 % quando esticado).

**C2.7 Breakdowns** para transições complexas (turkish-getup, burpee, inchworm, spider, box-jump): uma chave intermediária a cada mudança de apoio, com `apoio` explícito.

### Prioridade 3: render e encode (½–1 dia)

**C3.1 Motion blur.**
- Opção A (preferida), supersampling temporal só nos exercícios rápidos (cardio, pliometria, lutas, corda, battle rope e polichinelo; ou quando a velocidade de pico da mão ou do pé passar de 2,5 m/s):
  - renderizar a 2× (48 amostras/s) com metade das amostras do Cycles;
  - fazer a média de cada par, em ponto flutuante antes do `compor`;
  - equivale a um obturador de 180°, com custo de cerca de 1,6× nesses ~30 exercícios.
- Opção B: inserir keyframes nos ossos e no objeto do aparelho (frame−1, frame, frame+1) e usar `render.use_motion_blur = True`, `motion_blur_shutter = 0.4`.

**C3.2 FPS.** Manter 24 nos lentos. Usar **30 fps** nos rápidos (lista acima), com motion blur. O `meta.json` já guarda o `fps`.

**C3.3 Pontilhado.** Usar ruído **fixo** (a mesma semente em todos os quadros) ou um padrão azul ordenado. Ganho esperado de 10–25 % de bitrate e fim do "chuvisco" no fundo parado.

**C3.4 Encode.**
- `-tune animation` em vez de `film`.
- Manter CRF 18–20, `-preset slow`, High@4.0, yuv420p, `+faststart` e `-g` = N (um GOP por loop, o que facilita a emenda no player).
- Para economizar, CRF 20 com tune animation fica visualmente igual em tela de celular, com uns 20 % a menos.
- Conferir que o player do app usa loop sem gap (ExoPlayer `REPEAT_MODE_ONE`, ou concatenar 2 ciclos no arquivo se houver flash).

**C3.5 Amostras e denoise.**
- 12 amostras com OIDN "FAST" e prefilter FAST pode piscar entre quadros nos vales musculares.
- Usar 16 amostras com `denoising_prefilter = "ACCURATE"` nos quadros finais, ou fixar `seed` constante (`sc.cycles.seed = 0`, sem animar a semente) para o ruído ficar estável no tempo.

**C3.6 Luz.**
- A estrutura de 3 pontos está certa (chave lateral, preenchimento azulado, recorte quente).
- Ajustes:
  - aumentar um pouco o recorte nas câmeras posteriores (cam < 0), porque hoje a silhueta some no fundo escuro;
  - garantir a sombra de contato: adicionar AO de contato no shadow catcher ou baixar o tamanho da luz-chave de 3,5 para 2,5, para uma sombra mais definida sob os pés e as mãos.

**C3.7 Pele e músculo.**
- O destaque vermelho (0,86; 0,11; 0,06) com secundário salmão funciona.
- Em vistas posteriores, o glúteo vermelho por baixo do short escuro fica quase invisível. Subir a mistura de 0,8 para 0,9, ou deixar o short mais curto e cinza-médio.

### C3. Regras de dados por família (valores de referência)
Cadência no formato excêntrica-pausa-concêntrica-pausa (s). Os tempos totais são por repetição do loop.

| Família | Cadência / tempos | Ângulos-chave | Detalhes de vida e técnica |
|---|---|---|---|
| Agachamento (livre, goblet, barra, frontal, hack) | 2,0 desc (exc) · 0,25 fundo · 1,2 sub (con) · 0,4 topo | Fundo: joelho 100–120°, quadril 100–115°. Tronco `t` 140–150 (livre/costas), 155–165 (frontal/goblet). Canela 25–35° à frente. `pfa` 12–18 (joelhos para fora, na linha dos pés). | Quadril e joelho começam juntos (sem "quadril primeiro" exagerado). Calcanhar plantado. Barra sobre o meio do pé (CM, C2.1). Inspira no topo e segura na descida (tórax +1°). |
| Hinge (stiff/RDL, terra, good morning, swing) | RDL: 2,0 exc · 0,2 · 1,2 con · 0,4. Terra: 0,3 setup · 1,0 con · 0,3 lockout · 1,5 exc. | RDL: joelho 15–25° fixo, tronco 80–100° com a horizontal no fundo (`t` 95–110), quadril recua 2,5–4 unidades (ajuste por CM). Barra no meio do pé, raspando a coxa. | Coluna neutra (`cfl` 0). Olhar 1–2 m à frente (`c` = t + 10…20). No lockout, quadril estendido sem hiperestender a lombar. Swing: snap do quadril em 0,15–0,2 s (con) e pêndulo do kettlebell. |
| Lunges (afundo, passada, búlgaro, step-up) | 1,5 exc · 0,2 · 1,0 con · 0,3 | Joelho da frente ~90°, joelho de trás a 2–5 cm do chão. Tronco 170–180 (afundo); 160–170 no búlgaro com ênfase em glúteo. | Peso 70–80 % na perna da frente (CM). Passada andando com deslocamento real e passos (`passos: true`). |
| Empurrar horizontal (supino, flexão, máquina) | 2,0 exc · 0,2 · 1,0 con · 0,3 | Cotovelos a 45–60° do tronco no fundo. Barra no esterno baixo/mamilos; trajetória em "J" (sobe em direção aos ombros, 3–5 cm). Antebraço vertical no fundo. Flexão: mãos sob os ombros, corpo em linha. | Escápula retraída na descida e protração leve no topo (máquina/flexão). Pés plantados. Barra sem cruzar o rosto na câmera. |
| Puxar (remadas, puxadas, barra fixa, face-pull) | 1,0 con · 0,4 pico · 1,8 exc · 0,3 | Remada curvada: tronco 30–45° da horizontal (`t` 125–135). Puxada: cotovelo desce até ~altura das costelas, peito vai ao encontro da barra (inclinação de 10–15°). Face-pull: mãos ao lado das orelhas, cotovelos altos (C0.6). | A escápula retrai e deprime **antes** do braço (overlap de −0,1 s). Ombros não sobem (`oe` 0). Barra fixa: leve hollow body e pernas quietas, com micro-balanço de 1°. |
| Desenvolvimento / elevações | Des.: 1,0 con · 0,25 · 1,8 exc · 0,3. Elev. lateral: 1,0 · 0,3 · 2,0 · 0,4 | Elevação lateral no plano escapular (~25–30° à frente): use **slerp** (C1.6). Para em 85–90°, cotovelo com 10–20° de flexão, punho na altura do cotovelo. Desenvolvimento: antebraço vertical, barra/halteres sobem num leve arco por cima da cabeça, a cabeça "passa pela janela" na barra. | Ritmo 2:1 (C2.5). Tronco sem balançar (vida de 40 %). |
| Isolados de braço (roscas, tríceps) | 1,0 con · 0,3 · 2,0 exc · 0,3 | Rosca: o cotovelo avança no máximo 10–15° no topo e fica rente ao tronco. Tríceps na polia: cotovelo fixo ao lado do corpo, flexão de 30° → 150°. Tríceps testa: braço 5–10° atrás da vertical, a barra desce até a testa/topo da cabeça (sem pop: C0.1). | Punho neutro. Overlap mínimo (a carga acompanha a mão). Micro-transferência de peso entre os pés. |
| Core e abdominais | Crunch: 0,9 con · 0,4 · 1,5 exc. Isometrias: ciclos de respiração de 3–4 s | Crunch: só as escápulas saem do chão (flexão de tronco de 25–35° via `cfl`), mãos nas têmporas sem puxar a cabeça (`apoio` explícito: mãos fora). Prancha: corpo reto, quadril sem cair, retroversão de 5° (`pel`). | Isometria: camada de vida a 100 % mais tremor leve. Dead-bug: lombar colada (`pel` −5), braço e perna opostos ao mesmo tempo. |
| Pliometria | Antecipação 0,2–0,3 · decolagem 0,1 · voo (bal) · aterrissagem 0,2 · reset 0,4–0,6 | Contramovimento: joelho 60–90°, braços atrás (`bf` −40…−60). Aterrissagem: tornozelo-joelho-quadril amortecem, joelho 40–70°. | Voo balístico (C1.5). Joelhos sem valgo na aterrissagem. Box-jump: descer da caixa **andando** (step-down), não saltando para trás. |
| Corrida e cardio | Corrida leve: cadência de 165–175 passos/min (ciclo de 0,69–0,73 s). Tiros: 180–190. Bike: 80–95 rpm. Polichinelo: 0,8–1,0 s/rep. | Corrida: aterrissagem com o pé perto da vertical do quadril, joelho com 15–20° de flexão no contato, oscilação vertical de 6–8 cm, tronco a 5–8° à frente, cotovelo a ~90°, braço oposto à perna, contra-rotação de ±8°. | 30 fps mais motion blur (C3). Cabeça estável (o olhar não oscila: compensar `c` contra o tronco). `ease: lin`. |
| Lutas (sombra, saco, sprawl) | Jab 0,15 ida · 0,15 volta; cruzado 0,2 · 0,2; pausa/guarda 0,3–0,5 com bounce | Base: pés à largura dos ombros, escalonados (pé de trás 30–40 cm atrás, calcanhar de trás elevado), joelhos 15–25°. Guarda: mãos no queixo, cotovelos fechados. | Cruzado: rotação do pé de trás → quadril (`trp` 30–40°) → tronco → ombro → braço (overlap de 0,03–0,08 s). Retorno à guarda mais rápido que a ida. "Bounce" de ±1 cm a ~2 Hz. Saco reage (pêndulo). |
| Alongamento e mobilidade | Entrar 1,2–1,5 s (io) · segurar 3–6 s (respiração, cada expiração aprofunda 1–2°) · sair 1,2 s | Amplitude dentro do confortável (sem hiperextensão). Gato-camelo: `cfl` ±25, ciclo de 4–5 s. | Camada de vida a 100 %. Respirar: na expiração, aprofundar 1–2° (fase sincronizada com a respiração). |

Regras gerais para o JSON (atualizar o `INSTRUCOES.md` depois):
1. **Nunca dois quadros idênticos.** A diferença mínima é de 0,5–1° em `t` ou em `c` (respiração), ou usar a camada de vida.
2. Membro de trás com 2–4° de defasagem **e** 1–3 cm de diferença de altura de mão (assimetria natural), já que a regra 9 hoje cria só profundidade.
3. Pausa de 0,2–0,4 s no fim da concêntrica e de 0,3–0,5 s no início (setup e respiração) em exercícios de força. Hoje a maioria vai do fim direto para o início.
4. Campos novos: `ease`, `apoio`, `cam_el`, `barra_modo`, `cfl`, `pel`, `trp`, `pro`, `dep`, `vida` (0..1).

---

## D) Checklist de aprovação e verificação automática

### D1. Checklist visual (por animação)
1. O movimento lê em 1 s, sem som: dá para reconhecer o exercício no 1º ciclo.
2. A câmera mostra o plano principal do movimento (tabela C2.2); rosto e mãos visíveis em 100 % dos quadros.
3. O atleta ocupa 75–85 % da altura (em pé) ou 85–90 % da largura (deitado); margens ≥ 5 %.
4. Pés e mãos de apoio parados (sem deslizar) e sem flutuar; nenhum pé ou mão atravessa o chão, o banco ou a caixa.
5. Implemento colado à mão (sem escorregar); barra sem trocar de lugar; alavancas com comprimento constante, por fora do corpo.
6. Sem interpenetração corpo × aparelho (costas × banco, coxa × barra, canela × rolo).
7. Cadência dentro da tabela C3; excêntrica mais lenta que a concêntrica; pausas com vida.
8. Arcos limpos (mão e implemento sem "zigue-zague"); overlap visível na cabeça e nas mãos.
9. Técnica: coluna neutra (exceto nos exercícios de flexão de coluna), joelho na linha do pé, CM sobre o meio do pé, amplitude correta.
10. Loop: impossível achar o ponto da emenda assistindo 3 ciclos.
11. Nenhum quadro idêntico ao anterior (vida); sem pops.
12. Arquivo ≤ 350 KB (lentos) / ≤ 600 KB (rápidos); H.264 High, yuv420p, faststart, fps conforme a família.

### D2. Verificação automática: `tools/anim3d/qa.py` (proposta)
Rodar o motor **sem renderizar** (só `preparar_anim` + `quadro` para cada tau) e medir em espaço de mundo. As unidades estão em metros reais via `k`.

| Teste | Como medir | Limite para reprovar |
|---|---|---|
| Pé ou mão apoiada parada (foot-skate) | Para cada efetor com contato nas duas chaves do trecho: deslocamento horizontal do ponto mais baixo da pele (`info_efetor["baixo"]`) entre quadros consecutivos. | > 3 mm/quadro, ou > 1 cm acumulado no trecho |
| Flutuar ou afundar | `zmin` do efetor apoiado − superfície (`superficie_em`). | fora de [−5 mm, +8 mm] |
| Penetração no chão | `proxy(T)[:,2].min()` vs `ctx.z0`. | < −5 mm |
| Penetração em banco, caixa ou máquina | Pontos da proxy dentro das caixas de `superficies()` (exceto a face de apoio). | > 20 pontos ou profundidade > 1 cm |
| Mão × implemento | Distância entre `pegada(sf)` e o pegador do aparelho (barra: eixo; halter: centro; alavanca: ponto do pegador). Com alavanca rígida, vale como teste real. | > 5 mm |
| Barra contínua | Velocidade e aceleração do centro da barra. | salto > 3× a mediana, ou > 8 cm/quadro |
| Alavanca rígida | Comprimento pivô→pegador ao longo do loop. | variação > 2 mm |
| Haste por fora do tronco | Distância mínima entre o segmento da alavanca e a proxy do tronco e dos braços. | < 2 cm |
| Pop de pose | Deslocamento máximo de junta por quadro vs a mediana dos 4 vizinhos (também no vídeo: diferença de quadro, como em `energia.py`). | > 2,2× e > 4 cm |
| Emenda do loop | Posição p(0) vs a extrapolação 2·p(N−1) − p(N−2) para todas as juntas; velocidade v(N−1) vs v(0). | erro > 1,5× o passo médio, ou mudança de velocidade > 50 % |
| Congelamento | Quadros com deslocamento máximo de junta < 0,5 mm. | sequência > 6 quadros |
| Rosto livre | Projetar na câmera a esfera da cabeça (centro `head`, raio 0,11 m) e os polígonos das mãos e do implemento. | sobreposição > 15 % da área do rosto em qualquer quadro |
| Enquadramento | Caixa do corpo projetada / tamanho do quadro. | altura < 0,7 ou > 0,9 (em pé); margem < 4 % |
| CM sobre a base | Projeção do CM (C2.1) dentro do polígono de apoio, com margem de 1 cm (exercícios estáticos e lentos). | fora em > 10 % dos quadros |
| Limites articulares | Joelho e cotovelo de −5 a 160°; abdução do ombro ≤ 180°; tronco × coxa coerente. | fora dos limites |
| Cadência | Duração dos trechos por `ease` vs a tabela C3 da família (pelo `grupo` em `exercises.json`). | fora da faixa ±30 % |
| Encode | `ffprobe`: h264 High, yuv420p, faststart (átomo moov antes de mdat), fps = meta, nb_frames = meta.f. | qualquer divergência |
| Tamanho | Bytes do mp4. | > 600 KB |

Saída sugerida: `qa.json` por id, mais uma folha de contato com os quadros reprovados marcados em vermelho. No CI, rodar o QA em `.github/workflows/anim3d.yml` antes do render: falha só nos erros (pop, skate, penetração, emenda) e emite aviso nos demais.

### D3. Ordem de execução sugerida para o ANIMADOR
1. C0.1–C0.5 (pops e contatos) mais o `qa.py` mínimo (pop, emenda, skate). Re-renderizar os 17 com pop e rodar o QA nos 175.
2. C0.6–C0.7 (face-pull, monster-walk, supino-maquina, salto-distancia).
3. C1 (easing, tangentes, overlap, vida, balística, slerp, amostragem): mudança global; revisar uma amostra de 25 antes do lote completo.
4. C2.2 + C2.3 (câmera e chão) e C2.1 (CM).
5. Dados por família (C3), lote a lote, com o QA verde.
6. C2.4–C2.7 (rig avançado e física dos implementos) e C3 (render e encode). Render final no CI.
