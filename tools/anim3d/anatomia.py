"""Relevo muscular procedural para a malha do MakeHuman (em repouso, antes do esqueleto).

Cada músculo é um "domo" desenhado sobre a pele num sistema de coordenadas do segmento:
  tronco: "frente"/"costas" (u = |x|, v = z) e "lado" (u = y, v = z), em unidades da malha (~10 cm)
  membros: cilíndricas em volta do osso (u = ângulo em graus: 0 frente, 90 lateral/fora, 180 trás, -90 medial; v = t de 0 a 1 ao longo do osso)
Os domos se combinam por máximo suave: onde dois músculos se encontram a pele afunda (sulco), no centro ela sobe (volume).
O mesmo campo dá as regiões de cor (forma real de cada músculo) e um atributo de cavidade para o material.
"""
import math

import numpy as np

# ---------------------------------------------------------------- utilidades de malha


def arestas_vizinhos(E, n):
    deg = np.bincount(E.ravel(), minlength=n).astype(float)
    return E, np.maximum(deg, 1)


def suavizar_campo(arr, E, deg, passos=1, lam=0.5):
    arr = np.asarray(arr, dtype=float)
    multi = arr.ndim == 2
    cols = [arr[:, j] for j in range(arr.shape[1])] if multi else [arr]
    out = []
    n = len(deg)
    for c in cols:
        for _ in range(passos):
            s = np.bincount(E[:, 0], weights=c[E[:, 1]], minlength=n) + np.bincount(E[:, 1], weights=c[E[:, 0]], minlength=n)
            c = c * (1 - lam) + lam * s / deg
        out.append(c)
    return np.stack(out, axis=1) if multi else out[0]


def _smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


# ---------------------------------------------------------------- músculos
# (nome, região de cor, sistema, u0, v0, a, b, rotação°, altura, expoente da superelipse, afinamento)
#   afinamento > 0 alarga a ponta de v maior (gota); < 0 a de v menor
# alturas em unidades (0.1 = 1 cm)

M = []


def mus(nome, reg, sis, u0, v0, a, b, rot=0.0, h=0.08, n=2.0, af=0.0, exp=0.55):
    M.append(dict(nome=nome, reg=reg, sis=sis, u0=u0, v0=v0, a=a, b=b, rot=rot, h=h, n=n, af=af, exp=exp))


# --- tronco, frente (u = |x|, v = z)
mus("peitoral", "peito", "frente", 0.92, 5.02, 0.86, 0.80, 6, 0.12, 2.5, af=-0.25, exp=0.45)
mus("peitoral_clav", "peito", "frente", 0.78, 5.62, 0.62, 0.30, -10, 0.06, 2.0)
for i, (z, hz) in enumerate(((3.93, 0.31), (3.30, 0.29), (2.70, 0.27))):
    mus(f"reto_abd{i}", "abdomen", "frente", 0.42, z, 0.34 - 0.015 * i, hz, 0, 0.075, 3.2, exp=0.5)
mus("reto_abd_inf", "abdomen", "frente", 0.38, 1.85, 0.30, 0.52, 0, 0.05, 2.6, af=-0.35)
mus("obliquo", "obliquos", "frente", 1.10, 2.65, 0.30, 0.78, -14, 0.06, 2.2)
for i, z in enumerate((4.62, 4.25, 3.90)):
    mus(f"serratil{i}", "obliquos", "lado", -0.55, z, 0.42, 0.13, 24, 0.045, 2.0)
mus("trap_sup_f", "trapezio", "frente", 0.85, 6.30, 0.42, 0.22, -28, 0.05, 2.0)

# --- tronco, costas
mus("trap_sup", "trapezio", "costas", 0.62, 6.15, 0.74, 0.40, -20, 0.08, 2.0)
mus("trap_med", "trapezio", "costas", 0.36, 5.30, 0.44, 0.70, 0, 0.06, 2.2, af=0.45)
mus("trap_inf", "trapezio", "costas", 0.20, 4.40, 0.24, 0.62, 0, 0.04, 2.0, af=0.5)
mus("infraespinhal", "dorsal", "costas", 1.02, 5.15, 0.40, 0.38, -18, 0.07, 2.0)
mus("redondo", "dorsal", "costas", 1.38, 4.92, 0.30, 0.20, -35, 0.06, 2.0)
mus("dorsal", "dorsal", "costas", 1.02, 3.95, 0.50, 1.25, -24, 0.10, 2.2, af=0.35)
mus("eretor", "lombar", "costas", 0.32, 2.55, 0.22, 1.05, 0, 0.065, 2.4)
mus("gluteo_max", "gluteo", "costas", 0.78, 0.55, 0.70, 0.78, 12, 0.10, 2.2)
mus("gluteo_med", "gluteo", "costas", 1.25, 1.45, 0.38, 0.32, -20, 0.06, 2.0)

# --- braço (osso ombro -> cotovelo)
mus("deltoide_ant", "deltoide", "braco", 22, 0.06, 42, 0.36, 0, 0.10, 2.0, af=-0.3)
mus("deltoide_lat", "deltoide", "braco", 92, 0.08, 40, 0.40, 0, 0.11, 2.0, af=-0.3)
mus("deltoide_pos", "deltoide", "braco", 158, 0.06, 38, 0.36, 0, 0.09, 2.0, af=-0.3)
mus("biceps", "biceps", "braco", -10, 0.62, 62, 0.30, 0, 0.11, 2.0)
mus("braquial", "biceps", "braco", 72, 0.70, 26, 0.20, 0, 0.05, 2.0)
mus("triceps_lat", "triceps", "braco", 135, 0.48, 40, 0.26, 0, 0.09, 2.0, af=-0.2)
mus("triceps_long", "triceps", "braco", -150, 0.52, 46, 0.30, 0, 0.10, 2.0)

# --- antebraço (cotovelo -> punho); 0 = face flexora
mus("braquiorradial", "antebraco", "antebraco", 70, 0.24, 36, 0.28, 0, 0.08, 2.0)
mus("flexores", "antebraco", "antebraco", -40, 0.28, 62, 0.30, 0, 0.07, 2.0)
mus("extensores", "antebraco", "antebraco", 150, 0.28, 52, 0.30, 0, 0.065, 2.0)

# --- coxa (quadril -> joelho)
mus("vasto_lat", "quadriceps", "coxa", 72, 0.52, 44, 0.38, 0, 0.10, 2.0)
mus("reto_femoral", "quadriceps", "coxa", 8, 0.47, 30, 0.38, 0, 0.10, 2.0)
mus("vasto_med", "quadriceps", "coxa", -42, 0.80, 34, 0.15, 0, 0.12, 2.0, af=0.35)
mus("sartorio_adut", "adutores", "coxa", -95, 0.32, 38, 0.30, 0, 0.07, 2.0)
mus("biceps_fem", "posterior", "coxa", 142, 0.55, 30, 0.34, 0, 0.08, 2.0)
mus("semitend", "posterior", "coxa", -158, 0.55, 30, 0.34, 0, 0.08, 2.0)

# --- perna (joelho -> tornozelo)
mus("gastro_med", "panturrilha", "perna", -150, 0.30, 34, 0.23, 0, 0.11, 2.0, af=0.25)
mus("gastro_lat", "panturrilha", "perna", 150, 0.27, 30, 0.20, 0, 0.09, 2.0, af=0.25)
mus("soleo", "panturrilha", "perna", 180, 0.58, 70, 0.14, 0, 0.05, 2.0)
mus("tibial", "tibial", "perna", 48, 0.32, 26, 0.32, 0, 0.06, 2.0)

SISTEMAS_MEMBRO = {
    "braco": (("shoulder01", "upperarm01", "upperarm02"), "upperarm01", "lowerarm01"),
    "antebraco": (("lowerarm01", "lowerarm02"), "lowerarm01", "wrist"),
    "coxa": (("upperleg01", "upperleg02"), "upperleg01", "lowerleg01"),
    "perna": (("lowerleg01", "lowerleg02"), "lowerleg01", "foot"),
}
TRONCO_OSSOS = ["spine01", "spine02", "spine03", "spine04", "spine05", "breast.L", "breast.R", "root", "pelvis.L", "pelvis.R",
                "clavicle.L", "clavicle.R", "neck01"]


def _cilindricas(Vm, A, B, ref):
    u = B - A
    L = np.linalg.norm(u)
    u = u / L
    r = Vm - A
    s = r @ u
    t = s / L
    rad = r - s[:, None] * u
    f = ref - (ref @ u) * u
    f /= np.linalg.norm(f)
    lat = np.cross(u, f)
    if lat[0] < 0:
        lat = -lat
    th = np.degrees(np.arctan2(rad @ lat, rad @ f))
    return th, t


def esculpir(V, N, W, J, E, deg, intensidade=1.0):
    """V, N: vértices/normais em repouso (Blender, z para cima, -y frente). W: pesos por osso. J(osso, cauda) -> junta.
    Retorna (V deslocado, dict região -> máscara 0..1, cavidade 0..1)."""
    n = len(V)
    zero = np.zeros(n)
    soma = lambda nomes: sum((W.get(b, zero) for b in nomes), zero.copy())  # noqa: E731
    ax = np.abs(V[:, 0])
    Vm = V.copy()
    Vm[:, 0] = ax
    nx, ny = N[:, 0] * np.sign(V[:, 0] + 1e-9), N[:, 1]
    tronco = np.clip(soma(TRONCO_OSSOS), 0, 1)
    frente = _smooth(-0.2, 0.25, -ny) * tronco
    costas = _smooth(-0.2, 0.25, ny) * tronco
    lado = _smooth(0.15, 0.55, nx) * tronco
    coords = {"frente": (ax, V[:, 2], frente), "costas": (ax, V[:, 2], costas), "lado": (V[:, 1], V[:, 2], lado)}
    FRENTE = np.array((0.0, -1.0, 0.0))
    for sis, (ossos, a, b) in SISTEMAS_MEMBRO.items():
        A = np.array(J(a + ".L")); B = np.array(J(b + ".L"))
        if sis == "antebraco":
            ref = -(np.array(J("lowerarm01.L")) - np.array(J("upperarm01.L")))
        else:
            ref = FRENTE
        th, t = _cilindricas(Vm, A, B, ref)
        memb = np.clip(soma([o + ".L" for o in ossos]) + soma([o + ".R" for o in ossos]), 0, 1)
        coords[sis] = (th, t, memb)
    domos = {}
    P = 4.0
    acc = np.zeros(n)
    for m in M:
        u, v, w = coords[m["sis"]]
        du = u - m["u0"]
        if m["sis"] in SISTEMAS_MEMBRO:
            du = (du + 180) % 360 - 180
        dv = v - m["v0"]
        c, s = math.cos(math.radians(m["rot"])), math.sin(math.radians(m["rot"]))
        p = du * c + dv * s
        q = -du * s + dv * c
        qa = np.clip(q / m["b"], -1.5, 1.5)
        a = m["a"] * np.clip(1 + m["af"] * qa, 0.2, 3)
        r = (np.abs(p / a) ** m["n"] + np.abs(qa) ** m["n"]) ** (1 / m["n"])
        d = np.clip(1 - r * r, 0, 1) ** m["exp"] * w
        domos[m["nome"]] = (d, m)
        acc += (d * m["h"]) ** P
    D = acc ** (1 / P) * intensidade
    D = suavizar_campo(D, E, deg, 2, 0.5)
    # base de compensação: a pele "sem músculo" afunda um pouco (ossos, tendões) e o volume total quase não muda
    corpo = np.clip(tronco + sum(coords[s][2] for s in SISTEMAS_MEMBRO), 0, 1)
    corpo = suavizar_campo(corpo, E, deg, 6, 0.5)
    base = 0.035 * intensidade * corpo
    desloc = D - base
    V2 = V + N * desloc[:, None]
    # cavidade: quanto a pele está abaixo da média local (sulcos entre músculos)
    media = suavizar_campo(desloc, E, deg, 12, 0.5)
    cav = np.clip((media - desloc) / 0.03, 0, 1)
    regioes = {}
    for nome, (d, m) in domos.items():
        mask = _smooth(0.0, 0.14, d)
        regioes[m["reg"]] = np.maximum(regioes.get(m["reg"], zero), mask)
    return V2, regioes, cav, domos
