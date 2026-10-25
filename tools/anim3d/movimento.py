"""Interpolação natural das poses-chave (spline cúbica de Hermite em laço fechado) + curvas de velocidade autorais.

Cada canal (ângulo, posição, quaternion) vira uma "trilha" que PASSA pelos quadros-chave nos instantes dados por
"tempos". As tangentes são de Catmull-Rom não uniforme (média ponderada das inclinações vizinhas), amortecidas e
limitadas (Fritsch-Carlson) para não ultrapassar a pose. Tangente zero só nas inversões REAIS (ida e volta); na
chegada de uma pausa o corpo "assenta" com 15 % da velocidade (sem parada morta). Ângulos não são desenrolados (sem saltos
de 360°: os valores escritos são seguidos como na prévia 2D, então um braço de -45 a 150 passa pela frente) e o laço
fecha sem emenda.

Easing por trecho ("ease" na animação, mesmo comprimento de "tempos"): o tempo dentro do trecho é remapeado por uma
cúbica monotônica E(u) com E'(0)=a e E'(1)=b, e as tangentes são divididas por a/b: a velocidade continua contínua nas
chaves, mas o perfil fica assimétrico (concêntrica acelera rápido e freia longo, excêntrica controlada).
  "con" (1.7, 0.45) · "exc" (1.15, 0.55) · "io"/"pausa"/"bal" (1, 1) · "lin" (1, 1) com Catmull-Rom puro (cardio).
Sem "ease": trecho >= 1.3 s = exc, 0.5-1.3 s = con, curto = io; cardio (todos os trechos <= 0.26 s) = lin.

Camadas extras (TrilhasPose): atraso por canal (overlap: a cabeça chega depois do tronco), "vida" (respiração, peso,
olhar e tremor em senoides harmônicas do período, para o laço fechar) e direção dos braços por arco de círculo máximo
(slerp com o mesmo ritmo dos ângulos: elevação lateral sobe num plano, sem "ir para a frente e depois abrir").
"""
import math

import numpy as np

AMORTECIMENTO = 0.9  # 1 = Catmull-Rom puro; menor = mais "assentado" em cada pose
ASSENTAR = 0.15  # fração da velocidade de chegada mantida ao entrar numa pausa
DESENROLAR = False  # ângulos seguem os valores escritos (como na prévia 2D); giros de 180°+ são intencionais
G = 98.1  # gravidade em unidades do esqueleto 3D por s² (1 unidade = 1 dm)

EASES = {"con": (1.7, 0.45), "exc": (1.15, 0.55), "io": (1.0, 1.0), "pausa": (1.0, 1.0), "bal": (1.0, 1.0), "lin": (1.0, 1.0)}


def _wrap(d):
    return (d + 180.0) % 360.0 - 180.0


def _e(u, a, b):
    """Cúbica monotônica 0->1 com inclinações a (início) e b (fim)."""
    u2, u3 = u * u, u * u * u
    return (u3 - 2 * u2 + u) * a + (-2 * u3 + 3 * u2) + (u3 - u2) * b


class Trilha:
    """Spline cúbica periódica de um vetor de valores (n chaves x m componentes)."""

    def __init__(self, tempos, valores, angular=False, eases=None, catmull=False):
        v = np.array(valores, dtype=float)
        if v.ndim == 1:
            v = v[:, None]
        n = len(v)
        self.n = n
        self.dt = np.array([max(1e-3, float(t)) for t in tempos[:n]] + [1.0] * max(0, n - len(tempos)))
        self.t0 = np.concatenate([[0.0], np.cumsum(self.dt)])  # t0[i] = início do trecho i; t0[n] = período
        self.T = self.t0[-1]
        if angular and DESENROLAR:
            for i in range(1, n):
                v[i] = v[i - 1] + _wrap(v[i] - v[i - 1])
            fim = v[n - 1] + _wrap(v[0] - v[n - 1])
            self.periodo = fim - v[0]  # múltiplo de 360 (0 em movimentos que vão e voltam)
        else:
            self.periodo = np.zeros(v.shape[1])
        self.v = v
        self.amort = 1.0 if catmull else AMORTECIMENTO
        self.eases = [EASES.get(e, (1.0, 1.0)) if isinstance(e, str) else tuple(e) for e in (eases or [])]
        while len(self.eases) < n:
            self.eases.append((1.0, 1.0))
        self.m = self._tangentes()

    def _val(self, i):
        q, r = divmod(i, self.n)
        return self.v[r] + q * self.periodo

    def _tangentes(self):
        n = self.n
        m = np.zeros_like(self.v)
        if n < 2:
            return m
        d = np.array([(self._val(i + 1) - self._val(i)) / self.dt[i] for i in range(n)])  # inclinação do trecho i
        escala = np.maximum(np.abs(d).max(axis=0), 1e-9)
        parado = np.abs(d) < np.maximum(0.03 * escala, 1e-6)  # trecho praticamente parado (pausa) por componente
        for i in range(n):
            ia = (i - 1) % n
            dt0, dt1 = self.dt[ia], self.dt[i]
            d0, d1 = d[ia], d[i]
            mi = (dt1 * d0 + dt0 * d1) / (dt0 + dt1) * self.amort
            lim = 3.0 * np.minimum(np.abs(d0), np.abs(d1))
            mi = np.clip(mi, -lim, lim)
            p0, p1 = parado[ia], parado[i]
            inversao = (d0 * d1 < 0) & ~p0 & ~p1
            mi[inversao] = 0.0
            # chegada numa pausa: assenta com um resto de velocidade; saída de pausa: arranca suave
            so_p1 = p1 & ~p0
            so_p0 = p0 & ~p1
            mi[so_p1] = ASSENTAR * d0[so_p1]
            mi[so_p0] = ASSENTAR * d1[so_p0]
            mi[p0 & p1] = 0.0
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
        a, b = self.eases[i]
        p0, p1 = self._val(i), self._val(i + 1)
        m0, m1 = self.m[i] * self.dt[i] / a, self.m[(i + 1) % self.n] * self.dt[i] / b
        u = _e(u, a, b) if (a, b) != (1.0, 1.0) else u
        u2, u3 = u * u, u * u * u
        h00, h10, h01, h11 = 2 * u3 - 3 * u2 + 1, u3 - 2 * u2 + u, -2 * u3 + 3 * u2, u3 - u2
        return h00 * p0 + h10 * m0 + h01 * p1 + h11 * m1 + voltas * self.periodo


def suave(u, a=0.0, b=1.0):
    t = min(1.0, max(0.0, (u - a) / (b - a))) if b > a else float(u >= a)
    return t * t * (3 - 2 * t)


# ------------------------------------------------------------------ poses

ANGULOS = ("t", "c", "tr", "rol", "inc", "cinc", "cr", "bfa", "bta", "afa", "ata", "pfa", "pta", "cfa", "cta", "cfl", "pel", "trp",
           "puf", "put", "pdf", "pdt", "trt")
LINEARES = ("x", "z", "ay", "oe", "pro")
LISTAS = {"bf": 2, "bt": 2, "pf": 3, "pt": 3}
PADRAO = {"x": 0.0, "z": 0.0, "ay": 0.0, "oe": 0.0, "pro": 0.0, "t": 180.0, "c": 180.0, "tr": 0.0, "rol": 0.0, "inc": 0.0, "cinc": 0.0,
          "cr": 0.0, "cfl": 0.0, "pel": 0.0, "trp": 0.0, "puf": 0.0, "put": 0.0, "pdf": 0.0, "pdt": 0.0, "trt": 0.0,
          "bfa": 0.0, "bta": 0.0, "afa": 0.0, "ata": 0.0, "pfa": 0.0, "pta": 0.0, "cfa": 0.0, "cta": 0.0, "bf": [0.0, 0.0], "bt": [0.0, 0.0], "pf": [0.0, 0.0, 90.0], "pt": [0.0, 0.0, 90.0]}


def normalizar(p):
    """Pose completa (todos os canais numéricos). 'afa'/'ata' ausentes = abdução do braço; 'y' e 'apoio' ficam como estão."""
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
    if p.get("cfa") is None:
        q["cfa"] = q["pfa"]
    if p.get("cta") is None:
        q["cta"] = q["pta"]
    q["y"] = p.get("y")
    q["apoio"] = p.get("apoio")
    # campos discretos por quadro (não interpolados): estado das mãos, mão presa ao corpo, giro da mão apoiada
    for k in DISCRETOS:
        if k in p:
            q[k] = p[k]
    return q


DISCRETOS = ("maos", "segura", "dedos", "solta")


# direção de um segmento (espaço do esqueleto 3D: frente = -y, cima = +z, lado "f" = +x) a partir de ângulo 2D + abdução
def d2np(ang, abd=0.0, lado=1):
    r, b = math.radians(ang), math.radians(abd)
    v0 = np.array((0.0, -math.sin(r), -math.cos(r)))
    return v0 * math.cos(b) + np.array((lado * math.sin(b), 0.0, 0.0))


def slerp_v(a, b, w):
    """Arco de círculo máximo entre os vetores unitários a e b (w pode sair um pouco de 0..1)."""
    c = float(np.clip(np.dot(a, b), -1.0, 1.0))
    om = math.acos(c)
    if om < 1e-4:
        v = a + (b - a) * w
    else:
        s = math.sin(om)
        v = a * (math.sin((1 - w) * om) / s) + b * (math.sin(w * om) / s)
    return v / max(np.linalg.norm(v), 1e-9)


def eases_auto(tempos, eases=None):
    n = len(tempos)
    if eases:
        out = list(eases)[:n]
        while len(out) < n:
            out.append("io")
        return out, all(e == "lin" for e in out)
    cardio = all(float(t) <= 0.26 for t in tempos)
    if cardio:
        return ["lin"] * n, True
    out = []
    for t in tempos:
        t = float(t)
        out.append("exc" if t >= 1.3 else "con" if t >= 0.5 else "io")
    return out, False


class TrilhasPose:
    """Todas as trilhas de uma animação. __call__(tau) devolve a pose interpolada (formato normalizado)."""

    def __init__(self, quadros, tempos, eases=None, atrasos=None):
        self.chaves = [normalizar(p) for p in quadros]
        n = len(self.chaves)
        tempos = list(tempos) if tempos else [1.0] * n
        while len(tempos) < n:
            tempos.append(tempos[-1] if tempos else 1.0)
        self.tempos = tempos[:n]
        self.eases, self.cardio = eases_auto(self.tempos, eases)
        cat = self.cardio
        self.trilhas = {}
        for k in ANGULOS:
            self.trilhas[k] = Trilha(self.tempos, [c[k] for c in self.chaves], angular=True, eases=self.eases, catmull=cat)
        for k in LINEARES:
            self.trilhas[k] = Trilha(self.tempos, [c[k] for c in self.chaves], eases=self.eases, catmull=cat)
        for k in LISTAS:
            self.trilhas[k] = Trilha(self.tempos, [c[k] for c in self.chaves], angular=True, eases=self.eases, catmull=cat)
        base = self.trilhas["t"]
        self.T = base.T
        self.t0 = base.t0
        self.atrasos = dict(atrasos or {})
        self.vida = 0.0  # 0..1 (camada de micro-movimento)
        self.tremor = 0.0
        self.semente = 0
        # direções-chave dos braços (para o arco de círculo máximo); membros com giro > 150° entre chaves ficam angulares
        self.dirs = {}
        for lado, s in (("f", 1), ("t", -1)):
            for seg, idx, ab in (("b", 0, "b" + lado + "a"), ("a", 1, "a" + lado + "a")):
                ds = [d2np(c["b" + lado][idx], c[ab], s) for c in self.chaves]
                ok = all(math.degrees(math.acos(float(np.clip(np.dot(ds[i], ds[(i + 1) % n]), -1, 1)))) <= 150 for i in range(n))
                if ok and n >= 2:
                    self.dirs[(lado, seg)] = ds

    def segmento(self, tau):
        return self.trilhas["t"].segmento(tau)

    def _vida(self, tau, out):
        """Micro-movimento harmônico do período (o laço fecha): respiração, peso, olhar, ombros, tremor."""
        T = self.T
        if self.vida <= 0 and self.tremor <= 0:
            out["_resp"] = 0.0
            out["_dz"] = 0.0
            return
        rng = np.random.default_rng(self.semente)
        fases = rng.random(8) * 2 * math.pi
        nr = max(1, round(T / 3.2))  # ciclos de respiração por laço (~3,2 s cada)
        w = 2 * math.pi / T
        v = max(self.vida, self.peso_pausa(tau))  # nas pausas a vida sobe a 100 % (nunca dois quadros iguais)
        resp = math.sin(w * nr * tau + fases[0])
        out["_resp"] = 1.1 * v * resp  # graus no tórax (spine02/03)
        out["t"] += 0.7 * v * resp
        out["oe"] = out["oe"] + 0.03 * v * (0.5 + 0.5 * math.sin(w * nr * tau + fases[0] - 0.6))
        n2 = max(1, round(T / 2.3))
        n3 = max(1, round(T / 1.7))
        out["c"] += 1.6 * v * math.sin(w * n2 * tau + fases[1])
        out["cr"] += 2.0 * v * math.sin(w * n3 * tau + fases[2])
        out["cinc"] += 0.6 * v * math.sin(w * max(1, round(T / 2.9)) * tau + fases[3])
        out["_dz"] = 0.08 * v * math.sin(w * max(1, round(T / 4.0)) * tau + fases[4])
        for lado, ph in (("f", fases[5]), ("t", fases[6])):
            out["b" + lado][1] += 0.8 * v * math.sin(w * n2 * tau + ph)
        if self.tremor > 0:
            nt = max(1, round(T * 8.0))
            mod = 0.6 + 0.4 * math.sin(w * tau + fases[7])
            out["t"] += 0.3 * self.tremor * mod * math.sin(w * nt * tau)
            out["_resp"] += 0.3 * self.tremor * mod * math.sin(w * (nt + 1) * tau + 1.0)

    def _pausas(self):
        """Trechos praticamente parados (pausas e isometrias): variação de canal < 3° entre as chaves."""
        if hasattr(self, "_pz"):
            return self._pz
        n = len(self.chaves)
        pz = []
        for i in range(n):
            a, b = self.chaves[i], self.chaves[(i + 1) % n]
            d = max(abs(a[k] - b[k]) for k in ANGULOS)
            for k in LISTAS:
                d = max(d, max(abs(x - y) for x, y in zip(a[k], b[k])))
            d = max(d, 10 * max(abs(a[k] - b[k]) for k in ("x", "z", "ay")))
            pz.append(d < 3.0)
        self._pz = pz
        return pz

    def peso_pausa(self, tau):
        """0..1, contínuo: 1 dentro de um trecho de pausa, rampa suave nas bordas (laço periódico)."""
        pz = self._pausas()
        if not any(pz):
            return 0.0
        i, u = self.segmento(tau)
        n = len(pz)
        ant, prox = pz[(i - 1) % n], pz[(i + 1) % n]
        if pz[i]:
            w = 1.0
            if not ant:
                w = min(w, suave(u, 0.0, 0.35))
            if not prox:
                w = min(w, 1.0 - suave(u, 0.65, 1.0))
            return w
        w = 0.0
        if ant:
            w = max(w, 1.0 - suave(u, 0.0, 0.25))
        if prox:
            w = max(w, suave(u, 0.75, 1.0))
        return w * 0.0

    def __call__(self, tau, vida=True):
        out = {}
        for k, tr in self.trilhas.items():
            v = tr(tau - self.atrasos.get(k, 0.0))
            out[k] = [float(x) for x in v] if k in LISTAS else float(v[0])
        i, u = self.segmento(tau)
        n = len(self.chaves)
        a, b = self.chaves[i], self.chaves[(i + 1) % n]
        out["y"] = None if (a["y"] is None or b["y"] is None) else a["y"] + (b["y"] - a["y"]) * suave(u)
        # braços: arco de círculo máximo com o ritmo dos ângulos (mesmo trecho e mesmo progresso dos canais angulares)
        dirs = {}
        for lado in ("f", "t"):
            kk = "b" + lado
            tl = self.trilhas[kk]
            ti, ui = tl.segmento(tau)
            ja = (ti + 1) % n
            par = []
            for seg, idx, ab in (("b", 0, "b" + lado + "a"), ("a", 1, "a" + lado + "a")):
                ds = self.dirs.get((lado, seg))
                if ds is None:
                    par = None
                    break
                tla = self.trilhas[ab]
                va0, va1 = tl._val(ti)[idx], tl._val(ti + 1)[idx]
                vb0, vb1 = tla._val(ti)[0], tla._val(ti + 1)[0]
                da, db = va1 - va0, vb1 - vb0
                voltas = math.floor(tau / self.T)
                cur_a = out[kk][idx] - voltas * tl.periodo[idx]
                cur_b = out[ab] - voltas * tla.periodo[0]
                pesos = [(abs(da), (cur_a - va0) / da)] if abs(da) > 0.5 else []
                if abs(db) > 0.5:
                    pesos.append((abs(db), (cur_b - vb0) / db))
                wgt = sum(p * r for p, r in pesos) / sum(p for p, _ in pesos) if pesos else ui
                par.append(slerp_v(ds[ti], ds[ja], float(np.clip(wgt, -0.2, 1.2))))
            if par:
                dirs[lado] = tuple(par)
        out["_dirs"] = dirs
        if vida:
            self._vida(tau, out)
        else:
            out["_resp"] = 0.0
            out["_dz"] = 0.0
        out["apoio"] = None
        return out

    def instantes(self, fps):
        """Instantes dos quadros do vídeo: passo de tempo uniforme (N = round(T*fps)), o laço não repete o 1º quadro."""
        N = max(2, int(round(self.T * fps)))
        return [j * self.T / N for j in range(N)]


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
    """Posição (3) + rotação (quaternion) do corpo inteiro ao longo do laço. 'voos': [(t_ini, t_fim)] em que o quadril
    segue uma parábola (gravidade constante) e a horizontal tem velocidade constante."""

    def __init__(self, tempos, posicoes, quats, eases=None, catmull=False, voos=None):
        qs = quat_alinhar(quats)
        self.p = Trilha(tempos, posicoes, eases=eases, catmull=catmull)
        self.q = Trilha(tempos, qs, eases=eases, catmull=catmull)
        self.voos = []
        for a, b in (voos or []):
            pa, pb = self.p(a), self.p(b)
            self.voos.append((a, b, pa, pb))

    def __call__(self, tau):
        q = self.q(tau)
        q = q / max(np.linalg.norm(q), 1e-9)
        T = self.p.T
        tm = tau % T
        for a, b, pa, pb in self.voos:
            dur = (b - a) % T or T
            s = (tm - a) % T
            if s <= dur:
                v0 = (pb[2] - pa[2]) / dur + G * dur / 2
                p = pa + (pb - pa) * (s / dur)
                p = p.copy()
                p[2] = pa[2] + v0 * s - G * s * s / 2
                return p, q
        return self.p(tau), q
