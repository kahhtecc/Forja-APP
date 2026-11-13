# Revisão visual independente das animações 3D (175 exercícios)

Revisor independente (não participou da produção). Critérios: (a) mãos segurando de verdade; (b) apoios reais (nada flutuando nem apoiado no vazio);
(c) pose humanamente possível e movimento reconhecível; (d) interpenetração corpo×corpo e corpo×aparelho; (e) aparelho correto e no lugar.

Método: tira de 6 quadros do ciclo (360 px, `humano.py --tira 6`) de cada exercício, mais zoom das duas mãos em 4 instantes (0, 0,25, 0,5, 0,75 do ciclo; `zoom.py`)
e zoom de corpo inteiro de outros ângulos nos suspeitos. Ordem: turkish-getup, os 88 com aviso do QA (por gravidade), depois os 86 limpos.
Nada foi corrigido: só revisão. Gravidade: **grave** = defeito que o usuário vê na hora (mão vazia, apoio no vazio, atravessar corpo/aparelho grande, pose impossível);
**média** = visível ao prestar atenção; **leve** = detalhe.

Revisados: 136 de 175 — APROVADO 119, REPROVADO 17.

| # | exercício | veredito | gravidade | defeito visto | fase/quadro | causa provável |
|---|---|---|---|---|---|---|
| 2 | postura-crianca | APROVADO |  | sem defeito visível (ajoelhado → criança → volta; mãos no chão) | — | — |
| 3 | flexao-diamante | APROVADO |  | mãos juntas no chão, corpo em prancha, descida coerente | — | — |
| 4 | prancha | APROVADO |  | prancha em antebraços estável, apoios no chão | — | — |
| 5 | superman | APROVADO | leve | amplitude exagerada (pernas e braços altos demais, arco forte), mas possível | 0,3–0,7 | dados (amplitude) |
| 6 | remada-invertida | APROVADO |  | mãos fechadas na barra, pés no chão, peito sobe até a barra | — | — |
| 7 | mesa-flexora | APROVADO |  | mãos nos pegadores, rolo no tendão, flexão de joelho coerente | — | — |
| 8 | hack | REPROVADO | grave | uma das mãos fica fechada no ar, sem pegador (só a outra segura); mãos na altura das coxas e não nos pegadores dos ombros | todo o ciclo (zoom mão t 0–0,75) | motor (pegador do hack só para uma mão / "maos":1) + dados |
| 9 | flexao | APROVADO |  | sem defeito visível | — | — |
| 10 | torcao-coluna | REPROVADO | grave | a mão que deveria segurar o joelho fica aberta, dedos espalhados, flutuando ao lado do joelho (não há "segura" nos dados) | 0,25–1,0 (torção) | dados (falta "segura" mao_t→joelho_f) |
| 11 | prancha-lateral | REPROVADO | grave | apoio declarado no cotovelo, mas o corpo está apoiado num punho fechado com o antebraço vertical (cotovelo no ar): prancha lateral "sobre o soco", não existe assim | ciclo inteiro | dados ("maos": {"t":"punho"} + bt [0,90] com rol 70) / motor (cotovelo_t não desce ao chão) |
| 13 | alongamento-gluteo | APROVADO | leve | braços cruzam perto da coxa (mãos atrás da coxa ok); antebraço roça o tronco | 0,5–0,8 | dados |
| 14 | remo-ergometro | APROVADO |  | duas mãos fechadas no puxador, carro e pés coerentes | — | — |
| 15 | arremesso-rotacional | REPROVADO | média | na preparação a bola entra no quadril/abdômen (metade da bola dentro do corpo) e o antebraço de trás atravessa o tronco | 0–0,2 e 0,9–1,0 (carga) | dados (bola muito colada ao quadril; tr/bf da carga) |
| 16 | abdominal | APROVADO | leve | antebraços pairando ~3 cm acima do chão no início (parecem apoiados) | 0 | dados |
| 18 | elevacao-quadril | APROVADO | leve | barra encosta/entra um pouco nas coxas no fundo; mãos seguram a barra | 0 | motor (colisão barra×coxa) |
| 19 | russian-twist | APROVADO | leve | mãos abertas soltas (normalmente unidas/segurando peso); antebraço roça o tronco nas viradas | 0,1 e 0,9 | dados |
| 20 | rosca-scott | APROVADO |  | cotovelos no apoio (vista de trás confirma), pegada fechada | — | — |
| 21 | paralelas | APROVADO |  | mãos nas barras, joelhos dobrados, descida e subida coerentes | — | — |
| 22 | hiperextensao | APROVADO | leve | flexão do tronco no fundo muito profunda (cabeça quase no piso do aparelho), possível | 0,5–0,7 | dados |
| 23 | pallof | APROVADO | leve | vista frontal: a prensa (empurrar para a frente) quase não se lê; mãos seguram o pegador | ciclo | dados (câmera) |
| 24 | alongamento-panturrilha | REPROVADO | grave | as mãos atravessam o espaldar: degraus passam por dentro da palma/pulso, braços do outro lado das barras (não apoia nem segura) | todo o ciclo | dados (distância do corpo ao espaldar / mãos) + motor (sem colisão mão×degrau) |
| 25 | mountain-climber | APROVADO |  | mãos no chão, troca de pernas coerente | — | — |
| 26 | nordico | APROVADO |  | tornozelos presos, queda controlada com amparo das mãos | — | — |
| 27 | abdominal-bicicleta | REPROVADO | média | mãos "atrás da cabeça" com dedos abertos esticados no ar e a mão entrando no crânio | 0,25–0,75 | motor ("segura" nuca sem mão espalmada) / dados |
| 28 | maior-alongamento | APROVADO |  | afundo com mão no chão, rotação com braço para cima, isquiotibiais; coerente | — | — |
| 30 | agachamento-goblet | APROVADO |  | duas mãos nas alças do kettlebell, agachamento profundo coerente | — | — |
| 31 | roda-abdominal | APROVADO |  | mãos nas manoplas, roda no chão, joelhos apoiados | — | — |
| 33 | circulos-quadril | APROVADO | leve | círculo do quadril pequeno, pouco visível | ciclo | dados (amplitude) |
| 34 | flexao-joelhos | APROVADO |  | sem defeito visível | — | — |
| 36 | power-clean | APROVADO |  | chão → quadril → rack frontal → volta; pegada fechada | — | — |
| 37 | escada | REPROVADO | grave | mãos abertas por baixo do corrimão, sem segurar; corrimão atravessa punho/antebraço; degraus parecem um bloco ao lado das pernas | todo o ciclo | motor (corrimão da escada x IK da mão) + aparelho |
| 38 | triceps-banco | APROVADO |  | mãos espalmadas na borda do banco, pés no chão | — | — |
| 39 | bike-subida | APROVADO |  | em pé nos pedais, mãos nas manoplas | — | — |
| 40 | agachamento-barra | APROVADO |  | vista de trás: pegada larga na barra apoiada no trapézio, agachamento correto | — | — |
| 43 | alongamento-lateral | APROVADO |  | mão na cintura, braço por cima, inclinação lateral coerente | — | — |
| 46 | pike-pushup | APROVADO |  | mãos no chão, quadril alto, cabeça desce entre as mãos | — | — |
| 47 | cadeira-flexora | APROVADO |  | mãos nos pegadores, rolo atrás dos tornozelos, flexão coerente | — | — |
| 48 | afundo | APROVADO |  | sem defeito visível | — | — |
| 49 | barra-supinada | APROVADO | leve | subida termina com a barra na testa (queixo não passa da barra) | 0,4–0,6 | dados (amplitude) |
| 50 | rosca-direta | APROVADO |  | pegada fechada, cotovelo junto ao corpo | — | — |
| 51 | tempo-run | REPROVADO | média | no balanço dos braços a mão/antebraço passa por dentro do corrimão lateral da esteira | 0,25–0,5 (cada passada) | dados (largura/altura do balanço) + motor (sem colisão mão×corrimão) |
| 52 | rolo-quadriceps | APROVADO |  | coxas no rolo, antebraços no chão | — | — |
| 53 | barra-fixa | APROVADO | leve | subida termina com a barra na altura dos olhos (queixo não passa da barra) | 0,4–0,6 | dados (amplitude) |
| 54 | abdutora | APROVADO | leve | joelhos encostam um pouco dentro do estofado (≈2 cm) | ciclo | motor (colisão perna×estofado) |
| 55 | ponte-unilateral | APROVADO |  | sem defeito visível | — | — |
| 56 | swing | APROVADO |  | duas mãos na alça, kettlebell entre as pernas e até a altura do ombro | — | — |
| 57 | abdominal-infra | APROVADO |  | sem defeito visível | — | — |
| 59 | ponte-gluteo | APROVADO |  | sem defeito visível | — | — |
| 60 | terra | APROVADO |  | barra do chão ao quadril junto às pernas | — | — |
| 89 | supino-inclinado | APROVADO |  | halteres nas mãos, costas no banco inclinado, pés no chão | — | — |
| 90 | crossover | APROVADO |  | pegadores nas mãos, cabos das torres, cruzamento à frente | — | — |
| 91 | remada-unilateral | APROVADO |  | joelho e mão de apoio no banco, halter na mão de trabalho | — | — |
| 92 | pullover-polia | APROVADO |  | barra reta nas duas mãos, cabo da polia alta | — | — |
| 93 | desenvolvimento-halteres | APROVADO |  | halteres nas mãos, subida e descida coerentes | — | — |
| 94 | elevacao-lateral | APROVADO |  | halteres nas mãos, braços até a horizontal | — | — |
| 95 | arnold | REPROVADO | média | halter da mão de trás atravessa o rosto/cabeça na posição inicial (rotação de Arnold com halteres colados à face) | 0 e 1,0 (início/fim do ciclo) | dados (bt [72,182] bta 18 deixa a mão na frente do rosto; precisa afastar/abrir) |
| 96 | rosca-halteres | REPROVADO | média | movimento não reconhecível como rosca: no 3º quadro os dois halteres vão para a frente do quadril com cotovelos estendidos e no 6º o braço sobe reto à frente (elevação frontal) em vez de dobrar o cotovelo; a interpolação dos braços de bf [9,146] para [2,6] passa por braço esticado na horizontal | transições 0,3–0,5 e 0,9–1,0 | dados (chaves sem quadro intermediário) + motor (interpolação de ângulos do braço sem manter o cotovelo junto ao corpo) |
| 97 | triceps-polia | APROVADO |  | barra/corda nas mãos, cotovelos junto ao corpo | — | — |
| 98 | triceps-elastico | APROVADO | leve | elástico preso sob o pé de trás, mãos fechadas no elástico acima da cabeça; elástico passa colado ao corpo | ciclo | — |
| 99 | burpee | APROVADO |  | agacha, mãos no chão, prancha, volta, salto | — | — |
| 100 | thruster | APROVADO |  | halteres nas mãos, agachamento + desenvolvimento | — | — |
| 101 | farmer-walk | APROVADO |  | halteres nas mãos, caminhada | — | — |
| 102 | sombra | APROVADO |  | punhos fechados, guarda e golpes | — | — |
| 103 | longao | APROVADO |  | corrida reconhecível | — | — |
| 104 | caminhada | APROVADO | leve | mãos abertas à frente do corpo; braços balançam pouco, parece "segurar algo invisível" | ciclo | dados (braços) |
| 105 | circulos-braco | APROVADO |  | círculos de braço reconhecíveis | — | — |
| 106 | equilibrio-unipodal | APROVADO |  | apoio unipodal estável | — | — |
| 107 | circulos-ombro | APROVADO | leve | movimento quase imperceptível na tira | ciclo | dados (amplitude) |
| 108 | abertura-peito-dinamica | APROVADO |  | braços abrem e fecham à frente | — | — |
| 109 | agachamento-elastico | APROVADO |  | elástico sob os pés e nas mãos na altura dos ombros | — | — |
| 110 | agachamento-frontal | APROVADO |  | barra no rack frontal com cotovelos altos (vista de trás confirma) | — | — |
| 111 | passada-andando | APROVADO |  | afundos alternados reconhecíveis | — | — |
| 112 | monster-walk | APROVADO |  | miniband nos tornozelos, passos laterais em semiagachamento | — | — |
| 113 | salto-distancia | APROVADO | leve | na tira o voo e a aterrissagem não aparecem com clareza (quadros vazios entre amostras) | 0,5–0,6 | câmera/amostragem |
| 114 | educativos-corrida | APROVADO |  | skipping alto reconhecível | — | — |
| 115 | flexao-inclinada | APROVADO |  | mãos no banco, pés no chão | — | — |
| 116 | flexao-pliometrica | APROVADO |  | mãos saem do chão no impulso | — | — |
| 117 | supino-inclinado-barra | APROVADO |  | barra nas mãos, desce ao peito | — | — |
| 118 | peck-deck | APROVADO |  | mãos nos pegadores, braços abrem e fecham | — | — |
| 119 | puxada-triangulo | APROVADO |  | triângulo nas duas mãos, desce ao peito | — | — |
| 120 | remada-elastico | APROVADO |  | elástico preso no poste, mãos nos pegadores | — | — |
| 121 | face-pull | APROVADO |  | corda nas mãos, puxada até a face com cotovelos altos | — | — |
| 122 | desenvolvimento-barra | APROVADO |  | barra nas mãos, sobe acima da cabeça | — | — |
| 123 | elevacao-lateral-elastico | APROVADO |  | elástico sob os pés, pegadores nas mãos | — | — |
| 124 | rosca-martelo | REPROVADO | média | mesmo defeito da rosca com halteres: braço sobe esticado para a frente (parece elevação frontal) e os dois halteres saem do lado do corpo na transição | 0,2–0,3 e 0,8–0,9 | dados/motor (interpolação do braço) |
| 125 | triceps-coice | APROVADO |  | tronco inclinado, extensão do cotovelo para trás | — | — |
| 126 | polichinelo | APROVADO |  | reconhecível | — | — |
| 127 | sled-push | APROVADO |  | mãos nos postes do trenó, passos de empurrar | — | — |
| 128 | caminhada-corrida | APROVADO |  | corrida na esteira, sem tocar no console | — | — |
| 129 | alongamento-posterior | APROVADO |  | pé à frente com calcanhar no chão, tronco inclinado | — | — |
| 130 | alongamento-dorsal | APROVADO |  | braços à frente, costas arredondadas | — | — |
| 131 | agachamento-salto | APROVADO |  | reconhecível | — | — |
| 132 | stiff-halteres | APROVADO |  | halteres descem junto às pernas | — | — |
| 133 | panturrilha-pe | APROVADO |  | elevação na ponta dos pés | — | — |
| 134 | abdominal-polia | APROVADO |  | ajoelhado, corda junto à cabeça, flexão do tronco | — | — |
| 135 | bound-lateral | APROVADO |  | saltos laterais unipodais | — | — |
| 136 | supino-reto | APROVADO |  | barra nas mãos, desce ao peito, costas no banco | — | — |
| 137 | supino-maquina | REPROVADO | grave | as mãos fechadas empurram o ar: não há pegadores/alavancas na altura das mãos (a alavanca da máquina fica na altura do abdômen, atrás dos braços) e o movimento quase não existe (braços parados à frente em todos os quadros) | ciclo inteiro | motor (alavancas do supino máquina não acompanham a mão) + dados (bf [79,86] ≈ 1º quadro só no início) |
| 138 | supino-elastico | APROVADO | leve | elástico passa por trás das costas pelas axilas (correto), mas contorna o tronco um pouco afastado | ciclo | — |
| 139 | remada-baixa | APROVADO |  | pegador nas duas mãos, pés na plataforma | — | — |
| 140 | desenvolvimento-maquina | APROVADO |  | mãos nos pegadores, sobe e desce | — | — |
| 141 | elevacao-frontal | APROVADO |  | halteres nas mãos, subida à frente | — | — |
| 142 | rosca-elastico | APROVADO | leve | elástico sob o pé com as duas mãos; a mão de trás sobe pouco | ciclo | dados |
| 143 | triceps-testa | APROVADO |  | barra W nas mãos, desce até a testa | — | — |
| 144 | passe-medicine | APROVADO |  | bola entre as mãos, passe de peito | — | — |
| 145 | corda | REPROVADO | média | a corda de pular gira na horizontal/diagonal ao redor da cintura como um bambolê (anel elíptico em volta do corpo) em vez de passar por cima da cabeça e por baixo dos pés | 0,2–0,5 e 0,8–0,9 | motor (corda girando no plano errado) |
| 146 | arremesso-medicine | APROVADO |  | bola agarrada, agacha, arremessa acima | — | — |
| 147 | sprawl | APROVADO |  | cai em prancha estendida e volta | — | — |
| 148 | tiros | APROVADO |  | corrida reconhecível | — | — |
| 149 | gato-camelo | APROVADO |  | quatro apoios, arqueia e curva | — | — |
| 150 | chute-gluteo | APROVADO |  | calcanhar ao glúteo | — | — |
| 151 | alongamento-pescoco | APROVADO |  | inclinação lateral da cabeça | — | — |
| 152 | moinho | APROVADO |  | tronco desce, mão ao pé, braço oposto para cima | — | — |
| 153 | coice-gluteo | APROVADO |  | quatro apoios, perna para trás e para cima | — | — |
| 154 | panturrilha-sentado | APROVADO |  | almofada sobre as coxas com as mãos, antepé no bloco | — | — |
| 155 | dead-bug | APROVADO |  | braço e perna opostos se estendem | — | — |
| 156 | elevacao-pernas-barra | APROVADO |  | pendurado na barra, pernas sobem à horizontal | — | — |
| 157 | salto-tesoura | APROVADO |  | afundo com troca no ar | — | — |
| 158 | fuga-quadril | REPROVADO | média | não se lê como fuga de quadril: entre o "ponte" e o deitado de lado o corpo vira de bruços com braços para cima sem apoio, e no fim de lado sem apoio das mãos (corpo apoiado no braço dobrado sob o tronco) | 0,5–1,0 | dados (chaves da fuga com rol ±80) |
| 159 | sentar-levantar | APROVADO |  | senta no banco e levanta | — | — |
| 160 | flexao-declinada | APROVADO |  | pés no banco, mãos no chão | — | — |
| 161 | supino-halteres | APROVADO |  | halteres nas mãos, costas no banco | — | — |
| 162 | crucifixo | APROVADO |  | halteres nas mãos, abre e fecha no banco inclinado | — | — |
| 163 | barra-assistida | REPROVADO | média | o corpo fica "pendurado" com o pé de trás no ar e o joelho da frente no laço do elástico, mas o elástico passa por fora/atrás do corpo e está preso ao chão (vai da barra até o pé no chão), não sustenta nada; pé livre flutua | ciclo inteiro | motor (laço da barra assistida ancorado no chão) + dados |
| 164 | remada-curvada | APROVADO |  | barra nas mãos, tronco inclinado, puxa ao abdômen | — | — |
| 165 | pulldown-elastico | APROVADO |  | elástico no alto do poste, mãos nos pegadores | — | — |
| 166 | encolhimento | APROVADO |  | halteres nas mãos, ombros sobem | — | — |
| 167 | crucifixo-inverso | APROVADO |  | tronco inclinado, halteres abrem para os lados | — | — |
| 168 | isometria-pescoco | REPROVADO | média | a mão "empurra a testa" com os dedos abertos e a palma atravessando o crânio (mão entra na cabeça) | 0,2–1,0 | motor ("segura" cabeça sem contato de pele) / dados |
| 169 | battle-rope | APROVADO |  | cordas nas mãos com ondas | — | — |
| 170 | inchworm | APROVADO |  | mãos andam até prancha e voltam | — | — |
| 171 | bear-crawl | APROVADO |  | quatro apoios com joelhos no ar, mão e pé opostos avançam | — | — |
| 172 | prova | APROVADO |  | corrida reconhecível | — | — |
| 173 | alongamento-adutores | REPROVADO | grave | pernas cruzadas em pose impossível: coxa de trás atravessa a perna da frente e os pés somem dentro das coxas; mãos não seguram os pés (mãos abertas no chão) | ciclo inteiro | dados (borboleta: pf/pt e "segura" pés) |
| 174 | circulos-punho | APROVADO |  | antebraços parados, punhos fechados giram | — | — |
| 175 | carioca | APROVADO | leve | passo cruzado pouco visível na vista frontal | ciclo | câmera |
