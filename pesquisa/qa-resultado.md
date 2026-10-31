# Resultado do QA das animações 3D (pegada, amplitude articular, apoio)

Gerado por `tools/anim3d/qa.py` + `tools/anim3d/qa_relatorio.py` sobre os 175 exercícios. Critérios, limiares e método de validação em `tools/anim3d/qa_corpo.py` e na seção final.

**80 exercícios com erro, 43 só com aviso, 52 limpos.**

## Exercícios com defeito, por tipo

| Tipo | Exercícios com erro | Só aviso |
|---|---|---|
| Pegada | 2 | 11 |
| Amplitude (ROM) | 21 | 29 |
| Apoio / interpenetração | 63 | 37 |
| Motor (pops, skate, chão...) | 11 | 8 |

## Erros por verificação (nº de exercícios)

| Tipo | Verificação | Exercícios |
|---|---|---|
| apoio | penetra | 58 |
| apoio | base | 47 |
| apoio | pousada | 34 |
| rom | antebraco_pro | 16 |
| motor | pop | 9 |
| rom | antebraco_sup | 8 |
| motor | rosto | 6 |
| rom | ombro_ri | 5 |
| apoio | corpo | 4 |
| rom | ombro_re | 4 |
| rom | punho_ulnar | 4 |
| rom | ombro_aducao_h | 3 |
| rom | punho_radial | 3 |
| pegada | cruzada | 2 |
| rom | cotovelo_hiperext | 2 |
| rom | ombro_ext_excesso | 2 |
| apoio | flutua | 1 |
| motor | alavanca | 1 |
| motor | chao: | 1 |
| motor | skate | 1 |
| pegada | dist | 1 |
| rom | coluna_extensao | 1 |
| rom | quadril_flexao | 1 |
| rom | quadril_re | 1 |

## Os piores (gravidade = soma de valor/limite dos erros, pesada pela duração)

| # | Exercício | Gravidade | Principais erros |
|---|---|---|---|
| 1 | alongamento-adutores | 73.6 | pousada joelho dir 14.9 cm; pousada joelho esq 14.9 cm; base coxa dir 34.6 cm; pousada pelve 11.7 cm; pousada costas 10.4 cm |
| 2 | peck-deck | 65.7 | penetra braco_f x estrutura 10.7 cm; penetra antebraco_f x estrutura 13.3 cm; penetra braco_t x estrutura 10.4 cm; penetra antebraco_t x estrutura 11.1 cm; penetra mao_f x estrutura 9.5 cm |
| 3 | rotacao-toracica | 56.9 | base antebraço dir 57.4 cm; pousada coxa dir 14.7 cm; pousada joelho dir 14.9 cm; pousada pelve 15.0 cm; pousada antebraço dir 4.4 cm |
| 4 | turkish-getup | 54.8 | base costas 61.4 cm; penetra antebraco_f x kettlebell 6.8 cm; base coxa dir 16.6 cm; base joelho dir 34.5 cm; pousada joelho dir 9.7 cm |
| 5 | box-jump | 49.9 | penetra pe_f x caixa 18.7 cm; penetra perna_f x caixa 18.6 cm; penetra pe_t x caixa 18.6 cm; penetra perna_t x caixa 18.5 cm; penetra coxa_t x caixa 5.0 cm |
| 6 | hack | 38.3 | penetra pe_f x estrutura 3.9 cm; ombro_ext_excesso ombro dir 41°; ombro_ext_excesso ombro esq 38°; penetra braco_f x metal 2.2 cm; penetra antebraco_f x metal 2.2 cm |
| 7 | torcao-coluna | 37.9 | pousada coxa dir 15.0 cm; pousada joelho dir 14.8 cm; base joelho dir 14.2 cm |
| 8 | prancha-lateral | 33.9 | base antebraço dir 84.2 cm; pousada joelho dir 15.0 cm; pousada antebraço dir 12.3 cm |
| 9 | saco-combinacoes | 32.0 | base costas 28.7 cm; penetra mao_f x peça 8.4 cm; penetra mao_t x peça 8.4 cm; penetra antebraco_t x peça 7.9 cm; penetra antebraco_f x peça 7.1 cm |
| 10 | abdominal | 31.9 | base costas 41.3 cm; pousada costas 13.2 cm; pousada pelve 12.0 cm |
| 11 | afundo-halteres | 29.4 | base joelho dir 34.2 cm; base joelho esq 31.9 cm; base coxa esq 9.3 cm; base coxa dir 8.1 cm |
| 12 | step-up | 26.0 | base coxa esq 14.8 cm; base joelho dir 10.4 cm; penetra perna_t x caixa 4.5 cm; penetra pe_t x caixa 3.1 cm |
| 13 | superman | 25.3 | pousada costas 13.9 cm; pousada antebraço esq 12.7 cm; pousada antebraço dir 10.8 cm |
| 14 | fuga-quadril | 24.6 | base pelve 26.8 cm; base coxa esq 25.8 cm; cotovelo_hiperext cotovelo esq 29°; cotovelo_hiperext cotovelo dir 27° |
| 15 | rolo-it | 23.5 | base antebraço dir 47.7 cm; pousada coxa dir 14.8 cm |
| 16 | maior-alongamento | 23.4 | base joelho dir 43.4 cm; pousada joelho dir 14.9 cm |
| 17 | alongamento-triceps | 22.2 | ombro_ri ombro dir 179°; ombro_ri ombro esq 177°; antebraco_sup antebraço dir 180°; antebraco_pro antebraço esq 180°; antebraco_sup antebraço esq 176° |
| 18 | inchworm | 22.2 | base joelho dir 8.9 cm; base cabeça 7.0 cm; pop no quadro 36 (13.7 cm, lowerarm01.L); pop no quadro 42 (13.3 cm, lowerarm01.L); pop no quadro 58 (12.1 cm, lowerarm01.R) |
| 19 | supino-inclinado-barra | 20.6 | base costas 12.1 cm; pousada cabeça 11.3 cm; rosto coberto 22% |
| 20 | rolo-quadriceps | 18.9 | penetra coxa_t x peça laranja 7.2 cm; penetra coxa_f x peça laranja 5.4 cm |
| 21 | coice-gluteo | 17.7 | base joelho dir 35.7 cm; pousada joelho dir 6.8 cm |
| 22 | rosca-scott | 17.2 | penetra braco_f x estofado 8.5 cm; penetra torax x estofado 4.5 cm; penetra abdomen x estrutura 2.4 cm; penetra braco_t x estofado 2.5 cm |
| 23 | escada | 17.0 | punho_ulnar punho dir 81°; penetra mao_t x estrutura 2.5 cm; punho_ulnar punho esq 61°; pop no quadro 7 (18.4 cm, wrist.R); pop no quadro 10 (18.4 cm, wrist.R) |
| 24 | mountain-climber | 16.2 | base joelho esq 31.3 cm; base joelho dir 31.3 cm; quadril_flexao quadril esq 167° |
| 25 | bound-lateral | 16.0 | base joelho esq 17.7 cm; base joelho dir 17.7 cm |

## Tabela dos exercícios

Colunas: nº de verificações com erro (e aviso) por tipo; defeitos = os erros mais graves (verificação, parte, valor).

| Exercício | Pegada | ROM | Apoio | Motor | Defeitos |
|---|---|---|---|---|---|
| agachamento-livre | 0 | 0 | 0 | 0 | ok |
| agachamento-elastico | 0 | 0 | 0 | 0 | ok |
| agachamento-salto | 0 | 0 | 0 | 0 | ok |
| agachamento-barra | 0 | 0 (4) | 0 | 0 | só avisos |
| agachamento-frontal | 0 | **2** | 0 (4) | 0 | punho_radial punho esq 62°; punho_radial punho dir 59° |
| leg-press | 0 | 0 | **2** (1) | 0 | pousada costas 9.2 cm; pousada pelve 7.4 cm |
| hack | 0 | **2** (2) | **9** (3) | 0 | penetra pe_f x estrutura 3.9 cm; ombro_ext_excesso ombro dir 41°; ombro_ext_excesso ombro esq 38°; penetra braco_f x metal 2.2 cm |
| cadeira-extensora | 0 | 0 | 0 (2) | 0 | só avisos |
| cadeira-flexora | 0 (1) | 0 | 0 (1) | 0 | só avisos |
| mesa-flexora | 0 | 0 | **1** (3) | 0 | pousada pelve 6.0 cm |
| afundo | 0 | 0 | 0 (1) | 0 | só avisos |
| afundo-halteres | 0 | 0 | **4** | 0 | base joelho dir 34.2 cm; base joelho esq 31.9 cm; base coxa esq 9.3 cm; base coxa dir 8.1 cm |
| passada-andando | 0 | 0 | 0 | 0 | ok |
| bulgaro | 0 | 0 | **1** | 0 | penetra perna_t x estofado 2.9 cm |
| step-up | 0 | 0 | **4** (1) | 0 | base coxa esq 14.8 cm; base joelho dir 10.4 cm; penetra perna_t x caixa 4.5 cm; penetra pe_t x caixa 3.1 cm |
| terra | 0 (2) | 0 | 0 | 0 | só avisos |
| stiff | 0 (1) | 0 | 0 | 0 | só avisos |
| stiff-halteres | 0 | 0 | 0 | 0 | ok |
| terra-uma-perna | 0 | 0 | **2** (2) | 0 | base coxa dir 11.1 cm; penetra coxa_t x kettlebell 4.5 cm |
| ponte-gluteo | 0 | 0 | 0 (3) | 0 | só avisos |
| ponte-unilateral | 0 | 0 | 0 (3) | 0 | só avisos |
| elevacao-quadril | 0 | 0 | **1** (3) | 0 | base pelve 47.0 cm |
| coice-gluteo | 0 | 0 | **2** | 0 | base joelho dir 35.7 cm; pousada joelho dir 6.8 cm |
| abdutora | 0 | 0 | **2** | 0 | penetra perna_f x estofado 4.4 cm; penetra perna_t x estofado 3.9 cm |
| monster-walk | 0 | 0 | **1** | 0 | base costas 26.2 cm |
| panturrilha-pe | 0 | 0 | **1** | 0 | base costas 7.7 cm |
| panturrilha-sentado | 0 (2) | **4** | 0 | 0 (1) | antebraco_pro antebraço dir 148°; antebraco_pro antebraço esq 147°; punho_ulnar punho dir 54°; punho_ulnar punho esq 53° |
| panturrilha-elastico | 0 | 0 | 0 | 0 (1) | só avisos |
| superman | 0 | 0 | **3** | 0 | pousada costas 13.9 cm; pousada antebraço esq 12.7 cm; pousada antebraço dir 10.8 cm |
| hiperextensao | 0 | 0 (2) | **3** (7) | 0 | penetra coxa_t x estofado 3.8 cm; penetra coxa_f x estofado 3.8 cm; penetra perna_t x estofado 3.4 cm |
| prancha | 0 | 0 | 0 (4) | 0 | só avisos |
| prancha-lateral | 0 | 0 | **3** | 0 | base antebraço dir 84.2 cm; pousada joelho dir 15.0 cm; pousada antebraço dir 12.3 cm |
| abdominal | 0 | 0 | **3** | 0 | base costas 41.3 cm; pousada costas 13.2 cm; pousada pelve 12.0 cm |
| abdominal-infra | 0 | 0 | 0 (2) | 0 | só avisos |
| dead-bug | 0 | 0 | **1** | 0 | pousada cabeça 4.8 cm |
| mountain-climber | 0 | **1** (3) | **2** | 0 | base joelho esq 31.3 cm; base joelho dir 31.3 cm; quadril_flexao quadril esq 167° |
| russian-twist | 0 | 0 | 0 (4) | 0 | só avisos |
| abdominal-bicicleta | 0 | **4** (1) | 0 | 0 | ombro_ri ombro dir 180°; ombro_ri ombro esq 177°; ombro_re ombro esq 180°; ombro_re ombro dir 177° |
| elevacao-pernas-barra | 0 | 0 | 0 | 0 | ok |
| roda-abdominal | 0 | 0 | 0 (2) | 0 | só avisos |
| canivete | 0 | 0 (1) | 0 | 0 | só avisos |
| box-jump | 0 | 0 | **6** | 0 | penetra pe_f x caixa 18.7 cm; penetra perna_f x caixa 18.6 cm; penetra pe_t x caixa 18.6 cm; penetra perna_t x caixa 18.5 cm |
| salto-distancia | 0 | 0 | **3** | 0 | base costas 8.5 cm; base coxa esq 4.4 cm; flutua corpo 4quadros |
| bound-lateral | 0 | 0 | **2** | 0 | base joelho esq 17.7 cm; base joelho dir 17.7 cm |
| salto-tesoura | 0 | 0 | 0 | 0 | ok |
| tuck-jump | 0 | 0 | 0 | 0 | ok |
| arremesso-rotacional | 0 | **1** (1) | **1** (7) | 0 | penetra antebraco_f x halter 5.7 cm; ombro_aducao_h ombro esq 69° |
| ponte-pescoco | 0 | **2** (1) | 0 (2) | 0 | antebraco_pro antebraço esq 164°; antebraco_pro antebraço dir 150° |
| fuga-quadril | 0 | **2** | **2** | 0 | base pelve 26.8 cm; base coxa esq 25.8 cm; cotovelo_hiperext cotovelo esq 29°; cotovelo_hiperext cotovelo dir 27° |
| nordico | 0 | 0 | **3** (2) | 0 | penetra pe_f x estofado 4.3 cm; penetra pe_t x estofado 4.3 cm; penetra perna_t x estofado 4.0 cm |
| educativos-corrida | 0 | 0 | 0 | 0 | ok |
| bike-subida | 0 | 0 | 0 (4) | 0 | só avisos |
| sentar-levantar | 0 | 0 | 0 | 0 | ok |
| flexao | 0 | 0 | 0 (4) | 0 | só avisos |
| agachamento-goblet | 0 | 0 (4) | **2** | 0 | penetra antebraco_t x kettlebell 1.9 cm; penetra antebraco_f x kettlebell 1.6 cm |
| pallof | **2** | **2** | 0 (7) | 0 (1) | cruzada mão esq 82°; cruzada mão dir 78°; antebraco_pro antebraço dir 135°; antebraco_pro antebraço esq 135° |
| abdominal-polia | 0 | 0 | 0 | 0 | ok |
| flexao-inclinada | 0 | 0 (2) | 0 | 0 | só avisos |
| flexao-joelhos | 0 | 0 | 0 (1) | 0 | só avisos |
| flexao-declinada | 0 | 0 | 0 | 0 | ok |
| flexao-diamante | 0 | 0 | 0 (4) | 0 | só avisos |
| flexao-pliometrica | 0 | 0 | **1** | 0 | base coxa dir 43.1 cm |
| supino-reto | 0 | 0 | 0 | 0 | ok |
| supino-halteres | 0 | 0 | 0 | 0 | ok |
| supino-inclinado | 0 | 0 | **2** (1) | 0 | pousada cabeça 13.4 cm; base costas 5.1 cm |
| supino-inclinado-barra | 0 | 0 | **2** (1) | **1** | base costas 12.1 cm; pousada cabeça 11.3 cm; rosto coberto 22% |
| supino-maquina | 0 | 0 | 0 | 0 | ok |
| crucifixo | 0 | 0 | **1** | **1** | pousada cabeça 5.2 cm; rosto coberto 24% |
| crossover | 0 | 0 | 0 | 0 | ok |
| peck-deck | 0 | 0 | **6** | **1** | penetra braco_f x estrutura 10.7 cm; penetra antebraco_f x estrutura 13.3 cm; penetra braco_t x estrutura 10.4 cm; penetra antebraco_t x estrutura 11.1 cm |
| supino-elastico | 0 | 0 | **1** | 0 | corpo cabo/elástico x corpo 4.8 cm |
| crucifixo-elastico | 0 | 0 | 0 | 0 | ok |
| paralelas | **1** (3) | **2** | 0 | 0 | antebraco_pro antebraço dir 180°; dist mão esq 2.4 cm; antebraco_sup antebraço dir 180° |
| barra-fixa | 0 (2) | 0 | 0 | 0 | só avisos |
| barra-supinada | 0 | **4** | 0 | **1** | antebraco_sup antebraço dir 167°; antebraco_sup antebraço esq 167°; antebraco_pro antebraço esq 178°; antebraco_pro antebraço dir 177° |
| barra-assistida | 0 (2) | 0 | **1** | 0 | corpo cabo/elástico x corpo 9.9 cm |
| puxada-frente | 0 | 0 | **1** (3) | **1** | corpo cabo/elástico x corpo 4.2 cm; rosto coberto 27% |
| puxada-triangulo | 0 | 0 (2) | 0 (3) | 0 | só avisos |
| remada-baixa | 0 | 0 | **2** (6) | 0 | penetra pe_f x estofado 3.7 cm; penetra pe_t x estofado 3.7 cm |
| remada-curvada | 0 | 0 | 0 | 0 | ok |
| remada-unilateral | 0 | 0 | **2** (2) | 0 | penetra perna_f x estofado 3.8 cm; penetra mao_f x estofado 3.8 cm |
| remada-elastico | 0 | 0 | 0 | 0 | ok |
| remada-invertida | 0 (4) | 0 (2) | 0 (2) | 0 | só avisos |
| pulldown-elastico | 0 | 0 | 0 | 0 | ok |
| pullover-polia | 0 | 0 | 0 | 0 | ok |
| face-pull | 0 | 0 (3) | 0 | **1** | rosto coberto 26% |
| band-pull-apart | 0 | 0 | **1** | 0 | corpo cabo/elástico x corpo 5.3 cm |
| encolhimento | 0 | 0 | 0 | 0 | ok |
| desenvolvimento-halteres | 0 | 0 (4) | 0 | 0 | só avisos |
| desenvolvimento-barra | 0 | 0 | 0 | **1** | rosto coberto 27% |
| desenvolvimento-maquina | 0 | 0 (7) | **1** | 0 | penetra mao_t x estrutura 3.3 cm |
| desenvolvimento-elastico | 0 | 0 (4) | 0 (1) | 0 | só avisos |
| elevacao-lateral | 0 | 0 | 0 | 0 | ok |
| elevacao-lateral-elastico | 0 | 0 | 0 | 0 | ok |
| elevacao-frontal | 0 | 0 | 0 | 0 | ok |
| crucifixo-inverso | 0 | 0 | 0 | 0 | ok |
| arnold | 0 | 0 (2) | 0 | 0 | só avisos |
| pike-pushup | 0 | 0 | 0 (2) | 0 | só avisos |
| rotacao-externa | 0 | 0 | 0 | 0 | ok |
| rosca-direta | 0 | 0 (2) | 0 | 0 | só avisos |
| rosca-halteres | 0 | 0 | 0 | 0 | ok |
| rosca-martelo | 0 | 0 | 0 | 0 | ok |
| rosca-elastico | 0 | 0 | 0 | 0 | ok |
| rosca-scott | 0 | 0 (2) | **4** | 0 | penetra braco_f x estofado 8.5 cm; penetra torax x estofado 4.5 cm; penetra abdomen x estrutura 2.4 cm; penetra braco_t x estofado 2.5 cm |
| triceps-polia | 0 | 0 | 0 | 0 | ok |
| triceps-frances | 0 (2) | 0 (6) | 0 | **1** | pop no quadro 20 (5.2 cm, wrist.R) |
| triceps-testa | 0 | 0 (6) | **1** | 0 | pousada cabeça 5.5 cm |
| triceps-banco | 0 | 0 (2) | 0 | 0 | só avisos |
| triceps-elastico | 0 | **4** (4) | 0 | 0 | antebraco_pro antebraço esq 180°; antebraco_pro antebraço dir 174°; antebraco_sup antebraço dir 171°; antebraco_sup antebraço esq 166° |
| triceps-coice | 0 | 0 | **1** | 0 | base costas 8.6 cm |
| passe-medicine | 0 | 0 | 0 (1) | 0 | só avisos |
| isometria-pescoco | 0 | **2** (2) | 0 (2) | 0 (1) | ombro_ri ombro esq 144°; antebraco_sup antebraço esq 135° |
| burpee | 0 | 0 | 0 | 0 | ok |
| polichinelo | 0 | 0 | 0 | 0 | ok |
| corda | 0 | 0 | 0 | 0 | ok |
| swing | 0 | 0 | 0 (2) | 0 | só avisos |
| thruster | 0 | 0 | 0 | 0 | ok |
| power-clean | 0 (1) | 0 (2) | 0 (1) | 0 | só avisos |
| arremesso-medicine | 0 | 0 | 0 (2) | 0 | só avisos |
| battle-rope | 0 | 0 | 0 | 0 | ok |
| farmer-walk | 0 | 0 | 0 | 0 | ok |
| sled-push | 0 | 0 | 0 | 0 | ok |
| turkish-getup | 0 | 0 (6) | **6** | 0 | base costas 61.4 cm; penetra antebraco_f x kettlebell 6.8 cm; base coxa dir 16.6 cm; base joelho dir 34.5 cm |
| inchworm | 0 | 0 | **2** | **7** | base joelho dir 8.9 cm; base cabeça 7.0 cm; pop no quadro 36 (13.7 cm, lowerarm01.L); pop no quadro 42 (13.3 cm, lowerarm01.L) |
| sombra | 0 | 0 | **1** | 0 | base costas 29.8 cm |
| saco-combinacoes | 0 | 0 | **5** | 0 | base costas 28.7 cm; penetra mao_f x peça 8.4 cm; penetra mao_t x peça 8.4 cm; penetra antebraco_t x peça 7.9 cm |
| sprawl | 0 | 0 | **1** | **1** | base joelho dir 39.3 cm; chao: pele 1.2 cm abaixo do chão |
| bear-crawl | 0 | 0 | 0 | 0 | ok |
| corrida-leve | 0 | 0 | 0 (1) | 0 | só avisos |
| caminhada-corrida | 0 | 0 | 0 | 0 | ok |
| tiros | 0 | 0 | 0 | 0 | ok |
| tempo-run | 0 | 0 | 0 (2) | 0 | só avisos |
| longao | 0 | 0 | 0 | 0 | ok |
| bike-leve | 0 | 0 | 0 (2) | 0 | só avisos |
| bike-intervalado | 0 | 0 | 0 (3) | 0 | só avisos |
| bike-cadencia | 0 | 0 | 0 (2) | 0 | só avisos |
| eliptico | 0 (2) | **2** (2) | 0 | 0 | antebraco_pro antebraço esq 128°; antebraco_pro antebraço dir 128° |
| remo-ergometro | 0 | 0 (4) | **1** | 0 | penetra abdomen x estrutura 1.8 cm |
| escada | 0 (2) | **2** | **3** | **2** | punho_ulnar punho dir 81°; penetra mao_t x estrutura 2.5 cm; punho_ulnar punho esq 61°; pop no quadro 7 (18.4 cm, wrist.R) |
| prova | 0 | 0 | 0 | 0 | ok |
| caminhada | 0 | 0 | 0 | 0 | ok |
| maior-alongamento | 0 | 0 (2) | **2** | 0 | base joelho dir 43.4 cm; pousada joelho dir 14.9 cm |
| gato-camelo | 0 | 0 (1) | 0 (2) | 0 | só avisos |
| postura-crianca | 0 | **1** (4) | 0 (8) | 0 | coluna_extensao coluna 60° |
| flexor-quadril | 0 | 0 (1) | 0 | 0 | só avisos |
| alongamento-posterior | 0 | 0 | 0 | 0 | ok |
| alongamento-quadriceps | 0 | 0 (1) | **1** | 0 | base joelho esq 9.0 cm |
| alongamento-panturrilha | 0 | 0 | 0 (4) | 0 | só avisos |
| circulos-braco | 0 | 0 | 0 | 0 | ok |
| circulos-quadril | 0 | 0 | 0 (2) | 0 | só avisos |
| rolo-quadriceps | 0 | 0 | **2** (6) | 0 | penetra coxa_t x peça laranja 7.2 cm; penetra coxa_f x peça laranja 5.4 cm |
| rolo-panturrilha | 0 | 0 (3) | **1** (2) | 0 | penetra perna_f x peça laranja 3.9 cm |
| rolo-it | 0 | 0 (1) | **2** (1) | 0 | base antebraço dir 47.7 cm; pousada coxa dir 14.8 cm |
| alongamento-peito | 0 | **1** (1) | **1** | 0 | penetra mao_t x caixa 3.6 cm; ombro_re ombro dir 140° |
| rotacao-toracica | 0 | **2** | **5** | 0 | base antebraço dir 57.4 cm; pousada coxa dir 14.7 cm; pousada joelho dir 14.9 cm; pousada pelve 15.0 cm |
| alongamento-adutores | 0 | 0 (2) | **7** | 0 | pousada joelho dir 14.9 cm; pousada joelho esq 14.9 cm; base coxa dir 34.6 cm; pousada pelve 11.7 cm |
| equilibrio-unipodal | 0 | 0 | **1** | 0 (1) | base coxa esq 7.8 cm |
| balanco-pernas | 0 | 0 (2) | **1** (1) | 0 | base costas 10.1 cm |
| circulos-tornozelo | 0 | 0 | **1** (2) | 0 | base costas 8.7 cm |
| circulos-punho | 0 | 0 | 0 | 0 | ok |
| circulos-ombro | 0 | 0 | 0 | 0 | ok |
| circulos-joelho | 0 | 0 | 0 | 0 | ok |
| chute-gluteo | 0 | 0 | **2** | 0 | base joelho dir 16.5 cm; base joelho esq 12.0 cm |
| carioca | 0 | 0 | **1** | 0 | base costas 28.4 cm |
| abertura-peito-dinamica | 0 | 0 | 0 | 0 | ok |
| spider | 0 | 0 (1) | **1** | 0 | base joelho dir 23.3 cm |
| alongamento-gluteo | 0 | **1** (2) | 0 (3) | 0 | quadril_re quadril esq 93° |
| abraco-joelhos | 0 | 0 | **3** | 0 | pousada cabeça 8.5 cm; base cabeça 7.6 cm; pousada pelve 3.9 cm |
| alongamento-triceps | 0 | **7** (5) | 0 (6) | 0 | ombro_ri ombro dir 179°; ombro_ri ombro esq 177°; antebraco_sup antebraço dir 180°; antebraco_pro antebraço esq 180° |
| alongamento-antebraco | 0 | 0 | 0 | 0 | ok |
| alongamento-pescoco | 0 | 0 | 0 | 0 (1) | só avisos |
| alongamento-lateral | 0 | **2** (2) | 0 (10) | 0 | ombro_aducao_h ombro dir 87°; ombro_aducao_h ombro esq 83° |
| torcao-coluna | 0 | 0 | **3** (1) | 0 (1) | pousada coxa dir 15.0 cm; pousada joelho dir 14.8 cm; base joelho dir 14.2 cm |
| alongamento-dorsal | 0 | 0 | 0 | 0 (1) | só avisos |
| moinho | 0 | 0 | 0 | 0 | ok |

## Rodada

- Rodada retomável (`qa.py --retomar`), 1 processo, 24 fps. Começou com o código do QA em `9c56171` e o motor em `fb1f86c`
  e terminou em 31/10/2026 ~21h30 UTC com o repositório em `8b5360c`. Os animadores estavam mexendo nos lotes nesse intervalo,
  então parte dos exercícios foi medida com dados anteriores às correções da rodada 7 (lote2 `0548945`, lote3 `26068c5`, lote1 `8b5360c`).
  Para medir de novo: `python tools/anim3d/qa.py --mh <makehuman/data> --anim tools/anim/dados/lote{1,2,3}.json --so-avisar --saida qa.json`.
- Pós-rodada, para igualar ao `qa_corpo.py` final: hiperextensão de cotovelo com o cotovelo dobrado > 35° virou aviso (torção da malha), flexão/extensão do quadril perto de ±180° virou aviso (medida degenerada), estofado "penetrado" mais fundo que a própria espessura virou aviso.
- Os achados de "corpo dentro do corpo" (braço no tronco, perna na outra) foram rebaixados para aviso depois da rodada
  (mesma regra do `qa_corpo.py` atual): o teste satura em 6 cm e acusou exercícios que a auditoria aprovou.

## Método (resumo; os detalhes e limiares estão no cabeçalho de `tools/anim3d/qa_corpo.py`)

- **Pegada**: o centro do túnel que os dedos 2–5 formam ao fechar (um círculo ajustado pelas articulações de cada dedo)
  comparado com o eixo da empunhadura real que `aparelhos.py` coloca em cada quadro (barra, halter, alça do kettlebell,
  puxador, corda/cabo, alça do elástico, pegador da máquina, barra fixa, paralelas, manopla). Erro com mais de 2 cm. Mede
  também a pele da mão dentro da empunhadura, o ângulo entre a empunhadura e a linha dos nós dos dedos e o fechamento dos dedos.
- **ROM**: ângulos reais do esqueleto em cada quadro (joelho, cotovelo, ombro com elevação, abdução horizontal e rotação
  pelo antebraço, antebraço, punho, quadril com rotação pela convenção de Euler da ISB, coluna total e por segmento,
  pescoço) comparados com os valores da AAOS e de Norkin & White. Validado em poses conhecidas: agachamento (joelho 125°,
  quadril 120°), flexão (punho em extensão de 80°, pronação de 80°), rosca (supinação de 85–99°).
- **Apoio**: centro de massa por segmentos (Dempster/Winter) mais a massa do implemento, ponto de momento zero (ZMP) e
  polígono de apoio formado pela pele a até 3 cm do chão ou de uma superfície horizontal real do kit. Mede também a região
  do tronco parada no ar acima de uma superfície, a pele dentro de um aparelho (com BVH das malhas do kit) e o cabo ou
  elástico atravessando o corpo.

## Validação visual e contra as auditorias

Conferi com renders de perto (`zoom.py` no scratchpad, com marcadores no túnel e na pegada) e com quadros dos MP4:
- **Acusações confirmadas**:
  - Com o motor antigo: halter e barra ficavam 5,5 cm fora do túnel dos dedos (rosca, supino, terra), o kettlebell flutuava
    entre as mãos no swing, os dedos ficavam abertos no guidão da bike, a mão ficava ao lado da barra nas paralelas e o
    puxador atravessava o antebraço na puxada. O motor novo corrigiu a maior parte.
  - Na rodada atual:
    - corpo flutuando sobre o tapete (ponte-glúteo e abdominal no motor antigo);
    - costas no ar no leg-press;
    - cabeça pairando de 5 a 14 cm acima do banco (supinos, dead-bug);
    - glúteo acima do assento (sentar-levantar, cadeira extensora);
    - joelho de apoio a 7 cm do tapete no coice-glúteo, com o peso só nas mãos;
    - centro de massa fora do pé no equilíbrio unipodal;
    - braços atrás das almofadas do hack, com extensão do ombro além do limite.
- **Aprovações confirmadas**: agachamento-livre, agachamento-salto, stiff-halteres e rosca-halteres (motor novo), com a
  pegada fechada em volta do cabo.
- **Falsos positivos corrigidos na calibração**:
  - flexão e tríceps-banco (antebraço "pousado");
  - postura da criança (rotação do quadril degenerada);
  - corrida e caminhada (base de apoio em locomoção);
  - pegada do supino com a palma comprimindo a barra (o limiar de "atravessa" subiu para 2,5 cm);
  - braço junto ao tronco;
  - adução horizontal com o braço acima da cabeça.
- **Discordâncias que continuam** (a auditoria aprovou e o QA acusa):
  - Nove casos que conferi e que parecem defeitos reais e sutis: coice-glúteo, maior-alongamento, equilíbrio-unipodal,
    terra-uma-perna (kettlebell na coxa), nórdico (rolo afundando 4 cm no tornozelo), dead-bug (cabeça a 5 cm do tapete),
    búlgaro (canela 3 cm dentro do banco), sentar-levantar e spider.
  - Prováveis falsos positivos de base em movimento dinâmico lateral: bound-lateral, chute-glúteo e monster-walk.
  - Prováveis falsos positivos de ROM em alongamentos extremos: postura-criança (flexão do quadril passiva de 172°) e
    alongamento-peito (rotação externa de 140°).
  - Muitos defeitos das auditorias que o QA não acusa foram corrigidos depois pelo motor (pegada real, tronco como apoio).
    Os que sobram estão fora do escopo geométrico: estética, ritmo, aparelho errado e corda que parece um aro.
