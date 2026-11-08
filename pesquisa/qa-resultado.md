# Resultado do QA das animações 3D (pegada, amplitude articular, apoio)

Gerado por `tools/anim3d/qa.py` + `tools/anim3d/qa_relatorio.py` sobre os 175 exercícios. Critérios, limiares e método de validação em `tools/anim3d/qa_corpo.py` e na seção final.

**16 exercícios com erro, 77 só com aviso, 82 limpos.**

## Exercícios com defeito, por tipo

| Tipo | Exercícios com erro | Só aviso |
|---|---|---|
| Pegada | 1 | 6 |
| Amplitude (ROM) | 3 | 29 |
| Apoio / interpenetração | 11 | 57 |
| Motor (pops, skate, chão...) | 6 | 9 |

## Erros por verificação (nº de exercícios)

| Tipo | Verificação | Exercícios |
|---|---|---|
| motor | pop | 25 |
| apoio | base | 10 |
| apoio | pousada | 10 |
| apoio | penetra | 4 |
| apoio | corpo | 1 |
| motor | chao: | 1 |
| motor | skate | 1 |
| pegada | dist | 1 |
| rom | joelho_flexao | 1 |
| rom | ombro_ext_excesso | 1 |
| rom | ombro_re | 1 |
| rom | ombro_ri | 1 |
| rom | quadril_extensao | 1 |
| rom | quadril_re | 1 |

## Os piores (gravidade = soma de valor/limite dos erros, pesada pela duração)

| # | Exercício | Gravidade | Principais erros |
|---|---|---|---|
| 1 | turkish-getup | 58.0 | penetra antebraco_f x kettlebell 6.9 cm; base coxa esq 17.4 cm; base coxa dir 20.6 cm; ombro_ext_excesso ombro dir 37°; pousada costas 6.0 cm |
| 2 | rotacao-toracica | 51.8 | base costas 19.3 cm; pousada pelve 13.2 cm; pousada joelho dir 11.6 cm; pousada antebraço dir 9.6 cm; pousada costas 7.7 cm |
| 3 | inchworm | 32.2 | base joelho dir 10.4 cm; base cabeça 10.0 cm; pop no quadro 33 (8.6 cm, lowerarm01.L); pop no quadro 44 (11.0 cm, lowerarm01.L); pop no quadro 55 (11.8 cm, lowerarm01.L) |
| 4 | alongamento-triceps | 17.3 | ombro_ri ombro dir 180°; ombro_re ombro dir 179°; pop no quadro 26 (6.5 cm, wrist.R); pop no quadro 27 (6.2 cm, wrist.R); pop no quadro 38 (4.3 cm, wrist.R) |
| 5 | afundo-halteres | 16.2 | base joelho dir 11.4 cm; base costas 8.0 cm; base coxa dir 8.1 cm |
| 6 | alongamento-gluteo | 14.9 | quadril_re quadril esq 93°; pop no quadro 58 (4.8 cm, wrist.L); pop no quadro 62 (6.2 cm, wrist.R); pop no quadro 65 (4.6 cm, wrist.R); pop no quadro 68 (5.4 cm, wrist.L) |
| 7 | maior-alongamento | 14.3 | base cabeça 19.6 cm; base joelho dir 13.6 cm |
| 8 | alongamento-quadriceps | 8.0 | pop no quadro 59 (5.9 cm, lowerarm01.L); pop no quadro 61 (4.8 cm, lowerarm01.L); pop no quadro 88 (4.7 cm, lowerarm01.L); pop no quadro 91 (6.0 cm, lowerarm01.L) |
| 9 | alongamento-peito | 8.0 | penetra mao_t x caixa 5.0 cm |
| 10 | balanco-pernas | 5.8 | penetra mao_t x caixa 4.0 cm |
| 11 | supino-inclinado-barra | 4.4 | pousada cabeça 5.5 cm |
| 12 | supino-inclinado | 4.4 | pousada cabeça 5.5 cm |
| 13 | puxada-triangulo | 4.0 | pop no quadro 57 (5.8 cm, wrist.L); pop no quadro 66 (4.1 cm, wrist.L) |
| 14 | remo-ergometro | 2.5 | penetra abdomen x estrutura 1.8 cm |
| 15 | remada-invertida | 2.1 | dist mão esq 2.0 cm |
| 16 | puxada-frente | 2.1 | corpo cabo/elástico x corpo 3.3 cm |
| 17 | agachamento-livre | 0.0 |  |
| 18 | agachamento-elastico | 0.0 |  |
| 19 | agachamento-salto | 0.0 |  |
| 20 | agachamento-goblet | 0.0 |  |
| 21 | agachamento-barra | 0.0 |  |
| 22 | agachamento-frontal | 0.0 |  |
| 23 | leg-press | 0.0 |  |
| 24 | hack | 0.0 |  |
| 25 | cadeira-extensora | 0.0 |  |

## Tabela dos exercícios

Colunas: nº de verificações com erro (e aviso) por tipo; defeitos = os erros mais graves (verificação, parte, valor).

| Exercício | Pegada | ROM | Apoio | Motor | Defeitos |
|---|---|---|---|---|---|
| agachamento-livre | 0 | 0 | 0 | 0 | ok |
| agachamento-elastico | 0 | 0 | 0 | 0 | ok |
| agachamento-salto | 0 | 0 | 0 | 0 | ok |
| agachamento-goblet | 0 | 0 (2) | 0 (1) | 0 | só avisos |
| agachamento-barra | 0 | 0 (2) | 0 | 0 | só avisos |
| agachamento-frontal | 0 | 0 | 0 | 0 | ok |
| leg-press | 0 | 0 | 0 (3) | 0 | só avisos |
| hack | 0 | 0 | 0 (4) | 0 | só avisos |
| cadeira-extensora | 0 | 0 | 0 (3) | 0 | só avisos |
| cadeira-flexora | 0 | 0 | 0 (2) | 0 | só avisos |
| mesa-flexora | 0 | 0 | 0 (6) | 0 | só avisos |
| afundo | 0 | 0 | 0 (1) | 0 | só avisos |
| afundo-halteres | 0 | 0 | **3** | 0 | base joelho dir 11.4 cm; base costas 8.0 cm; base coxa dir 8.1 cm |
| passada-andando | 0 | 0 | 0 | 0 | ok |
| bulgaro | 0 | 0 | 0 (1) | 0 | só avisos |
| step-up | 0 | 0 | 0 (1) | 0 | só avisos |
| terra | 0 (2) | 0 | 0 | 0 | só avisos |
| stiff | 0 (1) | 0 | 0 | 0 | só avisos |
| stiff-halteres | 0 | 0 | 0 | 0 | ok |
| terra-uma-perna | 0 | 0 | 0 (1) | 0 | só avisos |
| ponte-gluteo | 0 | 0 | 0 (2) | 0 (1) | só avisos |
| ponte-unilateral | 0 | 0 | 0 (2) | 0 | só avisos |
| elevacao-quadril | 0 | 0 | 0 (3) | 0 | só avisos |
| coice-gluteo | 0 | 0 | 0 | 0 | ok |
| abdutora | 0 | 0 | 0 (2) | 0 | só avisos |
| monster-walk | 0 | 0 | 0 | 0 | ok |
| panturrilha-pe | 0 | 0 | 0 | 0 | ok |
| panturrilha-sentado | 0 | 0 | 0 | 0 | ok |
| panturrilha-elastico | 0 | 0 | 0 | 0 (1) | só avisos |
| superman | 0 | 0 (1) | 0 (3) | 0 | só avisos |
| hiperextensao | 0 | 0 | 0 (4) | 0 | só avisos |
| prancha | 0 | 0 | 0 (4) | 0 | só avisos |
| prancha-lateral | 0 | 0 | 0 (3) | 0 | só avisos |
| abdominal | 0 | 0 | 0 (2) | 0 | só avisos |
| abdominal-infra | 0 | 0 | 0 (1) | 0 | só avisos |
| dead-bug | 0 | 0 | 0 | 0 | ok |
| mountain-climber | 0 | 0 (4) | 0 | 0 | só avisos |
| russian-twist | 0 | 0 | 0 (4) | 0 | só avisos |
| abdominal-bicicleta | 0 | 0 (3) | 0 | 0 | só avisos |
| elevacao-pernas-barra | 0 | 0 | 0 | 0 | ok |
| roda-abdominal | 0 | 0 | 0 (2) | 0 | só avisos |
| pallof | 0 | 0 | 0 (4) | 0 (1) | só avisos |
| abdominal-polia | 0 | 0 | 0 | 0 | ok |
| canivete | 0 | 0 (1) | 0 | 0 | só avisos |
| box-jump | 0 | 0 | 0 (3) | 0 | só avisos |
| salto-distancia | 0 | 0 | 0 | 0 | ok |
| bound-lateral | 0 | 0 | 0 | 0 | ok |
| salto-tesoura | 0 | 0 | 0 | 0 | ok |
| tuck-jump | 0 | 0 | 0 | 0 | ok |
| arremesso-rotacional | 0 | 0 | 0 (6) | 0 | só avisos |
| ponte-pescoco | 0 | 0 (1) | 0 (1) | 0 | só avisos |
| fuga-quadril | 0 | 0 | 0 | 0 | ok |
| nordico | 0 | 0 | 0 (3) | 0 | só avisos |
| educativos-corrida | 0 | 0 | 0 | 0 | ok |
| bike-subida | 0 | 0 | 0 (4) | 0 | só avisos |
| sentar-levantar | 0 | 0 | 0 | 0 | ok |
| flexao | 0 | 0 | 0 (4) | 0 | só avisos |
| flexao-inclinada | 0 | 0 | 0 | 0 | ok |
| flexao-joelhos | 0 | 0 | 0 (1) | 0 | só avisos |
| flexao-declinada | 0 | 0 | 0 | 0 | ok |
| flexao-diamante | 0 | 0 (4) | 0 (5) | 0 | só avisos |
| flexao-pliometrica | 0 | 0 | 0 | 0 | ok |
| supino-reto | 0 | 0 | 0 | 0 | ok |
| supino-halteres | 0 | 0 | 0 | 0 | ok |
| supino-inclinado | 0 | 0 | **1** | 0 | pousada cabeça 5.5 cm |
| supino-inclinado-barra | 0 | 0 | **1** | 0 | pousada cabeça 5.5 cm |
| supino-maquina | 0 | 0 | 0 | 0 | ok |
| crucifixo | 0 | 0 | 0 | 0 | ok |
| crossover | 0 | 0 | 0 | 0 | ok |
| peck-deck | 0 | 0 | 0 | 0 | ok |
| supino-elastico | 0 | 0 | 0 | 0 | ok |
| crucifixo-elastico | 0 | 0 | 0 (1) | 0 | só avisos |
| paralelas | 0 (4) | 0 | 0 | 0 | só avisos |
| barra-fixa | 0 (2) | 0 | 0 | 0 | só avisos |
| barra-supinada | 0 | 0 (2) | 0 | 0 | só avisos |
| barra-assistida | 0 | 0 | 0 | 0 | ok |
| puxada-frente | 0 | 0 | **1** (1) | 0 | corpo cabo/elástico x corpo 3.3 cm |
| puxada-triangulo | 0 | 0 | 0 | **2** | pop no quadro 57 (5.8 cm, wrist.L); pop no quadro 66 (4.1 cm, wrist.L) |
| remada-baixa | 0 | 0 | 0 | 0 | ok |
| remada-curvada | 0 | 0 | 0 | 0 | ok |
| remada-unilateral | 0 | 0 | 0 | 0 | ok |
| remada-elastico | 0 | 0 | 0 | 0 | ok |
| remada-invertida | **1** (3) | 0 (2) | 0 (4) | 0 | dist mão esq 2.0 cm |
| pulldown-elastico | 0 | 0 | 0 | 0 | ok |
| pullover-polia | 0 | 0 | 0 | 0 | ok |
| face-pull | 0 | 0 | 0 | 0 | ok |
| band-pull-apart | 0 | 0 | 0 (1) | 0 | só avisos |
| encolhimento | 0 | 0 | 0 | 0 | ok |
| desenvolvimento-halteres | 0 | 0 | 0 | 0 | ok |
| desenvolvimento-barra | 0 | 0 | 0 | 0 | ok |
| desenvolvimento-maquina | 0 | 0 | 0 | 0 | ok |
| desenvolvimento-elastico | 0 | 0 | 0 (1) | 0 | só avisos |
| elevacao-lateral | 0 | 0 | 0 | 0 | ok |
| elevacao-lateral-elastico | 0 | 0 | 0 | 0 | ok |
| elevacao-frontal | 0 | 0 | 0 | 0 | ok |
| crucifixo-inverso | 0 | 0 | 0 | 0 | ok |
| arnold | 0 | 0 | 0 | 0 | ok |
| pike-pushup | 0 | 0 | 0 (2) | 0 | só avisos |
| rotacao-externa | 0 | 0 | 0 (1) | 0 | só avisos |
| rosca-direta | 0 | 0 (2) | 0 | 0 | só avisos |
| rosca-halteres | 0 | 0 | 0 | 0 | ok |
| rosca-martelo | 0 | 0 | 0 | 0 | ok |
| rosca-elastico | 0 | 0 | 0 | 0 | ok |
| rosca-scott | 0 | 0 (2) | 0 | 0 | só avisos |
| triceps-polia | 0 | 0 | 0 | 0 | ok |
| triceps-frances | 0 | 0 (2) | 0 | 0 | só avisos |
| triceps-testa | 0 | 0 | 0 | 0 | ok |
| triceps-banco | 0 | 0 (2) | 0 | 0 | só avisos |
| triceps-elastico | 0 | 0 | 0 | 0 | ok |
| triceps-coice | 0 | 0 | 0 | 0 | ok |
| passe-medicine | 0 | 0 | 0 | 0 | ok |
| isometria-pescoco | 0 | 0 | 0 | 0 (1) | só avisos |
| burpee | 0 | 0 | 0 | 0 | ok |
| polichinelo | 0 | 0 | 0 | 0 | ok |
| corda | 0 | 0 | 0 | 0 | ok |
| swing | 0 | 0 | 0 (2) | 0 | só avisos |
| thruster | 0 | 0 | 0 | 0 | ok |
| power-clean | 0 (1) | 0 (2) | 0 (1) | 0 | só avisos |
| arremesso-medicine | 0 | 0 | 0 | 0 | ok |
| battle-rope | 0 | 0 | 0 | 0 | ok |
| farmer-walk | 0 | 0 | 0 | 0 | ok |
| sled-push | 0 | 0 | 0 | 0 | ok |
| turkish-getup | 0 | **3** | **6** | **1** | penetra antebraco_f x kettlebell 6.9 cm; base coxa esq 17.4 cm; base coxa dir 20.6 cm; ombro_ext_excesso ombro dir 37° |
| inchworm | 0 | 0 (2) | **2** | **9** | base joelho dir 10.4 cm; base cabeça 10.0 cm; pop no quadro 33 (8.6 cm, lowerarm01.L); pop no quadro 44 (11.0 cm, lowerarm01.L) |
| sombra | 0 | 0 | 0 | 0 | ok |
| saco-combinacoes | 0 | 0 | 0 (1) | 0 | só avisos |
| sprawl | 0 | 0 | 0 | 0 | ok |
| bear-crawl | 0 | 0 | 0 | 0 | ok |
| corrida-leve | 0 | 0 | 0 (1) | 0 | só avisos |
| caminhada-corrida | 0 | 0 | 0 | 0 | ok |
| tiros | 0 | 0 | 0 | 0 | ok |
| tempo-run | 0 | 0 | 0 (2) | 0 | só avisos |
| longao | 0 | 0 | 0 | 0 | ok |
| bike-leve | 0 | 0 | 0 (2) | 0 | só avisos |
| bike-intervalado | 0 | 0 | 0 (3) | 0 | só avisos |
| bike-cadencia | 0 | 0 | 0 (2) | 0 | só avisos |
| eliptico | 0 (2) | 0 (2) | 0 | 0 | só avisos |
| remo-ergometro | 0 | 0 (2) | **1** (4) | 0 | penetra abdomen x estrutura 1.8 cm |
| escada | 0 | 0 | 0 (3) | 0 | só avisos |
| prova | 0 | 0 | 0 | 0 | ok |
| caminhada | 0 | 0 | 0 | 0 | ok |
| maior-alongamento | 0 | 0 (2) | **2** (1) | 0 | base cabeça 19.6 cm; base joelho dir 13.6 cm |
| gato-camelo | 0 | 0 | 0 | 0 | ok |
| postura-crianca | 0 | 0 (4) | 0 (7) | 0 | só avisos |
| flexor-quadril | 0 | 0 (1) | 0 | 0 | só avisos |
| alongamento-posterior | 0 | 0 | 0 | 0 | ok |
| alongamento-quadriceps | 0 | 0 | 0 | **4** | pop no quadro 59 (5.9 cm, lowerarm01.L); pop no quadro 61 (4.8 cm, lowerarm01.L); pop no quadro 88 (4.7 cm, lowerarm01.L); pop no quadro 91 (6.0 cm, lowerarm01.L) |
| alongamento-panturrilha | 0 | 0 | 0 (4) | 0 | só avisos |
| circulos-braco | 0 | 0 | 0 | 0 | ok |
| circulos-quadril | 0 | 0 | 0 (2) | 0 | só avisos |
| rolo-quadriceps | 0 | 0 | 0 (1) | 0 | só avisos |
| rolo-panturrilha | 0 | 0 | 0 | 0 | ok |
| rolo-it | 0 | 0 | 0 (3) | 0 | só avisos |
| alongamento-peito | 0 | 0 (1) | **1** (1) | 0 (1) | penetra mao_t x caixa 5.0 cm |
| rotacao-toracica | 0 | 0 (3) | **6** | 0 | base costas 19.3 cm; pousada pelve 13.2 cm; pousada joelho dir 11.6 cm; pousada antebraço dir 9.6 cm |
| alongamento-adutores | 0 | 0 | 0 | 0 (1) | só avisos |
| equilibrio-unipodal | 0 | 0 | 0 | 0 | ok |
| balanco-pernas | 0 | 0 (2) | **1** (1) | 0 | penetra mao_t x caixa 4.0 cm |
| circulos-tornozelo | 0 | 0 | 0 (1) | 0 | só avisos |
| circulos-punho | 0 | 0 | 0 | 0 | ok |
| circulos-ombro | 0 | 0 | 0 | 0 | ok |
| circulos-joelho | 0 | 0 (2) | 0 (2) | 0 | só avisos |
| chute-gluteo | 0 | 0 | 0 | 0 | ok |
| carioca | 0 | 0 | 0 | 0 | ok |
| abertura-peito-dinamica | 0 | 0 | 0 | 0 | ok |
| spider | 0 | 0 (1) | 0 | 0 | só avisos |
| alongamento-gluteo | 0 | **1** (3) | 0 (4) | **6** | quadril_re quadril esq 93°; pop no quadro 58 (4.8 cm, wrist.L); pop no quadro 62 (6.2 cm, wrist.R); pop no quadro 65 (4.6 cm, wrist.R) |
| abraco-joelhos | 0 | 0 (2) | 0 | 0 | só avisos |
| alongamento-triceps | 0 | **2** (1) | 0 (4) | **5** | ombro_ri ombro dir 180°; ombro_re ombro dir 179°; pop no quadro 26 (6.5 cm, wrist.R); pop no quadro 27 (6.2 cm, wrist.R) |
| alongamento-antebraco | 0 | 0 (2) | 0 | 0 | só avisos |
| alongamento-pescoco | 0 | 0 | 0 | 0 (1) | só avisos |
| alongamento-lateral | 0 | 0 | 0 (3) | 0 | só avisos |
| torcao-coluna | 0 | 0 (4) | 0 (2) | 0 (2) | só avisos |
| alongamento-dorsal | 0 | 0 | 0 | 0 (1) | só avisos |
| moinho | 0 | 0 | 0 | 0 | ok |
