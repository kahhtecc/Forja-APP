# Auditoria das animações 3D: lote3 (63 exercícios)

Auditor: biomecânica e animação técnica. Fonte: vídeos de produção `app/src/main/assets/video3d/<id>.mp4` (720 px, 30 fps),
quadro a quadro, mais renders extras de perfil (cam 0) e de frente (cam 90) com `tools/anim3d/humano.py`.
Folhas de contato: `/tmp/claude-0/-home-user-teste-3/400edce2-80ea-57f6-97f9-c6ff24db5c18/scratchpad/auditoria/lote3/folhas/`
(abaixo abreviado como `F/`). "q12" = quadro 12 do vídeo (30 fps); "Q2" = quadro-chave 2 do JSON (base 0).

## Resumo

| Status | Qtde | Exercícios |
|---|---|---|
| APROVADO (só ressalvas leves ou nenhuma) | 26 | farmer-walk, corrida-leve, tiros, tempo-run, longao, prova, bike-leve, bike-intervalado, bike-cadencia, caminhada, maior-alongamento, gato-camelo, postura-crianca, flexor-quadril, alongamento-posterior, alongamento-panturrilha, circulos-braco, alongamento-peito, equilibrio-unipodal, chute-gluteo, abertura-peito-dinamica, spider, alongamento-pescoco, alongamento-lateral, alongamento-dorsal, moinho |
| DEFEITO CRÍTICO | 21 | corda, swing, thruster, power-clean, arremesso-medicine, battle-rope, sled-push, turkish-getup, inchworm, sombra, saco-combinacoes, bear-crawl, eliptico, remo-ergometro, escada, alongamento-quadriceps, rolo-it, rotacao-toracica, circulos-punho, alongamento-gluteo, abraco-joelhos |
| DEFEITO MÉDIO (pior defeito) | 15 | burpee, polichinelo, sprawl, caminhada-corrida, circulos-quadril, rolo-quadriceps, rolo-panturrilha, alongamento-adutores, balanco-pernas, circulos-ombro, circulos-joelho, carioca, alongamento-triceps, alongamento-antebraco, torcao-coluna |
| DEFEITO LEVE (só) | 1 | circulos-tornozelo |

### Falhas sistêmicas do motor (para o especialista do motor)
- **S1. Implemento seguro com as duas mãos fica no ponto médio entre punhos afastados** (`aparelhos._kettlebell`, `_bola`; `estado_maos`): kettlebell/bola flutuam entre as mãos sem contato (swing, thruster, arremesso-medicine). Precisa: IK que converge as duas pegadas no implemento (alça do kettlebell: mãos lado a lado; bola: palmas nos lados da esfera, dedos abertos), sino orientado pelo antebraço (rack/overhead), e soltura/parábola para arremessos.
- **S2. Mão livre nunca fecha** (`estado_maos` → 0 = relaxada): socos de mão aberta (sombra, saco, sprawl), corrida/caminhada com dedos esticados, guidão da bike com mão espalmada. Precisa: campo por animação `"maos": "punho" | "semi"` e "ocupada" quando a mão está em guidão/alça.
- **S3. Sem "mão segura parte do corpo"**: quadríceps (mão no pé), figura 4 e abraço dos joelhos (mãos na coxa/canela), tríceps (mão no cotovelo), círculos de joelho/quadril (mãos nos joelhos/cintura), borboleta (mãos nos pés), torção (cotovelo no joelho). Precisa: restrição `"segura": {"mao_f": "pe_f" | "joelho_t" | "cotovelo_f" | "quadril"}` resolvida por IK depois da pose, com dedos fechados.
- **S4. Aparelhos genéricos não representam a máquina** (`maquina` bloco/pedestal): sled-push (púlpito com uma mão), elíptico (sem pedais/alças móveis, coluna entre as pernas), escada (sem degraus, pé pisando no ar), balanço de pernas sem parede. Precisa: aparelhos dedicados (trenó com dois postes, elíptico com pedais e alças presos aos pés/mãos, stair climber com degraus, parede opcional).
- **S5. Assento do remo em altura fixa** (`_assento_remo` z=1,05): quadril acima do assento na pegada. Assento deve seguir os ísquios (ou o dado manter `y` constante).
- **S6. Transições com pés presos e coxa passando pela vertical arrastam o joelho no chão** (burpee, sprawl): falta fase de voo/"pés soltos" quando o dado não declara; sugerir `apoio` só nas mãos no trecho e `ay` curto.
- **S7. Apoios que mudam de lugar nas mãos** (inchworm): mãos deslizam e o corpo encolhe; o "apoio que muda vira passo" precisa valer para as mãos.
- **S8. Corda de pular e corda naval** (`_corda`, `elastico`): corda passa pelos pés no apoio (2 voltas/ciclo, fase errada), atravessa o tronco e parece aro; corda naval é haste reta sem ondas.
- **S9. `rol` (deitado de lado) com apoio automático** escolhe a mão como ponto mais baixo e o corpo flutua (rotacao-toracica; rolo-it com perna de cima no ar). Precisa: apoio por "lado do corpo" (ombro/quadril/joelhos de baixo) quando `rol` ≈ 90.
- **S10. Sem articulação do punho controlável** (circulos-punho) e sem rotação da mão apoiada (alongamento-antebraco: dedos para trás). Campos novos `puf/pud` e `"dedos": "tras"`.
- **S11. Ombro em abdução >150°**: trapézio/deltoide "engolem" o pescoço (polichinelo, braços acima da cabeça); limitar elevação da clavícula/corrigir pesos.
- **S12. Barra no clean** (`corrigir_barra` modo "clean"): mistura com o rack depende da distância das mãos; com dados ruins a barra fica no rosto. Forçar rack (peso 1) quando cotovelo > 80° e mãos por IK até a barra.

---

---

## Exercícios

### 1. burpee: DEFEITOS
Folhas: `F/burpee.png`, `F/burpee_joelho_chao.png`, `F/p0_b.png` (perfil).
- **Q1→Q2 e Q3→Q4 (q15–q17, q26–q28): joelhos caem até o chão no "pular para trás/para frente"** (médio). Causa: a coxa interpola de 77,9° para -72,3° passando por 0° (vertical para baixo) com os pés presos no chão, então o joelho desce em arco até tocar o piso. No burpee real os pés saltam para trás com o quadril alto (pés no ar por um instante). Correção: inserir um quadro intermediário de voo entre Q1 e Q2 (e entre Q3 e Q4): `"apoio": ["mao_f","mao_t"]`, `"ay": 0.5`, `pf [10, -60, 40]`, `pt [8, -62, 40]`, `t 112`; ou pelo menos `"apoio":["mao_f","mao_t"]` nesses trechos para os pés não ficarem pregados.
- **Ritmo rápido demais** (leve): ciclo inteiro 1,73 s; burpee técnico leva ~2,5–3 s. Correção: `tempos [0.6, 0.45, 0.45, 0.5, 0.5]`.
- Salto final (Q4) e prancha OK; mãos espalmadas no chão OK.

### 2. polichinelo: DEFEITOS
Folhas: `F/polichinelo.png`, `F/polichinelo_ombros.png`.
- **Braços acima da cabeça (q9–q12): ombros/trapézio "engolem" o pescoço; a cabeça afunda entre os deltoides** (médio). Causa: motor/skin (pesos padrão MakeHuman do `clavicle`/`shoulder01` + elevação escapular pelo ritmo escápulo-umeral sem compensação), não o dado. Correção (motor): limitar a elevação da clavícula a ~20° em abdução >150° e/ou corrigir pesos do deltoide/trapézio (ou alvo corretivo "shoulder-up"); ver Falhas sistêmicas S2.
- Resto OK: pernas abrem ~ largura correta, voo no meio do trecho, aterrissagem nas pontas, ciclo 0,72 s.

### 3. corda (pular corda): DEFEITOS
Folhas: `F/corda.png`, `F/p0_b.png`.
- **Corda passa por baixo dos pés quando os pés estão no chão** (crítico). Causa: `aparelhos._corda` usa `fase = tau/(T/2)·2π` → 2 voltas por ciclo, com o ponto mais baixo em tau=0 (Q0, pés apoiados) e em tau=T/2. Correção (motor): 1 volta por salto e ponto mais baixo no pico do voo: `fase = 2π·(tau - t_pico)/T`, com `t_pico` = instante de maior `ay` (Q1 ≈ 0,2 s).
- **Corda atravessa o tronco** (q3, q9: o laço cruza peito/quadril) e **forma um "aro" fino** (crítico). Causa: a curva é uma Bézier de mão a mão com o ponto de controle no plano sagital do corpo (x=0) e as mãos quase juntas; não abre para fora dos ombros. Correção (motor): corda como dois ramos que saem de cada mão para fora (x = ±(meia largura dos ombros + 0,6)) e se unem no ponto M, com M girando num círculo de raio ≈ altura do ombro em torno de um eixo à altura das mãos; corda sempre por fora do corpo.
- Sem cabos/manoplas nas mãos (leve): adicionar cilindros de 1,2 unid. nas pegadas.
- Pose do saltador OK (cotovelos junto ao corpo, saltos baixos, ponta dos pés).

### 4. swing (kettlebell swing): DEFEITOS
Folhas: `F/swing.png`, `F/swing_pegada.png`, `F/p0_b.png`.
- **As mãos não seguram a alça: punhos a ~largura dos ombros e a kettlebell flutuando entre eles** (crítico, todo o vídeo). Causa: `bfa/bta` 0–4 (braços paralelos) e `_kettlebell` só posiciona o sino no ponto médio das pegadas. Correção: dados com as mãos juntas na alça (`bfa -8`, `bta -8` em todos os quadros, ou o motor convergir as mãos: em kettlebell "ambas", IK das pegadas para ±0,3 unid. do centro da alça, ao longo do eixo da alça).
- **No topo (q17–q19) o sino fica pendurado abaixo das mãos** (médio): no swing real, no ponto alto o sino está alinhado com os braços (flutua). Causa: amortecimento do pêndulo em `_kettlebell` (ze 0,42, mistura 0,25 de "para baixo"). Correção: no swing, direção = linha do antebraço (peso 1,0) no trecho de subida/topo; pêndulo só na descida.
- Dobradiça de quadril, joelhos e tronco: OK.

### 5. thruster (com kettlebell): DEFEITOS
Folhas: `F/thruster.png`, `F/thruster_pegada.png`, `F/p0_b.png`.
- **Kettlebell flutuando entre os dois punhos, sem contato com nenhuma mão** em todas as fases (crítico). Causa: um único `kettlebell` "em maos" com as mãos separadas ~largura dos ombros. Correção: usar dois kettlebells (`{"tipo":"kettlebell","maos":"f"}`, `{"tipo":"kettlebell","maos":"t"}`), ou um só segurado pelos "chifres" com as mãos juntas (`bfa/bta` ≈ -10 e `afa/ata` 0 para as mãos se tocarem diante do peito); no motor, a orientação do sino tem que seguir o antebraço: no rack o sino apoia no dorso do antebraço (por fora), e acima da cabeça fica atrás do punho (não pendurado ao lado da cabeça).
- **Rack (Q1–Q2): punho da frente encostado no queixo/boca** (q8) (médio). Correção: `bf [28,162]` → `bf [20,150]`, `bfa 25` (cotovelo à frente e para fora, mão diante do ombro).
- Agachamento e empurrão: OK.

### 6. power-clean: DEFEITOS
Folhas: `F/power-clean.png`, `F/power-clean_rack.png`, `F/p0_c.png`.
- **Recepção (Q2–Q3, q16–q37): barra na altura da boca/nariz atravessando o rosto; mãos acima da barra abertas, sem segurá-la** (crítico). Causa: dados `bf [62,202]` (braço abaixo da horizontal, antebraço apontando para trás/cima) levam as mãos até o rosto; no modo "clean" (`corrigir_barra`) a mistura com o rack depende da distância mão-rack, e com as mãos longe a barra fica no meio do caminho. Correção: rack frontal real = braço ~horizontal à frente, cotovelos altos, barra sobre os deltoides: `bf [95, 215]`, `bt [92, 212]`, `bfa/bta 18`, `afa/ata 0`; no motor, no modo "clean" a barra deve ir a `rack` com peso 1 quando o cotovelo passa de 80°, e as mãos fazem IK até a barra (dedos por baixo).
- **Volta do rack ao quadril (Q3→Q4, q43): barra sobe para a frente com braços estendidos na horizontal** (médio): parece uma elevação frontal. Causa: o antebraço interpola de 202° para -1° passando por 100°. Correção: quadro intermediário `bf [15, 100]`, `bt [13, 98]` (barra desce rente ao peito) ou `ease` com o antebraço descendo primeiro.
- Posição inicial, primeira e segunda puxada: OK.

### 7. arremesso-medicine: DEFEITOS
Folhas: `F/arremesso-medicine.png`, `F/arremesso_pegada.png`, `F/p0_c.png`.
- **Bola não fica entre as palmas: mãos afastadas ~largura dos ombros, bola flutuando ao lado/abaixo de um punho** (q0, q36, q42) (crítico). Causa: `_bola` coloca a bola no ponto médio das pegadas + direção da palma; os dados têm braços paralelos (`bfa 6–12`). Correção: mãos espalmadas nos lados da bola (distância entre palmas ≈ 2,2 unid.): `bfa/bta -6` com `afa/ata -10`; motor: na bola, IK das duas palmas para os lados da esfera e dedos abertos (estado 0 ou -0,3, não "pegada" fechada).
- **A bola nunca sai das mãos** (médio): o arremesso não tem soltura/quique. Correção: (motor) modo "solta" entre Q1 e Q2: a bola segue parábola até o chão e quica para as mãos em Q2.
- Movimento do corpo (extensão acima da cabeça, agachar no arremesso, pegar): OK.

### 8. battle-rope (corda naval): DEFEITOS
Folhas: `F/battle-rope.png`, `F/battle_zoom.png`, `F/p0_c.png`.
- **As cordas são hastes retas e rígidas da mão até o chão, sem ondas** (médio–crítico para a leitura do exercício). Causa: prop `elastico` (segmento reto até [15, 0.3]). Correção (motor): prop novo "corda_naval": dois cabos grossos ancorados a ~25 unid. à frente, deitados no chão, com onda senoidal propagando da mão para a âncora (amplitude ∝ altura da mão, fase defasada por lado para ondas alternadas).
- Pose semi-agachada e braços alternados: OK. Mãos fechadas na ponta da corda: OK.

### 9. farmer-walk: APROVADO com ressalvas leves
Folhas: `F/farmer-walk.png`, `F/p0_c.png`.
- Halteres pequenos para "pesos pesados" (leve): aumentar o halter (anilhas maiores) quando `id` = farmer-walk.
- Braços balançam ~17° no antebraço (leve): com carga pesada os braços pendem parados. Correção: `bf/bt` ±1°, antebraço igual ao braço.
- Passada longa para "passos curtos" (leve): reduzir amplitude das coxas em ~30%.
- Pegada, postura e contato dos pés: OK.

### 10. sled-push (empurrar trenó): DEFEITOS
Folhas: `F/sled-push.png`, `F/sled_pes.png`, `aud3render/c0/sled-push.jpg` (perfil).
- **Pés no ar a maior parte do ciclo: o corpo fica "pendurado" no apoio das mãos, nenhum pé empurra o chão** (crítico). Causa: `fixo: "maos"` + `rolar` e os ângulos das pernas não alcançam y=0; sem `apoio` por quadro. Correção: baixar o quadril (`y` explícito) ou reduzir a flexão do joelho da perna de apoio para que um pé toque o chão em todo quadro (perna de apoio estendida para trás: `pt [-40,-45,60]`, joelho da perna que avança `pf [55,-20,90]`) e declarar `"apoio": ["mao_f","mao_t","pe_t"]` / `["mao_f","mao_t","pe_f"]` alternando.
- **Mão de trás no ar acima/além do aparelho** (perfil) e **"trenó" é um pedestal fino tipo púlpito** (crítico/médio). Causa: `maquina` w 1,4 × h 9,41 só recebe uma mão. Correção: aparelho próprio de trenó (base no chão + dois postes verticais com pegadores na altura das mãos, separados ~largura dos ombros); `bfa/bta 12` com as duas mãos fechadas nos postes.
- Ciclo de 1,28 s com passos de 0,32 s (leve): trenó pesado tem passos de ~0,45 s. `tempos [0.42,0.42,0.42,0.42]`.

### 11. turkish-getup: DEFEITOS
Folhas: `F/turkish-getup.png`, `F/tgu_zoom.png`, `F/tgu_seq.png`, `F/p0_a.png` (perfil).
- **Fase "sentar no cotovelo/mão" (Q1, q22–q46 e q180–q200): tronco inclinado ~35° para trás SEM apoio: a mão livre fica no ar atrás do quadril (não toca o chão)** (crítico: corpo apoiado no invisível). Causa: `bt [-30,-28]` com `bta 38` deixa a mão ~1 unid. acima do chão e sem `apoio`. Correção: mão livre espalmada no chão a ~45° do tronco: `bt [-40,-20]`, `bta 40`, `"apoio": ["mao_t","pe_f"]` (+ quadril) e conferir y≈0 da mão; incluir a etapa "no cotovelo" antes (`bt [-10, 60]` com antebraço no chão).
- **Falta a ponte de quadril e a passagem da perna por baixo (leg sweep)** (médio): de Q1 para Q2 o corpo sobe direto para o ajoelhado, a perna estendida se dobra no ar (q50–q58) e o joelho "aterrissa" já atrás. No TGU real: mão e pé apoiados, quadril sobe (ponte), a perna estendida passa por baixo e o joelho apoia sob o quadril. Correção: quadro intermediário de ponte (`t -150`, `y` do quadril +2, `pt [70,-20,90]` flexionando, `apoio ["mao_t","pe_f","pe_t"]`) e depois ajoelhado com mão ainda no chão, então tronco ereto.
- **Ajoelhado (Q2/Q4): joelho de trás e dorso do pé apoiados OK, mas o pé de trás aparece com a planta para cima atravessando o piso em q62–q66** (leve). Causa: `pt [-6,-94,268]`. Correção: `pt [-6,-90,-92]` (dorso do pé no chão) ou `[-6,-90,-160]` (dedos apoiados).
- Braço do kettlebell vertical e travado o tempo todo e olhar no peso: OK. Kettlebell na mão (`maos: f`): OK.

### 12. inchworm: DEFEITOS
Folhas: `F/inchworm.png`, `F/inchworm_zoom.png`, `F/p0_a.png`.
- **Prancha nunca é atingida: em Q3 (q55–q74) joelhos dobrados quase no chão e quadril cedendo** (crítico: o exercício termina em prancha alta). Causa: `fixo: "pes"` + mãos presas no ponto do 1º apoio; o motor não consegue afastar mãos e pés o bastante e "encolhe" as pernas. Correção: mãos realmente andam: 3–4 passos de mão (quadros com `apoio` só de uma mão, deslocando `x`); ou modelar como prancha final com `x` do quadril +4 e permitir que as mãos sejam âncoras novas por trecho (motor: "apoio que muda de lugar vira passo" precisa valer para as mãos neste exercício). Pendência já conhecida no PROGRESSO (skate das mãos).
- **As mãos deslizam no chão em vez de dar passos** (crítico, q28–q55 e q83–q110). Mesma causa/correção acima.
- **Dobra excessiva em Q1/Q5 (q18–q37, q101–q110): cabeça entre as canelas, abaixo dos joelhos** (médio). Causa: `t 18`, `c 8` (tronco 18° da vertical para baixo). Correção: `t 35`, `c 30`, joelhos levemente flexionados (`pf [12,-10,90]`).

### 13. sombra (shadow boxing): DEFEITOS
Folhas: `F/sombra.png`.
- **Socos com a mão aberta (dedos esticados) e guarda com palmas abertas** (crítico: no boxe a mão é fechada). Causa: `estado_maos` dá 0 (relaxada) quando a mão não segura nada. Correção (motor): campo por animação `"maos": "punho"` (estado 1 = punho fechado, sem objeto) ligado por padrão em sombra/saco/sprawl-guarda; ou detectar `id` de luta.
- Golpes, guarda alta, rotação de tronco (`tr`/`trp`) e esquiva (`inc -14`): OK. Calcanhar de trás elevado: OK.

### 14. saco-combinacoes: DEFEITOS
Folhas: `F/saco-combinacoes.png`.
- **Mãos abertas nos golpes e na guarda (sem luva/punho)** (crítico). Mesma causa de sombra. Correção: punho fechado; idealmente luvas (esfera achatada nas mãos).
- **Direto/cruzado (Q2, q14–q19) não alcança o saco (mão para ~3 unid. antes)**, mas o saco balança como se tivesse sido atingido (médio). Correção: `saco.x` 7,48 → 6,6 ou braço `bt [86,88]` → `[90,90]` com `tr` 30 e passo à frente (`pf [24,-2,88]`).
- Saco pendurado e pêndulo: OK.

### 15. sprawl: DEFEITOS
Folhas: `F/sprawl.png`, `F/p0_a.png`.
- **Volta à base (Q1→Q2, q15–q20): joelhos encostam/arrastam no chão** (médio). Causa: coxa interpola de -83° para 72° passando pela vertical com pés presos. Correção: no retorno, quadro intermediário com salto curto (`apoio ["mao_f","mao_t"]`, `ay 0.4`, `pf [20,-70,40]`), como no burpee.
- **Q2 = agachado com mãos no chão (q22–q26): retorno passa por posição de cócoras que não existe no sprawl** (leve): no sprawl volta-se direto à guarda em pé. Correção: Q2 com tronco 140°, mãos saindo do chão (`apoio ["pe_f","pe_t"]`).
- Mãos abertas na guarda (leve; ver punho fechado acima). Queda e quadril no chão: OK.

### 16. bear-crawl: DEFEITOS
Folhas: `F/bear-crawl.png`, `F/p0_a.png`.
- **Joelho de apoio praticamente no chão (canela paralela ao chão) em quase todo o ciclo** (crítico: o exercício pede joelhos 3–5 cm fora do chão). Causa: `pf [35.4,-88.5,-30]`/`pt [31.3,-105.3,10]` (canela a -88/-105°, horizontal). Correção: canela inclinada (joelho acima do tornozelo): coxas ~80°, canelas ~-45° e pés com dedos apoiados (`pe -100`): ex. `pf [80,-40,-100]`, `pt [70,-50,-100]`; quadril um pouco mais baixo que os ombros (`t 95`).
- **Pé que avança sobe alto atrás (q19–q26: calcanhar à altura do glúteo) em vez de passar rente ao chão** (médio). Causa: `pf [31.3,-105.3,10]`. Correção: perna em balanço `[60,-30,-90]` (pé 3–5 cm acima do chão, à frente).
- Mão e pé opostos: OK.
- **Vista de frente (`F/p90_cardio.png`, última linha): as duas mãos ficam abertas no ar, afastadas para os lados do pedestal; nenhuma toca o aparelho; o pedestal passa entre as pernas** (crítico). Mesma correção (aparelho de trenó com dois postes laterais e `bfa` que leve as mãos até eles).

### 17–21, 28. corrida-leve, tiros, tempo-run, longao, prova: APROVADOS (ressalvas leves); caminhada-corrida: DEFEITOS (médio)
Folhas: `F/corrida-leve.png`, `F/corrida_zoom.png`, `F/tiros.png`, `F/multi_corridas.png`, perfis em `aud3render/c0/`.
- Mecânica de corrida coerente (apoio sob o quadril, voo, braço oposto, inclinação leve do tronco), piso rolante sem patinar, esteira de frente para o console, corrimãos por fora do corpo (x = ±2,6). Loop sem salto.
- caminhada-corrida (leve/médio): a animação mostra só o trote; não há bloco de caminhada. Correção: 6 quadros de caminhada (como `caminhada`) seguidos dos 6 de trote, ou deixar só o trote e aceitar.
- Todas (leve): os seis vídeos são quase idênticos (só muda a amplitude). tiros e prova poderiam ter tronco mais inclinado (t 168) e braço mais amplo; longao/corrida-leve passada mais curta. Mãos totalmente abertas e dedos esticados (leve): na corrida a mão fica semi-fechada (estado 0,4).

### 22–24. bike-leve, bike-intervalado, bike-cadencia: APROVADOS (ressalva leve)
Folhas: `F/bike_zoom.png`, `F/multi_bikes.png`, `F/p0_cardio.png`, `F/p90_cardio.png`.
- Sentado no selim, pés acompanhando o pedivela, joelho levemente flexionado embaixo, joelhos alinhados de frente, mãos no guidão: OK.
- (leve) Mãos espalmadas em cima do guidão, dedos sem envolver a barra: usar estado de pegada 1 quando a mão está no guidão (motor `estado_maos`: bike conta como "ocupada").
- (leve) bike-intervalado deveria mostrar carga maior (tronco mais à frente/fora do selim em parte do ciclo); bike-cadencia OK com ciclo mais rápido.

### 25. eliptico: DEFEITOS
Folhas: `F/eliptico_zoom.png`, `F/multi_bikes.png`, `F/p0_cardio.png`, `F/p90_cardio.png`.
- **Pés andam sobre a base fixa: não há pedais acompanhando os pés** (crítico: o pé "pisa" numa barra parada e escorrega por ela). Causa: `maquina` genérica + motor sem pedais móveis no elíptico. Correção (motor): duas plataformas de pé (2,8 × 1,0) presas a cada pé por quadro (pé sempre apoiado), ligadas a braços que vão até a roda traseira; pé nunca sai da plataforma (apoio contínuo, calcanhar sobe um pouco no fim do ciclo).
- **Mãos abertas ao lado das alças, sem segurá-las** (crítico). Correção: alças móveis presas às pegadas (estado 1) que vão até o eixo da coluna; ou dados com as mãos na altura da alça e `bfa` ≈ 10.
- **Coluna do aparelho passa entre as pernas, com o "console" na altura da virilha** (crítico, vista de frente). Correção: coluna à frente dos pés (y do aparelho ≥ ponta do pé + 1,5) e console na altura do peito (h ≈ 13).

### 26. remo-ergometro: DEFEITOS
Folhas: `F/remo.png`, `F/remo_assento.png`, `F/p0_cardio.png`.
- **Na pegada (catch, Q0/Q3, q0–q5 e q43–q59) o quadril fica ~0,8 unid. acima do assento: a pessoa "senta no ar"** (crítico). Causa: `_assento_remo` mantém o assento em z fixo 1,05 e só acompanha y; o dado sobe o quadril (`y 1.9`) na pegada. Correção: quadril com altura constante (`y` igual em todos os quadros, ~1,5, ísquios sobre o assento) e o motor colocar o assento sob os ísquios (z = ísquio - espessura) e trilho reto.
- Sequência pernas→tronco→braços e retorno inverso: OK. Pés no apoio, cabo saindo do volante: OK.

### 27. escada (stair climber): DEFEITOS
Folhas: `F/escada_zoom.png`, `F/p0_cardio.png`, `F/p90_cardio.png`.
- **Não há degraus: o pé que sobe fica parado no ar sem superfície** (crítico: "apoiado no invisível"). Causa: `maquina` só desenha um pedestal; os pés alternam alturas sem nada embaixo. Correção (motor): aparelho de escada com degraus rotativos (ou pelo menos dois pedais que acompanham cada pé, como o stepper) e corrimãos laterais; o pé alto sempre sobre um degrau.
- **Pedestal entre as pernas (vista de frente), com o topo na altura da virilha** (crítico). Correção: estrutura à frente (console) e corrimãos laterais na altura da cintura.
- Mãos pairando sobre o console sem tocar (leve): apoiar levemente os dedos no corrimão.

### 29. caminhada: APROVADO (ressalva leve)
Folhas: `F/caminhada_zoom.png`, `F/multi_corridas.png`.
- Passada, contato calcanhar-ponta, braços opostos e esteira: OK. (leve) mãos abertas e estendidas; semi-fechar.

### 30. maior-alongamento (world's greatest stretch): APROVADO (leve)
Folhas: `F/maior-alongamento.png`, `F/wgs_zoom.png`.
- Afundo longo, mão no chão por dentro do pé, rotação com braço ao teto e olhar acompanhando, fase de posterior (quadril alto, q122–q134): OK.
- (leve) joelho de trás quase no chão em Q0–Q3; no WGS ele fica alto: `pt [-28,-100,-22]` → `[-35,-75,-60]` com dedos apoiados.

### 31. gato-camelo: APROVADO (leve)
Folha: `F/gato_zoom.png`. Flexão (gato) clara; (leve) extensão (camelo, q33–q66) pouco visível: `cfl -20` → `-30`, `pel 14` → `20`, cabeça `c 150` → `160`.

### 32. postura-crianca: APROVADO
Folha: `F/crianca_zoom.png`. Sentado nos calcanhares, braços estendidos no tapete, entrada e saída suaves.

### 33. flexor-quadril: APROVADO (leve)
Folha: `F/flexor-quadril.png`. Joelho de trás e dorso do pé no tapete, mão da frente sobre o joelho, braço do lado alongado acima da cabeça. (leve) avanço do quadril pequeno (x 1,6–1,9): usar `x 2.4` e `pel -8` (retroversão = glúteo contraído).

### 34. alongamento-posterior: APROVADO
Folha: `F/multi_mob1.png`. Perna da frente estendida com calcanhar no chão, dobradiça de quadril com coluna neutra, mãos na coxa.

### 35. alongamento-quadriceps: DEFEITOS
Folhas: `F/alongamento-quadriceps.png`, `F/quad_mao.png`.
- **A mão NÃO segura o pé: pé encostado no glúteo e a mão pendurada ao lado, aberta, ~15 cm longe do tornozelo** (crítico, q34–q95). Causa: `bf [-27.6,-11]` / `[-34,-6.9]` não alcança o tornozelo e não há IK de pegada no pé. Correção: braço para trás e para baixo até o dorso do pé: `bf [-30, -60]`, `bfa 12`, `afa 20` (conferir na prévia que `mao_f` coincide com `tornozelo_f`); motor: opção `"segura": {"mao_f": "pe_f"}` que faça IK da pegada até o tornozelo e feche os dedos (estado 1).
- Braço livre aberto para o lado como equilíbrio (`bta 42`): OK.

### 36. alongamento-panturrilha: APROVADO
Folha: `F/multi_mob1.png`. Mãos na espaldar/parede, perna de trás estendida com calcanhar no chão, perna da frente flexionada. (leve) o aparelho é um espaldar de madeira; a dica fala em parede (aceitável).

### 37. circulos-braco: APROVADO (leve)
Folha: `F/circulos-braco.png`. Círculos amplos e contínuos, sem salto no loop. (leve) os braços passam junto ao quadril (bf 0 com `bfa 66`); o exercício pede braços abertos na linha dos ombros e círculos de pequeno a grande: manter `bfa 85–90` e variar `bf` 70↔110 (círculos menores).

### 38. circulos-quadril: DEFEITOS
Folhas: `F/quadril_zoom.png`, `F/multi_mob2.png`.
- **Mãos não ficam na cintura: a mão da frente desliza para a frente do short (virilha) em q20–q32 e a de trás fica no ar atrás do quadril** (médio). Causa: braços em FK (`bf [-35,35]`, `afa -40`) enquanto a pelve se desloca e o tronco inclina. Correção (motor/dado): mãos com IK presas às cristas ilíacas (alvo = quadril ± largura da pelve), ou ajustar `bf [-20,60]`, `bfa 50`, `afa -60` em todos os quadros.
- **Círculo do quadril pequeno, quase só inclinação do tronco** (médio). Correção: usar `z` ±0,6 (lado) e `x` ±0,5 (frente/trás) no quadril com pés fixos, em vez de `t` 186/173.

### 39. rolo-quadriceps: DEFEITOS
Folhas: `F/rolo_quad_zoom.png`, `F/p0_rolos.png`.
- **Amplitude de rolagem de só ~15 cm (x 2,0 → 3,45), o rolo fica sempre perto do quadril; não vai até o joelho** (médio). Correção: `x` 1,0 → 4,6 (o rolo percorre a coxa do quadril ao joelho), tempos 2,4/2,4.
- (leve) apoio nas mãos com cotovelos dobrados; a dica pede antebraços no chão: `bf [-3,90]` → `bf [0, 90]` com cotovelo no chão (`apoio` nos antebraços, motor precisa aceitar antebraço como apoio).
- (leve) o rolo não gira enquanto o corpo passa por cima (motor: girar o cilindro pelo deslocamento/raio).

### 40. rolo-panturrilha: DEFEITOS
Folhas: `F/rolo_pant_zoom.png`, `F/p0_rolos.png`.
- **Amplitude de ~15 cm: o rolo fica sempre sob o tornozelo/terço baixo da panturrilha** (médio). Correção: `x` 0 → 3,2 (rolo do tornozelo ao joelho).
- (leve) sem a variação "perna cruzada por cima". Mãos no chão atrás, quadril elevado: OK.

### 41. rolo-it: DEFEITOS
Folhas: `F/rolo_it_zoom.png`, `F/p0_rolos.png`.
- **Perna de cima esticada e levantada no ar (~30° acima do chão), sem apoio** (crítico: a dica pede a perna de cima cruzada à frente com o pé no chão para dosar a pressão). Causa: `pf [-40,-44,-10]` com `pfa -30` (com `rol 90`, "pfa" negativo levanta a perna). Correção: perna de cima flexionada e cruzada à frente, pé plantado: `pf [60,-20,-90]`, `pfa 10`, `apoio ["mao_t","pe_f"]`.
- **Pé de baixo apoiado no chão como se fosse a base, enquanto o rolo está sob o quadril/coxa** (médio): no IT a perna de baixo fica estendida sobre o rolo, pé solto. Correção: `pt [-85,-85,-10]` sem apoio.
- Amplitude de rolagem 9 cm (x 2,0 → 2,9) (médio): `x` 1,0 → 4,0.

### 42. alongamento-peito: APROVADO (leve)
Folha: `F/peito_zoom.png`. Braço a 90/90 no batente e giro do tronco para o lado oposto: OK. (leve) só a palma toca o batente; o antebraço deveria encostar ao longo do batente (`bta 98` → `bta 90` e x do corpo 0,3 mais perto da parede).

### 43. rotacao-toracica: DEFEITOS
Folhas: `F/rot_tor_zoom.png`, `F/p0_mobA.png`, `F/p90_mobA.png`.
- **Corpo flutuando acima do tapete, sustentado só pelo braço de baixo esticado verticalmente; pernas e quadril no ar** (crítico, todo o vídeo). Causa: `rol 90` + `bt [0,0]` (braço "para baixo" no referencial do corpo vira pilar até o chão) e o apoio automático pega a mão como ponto mais baixo. Correção: deitado de lado de verdade: cabeça e ombro de baixo no tapete, braço de baixo estendido à frente no chão (`bt [90,90]`, `bta 0`), quadril e joelhos 90/90 empilhados no chão (`pf [90,0,90]`, `pt [92,2,90]`), `apoio` com quadril/joelhos, e usar `y` explícito para o tronco encostar no tapete.
- **Pelve e pernas giram junto com o tronco** (médio): na rotação torácica os joelhos ficam empilhados. Correção: `tr` só nas vértebras torácicas (motor) ou `trp` = -tr·0,2.
- Braço de cima abrindo com o olhar acompanhando: OK.

### 44. alongamento-adutores (borboleta): DEFEITOS
Folha: `F/adut_zoom.png`.
- **Mãos penduradas no ar ao lado dos pés, sem segurá-los** (médio): na borboleta as mãos seguram os pés/tornozelos. Correção: `bf [20,60]`, `bfa -10` (mãos convergem nos pés), com IK de pegada nos pés.
- **Joelho da frente deformado: a malha dobra num "nó" branco (q0–q66)** (médio). Causa: skin do joelho com `cfa -74/-78` (abdução da canela muito diferente da coxa → torção do joelho). Correção: reduzir para `cfa -50`, `pfa 60` e usar rotação externa do quadril em vez de abdução da canela (motor).
- Coluna alta e inclinação leve: OK.

### 45. equilibrio-unipodal: APROVADO
Folha: `F/multi_mob3.png`. Apoio em uma perna, joelho levemente flexionado, braços equilibrando, micro-oscilação.

### 46. balanco-pernas: DEFEITOS
Folha: `F/balanco_zoom.png`.
- **A mão de apoio fica estendida no ar, sem parede** (médio): o braço está na pose de "mão na parede" mas não há parede. Correção: prop `{"tipo":"parede","mao":"t"}` (como no alongamento-peito) com a palma encostada, ou `bt` caído ao lado.
- Balanço frente/trás e lateral cruzando: OK. Tronco ereto: OK.

### 47. circulos-tornozelo: DEFEITOS (leve)
Folha: `F/tornozelo_zoom.png`.
- (leve) Q0 (q0): ponta do pé atravessa o chão ~1 cm com o pé em flexão plantar (`pf [42,12,42]`). Correção: `y` da perna ou `pe 50`, ou o motor aplicar `sem_atravessar` ao pé livre.
- Círculos, mãos na cintura e apoio unipodal: OK.

### 48. circulos-punho: DEFEITOS
Folhas: `F/punho_zoom.png`, `F/multi_mob4.png`.
- **O punho não gira: quem se move é o antebraço inteiro (o cotovelo flexiona 54°→86° e o antebraço abduz), parecendo "abanar" os braços** (crítico: o movimento não existe no exercício). Causa: dados variam `bf[1]` 76–108 e `afa` -22–10; o motor não tem controle de punho. Correção (motor): campos `"puf"/"put"` (flexão/extensão do punho) e `"pud"` (desvio radial/ulnar) aplicados ao osso `wrist`; dados com antebraço parado (`bf [22,100]`) e o punho fazendo flexão→desvio radial→extensão→desvio ulnar (±60°/±25°), mãos fechadas ou dedos entrelaçados.

### 49. circulos-ombro: DEFEITOS
Folha: `F/multi_mob4.png`.
- **Só sobe e desce os ombros (`oe`), sem ir para trás/para frente: não é um círculo** (médio). Correção: acrescentar `pro`: Q0 `pro 0.5`, Q1 `oe 0.7, pro 0`, Q2 `pro -0.7`, Q3 `oe 0, pro 0`; braços parados (`bf` ±1°).
- Câmera em 3/4 esconde a retração: `cam 20`.

### 50. circulos-joelho: DEFEITOS
Folha: `F/joelho_zoom.png`.
- **Só a mão da frente toca o joelho; a mão de trás fica pendurada no ar ao lado da canela** (médio). Causa: `bt [-8.7,-8.1]` não alcança o joelho de trás. Correção: IK das duas mãos até as patelas, ou `bt [-15,-5]`, `bta -8`. Os joelhos devem estar juntos (pés juntos), círculos pequenos: OK.

### 51. chute-gluteo: APROVADO
Folha: `F/multi_mob4.png`. Calcanhar ao glúteo alternado, tronco alto, ritmo leve.

### 52. carioca: DEFEITOS
Folhas: `F/carioca_zoom.png`, `F/multi_mob4.png`.
- **Sem deslocamento lateral: o corpo cruza as pernas no lugar** (médio: o exercício é deslocar-se de lado). Correção: `z` crescente por quadro (0, 0,8, 1,6, 2,4) com retorno, ou piso rolante lateral (`rolar` no eixo z, motor).
- (leve) braços abertos a 55° rígidos; normal é braços soltos para equilíbrio (`bfa 30`).
- Cruzamento pela frente/por trás e giro do quadril (`trp`): OK.

### 53. abertura-peito-dinamica: APROVADO
Folha: `F/multi_mob4.png`. Braços à frente na altura dos ombros abrindo até atrás do plano frontal (`bfa 108`).

### 54. spider: APROVADO
Folha: `F/spider_zoom.png`. Pé ao lado da mão, quadril afundado, rotação com braço ao teto, apoio firme na mão de baixo.

### 55. alongamento-gluteo (figura 4): DEFEITOS
Folhas: `F/gluteo_zoom.png`, `F/p0_mobA.png`, `F/p90_mobA.png`.
- **As mãos não puxam a perna: abertas no ar, longe da coxa (vista de frente: braços abertos para os lados)** (crítico). Correção: mãos entrelaçadas atrás da coxa da perna de baixo: `bf/bt [140, 175]`, `bfa/bta -15` e IK das pegadas até a coxa `pt` (meio do fêmur).
- **Transição Q0→Q1: a perna cruzada sobe esticada na vertical (q20–q40) em vez de o tornozelo pousar sobre o joelho oposto** (médio). Causa: `pf [178,172,150]`. Correção: Q1 com `pf [130,40,150]`, `pfa 45`, `cfa -60`, tornozelo encostado na coxa logo acima do joelho de `pt [140,-20]`.
- (leve) Q3→Q0 as pernas se atravessam (q137).

### 56. abraco-joelhos: DEFEITOS
Folhas: `F/abraco_zoom.png`, `F/p0_mobA.png`, `F/p90_mobA.png`.
- **Não há abraço: os braços ficam abertos para cima e para os lados (vista de frente em "V"), mãos no ar, longe dos joelhos** (crítico). Causa: `bf [98.2,183.6]` (antebraço apontando para cima) e `bfa 28`. Correção: braços envolvendo as canelas logo abaixo dos joelhos: `bf [130,100]`, `bt [128,98]`, `bfa/bta -10`, `afa/ata -30` (mãos se encontram por cima das canelas); IK das mãos até as canelas.
- **Canelas apontando para cima (pés acima dos joelhos)** (médio): no abraço os joelhos vêm ao peito com as canelas quase horizontais. Correção: `pf [228,140,170]`, `pt [226,138,170]`.
- Balanço lateral (`rol` ±14): OK.

### 57. alongamento-triceps: DEFEITOS
Folhas: `F/triceps_zoom.png`, `F/p0_mobA.png`, `F/p90_mobA.png`.
- **A mão que empurra fica acima do cotovelo com os dedos para cima, no ar, sem encostar no cotovelo** (médio, q32–q97). Causa: `bt [140,-127]`, `bta -37`. Correção: palma sobre o cotovelo do braço alongado (IK da mão auxiliar até o olécrano), ex. `bt [150,-150]`, `bta -60`.
- Braço alongado com cotovelo para cima e mão atrás da cabeça: OK.

### 58. alongamento-antebraco: DEFEITOS
Folha: `F/antebraco_zoom.png`.
- **Dedos apontam para a frente, não para os joelhos** (médio): o alongamento pede dedos virados para você (supinação/rotação externa da mão 180°). Causa: `mao_apoiada_rot` sempre põe os dedos à frente. Correção (motor): campo `"dedos": "tras"` por animação/quadro para girar a mão apoiada 180° em torno da vertical; segunda metade com o dorso da mão no chão.
- Quadril indo para trás com braços estendidos: OK.

### 59. alongamento-pescoco: APROVADO (leve)
Folha: `F/pescoco_zoom.png`. Inclinação lateral sem rotação, ombros relaxados, dois lados. (leve) `destaque: ["tronco"]` pinta o abdome; deveria destacar pescoço/trapézio.

### 60. alongamento-lateral: APROVADO
Folha: `F/multi_mob6.png`. Braço acima da cabeça, inclinação para o lado oposto, mão livre na cintura, dois lados.

### 61. torcao-coluna: DEFEITOS
Folhas: `F/torcao_zoom.png`, `F/multi_mob6.png`.
- **Perna não cruza sobre a outra: o pé da perna flexionada fica por dentro, ao lado do joelho da perna estendida** (médio). Correção: `pfa -14` → `pfa -30` e pé do lado de fora do joelho oposto (`cfa 10`).
- **Mão da frente solta no ar diante do peito, sem abraçar/empurrar o joelho; mão de trás no ar ao lado, não apoiada no chão atrás do quadril** (médio). Correção: cotovelo por fora do joelho flexionado (`bt [80,150]` com IK ao joelho) e mão de trás espalmada no chão atrás (`bf [-30,-30]`, `bfa 10`, `apoio ["mao_f"]`).
- Rotação do tronco e da cabeça: OK.

### 62. alongamento-dorsal: APROVADO (leve)
Folha: `F/multi_mob6.png`. Braços à frente, quadril para trás, costas arredondadas. (leve) dedos não entrelaçados (mãos lado a lado): `bfa/bta -12` para as mãos se tocarem.

### 63. moinho: APROVADO (leve)
Folha: `F/moinho_zoom.png`. Rotação com mão ao pé oposto e braço oposto ao teto, alternando. (leve) no 2º lado (q67) a mão para no meio da canela; aumentar `t` 108 → 100 nesse quadro.
