"""Renderização 3D das demonstrações do Forja (Blender como módulo Python).

Corpo: malha-base do MakeHuman (CC0) com alvos de atleta (homem jovem, musculatura máxima, gordura mínima).
Esqueleto: default.mhskel + pesos default_weights.mhw do MakeHuman.
Poses: as mesmas de tools/anim (ângulos absolutos no plano sagital) + campos 3D opcionais:
  "bfa"/"bta": abdução do braço da frente/trás (0 = no plano sagital, 90 = aberto para o lado)
  "afa"/"ata": abdução do antebraço
  "pfa"/"pta": abdução da perna (coxa)
  "tr": rotação do tronco (torção, graus; + gira o peito para o lado da câmera)
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
from mathutils import Matrix, Vector

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "anim"))
from esqueleto import completar, interpolar, pontos_anim  # noqa: E402

sys.path.insert(0, AQUI)
import anatomia  # noqa: E402

FRENTE = Vector((0, -1, 0))
CIMA = Vector((0, 0, 1))
ESQ = Vector((1, 0, 0))  # lado esquerdo do personagem = lado "f" (perto da câmera)

ALVOS = [
    ("macrodetails/universal-male-young-maxmuscle-averageweight.target", 1.15),
    ("macrodetails/caucasian-male-young.target", 1 / 3), ("macrodetails/african-male-young.target", 1 / 3), ("macrodetails/asian-male-young.target", 1 / 3),
    ("macrodetails/proportions/male-young-maxmuscle-averageweight-idealproportions.target", 1.0),
    # proporções de atleta natural (V): ombros largos, cintura fina, barriga chapada
    ("torso/torso-vshape-incr.target", 0.55),
    ("measure/measure-waist-circ-decr.target", 0.55),
    ("measure/measure-shoulder-dist-incr.target", 0.35),
    ("stomach/stomach-pregnant-decr.target", 0.6),
    ("measure/measure-neck-circ-incr.target", 0.35),
    ("buttocks/buttocks-volume-incr.target", 0.25),
    ("torso/torso-muscle-dorsi-incr.target", 0.4),
    ("torso/torso-muscle-pectoral-incr.target", 0.3),
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
        elif linha.startswith("f ") and grupo == "body":
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
        for lado, s, sufixo in (("f", 1, ".L"), ("t", -1, ".R")):
            b, a = p["b" + lado]
            ab = pose.get("b" + lado + "a", 0) or 0
            aa = pose.get("a" + lado + "a", ab) or 0
            for nome in ("upperarm01", "upperarm02"):
                self._apontar(nome + sufixo, d(b, ab, s))
            for nome in ("lowerarm01", "lowerarm02", "wrist"):
                self._apontar(nome + sufixo, d(a, aa, s))
            c_, sh, pe = p["p" + lado]
            pa = pose.get("p" + lado + "a", 0) or 0
            for nome in ("upperleg01", "upperleg02"):
                self._apontar(nome + sufixo, d(c_, pa, s))
            for nome in ("lowerleg01", "lowerleg02"):
                self._apontar(nome + sufixo, d(sh, pa, s))
            # o osso do pé aponta ~27° para baixo com o pé apoiado (pe = 90)
            self._apontar("foot" + sufixo, d(pe - 27, pa * 0.3, s))

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

PELE = (0.62, 0.60, 0.58)
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
    R["_short"] = ((z > hipz - 1.45 + 0.12 * yb) & (z < hipz + 0.92) & ((coxa + tronco) > 0.5) & (braco + antebr < 0.2)).astype(float)
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
    luz("chave", (22, -12, 26), 11000, 3)
    luz("preenchimento", (-16, -20, 8), 1800, 16, (0.9, 0.95, 1.0))
    luz("recorte", (-10, 22, 20), 9000, 4, (1.0, 0.80, 0.62))
    cam = bpy.data.cameras.new("cam")
    cam.type = "ORTHO"
    co = bpy.data.objects.new("cam", cam)
    sc.collection.objects.link(co)
    sc.camera = co
    return co


def material_corpo():
    m = bpy.data.materials.new("pele")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    attr = nt.nodes.new("ShaderNodeVertexColor")
    attr.layer_name = "cor"
    ao = nt.nodes.new("ShaderNodeAmbientOcclusion")
    ao.inputs["Distance"].default_value = 0.9
    ao.samples = 8
    mult = nt.nodes.new("ShaderNodeMix")
    mult.data_type = "RGBA"
    mult.blend_type = "MULTIPLY"
    mult.inputs["Factor"].default_value = 0.7
    gam = nt.nodes.new("ShaderNodeGamma")
    gam.inputs["Gamma"].default_value = 1.8
    nt.links.new(ao.outputs["AO"], gam.inputs["Color"])
    nt.links.new(attr.outputs["Color"], mult.inputs[6])
    nt.links.new(gam.outputs["Color"], mult.inputs[7])
    nt.links.new(mult.outputs[2], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.42
    bsdf.inputs["Coat Weight"].default_value = 0.2
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
                ap.cilindro((-5, c.y, c.z), (5, c.y, c.z), 0.16, ap.metal)
                for dx in (-5, 5):
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
            mf = h.junta_mundo("wrist.L", True); mt = h.junta_mundo("wrist.R", True)
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
                if ate == "pes":
                    for m, pe in ((mf, h.junta_mundo("foot.L")), (mt, h.junta_mundo("foot.R"))):
                        ap.cilindro(m, pe, 0.07, ap.brasa, 8)
                elif isinstance(ate, list):
                    a = p2_para_3d(ate[0], ate[1], ref)
                    for m in (mf, mt):
                        ap.cilindro(m, (m.x, a.y, a.z), 0.06 if tp == "cabo" else 0.08, ap.metal if tp == "cabo" else ap.brasa, 8)


# ------------------------------------------------------------------ animação

CAMPOS_3D = ("bfa", "bta", "afa", "ata", "pfa", "pta", "tr")


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


def posicionar(h, anim, pose, k, ref0):
    """Posa e coloca o corpo no lugar: apoio no chão + âncora/deslocamento horizontal."""
    h.rig.location = (0, 0, 0)
    h.posar(pose)
    p2 = pontos_anim(anim, completar({kk: v for kk, v in pose.items() if kk not in CAMPOS_3D}))
    quad3 = h.junta_mundo("root")
    if ref0 is None:
        alvo_y = quad3.y
    else:
        alvo_y = ref0[1].y + (-(p2["quadril"][0] - ref0[0])) * k  # frente = -Y
    dy = alvo_y - quad3.y
    if pose.get("y") is not None:
        dz = p2["quadril"][1] * k - quad3.z
    else:
        pts = h.pontos_mundo()
        dz = -pts[:, 2].min() + (pose.get("ay", 0) or 0) * k
    h.rig.location = (0, dy, dz)
    bpy.context.view_layer.update()
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
            anim["_anilha"] = 1.25 if ex.get("grupo") in ("Bíceps", "Tríceps", "Ombros", "Trapézio") else 2.2
            poses = anim["quadros"] if a.chaves else quadros_anim(anim, a.fps)
            # referência (quadro 0) e enquadramento fixo
            p2 = posicionar(h, anim, anim["quadros"][0], k, None)
            ref0 = (p2["quadril"][0], h.junta_mundo("root").copy())
            ref_props = (p2["quadril"][0], h.junta_mundo("root").copy(), k)
            todos = []
            for pose in anim["quadros"] + poses[:: max(1, len(poses) // 8)]:
                posicionar(h, anim, pose, k, ref0)
                todos.append(h.pontos_mundo())
            ap.limpar()
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
