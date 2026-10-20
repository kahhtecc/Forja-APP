"""Interpolação natural das poses-chave (spline cúbica de Hermite em laço fechado).

Cada canal (ângulo, posição, quaternion) vira uma "trilha" que PASSA pelos quadros-chave nos instantes dados por
"tempos". As tangentes são de Catmull-Rom não uniforme (média ponderada das inclinações vizinhas), amortecidas e
limitadas (Fritsch-Carlson) para não ultrapassar a pose; nos pontos de inversão de um movimento de ida e volta a
tangente é zero (o corpo desacelera e volta, como uma pessoa real). Ângulos são desenrolados (sem saltos de 360°) e o
laço fecha sem emenda (o último quadro volta ao primeiro com a mesma tangente).
"""
import math

import numpy as np

AMORTECIMENTO = 0.9  # 1 = Catmull-Rom puro; menor = mais "assentado" em cada pose


def _wrap(d):
    return (d + 180.0) % 360.0 - 180.0


class Trilha:
    """Spline cúbica periódica de um vetor de valores (n chaves x m componentes)."""

    def __init__(self, tempos, valores, angular=False):
        v = np.array(valores, dtype=float)
        if v.ndim == 1:
            v = v[:, None]
        n = len(v)
        self.n = n
        self.dt = np.array([max(1e-3, float(t)) for t in tempos[:n]] + [1.0] * max(0, n - len(tempos)))
        self.t0 = np.concatenate([[0.0], np.cumsum(self.dt)])  # t0[i] = início do trecho i; t0[n] = período
        self.T = self.t0[-1]
        if angular:
            for i in range(1, n):
                v[i] = v[i - 1] + _wrap(v[i] - v[i - 1])
            fim = v[n - 1] + _wrap(v[0] - v[n - 1])
            self.periodo = fim - v[0]  # múltiplo de 360 (0 em movimentos que vão e voltam)
        else:
            self.periodo = np.zeros(v.shape[1])
        self.v = v
        self.m = self._tangentes()

    def _val(self, i):
        q, r = divmod(i, self.n)
        return self.v[r] + q * self.periodo

    def _tangentes(self):
        n = self.n
        m = np.zeros_like(self.v)
        if n < 2:
            return m
        for i in range(n):
            dt0 = self.dt[(i - 1) % n]
            dt1 = self.dt[i]
            d0 = (self._val(i) - self._val(i - 1)) / dt0
            d1 = (self._val(i + 1) - self._val(i)) / dt1
            mi = (dt1 * d0 + dt0 * d1) / (dt0 + dt1) * AMORTECIMENTO
            inversao = d0 * d1 <= 0
            lim = 3.0 * np.minimum(np.abs(d0), np.abs(d1))
            mi = np.clip(mi, -lim, lim)
            mi[inversao] = 0.0
            m[i] = mi
        return m

    def segmento(self, tau):
        """(índice do trecho, fração 0..1) para o instante tau (periódico)."""
        tau = tau % self.T
        i = int(np.searchsorted(self.t0, tau, side="right") - 1)
        i = min(max(i, 0), self.n - 1)
        return i, (tau - self.t0[i]) / self.dt[i]

    def __call__(self, tau):
        if self.n < 2:
            return self.v[0].copy()
        voltas = math.floor(tau / self.T)
        i, u = self.segmento(tau)
        p0, p1 = self._val(i), self._val(i + 1)
        m0, m1 = self.m[i] * self.dt[i], self.m[(i + 1) % self.n] * self.dt[i]
        u2, u3 = u * u, u * u * u
        h00, h10, h01, h11 = 2 * u3 - 3 * u2 + 1, u3 - 2 * u2 + u, -2 * u3 + 3 * u2, u3 - u2
        return h00 * p0 + h10 * m0 + h01 * p1 + h11 * m1 + voltas * self.periodo


def suave(u, a=0.0, b=1.0):
    t = min(1.0, max(0.0, (u - a) / (b - a))) if b > a else float(u >= a)
    return t * t * (3 - 2 * t)


# ------------------------------------------------------------------ poses

ANGULOS = ("t", "c", "tr", "rol", "inc", "cinc", "cr", "bfa", "bta", "afa", "ata", "pfa", "pta")
LINEARES = ("x", "z", "ay", "oe")
LISTAS = {"bf": 2, "bt": 2, "pf": 3, "pt": 3}
PADRAO = {"x": 0.0, "z": 0.0, "ay": 0.0, "oe": 0.0, "t": 180.0, "c": 180.0, "tr": 0.0, "rol": 0.0, "inc": 0.0, "cinc": 0.0, "cr": 0.0,
          "bfa": 0.0, "bta": 0.0, "afa": 0.0, "ata": 0.0, "pfa": 0.0, "pta": 0.0, "bf": [0.0, 0.0], "bt": [0.0, 0.0], "pf": [0.0, 0.0, 90.0], "pt": [0.0, 0.0, 90.0]}


def normalizar(p):
    """Pose completa (todos os canais numéricos). 'afa'/'ata' ausentes = abdução do braço; 'y' fica como está."""
    q = {}
    for k, d in PADRAO.items():
        v = p.get(k)
        if isinstance(d, list):
            v = list(v) if isinstance(v, (list, tuple)) else []
            v = [float(x) for x in v] + d[len(v):]
            q[k] = v[:len(d)]
        else:
            q[k] = float(v) if v is not None else d
    if p.get("afa") is None:
        q["afa"] = q["bfa"]
    if p.get("ata") is None:
        q["ata"] = q["bta"]
    q["y"] = p.get("y")
    return q


class TrilhasPose:
    """Todas as trilhas de uma animação. __call__(tau) devolve a pose interpolada (formato normalizado)."""

    def __init__(self, quadros, tempos):
        self.chaves = [normalizar(p) for p in quadros]
        n = len(self.chaves)
        tempos = list(tempos) if tempos else [1.0] * n
        while len(tempos) < n:
            tempos.append(tempos[-1] if tempos else 1.0)
        self.tempos = tempos[:n]
        self.trilhas = {}
        for k in ANGULOS:
            self.trilhas[k] = Trilha(self.tempos, [c[k] for c in self.chaves], angular=True)
        for k in LINEARES:
            self.trilhas[k] = Trilha(self.tempos, [c[k] for c in self.chaves])
        for k in LISTAS:
            self.trilhas[k] = Trilha(self.tempos, [c[k] for c in self.chaves], angular=True)
        base = self.trilhas["t"]
        self.T = base.T
        self.t0 = base.t0

    def segmento(self, tau):
        return self.trilhas["t"].segmento(tau)

    def __call__(self, tau):
        out = {}
        for k, tr in self.trilhas.items():
            v = tr(tau)
            out[k] = [float(x) for x in v] if k in LISTAS else float(v[0])
        i, u = self.segmento(tau)
        a, b = self.chaves[i], self.chaves[(i + 1) % len(self.chaves)]
        out["y"] = None if (a["y"] is None or b["y"] is None) else a["y"] + (b["y"] - a["y"]) * suave(u)
        return out

    def instantes(self, fps):
        """Instantes dos quadros do vídeo (laço: o último não repete o primeiro)."""
        n = max(2, int(round(self.T * fps)))
        return [j * self.T / n for j in range(n)]


def quat_alinhar(qs):
    """Garante continuidade de sinal entre quaternions consecutivos (w, x, y, z)."""
    out = [np.array(qs[0], float)]
    for q in qs[1:]:
        q = np.array(q, float)
        if np.dot(q, out[-1]) < 0:
            q = -q
        out.append(q)
    return out


class TrilhaRigida:
    """Posição (3) + rotação (quaternion) do corpo inteiro ao longo do laço."""

    def __init__(self, tempos, posicoes, quats):
        qs = quat_alinhar(quats)
        self.p = Trilha(tempos, posicoes)
        self.q = Trilha(tempos, qs)

    def __call__(self, tau):
        q = self.q(tau)
        q = q / max(np.linalg.norm(q), 1e-9)
        return self.p(tau), q
