# Animador — rodada pós-revisão (dados dos reprovados na revisão visual)

Entrada: `pesquisa/revisao-independente.md` (19 reprovados; 10 resolvidos antes no motor, ver a seção "Rodada pós-revisão" de
`pesquisa/motor-pendencias.md`) e o QA novo (88 limpos, 86 avisos, 1 erro). Só dados mudaram (`tools/anim/dados/lote1.json`,
`lote2.json`, `lote3.json`); o motor (`tools/anim3d/*.py`) ficou como estava. Um commit e push por exercício.

Método: para cada exercício, tira de 6 quadros (`humano.py --tira 6`) e corpo inteiro de outro ângulo (`zoom2.py --daz`),
zoom das mãos de 2–4 ângulos, antes e depois; QA (`qa.py`) do exercício a cada variante. Sondas no scratchpad (`<scratch>/pr/`):
`sonda.py` (juntas e altura mínima de cada região), `smao.py` (mão com "segura": distância palma–alvo, ângulo da palma, dedos x
canela/pé), `pencab.py` (quanto a mão entra na cabeça), `fkcab.py`/`grade_cab*.py` (direção da palma FK em relação à cabeça),
`cotov.py` (flexão do cotovelo renderizada), `lote_sonda*.py` (muitas variantes de uma chave num processo só), `v.sh`/`zz.sh`
(render antes/depois), `qa1.sh`. Imagens antes/depois: `<scratch>/pr/<tag>.jpg` (tag0 = antes) e `zm_<tag>*.jpg`.

## O que mudou

| Exercício | Defeito (revisão) | Mudança nos dados | QA antes → depois |
|---|---|---|---|
| prancha-lateral | apoiado num punho fechado, antebraço "vertical" | O antebraço já estava deitado no chão (cotovelo 0,5 dm, pele 1 cm), mas apontava para a câmera (cam 90) e o punho fechado parecia o apoio. Tirado `"maos": {"t": "punho"}`, mão de baixo em `apoio` (espalmada no chão, 0,7 cm), câmera 100 / elevação 30: antebraço e mão deitados aparecem inteiros | aviso (3) → aviso (os mesmos 3) |
| torcao-coluna | mão que segura o joelho aberta, flutuando | `"segura": {"mao_t": "joelho_f"}` em todas as chaves (com rampa de entrada o punho passava de 62° de desvio ulnar, erro); braço de trás `bt` [50,80] `bta` −60 `ata` −90 (abraça o joelho por fora); joelho 1,2 dm mais à frente (`pf` [128,36,90]; com o joelho colado ao peito a palma ia parar no peitoral); torção 6° menor | aviso (8) → aviso (6): sumiram flexão do quadril 157°, congelado e mão flutuando |
| arnold | halter atravessa o rosto no início | Não havia penetração (QA de penetração limpo): na câmera 75 o halter de trás passava na frente dos olhos. Início com as mãos na altura do queixo e mais abertas (`bf` [38,168] `bfa` 28; chaves 1 e 5 [62,176] `bfa` 36): mãos a ±3,2 dm do centro (antes ±2,4) e 1 dm mais baixas | ok → ok |
| arremesso-rotacional | bola entra no quadril na carga | Na carga os braços iam para trás do corpo e a bola ficava colada ao quadril do lado da câmera, com o antebraço de trás atravessando o tronco. Braços à frente do peito girado (`bf` [30,50] `bt` [32,52] `bfa` −5 `bta` 5, `tr` −50): a bola fica ~4 dm à frente do quadril de trás | aviso (6) → aviso (2: braço/antebraço de trás no flanco na transição, já existia) |
| abdominal-bicicleta | mão aberta entra no crânio | Punho em extensão (`puf`/`put` −68) em todas as chaves: a mão chega quase tangente à cabeça e o giro de 75 % do "segura" não enfia os dedos no crânio (penetração medida 4,9 → 1,9 cm) | aviso (4) → aviso (2: desvio ulnar já existente) |
| isometria-pescoco | mão aberta entra no crânio | A palma ia para o topo da cabeça com os dedos para cima. Cotovelo para o lado e antebraço cruzando para a testa (`bf` [148,160] `bfa` 40 `afa` −55 nas chaves 2–4; aproximação [90,130] `bfa` 30): palma deitada na testa, dedos sobre a linha do cabelo; câmera 30 → 85 (de frente) | aviso (congelado) → aviso (congelado) |
| alongamento-quadriceps | mão espalmada no pé, não agarra | Alvo `tornozelo_f` (antes `pe_f`, palma no dorso com os dedos ao longo do pé) e braço `bf` [−40,−40] `bfa` 30 `afa` 20, escolhido numa busca de 81 variantes (palma a 8° do alvo, dedos atravessando o tornozelo): os dedos curvam em volta do tornozelo. Dedos perpendiculares à canela exigiam rotação interna do ombro de 107–135° (erro) | aviso (1) → **limpo** |
| alongamento-adutores | não se lê como borboleta (de cócoras) | Recoreografada: sem `apoio` o corpo assentava pelos pés (pelve 18 cm no ar). Agora `apoio` [gluteo, pe_f, pe_t], coxas `pf` [105] `pfa` 52 (joelhos abertos), canelas para dentro e para trás (`pf[1]` −30, `cfa` −75: tornozelos a 1,3 dm um do outro, 2,5 dm à frente do quadril), mãos sobre os pés (`segura` pés, braços com `bfa` 25 `afa` −30, dedos sobre os dedos dos pés sem passar do chão); tronco ereto → inclina 14–21° | aviso (congelado) → aviso (rotação externa do quadril 75°; joelhos e antebraços "pousados" no ar) |
| fuga-quadril | não se lê como fuga de quadril | Recoreografada como o shrimp do jiu-jitsu num lado: deitado de lado o ciclo todo (`rol` 85, `apoio` [lado, pe_f]), corpo estendido com o pé de cima plantado → "camarão" (quadril para trás, flexão 80–100°, tronco enrolado, `x` −1,4) com os braços estendidos empurrando para os joelhos; câmera de cima (`cam` −90, `cam_el` 55) mostra o C | ok → aviso (pernas encostando 5,4 cm em 12 quadros da transição) |
| remada-invertida | (QA) cotovelo renderizado 48 % da amplitude dos dados | Era dado: na chave de baixo (`t` −109) o corpo ficava alto demais para os braços esticarem (cotovelo 45° no fundo, dados 10°). Fundo mais baixo (`t` −100, `c` −86, pernas na mesma linha): cotovelo renderizado 92° → 33° | aviso (10) → aviso (2: rotação interna do ombro 93°) |

Turkish-getup (item 9) não foi mexido: o orçamento acabou nas recoreografias da borboleta e da fuga de quadril; segue o único
erro do QA (aprovado visualmente).

## Tentado e descartado
- Bicicleta: alvo "cabeca" no lugar de "nuca" (sem o polo do cotovelo para fora: rotação externa do ombro 175°, erro); braços
  com o antebraço paralelo à cabeça (não existe com a palma do lado da cabeça e o cotovelo aberto); só ângulos de braço (abC–abE).
- Isometria: `afa` −70 (supinação 111°, aviso novo) e `bfa` 55 (supinação 126°, erro).
- Borboleta: coxas mais abertas (`pfa` 60–62) e canelas mais para dentro (`cfa` −78 a −85): rotação externa 82–90° (erro), mãos
  abaixo do chão com o tronco inclinado.
- Fuga de quadril alternando os lados passando de costas (como era): as chaves de lado ficam com o quadril 1,3 dm no ar (o
  motor só nivela ombro e quadril quando todas as chaves são "lado") e o QA dá centro de massa fora da base (erro).
- Remada-invertida: mudar os ângulos do braço da chave de baixo tira as mãos da barra (6 cm, erro).

## Para o motor (registrado em motor-pendencias.md, "Rodada pós-revisão (animador, dados)")
"segura" na cabeça/nuca põe a palma até 2–7 cm dentro do crânio conforme o lado (raio da pele estimado só com pontos a menos
de 1 dm) e gira a mão só 75 %; "segura" fecha a mão sempre em 0,55 (tornozelo/punho finos poderiam fechar); o pé não gira em
torno da canela (sem solas unidas); `nivelar_de_lado` só com todas as chaves "lado"; pegada da barra fixa depende do braço FK.

## QA dos 175
qa.py completo (4 processos, 24 fps; refeito depois de o container reiniciar no meio da primeira rodada):
**88 limpos, 86 só com aviso, 1 com erro (turkish-getup)** — mesmas contagens de antes (88 / 86 / 1). Comparação exercício a
exercício com o `pesquisa/qa-resultado.json` anterior (fdc1fa3): mudaram só os da rodada, nenhum outro exercício e nenhuma
regressão para erro:
- alongamento-quadriceps aviso → limpo; fuga-quadril limpo → aviso (pernas encostando na transição; antes estava limpo mas era
  irreconhecível).
- avisos a menos: remada-invertida 10 → 2, arremesso-rotacional 6 → 2, abdominal-bicicleta 4 → 2, torcao-coluna 8 → 6.
- avisos a mais: alongamento-adutores 1 → 6 (rotação externa do quadril 75°, joelhos/antebraços "pousados" no ar: próprios da
  borboleta sentada; antes era a pose de cócoras).
- prancha-lateral, arnold e isometria-pescoco: mesmos achados.
Relatório: `pesquisa/qa-resultado.md` / `.json`.
