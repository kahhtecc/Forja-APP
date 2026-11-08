# Animador lote3: andamento

QA = `tools/anim3d/qa.py` atual (motor 9534d68+) no lote todo, rodada final de 2026-11-08 (`pesquisa/qa-resultado.json`). "aviso" só com justificativa.
Conferência visual: tiras de 4–8 quadros e zoom das mãos/pés/cabeça nos exercícios alterados.
Resultado: 27 limpos, 26 só com aviso, 10 com erro.

| id | status | qa | observação |
|---|---|---|---|
| burpee | ok | limpo |  |
| polichinelo | ok | limpo |  |
| corda | ok | limpo |  |
| swing | ok | aviso: corpo |  |
| thruster | ok | limpo |  |
| power-clean | ok | aviso: antebraco_pro; dist; penetra |  |
| arremesso-medicine | ok | limpo |  |
| battle-rope | ok | limpo |  |
| farmer-walk | ok | limpo |  |
| sled-push | ok | limpo |  |
| turkish-getup | erro (dados) | erro | erro: vários (antebraço no kettlebell, CM na passagem da perna, pousadas) — não retrabalhado nesta rodada |
| inchworm | pendente motor | erro | pendente motor: pops do antebraço nos passos de mão automáticos |
| sombra | ok | limpo |  |
| saco-combinacoes | ok | aviso: penetra |  |
| sprawl | ok | limpo |  |
| bear-crawl | ok | limpo |  |
| corrida-leve | ok | aviso: penetra |  |
| caminhada-corrida | ok | limpo |  |
| tiros | ok | limpo |  |
| tempo-run | ok | aviso: penetra |  |
| longao | ok | limpo |  |
| bike-leve | ok | aviso: penetra |  |
| bike-intervalado | ok | aviso: penetra |  |
| bike-cadencia | ok | aviso: penetra |  |
| eliptico | ok | aviso: antebraco_pro; atravessa | antebraço com abdução 12 (pronação 128 → 108°, aviso) |
| remo-ergometro | pendente motor | erro | pelve em retroversão na pegada (flexão do quadril ok); pendente motor: abdômen 1,7 cm no carro do assento (limite 1,5) |
| escada | ok | aviso: penetra |  |
| prova | ok | limpo |  |
| caminhada | ok | limpo |  |
| maior-alongamento | erro (dados) | erro | erro: CM fora da base em 4–5 quadros na passagem para o posterior (o pé de trás dá um passo de 2 dm com só mão+pé da frente no chão); variante com joelho de trás no chão testada e descartada (flexão de quadril 170°) |
| gato-camelo | ok | limpo |  |
| postura-crianca | ok | aviso: coluna_extensao; joelho_flexao; pousada; punho_ulnar | pelve −25 (quadril e coluna dentro do limite); avisos de joelho 154° (sentado nos calcanhares) |
| flexor-quadril | ok | aviso: quadril_extensao |  |
| alongamento-posterior | ok | limpo |  |
| alongamento-quadriceps | pendente motor | erro | braço FK quase reto (modo de repouso: rotação externa 179° → ok); pendente motor: pops 5–6 cm do "segura" (alvo pula de vértice) |
| alongamento-panturrilha | ok | aviso: penetra |  |
| circulos-braco | ok | limpo |  |
| circulos-quadril | ok | aviso: corpo |  |
| rolo-quadriceps | ok | aviso: pousada |  |
| rolo-panturrilha | ok | limpo |  |
| rolo-it | ok | aviso: penetra; pousada |  |
| alongamento-peito | pendente motor | erro | pendente motor: dedos 5 cm no batente (`parede` posta pela palma, não pela orientação da mão); rotação do tronco 16/18 (ombro só aviso) |
| rotacao-toracica | pendente motor | erro | rotação torácica 62° (ROM ok); pendente motor: deitado de lado ("lado") sem encostar no tapete no início |
| alongamento-adutores | ok | aviso: congelado |  |
| equilibrio-unipodal | ok | limpo |  |
| balanco-pernas | pendente motor | erro | pendente motor: mão 4 cm no batente (mesma causa do alongamento-peito) |
| circulos-tornozelo | ok | aviso: corpo |  |
| circulos-punho | ok | limpo |  |
| circulos-ombro | ok | limpo |  |
| circulos-joelho | ok | aviso: corpo; punho_extensao |  |
| chute-gluteo | ok | limpo | fases de voo declaradas ("apoio": [] nas chaves de troca): CM fora da base resolvido |
| carioca | ok | limpo |  |
| abertura-peito-dinamica | ok | limpo |  |
| spider | ok | aviso: quadril_flexao | apoios declarados; mão volta ao chão antes de tirar o pé; aviso: flexão do quadril 162° (afundo profundo do alongamento) |
| alongamento-gluteo | pendente motor | erro | pendente motor: pops do "segura" coxa; rotação externa do quadril 93° não responde a pfa/cfa (pose da figura 4 a refazer) |
| abraco-joelhos | ok | aviso: antebraco_sup; ombro_ri | joelhos realmente dobrados no peito (pf [205,80]), mãos nas canelas (bfa 20), balanço ±8 |
| alongamento-triceps | pendente motor | erro | braço de cima com antebraço 318° (sem cotovelo invertido); pendente motor: braço que segura o cotovelo vira 180° no IK do "segura" + pops |
| alongamento-antebraco | ok | aviso: antebraco_sup |  |
| alongamento-pescoco | ok | aviso: congelado |  |
| alongamento-lateral | ok | aviso: corpo | braço de cima sem cruzar a linha média (bfa −15) |
| torcao-coluna | ok | aviso: congelado; corpo; flutua; pousada; punho_radial; punho_ulnar; quadril_flexao | apoios sentados (glúteo, pés, mão de trás), mãos abertas ao lado do quadril no início; avisos de punho/flexão do quadril no limite |
| alongamento-dorsal | ok | aviso: congelado |  |
| moinho | ok | limpo |  |
