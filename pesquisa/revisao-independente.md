# Revisão visual independente das animações 3D (175 exercícios)

Revisor independente (não participou da produção). Critérios: (a) mãos segurando de verdade; (b) apoios reais (nada flutuando nem apoiado no vazio);
(c) pose humanamente possível e movimento reconhecível; (d) interpenetração corpo×corpo e corpo×aparelho; (e) aparelho correto e no lugar.

Método: tira de 6 quadros do ciclo (360 px, `humano.py --tira 6`) de cada exercício, mais zoom das duas mãos em 4 instantes (0, 0,25, 0,5, 0,75 do ciclo; `zoom.py`)
e zoom de corpo inteiro de outros ângulos nos suspeitos. Ordem: turkish-getup, os 88 com aviso do QA (por gravidade), depois os 86 limpos.
Nada foi corrigido: só revisão. Gravidade: **grave** = defeito que o usuário vê na hora (mão vazia, apoio no vazio, atravessar corpo/aparelho grande, pose impossível);
**média** = visível ao prestar atenção; **leve** = detalhe.

Revisados: 175 de 175 — APROVADO 156, REPROVADO 19.

| # | exercício | veredito | gravidade | defeito visto | fase/quadro | causa provável |
|---|---|---|---|---|---|---|
| 1 | turkish-getup | APROVADO | leve | sequência legível (deitado → cotovelo → mão → ponte → joelho → em pé e volta), kettlebell sempre na mão; o "erro" do QA não aparece como defeito visível. Detalhes: punho do kettlebell dobrado para trás no deitado e braço de apoio muito aberto atrás no sentar | 0,02–0,14 | dados (detalhe) |
| 2 | postura-crianca | APROVADO |  | sem defeito visível (ajoelhado → criança → volta; mãos no chão) | — | — |
| 3 | flexao-diamante | APROVADO |  | mãos juntas no chão, corpo em prancha, descida coerente | — | — |
| 4 | prancha | APROVADO |  | prancha em antebraços estável, apoios no chão | — | — |
| 5 | superman | APROVADO | leve | amplitude exagerada (pernas e braços altos demais, arco forte), mas possível | 0,3–0,7 | dados (amplitude) |
| 6 | remada-invertida | APROVADO → **CORRIGIDO** (dados, pós-revisão: (QA) desce mais no fundo; amplitude do cotovelo 48 → 59°, sem aviso) |  | mãos fechadas na barra, pés no chão, peito sobe até a barra | — | — |
| 7 | mesa-flexora | APROVADO |  | mãos nos pegadores, rolo no tendão, flexão de joelho coerente | — | — |
| 8 | hack | REPROVADO → **CORRIGIDO** (motor, rodada pós-revisão em motor-pendencias.md) | grave | uma das mãos fica fechada no ar, sem pegador (só a outra segura); mãos na altura das coxas e não nos pegadores dos ombros | todo o ciclo (zoom mão t 0–0,75) | motor (pegador do hack só para uma mão / "maos":1) + dados |
| 9 | flexao | APROVADO |  | sem defeito visível | — | — |
| 10 | torcao-coluna | REPROVADO → **CORRIGIDO** (dados, pós-revisão: mão de trás segura o joelho (abraço) o ciclo todo) | grave | a mão que deveria segurar o joelho fica aberta, dedos espalhados, flutuando ao lado do joelho (não há "segura" nos dados) | 0,25–1,0 (torção) | dados (falta "segura" mao_t→joelho_f) |
| 11 | prancha-lateral | REPROVADO → **CORRIGIDO** (dados, pós-revisão: antebraço e mão espalmada no chão, câmera 100/30) | grave | apoio declarado no cotovelo, mas o corpo está apoiado num punho fechado com o antebraço vertical (cotovelo no ar): prancha lateral "sobre o soco", não existe assim | ciclo inteiro | dados ("maos": {"t":"punho"} + bt [0,90] com rol 70) / motor (cotovelo_t não desce ao chão) |
| 12 | rotacao-toracica | APROVADO | leve | deitado de lado com joelhos empilhados, braço de cima abre para o outro lado; na abertura máxima os joelhos se descolam um pouco (perna de cima sobe) | 0,4–0,6 | dados |
| 13 | alongamento-gluteo | APROVADO | leve | braços cruzam perto da coxa (mãos atrás da coxa ok); antebraço roça o tronco | 0,5–0,8 | dados |
| 14 | remo-ergometro | APROVADO |  | duas mãos fechadas no puxador, carro e pés coerentes | — | — |
| 15 | arremesso-rotacional | REPROVADO → **CORRIGIDO** (dados, pós-revisão: bola à frente do quadril de trás na carga) | média | na preparação a bola entra no quadril/abdômen (metade da bola dentro do corpo) e o antebraço de trás atravessa o tronco | 0–0,2 e 0,9–1,0 (carga) | dados (bola muito colada ao quadril; tr/bf da carga) |
| 16 | abdominal | APROVADO | leve | antebraços pairando ~3 cm acima do chão no início (parecem apoiados) | 0 | dados |
| 17 | abraco-joelhos | APROVADO |  | deitado, mãos nas canelas puxando os joelhos | — | — |
| 18 | elevacao-quadril | APROVADO | leve | barra encosta/entra um pouco nas coxas no fundo; mãos seguram a barra | 0 | motor (colisão barra×coxa) |
| 19 | russian-twist | APROVADO | leve | mãos abertas soltas (normalmente unidas/segurando peso); antebraço roça o tronco nas viradas | 0,1 e 0,9 | dados |
| 20 | rosca-scott | APROVADO |  | cotovelos no apoio (vista de trás confirma), pegada fechada | — | — |
| 21 | paralelas | APROVADO |  | mãos nas barras, joelhos dobrados, descida e subida coerentes | — | — |
| 22 | hiperextensao | APROVADO | leve | flexão do tronco no fundo muito profunda (cabeça quase no piso do aparelho), possível | 0,5–0,7 | dados |
| 23 | pallof | APROVADO | leve | vista frontal: a prensa (empurrar para a frente) quase não se lê; mãos seguram o pegador | ciclo | dados (câmera) |
| 24 | alongamento-panturrilha | REPROVADO → **CORRIGIDO** (motor, rodada pós-revisão em motor-pendencias.md) | grave | as mãos atravessam o espaldar: degraus passam por dentro da palma/pulso, braços do outro lado das barras (não apoia nem segura) | todo o ciclo | dados (distância do corpo ao espaldar / mãos) + motor (sem colisão mão×degrau) |
| 25 | mountain-climber | APROVADO |  | mãos no chão, troca de pernas coerente | — | — |
| 26 | nordico | APROVADO |  | tornozelos presos, queda controlada com amparo das mãos | — | — |
| 27 | abdominal-bicicleta | REPROVADO → **CORRIGIDO** (dados, pós-revisão: punho estendido: dedos não entram no crânio (4,9 → 1,9 cm)) | média | mãos "atrás da cabeça" com dedos abertos esticados no ar e a mão entrando no crânio | 0,25–0,75 | motor ("segura" nuca sem mão espalmada) / dados |
| 28 | maior-alongamento | APROVADO |  | afundo com mão no chão, rotação com braço para cima, isquiotibiais; coerente | — | — |
| 29 | box-jump | APROVADO |  | salto para cima da caixa e descida em passo | — | — |
| 30 | agachamento-goblet | APROVADO |  | duas mãos nas alças do kettlebell, agachamento profundo coerente | — | — |
| 31 | roda-abdominal | APROVADO |  | mãos nas manoplas, roda no chão, joelhos apoiados | — | — |
| 32 | eliptico | REPROVADO → **CORRIGIDO** (motor, rodada pós-revisão em motor-pendencias.md) | grave | a mão de trás solta a alça móvel: de 0,25 a 0,75 fica aberta ao lado da coluna/console, sem segurar nada (só a mão da frente segura) | 0,25–0,75 | motor (IK das alças do elíptico só para uma mão / alvo da mão de trás) |
| 33 | circulos-quadril | APROVADO | leve | círculo do quadril pequeno, pouco visível | ciclo | dados (amplitude) |
| 34 | flexao-joelhos | APROVADO |  | sem defeito visível | — | — |
| 35 | leg-press | APROVADO | leve | mão de trás escondida sob a coxa (não dá para confirmar que segura o pegador); pés na placa, costas no encosto | ciclo | — |
| 36 | power-clean | APROVADO |  | chão → quadril → rack frontal → volta; pegada fechada | — | — |
| 37 | escada | REPROVADO → **CORRIGIDO** (motor, rodada pós-revisão em motor-pendencias.md) | grave | mãos abertas por baixo do corrimão, sem segurar; corrimão atravessa punho/antebraço; degraus parecem um bloco ao lado das pernas | todo o ciclo | motor (corrimão da escada x IK da mão) + aparelho |
| 38 | triceps-banco | APROVADO |  | mãos espalmadas na borda do banco, pés no chão | — | — |
| 39 | bike-subida | APROVADO |  | em pé nos pedais, mãos nas manoplas | — | — |
| 40 | agachamento-barra | APROVADO |  | vista de trás: pegada larga na barra apoiada no trapézio, agachamento correto | — | — |
| 41 | balanco-pernas | APROVADO | leve | palma na parede, perna balança; no balanço para a frente o pé passa rente ao batente | 0,9–1,0 | dados |
| 42 | bike-intervalado | APROVADO | leve | selim baixo/recuado: joelho sobe quase até o guidão e o glúteo fica na ponta de trás do selim (parece "empoleirado"); mãos no guidão, pés nos pedais | ciclo | dados (y/x do quadril) ou aparelho (altura do selim) |
| 43 | alongamento-lateral | APROVADO |  | mão na cintura, braço por cima, inclinação lateral coerente | — | — |
| 44 | alongamento-triceps | APROVADO | leve | mão que puxa o cotovelo fica com os dedos abertos (encosta, não segura) | 0,3–0,7 | motor ("segura" cotovelo sem fechar os dedos) |
| 45 | puxada-frente | APROVADO |  | barra nas mãos, desce à frente do rosto até o peito | — | — |
| 46 | pike-pushup | APROVADO |  | mãos no chão, quadril alto, cabeça desce entre as mãos | — | — |
| 47 | cadeira-flexora | APROVADO |  | mãos nos pegadores, rolo atrás dos tornozelos, flexão coerente | — | — |
| 48 | afundo | APROVADO |  | sem defeito visível | — | — |
| 49 | barra-supinada | APROVADO | leve | subida termina com a barra na testa (queixo não passa da barra) | 0,4–0,6 | dados (amplitude) |
| 50 | rosca-direta | REPROVADO → **CORRIGIDO** (motor, rodada pós-revisão em motor-pendencias.md) | grave | a rosca não é uma rosca: na subida e na descida o braço inteiro vai para a frente esticado (cotovelo reto, ombro a ~60–80°, como elevação frontal) e só no topo dobra o cotovelo; nos dados o ombro varia só 2→10° e o cotovelo 6→146° | 0,05–0,3 e 0,6–0,95 (vista 3/4 de trás) | motor (direção dos braços por arco de círculo máximo em movimento.py: o antebraço é interpolado em direção de mundo e arrasta o úmero para a frente) |
| 51 | tempo-run | APROVADO | leve | no balanço dos braços a mão roça o corrimão lateral da esteira (≈1,5 cm, 1–2 quadros por passada) | 0,25–0,5 | dados (largura do balanço) + motor (sem colisão mão×corrimão) |
| 52 | rolo-quadriceps | APROVADO |  | coxas no rolo, antebraços no chão | — | — |
| 53 | barra-fixa | APROVADO | leve | subida termina com a barra na altura dos olhos (queixo não passa da barra) | 0,4–0,6 | dados (amplitude) |
| 54 | abdutora | APROVADO | leve | joelhos encostam um pouco dentro do estofado (≈2 cm) | ciclo | motor (colisão perna×estofado) |
| 55 | ponte-unilateral | APROVADO |  | sem defeito visível | — | — |
| 56 | swing | APROVADO |  | duas mãos na alça, kettlebell entre as pernas e até a altura do ombro | — | — |
| 57 | abdominal-infra | APROVADO |  | sem defeito visível | — | — |
| 58 | bike-cadencia | APROVADO | leve | mesmo enquadramento e pose da bike-intervalado (tiras praticamente idênticas); selim baixo, joelho alto | ciclo | dados |
| 59 | ponte-gluteo | APROVADO |  | sem defeito visível | — | — |
| 60 | terra | APROVADO |  | barra do chão ao quadril junto às pernas | — | — |
| 61 | bike-leve | APROVADO | leve | mesma pose das outras bikes sentadas (vista lateral confirma glúteo no selim); joelho alto | ciclo | dados |
| 62 | triceps-frances | APROVADO |  | halter nas duas mãos, desce atrás da cabeça | — | — |
| 63 | rolo-panturrilha | APROVADO |  | panturrilhas no rolo, mãos no chão atrás | — | — |
| 64 | alongamento-antebraco | APROVADO |  | quatro apoios com dedos para trás | — | — |
| 65 | desenvolvimento-elastico | APROVADO |  | elástico sob os pés, mãos fechadas no elástico | — | — |
| 66 | circulos-tornozelo | APROVADO |  | mãos na cintura, ponta do pé no chão girando | — | — |
| 67 | flexor-quadril | APROVADO |  | semiajoelhado, braço sobe | — | — |
| 68 | bulgaro | APROVADO | leve | no fundo o halter da mão de perto passa rente/na frente da coxa da perna de apoio (parece encostar) | 0,5–0,7 | dados (bfa) |
| 69 | spider | APROVADO |  | prancha, pé ao lado da mão, rotação com braço para cima | — | — |
| 70 | alongamento-peito | APROVADO |  | antebraço no batente, tronco gira | — | — |
| 71 | cadeira-extensora | APROVADO |  | sentado, rolo nos tornozelos, extensão do joelho | — | — |
| 72 | crucifixo-elastico | APROVADO |  | elástico preso atrás, pegadores nas mãos, braços fecham à frente | — | — |
| 73 | corrida-leve | APROVADO | leve | mesmo roçar da mão no corrimão lateral da esteira (≈1,4 cm, 2 quadros) | 0,25–0,5 | dados/motor |
| 74 | ponte-pescoco | APROVADO | leve | na ponte os braços ficam estendidos para cima no ar (sem função; normalmente cruzados no peito ou no chão) | 0,2–0,7 | dados (braços) |
| 75 | step-up | APROVADO |  | halteres nas mãos, sobe e desce da caixa | — | — |
| 76 | canivete | APROVADO |  | V-up reconhecível | — | — |
| 77 | saco-combinacoes | APROVADO |  | golpes em direção ao saco, punhos fechados | — | — |
| 78 | rotacao-externa | APROVADO |  | elástico do poste à mão, cotovelo junto ao corpo | — | — |
| 79 | band-pull-apart | APROVADO |  | elástico nas duas mãos, abre à altura do peito | — | — |
| 80 | circulos-joelho | APROVADO |  | mãos nos joelhos, círculos | — | — |
| 81 | stiff | APROVADO | leve | no fundo as anilhas ficam rente ao chão (parecem tocar o piso) | 0,5–0,7 | dados (profundidade) |
| 82 | rolo-it | APROVADO |  | deitado de lado sobre o rolo, antebraço e pé de cima apoiados | — | — |
| 83 | alongamento-quadriceps | REPROVADO → **CORRIGIDO** (dados, pós-revisão: mão segura o tornozelo, dedos em volta) | média | a mão que deveria segurar o pé fica espalmada sobre o dorso do pé/canela com os dedos abertos (encosta, não agarra o tornozelo) | 0,25–0,75 | motor ("segura" pé sem fechar a mão) |
| 84 | terra-uma-perna | APROVADO |  | kettlebell numa mão, perna de trás sobe, mão livre ao lado | — | — |
| 85 | agachamento-livre | APROVADO |  | reconhecível | — | — |
| 86 | afundo-halteres | APROVADO |  | halteres nas mãos, afundo e volta | — | — |
| 87 | panturrilha-elastico | APROVADO |  | elástico sob os pés, mãos nos ombros | — | — |
| 88 | tuck-jump | APROVADO |  | salto com joelhos ao peito | — | — |
| 89 | supino-inclinado | APROVADO |  | halteres nas mãos, costas no banco inclinado, pés no chão | — | — |
| 90 | crossover | APROVADO |  | pegadores nas mãos, cabos das torres, cruzamento à frente | — | — |
| 91 | remada-unilateral | APROVADO |  | joelho e mão de apoio no banco, halter na mão de trabalho | — | — |
| 92 | pullover-polia | APROVADO |  | barra reta nas duas mãos, cabo da polia alta | — | — |
| 93 | desenvolvimento-halteres | APROVADO |  | halteres nas mãos, subida e descida coerentes | — | — |
| 94 | elevacao-lateral | APROVADO |  | halteres nas mãos, braços até a horizontal | — | — |
| 95 | arnold | REPROVADO → **CORRIGIDO** (dados, pós-revisão: halteres na altura do queixo e mais abertos no início) | média | halter da mão de trás atravessa o rosto/cabeça na posição inicial (rotação de Arnold com halteres colados à face) | 0 e 1,0 (início/fim do ciclo) | dados (bt [72,182] bta 18 deixa a mão na frente do rosto; precisa afastar/abrir) |
| 96 | rosca-halteres | REPROVADO → **CORRIGIDO** (motor, rodada pós-revisão em motor-pendencias.md) | grave | mesmo defeito da rosca direta: halter sobe com o braço esticado à frente (elevação frontal) em vez de dobrar o cotovelo junto ao corpo; nos dados ombro 2→9° e cotovelo 6→146° | transições de cada braço | motor (arco de círculo máximo dos braços) |
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
| 124 | rosca-martelo | REPROVADO → **CORRIGIDO** (motor, rodada pós-revisão em motor-pendencias.md) | grave | mesmo defeito: braço sobe esticado à frente antes de dobrar; dados com ombro 2→10° e cotovelo 6→140° | transições | motor (arco de círculo máximo dos braços) |
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
| 137 | supino-maquina | REPROVADO → **CORRIGIDO** (motor, rodada pós-revisão em motor-pendencias.md) | grave | não há movimento: braços ficam esticados à frente em todos os quadros (0,1–0,9 idênticos) apesar de o 1º quadro dos dados ter cotovelos atrás (bf [-28,102]); as mãos parecem presas no pegador parado da alavanca | ciclo inteiro | motor (alavanca/pegador do supino máquina não acompanha a pose; IK prende a mão) |
| 138 | supino-elastico | APROVADO | leve | elástico passa por trás das costas pelas axilas (correto), mas contorna o tronco um pouco afastado | ciclo | — |
| 139 | remada-baixa | APROVADO |  | pegador nas duas mãos, pés na plataforma | — | — |
| 140 | desenvolvimento-maquina | APROVADO |  | mãos nos pegadores, sobe e desce | — | — |
| 141 | elevacao-frontal | APROVADO |  | halteres nas mãos, subida à frente | — | — |
| 142 | rosca-elastico | REPROVADO → **CORRIGIDO** (motor, rodada pós-revisão em motor-pendencias.md) | grave | mesmo defeito das roscas: a mão da frente sai esticada para a frente na transição (quadros 2 e 5 da tira) | transições | motor (arco de círculo máximo dos braços) |
| 143 | triceps-testa | APROVADO |  | barra W nas mãos, desce até a testa | — | — |
| 144 | passe-medicine | APROVADO |  | bola entre as mãos, passe de peito | — | — |
| 145 | corda | REPROVADO → **CORRIGIDO** (motor, rodada pós-revisão em motor-pendencias.md) | média | a corda de pular gira na horizontal/diagonal ao redor da cintura como um bambolê (anel elíptico em volta do corpo) em vez de passar por cima da cabeça e por baixo dos pés | 0,2–0,5 e 0,8–0,9 | motor (corda girando no plano errado) |
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
| 158 | fuga-quadril | REPROVADO → **CORRIGIDO** (dados, pós-revisão: recoreografada: shrimp de lado (estendido → C), câmera de cima) | média | não se lê como fuga de quadril: os braços ficam estendidos no ar (não empurram nada) e o corpo só rola de lado sem levar o quadril para trás; na volta a pose deitada de lado tem o braço de baixo dobrado sob o tronco | 0,1–0,3 e 0,6–0,9 | dados (chaves com rol ±75 e braços bf [125,135]) |
| 159 | sentar-levantar | APROVADO |  | senta no banco e levanta | — | — |
| 160 | flexao-declinada | APROVADO |  | pés no banco, mãos no chão | — | — |
| 161 | supino-halteres | APROVADO |  | halteres nas mãos, costas no banco | — | — |
| 162 | crucifixo | APROVADO |  | halteres nas mãos, abre e fecha no banco inclinado | — | — |
| 163 | barra-assistida | APROVADO | leve | pé no laço do elástico com a perna estendida à frente e elástico em diagonal (o normal é o joelho/pé sob o corpo com o elástico vertical); a outra perna pendurada | ciclo | dados (perna do laço) |
| 164 | remada-curvada | APROVADO |  | barra nas mãos, tronco inclinado, puxa ao abdômen | — | — |
| 165 | pulldown-elastico | APROVADO |  | elástico no alto do poste, mãos nos pegadores | — | — |
| 166 | encolhimento | APROVADO |  | halteres nas mãos, ombros sobem | — | — |
| 167 | crucifixo-inverso | APROVADO |  | tronco inclinado, halteres abrem para os lados | — | — |
| 168 | isometria-pescoco | REPROVADO → **CORRIGIDO** (dados, pós-revisão: palma deitada na testa, câmera de frente) | média | a mão "empurra a testa" com os dedos abertos e a palma atravessando o crânio (mão entra na cabeça) | 0,2–1,0 | motor ("segura" cabeça sem contato de pele) / dados |
| 169 | battle-rope | APROVADO |  | cordas nas mãos com ondas | — | — |
| 170 | inchworm | APROVADO |  | mãos andam até prancha e voltam | — | — |
| 171 | bear-crawl | APROVADO |  | quatro apoios com joelhos no ar, mão e pé opostos avançam | — | — |
| 172 | prova | APROVADO |  | corrida reconhecível | — | — |
| 173 | alongamento-adutores | REPROVADO → **CORRIGIDO** (dados, pós-revisão: recoreografada: sentado, joelhos abertos, pés juntos, mãos nos pés) | média | não se lê como borboleta: o corpo fica de cócoras sentado sobre os pés (vista de trás), com a perna de trás atravessando a da frente na vista 3/4 e mãos soltas perto dos pés; a borboleta real é sentado no chão com as solas unidas e joelhos abertos | ciclo inteiro | dados (pf/pt, t/c do sentado) + motor (segura pés) |
| 174 | circulos-punho | APROVADO |  | antebraços parados, punhos fechados giram | — | — |
| 175 | carioca | APROVADO | leve | passo cruzado pouco visível na vista frontal | ciclo | câmera |

## Reprovados por gravidade

**Grave (12)**
1. **rosca-direta, rosca-halteres, rosca-martelo, rosca-elastico** (mesma causa): o braço sobe esticado à frente, como numa elevação frontal, e só dobra o cotovelo no topo. Os dados estão certos (ombro de 2 a 10°, cotovelo de 6 a 146°). A causa provável está no motor: a direção do antebraço é interpolada por arco de círculo máximo em `movimento.py` (`TrilhasPose.__call__`, `slerp_v` dos segmentos "b"/"a") e o IK leva o úmero junto. O QA dá "ok" ou só um aviso de supinação.
2. **supino-maquina**: os braços ficam parados e esticados no ciclo inteiro, porque a mão fica presa ao pegador parado. O QA dá "ok".
3. **eliptico**: a mão de trás solta a alça móvel e fica aberta no ar entre 0,25 e 0,75 do ciclo.
4. **escada**: as mãos ficam abertas por baixo do corrimão e o corrimão atravessa punho e antebraço.
5. **hack**: só uma mão segura o pegador; a outra fica fechada no ar.
6. **alongamento-panturrilha**: mãos e antebraços atravessam os degraus do espaldar.
7. **torcao-coluna**: a mão que devia segurar o joelho fica aberta e flutuando ao lado dele.
8. **prancha-lateral**: o corpo se apoia num punho fechado com o antebraço vertical, quando o certo é o cotovelo e o antebraço deitados no chão.

**Média (7)**: arnold (o halter atravessa o rosto no início), arremesso-rotacional (a bola entra no quadril na carga),
abdominal-bicicleta e isometria-pescoco (mão aberta "atrás ou na frente da cabeça" entrando no crânio), alongamento-quadriceps
(a mão fica espalmada no pé e não agarra), corda (a corda gira como um bambolê na cintura), fuga-quadril e alongamento-adutores (movimento ou pose
que não se reconhece como o exercício real).

## O que o QA automático não está pegando

- **Trajetória entre as chaves.** O QA mede limites, contato e penetração quadro a quadro, mas não compara o caminho com o movimento real. As 4 roscas
  "levantam o braço esticado" e passam como ok ou só com aviso. Falta checar que a distância entre cotovelo e tronco (e o ângulo do ombro) fica perto do valor das chaves durante as
  transições, sem passar de max(chaves) mais uma margem.
- **Mão que deveria segurar e não segura** quando o alvo é parte do corpo ("segura" nuca, cabeça, pé, joelho, cotovelo). O QA olha a pegada
  só em implementos. Precisa medir a distância entre a pele da palma e o alvo e o fechamento dos dedos: mão aberta com dedos esticados não conta como "segura".
- **Mão que deveria estar num pegador e está livre** (elíptico, hack, supino máquina, escada). Se o aparelho tem dois pegadores,
  as duas mãos devem estar presas em todos os quadros. Hoje a ausência de contato não gera achado.
- **Ausência de movimento.** Um ciclo com amplitude quase nula, como o supino-maquina, não é sinalizado. Basta comparar a amplitude renderizada com a amplitude
  dos dados (ex.: |Δcotovelo| real < 30 % do previsto vira erro).
- **Interpenetração mão×cabeça e implemento×corpo nas mãos.** O halter que atravessa o rosto (arnold), a bola que entra no quadril (arremesso-rotacional) e a
  mão que entra no crânio (isometria/bicicleta) não aparecem. O teste corpo×corpo parece cobrir só pernas e tronco.
- **Penetração "rasa" em tubos finos.** No espaldar e na escada, o QA mede 1,4–1,5 cm (só aviso), mas visualmente o degrau passa por dentro
  da mão. A profundidade sozinha não basta para tubo fino: falta testar se o eixo do tubo cruza o volume da mão ou do antebraço.
- **Apoio declarado diferente do apoio visível.** Na prancha-lateral o apoio declarado é o "cotovelo_t", mas quem toca o chão é o punho. O QA
  aceita porque alguma parte do braço toca.
- **Plano de rotação de implementos animados** (corda de pular girando na horizontal): não há nenhuma verificação.
- **Pose reconhecível** (borboleta, fuga de quadril): só um revisor humano pega. Sugestão: uma folha de contato por exercício
  revisada a cada rodada do motor, com a ficha "pose de referência" ao lado.

## Observação sobre o turkish-getup

É o único "erro" do QA, mas visualmente não está entre os piores. A sequência deitado → cotovelo → mão → ponte → joelho → em pé e a volta
se leem bem e o kettlebell fica na mão o tempo todo. Ficaram só detalhes (punho dobrado no deitado e braço de apoio muito aberto atrás).

