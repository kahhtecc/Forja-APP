"""Renderização 3D das demonstrações do Forja (Blender como módulo Python).

Corpo: malha-base do MakeHuman (CC0) com alvos de atleta (homem jovem, musculatura máxima, gordura mínima).
Esqueleto: default.mhskel + pesos default_weights.mhw do MakeHuman.
Poses: as mesmas de tools/anim (ângulos absolutos no plano sagital) + campos 3D opcionais:
  "bfa"/"bta": abdução do braço da frente/trás (0 = no plano sagital, 90 = aberto para o lado)
  "afa"/"ata": abdução do antebraço
  "pfa"/"pta": abdução da perna (coxa)
  "tr": rotação do tronco (torção, graus; + gira o peito para o lado da câmera)
  "oe": elevação dos ombros 0..1 (encolhimento). Se ausente em exercícios do grupo Trapézio, vale 0 no 1º quadro e 1 nos demais.
Elástico entre as mãos: {"tipo": "elastico", "de": "maos", "ate": "maos"} (automático no band-pull-apart sem props).
Uso (python do ambiente com bpy):
  python tools/anim3d/humano.py --mh <pasta makehuman/data> --anim <dados.json> [--ids a,b] --saida <pasta> [--tam 480] [--amostras 24] [--quadros 12]
"""
import argparse
import json
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix, Quaternion, Vector

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "anim"))
from esqueleto import completar, interpolar, pontos_anim  # noqa: E402

sys.path.insert(0, AQUI)
import anatomia  # noqa: E402

FRENTE = Vector((0, -1, 0))
CIMA = Vector((0, 0, 1))
ESQ = Vector((1, 0, 0))  # lado esquerdo do personagem = lado "f" (perto da câmera)

ALVOS = [
    ("macrodetails/universal-male-young-maxmuscle-averageweight.target", 1.0),
    ("macrodetails/caucasian-male-young.target", 1 / 3), ("macrodetails/african-male-young.target", 1 / 3), ("macrodetails/asian-male-young.target", 1 / 3),
    ("macrodetails/proportions/male-young-maxmuscle-averageweight-idealproportions.target", 1.0),
    # proporções de atleta natural (V): ombros largos, cintura fina, barriga chapada
    ("torso/torso-vshape-incr.target", 0.3),
    ("measure/measure-waist-circ-decr.target", 0.5),
    ("stomach/stomach-pregnant-decr.target", 0.6),
    ("measure/measure-neck-circ-incr.target", 0.25),
    ("buttocks/buttocks-volume-incr.target", 0.2),
    ("measure/measure-upperarm-circ-incr.target", 0.35),
    ("measure/measure-thigh-circ-incr.target", 0.2),
    ("measure/measure-calf-circ-incr.target", 0.25),
]
NIVEL_SUB = 2  # subdivisão da malha em repouso (relevo muscular precisa de densidade)


# ------------------------------------------------------------------ carga do MakeHuman

def ler_obj(caminho):
    verts, faces, grupo = [], [], None
    for linha in open(caminho):
        if linha.startswith("v "):
            _, x, y, z = linha.split()[:4]
            verts.append((float(x), float(y), float(z)))
        elif linha.startswith("g "):
            grupo = linha.split()[1].strip()
        elif linha.startswith("f ") and grupo in ("body", "helper-l-eye", "helper-r-eye"):
            faces.append([int(p.split("/")[0]) - 1 for p in linha.split()[1:]])
    return np.array(verts), faces


def aplicar_alvos(v, mh):
    for rel, peso in ALVOS:
        p = os.path.join(mh, "targets", rel)
        if not os.path.exists(p):
            print("alvo ausente:", rel)
            continue
        for linha in open(p):
            if not linha.strip() or linha.startswith("#"):
                continue
            i, dx, dy, dz = linha.split()
            v[int(i)] += peso * np.array((float(dx), float(dy), float(dz)))
    return v


def mh_para_blender(v):
    return np.stack([v[:, 0], -v[:, 2], v[:, 1]], axis=1)


class Humano:
    def __init__(self, mh):
        v, faces = ler_obj(os.path.join(mh, "3dobjs", "base.obj"))
        v = mh_para_blender(aplicar_alvos(v, mh))
        usados = sorted({i for f in faces for i in f})
        mapa = {old: new for new, old in enumerate(usados)}
        self.verts = v[usados]
        self.faces = [[mapa[i] for i in f] for f in faces]
        skel = json.load(open(os.path.join(mh, "rigs", "default.mhskel")))
        self.juntas = {k: v[idx].mean(axis=0) for k, idx in skel["joints"].items()}
        self.ossos = skel["bones"]
        pesos = json.load(open(os.path.join(mh, "rigs", "default_weights.mhw")))["weights"]
        self.pesos = {b: [(mapa[i], w) for i, w in lst if i in mapa] for b, lst in pesos.items()}
        self._criar()

    def _criar(self):
        malha = bpy.data.meshes.new("corpo")
        malha.from_pydata([tuple(p) for p in self.verts], [], self.faces)
        malha.update()
        self.obj = bpy.data.objects.new("corpo", malha)
        bpy.context.scene.collection.objects.link(self.obj)
        for b, lst in self.pesos.items():
            g = self.obj.vertex_groups.new(name=b)
            for i, w in lst:
                g.add([i], w, "REPLACE")
        self._subdividir_e_esculpir()
        arm = bpy.data.armatures.new("esqueleto")
        self.rig = bpy.data.objects.new("esqueleto", arm)
        bpy.context.scene.collection.objects.link(self.rig)
        bpy.context.view_layer.objects.active = self.rig
        bpy.ops.object.mode_set(mode="EDIT")
        eb = {}
        for nome, b in self.ossos.items():
            o = arm.edit_bones.new(nome)
            o.head = Vector(self.juntas[b["head"]])
            o.tail = Vector(self.juntas[b["tail"]])
            if (o.tail - o.head).length < 1e-4:
                o.tail = o.head + Vector((0, 0, 0.1))
            eb[nome] = o
        for nome, b in self.ossos.items():
            if b.get("parent"):
                eb[nome].parent = eb[b["parent"]]
        bpy.ops.object.mode_set(mode="OBJECT")
        mod = self.obj.modifiers.new("arm", "ARMATURE")
        mod.object = self.rig
        self.obj.parent = self.rig
        self._preparar_dedos()
        self.pernas = (self.juntas[self.ossos["upperleg01.L"]["head"]], self.juntas[self.ossos["lowerleg02.L"]["tail"]])

    def _subdividir_e_esculpir(self):
        """Subdivide a malha em repouso (pesos interpolados) e aplica o relevo muscular (anatomia.py)."""
        ob = self.obj
        if NIVEL_SUB:
            bpy.context.view_layer.objects.active = ob
            sub = ob.modifiers.new("sub0", "SUBSURF")
            sub.levels = NIVEL_SUB
            sub.render_levels = NIVEL_SUB
            bpy.ops.object.modifier_apply(modifier="sub0")
        me = ob.data
        n = len(me.vertices)
        co = np.zeros(n * 3); me.vertices.foreach_get("co", co); V = co.reshape(-1, 3)
        no = np.zeros(n * 3); me.vertex_normals.foreach_get("vector", no); N = no.reshape(-1, 3)
        ev = np.zeros(len(me.edges) * 2, dtype=np.int64); me.edges.foreach_get("vertices", ev); E = ev.reshape(-1, 2)
        nomes = {g.index: g.name for g in ob.vertex_groups}
        W = {nm: np.zeros(n) for nm in nomes.values()}
        for v in me.vertices:
            for g in v.groups:
                W[nomes[g.group]][v.index] = g.weight
        self.W = W
        self.E, self.deg = anatomia.arestas_vizinhos(E, n)
        J = lambda osso, cauda=False: self.juntas[self.ossos[osso]["tail" if cauda else "head"]]  # noqa: E731
        V2, self.musculos, self.cavidade, self.domos = anatomia.esculpir(V, N, W, J, self.E, self.deg)
        me.vertices.foreach_set("co", V2.ravel())
        me.update()
        me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
        self.verts = V2
        self.normais = N
        dedos = lambda sf: [b for b in W if b.endswith(sf) and (b.startswith(("finger", "metacarpal")) or b.startswith("wrist"))]  # noqa: E731
        sm = lambda nomes: sum((W.get(b, np.zeros(n)) for b in nomes), np.zeros(n))  # noqa: E731
        self.partes = {}
        for lado, sf in (("f", ".L"), ("t", ".R")):
            self.partes["mao_" + lado] = sm(dedos(sf)) > 0.5
            self.partes["pe_" + lado] = sm(["foot" + sf] + [b for b in W if b.startswith("toe") and b.endswith(sf)]) > 0.5
            jo = np.array(J("lowerleg01" + sf))
            self.partes["joelho_" + lado] = (np.linalg.norm(V2 - jo, axis=1) < 0.75) & (sm(["lowerleg01" + sf, "upperleg02" + sf]) > 0.5)
        a = me.attributes.new("cavidade", "FLOAT", "POINT")
        a.data.foreach_set("value", self.cavidade.astype(np.float32))

    # ---------------------------------------------------------- pose
    def _apontar(self, nome, direcao, torcao=0.0, referencia=None):
        """Orienta o osso para 'direcao' (mundo). Com 'referencia', aplica a rotação referencia->direcao ao osso em repouso."""
        pb = self.rig.pose.bones[nome]
        rest = pb.bone.matrix_local.copy()
        dir_rest = referencia if referencia is not None else (rest.to_3x3() @ Vector((0, 1, 0))).normalized()
        q = dir_rest.rotation_difference(direcao.normalized())
        if torcao:
            q = Matrix.Rotation(math.radians(torcao), 4, direcao.normalized()).to_quaternion() @ q
        m = q.to_matrix().to_4x4() @ Matrix(rest.to_3x3()).to_4x4()
        # posição: cabeça do osso onde o pai deixou
        if pb.parent:
            parent_m = pb.parent.matrix
            rel = pb.parent.bone.matrix_local.inverted() @ rest
            m.translation = (parent_m @ rel).translation
        else:
            m.translation = rest.translation
        pb.matrix = m
        bpy.context.view_layer.update()

    def posar(self, pose):
        p = completar(pose)
        for pb in self.rig.pose.bones:
            pb.matrix_basis = Matrix()
        bpy.context.view_layer.update()

        def d(ang, abd=0.0, lado=1):
            r = math.radians(ang)
            v0 = FRENTE * math.sin(r) + CIMA * (-math.cos(r))
            b = math.radians(abd)
            return (v0 * math.cos(b) + ESQ * lado * math.sin(b)).normalized()

        tronco = d(p["t"])
        tr = p.get("tr", 0) or 0
        # raiz e coluna seguem o tronco
        self._apontar("root", tronco, tr * 0.3, referencia=CIMA)
        for nome in ("spine05", "spine04", "spine03", "spine02", "spine01"):
            self._apontar(nome, tronco, tr * 0.15)
        cab = d(p["c"])
        for nome in ("neck01", "neck02", "neck03", "head"):
            self._apontar(nome, cab)
        # elevação dos ombros (encolhimento): campo opcional "oe" 0..1
        oe = pose.get("oe", 0) or 0
        if oe:
            for sf, sx in ((".L", 1), (".R", -1)):
                pb = self.rig.pose.bones["clavicle" + sf]
                eixo = (pb.bone.matrix_local.to_3x3().inverted() @ FRENTE).normalized()
                pb.rotation_mode = "QUATERNION"
                pb.rotation_quaternion = Quaternion(eixo, math.radians(17 * oe * sx))
            bpy.context.view_layer.update()
        for lado, s, sufixo in (("f", 1, ".L"), ("t", -1, ".R")):
            b, a = p["b" + lado]
            ab = pose.get("b" + lado + "a", 0) or 0
            aa = pose.get("a" + lado + "a", ab) or 0
            for nome in ("upperarm01", "upperarm02"):
                self._apontar(nome + sufixo, d(b, ab, s))
            for nome in ("lowerarm01", "lowerarm02"):
                self._apontar(nome + sufixo, d(a, aa, s))
            if self.mao_apoio.get(lado):
                # mão espalmada: dedos para a frente, palma para baixo
                self._apontar("wrist" + sufixo, (FRENTE + ESQ * s * 0.25).normalized(), self.TORCAO_APOIO * s)
            else:
                self._apontar("wrist" + sufixo, d(a, aa, s))
            c_, sh, pe = p["p" + lado]
            pa = pose.get("p" + lado + "a", 0) or 0
            for nome in ("upperleg01", "upperleg02"):
                self._apontar(nome + sufixo, d(c_, pa, s))
            for nome in ("lowerleg01", "lowerleg02"):
                self._apontar(nome + sufixo, d(sh, pa, s))
            # o osso do pé aponta ~27° para baixo com o pé apoiado (pe = 90)
            self._apontar("foot" + sufixo, d(pe - 27, pa * 0.3, s))
        self._dedos(self.pegada)

    mao_apoio = {}
    TORCAO_APOIO = 0

    # dedos: 0 = relaxados (levemente fechados), 1 = segurando (barra/halter)
    pegada = 0.0
    CURVA = {"rel": ((14, 18, 12), (8, 10, 6)), "peg": ((62, 78, 48), (25, 30, 25))}

    def _dedos(self, pegada):
        for sufixo in (".L", ".R"):
            for f in range(1, 6):
                rel, peg = self.CURVA["rel"][f == 1], self.CURVA["peg"][f == 1]
                for j in range(1, 4):
                    nome = f"finger{f}-{j}{sufixo}"
                    if nome not in self.rig.pose.bones:
                        continue
                    ang = rel[j - 1] + (peg[j - 1] - rel[j - 1]) * pegada
                    pb = self.rig.pose.bones[nome]
                    eixo = self._eixo_dedo[nome]
                    pb.rotation_mode = "QUATERNION"
                    pb.rotation_quaternion = Quaternion(eixo, math.radians(ang * self.SINAL_DEDO))
        bpy.context.view_layer.update()

    SINAL_DEDO = 1

    def _preparar_dedos(self):
        """Eixo de flexão de cada falange (no espaço local do osso), a partir da geometria da mão em repouso."""
        self._eixo_dedo = {}
        J = lambda o, c=False: Vector(self.juntas[self.ossos[o]["tail" if c else "head"]])  # noqa: E731
        for sufixo, sx in ((".L", 1), (".R", -1)):
            punho = J("wrist" + sufixo)
            ponta = sum((J(f"finger{f}-1{sufixo}") for f in range(2, 6)), Vector()) / 4
            dmao = (ponta - punho).normalized()
            atravs = (J("finger2-1" + sufixo) - J("finger5-1" + sufixo)).normalized()
            for f in range(1, 6):
                for j in range(1, 4):
                    nome = f"finger{f}-{j}{sufixo}"
                    if nome not in self.ossos:
                        continue
                    b = self.rig.data.bones[nome]
                    dir_b = (J(nome, True) - J(nome)).normalized()
                    if f == 1:
                        palma = dmao.cross(atravs).normalized() * sx
                        eixo = palma.cross(dir_b).normalized()
                    else:
                        eixo = atravs * sx
                    self._eixo_dedo[nome] = (b.matrix_local.to_3x3().inverted() @ eixo).normalized()

    def pontos_mundo(self):
        """Malha avaliada (posada) em coordenadas do mundo."""
        dg = bpy.context.evaluated_depsgraph_get()
        ev = self.obj.evaluated_get(dg)
        me = ev.to_mesh()
        co = np.zeros(len(me.vertices) * 3)
        me.vertices.foreach_get("co", co)
        ev.to_mesh_clear()
        mw = np.array(ev.matrix_world)
        return co.reshape(-1, 3) @ mw[:3, :3].T + mw[:3, 3]

    def ik_braco(self, sf, alvo):
        """Reorienta braço/antebraço (espaço da armadura, rig na identidade) para a pegada chegar em 'alvo'."""
        S = np.array(self.junta_mundo("upperarm01" + sf))
        E = np.array(self.junta_mundo("lowerarm01" + sf))
        W = np.array(self.junta_mundo("wrist" + sf))
        G = self.pegada_mundo(sf)
        l1 = np.linalg.norm(E - S)
        l2 = np.linalg.norm(G - E)
        v = alvo - S
        d = min(np.linalg.norm(v), (l1 + l2) * 0.999)
        d = max(d, abs(l1 - l2) + 1e-3)
        u = v / max(np.linalg.norm(v), 1e-6)
        n = np.cross(E - S, G - S)
        if np.linalg.norm(n) < 1e-4:
            n = np.cross(u, np.array((1.0, 0, 0)))
        n /= np.linalg.norm(n)
        perp = np.cross(n, u)
        if np.dot(perp, E - S) < 0:
            perp = -perp
        a = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
        hh = math.sqrt(max(l1 * l1 - a * a, 0))
        E2 = S + u * a + perp * hh
        G2 = S + u * d
        dir1 = Vector(E2 - S).normalized()
        # o antebraço aponta do cotovelo ao punho; corrige pelo desvio punho->pegada
        ang_off = Vector(W - E).normalized().rotation_difference(Vector(G - E).normalized())
        dir2 = (ang_off.inverted() @ Vector(G2 - E2)).normalized()
        punho = Vector(self.rig.pose.bones["wrist" + sf].tail - self.rig.pose.bones["wrist" + sf].head).normalized()
        q_ante = Vector(W - E).normalized().rotation_difference(dir2)
        for nome in ("upperarm01", "upperarm02"):
            self._apontar(nome + sf, dir1)
        for nome in ("lowerarm01", "lowerarm02"):
            self._apontar(nome + sf, dir2)
        self._apontar("wrist" + sf, q_ante @ punho)
        self._dedos(self.pegada)

    def pegada_mundo(self, sufixo):
        """Centro da palma (onde a barra/halter fica) em coordenadas do mundo."""
        w = self.junta_mundo("wrist" + sufixo)
        f3 = self.junta_mundo("finger3-1" + sufixo)
        f2 = self.junta_mundo("finger2-1" + sufixo)
        f5 = self.junta_mundo("finger5-1" + sufixo)
        sx = 1 if sufixo == ".L" else -1
        palma = (f3 - w).cross(f2 - f5).normalized() * sx
        return np.array(w + (f3 - w) * 0.62 + palma * 0.22)

    def junta_mundo(self, nome_osso, cauda=False):
        pb = self.rig.pose.bones[nome_osso]
        return self.rig.matrix_world @ (pb.tail if cauda else pb.head)


# ------------------------------------------------------------------ regiões musculares

TRONCO = ["spine01", "spine02", "spine03", "spine04", "spine05", "breast.L", "breast.R", "root"]
PESCOCO_OSSOS = ["neck01", "neck02", "neck03"]

GRUPOS = {
    "Peito": (["peito"], ["deltoide", "triceps"]),
    "Costas": (["dorsal", "trapezio"], ["biceps", "deltoide"]),
    "Ombros": (["deltoide"], ["trapezio", "triceps"]),
    "Trapézio": (["trapezio"], ["deltoide"]),
    "Bíceps": (["biceps"], ["antebraco"]),
    "Tríceps": (["triceps"], ["deltoide", "peito"]),
    "Pernas": (["quadriceps", "gluteo"], ["posterior", "adutores", "panturrilha"]),
    "Posterior de coxa": (["posterior"], ["gluteo", "lombar"]),
    "Glúteos": (["gluteo"], ["posterior", "quadriceps"]),
    "Panturrilhas": (["panturrilha"], []),
    "Core": (["abdomen", "obliquos"], []),
    "Lombar": (["lombar"], ["gluteo", "posterior"]),
    "Pescoço": (["pescoco"], ["trapezio"]),
    "Corpo inteiro": (["quadriceps", "gluteo", "deltoide"], ["abdomen", "peito", "dorsal"]),
    "Cardio": (["quadriceps", "panturrilha"], ["gluteo", "posterior"]),
    "Equilíbrio": (["panturrilha", "gluteo"], ["abdomen"]),
}
DESTAQUE_PARA = {"coxa": ["quadriceps", "posterior"], "perna": ["panturrilha"], "tronco": ["abdomen", "lombar"], "braco": ["deltoide", "biceps", "triceps"],
                 "antebraco": ["antebraco"], "gluteo": ["gluteo"], "ombro": ["deltoide"]}

PELE = (0.50, 0.495, 0.49)
SHORT = (0.10, 0.10, 0.11)
TENIS = (0.08, 0.08, 0.085)
SOLA = (0.95, 0.30, 0.10)
PRIMARIO = (0.86, 0.11, 0.06)
SECUNDARIO = (0.93, 0.42, 0.28)


def calcular_regioes(h):
    """Regiões de cor = forma dos músculos esculpidos (anatomia.py) + short/tênis por geometria."""
    n = len(h.verts)
    V = h.verts
    W = h.W
    zero = np.zeros(n)

    def soma(nomes):
        return sum((W.get(x, zero) for x in nomes), zero.copy())
    J = lambda osso, cauda=False: h.juntas[h.ossos[osso]["tail" if cauda else "head"]]  # noqa: E731
    hip = J("upperleg01.L"); ank = J("foot.L")
    hipz, az = hip[2], ank[2]
    z = V[:, 2]
    tronco = soma(TRONCO) + soma(["pelvis.L", "pelvis.R"])
    braco = soma(["upperarm01.L", "upperarm01.R", "upperarm02.L", "upperarm02.R"])
    antebr = soma(["lowerarm01.L", "lowerarm01.R", "lowerarm02.L", "lowerarm02.R"]) + 0.6 * soma(["wrist.L", "wrist.R"])
    coxa = soma(["upperleg01.L", "upperleg01.R", "upperleg02.L", "upperleg02.R"])
    pesc = soma(PESCOCO_OSSOS)
    pe = soma(["foot.L", "foot.R"]) + soma([b for b in W if b.startswith("toe")])
    R = {k: v.copy() for k, v in h.musculos.items()}
    R["pescoco"] = np.clip((pesc - 0.4) * 2, 0, 1) * (V[:, 1] > -0.75 + 0 * z)
    # short: bainha levemente mais baixa atrás, cintura reta
    yb = np.clip(V[:, 1], -1, 1)
    lo, hi = hipz - 1.45 + 0.12 * yb, hipz + 0.92
    R["_short"] = (anatomia._smooth(lo - 0.025, lo + 0.025, z) * (1 - anatomia._smooth(hi - 0.025, hi + 0.025, z))
                   * anatomia._smooth(0.3, 0.6, coxa + tronco) * (1 - anatomia._smooth(0.1, 0.3, braco + antebr)))
    R["_tenis"] = ((pe > 0.5) | (z < az + 0.25)).astype(float)
    R["_sola"] = (z < (V[:, 2].min() + 0.22)).astype(float)
    h.regioes = R


def suavizar(h, arr, passos=3):
    return anatomia.suavizar_campo(arr, h.E, h.deg, passos * 2, 0.5)


def colorir(h, primarios, secundarios):
    n = len(h.verts)
    cor = np.tile(np.array(PELE), (n, 1))

    def pinta(mask, c, forca=1.0):
        m = suavizar(h, mask, 1) * forca
        cor[:] = cor * (1 - m[:, None]) + np.array(c) * m[:, None]
    for r in secundarios:
        if r in h.regioes:
            pinta(h.regioes[r], SECUNDARIO, 0.9)
    for r in primarios:
        if r in h.regioes:
            pinta(h.regioes[r], PRIMARIO, 1.0)
    # short (com o glúteo em destaque aparecendo por cima em tom escuro avermelhado)
    sm = suavizar(h, h.regioes["_short"], 1)
    alvo_short = np.tile(np.array(SHORT), (n, 1))
    if "gluteo" in primarios:
        g = suavizar(h, h.regioes["gluteo"], 1) * 0.8
        alvo_short = alvo_short * (1 - g[:, None]) + np.array((0.50, 0.05, 0.035)) * g[:, None]
    cor = cor * (1 - sm[:, None]) + alvo_short * sm[:, None]
    tm = suavizar(h, h.regioes["_tenis"], 1)
    cor = cor * (1 - tm[:, None]) + np.array(TENIS) * tm[:, None]
    so = h.regioes["_sola"]
    cor = cor * (1 - so[:, None]) + np.array(SOLA) * so[:, None]
    rgba = np.concatenate([cor, np.ones((n, 1))], axis=1).astype(np.float32)
    h.obj.data.color_attributes["cor"].data.foreach_set("color", rgba.ravel())


# ------------------------------------------------------------------ cena

def cena(tam, amostras):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = amostras
    sc.cycles.use_denoising = True
    sc.render.resolution_x = tam
    sc.render.resolution_y = tam
    sc.render.film_transparent = True
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    world = bpy.data.worlds.new("mundo")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.05, 0.045, 0.04, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.6
    sc.world = world
    bpy.ops.mesh.primitive_plane_add(size=120, location=(0, 0, 0))
    bpy.context.active_object.is_shadow_catcher = True

    def luz(nome, loc, energia, tam_luz, cor=(1, 1, 1)):
        l = bpy.data.lights.new(nome, "AREA")
        l.energy = energia; l.size = tam_luz; l.color = cor
        o = bpy.data.objects.new(nome, l)
        o.location = loc
        o.rotation_euler = (Vector((0, 0, 9)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        sc.collection.objects.link(o)
    # chave bem lateral em relação à câmera (azimute ~64°) para revelar o relevo; preenchimento suave do lado da câmera
    luz("chave", (-6, -26, 24), 9000, 3.5)
    luz("preenchimento", (26, -6, 10), 1500, 18, (0.9, 0.95, 1.0))
    luz("recorte", (8, 24, 20), 7000, 4, (1.0, 0.82, 0.66))
    cam = bpy.data.cameras.new("cam")
    cam.type = "ORTHO"
    co = bpy.data.objects.new("cam", cam)
    sc.collection.objects.link(co)
    sc.camera = co
    return co


def material_corpo():
    """Pele clara acinzentada, leve brilho; cavidade dos sulcos (anatomia) + AO escurecem os vales entre músculos."""
    m = bpy.data.materials.new("pele")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    attr = nt.nodes.new("ShaderNodeVertexColor")
    attr.layer_name = "cor"
    cav = nt.nodes.new("ShaderNodeAttribute")
    cav.attribute_name = "cavidade"
    cavm = nt.nodes.new("ShaderNodeMapRange")
    cavm.inputs["To Min"].default_value = 1.0
    cavm.inputs["To Max"].default_value = 0.55
    nt.links.new(cav.outputs["Fac"], cavm.inputs["Value"])
    ao = nt.nodes.new("ShaderNodeAmbientOcclusion")
    ao.inputs["Distance"].default_value = 0.6
    ao.samples = 6
    gam = nt.nodes.new("ShaderNodeGamma")
    gam.inputs["Gamma"].default_value = 1.4
    nt.links.new(ao.outputs["AO"], gam.inputs["Color"])
    m1 = nt.nodes.new("ShaderNodeMix"); m1.data_type = "RGBA"; m1.blend_type = "MULTIPLY"
    m1.inputs["Factor"].default_value = 0.75
    nt.links.new(attr.outputs["Color"], m1.inputs[6])
    nt.links.new(gam.outputs["Color"], m1.inputs[7])
    m2 = nt.nodes.new("ShaderNodeMix"); m2.data_type = "RGBA"; m2.blend_type = "MULTIPLY"
    m2.inputs["Factor"].default_value = 1.0
    nt.links.new(m1.outputs[2], m2.inputs[6])
    nt.links.new(cavm.outputs["Result"], m2.inputs[7])
    nt.links.new(m2.outputs[2], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.5
    bsdf.inputs["Specular IOR Level"].default_value = 0.45
    bsdf.inputs["Coat Weight"].default_value = 0.08
    bsdf.inputs["Coat Roughness"].default_value = 0.25
    bsdf.inputs["Subsurface Weight"].default_value = 0.0
    return m


def mat_simples(nome, cor, metal=0.0, rug=0.5, emissao=None):
    m = bpy.data.materials.get(nome) or bpy.data.materials.new(nome)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*cor, 1)
    b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rug
    return m


def apontar_camera(co, centro, raio, azimute=64, elevacao=10):
    az, el = math.radians(azimute), math.radians(elevacao)
    dirc = (FRENTE * math.cos(az) + ESQ * math.sin(az)) * math.cos(el) + CIMA * math.sin(el)
    co.location = Vector(centro) + dirc * 80
    co.rotation_euler = (Vector(centro) - co.location).to_track_quat("-Z", "Y").to_euler()
    co.data.ortho_scale = raio * 2.2
    co.data.clip_end = 300


# ------------------------------------------------------------------ aparelhos 3D

class Aparelhos:
    def __init__(self):
        self.objs = []
        self.metal = mat_simples("metal", (0.62, 0.62, 0.64), 1.0, 0.28)
        self.preto = mat_simples("preto", (0.035, 0.035, 0.04), 0.0, 0.55)
        self.estofado = mat_simples("estofado", (0.07, 0.07, 0.075), 0.0, 0.65)
        self.brasa = mat_simples("brasa", (0.95, 0.28, 0.08), 0.0, 0.4)
        self.chao = mat_simples("tapete", (0.20, 0.08, 0.05), 0.0, 0.9)

    def limpar(self):
        for o in self.objs:
            bpy.data.objects.remove(o, do_unlink=True)
        self.objs = []

    def _add(self, o, mat):
        o.data.materials.clear(); o.data.materials.append(mat)
        for p in o.data.polygons:
            p.use_smooth = True
        self.objs.append(o)
        return o

    def cilindro(self, a, b, r, mat, verts=32):
        a, b = Vector(a), Vector(b)
        d = b - a
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=max(d.length, 1e-3), location=(a + b) / 2)
        o = bpy.context.active_object
        o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
        return self._add(o, mat)

    def caixa(self, centro, tam, mat, bevel=0.15):
        bpy.ops.mesh.primitive_cube_add(size=1, location=centro)
        o = bpy.context.active_object
        o.scale = tam
        bpy.ops.object.transform_apply(scale=True)
        if bevel:
            m = o.modifiers.new("b", "BEVEL"); m.width = bevel; m.segments = 3
        return self._add(o, mat)

    def esfera(self, c, r, mat):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=c, segments=32, ring_count=16)
        return self._add(bpy.context.active_object, mat)

    def toro(self, c, r1, r2, mat, eixo=(1, 0, 0)):
        bpy.ops.mesh.primitive_torus_add(major_radius=r1, minor_radius=r2, location=c)
        o = bpy.context.active_object
        o.rotation_euler = Vector(eixo).to_track_quat("Z", "Y").to_euler()
        return self._add(o, mat)


def p2_para_3d(x2, y2, ref):
    """Converte um ponto 2D da animação (x para frente, y para cima) em 3D. ref = (x2_quadril0, ponto3d_quadril0, k)."""
    hx2, h3, k = ref
    return Vector((0, h3.y, 0)) + FRENTE * ((x2 - hx2) * k) + CIMA * (y2 * k) + Vector((0, 0, 0)) * 0


def montar_aparelhos(ap, anim, h, ref, fase):
    """fase 'fixos': objetos parados; 'maos': objetos presos às mãos (refeitos a cada quadro)."""
    k = ref[2]
    for pr in anim.get("props", []):
        tp = pr.get("tipo")
        if fase == "fixos":
            if tp in ("banco", "maquina", "caixa"):
                x, y, w, hh = pr.get("x", 0), pr.get("y", 0), pr.get("w", 8), pr.get("h", 4)
                c = p2_para_3d(x + w / 2, 0, ref)
                topo = (y + hh) * k
                ap.caixa((c.x, c.y, topo - 0.45), (3.4, w * k, 0.9), ap.estofado)
                for dx in (-1.2, 1.2):
                    for dyy in (-w * k / 2 + 0.6, w * k / 2 - 0.6):
                        ap.cilindro((dx, c.y + dyy, 0), (dx, c.y + dyy, topo - 0.9), 0.18, ap.metal, 16)
                if tp == "maquina":
                    tras = p2_para_3d(x + w - 0.5, 0, ref)
                    ap.caixa((0, tras.y + 0.6, topo + 6), (4.5, 1.2, 12 + topo * 0.2), ap.preto, 0.2)
                    ap.caixa((0, tras.y + 1.4, 5), (2.4, 0.6, 8), ap.metal, 0.1)
            elif tp == "barra_fixa":
                c = p2_para_3d(pr.get("x", 0), pr.get("y", 21), ref)
                mb = max(5.0, anim.get("_xmax_maos", 0) + 1.0)
                ap.cilindro((-mb, c.y, c.z), (mb, c.y, c.z), 0.16, ap.metal)
                for dx in (-mb, mb):
                    ap.cilindro((dx, c.y, 0), (dx, c.y, c.z + 0.3), 0.25, ap.preto, 16)
            elif tp == "saco":
                c = p2_para_3d(pr.get("x", 9), 0, ref)
                ap.cilindro((0, c.y, 5.5 * k), (0, c.y, 17.5 * k), 1.5, ap.preto)
                ap.cilindro((0, c.y, 17.5 * k), (0, c.y, 26), 0.05, ap.metal, 8)
                ap.toro((0, c.y, 11.5 * k), 1.52, 0.06, ap.brasa, (0, 0, 1))
            elif tp == "esteira":
                c = p2_para_3d(0, 0, ref)
                ap.caixa((0, c.y, 0.35), (5, 18, 0.7), ap.preto, 0.2)
                ap.caixa((0, c.y - 8.5, 0.72), (4.4, 1.2, 0.05), ap.brasa, 0)
                ap.cilindro((2.2, c.y - 9, 0.7), (2.2, c.y - 10.5, 11), 0.2, ap.metal, 16)
                ap.cilindro((-2.2, c.y - 9, 0.7), (-2.2, c.y - 10.5, 11), 0.2, ap.metal, 16)
                ap.caixa((0, c.y - 10.6, 11.2), (5, 1.4, 1.0), ap.preto, 0.2)
            elif tp == "tapete":
                c = p2_para_3d(0, 0, ref)
                ap.caixa((0, c.y, 0.06), (6, 20, 0.12), ap.chao, 0.05)
            elif tp == "rolo":
                c = p2_para_3d(pr.get("x", 0), pr.get("y", 0.8), ref)
                ap.cilindro((-3, c.y, c.z), (3, c.y, c.z), 0.8, ap.brasa)
            elif tp == "bike":
                q = h.junta_mundo("root")
                cy = q.y
                for dy in (5.5, -6.5):
                    ap.toro((0, cy + dy, 2.7), 2.6, 0.13, ap.preto)
                ap.cilindro((0, cy, q.z - 0.6), (0, cy - 1.2, 2.7), 0.18, ap.metal, 16)
                ap.cilindro((0, cy - 1.2, 2.7), (0, cy + 5.5, 2.7), 0.16, ap.metal, 16)
                ap.cilindro((0, cy - 1.2, 2.7), (0, cy - 5.6, q.z + 2.0), 0.16, ap.metal, 16)
                ap.cilindro((0, cy - 5.6, q.z + 2.0), (0, cy - 6.5, 2.7), 0.16, ap.metal, 16)
                ap.caixa((0, cy + 0.2, q.z - 0.55), (1.0, 2.2, 0.35), ap.estofado, 0.1)
                ap.cilindro((-1.6, cy - 5.6, q.z + 2.0), (1.6, cy - 5.6, q.z + 2.0), 0.13, ap.metal, 16)
            elif tp in ("elastico", "cabo") and isinstance(pr.get("ate"), list):
                a = p2_para_3d(pr["ate"][0], pr["ate"][1], ref)
                if tp == "cabo":
                    ap.caixa((0, a.y + 0.9, max(a.z, 1) / 2 + 3), (3.0, 1.0, max(a.z, 1) + 6), ap.preto, 0.2)
                    ap.toro((0, a.y + 0.2, a.z), 0.45, 0.12, ap.metal, (1, 0, 0))
        else:
            mf = Vector(h.pegada_mundo(".L")); mt = Vector(h.pegada_mundo(".R"))
            meio = (mf + mt) / 2
            if tp == "barra":
                R = anim.get("_anilha", 2.2)
                comp = 10 if R > 1.5 else 7
                ap.cilindro((-comp, meio.y, meio.z), (comp, meio.y, meio.z), 0.15, ap.metal)
                for sx in (-1, 1):
                    ap.cilindro((sx * (comp - 3.8), meio.y, meio.z), (sx * (comp - 3.2), meio.y, meio.z), R, ap.preto, 48)
                    ap.toro((sx * (comp - 3.15), meio.y, meio.z), R, 0.07, ap.brasa)
            elif tp == "halter":
                for m in (mf, mt):
                    ap.cilindro((m.x - 0.6, m.y, m.z), (m.x + 0.6, m.y, m.z), 0.14, ap.metal, 16)
                    for sx in (-1, 1):
                        ap.cilindro((m.x + sx * 0.6, m.y, m.z), (m.x + sx * 1.05, m.y, m.z), 0.62, ap.preto, 6)
            elif tp == "kettlebell":
                c = meio + Vector((0, 0, -1.1))
                ap.esfera(c, 0.95, ap.preto)
                ap.toro(c + Vector((0, 0, 1.0)), 0.5, 0.12, ap.preto, (1, 0, 0))
            elif tp == "bola":
                ap.esfera(meio, 1.1, ap.brasa)
            elif tp in ("elastico", "cabo"):
                ate = pr.get("ate")
                if ate == "maos":
                    ap.cilindro(mf, mt, 0.09, ap.brasa, 12)
                elif ate == "pes":
                    for m, pe in ((mf, h.junta_mundo("foot.L")), (mt, h.junta_mundo("foot.R"))):
                        ap.cilindro(m, pe, 0.07, ap.brasa, 8)
                elif isinstance(ate, list):
                    a = p2_para_3d(ate[0], ate[1], ref)
                    for m in (mf, mt):
                        ap.cilindro(m, (m.x, a.y, a.z), 0.06 if tp == "cabo" else 0.08, ap.metal if tp == "cabo" else ap.brasa, 8)


# ------------------------------------------------------------------ animação

CAMPOS_3D = ("bfa", "bta", "afa", "ata", "pfa", "pta", "tr", "oe")


def interp3(a, b, t):
    p = interpolar(a, b, t)
    e = t * t * (3 - 2 * t)
    for k in CAMPOS_3D:
        va, vb = a.get(k), b.get(k)
        if va is None and vb is None:
            continue
        if k in ("afa", "ata"):
            base = "bfa" if k == "afa" else "bta"
            va = va if va is not None else a.get(base, 0) or 0
            vb = vb if vb is not None else b.get(base, 0) or 0
        p[k] = (va or 0) + ((vb or 0) - (va or 0)) * e
    return p


def quadros_anim(anim, fps):
    q = anim["quadros"]
    tempos = anim.get("tempos", [1.0] * len(q))
    out = []
    for i in range(len(q)):
        n = max(2, round(tempos[i % len(tempos)] * fps))
        for j in range(n):
            out.append(interp3(q[i], q[(i + 1) % len(q)], j / n))
    return out


def _mat_np(m):
    return np.array([list(r) for r in m])


def _aplicar(T, pts):
    return pts @ T[:3, :3].T + T[:3, 3]


def _rot_x(piv, ang):
    c, s = math.cos(ang), math.sin(ang)
    R = np.eye(4)
    R[1, 1], R[1, 2], R[2, 1], R[2, 2] = c, -s, s, c
    A = np.eye(4); A[:3, 3] = piv
    B = np.eye(4); B[:3, 3] = -np.asarray(piv)
    return A @ R @ B


def _trans(d):
    T = np.eye(4); T[:3, 3] = d
    return T


def _barra_2d(anim):
    for pr in anim.get("props", []):
        if pr.get("tipo") == "barra_fixa":
            return (pr.get("x", 0), pr.get("y", 21))
    return None


def _topos_apoio(anim):
    """Superfícies onde a mão pode apoiar espalmada: chão + topo de bancos/caixas (x0, x1, altura) em unidades 2D."""
    tops = [(-1e9, 1e9, 0.0)]
    for pr in anim.get("props", []):
        if pr.get("tipo") in ("banco", "caixa", "maquina"):
            x, w = pr.get("x", 0), pr.get("w", 8)
            tops.append((x - 0.5, x + w + 0.5, pr.get("y", 0) + pr.get("h", 4)))
    return tops


def posicionar(h, anim, pose, k, ref):
    """Posa e coloca o corpo no lugar, corrigindo a diferença de proporções entre o esqueleto 2D e o humano 3D:
    - mãos de apoio (no chão/banco) ficam espalmadas, dedos para a frente;
    - com dois apoios no chão (mãos e pés/joelhos) o corpo gira no plano sagital até os dois tocarem o chão;
    - "fixo": o ponto fixo (mão/pé da frente) fica parado no mundo 3D, não no 2D;
    - barra fixa: mãos na barra (pendurado: o corpo sobe/desce até a pegada; com pés no chão: gira em volta dos pés).
    ref: dict compartilhado na animação (k, e o que o primeiro quadro define)."""
    if not isinstance(ref, dict):
        ref = {"k": k}
    pose2 = completar({kk: v for kk, v in pose.items() if kk not in CAMPOS_3D})
    p2 = pontos_anim(anim, pose2)
    props_maos = any(pr.get("em") == "maos" for pr in anim.get("props", []))
    barra = _barra_2d(anim)
    tops = _topos_apoio(anim)
    apoio = {}
    for lado in ("f", "t"):
        mx, my = p2["mao_" + lado]
        perto_barra = barra is not None and math.dist((mx, my), barra) < 1.6
        apoio[lado] = (not props_maos and not perto_barra and any(x0 <= mx <= x1 and abs(my - top) < 0.4 for x0, x1, top in tops))
    h.mao_apoio = apoio
    h.rig.matrix_world = Matrix()
    bpy.context.view_layer.update()
    h.posar(pose)
    pts = h.pontos_mundo()
    T = np.eye(4)
    junta = lambda nome, cauda=False: np.array(h.junta_mundo(nome, cauda))  # noqa: E731 (sem T: rig na identidade)
    # 1) dois apoios no chão -> nivelar
    sup = []
    for nome2, parte in (("mao_f", "mao_f"), ("mao_t", "mao_t"), ("ponta_f", "pe_f"), ("calcanhar_f", "pe_f"), ("ponta_t", "pe_t"),
                         ("calcanhar_t", "pe_t"), ("joelho_f", "joelho_f"), ("joelho_t", "joelho_t")):
        if p2[nome2][1] < 0.35 and pose.get("y") is None:
            sup.append((p2[nome2][0], parte))
    if sup:
        xs = [x for x, _ in sup]
        if max(xs) - min(xs) > 2.5:
            frente = {pt for x, pt in sup if x > max(xs) - 1.2}
            tras = {pt for x, pt in sup if x < min(xs) + 1.2}
            for _ in range(2):
                P = _aplicar(T, pts)

                def baixo(partes):
                    m = np.zeros(len(P), bool)
                    for pt in partes:
                        m |= h.partes[pt]
                    idx = np.where(m)[0]
                    i0 = idx[np.argmin(P[idx, 2])]
                    return P[i0]
                a, b = baixo(frente), baixo(tras)
                ang = math.atan2(b[2] - a[2], b[1] - a[1])
                alvo = 0.0 if abs(ang) < math.pi / 2 else math.copysign(math.pi, ang)
                giro = max(-0.45, min(0.45, alvo - ang))
                T = _rot_x(a, giro) @ T
    # 2) horizontal
    fixo = anim.get("fixo")
    chave3 = None
    if fixo == "maos":
        chave3 = lambda TT: _aplicar(TT, h.pegada_mundo(".L")[None])[0]  # noqa: E731
    elif fixo == "pes":
        chave3 = lambda TT: _aplicar(TT, junta("foot.L")[None])[0]  # noqa: E731
    quad3 = _aplicar(T, junta("root")[None])[0]
    if chave3 is not None and "ancora" in ref:
        dy = ref["ancora"] - chave3(T)[1]
    elif "quad" in ref:
        dy = ref["quad"][1][1] + (-(p2["quadril"][0] - ref["quad"][0])) * k - quad3[1]
    else:
        dy = 0.0
    T = _trans((0, dy, 0)) @ T
    # 3) vertical
    if pose.get("y") is not None:
        dz = p2["quadril"][1] * k - _aplicar(T, junta("root")[None])[0][2]
    else:
        dz = -_aplicar(T, pts)[:, 2].min() + (pose.get("ay", 0) or 0) * k
    T = _trans((0, 0, dz)) @ T
    # 4) barra fixa: mãos na barra
    if barra is not None and "barra3" in ref and math.dist(p2["mao_f"], barra) < 1.6:
        g = (_aplicar(T, h.pegada_mundo(".L")[None])[0] + _aplicar(T, h.pegada_mundo(".R")[None])[0]) / 2
        b3 = ref["barra3"]
        pes_chao = min(p2["ponta_f"][1], p2["calcanhar_f"][1]) < 0.35 and pose.get("y") is None
        if pes_chao:
            piv = _aplicar(T, junta("foot.L")[None])[0]
            r = math.hypot(g[1] - piv[1], g[2] - piv[2])
            if r > 1e-3 and abs(b3[2] - piv[2]) < r:
                ang_g = math.atan2(g[2] - piv[2], g[1] - piv[1])
                alvo = math.asin((b3[2] - piv[2]) / r)
                alvo = alvo if math.cos(ang_g) >= 0 else math.pi - alvo
                d = (alvo - ang_g + math.pi) % (2 * math.pi) - math.pi
                T = _rot_x(piv, max(-0.5, min(0.5, d))) @ T
        else:
            T = _trans((0, b3[1] - g[1], b3[2] - g[2])) @ T
        # IK de dois ossos por braço: cada mão alcança a barra (corrige braço 3D x 2D)
        Ti = np.linalg.inv(T)
        for _ in range(2):
            for sf in (".L", ".R"):
                gl = h.pegada_mundo(sf)
                alvo = _aplicar(Ti, np.array([[0, b3[1], b3[2]]]))[0]
                alvo[0] = gl[0]
                h.ik_braco(sf, alvo)
        if os.environ.get("FORJA_DEBUG"):
            g2 = (_aplicar(T, h.pegada_mundo(".L")[None])[0] + _aplicar(T, h.pegada_mundo(".R")[None])[0]) / 2
            print("barra: pegada-barra", np.round(g2 - b3, 2), flush=True)
    if chave3 is not None and "ancora" not in ref:
        ref["ancora"] = chave3(T)[1]
    gx = max(abs(_aplicar(T, h.pegada_mundo(sf)[None])[0][0]) for sf in (".L", ".R"))
    ref["xmax_maos"] = max(ref.get("xmax_maos", 0.0), gx)
    h.rig.matrix_world = Matrix(T.tolist())
    bpy.context.view_layer.update()
    if "quad" not in ref:
        ref["quad"] = (p2["quadril"][0], np.array(h.junta_mundo("root")))
    return p2


def fundo(tam):
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (tam, tam))
    px = img.load()
    for yy in range(tam):
        t = yy / tam
        c = (int(27 - 13 * t), int(24 - 11 * t), int(21 - 9 * t))
        for xx in range(tam):
            px[xx, yy] = c
    halo = Image.new("L", (tam, tam), 0)
    ImageDraw.Draw(halo).ellipse((tam * 0.1, tam * 0.0, tam * 0.9, tam * 0.75), fill=40)
    from PIL import ImageFilter
    halo = halo.filter(ImageFilter.GaussianBlur(tam / 8))
    luz = Image.new("RGB", (tam, tam), (255, 190, 140))
    return Image.composite(luz, img, halo)


def main():
    from PIL import Image
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--mh", required=True)
    ap_.add_argument("--anim", required=True, nargs="+")
    ap_.add_argument("--ex", default=os.path.join(AQUI, "..", "..", "app", "src", "main", "assets", "exercises.json"))
    ap_.add_argument("--ids", default="")
    ap_.add_argument("--saida", required=True)
    ap_.add_argument("--tam", type=int, default=320)
    ap_.add_argument("--amostras", type=int, default=20)
    ap_.add_argument("--fps", type=float, default=6)
    ap_.add_argument("--chaves", action="store_true", help="só quadros-chave (revisão)")
    ap_.add_argument("--pular-existentes", action="store_true")
    a = ap_.parse_args(sys.argv[1:])
    bpy.ops.wm.read_factory_settings(use_empty=True)
    os.makedirs(a.saida, exist_ok=True)
    co = cena(a.tam * 2 if a.chaves else a.tam, a.amostras)
    h = Humano(a.mh)
    h.obj.data.materials.append(material_corpo())
    h.obj.data.color_attributes.new("cor", "FLOAT_COLOR", "POINT")
    calcular_regioes(h)
    grupos = {e["id"]: e for e in json.load(open(a.ex))}
    ap = Aparelhos()
    tam_saida = a.tam * 2 if a.chaves else a.tam
    bg = fundo(tam_saida)
    k = (h.juntas[h.ossos["upperleg01.L"]["head"]][2] - h.juntas[h.ossos["foot.L"]["head"]][2]) / 8.7
    meta_path = os.path.join(a.saida, "meta.json")
    meta = json.load(open(meta_path)) if os.path.exists(meta_path) else {}
    ids = set(x for x in a.ids.split(",") if x)
    for arq in a.anim:
        for anim in json.load(open(arq)):
            aid = anim["id"]
            if ids and aid not in ids:
                continue
            if a.pular_existentes and not a.chaves and os.path.exists(os.path.join(a.saida, f"{aid}.webp")):
                continue
            ex = grupos.get(aid, {})
            prim, sec = GRUPOS.get(ex.get("grupo", ""), ([], []))
            prim, sec = list(prim), list(sec)
            for d in anim.get("destaque", []):
                for r in DESTAQUE_PARA.get(d, []):
                    if r not in prim and r not in sec:
                        (prim if not prim else sec).append(r)
            colorir(h, prim, sec)
            if ex.get("grupo") == "Trapézio" and not any("oe" in q for q in anim["quadros"]):
                for i_q, q in enumerate(anim["quadros"]):
                    q["oe"] = 0 if i_q == 0 else 1
            if anim["id"].startswith("band-pull-apart") and not anim.get("props"):
                anim["props"] = [{"tipo": "elastico", "de": "maos", "ate": "maos"}]
            h.pegada = 1.0 if any(pr.get("em") == "maos" or pr.get("de") == "maos" or pr.get("tipo") == "barra_fixa"
                                  for pr in anim.get("props", [])) else 0.0
            anim["_anilha"] = 1.25 if ex.get("grupo") in ("Bíceps", "Tríceps", "Ombros", "Trapézio") else 2.2
            poses = anim["quadros"] if a.chaves else quadros_anim(anim, a.fps)
            # referência (quadro 0) e enquadramento fixo
            ref0 = {"k": k}
            posicionar(h, anim, anim["quadros"][0], k, ref0)
            ref_props = (ref0["quad"][0], Vector(ref0["quad"][1]), k)
            b2 = _barra_2d(anim)
            if b2 is not None:
                ref0["barra3"] = np.array(p2_para_3d(b2[0], b2[1], ref_props))
            todos = []
            for pose in anim["quadros"] + poses[:: max(1, len(poses) // 8)]:
                posicionar(h, anim, pose, k, ref0)
                todos.append(h.pontos_mundo())
            ap.limpar()
            anim["_xmax_maos"] = ref0.get("xmax_maos", 0)
            montar_aparelhos(ap, anim, h, ref_props, "fixos")
            pts = np.concatenate(todos)
            extra = [o for o in ap.objs]
            lo, hi = pts.min(axis=0), pts.max(axis=0)
            for o in extra:
                for c in o.bound_box:
                    w = o.matrix_world @ Vector(c)
                    lo = np.minimum(lo, np.array(w)); hi = np.maximum(hi, np.array(w))
            lo[2] = 0
            centro = (lo + hi) / 2
            raio = max(hi[2] - lo[2], np.linalg.norm((hi - lo)[:2]) * 0.85) / 2 + 0.6
            apontar_camera(co, centro, raio)
            n_fixos = len(ap.objs)
            frames = []
            for j, pose in enumerate(poses):
                posicionar(h, anim, pose, k, ref0)
                for o in ap.objs[n_fixos:]:
                    bpy.data.objects.remove(o, do_unlink=True)
                ap.objs = ap.objs[:n_fixos]
                montar_aparelhos(ap, anim, h, ref_props, "maos")
                caminho = os.path.join(a.saida, f"_tmp_{aid}_{j}.png")
                bpy.context.scene.render.filepath = caminho
                bpy.ops.render.render(write_still=True)
                im = Image.open(caminho).convert("RGBA")
                base = bg.copy().convert("RGBA")
                base.alpha_composite(im)
                frames.append(base.convert("RGB"))
                os.remove(caminho)
            if a.chaves:
                folha = Image.new("RGB", (tam_saida * len(frames), tam_saida))
                for j, f in enumerate(frames):
                    folha.paste(f, (j * tam_saida, 0))
                folha.save(os.path.join(a.saida, f"{aid}.jpg"), quality=88)
            else:
                cols = 6
                linhas = math.ceil(len(frames) / cols)
                folha = Image.new("RGB", (cols * a.tam, linhas * a.tam), (14, 13, 12))
                for j, f in enumerate(frames):
                    folha.paste(f, ((j % cols) * a.tam, (j // cols) * a.tam))
                folha.save(os.path.join(a.saida, f"{aid}.webp"), "WEBP", quality=70, method=6)
                meta[aid] = {"f": len(frames), "c": cols, "s": a.tam, "fps": a.fps}
                json.dump(meta, open(meta_path, "w"), separators=(",", ":"))
            print("pronto", aid, len(frames), flush=True)


if __name__ == "__main__":
    main()
