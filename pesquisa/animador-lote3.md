# Animador lote3: andamento

QA = `tools/anim3d/qa.py` rodado só no id (motor de 4217049 + qa de 33fd5cb). "aviso" só quando há justificativa (anotada).
Conferência visual: tiras de 8–10 quadros e zoom de mãos/pés/apoios (scratchpad/a3/zoom.sh, vistas de perfil e de frente).

| id | status | qa | observação |
|---|---|---|---|
| burpee | ok | limpo | quadros de voo com apoio só nas mãos (ida e volta da prancha), aterrissagem em semiagachamento, ciclo ~2,4 s |
| swing | ok | aviso: braço x tronco 4 cm na volta entre as pernas | mãos juntas na alça (bfa -8 na subida), protração na fase baixa; o contato braço-costelas na volta é o da técnica |
| thruster | ok | limpo | dois halteres (equip "kettlebell, halter"): rack nos ombros com cotovelos à frente; cam 75 |
| power-clean | ok | aviso: pronação 122° em 3 quadros da 1ª puxada; barra roçando a coxa 1,2 cm | rack bf [45,188] (modo clean mistura total: barra nos deltoides); quadro intermediário na volta; cam 35 |
| arremesso-medicine | ok | aviso: braço x tronco 3,6 cm em 1 quadro (pegar a bola entre os joelhos) | bola com voo e quique, palmas nos lados da bola |
| farmer-walk | ok | limpo | braços quase parados |
| sled-push | ok | limpo | pés empurram o chão (apoio alternado só nos pés), mãos fechadas nos postes do trenó (mão não pode ser declarada apoio) |
| bear-crawl | ok | limpo | joelhos 5–10 cm fora do chão, apoio nos dedos dos pés, mão e pé opostos |
| inchworm | pendente motor | erro: pops do antebraço nos passos de mão | t 35, c 30, joelhos levemente flexionados, tempos 1,6 s; ver motor-pendencias |
| sombra | ok | limpo | apoio declarado nos pés; punho fechado automático |
| saco-combinacoes | ok | aviso: mão 1,2 cm no saco no cruzado (compressão do saco no impacto) | saco x 9,7 (jab e cruzado tocam, sem atravessar); gancho ao corpo com inclinação |
| sprawl | ok | limpo | pernas estendidas atrás com dedos no chão, quadril no chão; volta com salto curto (voo) e base escalonada |
| polichinelo, corda, battle-rope | ok | limpo | sem mudanças de dados (motor resolveu) |
| carioca | ok | limpo | deslocamento lateral real: 4 passos para um lado e 4 de volta, perna de trás cruza pela frente e por trás |
| circulos-braco | ok | limpo | círculos pequenos na linha dos ombros (cone de 25° em torno do eixo lateral) |
| circulos-ombro | ok | limpo | protração/elevação/retração: círculo completo; cam 20 |
| circulos-punho | ok | limpo | antebraço parado, punho em flexão → desvio radial → extensão → desvio ulnar |
| maior-alongamento | em revisão | erro: base nas transições para o posterior | afundo mais fundo para a mão alcançar o chão, joelho de trás a 15 cm |
| gato-camelo | ok | limpo | apoio em joelhos e mãos; amplitude no limite do qa |
| flexor-quadril | ok | aviso: extensão do quadril 39° (é o alongamento) | pelve em retroversão |
| alongamento-quadriceps | pendente motor | erro: 1 pop de 4,3 cm no punho (IK do "segura") | mão segura o pé ("segura"), peso transferido para a perna de apoio antes de tirar o pé |
| rolo-quadriceps | ok | aviso: joelho 4 cm acima do tapete (pernas estendidas) | antebraços no chão, rolo do quadril ao joelho, coxas apoiadas no rolo |
| rolo-panturrilha | ok | limpo | quadril elevado, mãos fixas, rolo do tornozelo ao meio da panturrilha |
| rolo-it | ok | aviso: coxa/joelho a 14–15 cm (estão sobre o rolo) | deitado de lado no antebraço, perna de cima cruzada com o pé no chão, mão de cima no quadril |
