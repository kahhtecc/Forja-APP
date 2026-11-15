# Pegadas: dedos flexionando para a palma (correção da hiperextensão)

Entrada: achado em aberto de `pesquisa/aprimoramento-final.md` / `motor-pendencias.md` ("dedos fecham para o dorso nas
pegadas") e QA dos 175 de 043c19d (94 limpos, 80 avisos, 1 erro). Scratch: `<scratch>/dd/` (`PROGRESSO.md`, sondas, close-ups).

## 1. O defeito (reproduzido)
O eixo de flexão das falanges (`_preparar_maos`) levava a ponta do dedo para o lado do DORSO com ângulo positivo, e as
pegadas eram calibradas nesse sentido. De longe a mão "fechava" em volta do cabo, mas de perto era uma mão em
hiperextensão: unhas para dentro do cabo, palma para fora, nós dos dedos abertos para trás — a "mão que não segura".
Também valia para a corrida (estado "semi" 0,45) e para o punho fechado das lutas (1,6).

Sonda `<scratch>/dd/sonda_flex.py` (ângulo de cada articulação no plano da falange-pai, + = para a palma), mão esquerda:

| Estado | Indicador (MCP/PIP/DIP) | Médio | Anelar | Mínimo |
|---|---|---|---|---|
| relaxada (0) | 7 / 15 / 24 | 10 / 12 / 22 | 7 / 11 / 21 | 12 / 18 / 20 |
| pegada (1,0), antes | **−39 / −51 / −16** | **−55 / −86 / −40** | **−57 / −86 / −42** | **−30 / −45 / −18** |
| punho (1,6), antes | −65 / −81 / −47 | −68 / −93 / −52 | −70 / −93 / −54 | −67 / −89 / −62 |
| pegada (1,0), depois | 41 / 52 / 44 | 61 / 61 / 51 | 60 / 63 / 51 | 47 / 52 / 41 |
| punho (1,6), depois | 69 / 78 / 59 | 82 / 77 / 61 | 81 / 79 / 61 | 81 / 80 / 56 |

Close-ups antes (motor de 043c19d, 4 ângulos x 2 instantes): `<scratch>/dd/antes_barra-fixa.jpg`,
`antes_rosca-halteres.jpg`, `antes_supino-reto.jpg`, `antes_puxada-frente.jpg`, `antes_remada-baixa.jpg`.

## 2. O que mudou no motor (humano.py / aparelhos.py)
1. **Flexão anatômica** (`dedo`, `_angs_novo`, `_curvar`): estados > 0 (semifechada, pegada, punho) flexionam MCP, PIP e
   DIP para a palma; os estados ≤ 0 (relaxada, aberta, espalmada) ficaram idênticos. A calibração da pegada por raio
   (`_calibrar_pegada`) é refeita no sentido novo: o centro do túnel (centro da pegada, `off_peg`) passa para o lado da
   palma, então o cabo fica NA palma e os dedos passam por cima dele (pegada pronada na barra fixa: palma para a frente
   encostada na barra, dedos por cima, nós dos dedos para trás).
2. **Palma no cabo**: a pele dos metacarpos não entra no cabo além de `COMPRESSAO_PALMA` (7 mm, partes moles); o centro da
   pegada se afasta da palma o que faltar e médio/anelar fecham de novo até encostar.
3. **Polegar em oposição** (`_quats_polegar`, `POLEGAR_PEG`, `POLEGAR_PUNHO`): base girada para a palma (vetor de rotação no
   referencial da mão) e MCP/IP fechando até a ponta passar para o lado oposto do cabo, sobre o indicador. A tabela vem de
   `_calibrar_polegar` (Nelder-Mead por raio: contato com o cabo sem atravessá-lo, ângulo da ponta em volta do cabo = o da
   falange média do indicador, sem entrar nos dedos, família de solução única entre os raios). Recalibrar:
   `python <scratch>/dd/cal_pol.py` e copiar a saída para as tabelas.
4. **Punho fechado** (`CURVA["punho_anat"]` 63/72/50°): com 88/100/70 as pontas atravessavam a palma e saíam no dorso da
   mão deste modelo (sonda `<scratch>/dd/sonda_punho.py`).
5. **"segura" inalterado**: continua com o sentido legado como base (`legado=True`), só a mistura fora do contato parte do
   estado novo da mão (sem salto na transição).
6. **Consequências da mão do outro lado do cabo** (o punho fica uns 4–5 cm em outro lugar em relação ao implemento):
   - barra nas costas (agachamento-barra): punho estendido 35° (`_estender_punho`), a barra na base da palma — sem isso a
     rotação externa do ombro ia de 108° para 122° (erro);
   - kettlebell de uma mão (terra-uma-perna): o sino não entra na coxa (`kettlebell_fora_do_corpo`, como os halteres);
   - triângulo do cabo (remada-baixa, puxada-triangulo): vem até as mãos ao longo do cabo quando os braços esticados não
     alcançam (1,7 cm fora do túnel), pegadores de 1,4 dm (a mão fechada encostava nas hastes) e perpendiculares aos
     antebraços (desvio radial 30°);
   - paralelas: mãos presas no x fixo dos tubos (o motor usava o x da pegada e o desenho outro: 3,4 cm fora do túnel);
   - pallof: sentido do pegador único fixo (o automático virava no meio do movimento: pop de 4,3 cm).
7. **Outros ajustes de geometria**: corrimão da esteira em ±2,85 dm (a mão do balanço encostava nele), cabo do crossover
   preso no ápice do pegador D (saía de dentro do punho), corda de pular saindo da ponta da manopla, elástico sob os pés
   contornando também o antebraço; com o cabo cruzando a palma no sentido da pegada aberta (desvio radial), mínimo e anelar
   abrem a MCP (a falange média do mínimo entrava 1,6 cm na barra fixa). Testados e desfeitos: limitar essa diagonal a 12°
   (desvio radial do punho até 36°), desempate do sentido automático pela palma (não validado nos 175), curva natural para
   a mão semifechada (mãos de apoio do bear-crawl flutuando).
8. **Dados** (cinco exercícios): puxada-frente `cam` 30 → 50 (a barra agora passa na frente das mãos e cobria o rosto),
   roda-abdominal com os joelhos declarados como apoio (ficavam 7 cm no ar), abdominal-polia com o antebraço menos aberto
   na chave 0 (pronação 103° → 89°), desenvolvimento-barra com os cotovelos mais abertos na chave 0 (bfa 17,8 → 22: o
   braço encostava no peito) e educativos-corrida com o braço de trás um pouco aberto (bfa 8).

## 3. QA novo (qa_corpo.py)
- `rom/dedos_hiperext` (toda mão, todo quadro): sinal da flexão de cada falange em relação à normal palmar levada pelo
  osso-pai (polegar: dobra de repouso); extensão além do fisiológico (MCP 30°, PIP 10°, DIP 15°, polegar 20°) > 0 aviso,
  > 15° erro.
- `pegada/palma`: centro do túnel atrás do plano palmar (linha das MCP): > 0,5 cm aviso, > 1 cm erro.
- `pegada/polegar`: ponta do polegar atrás do plano palmar numa pegada: > 0,5 cm aviso, > 1,5 cm erro.
- Validação no motor antigo (cópia de 043c19d com o qa_corpo novo): barra-fixa e rosca-halteres dão erro (hiperextensão
  77°, cabo 2,1 cm do lado do dorso, polegar 0,8 cm atrás), sombra dá erro (83°). No motor novo, nenhum exercício aciona.

## 4. QA dos 175 (antes → depois)
| | Limpos | Só aviso | Com erro | Avisos (total) | Erros (total) |
|---|---|---|---|---|---|
| Antes (043c19d) | 94 | 80 | 1 | 190 | 5 |
| Depois (motor e dados finais, com as 3 verificações novas) | **104** | **70** | **1** | **176** | **5** |

Comparação exercício a exercício com o `qa-resultado.json` anterior (`<scratch>/ap/cmp.py dd4`, saída em
`<scratch>/dd/cmp_dd4.txt`): **nenhuma regressão de status**. De aviso para limpo: barra-fixa, barra-supinada, paralelas,
band-pull-apart, crucifixo-elastico, desenvolvimento-elastico, corrida-leve, tempo-run, stiff, saco-combinacoes. O único
erro continua o turkish-getup (mesmas 5 verificações, dados). As verificações novas não acionam em nenhum exercício.

Rodadas intermediárias que acharam as regressões corrigidas na seção 2 (todas re-verificadas uma a uma e no QA final):
dd1/dd2 (agachamento-barra 122° de rotação externa, terra-uma-perna 1,8 cm, paralelas 3,4 cm, puxada-frente rosto 24 %,
pallof pop 4,3 cm, desenvolvimento-elastico 3,6 cm; e de limpo para aviso: remada-baixa, puxada-triangulo, roda-abdominal,
abdominal-polia, barra-assistida, crossover, corda, caminhada, desenvolvimento-barra) e dd3 (bear-crawl e
educativos-corrida, causados pela curva natural da mão semifechada, desfeita).

## 5. Verificação visual
- Close-ups antes (motor de 043c19d, cópia em `<scratch>/dd/head`) × depois, 4 ângulos × 2 instantes, mão esquerda:
  `<scratch>/dd/ab_fin_bf.jpg` (barra fixa), `ab_fin_rh.jpg` (rosca com halteres), `ab_fin_sr.jpg` (supino com barra),
  `ab_fin_pf.jpg` (puxada com barra no cabo), `ab_fin_rb.jpg` (remada com triângulo), `ab_fin_so.jpg` (punho fechado,
  sombra), `ab_fin_ab.jpg` (barra nas costas). Em todos, antes: dedos dobrados para trás com o cabo do lado das unhas;
  depois: palma contra o cabo, dedos por cima voltando para a palma, nós dos dedos por fora, polegar cruzando o cabo.
- Tiras de 6 quadros (corpo inteiro + mão esquerda de perto, antes/depois) de 24 exercícios: `<scratch>/dd/tira_<id>.jpg`
  — barra-fixa, barra-supinada, paralelas, rosca-halteres, rosca-direta, supino-reto, puxada-frente, remada-baixa,
  remada-curvada, terra, swing, leg-press, triceps-polia, face-pull, crossover, pallof, sombra, agachamento-barra,
  agachamento-frontal, eliptico, caminhada-corrida, roda-abdominal, abdominal-polia, desenvolvimento-elastico.
  Conferidas: pegadas fechadas pelo lado certo em barra, halter, cabo (barra, corda, D, triângulo), pegadores de máquina
  (leg press, elíptico), kettlebell, roda e paralelas; punho fechado; mão de corrida flexionando para a palma. No terra e no
  agachamento com barra a anilha esconde a mão na câmera da tira (conferido no close-up `ab_fin_ab.jpg`).

## 6. Limites que ficaram
- Polegar por tabela calibrada nesta malha (MakeHuman padrão); outra malha de mão exige rodar `_calibrar_polegar` de novo.
  Em cabos grossos (raio ≥ 0,2 dm) o polegar não chega ao lado oposto (fica ao lado do cabo, como na mão real).
- A palma ainda entra até ~0,8 cm no cabo (compressão admitida de 7 mm; a pele do modelo é rígida) e a base do polegar
  até ~1,2 cm na barra fixa com pegada aberta: abaixo do aviso do QA (1,5 cm) e escondido dentro do cabo.
- Sentido automático do cabo (`rot_pegada` com `supinada=None`) segue a linha dos nós da pose livre; quando o cabo fica
  perpendicular a ela o sentido pode virar (resolvido no pallof fixando o sentido; não há desempate geral).
- Mão livre semifechada (corrida, 0,45) pouco curvada (MCP 24–40°), porque usa a curva escalada pelo raio do cabo.
- "segura" (mão no corpo) mantém o polegar na varredura antiga; os dedos já fechavam para a palma.
- Exercícios com câmera que esconde a mão (terra, agachamento com barra) só foram conferidos por close-up.
