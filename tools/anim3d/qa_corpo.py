"""Verificações de corpo do QA 3D (usadas por qa.py): pegada, amplitude articular (ROM) e apoio.

Tudo é medido no esqueleto e na pele (proxy) já posados pelo motor, e nos aparelhos montados por aparelhos.py (os mesmos
objetos do render, reposicionados em cada quadro por kit.atualizar). Unidades do mundo: 1 = 1 dm.

PEGADA (mão x implemento segurado)
  dist      centro da pegada (h.pegada) longe do eixo da empunhadura: > 2 cm erro, > 1,2 cm aviso
            (barra olímpica, halter, alça do kettlebell, puxador/corda do cabo, ponta do elástico, pegador da máquina,
             barra fixa/paralelas, manopla do guidão, bola medicinal = palma na superfície)
  atravessa pele da mão dentro da empunhadura: > 1,2 cm erro
  cruzada   empunhadura rígida fora do eixo da mão fechada (linha dos nós dos dedos): > 40° erro, > 28° aviso
  dedos     mão que segura com os dedos abertos (fechamento < 70 %)
  cabo      cabo/elástico saindo da mão para dentro do antebraço (ângulo < 20°)
ROM (ângulos reais do esqueleto x limites AAOS / Norkin & White; erro = além do limite + margem, aviso = perto)
  joelho: flexão 0-135 (aviso > 150, erro > 160), hiperextensão (aviso > 8, erro > 15), valgo/varo da malha (aviso > 15, erro > 25)
  cotovelo: flexão 0-150 (aviso > 150, erro > 160), hiperextensão aparente na malha (aviso > 10, erro > 18)
  ombro: extensão 60 / abdução horizontal 45 (limite cai com a elevação), adução horizontal 45 além da linha média,
         rotação externa 90 / interna 70 (medida pelo antebraço com o cotovelo dobrado)
  antebraço: pronação/supinação 80; punho: flexão 80, extensão 70, desvio radial 20, ulnar 30
  quadril: flexão 120, extensão 30, abdução 45, adução 30, rotação interna 45 / externa 45 (pelo plano da canela)
  coluna toracolombar: flexão 80, extensão 25, inclinação 35, rotação 45; dobra num segmento só > 25°/35°
  pescoço: flexão 45, extensão 45, inclinação 45, rotação 60-80
APOIO
  base      centro de massa (Dempster/Winter) / ponto de momento zero fora do polígono de apoio > 3 cm por >= 0,15 s,
            sem mão presa a algo fixo nem encosto lateral
  flutua    nenhum contato (fora das fases de voo balístico)
  pousada   pelve/costas/cabeça/coxa/joelho/antebraço parado de 3 a 15 cm acima de uma superfície (parece apoiado)
  penetra   pele dentro de aparelho > 1,5 cm (banco, encosto, máquina, barra, anilhas, kettlebell...)
  corpo     braço dentro do tronco, mão dentro da cabeça, coxa dentro da outra coxa: > 4 cm
"""
import math

import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

X = Vector((1, 0, 0))
Y = Vector((0, 1, 0))
Z = Vector((0, 0, 1))
FRENTE = Vector((0, -1, 0))
G = 98.1  # dm/s²

# ------------------------------------------------------------------ limites (graus): (aviso, erro)
LIM = {
    "joelho_flexao": (150, 160), "joelho_hiperext": (8, 15), "joelho_valgo": (15, 25),
    "cotovelo_flexao": (150, 160), "cotovelo_hiperext": (10, 18),
    "ombro_ext_excesso": (5, 15), "ombro_aducao_h": (50, 62), "ombro_re": (95, 110), "ombro_ri": (80, 100),
    "antebraco_sup": (90, 110), "antebraco_pro": (90, 110),
    "punho_flexao": (85, 100), "punho_extensao": (85, 100), "punho_radial": (25, 40), "punho_ulnar": (35, 50),
    "quadril_flexao": (125, 140), "quadril_extensao": (30, 42), "quadril_abducao": (52, 65), "quadril_aducao": (30, 40),
    "quadril_re": (55, 75), "quadril_ri": (45, 60),
    "coluna_flexao": (85, 100), "coluna_extensao": (35, 50), "coluna_inclinacao": (40, 52), "coluna_rotacao": (50, 65),
    "coluna_segmento": (25, 35),
    "pescoco_flexao": (55, 70), "pescoco_extensao": (60, 75), "pescoco_inclinacao": (50, 60), "pescoco_rotacao": (80, 92),
}
NOMES_ROM = {
    "joelho_flexao": "flexão do joelho", "joelho_hiperext": "hiperextensão do joelho", "joelho_valgo": "joelho dobrando de lado",
    "cotovelo_flexao": "flexão do cotovelo", "cotovelo_hiperext": "cotovelo dobrando ao contrário",
    "ombro_ext_excesso": "ombro: braço para trás além do limite", "ombro_aducao_h": "ombro: braço cruzando a linha média",
    "ombro_re": "ombro: rotação externa", "ombro_ri": "ombro: rotação interna",
    "antebraco_sup": "supinação do antebraço", "antebraco_pro": "pronação do antebraço",
    "punho_flexao": "flexão do punho", "punho_extensao": "extensão do punho", "punho_radial": "desvio radial do punho",
    "punho_ulnar": "desvio ulnar do punho",
    "quadril_flexao": "flexão do quadril", "quadril_extensao": "extensão do quadril", "quadril_abducao": "abdução do quadril",
    "quadril_aducao": "adução do quadril", "quadril_re": "rotação externa do quadril", "quadril_ri": "rotação interna do quadril",
    "coluna_flexao": "flexão da coluna", "coluna_extensao": "extensão da coluna", "coluna_inclinacao": "inclinação lateral da coluna",
    "coluna_rotacao": "rotação da coluna", "coluna_segmento": "coluna dobrada num segmento só",
    "pescoco_flexao": "flexão do pescoço", "pescoco_extensao": "extensão do pescoço", "pescoco_inclinacao": "inclinação do pescoço",
    "pescoco_rotacao": "rotação do pescoço",
}
LADO = {".L": "esq", ".R": "dir"}
COLUNA = ("root", "spine05", "spine04", "spine03", "spine02", "spine01")
PESCOCO = ("spine01", "neck01", "neck02", "neck03", "head")

# massas segmentares (Dempster, tabela de Winter) e posição do centro de massa no segmento
MASSAS = {"cabeca": 0.081, "torax": 0.216, "abdomen": 0.139, "pelve": 0.142, "braco": 0.028, "antebraco": 0.016, "mao": 0.006,
          "coxa": 0.100, "perna": 0.0465, "pe": 0.0145}

# regiões que costumam ficar "pousadas" numa superfície (checagem de região parada no ar)
REGIOES_POUSO = ("pelve", "costas", "cabeca", "coxa_f", "coxa_t", "joelho_f", "joelho_t", "antebraco_f", "antebraco_t")


def _deg(x):
    return math.degrees(x)


def _ang(a, b):
    return _deg(math.acos(max(-1.0, min(1.0, a.normalized().dot(b.normalized())))))


def _perp(v, eixo):
    w = v - eixo * v.dot(eixo)
    return w.normalized() if w.length > 1e-9 else w


def _assinado(a, b, eixo):
    """Ângulo (graus) de a para b em torno de eixo (a, b perpendiculares ao eixo)."""
    return _deg(math.atan2(a.cross(b).dot(eixo), a.dot(b)))


def _swing(de, para):
    return de.rotation_difference(para)


# ------------------------------------------------------------------ dados estáticos do corpo

class Corpo:
    def __init__(self, h):
        self.h = h
        R = lambda n: h.rest[n].to_3x3()  # noqa: E731
        J = lambda n: h.rest[n].translation  # noqa: E731
        # direção de dobra do cotovelo em repouso (o modelo do MakeHuman tem o cotovelo um pouco dobrado)
        self.dobra_cot = {}
        for sf in (".L", ".R"):
            u = (J("lowerarm01" + sf) - J("upperarm01" + sf)).normalized()
            a = (J("wrist" + sf) - J("lowerarm01" + sf)).normalized()
            self.dobra_cot[sf] = _perp(a, u)
        _ = R
        # rótulo de segmento de cada ponto da pele (osso de maior peso)
        nomes = h.px_nomes
        dom = [nomes[i] for i in h.px_ossos[:, 0]]

        def seg(b):
            s = "." in b and b[-2:] in (".L", ".R")
            lado = ("f" if b.endswith(".L") else "t") if s else ""
            if b.startswith(("finger", "metacarpal", "wrist")):
                return "mao_" + lado
            if b.startswith("lowerarm"):
                return "antebraco_" + lado
            if b.startswith(("upperarm", "shoulder")):
                return "braco_" + lado
            if b.startswith("upperleg"):
                return "coxa_" + lado
            if b.startswith("lowerleg"):
                return "perna_" + lado
            if b.startswith(("foot", "toe")):
                return "pe_" + lado
            if b.startswith(("root", "pelvis")):
                return "pelve"
            if b.startswith(("spine05", "spine04", "spine03")):
                return "abdomen"
            if b.startswith(("spine02", "spine01", "breast", "clavicle")):
                return "torax"
            if b.startswith(("neck",)):
                return "pescoco"
            return "cabeca"
        self.seg = np.array([seg(b) for b in dom])
        self.mask = {s: self.seg == s for s in set(self.seg.tolist())}
        # costas: tronco (tórax + abdômen) do lado de trás da coluna, em repouso
        rest = h.px_rest[:, :3]
        tronco = self.mask.get("torax", 0) | self.mask.get("abdomen", 0)
        self.mask["costas"] = tronco & (rest[:, 1] > 0.15)
        self.mask["tronco"] = tronco | self.mask.get("pelve", 0)
        for lado, sf in (("f", ".L"), ("t", ".R")):
            jo = np.array(J("lowerleg01" + sf))
            self.mask["joelho_" + lado] = np.linalg.norm(rest - jo, axis=1) < 0.8
        self.mask["bracos"] = np.zeros(len(self.seg), bool)
        for k in ("braco_f", "braco_t", "antebraco_f", "antebraco_t", "mao_f", "mao_t"):
            self.mask["bracos"] |= self.mask.get(k, False)
        # normais da pele em repouso (para dizer se um ponto está dentro do corpo)
        self.n_rest = np.asarray(h.normais)[h.px_idx]
        # subamostra (mãos e pés estão super-amostrados no proxy)
        n = len(self.seg)
        sub = np.zeros(n, bool)
        denso = self.mask.get("mao_f", 0) | self.mask.get("mao_t", 0) | self.mask.get("pe_f", 0) | self.mask.get("pe_t", 0)
        sub[::2] = True
        sub &= ~denso | (np.arange(n) % 6 == 0)
        self.sub = sub
        # valores em repouso (o "zero anatômico" é a posição em pé do modelo)
        h.zerar()
        self.rest_ang = {}
        a0 = self.angulos()
        for k in ("quadril_flexao.L", "quadril_flexao.R", "quadril_abducao.L", "quadril_abducao.R", "joelho_flexao.L", "joelho_flexao.R"):
            self.rest_ang[k] = a0.get(k, 0.0)

    # -------------------------------------------------------------- pele com normais
    def pele(self, T):
        h = self.h
        h._fk()
        S = np.array([np.array(h.P[b] @ h.rest_inv[b]) for b in h.px_nomes])
        S = np.einsum("ij,bjk->bik", np.array(T), S)
        M = S[h.px_ossos]
        v = np.einsum("pkij,pj->pki", M[:, :, :3, :], h.px_rest)
        P = (v * h.px_w[:, :, None]).sum(axis=1)
        nr = np.einsum("pkij,pj->pki", M[:, :, :3, :3], self.n_rest)
        N = (nr * h.px_w[:, :, None]).sum(axis=1)
        N /= np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-9)
        return P, N

    # -------------------------------------------------------------- ângulos articulares (espaço do esqueleto)
    def angulos(self):
        h = self.h
        Rr = lambda n: h.rot(n) @ h.rest_inv[n].to_3x3()  # noqa: E731
        C = h.cabeca
        out = {}
        Rp, Rt = Rr("root"), Rr("spine01")
        lat_p, up_p, fw_p = Rp @ X, Rp @ Z, Rp @ FRENTE
        lat_t, up_t, fw_t = Rt @ X, Rt @ Z, Rt @ FRENTE
        for sf, s in ((".L", 1), (".R", -1)):
            # ---- quadril e joelho
            q, j, a = C("upperleg01" + sf), C("lowerleg01" + sf), C("foot" + sf)
            t, sh = j - q, a - j
            tn = t.normalized()
            fl = _deg(math.atan2(t.dot(fw_p), -t.dot(up_p)))
            ab = _deg(math.asin(max(-1, min(1, tn.dot(lat_p) * s))))
            out["quadril_flexao" + sf] = fl - self.rest_ang.get("quadril_flexao" + sf, 0.0)
            out["quadril_abducao" + sf] = ab - self.rest_ang.get("quadril_abducao" + sf, 0.0)
            kf = _ang(t, sh)
            out["joelho_flexao" + sf] = kf - self.rest_ang.get("joelho_flexao" + sf, 0.0)
            ant = _perp(Rr("upperleg02" + sf) @ FRENTE, tn)
            sv = sh.normalized()
            out["joelho_sinal" + sf] = _deg(math.atan2(-sv.dot(ant), sv.dot(tn)))
            out["joelho_lat" + sf] = abs(_deg(math.asin(max(-1, min(1, sv.dot(tn.cross(ant)))))))
            if kf > 25:
                b = _perp(sv, tn)
                n0 = _perp(_swing(-up_p, tn) @ (-fw_p), tn)
                out["quadril_rot" + sf] = -_assinado(n0, b, tn) * s  # + = rotação externa
            # ---- ombro, cotovelo, antebraço, punho
            o, c, w = C("upperarm01" + sf), C("lowerarm01" + sf), C("wrist" + sf)
            u, fa = c - o, w - c
            un, an = u.normalized(), fa.normalized()
            elev = _ang(u, -up_t)
            out["ombro_elev" + sf] = elev
            tras = _deg(math.asin(max(0.0, min(1.0, -un.dot(fw_t)))))
            out["ombro_tras" + sf] = tras
            out["ombro_ext_excesso" + sf] = tras - _lim_tras(elev)
            out["ombro_aducao_h" + sf] = _deg(math.asin(max(0.0, min(1.0, -un.dot(lat_t) * s))))
            ef = _ang(u, fa)
            out["cotovelo_flexao" + sf] = ef
            antc = _perp(Rr("upperarm02" + sf) @ self.dobra_cot[sf], un)
            out["cotovelo_sinal" + sf] = _deg(math.atan2(an.dot(antc), an.dot(un)))
            if ef > 30 and elev < 140:
                b = _perp(an, un)
                n0 = _perp(_swing(-up_t, un) @ fw_t, un)
                out["ombro_rot" + sf] = -_assinado(n0, b, un) * s  # + = rotação externa
            Rw = Rr("wrist" + sf)
            F = h.ref_mao[sf]
            dmao, pol, pal = Rw @ F.col[0], Rw @ F.col[1], Rw @ F.col[2]
            out["punho_flex" + sf] = _deg(math.asin(max(-1, min(1, -an.dot(pal)))))  # + flexão, - extensão
            out["punho_desv" + sf] = _deg(math.asin(max(-1, min(1, -an.dot(pol)))))  # + radial, - ulnar
            if ef > 30:
                hinge = un.cross(an).normalized()
                ref = _perp(hinge * s, an)
                pp = _perp(pal, an)
                if pp.length > 0.5:
                    out["antebraco_sup" + sf] = -_assinado(ref, pp, an) * s  # + supinação, - pronação
        # ---- coluna e pescoço (rotações relativas entre segmentos, no referencial do segmento de baixo)
        def dec(Ra, Rb):
            Rl = Ra.transposed() @ Rb
            zz = Rl @ Z
            fl = _deg(math.atan2(-zz.y, zz.z))
            la = _deg(math.asin(max(-1, min(1, zz.x))))
            qq = Rl.to_quaternion()
            tw = _deg(2 * math.atan2(qq.z, qq.w))
            tw = (tw + 180) % 360 - 180
            return fl, la, tw
        Rs = [Rr(n) for n in COLUNA]
        fl, la, tw = dec(Rs[0], Rs[-1])
        out["coluna_fl"], out["coluna_la"], out["coluna_tw"] = fl, la, tw
        seg = 0.0
        for a_, b_ in zip(Rs[:-1], Rs[1:]):
            f_, l_, t_ = dec(a_, b_)
            seg = max(seg, abs(f_), abs(l_), abs(t_))
        out["coluna_segmento"] = seg
        fl, la, tw = dec(Rr(PESCOCO[0]), Rr(PESCOCO[-1]))
        out["pescoco_fl"], out["pescoco_la"], out["pescoco_tw"] = fl, la, tw
        return out

    # -------------------------------------------------------------- centro de massa (mundo)
    def centro_massa(self, T):
        h = self.h
        C = lambda n: T @ h.cabeca(n)  # noqa: E731
        Ct = lambda n: T @ h.cauda(n)  # noqa: E731
        pts = []
        hd = C("head")
        pts.append((MASSAS["cabeca"], hd + (Ct("head") - hd) * 0.35))
        quad = (C("upperleg01.L") + C("upperleg01.R")) / 2
        pts.append((MASSAS["pelve"], quad.lerp(C("spine05"), 0.35)))
        pts.append((MASSAS["abdomen"], C("spine04").lerp(C("spine03"), 0.5)))
        pts.append((MASSAS["torax"], C("spine02").lerp(Ct("spine02"), 0.6)))
        for sf in (".L", ".R"):
            o, c, w = C("upperarm01" + sf), C("lowerarm01" + sf), C("wrist" + sf)
            pts.append((MASSAS["braco"], o.lerp(c, 0.436)))
            pts.append((MASSAS["antebraco"], c.lerp(w, 0.43)))
            pts.append((MASSAS["mao"], T @ h.pegada(sf)))
            q, j, a = C("upperleg01" + sf), C("lowerleg01" + sf), C("foot" + sf)
            pts.append((MASSAS["coxa"], q.lerp(j, 0.433)))
            pts.append((MASSAS["perna"], j.lerp(a, 0.433)))
            pts.append((MASSAS["pe"], a.lerp(C("toe3-1" + sf), 0.5)))
        m = sum(p[0] for p in pts)
        return sum((p[1] * p[0] for p in pts), Vector()) / m

    def fechamento(self, sf):
        """0 = dedos relaxados, 1 = mão fechada de pegada (pelas rotações reais das falanges)."""
        h = self.h
        tot, n = 0.0, 0
        for f in range(2, 6):
            for j in range(1, 4):
                nm = f"finger{f}-{j}{sf}"
                if nm in h.basis:
                    q = h.basis[nm].to_quaternion()
                    tot += _deg(2 * math.acos(min(1.0, abs(q.w))))
                    n += 1
        s = tot / max(n, 1) * 3  # soma por dedo
        return (s - 50.0) / (192.0 - 50.0)


def _lim_tras(elev):
    """Quanto o braço pode ir para trás do plano frontal do tronco (graus), em função da elevação."""
    pts = ((0, 65), (65, 65), (90, 45), (140, 25), (180, 0))
    for (e0, l0), (e1, l1) in zip(pts[:-1], pts[1:]):
        if elev <= e1:
            return l0 + (l1 - l0) * (elev - e0) / (e1 - e0)
    return 0.0


def avaliar_rom(ang, lado_sf):
    """Converte os ângulos de um quadro em medidas comparáveis aos limites: {chave: (valor, parte)}."""
    m = {}
    for sf in (".L", ".R"):
        ld = LADO[sf]
        g = lambda k: ang.get(k + sf)  # noqa: E731
        m[("joelho_flexao", "joelho " + ld)] = g("joelho_flexao")
        sn = g("joelho_sinal")
        if sn is not None and g("joelho_flexao") is not None:
            m[("joelho_hiperext", "joelho " + ld)] = max(0.0, -sn) if abs(sn) < 90 else 0.0
            if g("joelho_flexao") > 20:
                m[("joelho_valgo", "joelho " + ld)] = g("joelho_lat")
        m[("cotovelo_flexao", "cotovelo " + ld)] = g("cotovelo_flexao")
        cs = g("cotovelo_sinal")
        if cs is not None:
            m[("cotovelo_hiperext", "cotovelo " + ld)] = max(0.0, -cs) if abs(cs) < 90 else 0.0
        m[("ombro_ext_excesso", "ombro " + ld)] = g("ombro_ext_excesso")
        m[("ombro_aducao_h", "ombro " + ld)] = g("ombro_aducao_h")
        r = g("ombro_rot")
        if r is not None:
            m[("ombro_re", "ombro " + ld)] = max(0.0, r)
            m[("ombro_ri", "ombro " + ld)] = max(0.0, -r)
        r = g("antebraco_sup")
        if r is not None:
            m[("antebraco_sup", "antebraço " + ld)] = max(0.0, r)
            m[("antebraco_pro", "antebraço " + ld)] = max(0.0, -r)
        r = g("punho_flex")
        m[("punho_flexao", "punho " + ld)] = max(0.0, r)
        m[("punho_extensao", "punho " + ld)] = max(0.0, -r)
        r = g("punho_desv")
        m[("punho_radial", "punho " + ld)] = max(0.0, r)
        m[("punho_ulnar", "punho " + ld)] = max(0.0, -r)
        r = g("quadril_flexao")
        m[("quadril_flexao", "quadril " + ld)] = max(0.0, r)
        m[("quadril_extensao", "quadril " + ld)] = max(0.0, -r)
        r = g("quadril_abducao")
        m[("quadril_abducao", "quadril " + ld)] = max(0.0, r)
        m[("quadril_aducao", "quadril " + ld)] = max(0.0, -r)
        r = g("quadril_rot")
        if r is not None:
            m[("quadril_re", "quadril " + ld)] = max(0.0, r)
            m[("quadril_ri", "quadril " + ld)] = max(0.0, -r)
    m[("coluna_flexao", "coluna")] = max(0.0, ang["coluna_fl"])
    m[("coluna_extensao", "coluna")] = max(0.0, -ang["coluna_fl"])
    m[("coluna_inclinacao", "coluna")] = abs(ang["coluna_la"])
    m[("coluna_rotacao", "coluna")] = abs(ang["coluna_tw"])
    m[("coluna_segmento", "coluna")] = ang["coluna_segmento"]
    m[("pescoco_flexao", "pescoço")] = max(0.0, ang["pescoco_fl"])
    m[("pescoco_extensao", "pescoço")] = max(0.0, -ang["pescoco_fl"])
    m[("pescoco_inclinacao", "pescoço")] = abs(ang["pescoco_la"])
    m[("pescoco_rotacao", "pescoço")] = abs(ang["pescoco_tw"])
    return {k: v for k, v in m.items() if v is not None}


# ------------------------------------------------------------------ pegada: túnel formado pelos dedos fechados

def _circulo(p2):
    A = np.c_[2 * p2, np.ones(len(p2))]
    b = (p2 ** 2).sum(1)
    s = np.linalg.lstsq(A, b, rcond=None)[0]
    c = s[:2]
    return c, float(np.sqrt(max(s[2] + c @ c, 0.0)))


def tunel(h, T, sf):
    """Centro (mundo), eixo e raio do túnel que os dedos 2-5 formam ao fechar (círculo pelas articulações de cada dedo,
    no plano perpendicular à linha dos nós dos dedos). É onde a empunhadura precisa passar para a mão segurá-la."""
    kl = (T @ h.cabeca("finger2-1" + sf) - T @ h.cabeca("finger5-1" + sf)).normalized()
    cs, rs = [], []
    for f in range(2, 6):
        P = [T @ h.cabeca(f"finger{f}-{j}{sf}") for j in (1, 2, 3)] + [T @ h.cauda(f"finger{f}-3{sf}")]
        o = P[0]
        u = (P[2] - o)
        u = (u - kl * u.dot(kl)).normalized()
        v = kl.cross(u)
        p2 = np.array([[(p - o).dot(u), (p - o).dot(v)] for p in P])
        c, r = _circulo(p2)
        cs.append(o + u * float(c[0]) + v * float(c[1]))
        rs.append(r)
    c = sum(cs, Vector()) / len(cs)
    return c, kl, float(np.mean(rs))


# ------------------------------------------------------------------ aparelhos montados (mesmos objetos do render)

def _seg_dist(p, a, b):
    """Distância do ponto p ao segmento ab e o parâmetro t (0..1)."""
    ab = b - a
    L2 = ab.dot(ab)
    t = 0.0 if L2 < 1e-12 else max(0.0, min(1.0, (p - a).dot(ab) / L2))
    return (p - (a + ab * t)).length, t


class Peca:
    def __init__(self, o):
        self.o = o
        me = o.data
        V = np.array([tuple(v.co) for v in me.vertices]) if len(me.vertices) else np.zeros((0, 3))
        self.V = V
        self.bvh = BVHTree.FromPolygons([tuple(v) for v in V], [tuple(p.vertices) for p in me.polygons]) if len(me.polygons) else None
        self.mat = me.materials[0].name if len(me.materials) and me.materials[0] else ""
        self.foco = bool(o.get("foco"))
        lo, hi = V.min(axis=0), V.max(axis=0)
        self.lo, self.hi = lo, hi
        span = hi - lo
        # cilindro do Kit (eixo local z): seção circular, número par de vértices
        self.cil = (len(V) >= 12 and len(V) % 2 == 0 and abs(span[0] - span[1]) < 2e-3 and not self.foco)
        self.r = float(span[0] / 2) if self.cil else 0.0
        self.movel = False
        self.tipo = "fixo"
        self.M = o.matrix_world.copy()
        self.Mi = self.M.inverted()

    def ler(self):
        self.M = self.o.matrix_world.copy()
        self.Mi = self.M.inverted_safe()
        self.visivel = not self.o.hide_render

    def eixo(self):
        """Segmento do eixo (mundo) de um cilindro."""
        a = self.M @ Vector((0, 0, float(self.lo[2])))
        b = self.M @ Vector((0, 0, float(self.hi[2])))
        return a, b

    def caixa_mundo(self):
        cs = np.array([tuple(self.M @ Vector(c)) for c in self.o.bound_box])
        return cs.min(axis=0), cs.max(axis=0)

    def mais_perto(self, p):
        """(distância no mundo, dentro?, normal no mundo) do ponto p (mundo) à superfície da peça."""
        pl = self.Mi @ Vector(p)
        loc, nrm, _, _ = self.bvh.find_nearest(pl)
        if loc is None:
            return 1e9, False, Z
        dentro = (pl - loc).dot(nrm) < 0
        lw = self.M @ loc
        nw = (self.Mi.to_3x3().transposed() @ nrm).normalized()
        return (Vector(p) - lw).length, dentro, nw

    def abaixo(self, p, zmax):
        """Altura (mundo) da superfície da peça logo abaixo de p (raio vertical), ou None."""
        o = self.Mi @ Vector(p)
        d = (self.Mi.to_3x3() @ Vector((0, 0, -1)))
        loc, nrm, _, dist = self.bvh.ray_cast(o, d.normalized())
        if loc is None:
            return None
        z = (self.M @ loc).z
        return z if z <= zmax else None


class Aparelhos:
    def __init__(self, kit, ctx, estados):
        self.ctx = ctx
        self.pecas = [Peca(o) for o in kit.objs if o.type == "MESH"]
        # móveis: matriz muda ao longo do ciclo
        amostra = [estados[0], estados[len(estados) // 3], estados[(2 * len(estados)) // 3]]
        ms = []
        for est in amostra:
            kit.atualizar(est)
            ms.append([p.o.matrix_world.copy() for p in self.pecas])
        bat = "battle" in ctx.id
        for i, p in enumerate(self.pecas):
            p.movel = any(not _mat_igual(ms[0][i], m[i]) for m in ms[1:])
            if p.foco:
                p.tipo = "segurado"
                sp = p.hi - p.lo
                if sp[0] > 8:
                    p.forma, p.pega = "barra", (6.5 if sp[0] > 14 else 4.2, 0.14)
                elif p.lo[2] < -1.5:
                    p.forma, p.pega = "kettlebell", (0.3, 0.12)
                elif sp[0] > 2.0 and sp[0] < 2.6:
                    p.forma, p.pega = "halter", (0.62, 0.15)
                else:
                    p.forma, p.pega = "bola", (0.0, float(sp.max() / 2))
            elif p.cil and p.movel and (p.mat in ("brasa", "cabo") or (p.mat == "preto" and p.r <= 0.115) or (bat and p.mat == "preto")):
                p.tipo = "fio"
            elif p.cil and p.movel and p.mat in ("preto", "metal") and 0.125 <= p.r <= 0.23:
                p.tipo = "pega"
            elif p.cil and not p.movel and p.r <= 0.25 and p.mat in ("metal", "preto", "madeira"):
                p.tipo = "tubo"  # barra fixa, paralelas, manopla do guidão, espaldar, corrimão
            else:
                p.tipo = "movel" if p.movel else "fixo"
        self.superficies = [p for p in self.pecas if p.tipo in ("fixo", "movel", "tubo") and p.bvh is not None]
        self.solidos = [p for p in self.pecas if p.tipo in ("fixo", "movel", "tubo", "segurado", "pega") and p.bvh is not None]

    def ler(self):
        for p in self.pecas:
            p.ler()
        for p in self.pecas:
            p.cx = p.caixa_mundo() if p.visivel else None

    def pegas(self):
        """Empunhaduras visíveis no quadro: (peça, a, b, raio, rígida)."""
        out = []
        for p in self.pecas:
            if not p.visivel:
                continue
            if p.tipo == "segurado":
                if p.forma == "bola":
                    continue
                if p.forma == "kettlebell":
                    c = p.M @ Vector((0, 0, 0.45))
                    e = (p.M.to_3x3() @ Y).normalized()
                    hl, r = p.pega
                    out.append((p, c - e * hl, c + e * hl, r, True))
                else:
                    hl, r = p.pega
                    out.append((p, p.M @ Vector((-hl, 0, 0)), p.M @ Vector((hl, 0, 0)), r, True))
            elif p.tipo in ("pega", "tubo", "fio"):
                a, b = p.eixo()
                out.append((p, a, b, p.r, p.tipo != "fio"))
        return out


def _mat_igual(a, b, tol=1e-4):
    return all(abs(a[i][j] - b[i][j]) < tol for i in range(4) for j in range(4))


def _casco(P):
    """Fecho convexo 2D (Andrew)."""
    P = sorted(set(map(tuple, np.round(P, 3))))
    if len(P) <= 2:
        return np.array(P)

    def cr(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in P:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(P):
        while len(up) >= 2 and cr(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return np.array(lo[:-1] + up[:-1])


def _dist_poligono(c, H):
    """Distância do ponto 2D c ao polígono convexo H (negativa = dentro)."""
    if len(H) == 0:
        return 1e9
    if len(H) == 1:
        return float(np.linalg.norm(c - H[0]))
    best = 1e9
    dentro = len(H) >= 3
    for i in range(len(H)):
        a, b = H[i], H[(i + 1) % len(H)]
        ab = b - a
        t = max(0.0, min(1.0, float(np.dot(c - a, ab) / max(np.dot(ab, ab), 1e-12))))
        best = min(best, float(np.linalg.norm(c - (a + ab * t))))
        if (ab[0] * (c[1] - a[1]) - ab[1] * (c[0] - a[0])) < 0:
            dentro = False
    return -best if dentro else best


def _kd(P, idx):
    kd = KDTree(len(idx))
    for i in idx:
        kd.insert(P[i], int(i))
    kd.balance()
    return kd
