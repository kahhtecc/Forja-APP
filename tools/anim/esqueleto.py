"""Esqueleto 2D (vista lateral, olhando para a direita) usado nas animações do Forja.

Formato de uma animação (JSON):
{
  "id": "agachamento-livre",
  "fixo": "pes",                            # opcional: "pes" ou "maos" ficam parados na horizontal (o corpo se move em volta)
  "props": [ ...acessórios... ],
  "destaque": ["coxa", "gluteo"],          # segmentos pintados na cor de destaque (músculos trabalhados)
  "tempos": [1.0, 1.0],                     # segundos de cada transição (quadro i -> i+1; o último volta ao primeiro)
  "quadros": [ pose, pose, ... ]            # 2 a 6 poses-chave
}

Pose (todos os ângulos em graus, ABSOLUTOS, medidos a partir de "apontando para baixo"):
   0 = para baixo, 90 = para frente (+x, direção em que a pessoa olha), 180 = para cima, -90 = para trás.
{
  "x": 0,            # posição horizontal do quadril (unidades ~10 cm). Opcional, padrão 0.
  "y": null,         # altura do quadril. Se omitido, o corpo é apoiado no chão automaticamente (ponto mais baixo em y=0).
  "ay": 0,           # altura extra somada depois de apoiar (saltos).
  "t": 180,          # tronco (quadril -> pescoço). Em pé = 180; inclinado 45° à frente = 135; deitado de costas = 90 ou -90.
  "c": 180,          # cabeça (pescoço -> centro da cabeça).
  "bf": [0, 0],      # braço da frente (perto da câmera): [braço, antebraço]
  "bt": [0, 0],      # braço de trás
  "pf": [0, 0, 90],  # perna da frente: [coxa, canela, pé]
  "pt": [0, 0, 90]   # perna de trás
}
Comprimentos (unidades): tronco 5.2, pescoço 0.7, cabeça raio 1.0, braço 3.0, antebraço 2.7, coxa 4.4, canela 4.3, pé 1.5.
Joelho: flexão = coxa - canela (0 a 160). Cotovelo: flexão = antebraço - braço (0 a 160).

Acessórios ("props"):
  {"tipo": "barra", "em": "maos"}                  barra olímpica vista de lado (anilha) nas mãos
  {"tipo": "halter", "em": "maos"}                 halter em cada mão
  {"tipo": "kettlebell", "em": "maos"}             kettlebell entre as mãos
  {"tipo": "bola", "em": "maos"}                   medicine ball
  {"tipo": "elastico", "de": "maos", "ate": [x, y]}  elástico/cabo da mão até um ponto fixo (ou "ate": "pes")
  {"tipo": "cabo", "de": "maos", "ate": [x, y]}    cabo de polia (desenha a polia no ponto)
  {"tipo": "banco", "x": -6, "y": 0, "w": 9, "h": 4.3}   banco/caixa/cadeira (retângulo apoiado no chão)
  {"tipo": "barra_fixa", "x": 1, "y": 21}          barra fixa (ponto) com suportes
  {"tipo": "saco", "x": 9}                         saco de pancada pendurado
  {"tipo": "bike", "x": 0}                         bicicleta/ergométrica sob o quadril
  {"tipo": "esteira"}                              faixa de esteira no chão
  {"tipo": "rolo", "x": 2, "y": 0.8}               rolo de liberação
  {"tipo": "corda"}                                corda de pular (arco ligando as mãos por baixo dos pés)
  {"tipo": "tapete"}                               colchonete
  {"tipo": "maquina", "x": -4, "y": 0, "w": 6, "h": 5}   máquina genérica (bloco)
"""
import math

L = dict(tronco=5.2, pescoco=0.7, cabeca=1.0, braco=3.0, antebraco=2.7, coxa=4.4, canela=4.3, pe=1.5)
PADRAO = {"x": 0, "y": None, "ay": 0, "t": 180, "c": 180, "bf": [0, 0], "bt": [0, 0], "pf": [0, 0, 90], "pt": [0, 0, 90]}


def _v(ang, comp):
    r = math.radians(ang)
    return (math.sin(r) * comp, -math.cos(r) * comp)  # 0 = para baixo (y negativo)


def _soma(a, b):
    return (a[0] + b[0], a[1] + b[1])


def completar(p):
    q = dict(PADRAO)
    q.update({k: v for k, v in p.items() if v is not None or k == "y"})
    for k in ("bf", "bt"):
        q[k] = list(q[k]) + [0] * (2 - len(q[k]))
    for k in ("pf", "pt"):
        q[k] = list(q[k]) + [0, 0, 90][len(q[k]):]
    return q


def pontos(p, fixo=None, ref_x=None):
    """Calcula as posições das articulações. Retorna dict nome -> (x, y).
    fixo: "pes" ou "maos" mantém esse ponto parado na horizontal (em ref_x) — o corpo se move em volta dele."""
    p = completar(p)
    quadril = (p["x"], 0.0)
    pescoco = _soma(quadril, _v(p["t"], L["tronco"]))
    ombro = _soma(quadril, _v(p["t"], L["tronco"] * 0.92))
    cabeca = _soma(pescoco, _v(p["c"], L["pescoco"] + L["cabeca"]))
    j = {"quadril": quadril, "pescoco": pescoco, "ombro": ombro, "cabeca": cabeca}
    for lado in ("f", "t"):
        b, a = p["b" + lado]
        cot = _soma(ombro, _v(b, L["braco"]))
        mao = _soma(cot, _v(a, L["antebraco"]))
        c, s, pe = p["p" + lado]
        joe = _soma(quadril, _v(c, L["coxa"]))
        tor = _soma(joe, _v(s, L["canela"]))
        ponta = _soma(tor, _v(pe, L["pe"]))
        calc = _soma(tor, _v(pe + 180, L["pe"] * 0.25))
        j.update({"cotovelo_" + lado: cot, "mao_" + lado: mao, "joelho_" + lado: joe, "tornozelo_" + lado: tor, "ponta_" + lado: ponta, "calcanhar_" + lado: calc})
    # apoio no chão
    if p["y"] is None:
        candidatos = [v[1] for k, v in j.items() if k != "cabeca"] + [j["cabeca"][1] - L["cabeca"]]
        dy = -min(candidatos)
    else:
        dy = p["y"]
    dy += p.get("ay", 0) or 0
    dx = 0.0
    if fixo in ("pes", "maos") and ref_x is not None:
        chave = "tornozelo_f" if fixo == "pes" else "mao_f"
        dx = ref_x - j[chave][0]
    return {k: (v[0] + dx, v[1] + dy) for k, v in j.items()}


def pontos_anim(anim, pose):
    """Pontos de uma pose respeitando o campo "fixo" da animação (referência = primeiro quadro)."""
    fixo = anim.get("fixo")
    ref = None
    if fixo in ("pes", "maos"):
        ref = pontos(anim["quadros"][0])["tornozelo_f" if fixo == "pes" else "mao_f"][0]
    return pontos(pose, fixo, ref)


def interpolar(a, b, t):
    """Interpolação suave (ease in-out) entre duas poses."""
    a, b = completar(a), completar(b)
    e = t * t * (3 - 2 * t)
    out = {}
    for k in PADRAO:
        va, vb = a[k], b[k]
        if isinstance(va, list):
            out[k] = [x + (y - x) * e for x, y in zip(va, vb)]
        elif va is None or vb is None:
            out[k] = None
        else:
            out[k] = va + (vb - va) * e
    return out


def validar(anim):
    """Avisos de anatomia e formato."""
    avisos = []
    q = anim.get("quadros", [])
    if not 2 <= len(q) <= 6:
        avisos.append(f"use de 2 a 6 quadros (tem {len(q)})")
    if len(anim.get("tempos", [])) != len(q):
        avisos.append(f"'tempos' deve ter {len(q)} valores (um por transição, incluindo a volta ao início)")
    for i, p in enumerate(q):
        p = completar(p)
        for lado in ("f", "t"):
            c, s, _ = p["p" + lado]
            joelho = c - s
            if not -5 <= joelho <= 165:
                avisos.append(f"quadro {i}: joelho {lado} dobrando ao contrário ({joelho:.0f}°)")
            b, a = p["b" + lado]
            cot = a - b
            if not -10 <= cot <= 165:
                avisos.append(f"quadro {i}: cotovelo {lado} dobrando ao contrário ({cot:.0f}°)")
        pts = pontos_anim(anim, p)
        if pts["cabeca"][1] < -0.5:
            avisos.append(f"quadro {i}: cabeça abaixo do chão")
    return avisos


def apoios(anim, pose):
    """Altura (y) dos pontos de contato, para conferir o que toca o chão."""
    pts = pontos_anim(anim, pose)
    return {k: round(pts[k][1], 2) for k in ("mao_f", "mao_t", "ponta_f", "calcanhar_f", "joelho_f", "quadril", "cabeca")}
