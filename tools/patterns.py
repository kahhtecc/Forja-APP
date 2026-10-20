# Padrões de movimento (usados pelo gerador para escolher e trocar exercícios)
# e restrições (limitações que pedem evitar o exercício).

PADROES = {
    # pernas
    "agachamento-livre": ["agachar"], "agachamento-elastico": ["agachar"], "agachamento-goblet": ["agachar"],
    "agachamento-barra": ["agachar"], "agachamento-frontal": ["agachar"], "leg-press": ["agachar"],
    "hack": ["agachar"], "sentar-levantar": ["agachar"],
    "agachamento-salto": ["pliometria"], "box-jump": ["pliometria"], "salto-distancia": ["pliometria"],
    "bound-lateral": ["pliometria"], "salto-tesoura": ["pliometria"], "tuck-jump": ["pliometria"],
    "cadeira-extensora": ["quadriceps"], "mesa-flexora": ["posterior"], "cadeira-flexora": ["posterior"],
    "afundo": ["unilateral"], "afundo-halteres": ["unilateral"], "passada-andando": ["unilateral"],
    "bulgaro": ["unilateral"], "step-up": ["unilateral"],
    "terra": ["dobradica"], "stiff": ["dobradica"], "stiff-halteres": ["dobradica"],
    "terra-uma-perna": ["dobradica", "unilateral"], "swing": ["dobradica", "potencia"],
    "ponte-gluteo": ["gluteo"], "ponte-unilateral": ["gluteo"], "elevacao-quadril": ["gluteo"],
    "coice-gluteo": ["gluteo"], "abdutora": ["gluteo"], "monster-walk": ["gluteo"],
    "panturrilha-pe": ["panturrilha"], "panturrilha-sentado": ["panturrilha"], "panturrilha-elastico": ["panturrilha"],
    # peito / empurrar
    "flexao": ["empurrar_h"], "flexao-inclinada": ["empurrar_h"], "flexao-joelhos": ["empurrar_h"],
    "flexao-declinada": ["empurrar_h"], "flexao-diamante": ["triceps", "empurrar_h"],
    "flexao-pliometrica": ["potencia_sup"], "supino-reto": ["empurrar_h"], "supino-halteres": ["empurrar_h"],
    "supino-inclinado": ["empurrar_h"], "supino-inclinado-barra": ["empurrar_h"], "supino-maquina": ["empurrar_h"],
    "supino-elastico": ["empurrar_h"], "paralelas": ["empurrar_h", "triceps"],
    "crucifixo": ["peito_iso"], "crossover": ["peito_iso"], "peck-deck": ["peito_iso"], "crucifixo-elastico": ["peito_iso"],
    # costas / puxar
    "barra-fixa": ["puxar_v"], "barra-supinada": ["puxar_v"], "barra-assistida": ["puxar_v"],
    "puxada-frente": ["puxar_v"], "puxada-triangulo": ["puxar_v"], "pulldown-elastico": ["puxar_v"],
    "pullover-polia": ["costas_iso"],
    "remada-baixa": ["puxar_h"], "remada-curvada": ["puxar_h"], "remada-unilateral": ["puxar_h"],
    "remada-elastico": ["puxar_h"], "remada-invertida": ["puxar_h"],
    "superman": ["lombar"], "hiperextensao": ["lombar"],
    "face-pull": ["ombro_post"], "band-pull-apart": ["ombro_post"], "crucifixo-inverso": ["ombro_post"],
    "rotacao-externa": ["ombro_post"], "encolhimento": ["trapezio"],
    # ombros
    "desenvolvimento-halteres": ["empurrar_v"], "desenvolvimento-barra": ["empurrar_v"],
    "desenvolvimento-maquina": ["empurrar_v"], "desenvolvimento-elastico": ["empurrar_v"], "arnold": ["empurrar_v"],
    "pike-pushup": ["empurrar_v"],
    "elevacao-lateral": ["ombro_lat"], "elevacao-lateral-elastico": ["ombro_lat"], "elevacao-frontal": ["ombro_lat"],
    # braços
    "rosca-direta": ["biceps"], "rosca-halteres": ["biceps"], "rosca-martelo": ["biceps"], "rosca-elastico": ["biceps"],
    "rosca-scott": ["biceps"],
    "triceps-polia": ["triceps"], "triceps-frances": ["triceps"], "triceps-testa": ["triceps"],
    "triceps-banco": ["triceps"], "triceps-elastico": ["triceps"], "triceps-coice": ["triceps"],
    # core
    "prancha": ["core"], "prancha-lateral": ["core"], "abdominal": ["core"], "abdominal-infra": ["core"],
    "dead-bug": ["core"], "russian-twist": ["core"], "abdominal-bicicleta": ["core"],
    "elevacao-pernas-barra": ["core"], "roda-abdominal": ["core"], "pallof": ["core"], "abdominal-polia": ["core"],
    "canivete": ["core"],
    # condicionamento / potência
    "mountain-climber": ["condicionamento", "core"], "burpee": ["condicionamento"], "polichinelo": ["condicionamento"],
    "corda": ["condicionamento"], "battle-rope": ["condicionamento"], "bear-crawl": ["condicionamento"],
    "thruster": ["potencia", "condicionamento"], "power-clean": ["potencia"],
    "arremesso-medicine": ["potencia_sup", "condicionamento"], "passe-medicine": ["potencia_sup"],
    "arremesso-rotacional": ["potencia_rot"], "farmer-walk": ["carregar"], "sled-push": ["potencia", "condicionamento"],
    "turkish-getup": ["core", "carregar"], "inchworm": ["mobilidade", "aquecimento"],
    # luta
    "sombra": ["luta"], "saco-combinacoes": ["luta"], "sprawl": ["luta", "condicionamento"],
    "ponte-pescoco": ["luta_solo"], "fuga-quadril": ["luta_solo"], "isometria-pescoco": ["pescoco"],
    "nordico": ["posterior"],
    # cardio
    "corrida-leve": ["corrida"], "caminhada-corrida": ["corrida"], "tiros": ["corrida"], "tempo-run": ["corrida"],
    "longao": ["corrida"], "prova": ["corrida"], "educativos-corrida": ["corrida", "aquecimento"], "caminhada": ["cardio"],
    "bike-leve": ["bike"], "bike-intervalado": ["bike"], "bike-subida": ["bike"], "bike-cadencia": ["bike"],
    "eliptico": ["cardio"], "remo-ergometro": ["cardio"], "escada": ["cardio"],
    # mobilidade
    "maior-alongamento": ["mobilidade", "aquecimento"], "gato-camelo": ["mobilidade", "aquecimento"],
    "postura-crianca": ["alongamento"], "flexor-quadril": ["alongamento"], "alongamento-posterior": ["alongamento"],
    "alongamento-quadriceps": ["alongamento"], "alongamento-panturrilha": ["alongamento"],
    "circulos-braco": ["aquecimento"], "circulos-quadril": ["aquecimento"], "rolo-quadriceps": ["rolo"],
    "rolo-panturrilha": ["rolo"], "rolo-it": ["rolo"], "alongamento-peito": ["alongamento"],
    "rotacao-toracica": ["mobilidade"], "balanco-pernas": ["aquecimento"], "circulos-tornozelo": ["aquecimento"],
    "circulos-punho": ["aquecimento"], "circulos-ombro": ["aquecimento"], "circulos-joelho": ["aquecimento"], "chute-gluteo": ["aquecimento"],
    "carioca": ["aquecimento"], "abertura-peito-dinamica": ["aquecimento"], "spider": ["mobilidade"], "moinho": ["mobilidade", "aquecimento"],
    "alongamento-gluteo": ["alongamento"], "abraco-joelhos": ["alongamento"], "alongamento-triceps": ["alongamento"],
    "alongamento-antebraco": ["alongamento"], "alongamento-pescoco": ["alongamento"], "alongamento-lateral": ["alongamento"],
    "torcao-coluna": ["alongamento"], "alongamento-dorsal": ["alongamento"], "alongamento-adutores": ["alongamento"], "equilibrio-unipodal": ["equilibrio"],
}

# Limitações informadas no questionário -> exercícios a evitar (conservador, não diagnóstico)
_J = "joelho"
_L = "lombar"
_O = "ombro"
_P = "punho"
_I = "impacto"  # alto impacto: evitar para iniciantes muito acima do peso, 50+ e queixa de joelho
EVITAR = {
    "agachamento-salto": [_J, _I], "box-jump": [_J, _I], "salto-distancia": [_J, _I], "bound-lateral": [_J, _I],
    "salto-tesoura": [_J, _I], "tuck-jump": [_J, _I], "burpee": [_J, _I, _P], "polichinelo": [_I],
    "corda": [_I], "afundo": [_J], "afundo-halteres": [_J], "passada-andando": [_J], "bulgaro": [_J],
    "agachamento-barra": [_J, _L], "agachamento-frontal": [_J, _L], "hack": [_J], "cadeira-extensora": [_J],
    "terra": [_L], "stiff": [_L], "remada-curvada": [_L], "power-clean": [_L, _O, _P], "swing": [_L],
    "roda-abdominal": [_L, _O], "canivete": [_L], "abdominal-infra": [_L], "elevacao-pernas-barra": [_O, _L],
    "russian-twist": [_L], "superman": [_L], "hiperextensao": [_L], "sled-push": [_L],
    "desenvolvimento-barra": [_O, _L], "pike-pushup": [_O, _P], "paralelas": [_O], "triceps-banco": [_O],
    "flexao-pliometrica": [_O, _P], "barra-fixa": [_O], "elevacao-frontal": [_O], "arnold": [_O],
    "supino-reto": [_O], "supino-inclinado-barra": [_O], "turkish-getup": [_O],
    "flexao": [_P], "flexao-declinada": [_P], "flexao-diamante": [_P, _O], "mountain-climber": [_P],
    "bear-crawl": [_P], "spider": [_P], "alongamento-antebraco": [_P], "sprawl": [_J, _L, _I], "thruster": [_O, _J],
}
