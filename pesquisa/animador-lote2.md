# Animador — lote2 (56 exercícios)

Conferência: qa.py em cada id + renders de perfil/frente/3/4 (tira de 6 quadros) e zoom em mãos/pés/apoios (`scratchpad/an2/`).
Status: **ok** = qa.py sem erro (avisos anotados e justificados) e conferido visualmente; **pendente motor** = o que sobra só se resolve no motor (ver `pesquisa/motor-pendencias.md`).

| id | status | qa.py | observação |
|---|---|---|---|
| flexao | ok | aviso | aviso pousada: coxas/joelhos a ~11 cm do chão no fundo da flexão = posição normal |
| flexao-inclinada | ok | limpo |  |
| flexao-joelhos | ok | aviso | aviso pousada: pelve perto do chão no fundo (normal) |
| flexao-declinada | ok | limpo |  |
| flexao-diamante | ok | aviso | mãos em diamante; avisos de punho ulnar/pronação inerentes à pegada |
| flexao-pliometrica | ok | limpo | fixo pes, apoio em todos os quadros, voo só nos pés |
| supino-reto | ok | limpo |  |
| supino-halteres | ok | limpo |  |
| supino-inclinado | pendente motor | erro | encosto inclinado: costas sempre ~2 cm acima da face medida pelo qa (pendência); apoio/base costas |
| supino-inclinado-barra | pendente motor | erro | idem supino-inclinado (pendência do encosto inclinado); apoio/base costas |
| supino-maquina | ok | limpo |  |
| crucifixo | ok | limpo |  |
| crossover | ok | limpo |  |
| peck-deck | ok | limpo |  |
| supino-elastico | pendente motor | erro | elástico "de costas" passa pelo braço (pendência); apoio/corpo cabo/elástico x corpo |
| crucifixo-elastico | ok | limpo |  |
| paralelas | pendente motor | erro | pegada no tubo longitudinal: polegar invertido na mão dir (pendência); pegada/dist mão dir; rom/antebraco_pro antebraço dir |
| barra-fixa | ok | aviso | aviso 1,6 cm (lim. 1,5) da pegada na barra: motor |
| barra-supinada | pendente motor | erro | torção do antebraço na pegada supinada pendurada (pendência antiga do motor); rom/antebraco_pro antebraço esq; rom/antebraco_pro antebraço dir; rom/antebraco_sup antebraço esq; rom/antebraco_sup antebraço dir |
| barra-assistida | ok | aviso | laço do centro da barra ao pé à frente; aviso 1,6 cm da pegada (motor) |
| puxada-frente | ok | aviso | aviso: cabo roça a cabeça (3,3 cm) na descida — torre/polia posicionadas pelo motor à frente dos joelhos |
| puxada-triangulo | ok | limpo |  |
| remada-baixa | ok | limpo |  |
| remada-curvada | ok | limpo |  |
| remada-unilateral | ok | limpo |  |
| remada-elastico | ok | limpo |  |
| remada-invertida | ok | aviso | avisos de pegada 1,8 cm (motor) e joelho "pousado" (prancha) |
| pulldown-elastico | ok | limpo |  |
| pullover-polia | ok | limpo |  |
| face-pull | ok | limpo |  |
| band-pull-apart | ok | aviso | aviso 1,6 cm: elástico encosta no esterno (técnica) |
| encolhimento | ok | limpo |  |
| desenvolvimento-halteres | ok | limpo | cotovelos 50° à frente (sem torção do cotovelo) |
| desenvolvimento-barra | ok | limpo |  |
| desenvolvimento-maquina | pendente motor | erro | mão entra na ligação alavanca–pegador no topo (pendência); apoio/penetra mao_t x estrutura; apoio/penetra mao_f x estrutura |
| desenvolvimento-elastico | ok | limpo | idem; pegada vista de frente parece aberta (pendência visual) |
| elevacao-lateral | ok | limpo |  |
| elevacao-lateral-elastico | ok | limpo |  |
| elevacao-frontal | ok | limpo |  |
| crucifixo-inverso | ok | limpo |  |
| arnold | ok | limpo | início com cotovelos à frente, rotação até 50° |
| pike-pushup | ok | aviso | aviso pousada: antebraço perto do chão no fundo (normal) |
| rotacao-externa | ok | limpo |  |
| rosca-direta | ok | aviso | aviso supinação 112° (motor) |
| rosca-halteres | ok | limpo |  |
| rosca-martelo | ok | limpo |  |
| rosca-elastico | ok | limpo |  |
| rosca-scott | pendente motor | erro | almofada do Scott entra na axila/tórax (pendência); apoio/penetra torax x estofado; apoio/penetra braco_t x estofado; apoio/penetra braco_f x estofado; apoio/penetra abdomen x estrutura |
| triceps-polia | ok | limpo |  |
| triceps-frances | pendente motor | erro | rotação do úmero com braço acima da cabeça (pendência); pop no quadro 20 (5.2 cm, wrist.R) |
| triceps-testa | pendente motor | erro | rotação do úmero com braço vertical (pendência); rom/cotovelo_hiperext cotovelo esq; rom/cotovelo_hiperext cotovelo dir |
| triceps-banco | ok | aviso | aviso extensão do ombro 19° no fundo do mergulho (amplitude real do exercício) |
| triceps-elastico | pendente motor | erro | rotação do úmero com braço acima da cabeça (pendência); rom/antebraco_pro antebraço esq; rom/antebraco_pro antebraço dir; rom/antebraco_sup antebraço esq; rom/antebraco_sup antebraço dir; rom/cotovelo_hiperext cotove |
| triceps-coice | ok | limpo |  |
| passe-medicine | ok | limpo |  |
| isometria-pescoco | ok | aviso | mão na testa (segura cabeca), quadros de ida/volta; aviso congelado = isometria |

Total: 46 ok, 10 pendentes do motor. QA final (qa.py, 56 ids): 34 limpos, 12 só com aviso (justificados na tabela), 10 com erro — todos dependentes do motor.
