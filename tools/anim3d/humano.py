"""Renderização 3D das demonstrações do Forja (Blender como módulo Python).

Corpo: malha-base do MakeHuman (CC0) com alvos de atleta (homem jovem, musculatura máxima, gordura mínima).
Esqueleto: default.mhskel + pesos default_weights.mhw do MakeHuman.
Poses: as mesmas de tools/anim (ângulos absolutos no plano sagital) + campos 3D opcionais (ausentes = 0):
  "bfa"/"bta": abdução do braço da frente/trás (0 = no plano sagital, 90 = aberto para o lado)
  "afa"/"ata": abdução do antebraço (padrão = a do braço)
  "pfa"/"pta": abdução da perna (coxa)
  "tr":   rotação do tronco (torção, graus; + gira o peito para o lado da câmera), distribuída pelas vértebras
  "inc":  inclinação lateral do tronco (graus; + inclina para o lado da câmera), distribuída pelas vértebras
  "rol":  rotação do corpo inteiro em torno do eixo frente-trás (graus; 90 = deitado de lado; + levanta o lado da câmera)
  "cinc": inclinação lateral da cabeça; "cr": rotação da cabeça (olhar para o lado; + para o lado da câmera)
  "z":    deslocamento lateral do quadril (unidades do esqueleto; + = para o lado da câmera)
  "oe":   elevação dos ombros 0..1 (encolhimento). Se ausente em exercícios do grupo Trapézio, vale 0 no 1º quadro e 1 nos demais.
Por animação:
  "cam":  azimute da câmera em graus (64 = 3/4, o padrão; 90 = de frente; 0 = perfil)
Acessórios além dos de tools/anim/esqueleto.py:
  "banco" com "inc": encosto inclinado (graus sobre a horizontal) saindo da borda de trás do assento ("enc": comprimento, padrão 7)
  "halter" com "maos": "f" | "t" | "ambas" (padrão)
  "cabo"/"elastico" com "ate": [x, y, z] (z = deslocamento lateral, + = lado da câmera) ou "ate": "pes"/"maos";
    "elastico" com "de": "costas" (passa por trás das costas, de mão a mão)
  "apoio_tornozelo" {"x":..,"y":..} (opcional): rolo que prende os tornozelos (nórdico); sem x/y usa os tornozelos do 1º quadro
  "maquina" alta (h >= 6.5, w <= 2.6) ao lado de um assento vira encosto; supino/peck-deck/desenvolvimento na máquina ganham braços móveis
Elástico entre as mãos: {"tipo": "elastico", "de": "maos", "ate": "maos"} (automático no band-pull-apart sem props).

Movimento: spline cúbica pelos quadros-chave (movimento.py), apoios firmes (pé/mão apoiados ficam parados no mundo via IK
de 2 ossos), nada atravessa o chão, coluna curva distribuída, pescoço/cabeça acompanham, escápulas sobem/retraem.

Uso (python do ambiente com bpy):
  python tools/anim3d/humano.py --mh <pasta makehuman/data> --anim <dados.json> [--ids a,b] --saida <pasta>
         [--tam 720] [--amostras 16] [--fps 22] [--video] [--crf 18] [--chaves | --tira N]
"""
import argparse
import json
import math
import os
import sys
import time

import bpy
import numpy as np
from mathutils import Matrix, Quaternion, Vector

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "anim"))
from esqueleto import pontos, pontos_anim  # noqa: E402

sys.path.insert(0, AQUI)
import anatomia  # noqa: E402
import aparelhos  # noqa: E402
import movimento as mov  # noqa: E402

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
    ("armslegs/l-lowerarm-muscle-incr.target", 0.6), ("armslegs/r-lowerarm-muscle-incr.target", 0.6),
    ("armslegs/l-upperarm-muscle-incr.target", 0.4), ("armslegs/r-upperarm-muscle-incr.target", 0.4),
    ("armslegs/l-lowerleg-muscle-incr.target", 0.3), ("armslegs/r-lowerleg-muscle-incr.target", 0.3),
    ("measure/measure-thigh-circ-incr.target", 0.2),
    ("measure/measure-calf-circ-incr.target", 0.25),
]
RELEVO = 1.2  # intensidade do relevo muscular (1 = alturas de anatomia.py)
NIVEL_SUB = 2  # subdivisão da malha em repouso (relevo muscular precisa de densidade)
LADOS = (("f", ".L", 1), ("t", ".R", -1))
COLUNA = ("root", "spine05", "spine04", "spine03", "spine02", "spine01")
PESCOCO = ("neck01", "neck02", "neck03", "head")


def d2(ang, abd=0.0, lado=1):
    """Direção (espaço do esqueleto) de um ângulo 2D absoluto + abdução para fora do corpo."""
    r = math.radians(ang)
    v0 = FRENTE * math.sin(r) + CIMA * (-math.cos(r))
    b = math.radians(abd)
    return (v0 * math.cos(b) + ESQ * lado * math.sin(b)).normalized()


def rot_corpo(phi, lat=0.0, tor=0.0):
    """Rotação de um segmento do tronco: inclinação sagital (ângulo 2D absoluto) . lateral . torção."""
    return (Matrix.Rotation(math.radians(180 - phi), 3, "X") @ Matrix.Rotation(math.radians(lat), 3, "Y")
            @ Matrix.Rotation(math.radians(tor), 3, "Z"))


def _wrap(a):
    return (a + 180.0) % 360.0 - 180.0


def _clamp(x, a, b):
    return a if x < a else b if x > b else x


def _lerp(a, b, t):
    return a + (b - a) * t


def _v(a):
    return Vector((float(a[0]), float(a[1]), float(a[2])))


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
        self._preparar_fk()
        self._preparar_maos()
        self._preparar_proxy()

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
        V2, self.musculos, self.cavidade, self.domos = anatomia.esculpir(V, N, W, J, self.E, self.deg, RELEVO)
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
            self.partes["antebraco_" + lado] = sm(["lowerarm01" + sf, "lowerarm02" + sf]) > 0.5
        self.partes["tronco"] = sm(["spine01", "spine02", "spine03", "spine04", "spine05", "root", "pelvis.L", "pelvis.R",
                                    "breast.L", "breast.R", "clavicle.L", "clavicle.R", "neck01", "neck02", "neck03"]) > 0.5
        self.partes["cabeca"] = sm(["head"] + [b for b in W if b.startswith(("jaw", "special", "levator", "oris", "oculi",
                                                                               "orbicularis", "temporalis", "risorius", "eye", "tongue"))]) > 0.5
        a = me.attributes.new("cavidade", "FLOAT", "POINT")
        a.data.foreach_set("value", self.cavidade.astype(np.float32))

    # ---------------------------------------------------------- cinemática direta própria (sem depsgraph a cada osso)
    def _preparar_fk(self):
        ossos = self.rig.data.bones
        self.ordem = []

        def visita(b):
            self.ordem.append(b.name)
            for c in b.children:
                visita(c)
        for b in ossos:
            if b.parent is None:
                visita(b)
        self.rest = {n: ossos[n].matrix_local.copy() for n in self.ordem}
        self.rest_inv = {n: m.inverted() for n, m in self.rest.items()}
        self.pai = {n: (ossos[n].parent.name if ossos[n].parent else None) for n in self.ordem}
        self.rel = {n: (self.rest_inv[self.pai[n]] @ self.rest[n] if self.pai[n] else self.rest[n].copy()) for n in self.ordem}
        self.comp = {n: ossos[n].length for n in self.ordem}
        self.basis = {n: Matrix.Identity(4) for n in self.ordem}
        self.P = {}
        self._sujo = True
        self._fk()
        L = lambda a, b: (self.cabeca(b) - self.cabeca(a)).length  # noqa: E731
        self.l_coxa = L("upperleg01.L", "lowerleg01.L")
        self.l_canela = L("lowerleg01.L", "foot.L")
        self.l_braco = L("upperarm01.L", "lowerarm01.L")
        self.l_antebraco = L("lowerarm01.L", "wrist.L")
        # frações acumuladas da coluna (centro de cada vértebra) para distribuir curvaturas
        cs = [self.comp[n] for n in COLUNA[1:]]
        tot = sum(cs)
        acc, fr = 0.0, []
        for c in cs:
            fr.append((acc + c / 2) / tot)
            acc += c
        self.frac_coluna = fr
        self.frac_media = sum(f * c for f, c in zip(fr, cs)) / tot

    def _fk(self):
        if not self._sujo:
            return
        P = self.P
        for n in self.ordem:
            p = self.pai[n]
            P[n] = (P[p] @ self.rel[n] if p else self.rel[n]) @ self.basis[n]
        self._sujo = False

    def zerar(self):
        for n in self.ordem:
            self.basis[n] = Matrix.Identity(4)
        self._sujo = True

    def set_rot(self, n, R3):
        """Rotação absoluta do osso (espaço do esqueleto); a cabeça fica onde o pai deixou."""
        self._fk()
        p = self.pai[n]
        base = self.P[p] @ self.rel[n] if p else self.rel[n]
        M = R3.to_4x4()
        M.translation = base.translation
        self.basis[n] = base.inverted() @ M
        self._sujo = True

    def girar(self, n, R3):
        """Aplica a rotação R3 (espaço do esqueleto) à orientação de repouso do osso."""
        self.set_rot(n, R3 @ self.rest[n].to_3x3())

    def apontar(self, n, direcao, ref=None, torcao=0.0):
        dir_rest = ref if ref is not None else (self.rest[n].to_3x3() @ Vector((0, 1, 0))).normalized()
        q = dir_rest.rotation_difference(direcao.normalized())
        if torcao:
            q = Quaternion(direcao.normalized(), math.radians(torcao)) @ q
        self.girar(n, q.to_matrix())

    def set_local(self, n, q):
        self.basis[n] = q.to_matrix().to_4x4()
        self._sujo = True

    def cabeca(self, n):
        self._fk()
        return self.P[n].translation.copy()

    def cauda(self, n):
        self._fk()
        return self.P[n] @ Vector((0, self.comp[n], 0))

    def rot(self, n):
        self._fk()
        return self.P[n].to_3x3()

    def estado(self):
        return {n: m.copy() for n, m in self.basis.items()}

    def restaurar(self, est):
        for n, m in est.items():
            self.basis[n] = m.copy()
        self._sujo = True

    def aplicar(self, T):
        """Escreve a pose calculada no esqueleto do Blender (uma única atualização)."""
        pbs = self.rig.pose.bones
        for n in self.ordem:
            pbs[n].matrix_basis = self.basis[n]
        self.rig.matrix_world = T
        bpy.context.view_layer.update()

    # ---------------------------------------------------------- mãos
    def _preparar_maos(self):
        """Referenciais da mão em repouso (direção dos dedos, polegar, palma) e eixo de flexão de cada falange."""
        self._eixo_dedo = {}
        self.ref_mao = {}
        J = lambda o, c=False: Vector(self.juntas[self.ossos[o]["tail" if c else "head"]])  # noqa: E731
        for sufixo, sx in ((".L", 1), (".R", -1)):
            punho = J("wrist" + sufixo)
            ponta = sum((J(f"finger{f}-1{sufixo}") for f in range(2, 6)), Vector()) / 4
            dmao = (ponta - punho).normalized()
            atravs = (J("finger2-1" + sufixo) - J("finger5-1" + sufixo)).normalized()
            pol = (atravs - dmao * atravs.dot(dmao)).normalized()
            palma = dmao.cross(pol).normalized() * sx
            F = Matrix((dmao, pol, palma)).transposed()
            self.ref_mao[sufixo] = F
            # centro da pegada (onde a barra/halter fica) e centro da palma, no referencial do osso do punho
            f3, f2, f5 = J("finger3-1" + sufixo), J("finger2-1" + sufixo), J("finger5-1" + sufixo)
            peg = punho + (f3 - punho) * 0.62 + palma * 0.22
            Rr = self.rest["wrist" + sufixo].to_3x3()
            self.__dict__.setdefault("off_peg", {})[sufixo] = Rr.inverted() @ (peg - punho)
            for f in range(1, 6):
                for j in range(1, 4):
                    nome = f"finger{f}-{j}{sufixo}"
                    if nome not in self.ossos:
                        continue
                    b = self.rig.data.bones[nome]
                    dir_b = (J(nome, True) - J(nome)).normalized()
                    if f == 1:
                        eixo = palma.cross(dir_b).normalized()
                    else:
                        eixo = atravs * sx
                    self._eixo_dedo[nome] = (b.matrix_local.to_3x3().inverted() @ eixo).normalized()

    # dedos: -1 = espalmados (apoio), 0 = relaxados, 1 = segurando (barra/halter/cabo)
    CURVA = {"plana": ((3, 4, 2), (6, 4, 3)), "rel": ((16, 20, 14), (10, 12, 8)), "peg": ((62, 78, 52), (28, 34, 28))}

    def dedos(self, sufixo, v):
        for f in range(1, 6):
            pol = f == 1
            a, b = (self.CURVA["rel"][pol], self.CURVA["peg"][pol]) if v >= 0 else (self.CURVA["rel"][pol], self.CURVA["plana"][pol])
            w = abs(v)
            for j in range(1, 4):
                nome = f"finger{f}-{j}{sufixo}"
                if nome not in self._eixo_dedo:
                    continue
                ang = a[j - 1] + (b[j - 1] - a[j - 1]) * w
                self.set_local(nome, Quaternion(self._eixo_dedo[nome], math.radians(ang)))

    def rot_mao(self, sufixo, dir_dedos, palma):
        """Rotação absoluta do punho para a mão ter os dedos em 'dir_dedos' e a palma voltada para 'palma' (esqueleto)."""
        hd = dir_dedos.normalized()
        pa = (palma - hd * palma.dot(hd)).normalized()
        sx = 1 if sufixo == ".L" else -1
        th = pa.cross(hd) * sx
        Ft = Matrix((hd, th, pa)).transposed()
        Fr = self.ref_mao[sufixo]
        R = Ft @ Fr.transposed()
        return R @ self.rest["wrist" + sufixo].to_3x3()

    def rot_pegada(self, sufixo, eixo, supinada=False):
        """Mão fechada em volta de uma barra de eixo 'eixo' (esqueleto), punho neutro (alinhado ao antebraço)."""
        sx = 1 if sufixo == ".L" else -1
        f = (self.cabeca("wrist" + sufixo) - self.cabeca("lowerarm01" + sufixo)).normalized()
        th = eixo.normalized() * (sx if supinada else -sx)
        th = th - f * th.dot(f)
        if th.length < 1e-3:
            th = FRENTE - f * FRENTE.dot(f)
        th.normalize()
        palma = f.cross(th) * sx
        return self.rot_mao(sufixo, f, palma)

    def pegada(self, sufixo):
        """Centro da pegada (espaço do esqueleto)."""
        return self.cabeca("wrist" + sufixo) + self.rot("wrist" + sufixo) @ self.off_peg[sufixo]

    def eixo_polegar(self, sufixo):
        R = self.rot("wrist" + sufixo) @ self.rest_inv["wrist" + sufixo].to_3x3()
        return (R @ self.ref_mao[sufixo].col[1]).normalized()

    # ---------------------------------------------------------- representação simplificada (pele) para contatos
    def _preparar_proxy(self):
        n = len(self.verts)
        idx = set(range(0, n, 9))
        for k in ("mao_f", "mao_t", "pe_f", "pe_t"):
            idx |= set(np.where(self.partes[k])[0][::3].tolist())
        idx = np.array(sorted(idx))
        nomes = [b for b in self.ordem if b in self.W]
        Wm = np.stack([self.W[b][idx] for b in nomes], axis=1)
        K = 6
        top = np.argsort(-Wm, axis=1)[:, :K]
        w = np.take_along_axis(Wm, top, axis=1)
        w = w / np.maximum(w.sum(axis=1, keepdims=True), 1e-9)
        self.px_idx = idx
        self.px_nomes = nomes
        self.px_ossos = top
        self.px_w = w
        self.px_rest = np.concatenate([self.verts[idx], np.ones((len(idx), 1))], axis=1)
        self.px_partes = {k: v[idx] for k, v in self.partes.items()}

    def proxy(self, T=None):
        """Pontos da pele (amostra) posados, no espaço do mundo (ou do esqueleto se T é None)."""
        self._fk()
        S = np.array([np.array(self.P[b] @ self.rest_inv[b]) for b in self.px_nomes])
        if T is not None:
            S = np.einsum("ij,bjk->bik", np.array(T), S)
        M = S[self.px_ossos]  # (p, K, 4, 4)
        v = np.einsum("pkij,pj->pki", M[:, :, :3, :], self.px_rest)
        return (v * self.px_w[:, :, None]).sum(axis=1)

    # ---------------------------------------------------------- pose
    def posar(self, p, maos=None):
        """p: pose normalizada (movimento.normalizar) com '_qb' (0..1: quadril apoiado deitado).
        maos: {".L": v, ".R": v} estado dos dedos (-1 apoio, 0 relaxado, 1 pegada)."""
        self.zerar()
        t = p["t"]
        # ---- coluna: curvatura distribuída
        vt = (math.sin(math.radians(t)), -math.cos(math.radians(t)))
        coxa = [(math.sin(math.radians(p[k][0])), -math.cos(math.radians(p[k][0]))) for k in ("pf", "pt")]
        vc = ((coxa[0][0] + coxa[1][0]) / 2, (coxa[0][1] + coxa[1][1]) / 2)
        nc = math.hypot(*vc) or 1.0
        H = math.degrees(math.acos(_clamp((vt[0] * vc[0] + vt[1] * vc[1]) / nc, -1, 1)))
        flex = max(0.0, 95.0 - H) * 0.5  # ritmo lombopélvico: flexão profunda do quadril arredonda a lombar
        P_a = t + flex * self.frac_media
        e = math.degrees(math.asin(_clamp(-math.cos(math.radians(t)), -1, 1)))  # elevação do tronco sobre a horizontal
        w_b = p.get("_qb", 0.0) * mov.suave(e, -20, -5) * (1 - mov.suave(e, 55, 75))
        if w_b > 0:
            P_h = 90.0 if math.sin(math.radians(t)) >= 0 else -90.0
            P_b = P_h + _wrap(t - P_h) * _clamp((e - 30) / 60, 0, 1) * 0.8
            Pp = P_a + _wrap(P_b - P_a) * w_b
        else:
            Pp = P_a
        B = _wrap(t - Pp)
        ang = [Pp] + [Pp + B * f / self.frac_media for f in self.frac_coluna]
        fr_tor = (0.2, 0.32, 0.45, 0.6, 0.8, 1.0)
        fr_inc = (0.1, 0.25, 0.42, 0.6, 0.8, 1.0)
        for n, a, ft, fi in zip(COLUNA, ang, fr_tor, fr_inc):
            self.girar(n, rot_corpo(a, p["inc"] * fi, p["tr"] * ft))
        phi_up = ang[-1]
        # ---- pescoço e cabeça
        rel = _clamp(_wrap(p["c"] - phi_up), -62, 48)
        for n, w in zip(PESCOCO, (0.3, 0.55, 0.8, 1.0)):
            self.girar(n, rot_corpo(phi_up + rel * w, p["inc"] + p["cinc"] * w, p["tr"] + p["cr"] * w))
        R_up = rot_corpo(phi_up, p["inc"], p["tr"])
        up_t, fw_t = R_up @ CIMA, R_up @ FRENTE
        # ---- braços (com cintura escapular)
        dirs = {}
        for lado, sf, s in LADOS:
            b, a = p["b" + lado]
            ab, aa = p["b" + lado + "a"], p["a" + lado + "a"]
            db, da = d2(b, ab, s), d2(a, aa, s)
            dirs[sf] = (db, da)
            elev = math.degrees(math.acos(_clamp(db.dot(-up_t), -1, 1)))
            e_cl = _clamp((elev - 75) / 105, 0, 1) * 20 + p["oe"] * 24
            f = db.dot(fw_t)
            ret = _clamp(-f * 1.4, 0, 1) * 14 - _clamp((f - 0.45) * 1.6, 0, 1) * 7
            cl = "clavicle" + sf
            Ri = self.rest_inv[cl].to_3x3()
            q = Quaternion((Ri @ CIMA).normalized(), math.radians(ret * s)) @ Quaternion((Ri @ FRENTE).normalized(), math.radians(e_cl * s))
            self.set_local(cl, q)
        for lado, sf, s in LADOS:
            db, da = dirs[sf]
            for n in ("upperarm01", "upperarm02"):
                self.apontar(n + sf, db)
            for n in ("lowerarm01", "lowerarm02"):
                self.apontar(n + sf, da)
            self.apontar("wrist" + sf, da)
            # ---- pernas
            c_, sh, pe = p["p" + lado]
            pa = p["p" + lado + "a"]
            for n in ("upperleg01", "upperleg02"):
                self.apontar(n + sf, d2(c_, pa, s))
            for n in ("lowerleg01", "lowerleg02"):
                self.apontar(n + sf, d2(sh, pa, s))
            # o osso do pé aponta ~27° para baixo com o pé apoiado (pe = 90)
            self.apontar("foot" + sf, d2(pe - 27, pa * 0.3, s))
            self.dedos(sf, (maos or {}).get(sf, 0.0))

    # ---------------------------------------------------------- IK de 2 ossos (espaço do esqueleto)
    def ik(self, membro, sf, alvo, rot_fim=None):
        """Leva a cabeça do osso final (tornozelo/punho) até 'alvo', mantendo o plano de flexão natural.
        rot_fim: rotação absoluta do pé/punho; se None, o pé/punho acompanha o segmento distal."""
        if membro == "perna":
            b1, b2, fim, l1, l2 = ("upperleg01", "upperleg02"), ("lowerleg01", "lowerleg02"), "foot", self.l_coxa, self.l_canela
        else:
            b1, b2, fim, l1, l2 = ("upperarm01", "upperarm02"), ("lowerarm01", "lowerarm02"), "wrist", self.l_braco, self.l_antebraco
        S, E, W = self.cabeca(b1[0] + sf), self.cabeca(b2[0] + sf), self.cabeca(fim + sf)
        R_fim_antes = self.rot(fim + sf)
        dist_antes = (W - E).normalized()
        v = alvo - S
        dv = max(v.length, 1e-6)
        u = v / dv
        d = _clamp(dv, abs(l1 - l2) + 1e-3, (l1 + l2) * 0.9995)
        n = (E - S).cross(W - S)
        if n.length < 1e-3 * l1 * l2:
            s = 1 if sf == ".L" else -1
            polo = FRENTE.copy() if membro == "perna" else (-FRENTE + ESQ * s * 0.5 - CIMA * 0.3)
            perp = polo - u * polo.dot(u)
        else:
            perp = n.normalized().cross(u)
            if perp.dot(E - S) < 0:
                perp = -perp
        if perp.length < 1e-6:
            perp = Vector((0, 0, 1)) - u * u.z
        perp.normalize()
        a = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
        hh = math.sqrt(max(l1 * l1 - a * a, 0.0))
        E2 = S + u * a + perp * hh
        W2 = S + u * d
        for nb in b1:
            self.apontar(nb + sf, E2 - S)
        for nb in b2:
            self.apontar(nb + sf, W2 - E2)
        if rot_fim is not None:
            self.set_rot(fim + sf, rot_fim)
        else:
            q = dist_antes.rotation_difference((W2 - E2).normalized())
            self.set_rot(fim + sf, q.to_matrix() @ R_fim_antes)

    def junta_mundo(self, nome, T, cauda=False):
        return T @ (self.cauda(nome) if cauda else self.cabeca(nome))


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
    R["pescoco"] = np.clip((pesc - 0.4) * 2, 0, 1)
    # short: bainha levemente mais baixa atrás, cintura reta
    yb = np.clip(V[:, 1], -1, 1)
    lo, hi = hipz - 1.2 + 0.12 * yb, hipz + 0.92
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

AZ_LUZES = 64.0


def cena(tam, amostras):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = amostras
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.02
    sc.cycles.adaptive_min_samples = max(4, amostras // 4)
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = "OPENIMAGEDENOISE"
    sc.cycles.denoising_input_passes = "RGB_ALBEDO_NORMAL"
    sc.cycles.denoising_prefilter = "ACCURATE"
    try:
        sc.cycles.denoising_quality = "BALANCED"
    except (AttributeError, TypeError):
        pass
    sc.cycles.max_bounces = 4
    sc.cycles.diffuse_bounces = 2
    sc.cycles.glossy_bounces = 2
    sc.cycles.transmission_bounces = 0
    sc.cycles.volume_bounces = 0
    sc.cycles.transparent_max_bounces = 2
    sc.cycles.caustics_reflective = False
    sc.cycles.caustics_refractive = False
    sc.cycles.blur_glossy = 1.0
    sc.render.use_persistent_data = True
    sc.render.resolution_x = tam
    sc.render.resolution_y = tam
    sc.render.film_transparent = True
    sc.render.filter_size = 1.2
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_depth = "16"
    sc.render.image_settings.color_mode = "RGBA"
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    sc.render.dither_intensity = 0.0  # o pontilhado é aplicado depois, na composição com o fundo
    world = bpy.data.worlds.new("mundo")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.05, 0.045, 0.04, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.6
    sc.world = world
    # chão que só recebe sombra: um disco do tamanho da cena (redimensionado em cada animação; o resto é fundo, barato)
    bpy.ops.mesh.primitive_circle_add(vertices=48, radius=1.0, fill_type="NGON", location=(0, 0, 0))
    chao = bpy.context.active_object
    chao.name = "chao"
    chao.is_shadow_catcher = True
    luzes = []

    def luz(nome, loc, energia, tam_luz, cor=(1, 1, 1)):
        l = bpy.data.lights.new(nome, "AREA")
        l.energy = energia; l.size = tam_luz; l.color = cor
        o = bpy.data.objects.new(nome, l)
        o["loc0"] = loc
        sc.collection.objects.link(o)
        luzes.append(o)
    # chave bem lateral em relação à câmera (azimute ~64°) para revelar o relevo; preenchimento suave do lado da câmera
    luz("chave", (-6, -26, 24), 9000, 3.5)
    luz("preenchimento", (26, -6, 10), 1500, 18, (0.9, 0.95, 1.0))
    luz("recorte", (8, 24, 20), 7000, 4, (1.0, 0.82, 0.66))
    cam = bpy.data.cameras.new("cam")
    cam.type = "ORTHO"
    co = bpy.data.objects.new("cam", cam)
    sc.collection.objects.link(co)
    sc.camera = co
    co["luzes"] = [l.name for l in luzes]
    return co


def azimute_de_cam(cam):
    """Campo "cam" (64 = 3/4 atual, 90 = de frente, 0 = perfil) -> azimute interno (0 = câmera de frente para o rosto)."""
    c = float(cam)
    if c <= 0:
        return 90.0 - c
    if c <= 64:
        return 90.0 - c * 26.0 / 64.0
    if c <= 90:
        return 64.0 - (c - 64.0) * 64.0 / 26.0
    return -(c - 90.0)


def base_camera(azimute, elevacao=10.0):
    az, el = math.radians(azimute), math.radians(elevacao)
    dirc = (FRENTE * math.cos(az) + ESQ * math.sin(az)) * math.cos(el) + CIMA * math.sin(el)
    olhar = -dirc
    direita = olhar.cross(CIMA).normalized()
    cima = direita.cross(olhar).normalized()
    return dirc, direita, cima


def enquadrar(co, pts, azimute, margem=0.07, elevacao=10.0):
    """Câmera ortográfica que mostra todos os pontos (corpo em todos os quadros + aparelhos) com margem."""
    dirc, direita, cima = base_camera(azimute, elevacao)
    P = np.asarray(pts)
    u = P @ np.array(direita)
    v = P @ np.array(cima)
    w = P @ np.array(dirc)
    u0, u1, v0, v1 = u.min(), u.max(), v.min(), v.max()
    lado = max(u1 - u0, v1 - v0) * (1 + 2 * margem) + 0.6
    uc, vc = (u0 + u1) / 2, (v0 + v1) / 2
    # pés perto da parte de baixo do quadro, mas com folga para a sombra
    vc = max(vc, v0 - lado * margem * 0.6 + lado / 2 - lado * (margem + 0.04)) if (v1 - v0) < (u1 - u0) else vc
    centro = direita * uc + cima * vc + dirc * float(w.mean())
    co.location = centro + dirc * 80
    co.rotation_euler = (-dirc).to_track_quat("-Z", "Y").to_euler()
    co.data.ortho_scale = lado
    co.data.clip_end = 300
    # as luzes giram junto com a câmera (mesmo desenho de luz em qualquer vista)
    giro = Matrix.Rotation(math.radians(azimute - AZ_LUZES), 3, "Z")
    alvo = Vector((centro.x, centro.y, 9))
    for nome in co["luzes"]:
        o = bpy.data.objects[nome]
        loc = giro @ Vector(o["loc0"]) + Vector((centro.x, centro.y, 0))
        o.location = loc
        o.rotation_euler = (alvo - loc).to_track_quat("-Z", "Y").to_euler()


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
    ao.samples = 4
    ao.only_local = True
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


# ------------------------------------------------------------------ animação

class Contexto:
    """Dados de uma animação compartilhados entre quadros: escala 2D->3D, referência, superfícies de apoio."""

    def __init__(self, h, anim, k, grupo):
        self.h, self.anim, self.k = h, anim, k
        self.id = anim["id"]
        self.props = anim.get("props", [])
        tipos = {pr.get("tipo") for pr in self.props}
        self.tipos = tipos
        self.z0 = 0.0
        if "esteira" in tipos:
            self.z0 = aparelhos.ALTURA_ESTEIRA
        elif "tapete" in tipos:
            self.z0 = aparelhos.ALTURA_TAPETE
        self.props_maos = any(pr.get("em") == "maos" or pr.get("de") == "maos" for pr in self.props)
        self.barra = None
        for pr in self.props:
            if pr.get("tipo") == "barra_fixa":
                self.barra = (pr.get("x", 0), pr.get("y", 21))
        self.paralelas = self.barra is not None and "paralela" in self.id
        self.barra_livre = "barra" in tipos  # barra olímpica nas mãos
        self.supinada = any(s in self.id for s in ("supinad", "rosca", "chin"))
        self.ref = {"k": k}
        self.grupo = grupo
        self.planta = "esteira" not in tipos and "bike" not in tipos

    def p3(self, x2, y2, z2=0.0):
        """Ponto 2D da animação (x para frente, y para cima; z opcional = para o lado da câmera) em 3D,
        com o quadril do 1º quadro como referência."""
        hx2, h3 = self.ref["quad"]
        return Vector((0, h3.y, 0)) + FRENTE * ((x2 - hx2) * self.k) + CIMA * (y2 * self.k) + ESQ * (z2 * self.k)

    def superficies(self):
        """(xmin, xmax, ymin, ymax, z topo) no mundo: chão + topo de bancos/caixas/máquinas."""
        if hasattr(self, "_sup"):
            return self._sup
        sup = [(-1e9, 1e9, -1e9, 1e9, self.z0)]
        for pr in self.props:
            if pr.get("tipo") in ("banco", "caixa", "maquina"):
                x, w, y, hh = pr.get("x", 0), pr.get("w", 8), pr.get("y", 0), pr.get("h", 4)
                a, b = self.p3(x, 0), self.p3(x + w, 0)
                sup.append((-3.2, 3.2, min(a.y, b.y) - 0.3, max(a.y, b.y) + 0.3, (y + hh) * self.k))
        self._sup = sup
        return sup

    def superficie_em(self, p, abaixo_de=None):
        """Altura da superfície mais alta sob o ponto p (que não esteja muito acima dele)."""
        z = self.z0
        lim = (abaixo_de if abaixo_de is not None else p[2]) + 0.6
        for x0, x1, y0, y1, zt in self.superficies():
            if x0 <= p[0] <= x1 and y0 <= p[1] <= y1 and zt <= lim:
                z = max(z, zt)
        return z


def _rot_eixo(piv, eixo, ang):
    piv = Vector(piv)
    return Matrix.Translation(piv) @ Matrix.Rotation(ang, 4, eixo) @ Matrix.Translation(-piv)


def _quadril_baixo(p2):
    return 1.0 - mov.suave(p2["quadril"][1], 1.6, 2.6)


def _pose2d(q):
    """Pose 2D (para esqueleto.pontos) a partir da pose normalizada."""
    return {"x": q["x"], "y": q["y"], "ay": q["ay"], "t": q["t"], "c": q["c"], "bf": q["bf"], "bt": q["bt"], "pf": q["pf"], "pt": q["pt"]}


EFETORES = (("pe_f", "perna", ".L"), ("pe_t", "perna", ".R"), ("mao_f", "braco", ".L"), ("mao_t", "braco", ".R"))


def _fim(membro, sf):
    return ("foot" if membro == "perna" else "wrist") + sf


def info_efetor(h, ctx, T, ef, membro, sf, P=None):
    """Posição/rotação no mundo do tornozelo/punho e o ponto mais baixo da pele do pé/mão."""
    P = h.proxy(T) if P is None else P
    m = h.px_partes[ef]
    pts = P[m]
    zmin = pts[:, 2].min()
    baixo = pts[pts[:, 2] < zmin + 0.12].mean(axis=0)
    fim = _fim(membro, sf)
    Tq = T.to_3x3()
    return {"pos": T @ h.cabeca(fim), "rot": (Tq @ h.rot(fim)).to_quaternion(), "baixo": Vector(baixo), "zmin": float(zmin)}


def mao_apoiada_rot(h, T, sf):
    """Rotação (esqueleto) do punho para a mão espalmada no apoio: palma para baixo, dedos à frente (ou seguindo o antebraço deitado)."""
    s = 1 if sf == ".L" else -1
    Ti = T.to_3x3().inverted()
    Tq = T.to_3x3()
    fwd = Tq @ FRENTE
    fwd.z = 0
    lat = Tq @ ESQ
    lat.z = 0
    if fwd.length < 1e-3:
        fwd = Vector((0, -1, 0))
    fwd.normalize()
    base = (fwd + lat.normalized() * s * 0.3).normalized() if lat.length > 1e-3 else fwd
    ante = Tq @ (h.cabeca("wrist" + sf) - h.cabeca("lowerarm01" + sf)).normalized()
    ah = Vector((ante.x, ante.y, 0))
    w = mov.suave(abs(ante.z), 0.45, 0.8)
    if ah.length > 1e-3:
        hd = (ah.normalized() * (1 - w) + base * w).normalized()
    else:
        hd = base
    return h.rot_mao(sf, Ti @ hd, Ti @ Vector((0, 0, -1)))


def estado_maos(ctx, apoio):
    v = {}
    for lado, sf, _ in LADOS:
        if apoio.get(lado):
            v[sf] = -1.0
        elif ctx.props_maos or ctx.barra is not None:
            v[sf] = 1.0
        else:
            v[sf] = 0.0
    return v


def apoios_2d(ctx, p2):
    """Mãos espalmadas: no chão ou em cima de banco/caixa (pelo esqueleto 2D)."""
    tops = [(-1e9, 1e9, 0.0)]
    for pr in ctx.props:
        if pr.get("tipo") in ("banco", "caixa", "maquina"):
            x, w = pr.get("x", 0), pr.get("w", 8)
            tops.append((x - 0.5, x + w + 0.5, pr.get("y", 0) + pr.get("h", 4)))
    out = {}
    for lado in ("f", "t"):
        mx, my = p2["mao_" + lado]
        perto_barra = ctx.barra is not None and math.dist((mx, my), ctx.barra) < 1.6
        out[lado] = (not ctx.props_maos and not perto_barra and any(x0 <= mx <= x1 and abs(my - top) < 0.45 for x0, x1, top in tops))
    return out


def colocar_chave(h, ctx, q):
    """Posa um quadro-chave e coloca o corpo no mundo, corrigindo a diferença de proporções entre o esqueleto 2D e o
    humano 3D: dois apoios no chão -> o corpo gira até os dois tocarem; "fixo" -> o ponto fixo fica parado no mundo 3D;
    barra fixa -> mãos na barra. Devolve (T, maos, extras)."""
    anim, k, ref = ctx.anim, ctx.k, ctx.ref
    p2 = pontos_anim(anim, _pose2d(q))
    apoio = apoios_2d(ctx, p2)
    q = dict(q)
    q["_qb"] = _quadril_baixo(p2)
    maos = estado_maos(ctx, apoio)
    h.posar(q, maos)
    T = Matrix.Identity(4)
    root0 = h.cabeca("root")
    if abs(q["rol"]) > 0.01:
        T = _rot_eixo(root0, FRENTE, math.radians(q["rol"])) @ T
    pts = h.proxy(T)
    # 1) dois apoios no chão -> nivelar (só com o corpo no plano sagital)
    sup = []
    if abs(q["rol"]) < 20 and q["y"] is None:
        for nome2, parte in (("mao_f", "mao_f"), ("mao_t", "mao_t"), ("ponta_f", "pe_f"), ("calcanhar_f", "pe_f"), ("ponta_t", "pe_t"),
                             ("calcanhar_t", "pe_t"), ("joelho_f", "joelho_f"), ("joelho_t", "joelho_t")):
            if p2[nome2][1] < 0.35:
                sup.append((p2[nome2][0], parte))
    if sup:
        xs = [x for x, _ in sup]
        if max(xs) - min(xs) > 2.5:
            frente = {pt for x, pt in sup if x > max(xs) - 1.2}
            tras = {pt for x, pt in sup if x < min(xs) + 1.2}
            for _ in range(2):
                P = h.proxy(T)

                def baixo(partes):
                    m = np.zeros(len(P), bool)
                    for pt in partes:
                        m |= h.px_partes[pt]
                    idx = np.where(m)[0]
                    return P[idx[np.argmin(P[idx, 2])]]
                a, b = baixo(frente), baixo(tras)
                ang = math.atan2(b[2] - a[2], b[1] - a[1])
                alvo = 0.0 if abs(ang) < math.pi / 2 else math.copysign(math.pi, ang)
                giro = max(-0.45, min(0.45, alvo - ang))
                T = _rot_eixo(a, Vector((1, 0, 0)), giro) @ T
    # 2) horizontal
    fixo = anim.get("fixo")
    chave3 = None
    if fixo == "maos":
        chave3 = lambda TT: TT @ h.pegada(".L")  # noqa: E731
    elif fixo == "pes":
        chave3 = lambda TT: TT @ h.cabeca("foot.L")  # noqa: E731
    quad3 = T @ h.cabeca("root")
    if chave3 is not None and "ancora" in ref:
        dy = ref["ancora"] - chave3(T).y
    elif "quad" in ref:
        dy = ref["quad"][1].y + (-(p2["quadril"][0] - ref["quad"][0])) * k - quad3.y
    else:
        dy = 0.0
    T = Matrix.Translation((0, dy, 0)) @ T
    # 3) vertical
    if q["y"] is not None:
        dz = p2["quadril"][1] * k - (T @ h.cabeca("root")).z
    else:
        dz = ctx.z0 - h.proxy(T)[:, 2].min() + q["ay"] * k
    T = Matrix.Translation((0, 0, dz)) @ T
    if q["y"] is not None:
        zmin = h.proxy(T)[:, 2].min()
        if zmin < ctx.z0:
            T = Matrix.Translation((0, 0, ctx.z0 - zmin)) @ T  # altura dada não pode enterrar joelhos/pés
    if q["z"]:
        T = Matrix.Translation(ESQ * (q["z"] * k)) @ T  # deslocamento lateral (+ = lado da câmera)
    # 4) barra fixa: mãos na barra
    if ctx.barra is not None and "barra3" in ref and math.dist(p2["mao_f"], ctx.barra) < 1.6:
        g = (T @ h.pegada(".L") + T @ h.pegada(".R")) / 2
        b3 = ref["barra3"]
        pes_chao = min(p2["ponta_f"][1], p2["calcanhar_f"][1]) < 0.35 and q["y"] is None
        if pes_chao:
            piv = T @ h.cabeca("foot.L")
            r = math.hypot(g.y - piv.y, g.z - piv.z)
            if r > 1e-3 and abs(b3.z - piv.z) < r:
                ang_g = math.atan2(g.z - piv.z, g.y - piv.y)
                alvo = math.asin((b3.z - piv.z) / r)
                alvo = alvo if math.cos(ang_g) >= 0 else math.pi - alvo
                dd = (alvo - ang_g + math.pi) % (2 * math.pi) - math.pi
                T = _rot_eixo(piv, Vector((1, 0, 0)), max(-0.5, min(0.5, dd))) @ T
        elif not ctx.paralelas:
            T = Matrix.Translation((0, b3.y - g.y, b3.z - g.z)) @ T
        else:
            T = Matrix.Translation((0, 0, b3.z - g.z)) @ T
        segurar_barra(h, ctx, T)
    if chave3 is not None and "ancora" not in ref:
        ref["ancora"] = chave3(T).y
    if "quad" not in ref:
        ref["quad"] = (p2["quadril"][0], T @ h.cabeca("root"))
    # 5) deitado de costas sobre banco: as costas encostam no estofado (o 2D não conhece a espessura do corpo 3D)
    T = repousar(h, ctx, T, q)
    # 6) mãos espalmadas no apoio + encaixe fino de pés/mãos na superfície
    for lado, sf, _ in LADOS:
        if apoio[lado]:
            h.set_rot("wrist" + sf, mao_apoiada_rot(h, T, sf))
    encaixar(h, ctx, T, apoio)
    return T, maos, {"apoio": apoio, "p2": p2}


def repousar(h, ctx, T, q):
    t = math.radians(q["t"])
    supino = -math.sin(t) > 0.75 and abs(q["rol"]) < 30
    if not supino:
        return T
    P = h.proxy(T)
    Q = P[h.px_partes["tronco"]]
    melhor = None
    for x0, x1, y0, y1, zt in ctx.superficies()[1:]:
        m = (Q[:, 0] >= x0) & (Q[:, 0] <= x1) & (Q[:, 1] >= y0) & (Q[:, 1] <= y1)
        if m.sum() < 20:
            continue
        gap = Q[m, 2].min() - zt
        if -1.0 < gap < 1.8 and (melhor is None or abs(gap) < abs(melhor)):
            melhor = gap
    if melhor is None or abs(melhor) < 0.03:
        return T
    return Matrix.Translation((0, 0, -melhor)) @ T


def segurar_barra(h, ctx, T):
    """IK: cada mão alcança a barra fixa (ou as paralelas) com a pegada fechada em volta dela."""
    b3 = ctx.ref["barra3"]
    Ti = T.inverted()
    for _ in range(2):
        for sf in (".L", ".R"):
            g = T @ h.pegada(sf)
            if ctx.paralelas:
                alvo_m = Vector((g.x, g.y, b3.z))
                eixo = Ti.to_3x3() @ Vector((0, 1, 0))
            else:
                alvo_m = Vector((g.x, b3.y, b3.z))
                eixo = Ti.to_3x3() @ Vector((1, 0, 0))
            R = h.rot_pegada(sf, eixo, ctx.supinada and not ctx.paralelas)
            alvo = Ti @ alvo_m - R @ h.off_peg[sf]
            h.ik("braco", sf, alvo, R)


def encaixar(h, ctx, T, apoio):
    """Pés e mãos que quase tocam uma superfície passam a tocá-la exatamente (IK), sem atravessar."""
    Ti = T.inverted()
    P = h.proxy(T)
    for ef, membro, sf in EFETORES:
        lado = ef[-1]
        if membro == "braco" and not apoio.get(lado):
            continue
        pts = P[h.px_partes[ef]]
        zmin = pts[:, 2].min()
        baixo = pts[pts[:, 2] < zmin + 0.12].mean(axis=0)
        zs = ctx.superficie_em(baixo, zmin)
        gap = zmin - zs
        if membro == "perna" and not (-2.0 < gap < 0.45):
            continue
        if abs(gap) < 0.01:
            continue
        fim = _fim(membro, sf)
        alvo = T @ h.cabeca(fim) - Vector((0, 0, gap))
        h.ik(membro, sf, Ti @ alvo, h.rot(fim))
        P = h.proxy(T)


def efetores_chave(h, ctx, T, apoio):
    """Estado de cada pé/mão num quadro-chave: posição/rotação e se está apoiado (chão, banco, barra)."""
    P = h.proxy(T)
    out = {}
    for ef, membro, sf in EFETORES:
        inf = info_efetor(h, ctx, T, ef, membro, sf, P)
        zs = ctx.superficie_em(inf["baixo"], inf["zmin"])
        contato = inf["zmin"] - zs < 0.3
        if membro == "braco":
            if ctx.barra is not None and "barra3" in ctx.ref:
                g = T @ h.pegada(sf)
                b3 = ctx.ref["barra3"]
                d = abs(g.z - b3.z) + (0 if ctx.paralelas else abs(g.y - b3.y))
                if d < 0.5:
                    contato = True
            elif ctx.props_maos:
                contato = False
            else:
                contato = contato and apoio.get(ef[-1], False)
        inf["contato"] = contato and ctx.planta
        out[ef] = inf
    return out


def _slerp(qa, qb, t):
    return qa.slerp(qb, t)


def plantar(h, ctx, T, chaves, i, j, u):
    """Mantém parados no mundo os pés/mãos apoiados nos dois quadros-chave vizinhos (IK); na saída/chegada do apoio
    o membro descola/pousa suavemente. Devolve os efetores plantados (peso 1)."""
    Ti = T.inverted()
    Tq = T.to_3x3()
    Tqi = Tq.inverted()
    fixos = set()
    ea, eb = chaves[i]["ef"], chaves[j]["ef"]
    for ef, membro, sf in EFETORES:
        a, b = ea[ef], eb[ef]
        if a["contato"] and b["contato"] and (a["baixo"] - b["baixo"]).length < 1.6:
            w = 1.0
            s = mov.suave(u)
            pos = a["pos"].lerp(b["pos"], s)
            rot = _slerp(a["rot"], b["rot"], s)
        elif a["contato"]:
            w = 1.0 - mov.suave(u, 0.0, 0.45)
            pos, rot = a["pos"], a["rot"]
        elif b["contato"]:
            w = mov.suave(u, 0.55, 1.0)
            pos, rot = b["pos"], b["rot"]
        else:
            continue
        if w <= 1e-3:
            continue
        fim = _fim(membro, sf)
        atual_p = T @ h.cabeca(fim)
        atual_r = (Tq @ h.rot(fim)).to_quaternion()
        alvo_p = atual_p.lerp(pos, w)
        alvo_r = _slerp(atual_r, rot, w)
        h.ik(membro, sf, Ti @ alvo_p, Tqi @ alvo_r.to_matrix())
        if w > 0.999:
            fixos.add(ef)
    return fixos


def sem_atravessar(h, ctx, T, fixos):
    """Pés/mãos livres não entram no chão/banco (IK levanta o membro); o corpo não atravessa o chão."""
    Ti = T.inverted()
    P = h.proxy(T)
    for ef, membro, sf in EFETORES:
        if ef in fixos:
            continue
        pts = P[h.px_partes[ef]]
        zmin = pts[:, 2].min()
        baixo = pts[pts[:, 2] < zmin + 0.12].mean(axis=0)
        zs = ctx.superficie_em(baixo, zmin + 0.25)
        gap = zmin - zs
        if gap < -0.005 and gap > -1.5:
            fim = _fim(membro, sf)
            alvo = T @ h.cabeca(fim) - Vector((0, 0, gap))
            h.ik(membro, sf, Ti @ alvo, h.rot(fim))
            P = h.proxy(T)
    zmin = P[:, 2].min()
    if zmin < ctx.z0 - 0.01:
        return Matrix.Translation((0, 0, ctx.z0 - zmin)) @ T
    return T


def dedos_pes(h, ctx, T):
    """Dedos do pé ficam no chão quando o calcanhar sobe (meia-ponta)."""
    Ti3 = T.to_3x3().inverted()
    Tq = T.to_3x3()
    for sf in (".L", ".R"):
        for f in range(1, 6):
            n = f"toe{f}-1{sf}"
            if n not in h.basis:
                continue
            cab = T @ h.cabeca(n)
            if cab.z - ctx.superficie_em(cab) > 0.35:
                continue
            d = Tq @ (h.cauda(n) - h.cabeca(n)).normalized()
            if d.z < -0.05:
                dh = Vector((d.x, d.y, 0.0))
                if dh.length > 1e-3:
                    h.apontar(n, Ti3 @ dh.normalized())


def corrigir_barra(h, ctx, T):
    """Barra olímpica: nas costas/no peito quando as mãos estão perto dos ombros; nunca atravessa o corpo nem o chão.
    Devolve o centro e o eixo da barra no mundo (as mãos são levadas até ela por IK)."""
    Ti = T.inverted()
    gL, gR = T @ h.pegada(".L"), T @ h.pegada(".R")
    centro = (gL + gR) / 2
    eixo = (gL - gR)
    if eixo.length < 1e-3:
        eixo = T.to_3x3() @ ESQ
    eixo.normalize()
    Tq = T.to_3x3()
    R_up = h.rot("spine01") @ h.rest_inv["spine01"].to_3x3()
    up_t = (Tq @ (R_up @ CIMA)).normalized()
    fw_t = (Tq @ (R_up @ FRENTE)).normalized()
    pesc = T @ h.cabeca("neck01")
    rel = centro - pesc
    meia = max(2.4, min(4.6, ((gL - gR).length) / 2))
    mudou = False
    if rel.length < 3.2 and rel.dot(up_t) > -2.4:
        if not any(x in ctx.id for x in ("front", "frontal", "clean", "zercher")):
            centro = pesc - fw_t * 0.95 - up_t * 0.55  # agachamento com barra nas costas (sobre o trapézio)
        else:
            centro = pesc + fw_t * 1.05 - up_t * 0.55  # barra apoiada nos deltoides (frente)
        eixo = (Tq @ ESQ).normalized()
        meia = 3.7
        mudou = True
    # não atravessar o corpo
    P = h.proxy(T)
    m = ~(h.px_partes["mao_f"] | h.px_partes["mao_t"] | h.px_partes["antebraco_f"] | h.px_partes["antebraco_t"])
    Q = P[m]
    c = np.array(centro)
    ax = np.array(eixo)
    rel_p = Q - c
    s = rel_p @ ax
    perto = np.abs(s) < 2.6
    if perto.any():
        radial = rel_p[perto] - np.outer(s[perto], ax)
        dist = np.linalg.norm(radial, axis=1)
        i = int(np.argmin(dist))
        folga = 0.42
        if dist[i] < folga:
            dirp = -radial[i] / max(dist[i], 1e-6)
            if dist[i] < 1e-4:
                dirp = np.array(fw_t)
            # empurra na direção de "sair do corpo": média das normais locais aproximadas
            centro = centro + Vector(dirp) * (folga - dist[i])
            mudou = True
    R = aparelhos.raio_anilha(ctx)
    zmin = ctx.z0 + R
    if centro.z < zmin:
        centro.z = zmin
        mudou = True
    if mudou:
        for _ in range(2):
            for sf, sx in ((".L", 1), (".R", -1)):
                alvo_m = centro + eixo * (meia * sx)
                Rh = h.rot_pegada(sf, Ti.to_3x3() @ eixo, ctx.supinada)
                h.ik("braco", sf, Ti @ alvo_m - Rh @ h.off_peg[sf], Rh)
        return centro, eixo
    for sf in (".L", ".R"):
        Rh = h.rot_pegada(sf, Ti.to_3x3() @ eixo, ctx.supinada)
        g_antes = h.pegada(sf)
        h.set_rot("wrist" + sf, Rh)
        # mantém a pegada no mesmo ponto
        h.ik("braco", sf, h.cabeca("wrist" + sf) + (g_antes - h.pegada(sf)), Rh)
    gL, gR = T @ h.pegada(".L"), T @ h.pegada(".R")
    return (gL + gR) / 2, (gL - gR).normalized() if (gL - gR).length > 1e-3 else eixo


def preparar_anim(h, anim, k, grupo):
    ctx = Contexto(h, anim, k, grupo)
    if grupo == "Trapézio" and not any("oe" in q for q in anim["quadros"]):
        for i_q, q in enumerate(anim["quadros"]):
            q["oe"] = 0 if i_q == 0 else 1
    if anim["id"].startswith("band-pull-apart") and not anim.get("props"):
        anim["props"] = [{"tipo": "elastico", "de": "maos", "ate": "maos"}]
        ctx = Contexto(h, anim, k, grupo)
    trilhas = mov.TrilhasPose(anim["quadros"], anim.get("tempos"))
    ctx.trilhas = trilhas
    # referência (quadro 0)
    colocar_chave(h, ctx, trilhas.chaves[0])
    if ctx.barra is not None:
        ctx.ref["barra3"] = ctx.p3(*ctx.barra)
    chaves = []
    for q in trilhas.chaves:
        T, maos, ext = colocar_chave(h, ctx, q)
        ef = efetores_chave(h, ctx, T, ext["apoio"])
        pos = T @ h.cabeca("root")
        chaves.append({"T": T, "maos": maos, "apoio": ext["apoio"], "ef": ef, "est": h.estado(), "pos": pos, "rot": T.to_quaternion(),
                       "q": q})
    ctx.chaves = chaves
    root0 = h.rest["root"].translation.copy()
    ctx.root0 = root0
    # trilha do corpo inteiro: posição do quadril (cabeça do osso root) e rotação
    ctx.rigido = mov.TrilhaRigida(trilhas.tempos, [list(c["pos"]) for c in chaves],
                                  [list(c["rot"]) for c in chaves])
    aparelhos.preparar(ctx, h)
    return ctx


def quadro(h, ctx, tau):
    """Calcula a pose completa (ossos + posição no mundo) no instante tau. Devolve um dicionário de estado."""
    tr = ctx.trilhas
    i, u = tr.segmento(tau)
    n = len(ctx.chaves)
    j = (i + 1) % n
    q = tr(tau)
    p2 = pontos(_pose2d(q))
    q["_qb"] = _quadril_baixo(p2)
    ca, cb = ctx.chaves[i], ctx.chaves[j]
    maos = {sf: _lerp(ca["maos"][sf], cb["maos"][sf], mov.suave(u)) for sf in (".L", ".R")}
    h.posar(q, maos)
    pos, rq = ctx.rigido(tau)
    R = Quaternion(rq).to_matrix().to_4x4()
    T = Matrix.Translation(_v(pos)) @ R @ Matrix.Translation(-ctx.root0)
    # mãos espalmadas: orientação da mão segue as chaves
    for lado, sf, _ in LADOS:
        wa = 1.0 if ca["apoio"][lado] else 0.0
        wb = 1.0 if cb["apoio"][lado] else 0.0
        w = _lerp(wa, wb, mov.suave(u))
        if w > 1e-3:
            Ra = h.rot("wrist" + sf).to_quaternion()
            Rb = mao_apoiada_rot(h, T, sf).to_quaternion()
            h.set_rot("wrist" + sf, Ra.slerp(Rb, w).to_matrix())
    return finalizar(h, ctx, T, tau, (i, j, u), maos)


def finalizar(h, ctx, T, tau, seg, maos):
    extras = {}
    aparelhos.antes_ik(ctx, h, T, tau, extras)
    fixos = set()
    if seg is not None:
        i, j, u = seg
        fixos = plantar(h, ctx, T, ctx.chaves, i, j, u)
        if ctx.barra is not None and "barra3" in ctx.ref and all(ctx.chaves[x]["ef"]["mao_f"]["contato"] for x in (i, j)):
            segurar_barra(h, ctx, T)
    for _ in range(2):
        T2 = sem_atravessar(h, ctx, T, fixos | extras.get("fixos", set()))
        if T2 is T:
            break
        T = T2
        if seg is not None:
            plantar(h, ctx, T, ctx.chaves, *seg)
    if seg is not None:
        i, j, u = seg
        ka, kb = ctx.chaves[i]["q"], ctx.chaves[j]["q"]
        livre = (ka["y"] is None and kb["y"] is None and ka["ay"] == 0 and kb["ay"] == 0 and not fixos
                 and not extras.get("fixos"))
        if livre:
            zmin = h.proxy(T)[:, 2].min()
            T = Matrix.Translation((0, 0, ctx.z0 - zmin)) @ T
    if ctx.barra_livre:
        extras["barra"] = corrigir_barra(h, ctx, T)
    dedos_pes(h, ctx, T)
    return {"T": T.copy(), "est": h.estado(), "tau": tau, "extras": extras}


def quadro_chave(h, ctx, i):
    c = ctx.chaves[i]
    h.restaurar(c["est"])
    tau = float(ctx.trilhas.t0[i])
    return finalizar(h, ctx, c["T"], tau, None, c["maos"])


# ------------------------------------------------------------------ imagem e vídeo

def fundo(tam):
    """Fundo em ponto flutuante (0..1): degradê quente com halo atrás do corpo."""
    yy = np.linspace(0, 1, tam)[:, None]
    base = np.array([27, 24, 21]) - np.array([13, 11, 9]) * yy[..., None]
    img = np.broadcast_to(base, (tam, tam, 3)).astype(np.float64) / 255.0
    X, Y = np.meshgrid(np.linspace(0, 1, tam), np.linspace(0, 1, tam))
    d = ((X - 0.5) / 0.42) ** 2 + ((Y - 0.36) / 0.42) ** 2
    halo = np.exp(-d * 1.6)[..., None] * (40 / 255.0)
    luz = np.array([255, 190, 140]) / 255.0
    return img * (1 - halo) + luz * halo


def compor(png, bg, rng):
    """RGBA 16 bits sobre o fundo, com pontilhado triangular (evita degraus no degradê e nas sombras)."""
    from PIL import Image
    im = np.array(Image.open(png)).astype(np.float64)
    if im.max() > 255:
        im /= 65535.0
    else:
        im /= 255.0
    a = im[..., 3:4]
    rgb = im[..., :3] + bg * (1 - a)  # cor pré-multiplicada pelo Cycles? (PNG do Blender é reta) -> composição reta
    rgb = im[..., :3] * a + bg * (1 - a)
    ruido = (rng.random(rgb.shape) - rng.random(rgb.shape)) * 0.9
    out = np.clip(rgb * 255.0 + ruido + 0.5, 0, 255).astype(np.uint8)
    return Image.fromarray(out, "RGB")


def gravar_video(frames, base, fps, crf):
    """Quadros -> <base>.mp4 (H.264, toca em Android, iPhone e navegador) + <base>.webp (pôster, quadro do meio)."""
    import shutil
    import subprocess
    import tempfile
    tmp = tempfile.mkdtemp()
    try:
        for j, f in enumerate(frames):
            f.save(os.path.join(tmp, f"{j:04d}.png"))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", os.path.join(tmp, "%04d.png"),
                        "-c:v", "libx264", "-profile:v", "high", "-level", "4.0", "-pix_fmt", "yuv420p", "-preset", "slow",
                        "-crf", str(crf), "-tune", "film", "-g", str(max(1, len(frames))), "-movflags", "+faststart", "-an",
                        base + ".mp4"], check=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    frames[len(frames) // 2].save(base + ".webp", "WEBP", quality=86, method=6)


def main():
    from PIL import Image
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--mh", required=True)
    ap_.add_argument("--anim", required=True, nargs="+")
    ap_.add_argument("--ex", default=os.path.join(AQUI, "..", "..", "app", "src", "main", "assets", "exercises.json"))
    ap_.add_argument("--ids", default="")
    ap_.add_argument("--saida", required=True)
    ap_.add_argument("--tam", type=int, default=720)
    ap_.add_argument("--amostras", type=int, default=16)
    ap_.add_argument("--fps", type=float, default=22)
    ap_.add_argument("--chaves", action="store_true", help="só quadros-chave (revisão)")
    ap_.add_argument("--tira", type=int, default=0, help="revisão: N quadros igualmente espaçados no ciclo, lado a lado")
    ap_.add_argument("--pular-existentes", action="store_true")
    ap_.add_argument("--video", action="store_true", help="grava <id>.mp4 (H.264) + <id>.webp (pôster) em vez da folha de quadros")
    ap_.add_argument("--crf", type=int, default=18)
    a = ap_.parse_args(sys.argv[1:])
    bpy.ops.wm.read_factory_settings(use_empty=True)
    os.makedirs(a.saida, exist_ok=True)
    revisao = a.chaves or a.tira
    tam_saida = a.tam * 2 if a.chaves else a.tam
    co = cena(tam_saida, a.amostras)
    h = Humano(a.mh)
    h.obj.data.materials.append(material_corpo())
    h.obj.data.color_attributes.new("cor", "FLOAT_COLOR", "POINT")
    calcular_regioes(h)
    grupos = {e["id"]: e for e in json.load(open(a.ex))}
    kit = aparelhos.Kit()
    bg = fundo(tam_saida)
    rng = np.random.default_rng(7)
    k = (h.juntas[h.ossos["upperleg01.L"]["head"]][2] - h.juntas[h.ossos["foot.L"]["head"]][2]) / 8.7
    meta_path = os.path.join(a.saida, "meta.json")
    meta = json.load(open(meta_path)) if os.path.exists(meta_path) else {}
    ids = set(x for x in a.ids.split(",") if x)
    chao = bpy.data.objects["chao"]
    for arq in a.anim:
        for anim in json.load(open(arq)):
            aid = anim["id"]
            if ids and aid not in ids:
                continue
            if a.pular_existentes and not revisao and os.path.exists(os.path.join(a.saida, f"{aid}.mp4" if a.video else f"{aid}.webp")):
                continue
            t_anim = time.time()
            ex = grupos.get(aid, {})
            prim, sec = GRUPOS.get(ex.get("grupo", ""), ([], []))
            prim, sec = list(prim), list(sec)
            for d in anim.get("destaque", []):
                for r in DESTAQUE_PARA.get(d, []):
                    if r not in prim and r not in sec:
                        (prim if not prim else sec).append(r)
            colorir(h, prim, sec)
            ctx = preparar_anim(h, anim, k, ex.get("grupo", ""))
            if a.chaves:
                estados = [quadro_chave(h, ctx, i) for i in range(len(ctx.chaves))]
            else:
                taus = ctx.trilhas.instantes(a.fps)
                if a.tira:
                    taus = [j * ctx.trilhas.T / a.tira for j in range(a.tira)]
                estados = [quadro(h, ctx, t) for t in taus]
            t_pose = time.time() - t_anim
            # aparelhos (fixos + móveis) e enquadramento com todos os quadros
            kit.limpar()
            aparelhos.montar(kit, ctx, h, estados)
            pts = []
            for est in estados[:: max(1, len(estados) // 24)] + [estados[-1]]:
                h.restaurar(est["est"])
                pts.append(h.proxy(est["T"])[::3])
                kit.atualizar(est)
                pts.append(kit.pontos())
            pts = np.concatenate(pts)
            az = azimute_de_cam(anim.get("cam", 64))
            enquadrar(co, pts, az)
            lo, hi = pts.min(axis=0), pts.max(axis=0)
            chao.location = ((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, 0.0)
            r_chao = max(hi[0] - lo[0], hi[1] - lo[1]) / 2 + 4.0
            chao.scale = (r_chao, r_chao, 1)
            frames = []
            t_render = time.time()
            for j, est in enumerate(estados):
                h.restaurar(est["est"])
                h.aplicar(est["T"])
                kit.atualizar(est)
                caminho = os.path.join(a.saida, f"_tmp_{aid}_{j}.png")
                bpy.context.scene.render.filepath = caminho
                bpy.ops.render.render(write_still=True)
                frames.append(compor(caminho, bg, rng))
                os.remove(caminho)
            t_render = (time.time() - t_render) / max(1, len(frames))
            if revisao:
                folha = Image.new("RGB", (tam_saida * len(frames), tam_saida))
                for j, f in enumerate(frames):
                    folha.paste(f, (j * tam_saida, 0))
                folha.save(os.path.join(a.saida, f"{aid}.jpg"), quality=88)
            elif a.video:
                gravar_video(frames, os.path.join(a.saida, aid), a.fps, a.crf)
                meta[aid] = {"v": 1, "f": len(frames), "s": a.tam, "fps": a.fps}
                json.dump(meta, open(meta_path, "w"), separators=(",", ":"), sort_keys=True)
            else:
                cols = 6
                linhas = math.ceil(len(frames) / cols)
                folha = Image.new("RGB", (cols * a.tam, linhas * a.tam), (14, 13, 12))
                for j, f in enumerate(frames):
                    folha.paste(f, ((j % cols) * a.tam, (j // cols) * a.tam))
                folha.save(os.path.join(a.saida, f"{aid}.webp"), "WEBP", quality=70, method=6)
                meta[aid] = {"f": len(frames), "c": cols, "s": a.tam, "fps": a.fps}
                json.dump(meta, open(meta_path, "w"), separators=(",", ":"))
            print("pronto", aid, len(frames), f"{(time.time() - t_anim) / max(1, len(frames)):.2f}s/quadro",
                  f"(render {t_render:.2f}s, poses {t_pose:.1f}s)", flush=True)


if __name__ == "__main__":
    main()
