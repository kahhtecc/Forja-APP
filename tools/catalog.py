# Catálogo de exercícios do Forja.
# Cada linha: slug, nome PT, id da imagem no free-exercise-db (ou None), equipamentos,
# grupo muscular principal, tipo, nível (1-3), dicas de execução, busca de vídeo (PT).
# Gera app/src/main/assets/exercises.json (rodar: python3 tools/build_assets.py).

E = []


def ex(slug, nome, fdb, equip, grupo, tipo, nivel, dicas, busca=None):
    E.append(dict(id=slug, nome=nome, fdb=fdb, equip=equip, grupo=grupo, tipo=tipo,
                  nivel=nivel, dicas=dicas, busca=busca or f"{nome} como executar corretamente"))


# ---------- PERNAS / GLÚTEOS ----------
ex("agachamento-livre", "Agachamento livre (peso do corpo)", "Bodyweight_Squat", ["corpo"], "Pernas", "forca", 1,
   ["Pés na largura dos ombros, pontas levemente para fora.", "Desça levando o quadril para trás, joelhos acompanhando a linha dos pés.", "Mantenha o peito aberto e o calcanhar no chão; suba empurrando o chão."])
ex("agachamento-elastico", "Agachamento com elástico", "Squats_-_With_Bands", ["elastico"], "Pernas", "forca", 1,
   ["Pise no elástico com os pés na largura dos ombros e segure as pontas nos ombros.", "Desça até a coxa ficar paralela ao chão, coluna neutra.", "Suba firme, sem deixar os joelhos caírem para dentro."])
ex("agachamento-salto", "Agachamento com salto", "Freehand_Jump_Squat", ["corpo"], "Pernas", "pliometria", 2,
   ["Agache até a metade e salte explosivamente.", "Aterrisse macio, na ponta dos pés rolando para o calcanhar.", "Já absorva o impacto entrando na próxima repetição."])
ex("agachamento-goblet", "Agachamento goblet", "Goblet_Squat", ["kettlebell", "halter"], "Pernas", "forca", 1,
   ["Segure o peso junto ao peito, cotovelos apontando para baixo.", "Desça entre as pernas mantendo o tronco ereto.", "Cotovelos tocam a parte interna dos joelhos no fundo; suba pelo meio do pé."])
ex("agachamento-barra", "Agachamento com barra", "Barbell_Full_Squat", ["barra"], "Pernas", "forca", 2,
   ["Barra apoiada no trapézio, mãos firmes, abdômen contraído (respire e trave).", "Desça controlando até pelo menos a paralela, joelhos na direção dos pés.", "Suba mantendo o peito alto e a barra sobre o meio do pé."])
ex("agachamento-frontal", "Agachamento frontal", "Front_Barbell_Squat", ["barra"], "Pernas", "forca", 3,
   ["Barra apoiada na frente dos ombros, cotovelos altos.", "Tronco bem vertical durante toda a descida.", "Suba empurrando com os cotovelos para cima."])
ex("leg-press", "Leg press 45°", "Leg_Press", ["maquina"], "Pernas", "forca", 1,
   ["Pés no meio da plataforma, na largura do quadril.", "Desça até ~90° de joelho sem tirar a lombar do encosto.", "Empurre sem travar totalmente os joelhos no topo."])
ex("hack", "Agachamento hack (máquina)", "Hack_Squat", ["maquina"], "Pernas", "forca", 2,
   ["Costas e ombros firmes no encosto.", "Desça controlado até a coxa passar da paralela, se a mobilidade permitir.", "Suba pelo meio do pé, joelhos alinhados."])
ex("cadeira-extensora", "Cadeira extensora", "Leg_Extensions", ["maquina"], "Pernas", "forca", 1,
   ["Ajuste o eixo da máquina na linha do joelho.", "Estenda as pernas e segure 1 segundo no topo.", "Desça devagar, sem deixar o peso bater."])
ex("mesa-flexora", "Mesa flexora", "Lying_Leg_Curls", ["maquina"], "Posterior de coxa", "forca", 1,
   ["Quadril colado no banco durante todo o movimento.", "Flexione puxando o calcanhar em direção ao glúteo.", "Volte em 2–3 segundos, controlando."])
ex("cadeira-flexora", "Cadeira flexora", "Seated_Leg_Curl", ["maquina"], "Posterior de coxa", "forca", 1,
   ["Trave a coxa com o apoio e alinhe o joelho ao eixo.", "Puxe os calcanhares para baixo e para trás.", "Retorne devagar sem estender bruscamente."])
ex("afundo", "Afundo (passada parada)", "Split_Squats", ["corpo"], "Pernas", "forca", 1,
   ["Um pé à frente e outro atrás, tronco ereto.", "Desça o joelho de trás em direção ao chão.", "Suba empurrando com o calcanhar da perna da frente."])
ex("afundo-halteres", "Afundo com halteres", "Dumbbell_Lunges", ["halter"], "Pernas", "forca", 2,
   ["Halteres ao lado do corpo, ombros para trás.", "Dê um passo à frente e desça até os dois joelhos formarem ~90°.", "Volte à posição inicial e alterne as pernas."])
ex("passada-andando", "Passada andando", "Bodyweight_Walking_Lunge", ["corpo"], "Pernas", "forca", 1,
   ["Passos longos e controlados, tronco ereto.", "Joelho de trás quase toca o chão.", "Empurre com a perna da frente e emende o próximo passo."])
ex("bulgaro", "Agachamento búlgaro", "Split_Squat_with_Dumbbells", ["halter", "banco"], "Pernas", "forca", 2,
   ["Pé de trás apoiado num banco, pé da frente bem à frente.", "Desça na vertical, joelho da frente acompanhando o pé.", "Suba pelo calcanhar da frente; termine um lado e troque."])
ex("step-up", "Subida no banco (step-up)", "Dumbbell_Step_Ups", ["banco", "halter"], "Pernas", "forca", 1,
   ["Pé inteiro apoiado no banco ou degrau firme.", "Suba empurrando só com a perna de cima.", "Desça controlando, sem 'quicar' com a perna de baixo."])
ex("terra", "Levantamento terra", "Barbell_Deadlift", ["barra"], "Posterior de coxa", "forca", 3,
   ["Barra sobre o meio do pé, canelas próximas.", "Costas neutras, peito aberto, puxe a 'folga' da barra antes de subir.", "Empurre o chão e estenda quadril e joelhos juntos; desça a barra rente às pernas."])
ex("stiff", "Stiff / terra romeno", "Romanian_Deadlift", ["barra", "halter"], "Posterior de coxa", "forca", 2,
   ["Joelhos levemente flexionados e fixos.", "Leve o quadril para trás com a barra deslizando rente às coxas.", "Desça até sentir alongar o posterior, coluna neutra; suba contraindo os glúteos."])
ex("stiff-halteres", "Stiff com halteres", "Stiff-Legged_Dumbbell_Deadlift", ["halter"], "Posterior de coxa", "forca", 1,
   ["Halteres na frente das coxas, joelhos destravados.", "Dobre no quadril mantendo as costas retas.", "Volte apertando os glúteos no topo."])
ex("terra-uma-perna", "Terra unilateral com kettlebell", "Kettlebell_One-Legged_Deadlift", ["kettlebell", "halter"], "Posterior de coxa", "forca", 2,
   ["Apoio numa perna, joelho levemente flexionado.", "Incline o tronco e estenda a perna livre para trás em linha.", "Volte mantendo o quadril nivelado (sem abrir)."])
ex("ponte-gluteo", "Ponte de glúteo", "Butt_Lift_Bridge", ["corpo"], "Glúteos", "forca", 1,
   ["Deitado, pés apoiados perto do quadril.", "Eleve o quadril até alinhar joelhos, quadril e ombros.", "Aperte os glúteos 1 s no topo e desça controlando."])
ex("ponte-unilateral", "Ponte de glúteo unilateral", "Single_Leg_Glute_Bridge", ["corpo"], "Glúteos", "forca", 2,
   ["Uma perna estendida, outra com o pé no chão.", "Suba o quadril sem deixá-lo girar.", "Desça devagar; complete as repetições e troque."])
ex("elevacao-quadril", "Elevação de quadril com barra (hip thrust)", "Barbell_Hip_Thrust", ["barra", "banco"], "Glúteos", "forca", 2,
   ["Escápulas apoiadas no banco, barra sobre o quadril (use proteção).", "Suba até o tronco ficar paralelo ao chão, queixo levemente baixo.", "Segure 1 s contraindo os glúteos; desça controlado."])
ex("coice-gluteo", "Coice de glúteo (4 apoios)", "Glute_Kickback", ["corpo"], "Glúteos", "forca", 1,
   ["Quatro apoios, mãos sob os ombros e joelhos sob o quadril.", "Empurre um calcanhar em direção ao teto.", "Não arqueie a lombar; volte devagar."])
ex("abdutora", "Cadeira abdutora", "Thigh_Abductor", ["maquina"], "Glúteos", "forca", 1,
   ["Sente com a coluna apoiada.", "Abra as pernas contra a resistência.", "Volte devagar sem deixar as placas baterem."])
ex("monster-walk", "Caminhada lateral com mini-band", "Monster_Walk", ["elastico"], "Glúteos", "forca", 1,
   ["Elástico acima dos joelhos ou nos tornozelos, semi-agachado.", "Passos laterais curtos mantendo a tensão no elástico.", "Joelhos para fora, sem arrastar os pés."])
ex("panturrilha-pe", "Elevação de panturrilha em pé", "Standing_Calf_Raises", ["maquina", "corpo"], "Panturrilhas", "forca", 1,
   ["Ponta dos pés na borda do degrau ou plataforma.", "Suba o máximo possível e segure 1 s.", "Desça até alongar bem o calcanhar abaixo da linha do degrau."])
ex("panturrilha-sentado", "Panturrilha sentado", "Seated_Calf_Raise", ["maquina"], "Panturrilhas", "forca", 1,
   ["Apoio sobre os joelhos, ponta dos pés na plataforma.", "Suba e contraia no topo.", "Desça devagar até o alongamento completo."])
ex("panturrilha-elastico", "Panturrilha com elástico", "Calf_Raises_-_With_Bands", ["elastico"], "Panturrilhas", "forca", 1,
   ["Pise no elástico e segure as pontas na altura dos ombros.", "Suba na ponta dos pés.", "Desça controlando."])

# ---------- PEITO ----------
ex("flexao", "Flexão de braço", "Pushups", ["corpo"], "Peito", "forca", 1,
   ["Mãos um pouco além da largura dos ombros, corpo em prancha.", "Desça até o peito quase tocar o chão, cotovelos a ~45°.", "Empurre o chão mantendo abdômen e glúteos firmes."])
ex("flexao-inclinada", "Flexão inclinada (mãos elevadas)", "Incline_Push-Up", ["corpo", "banco"], "Peito", "forca", 1,
   ["Mãos num banco, mesa ou parede firme.", "Corpo reto da cabeça aos calcanhares.", "Desça o peito até a borda e empurre. Quanto mais alto o apoio, mais fácil."])
ex("flexao-joelhos", "Flexão com joelhos apoiados", "Pushups_Close_and_Wide_Hand_Positions", ["corpo"], "Peito", "forca", 1,
   ["Joelhos no chão, quadril alinhado com o tronco.", "Desça o peito entre as mãos.", "Empurre sem deixar o quadril subir."], "flexão com joelhos apoiados como fazer")
ex("flexao-declinada", "Flexão com pés elevados", "Push-Ups_With_Feet_Elevated", ["corpo", "banco"], "Peito", "forca", 2,
   ["Pés num banco ou cadeira, mãos no chão.", "Corpo reto, desça controlando.", "Ênfase na parte superior do peito e ombros."])
ex("flexao-diamante", "Flexão fechada (tríceps)", "Push-Ups_-_Close_Triceps_Position", ["corpo"], "Tríceps", "forca", 2,
   ["Mãos próximas sob o peito.", "Cotovelos rentes ao corpo durante a descida.", "Empurre estendendo totalmente os braços."])
ex("flexao-pliometrica", "Flexão explosiva", "Plyo_Push-up", ["corpo"], "Peito", "pliometria", 3,
   ["Desça como numa flexão normal.", "Empurre com força para as mãos saírem do chão.", "Aterrisse com cotovelos destravados e emende."])
ex("supino-reto", "Supino reto com barra", "Barbell_Bench_Press_-_Medium_Grip", ["barra", "banco"], "Peito", "forca", 2,
   ["Escápulas retraídas, pés firmes no chão, leve arco natural.", "Desça a barra até a linha dos mamilos, cotovelos a ~45–70°.", "Empurre a barra para cima e levemente para trás."])
ex("supino-halteres", "Supino com halteres", "Dumbbell_Bench_Press", ["halter", "banco"], "Peito", "forca", 1,
   ["Halteres na linha do peito, escápulas encaixadas.", "Desça até sentir o alongamento do peitoral.", "Empurre juntando levemente os halteres no topo."])
ex("supino-inclinado", "Supino inclinado com halteres", "Incline_Dumbbell_Press", ["halter", "banco"], "Peito", "forca", 1,
   ["Banco a 30–45°.", "Desça os halteres na linha da parte alta do peito.", "Empurre sem bater os halteres."])
ex("supino-inclinado-barra", "Supino inclinado com barra", "Barbell_Incline_Bench_Press_-_Medium_Grip", ["barra", "banco"], "Peito", "forca", 2,
   ["Banco a ~30°, escápulas retraídas.", "Barra desce até a parte alta do peito.", "Empurre na vertical, controlando a descida."])
ex("supino-maquina", "Supino na máquina", "Machine_Bench_Press", ["maquina"], "Peito", "forca", 1,
   ["Ajuste o banco para as pegadas ficarem na linha do peito.", "Empurre sem tirar as costas do encosto.", "Volte devagar até alongar o peitoral."])
ex("crucifixo", "Crucifixo com halteres", "Dumbbell_Flyes", ["halter", "banco"], "Peito", "forca", 1,
   ["Cotovelos levemente flexionados e fixos.", "Abra os braços em arco até sentir o alongamento.", "Feche como se abraçasse uma árvore."])
ex("crossover", "Crossover na polia", "Cable_Crossover", ["polia"], "Peito", "forca", 1,
   ["Um passo à frente, tronco levemente inclinado.", "Traga as mãos à frente do corpo em arco.", "Volte controlando até alongar o peito."])
ex("peck-deck", "Voador (peck deck)", "Butterfly", ["maquina"], "Peito", "forca", 1,
   ["Pegadas na altura do peito, costas apoiadas.", "Feche os braços contraindo o peitoral.", "Volte devagar sem passar do alongamento confortável."])
ex("supino-elastico", "Supino com elástico", "Bench_Press_-_With_Bands", ["elastico"], "Peito", "forca", 1,
   ["Elástico passado atrás das costas (ou preso atrás de você).", "Empurre as mãos à frente na altura do peito.", "Volte controlando a tensão."])
ex("crucifixo-elastico", "Crucifixo com elástico", "Cross_Over_-_With_Bands", ["elastico"], "Peito", "forca", 1,
   ["Elástico preso atrás de você na altura do peito.", "Braços abertos, cotovelos levemente flexionados.", "Feche à frente e volte devagar."])
ex("paralelas", "Mergulho nas paralelas", "Dips_-_Chest_Version", ["barra_fixa"], "Peito", "forca", 3,
   ["Corpo inclinado levemente à frente para peito (vertical para tríceps).", "Desça até os ombros ficarem na linha dos cotovelos.", "Empurre até estender os braços."])

# ---------- COSTAS ----------
ex("barra-fixa", "Barra fixa (pegada pronada)", "Pullups", ["barra_fixa"], "Costas", "forca", 3,
   ["Pegada um pouco além dos ombros, braços estendidos.", "Puxe levando o peito em direção à barra, escápulas para baixo.", "Desça controlando até estender os braços."])
ex("barra-supinada", "Barra fixa supinada (chin-up)", "Chin-Up", ["barra_fixa"], "Costas", "forca", 2,
   ["Palmas viradas para você, largura dos ombros.", "Puxe até o queixo passar a barra.", "Desça devagar."])
ex("barra-assistida", "Barra fixa com elástico (assistida)", "Band_Assisted_Pull-Up", ["barra_fixa", "elastico"], "Costas", "forca", 1,
   ["Prenda o elástico na barra e apoie um pé ou joelho nele.", "Puxe o peito em direção à barra.", "Use elásticos mais finos conforme evolui."])
ex("puxada-frente", "Puxada frontal (pulldown)", "Wide-Grip_Lat_Pulldown", ["polia", "maquina"], "Costas", "forca", 1,
   ["Pegada aberta, coxas travadas no apoio.", "Puxe a barra até a parte alta do peito levando os cotovelos para baixo.", "Volte devagar, alongando as costas."])
ex("puxada-triangulo", "Puxada com triângulo", "V-Bar_Pulldown", ["polia"], "Costas", "forca", 1,
   ["Pegada neutra no triângulo.", "Puxe até o peito, inclinando levemente o tronco.", "Estenda os braços controlando."])
ex("remada-baixa", "Remada baixa sentada", "Seated_Cable_Rows", ["polia"], "Costas", "forca", 1,
   ["Coluna neutra, joelhos levemente flexionados.", "Puxe o pegador em direção ao umbigo, juntando as escápulas.", "Volte estendendo os braços sem curvar as costas."])
ex("remada-curvada", "Remada curvada com barra", "Bent_Over_Barbell_Row", ["barra"], "Costas", "forca", 2,
   ["Tronco inclinado ~45°, coluna neutra.", "Puxe a barra até a parte baixa do abdômen.", "Desça controlando sem perder a postura."])
ex("remada-unilateral", "Remada unilateral com halter", "One-Arm_Dumbbell_Row", ["halter", "banco"], "Costas", "forca", 1,
   ["Joelho e mão apoiados no banco, costas paralelas ao chão.", "Puxe o halter em direção ao quadril.", "Desça alongando sem girar o tronco."])
ex("remada-elastico", "Remada com elástico", "Seated_One-arm_Cable_Pulley_Rows", ["elastico"], "Costas", "forca", 1,
   ["Elástico preso à frente (porta ou pés).", "Puxe os cotovelos para trás, juntando as escápulas.", "Volte devagar mantendo a postura."], "remada com elástico em casa como fazer")
ex("remada-invertida", "Remada invertida", "Inverted_Row", ["barra_fixa", "corpo"], "Costas", "forca", 2,
   ["Sob uma barra baixa ou mesa firme, corpo reto.", "Puxe o peito até a barra.", "Desça controlando. Pés mais perto = mais fácil."])
ex("pulldown-elastico", "Puxada com elástico", "Rope_Straight-Arm_Pulldown", ["elastico"], "Costas", "forca", 1,
   ["Elástico preso no alto (porta).", "Puxe os cotovelos para baixo em direção às costelas.", "Volte controlando."], "puxada com elástico em casa")
ex("pullover-polia", "Pullover na polia (braços estendidos)", "Straight-Arm_Pulldown", ["polia"], "Costas", "forca", 1,
   ["Braços quase estendidos, leve inclinação do tronco.", "Leve a barra até as coxas em arco.", "Volte devagar até a altura dos olhos."])
ex("superman", "Superman", "Superman", ["corpo"], "Lombar", "forca", 1,
   ["Deitado de barriga para baixo, braços estendidos à frente.", "Eleve braços e pernas juntos, olhando para o chão.", "Segure 2 s e desça."])
ex("hiperextensao", "Extensão lombar no banco", "Hyperextensions_Back_Extensions", ["maquina"], "Lombar", "forca", 1,
   ["Quadril apoiado na borda do banco romano.", "Desça o tronco com a coluna neutra.", "Suba até alinhar com as pernas, sem hiperestender."])
ex("face-pull", "Face pull", "Face_Pull", ["polia", "elastico"], "Ombros", "forca", 1,
   ["Corda na altura dos olhos.", "Puxe em direção ao rosto abrindo os cotovelos.", "Termine com rotação externa (punhos para trás)."])
ex("band-pull-apart", "Abertura com elástico (pull apart)", "Band_Pull_Apart", ["elastico"], "Ombros", "forca", 1,
   ["Braços estendidos à frente segurando o elástico.", "Abra os braços até o elástico tocar o peito.", "Volte devagar, escápulas ativas."])
ex("encolhimento", "Encolhimento com halteres", "Dumbbell_Shrug", ["halter"], "Trapézio", "forca", 1,
   ["Halteres ao lado do corpo, braços estendidos.", "Eleve os ombros em direção às orelhas.", "Segure 1 s e desça devagar."])

# ---------- OMBROS ----------
ex("desenvolvimento-halteres", "Desenvolvimento com halteres", "Dumbbell_Shoulder_Press", ["halter"], "Ombros", "forca", 1,
   ["Halteres na altura das orelhas, cotovelos levemente à frente.", "Empurre para cima sem arquear a lombar.", "Desça até os cotovelos ~90°."])
ex("desenvolvimento-barra", "Desenvolvimento militar com barra", "Standing_Military_Press", ["barra"], "Ombros", "forca", 2,
   ["Em pé, barra na frente dos ombros, glúteos e abdômen contraídos.", "Empurre a barra passando rente ao rosto.", "Termine com a barra acima da cabeça, braços estendidos."])
ex("desenvolvimento-maquina", "Desenvolvimento na máquina", "Machine_Shoulder_Military_Press", ["maquina"], "Ombros", "forca", 1,
   ["Pegadas na altura dos ombros.", "Empurre sem tirar as costas do encosto.", "Desça controlando."])
ex("desenvolvimento-elastico", "Desenvolvimento com elástico", "Shoulder_Press_-_With_Bands", ["elastico"], "Ombros", "forca", 1,
   ["Pise no elástico e segure as pontas nos ombros.", "Empurre acima da cabeça.", "Desça devagar."])
ex("elevacao-lateral", "Elevação lateral", "Side_Lateral_Raise", ["halter"], "Ombros", "forca", 1,
   ["Cotovelos levemente flexionados.", "Eleve os braços até a altura dos ombros, conduzindo pelos cotovelos.", "Desça em 2–3 segundos."])
ex("elevacao-lateral-elastico", "Elevação lateral com elástico", "Lateral_Raise_-_With_Bands", ["elastico"], "Ombros", "forca", 1,
   ["Pise no elástico e segure as pontas.", "Eleve os braços lateralmente até os ombros.", "Volte controlando."])
ex("elevacao-frontal", "Elevação frontal", "Front_Dumbbell_Raise", ["halter"], "Ombros", "forca", 1,
   ["Halteres à frente das coxas.", "Eleve até a altura dos ombros.", "Desça devagar sem balançar."])
ex("crucifixo-inverso", "Crucifixo inverso", "Reverse_Flyes", ["halter"], "Ombros", "forca", 1,
   ["Tronco inclinado à frente, coluna neutra.", "Abra os braços para os lados, apertando a parte de trás dos ombros.", "Desça controlando."])
ex("arnold", "Desenvolvimento Arnold", "Arnold_Dumbbell_Press", ["halter"], "Ombros", "forca", 2,
   ["Comece com as palmas viradas para você na altura do queixo.", "Gire as palmas para frente enquanto empurra para cima.", "Inverta o movimento na descida."])
ex("pike-pushup", "Flexão pike (ombros)", "Handstand_Push-Ups", ["corpo"], "Ombros", "forca", 2,
   ["Quadril alto, corpo em 'V' invertido.", "Desça a cabeça em direção ao chão entre as mãos.", "Empurre de volta. Avançado: pés na parede."], "flexão pike para ombros como fazer")
ex("rotacao-externa", "Rotação externa com elástico", "External_Rotation_with_Band", ["elastico"], "Ombros", "forca", 1,
   ["Cotovelo colado ao corpo a 90°.", "Gire o antebraço para fora contra o elástico.", "Volte devagar. Ótimo para saúde do ombro."])

# ---------- BRAÇOS ----------
ex("rosca-direta", "Rosca direta com barra", "Barbell_Curl", ["barra"], "Bíceps", "forca", 1,
   ["Cotovelos colados ao corpo.", "Suba a barra sem balançar o tronco.", "Desça devagar até estender os braços."])
ex("rosca-halteres", "Rosca alternada com halteres", "Dumbbell_Alternate_Bicep_Curl", ["halter"], "Bíceps", "forca", 1,
   ["Palmas viradas para frente, cotovelos fixos.", "Suba um halter por vez.", "Controle a descida."])
ex("rosca-martelo", "Rosca martelo", "Hammer_Curls", ["halter"], "Bíceps", "forca", 1,
   ["Pegada neutra (palmas uma para a outra).", "Suba sem mexer os cotovelos.", "Desça devagar."])
ex("rosca-elastico", "Rosca com elástico", "Standing_Biceps_Cable_Curl", ["elastico"], "Bíceps", "forca", 1,
   ["Pise no elástico, palmas para frente.", "Flexione os cotovelos sem afastá-los do corpo.", "Volte controlando."], "rosca bíceps com elástico")
ex("rosca-scott", "Rosca Scott", "Preacher_Curl", ["barra", "maquina"], "Bíceps", "forca", 1,
   ["Braços apoiados no banco Scott.", "Suba até contrair o bíceps.", "Desça quase estendendo, sem travar o cotovelo."])
ex("triceps-polia", "Tríceps na polia (corda)", "Triceps_Pushdown_-_Rope_Attachment", ["polia"], "Tríceps", "forca", 1,
   ["Cotovelos colados ao corpo.", "Empurre a corda para baixo e abra as mãos no final.", "Volte até ~90° sem mexer os ombros."])
ex("triceps-frances", "Tríceps francês com halter", "Standing_Dumbbell_Triceps_Extension", ["halter"], "Tríceps", "forca", 1,
   ["Halter acima da cabeça seguro com as duas mãos.", "Desça atrás da cabeça mantendo cotovelos apontados para cima.", "Estenda os braços."])
ex("triceps-testa", "Tríceps testa", "Lying_Dumbbell_Tricep_Extension", ["halter", "barra", "banco"], "Tríceps", "forca", 2,
   ["Deitado, braços estendidos acima do peito.", "Flexione só os cotovelos levando o peso em direção à testa.", "Estenda de volta."])
ex("triceps-banco", "Mergulho no banco", "Bench_Dips", ["corpo", "banco"], "Tríceps", "forca", 1,
   ["Mãos na borda de um banco ou cadeira firme.", "Desça até os cotovelos ~90°, costas próximas ao banco.", "Empurre de volta."])
ex("triceps-elastico", "Tríceps com elástico acima da cabeça", "Speed_Band_Overhead_Triceps", ["elastico"], "Tríceps", "forca", 1,
   ["Elástico preso atrás/abaixo, mãos atrás da cabeça.", "Estenda os braços para cima.", "Volte devagar."])
ex("triceps-coice", "Tríceps coice", "Tricep_Dumbbell_Kickback", ["halter"], "Tríceps", "forca", 1,
   ["Tronco inclinado, cotovelo alto e fixo junto ao corpo.", "Estenda o braço para trás.", "Volte controlando."])

# ---------- CORE ----------
ex("prancha", "Prancha", "Plank", ["corpo"], "Core", "forca", 1,
   ["Antebraços no chão, cotovelos sob os ombros.", "Corpo reto, glúteos e abdômen contraídos.", "Respire normalmente; não deixe o quadril cair."])
ex("prancha-lateral", "Prancha lateral", "Side_Bridge", ["corpo"], "Core", "forca", 1,
   ["Apoio no antebraço e na lateral do pé.", "Quadril alto, corpo em linha reta.", "Segure o tempo e troque o lado."])
ex("abdominal", "Abdominal supra (crunch)", "Crunches", ["corpo"], "Core", "forca", 1,
   ["Joelhos flexionados, mãos ao lado da cabeça sem puxar o pescoço.", "Enrole o tronco tirando as escápulas do chão.", "Desça devagar."])
ex("abdominal-infra", "Abdominal infra (elevação de pernas)", "Flat_Bench_Lying_Leg_Raise", ["corpo"], "Core", "forca", 1,
   ["Deitado, lombar colada ao chão.", "Eleve as pernas até 90°.", "Desça devagar sem arquear a lombar."])
ex("dead-bug", "Dead bug", "Dead_Bug", ["corpo"], "Core", "forca", 1,
   ["Deitado, braços para o teto e joelhos a 90°.", "Estenda braço e perna opostos sem tirar a lombar do chão.", "Volte e alterne."])
ex("mountain-climber", "Escalador (mountain climber)", "Mountain_Climbers", ["corpo"], "Core", "cardio", 1,
   ["Posição de prancha alta.", "Leve os joelhos ao peito alternadamente, rápido.", "Quadril baixo e estável."])
ex("russian-twist", "Giro russo", "Russian_Twist", ["corpo"], "Core", "forca", 1,
   ["Sentado, tronco inclinado para trás, pés no chão ou elevados.", "Gire o tronco de um lado ao outro.", "Movimento vem do tronco, não só dos braços."])
ex("abdominal-bicicleta", "Abdominal bicicleta", "Air_Bike", ["corpo"], "Core", "forca", 1,
   ["Mãos atrás da cabeça, pernas elevadas.", "Cotovelo em direção ao joelho oposto, alternando.", "Ritmo controlado."])
ex("elevacao-pernas-barra", "Elevação de pernas na barra", "Hanging_Leg_Raise", ["barra_fixa"], "Core", "forca", 3,
   ["Pendurado na barra, sem balanço.", "Eleve as pernas até a altura do quadril ou mais.", "Desça devagar."])
ex("roda-abdominal", "Roda abdominal", "Ab_Roller", ["outro"], "Core", "forca", 3,
   ["Ajoelhado, mãos na roda.", "Role à frente mantendo o abdômen firme e a lombar neutra.", "Volte contraindo o core."])
ex("pallof", "Pallof press (antirrotação)", "Pallof_Press", ["polia", "elastico"], "Core", "forca", 1,
   ["Lateral à polia/elástico, mãos no peito.", "Estenda os braços à frente sem deixar o tronco girar.", "Segure 2 s e volte."])
ex("abdominal-polia", "Abdominal na polia", "Cable_Crunch", ["polia"], "Core", "forca", 2,
   ["Ajoelhado, corda junto à cabeça.", "Flexione o tronco levando os cotovelos aos joelhos.", "Volte devagar."])
ex("canivete", "Canivete (V-up)", "Jackknife_Sit-Up", ["corpo"], "Core", "forca", 2,
   ["Deitado, braços estendidos atrás da cabeça.", "Eleve pernas e tronco juntos, tocando as mãos nos pés.", "Desça controlando."])

# ---------- CORPO INTEIRO / POTÊNCIA / CONDICIONAMENTO ----------
ex("burpee", "Burpee", None, ["corpo"], "Corpo inteiro", "cardio", 2,
   ["Agache e apoie as mãos no chão.", "Jogue os pés para trás em prancha (opcional: flexão).", "Volte os pés e salte com os braços para cima."])
ex("polichinelo", "Polichinelo", "Star_Jump", ["corpo"], "Corpo inteiro", "cardio", 1,
   ["Salte abrindo pernas e braços.", "Volte fechando.", "Mantenha ritmo constante e aterrisse macio."], "polichinelo como fazer")
ex("corda", "Pular corda", "Rope_Jumping", ["corda"], "Corpo inteiro", "cardio", 1,
   ["Saltos baixos na ponta dos pés.", "Gire a corda com os punhos, cotovelos perto do corpo.", "Respire no ritmo."])
ex("swing", "Kettlebell swing", "One-Arm_Kettlebell_Swings", ["kettlebell"], "Corpo inteiro", "potencia", 2,
   ["Movimento de quadril (dobradiça), não de agachamento.", "Projete o quadril à frente com força; o sino sobe até a altura do peito.", "Deixe o sino descer entre as pernas e repita."], "kettlebell swing técnica correta")
ex("thruster", "Thruster com kettlebell", "Kettlebell_Thruster", ["kettlebell", "halter"], "Corpo inteiro", "potencia", 2,
   ["Peso na altura dos ombros.", "Agache e, na subida, use o impulso para empurrar acima da cabeça.", "Desça o peso aos ombros já entrando no próximo agachamento."])
ex("power-clean", "Power clean", "Power_Clean", ["barra"], "Corpo inteiro", "potencia", 3,
   ["Posição de terra, costas neutras.", "Puxe explosivamente estendendo quadril, joelhos e tornozelos.", "Receba a barra nos ombros em meio agachamento."])
ex("box-jump", "Salto na caixa", "Front_Box_Jump", ["outro"], "Pernas", "pliometria", 2,
   ["De frente para uma caixa firme.", "Balance os braços e salte com os dois pés.", "Aterrisse macio, em pé completo; desça caminhando."])
ex("salto-distancia", "Salto horizontal", "Standing_Long_Jump", ["corpo"], "Pernas", "pliometria", 2,
   ["Pés na largura do quadril.", "Balance os braços e salte o mais longe possível.", "Aterrisse com joelhos flexionados e estabilize."])
ex("bound-lateral", "Salto lateral (skater)", "Lateral_Bound", ["corpo"], "Pernas", "pliometria", 2,
   ["Impulsione com uma perna para o lado.", "Aterrisse na outra perna e estabilize.", "Alterne mantendo o controle do joelho."])
ex("salto-tesoura", "Salto afundo alternado", "Split_Jump", ["corpo"], "Pernas", "pliometria", 2,
   ["Posição de afundo.", "Salte e troque as pernas no ar.", "Aterrisse macio e emende."])
ex("tuck-jump", "Salto grupado", "Knee_Tuck_Jump", ["corpo"], "Pernas", "pliometria", 3,
   ["Salte levando os joelhos ao peito.", "Aterrisse macio.", "Emende os saltos mantendo a postura."])
ex("arremesso-medicine", "Arremesso de medicine ball no chão", "Overhead_Slam", ["bola"], "Corpo inteiro", "potencia", 1,
   ["Bola acima da cabeça, braços estendidos.", "Arremesse com força contra o chão usando o corpo todo.", "Pegue a bola e repita."])
ex("passe-medicine", "Passe de peito com medicine ball", "Medicine_Ball_Chest_Pass", ["bola"], "Peito", "potencia", 1,
   ["Bola na frente do peito.", "Empurre explosivamente contra a parede.", "Receba e repita."])
ex("arremesso-rotacional", "Arremesso rotacional de medicine ball", "Medicine_Ball_Full_Twist", ["bola"], "Core", "potencia", 2,
   ["Lateral à parede.", "Gire o quadril e o tronco arremessando a bola.", "Receba e repita; troque o lado."])
ex("battle-rope", "Corda naval", "Battling_Ropes", ["outro"], "Corpo inteiro", "cardio", 1,
   ["Semi-agachado, uma ponta em cada mão.", "Faça ondas alternadas rápidas.", "Mantenha o core firme."])
ex("farmer-walk", "Caminhada do fazendeiro", "Farmers_Walk", ["halter", "kettlebell"], "Corpo inteiro", "forca", 1,
   ["Pesos pesados ao lado do corpo.", "Caminhe com passos curtos, peito aberto e ombros para trás.", "Não deixe o tronco inclinar."])
ex("sled-push", "Empurrar trenó", "Sled_Push", ["outro"], "Corpo inteiro", "potencia", 2,
   ["Mãos no trenó, corpo inclinado.", "Empurre com passos curtos e fortes.", "Mantenha a coluna neutra."])
ex("turkish-getup", "Levantamento turco (Turkish get-up)", "Kettlebell_Turkish_Get-Up_Squat_style", ["kettlebell"], "Corpo inteiro", "forca", 3,
   ["Deitado, peso acima do ombro com braço estendido.", "Levante-se em etapas mantendo o olhar no peso.", "Inverta as etapas para voltar."])
ex("inchworm", "Inchworm (minhoca)", "Inchworm", ["corpo"], "Corpo inteiro", "mobilidade", 1,
   ["Em pé, dobre-se e apoie as mãos no chão.", "Caminhe com as mãos até a prancha.", "Volte com as mãos até os pés e levante."])

# ---------- LUTAS ----------
ex("sombra", "Boxe de sombra (shadow boxing)", None, ["corpo"], "Corpo inteiro", "tecnica", 1,
   ["Guarda alta, queixo baixo, base firme.", "Combine jab, direto, cruzado e esquivas em movimento.", "Volte sempre à guarda após cada golpe."], "shadow boxing para iniciantes")
ex("saco-combinacoes", "Combinações no saco de pancada", "Heavy_Bag_Thrust", ["saco"], "Corpo inteiro", "tecnica", 2,
   ["Use bandagem e luvas.", "Golpeie em rounds com combinações de 2–4 golpes.", "Gire o quadril e o pé no golpe; volte à guarda."], "saco de pancada combinações treino")
ex("sprawl", "Sprawl", None, ["corpo"], "Corpo inteiro", "cardio", 2,
   ["Da guarda, jogue as pernas para trás e o quadril ao chão.", "Peito pesado, quadril baixo (defesa de queda).", "Volte rápido à base."], "sprawl defesa de queda como fazer")
ex("ponte-pescoco", "Ponte com rolamento de quadril (bridge and roll)", "Pelvic_Tilt_Into_Bridge", ["corpo"], "Core", "tecnica", 2,
   ["Deitado, pés perto do quadril.", "Ponte explosiva sobre um ombro.", "Use para a fuga de montada (upa)."], "upa fuga da montada jiu jitsu treino")
ex("fuga-quadril", "Fuga de quadril (shrimp)", None, ["corpo"], "Core", "tecnica", 1,
   ["Deitado de lado, empurre o chão com o pé.", "Leve o quadril para trás criando espaço.", "Alterne os lados deslocando-se pelo tatame."], "fuga de quadril shrimp jiu jitsu")
ex("bear-crawl", "Caminhada do urso", None, ["corpo"], "Corpo inteiro", "cardio", 1,
   ["Quatro apoios com joelhos fora do chão.", "Ande movendo mão e pé opostos.", "Quadril baixo e costas estáveis."], "bear crawl como fazer")

ex("isometria-pescoco", "Isometria de pescoço", "Isometric_Neck_Exercise_-_Front_And_Back", ["corpo"], "Pescoço", "forca", 1,
   ["Mão na testa (ou nuca), pescoço neutro.", "Empurre a cabeça contra a mão sem deixar mover, 10–20 s.", "Faça frente, trás e lados. Pressão progressiva, sem dor."], "isometria de pescoço para lutadores")
ex("nordico", "Flexão nórdica (nordic hamstring)", "Natural_Glute_Ham_Raise", ["corpo"], "Posterior de coxa", "forca", 3,
   ["Ajoelhado, tornozelos presos por um parceiro ou apoio.", "Desça o tronco à frente o mais devagar possível, quadril estendido.", "Amorteça com as mãos e volte empurrando. Prevenção de lesão de posterior."], "nordic hamstring curl como fazer")

# ---------- CARDIO / CORRIDA / BIKE (sessões) ----------
ex("corrida-leve", "Corrida leve (zona 2)", "Jogging_Treadmill", ["rua", "esteira"], "Cardio", "cardio", 1,
   ["Ritmo de conversa: você consegue falar frases inteiras.", "Passos curtos e cadência alta (~170–180/min).", "Tronco levemente inclinado à frente, braços relaxados."], "técnica de corrida para iniciantes")
ex("caminhada-corrida", "Caminhada + corrida intercalada", "Walking_Treadmill", ["rua", "esteira"], "Cardio", "cardio", 1,
   ["Alterne blocos de caminhada rápida e trote leve.", "Aumente os blocos de corrida a cada semana.", "Se ficar sem fôlego para falar, desacelere."], "caminhada e corrida intercalada iniciantes")
ex("tiros", "Tiros (intervalado)", "Wind_Sprints", ["rua", "esteira", "pista"], "Cardio", "cardio", 2,
   ["Aqueça bem antes (10–15 min).", "Corra os tiros em ritmo forte, mas sustentável até o último.", "Recupere trotando ou caminhando entre os tiros."], "treino intervalado de corrida tiros")
ex("tempo-run", "Corrida de limiar (tempo run)", "Running_Treadmill", ["rua", "esteira"], "Cardio", "cardio", 2,
   ["Ritmo 'confortavelmente difícil': frases curtas apenas.", "Mantenha o ritmo constante do início ao fim.", "Sempre com aquecimento e desaquecimento."], "tempo run corrida de limiar")
ex("longao", "Longão (corrida longa)", "Trail_Running_Walking", ["rua"], "Cardio", "cardio", 2,
   ["Ritmo bem leve, mais lento que o de prova.", "Leve água para treinos acima de 60 min.", "O objetivo é tempo em movimento, não velocidade."], "corrida longa longão dicas")
ex("educativos-corrida", "Educativos de corrida (skipping)", "Fast_Skipping", ["rua", "pista"], "Pernas", "tecnica", 1,
   ["Skipping alto, anfersen (calcanhar ao glúteo) e dribling.", "20–30 m cada, voltando caminhando.", "Postura alta e braços coordenados."], "educativos de corrida skipping anfersen")
ex("bike-leve", "Pedal contínuo leve (zona 2)", "Bicycling_Stationary", ["bike"], "Cardio", "cardio", 1,
   ["Cadência confortável de 80–95 rpm.", "Esforço em que dá para conversar.", "Ajuste o banco: joelho levemente flexionado no ponto mais baixo."], "ajuste de bike e pedal zona 2")
ex("bike-intervalado", "Bike intervalado", "Bicycling_Stationary", ["bike"], "Cardio", "cardio", 2,
   ["Aqueça 10 min.", "Blocos fortes com carga/marcha mais pesada.", "Recupere pedalando leve entre os blocos."], "treino intervalado de bike")
ex("bike-subida", "Simulação de subida (força no pedal)", "Bicycling", ["bike"], "Pernas", "cardio", 2,
   ["Marcha pesada, cadência baixa (60–70 rpm).", "Tronco estável, força vem das pernas.", "Pode alternar sentado e em pé."], "treino de subida ciclismo força")
ex("bike-cadencia", "Drills de cadência", "Recumbent_Bike", ["bike"], "Cardio", "tecnica", 2,
   ["Carga leve, aumente a rotação até 110+ rpm por 30 s.", "Quadril parado no selim (sem quicar).", "Recupere 1–2 min entre as repetições."], "treino de cadência ciclismo")
ex("eliptico", "Elíptico / transport", "Elliptical_Trainer", ["maquina"], "Cardio", "cardio", 1,
   ["Postura ereta, mãos leves nas alças.", "Ritmo constante.", "Ótima opção de baixo impacto."])
ex("remo-ergometro", "Remo ergômetro", "Rowing_Stationary", ["maquina"], "Corpo inteiro", "cardio", 2,
   ["Sequência: pernas, tronco, braços na puxada.", "Volte na ordem inversa: braços, tronco, pernas.", "60% da força vem das pernas."], "remo ergômetro técnica correta")
ex("escada", "Escada / stair climber", "Stairmaster", ["maquina"], "Cardio", "cardio", 1,
   ["Não se apoie com força no corrimão.", "Pé inteiro no degrau.", "Ritmo em que você ainda consegue falar."])
ex("prova", "Prova ou teste de distância", "Running_Treadmill", ["rua", "pista", "esteira"], "Cardio", "cardio", 2,
   ["Aqueça 10–15 min com trote leve e 3–4 acelerações curtas.", "Comece um pouco mais devagar do que acha que aguenta; acelere na segunda metade.", "Hidrate-se e anote o tempo: ele recalibra seus ritmos."], "estratégia de prova de corrida ritmo")
ex("caminhada", "Caminhada rápida", "Walking_Treadmill", ["rua", "esteira"], "Cardio", "cardio", 1,
   ["Passos rápidos, braços acompanhando.", "Postura alta.", "Intensidade moderada: respiração acelerada, mas dá para conversar."], "caminhada rápida para saúde")

# ---------- MOBILIDADE / ALONGAMENTO ----------
ex("maior-alongamento", "Alongamento do mundo (world's greatest stretch)", "Worlds_Greatest_Stretch", ["corpo"], "Mobilidade", "mobilidade", 1,
   ["Afundo longo, mão no chão por dentro do pé da frente.", "Gire o tronco levando o braço ao teto.", "Volte e troque o lado."])
ex("gato-camelo", "Gato-camelo", "Cat_Stretch", ["corpo"], "Mobilidade", "mobilidade", 1,
   ["Quatro apoios.", "Arredonde a coluna para cima, depois afunde suavemente.", "Movimento lento acompanhando a respiração."], "gato camelo mobilidade coluna")
ex("postura-crianca", "Postura da criança", "Childs_Pose", ["corpo"], "Mobilidade", "mobilidade", 1,
   ["Ajoelhado, sente nos calcanhares.", "Estenda os braços à frente e relaxe o tronco.", "Respire fundo por 30–60 s."])
ex("flexor-quadril", "Alongamento de flexor do quadril", "Kneeling_Hip_Flexor", ["corpo"], "Mobilidade", "mobilidade", 1,
   ["Ajoelhado em afundo, joelho de trás no chão.", "Contraia o glúteo de trás e leve o quadril à frente.", "Segure 30 s cada lado."])
ex("alongamento-posterior", "Alongamento de posterior de coxa", "Hamstring_Stretch", ["corpo"], "Mobilidade", "mobilidade", 1,
   ["Perna estendida apoiada, coluna reta.", "Incline o tronco a partir do quadril.", "Segure 30 s sem 'balançar'."])
ex("alongamento-quadriceps", "Alongamento de quadríceps", "Quad_Stretch", ["corpo"], "Mobilidade", "mobilidade", 1,
   ["Em pé, segure o pé atrás do corpo.", "Joelhos juntos, quadril levemente à frente.", "30 s cada lado."])
ex("alongamento-panturrilha", "Alongamento de panturrilha na parede", "Calf_Stretch_Hands_Against_Wall", ["corpo"], "Mobilidade", "mobilidade", 1,
   ["Mãos na parede, uma perna atrás estendida.", "Calcanhar de trás no chão.", "30 s cada lado."])
ex("circulos-braco", "Círculos de braço", "Arm_Circles", ["corpo"], "Mobilidade", "mobilidade", 1,
   ["Braços estendidos para os lados.", "Círculos pequenos aumentando para grandes.", "Inverta o sentido."])
ex("circulos-quadril", "Círculos de quadril", "Standing_Hip_Circles", ["corpo"], "Mobilidade", "mobilidade", 1,
   ["Mãos na cintura, pés afastados.", "Faça círculos amplos com o quadril.", "10 para cada lado."])
ex("rolo-quadriceps", "Liberação com rolo (quadríceps)", "Quadriceps-SMR", ["rolo"], "Mobilidade", "mobilidade", 1,
   ["Rolo sob as coxas, apoio nos antebraços.", "Role devagar do quadril ao joelho.", "Pare 20–30 s nos pontos mais sensíveis."])
ex("rolo-panturrilha", "Liberação com rolo (panturrilha)", "Calves-SMR", ["rolo"], "Mobilidade", "mobilidade", 1,
   ["Rolo sob a panturrilha, quadril elevado.", "Role do tornozelo ao joelho.", "Cruze a outra perna por cima para aumentar a pressão."])
ex("rolo-it", "Liberação com rolo (lateral da coxa)", "Iliotibial_Tract-SMR", ["rolo"], "Mobilidade", "mobilidade", 1,
   ["Deitado de lado sobre o rolo.", "Role do quadril até perto do joelho.", "Apoie a perna de cima no chão para dosar a pressão."])
ex("alongamento-peito", "Alongamento de peitoral", "Chest_And_Front_Of_Shoulder_Stretch", ["corpo"], "Mobilidade", "mobilidade", 1,
   ["Antebraço apoiado num batente ou parede.", "Gire o tronco para o lado oposto.", "30 s cada lado."])
ex("rotacao-toracica", "Rotação torácica deitado", "Side-Lying_Floor_Stretch", ["corpo"], "Mobilidade", "mobilidade", 1,
   ["Deitado de lado, joelhos flexionados a 90°.", "Abra o braço de cima girando o tronco.", "Acompanhe com o olhar; 8–10 cada lado."], "rotação torácica deitado de lado mobilidade")
ex("alongamento-adutores", "Alongamento de adutores (borboleta)", "Groin_and_Back_Stretch", ["corpo"], "Mobilidade", "mobilidade", 1,
   ["Sentado, solas dos pés juntas.", "Coluna alta, joelhos caindo para os lados.", "30–60 s respirando."])
ex("equilibrio-unipodal", "Equilíbrio em uma perna", "Balance_Board", ["corpo"], "Equilíbrio", "mobilidade", 1,
   ["Fique numa perna perto de um apoio.", "Mantenha 30 s com o joelho levemente flexionado.", "Avance fechando os olhos ou em superfície instável."], "exercício de equilíbrio em uma perna idosos")
ex("sentar-levantar", "Sentar e levantar da cadeira", "Chair_Squat", ["corpo"], "Pernas", "forca", 1,
   ["Sente-se na borda de uma cadeira firme.", "Levante sem usar as mãos, se possível.", "Sente devagar, controlando."], "sentar e levantar da cadeira exercício")

# ---------- MOBILIDADE E ALONGAMENTO (rotinas de preparo e pós-treino) ----------
ex("balanco-pernas", "Balanço de pernas (leg swing)", "Front_Leg_Raises", ["corpo"], "Mobilidade", "mobilidade", 1,
   ["Apoie uma mão na parede, tronco ereto.", "Balance a perna para frente e para trás, aumentando a amplitude aos poucos.", "Depois balance de lado a lado, cruzando à frente do corpo. Troque a perna."], "leg swing balanço de pernas aquecimento")
ex("circulos-tornozelo", "Círculos de tornozelo", "Ankle_Circles", ["corpo"], "Mobilidade", "mobilidade", 1,
   ["Apoie a ponta do pé no chão (ou eleve o pé).", "Desenhe círculos amplos com o tornozelo.", "10 para cada lado, nos dois pés."], "mobilidade de tornozelo círculos")
ex("circulos-punho", "Círculos de punho", "Wrist_Circles", ["corpo"], "Mobilidade", "mobilidade", 1,
   ["Entrelace os dedos ou deixe as mãos soltas.", "Gire os punhos em círculos amplos.", "Inverta o sentido. Ótimo antes de flexões, socos e raquete."], "mobilidade de punho aquecimento")
ex("circulos-ombro", "Rotação de ombros", "Shoulder_Circles", ["corpo"], "Mobilidade", "mobilidade", 1,
   ["Braços relaxados ao lado do corpo.", "Leve os ombros para cima, para trás e para baixo em círculos.", "10 para trás e 10 para frente."], "rotação de ombros mobilidade")
ex("circulos-joelho", "Círculos de joelho", "Knee_Circles", ["corpo"], "Mobilidade", "mobilidade", 1,
   ["Pés juntos, mãos apoiadas nos joelhos levemente flexionados.", "Faça círculos pequenos e controlados.", "Inverta o sentido. Sem dor."], "círculos de joelho aquecimento")
ex("chute-gluteo", "Calcanhar ao glúteo", "Single_Leg_Butt_Kick", ["corpo"], "Mobilidade", "mobilidade", 1,
   ["Trote no lugar ou deslocando-se.", "Leve o calcanhar em direção ao glúteo alternando as pernas.", "Ritmo leve, tronco alto."], "anfersen calcanhar no glúteo educativo")
ex("carioca", "Carioca (deslocamento cruzado)", "Carioca_Quick_Step", ["corpo"], "Mobilidade", "mobilidade", 1,
   ["Desloque-se de lado cruzando a perna de trás pela frente e por trás.", "Gire o quadril, ombros voltados para frente.", "Volte para o outro lado."], "carioca aquecimento futebol")
ex("abertura-peito-dinamica", "Abertura dinâmica de peito", "Dynamic_Chest_Stretch", ["corpo"], "Mobilidade", "mobilidade", 1,
   ["Braços estendidos à frente na altura dos ombros.", "Abra os braços para trás com ritmo, sentindo o peito abrir.", "Volte e repita 10–15 vezes."], "alongamento dinâmico de peito aquecimento")
ex("spider", "Afundo do homem-aranha", "Spider_Crawl", ["corpo"], "Mobilidade", "mobilidade", 2,
   ["Da prancha, leve um pé ao lado da mão.", "Afunde o quadril e segure 2 s; opcional: gire o tronco abrindo o braço.", "Volte e troque o lado."], "spiderman lunge mobilidade de quadril")
ex("alongamento-gluteo", "Alongamento de glúteo (figura 4)", "Ankle_On_The_Knee", ["corpo"], "Mobilidade", "mobilidade", 1,
   ["Deitado ou sentado, cruze o tornozelo sobre o joelho oposto.", "Puxe a perna de baixo em direção ao peito (ou incline o tronco).", "30 s cada lado, respirando."], "alongamento de glúteo piriforme figura 4")
ex("abraco-joelhos", "Abraço dos joelhos (lombar)", "Hug_Knees_To_Chest", ["corpo"], "Mobilidade", "mobilidade", 1,
   ["Deitado de barriga para cima.", "Abrace os joelhos e traga-os ao peito.", "Balance suavemente de um lado ao outro, relaxando a lombar."], "alongamento lombar joelhos ao peito")
ex("alongamento-triceps", "Alongamento de tríceps", "Triceps_Stretch", ["corpo"], "Mobilidade", "mobilidade", 1,
   ["Leve uma mão atrás da cabeça, cotovelo apontado para cima.", "Com a outra mão, empurre levemente o cotovelo.", "30 s cada lado."])
ex("alongamento-antebraco", "Alongamento de punho e antebraço", "Kneeling_Forearm_Stretch", ["corpo"], "Mobilidade", "mobilidade", 1,
   ["Ajoelhado, apoie as mãos no chão com os dedos virados para você.", "Leve o quadril para trás devagar até sentir o antebraço.", "Segure 20–30 s; depois vire o dorso das mãos."], "alongamento de antebraço e punho")
ex("alongamento-pescoco", "Alongamento lateral de pescoço", "Side_Neck_Stretch", ["corpo"], "Mobilidade", "mobilidade", 1,
   ["Sentado ou em pé, ombros relaxados.", "Incline a orelha em direção ao ombro, sem girar.", "Segure 20–30 s cada lado, sem puxar com força."], "alongamento de pescoço lateral")
ex("alongamento-lateral", "Alongamento lateral de tronco", "Standing_Lateral_Stretch", ["corpo"], "Mobilidade", "mobilidade", 1,
   ["Em pé, braço elevado acima da cabeça.", "Incline o tronco para o lado oposto.", "Segure 20–30 s cada lado."], "alongamento lateral do tronco em pé")
ex("torcao-coluna", "Torção de coluna sentado", "Spinal_Stretch", ["corpo"], "Mobilidade", "mobilidade", 1,
   ["Sentado, cruze uma perna sobre a outra.", "Gire o tronco para o lado da perna de cima, coluna alta.", "Segure 30 s cada lado respirando fundo."], "torção de coluna sentado alongamento")
ex("alongamento-dorsal", "Alongamento de dorsal", "Upper_Back_Stretch", ["corpo"], "Mobilidade", "mobilidade", 1,
   ["Entrelace os dedos à frente e empurre as mãos para longe.", "Arredonde as costas afastando as escápulas.", "Segure 20–30 s."], "alongamento de dorsal costas")
ex("moinho", "Moinho (rotação de tronco em pé)", "Windmills", ["corpo"], "Mobilidade", "mobilidade", 1,
   ["Pés afastados, braços abertos.", "Gire o tronco levando a mão ao pé oposto.", "Alterne os lados em ritmo controlado."], "moinho exercício de mobilidade windmill")
