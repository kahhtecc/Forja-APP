# Resultado do QA das animações 3D (pegada, amplitude articular, apoio)

Gerado por `tools/anim3d/qa.py` + `tools/anim3d/qa_relatorio.py` sobre os 175 exercícios. Critérios, limiares e método de validação em `tools/anim3d/qa_corpo.py` e na seção final.

**1 exercícios com erro, 86 só com aviso, 88 limpos.**

## Exercícios com defeito, por tipo

| Tipo | Exercícios com erro | Só aviso |
|---|---|---|
| Pegada | 0 | 6 |
| Amplitude (ROM) | 1 | 28 |
| Apoio / interpenetração | 1 | 62 |
| Motor (pops, skate, chão...) | 0 | 7 |

## Erros por verificação (nº de exercícios)

| Tipo | Verificação | Exercícios |
|---|---|---|
| apoio | base | 3 |
| apoio | pousada | 2 |
| rom | quadril_extensao | 1 |

## Os piores (gravidade = soma de valor/limite dos erros, pesada pela duração)

| # | Exercício | Gravidade | Principais erros |
|---|---|---|---|
| 1 | turkish-getup | 40.4 | base coxa dir 22.8 cm; base costas 13.4 cm; pousada joelho dir 10.6 cm; base coxa esq 11.5 cm; quadril_extensao quadril dir 42° |
| 2 | agachamento-livre | 0.0 |  |
| 3 | agachamento-barra | 0.0 |  |
| 4 | cadeira-extensora | 0.0 |  |
| 5 | afundo-halteres | 0.0 |  |
| 6 | terra | 0.0 |  |
| 7 | ponte-gluteo | 0.0 |  |
| 8 | abdutora | 0.0 |  |
| 9 | panturrilha-elastico | 0.0 |  |
| 10 | prancha-lateral | 0.0 |  |
| 11 | mountain-climber | 0.0 |  |
| 12 | roda-abdominal | 0.0 |  |
| 13 | box-jump | 0.0 |  |
| 14 | tuck-jump | 0.0 |  |
| 15 | nordico | 0.0 |  |
| 16 | flexao | 0.0 |  |
| 17 | flexao-diamante | 0.0 |  |
| 18 | supino-inclinado | 0.0 |  |
| 19 | crossover | 0.0 |  |
| 20 | paralelas | 0.0 |  |
| 21 | puxada-frente | 0.0 |  |
| 22 | remada-unilateral | 0.0 |  |
| 23 | pullover-polia | 0.0 |  |
| 24 | desenvolvimento-halteres | 0.0 |  |
| 25 | elevacao-lateral | 0.0 |  |

## Tabela dos exercícios

Colunas: nº de verificações com erro (e aviso) por tipo; defeitos = os erros mais graves (verificação, parte, valor).

| Exercício | Pegada | ROM | Apoio | Motor | Defeitos |
|---|---|---|---|---|---|
| agachamento-livre | 0 | 0 | 0 | 0 | ok |
| agachamento-barra | 0 | 0 (2) | 0 | 0 | só avisos |
| cadeira-extensora | 0 | 0 | 0 (1) | 0 | só avisos |
| afundo-halteres | 0 | 0 | 0 | 0 | ok |
| terra | 0 (2) | 0 | 0 | 0 | só avisos |
| ponte-gluteo | 0 | 0 | 0 (2) | 0 (1) | só avisos |
| abdutora | 0 | 0 | 0 (2) | 0 | só avisos |
| panturrilha-elastico | 0 | 0 | 0 | 0 (1) | só avisos |
| prancha-lateral | 0 | 0 | 0 (3) | 0 | só avisos |
| mountain-climber | 0 | 0 (4) | 0 | 0 | só avisos |
| roda-abdominal | 0 | 0 | 0 (2) | 0 | só avisos |
| box-jump | 0 | 0 | 0 (3) | 0 | só avisos |
| tuck-jump | 0 | 0 | 0 | 0 | ok |
| nordico | 0 | 0 | 0 (3) | 0 | só avisos |
| flexao | 0 | 0 | 0 (4) | 0 | só avisos |
| flexao-diamante | 0 | 0 (4) | 0 (5) | 0 | só avisos |
| supino-inclinado | 0 | 0 | 0 | 0 | ok |
| crossover | 0 | 0 | 0 | 0 | ok |
| paralelas | 0 (4) | 0 | 0 | 0 | só avisos |
| puxada-frente | 0 | 0 | 0 (2) | 0 | só avisos |
| remada-unilateral | 0 | 0 | 0 | 0 | ok |
| pullover-polia | 0 | 0 | 0 | 0 | ok |
| desenvolvimento-halteres | 0 | 0 | 0 | 0 | ok |
| elevacao-lateral | 0 | 0 | 0 | 0 | ok |
| arnold | 0 | 0 | 0 | 0 | ok |
| rosca-halteres | 0 | 0 | 0 | 0 | ok |
| triceps-polia | 0 | 0 | 0 | 0 | ok |
| triceps-elastico | 0 | 0 | 0 | 0 | ok |
| burpee | 0 | 0 | 0 | 0 | ok |
| thruster | 0 | 0 | 0 | 0 | ok |
| farmer-walk | 0 | 0 | 0 | 0 | ok |
| sombra | 0 | 0 | 0 | 0 | ok |
| corrida-leve | 0 | 0 | 0 (1) | 0 | só avisos |
| longao | 0 | 0 | 0 | 0 | ok |
| eliptico | 0 (2) | 0 | 0 | 0 | só avisos |
| caminhada | 0 | 0 | 0 | 0 | ok |
| flexor-quadril | 0 | 0 (1) | 0 | 0 | só avisos |
| circulos-braco | 0 | 0 | 0 | 0 | ok |
| rolo-it | 0 | 0 | 0 (1) | 0 | só avisos |
| equilibrio-unipodal | 0 | 0 | 0 | 0 | ok |
| circulos-ombro | 0 | 0 | 0 | 0 | ok |
| abertura-peito-dinamica | 0 | 0 | 0 | 0 | ok |
| alongamento-triceps | 0 | 0 | 0 (2) | 0 | só avisos |
| torcao-coluna | 0 | 0 (4) | 0 (2) | 0 | só avisos |
| agachamento-elastico | 0 | 0 | 0 | 0 | ok |
| agachamento-frontal | 0 | 0 | 0 | 0 | ok |
| cadeira-flexora | 0 | 0 | 0 (2) | 0 | só avisos |
| passada-andando | 0 | 0 | 0 | 0 | ok |
| stiff | 0 (1) | 0 | 0 | 0 | só avisos |
| ponte-unilateral | 0 | 0 | 0 (2) | 0 | só avisos |
| monster-walk | 0 | 0 | 0 | 0 | ok |
| superman | 0 | 0 (1) | 0 (3) | 0 | só avisos |
| abdominal | 0 | 0 | 0 (2) | 0 | só avisos |
| russian-twist | 0 | 0 | 0 (4) | 0 | só avisos |
| pallof | 0 | 0 | 0 (4) | 0 (1) | só avisos |
| salto-distancia | 0 | 0 | 0 | 0 | ok |
| arremesso-rotacional | 0 | 0 | 0 (2) | 0 | só avisos |
| educativos-corrida | 0 | 0 | 0 | 0 | ok |
| flexao-inclinada | 0 | 0 | 0 | 0 | ok |
| flexao-pliometrica | 0 | 0 | 0 | 0 | ok |
| supino-inclinado-barra | 0 | 0 | 0 | 0 | ok |
| peck-deck | 0 | 0 | 0 | 0 | ok |
| barra-fixa | 0 (2) | 0 | 0 | 0 | só avisos |
| puxada-triangulo | 0 | 0 | 0 | 0 | ok |
| remada-elastico | 0 | 0 | 0 | 0 | ok |
| face-pull | 0 | 0 | 0 | 0 | ok |
| desenvolvimento-barra | 0 | 0 | 0 | 0 | ok |
| elevacao-lateral-elastico | 0 | 0 | 0 | 0 | ok |
| pike-pushup | 0 | 0 | 0 (2) | 0 | só avisos |
| rosca-martelo | 0 | 0 | 0 | 0 | ok |
| triceps-frances | 0 | 0 (2) | 0 | 0 | só avisos |
| triceps-coice | 0 | 0 | 0 | 0 | ok |
| polichinelo | 0 | 0 | 0 | 0 | ok |
| power-clean | 0 (1) | 0 (2) | 0 (1) | 0 | só avisos |
| sled-push | 0 | 0 | 0 | 0 | ok |
| saco-combinacoes | 0 | 0 | 0 (1) | 0 | só avisos |
| caminhada-corrida | 0 | 0 | 0 | 0 | ok |
| bike-leve | 0 | 0 | 0 (2) | 0 | só avisos |
| remo-ergometro | 0 | 0 (2) | 0 (2) | 0 | só avisos |
| maior-alongamento | 0 | 0 (2) | 0 (1) | 0 | só avisos |
| alongamento-posterior | 0 | 0 | 0 | 0 | ok |
| circulos-quadril | 0 | 0 | 0 (2) | 0 | só avisos |
| alongamento-peito | 0 | 0 (1) | 0 | 0 (1) | só avisos |
| balanco-pernas | 0 | 0 (2) | 0 (1) | 0 | só avisos |
| circulos-joelho | 0 | 0 | 0 (1) | 0 | só avisos |
| spider | 0 | 0 (1) | 0 | 0 | só avisos |
| alongamento-antebraco | 0 | 0 (2) | 0 | 0 | só avisos |
| alongamento-dorsal | 0 | 0 | 0 | 0 (1) | só avisos |
| agachamento-salto | 0 | 0 | 0 | 0 | ok |
| leg-press | 0 | 0 | 0 (3) | 0 | só avisos |
| mesa-flexora | 0 | 0 | 0 (6) | 0 | só avisos |
| bulgaro | 0 | 0 | 0 (1) | 0 | só avisos |
| stiff-halteres | 0 | 0 | 0 | 0 | ok |
| elevacao-quadril | 0 | 0 | 0 (3) | 0 | só avisos |
| panturrilha-pe | 0 | 0 | 0 | 0 | ok |
| hiperextensao | 0 | 0 | 0 (4) | 0 | só avisos |
| abdominal-infra | 0 | 0 | 0 (1) | 0 | só avisos |
| abdominal-bicicleta | 0 | 0 (2) | 0 | 0 | só avisos |
| abdominal-polia | 0 | 0 | 0 | 0 | ok |
| bound-lateral | 0 | 0 | 0 | 0 | ok |
| ponte-pescoco | 0 | 0 (1) | 0 | 0 | só avisos |
| bike-subida | 0 | 0 | 0 (4) | 0 | só avisos |
| flexao-joelhos | 0 | 0 | 0 (1) | 0 | só avisos |
| supino-reto | 0 | 0 | 0 | 0 | ok |
| supino-maquina | 0 | 0 | 0 | 0 | ok |
| supino-elastico | 0 | 0 | 0 | 0 | ok |
| barra-supinada | 0 | 0 (2) | 0 | 0 | só avisos |
| remada-baixa | 0 | 0 | 0 | 0 | ok |
| remada-invertida | 0 | 0 (2) | 0 | 0 | só avisos |
| band-pull-apart | 0 | 0 | 0 (1) | 0 | só avisos |
| desenvolvimento-maquina | 0 | 0 | 0 | 0 | ok |
| elevacao-frontal | 0 | 0 | 0 | 0 | ok |
| rotacao-externa | 0 | 0 | 0 (1) | 0 | só avisos |
| rosca-elastico | 0 | 0 | 0 | 0 | ok |
| triceps-testa | 0 | 0 | 0 | 0 | ok |
| passe-medicine | 0 | 0 | 0 | 0 | ok |
| corda | 0 | 0 | 0 | 0 | ok |
| arremesso-medicine | 0 | 0 | 0 | 0 | ok |
| turkish-getup | 0 | **1** (2) | **5** | 0 | base coxa dir 22.8 cm; base costas 13.4 cm; pousada joelho dir 10.6 cm; base coxa esq 11.5 cm |
| sprawl | 0 | 0 | 0 | 0 | ok |
| tiros | 0 | 0 | 0 | 0 | ok |
| bike-intervalado | 0 | 0 | 0 (3) | 0 | só avisos |
| escada | 0 | 0 | 0 | 0 | ok |
| gato-camelo | 0 | 0 | 0 | 0 | ok |
| alongamento-quadriceps | 0 | 0 | 0 | 0 | ok |
| rolo-quadriceps | 0 | 0 | 0 (2) | 0 | só avisos |
| rotacao-toracica | 0 | 0 (1) | 0 (4) | 0 | só avisos |
| circulos-tornozelo | 0 | 0 | 0 (1) | 0 | só avisos |
| chute-gluteo | 0 | 0 | 0 | 0 | ok |
| alongamento-gluteo | 0 | 0 (1) | 0 (5) | 0 | só avisos |
| alongamento-pescoco | 0 | 0 | 0 | 0 (1) | só avisos |
| moinho | 0 | 0 | 0 | 0 | ok |
| agachamento-goblet | 0 | 0 (2) | 0 (1) | 0 | só avisos |
| hack | 0 | 0 | 0 (6) | 0 | só avisos |
| afundo | 0 | 0 | 0 (1) | 0 | só avisos |
| step-up | 0 | 0 | 0 (1) | 0 | só avisos |
| terra-uma-perna | 0 | 0 | 0 (1) | 0 | só avisos |
| coice-gluteo | 0 | 0 | 0 | 0 | ok |
| panturrilha-sentado | 0 | 0 | 0 | 0 | ok |
| prancha | 0 | 0 | 0 (4) | 0 | só avisos |
| dead-bug | 0 | 0 | 0 | 0 | ok |
| elevacao-pernas-barra | 0 | 0 | 0 | 0 | ok |
| canivete | 0 | 0 (1) | 0 | 0 | só avisos |
| salto-tesoura | 0 | 0 | 0 | 0 | ok |
| fuga-quadril | 0 | 0 | 0 (1) | 0 | só avisos |
| sentar-levantar | 0 | 0 | 0 | 0 | ok |
| flexao-declinada | 0 | 0 | 0 | 0 | ok |
| supino-halteres | 0 | 0 | 0 | 0 | ok |
| crucifixo | 0 | 0 | 0 | 0 | ok |
| crucifixo-elastico | 0 | 0 | 0 (1) | 0 | só avisos |
| barra-assistida | 0 | 0 | 0 | 0 | ok |
| remada-curvada | 0 | 0 | 0 | 0 | ok |
| pulldown-elastico | 0 | 0 | 0 | 0 | ok |
| encolhimento | 0 | 0 | 0 | 0 | ok |
| desenvolvimento-elastico | 0 | 0 | 0 (1) | 0 | só avisos |
| crucifixo-inverso | 0 | 0 | 0 | 0 | ok |
| rosca-direta | 0 | 0 (2) | 0 | 0 | só avisos |
| rosca-scott | 0 | 0 (2) | 0 (2) | 0 | só avisos |
| triceps-banco | 0 | 0 (2) | 0 | 0 | só avisos |
| isometria-pescoco | 0 | 0 | 0 | 0 (1) | só avisos |
| swing | 0 | 0 | 0 (2) | 0 | só avisos |
| battle-rope | 0 | 0 | 0 | 0 | ok |
| inchworm | 0 | 0 | 0 | 0 | ok |
| bear-crawl | 0 | 0 | 0 | 0 | ok |
| tempo-run | 0 | 0 | 0 (2) | 0 | só avisos |
| bike-cadencia | 0 | 0 | 0 (2) | 0 | só avisos |
| prova | 0 | 0 | 0 | 0 | ok |
| postura-crianca | 0 | 0 (4) | 0 (7) | 0 | só avisos |
| alongamento-panturrilha | 0 | 0 | 0 | 0 | ok |
| rolo-panturrilha | 0 | 0 | 0 (1) | 0 | só avisos |
| alongamento-adutores | 0 | 0 (2) | 0 (4) | 0 | só avisos |
| circulos-punho | 0 | 0 | 0 | 0 | ok |
| carioca | 0 | 0 | 0 | 0 | ok |
| abraco-joelhos | 0 | 0 (4) | 0 | 0 | só avisos |
| alongamento-lateral | 0 | 0 | 0 (3) | 0 | só avisos |
