"""Aparelhos 3D das demonstrações (simples, mas reconhecíveis).

Peças fixas são criadas uma vez por animação; peças móveis (barra, halteres, cabos, pedais, plataforma do leg press,
rolo da extensora...) são objetos criados uma vez e reposicionados a cada quadro pela matriz (barato para o Cycles).
Interface usada por humano.py:
  ALTURA_ESTEIRA, ALTURA_TAPETE, raio_anilha(ctx)
  preparar(ctx, h)                      -> antes das poses (círculo dos pedais da bike etc.)
  antes_ik(ctx, h, T, tau, extras)      -> em cada quadro, antes do IK de apoio (pés nos pedais)
  Kit(); montar(kit, ctx, h, estados); kit.atualizar(estado); kit.pontos(); kit.limpar()
"""
import math

import bpy
import numpy as np
from mathutils import Matrix, Quaternion, Vector

ALTURA_ESTEIRA = 0.38
ALTURA_TAPETE = 0.07
FRENTE = Vector((0, -1, 0))
CIMA = Vector((0, 0, 1))
X = Vector((1, 0, 0))


def raio_anilha(ctx):
    return 1.2 if ctx.grupo in ("Bíceps", "Tríceps", "Ombros", "Trapézio") else 2.0


# ------------------------------------------------------------------ materiais e primitivas

def _mat(nome, cor, metal=0.0, rug=0.5, coat=0.0):
    m = bpy.data.materials.get(nome) or bpy.data.materials.new(nome)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*cor, 1)
    b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rug
    b.inputs["Coat Weight"].default_value = coat
    return m


def _alinhar(eixo_de, eixo_para):
    return eixo_de.rotation_difference(eixo_para.normalized()).to_matrix().to_4x4()


class Kit:
    def __init__(self):
        self.objs = []
        self.moveis = []  # funções (estado) -> None
        self.metal = _mat("metal", (0.72, 0.72, 0.74), 1.0, 0.25)
        self.quadro = _mat("quadro", (0.13, 0.135, 0.145), 0.5, 0.38)
        self.preto = _mat("preto", (0.035, 0.035, 0.04), 0.0, 0.55)
        self.estofado = _mat("estofado", (0.05, 0.05, 0.055), 0.0, 0.6, 0.15)
        self.borracha = _mat("borracha", (0.03, 0.03, 0.032), 0.0, 0.75)
        self.brasa = _mat("brasa", (0.95, 0.28, 0.08), 0.0, 0.4)
        self.cabo_m = _mat("cabo", (0.25, 0.25, 0.27), 0.8, 0.35)
        self.chao = _mat("tapete", (0.075, 0.04, 0.032), 0.0, 0.95)
        self.madeira = _mat("madeira", (0.42, 0.27, 0.15), 0.0, 0.6)
        self.cinza = _mat("cinza", (0.30, 0.30, 0.32), 0.0, 0.6)

    def limpar(self):
        for o in self.objs:
            me = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if me is not None and me.users == 0:
                bpy.data.meshes.remove(me)
        self.objs = []
        self.moveis = []

    def _add(self, o, mat, liso=True):
        o.data.materials.clear()
        o.data.materials.append(mat)
        if liso:
            for p in o.data.polygons:
                p.use_smooth = True
        self.objs.append(o)
        return o

    # ---- fixas
    def cil(self, a, b, r, mat, verts=24):
        a, b = Vector(a), Vector(b)
        d = b - a
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=max(d.length, 1e-3), location=(a + b) / 2)
        o = bpy.context.active_object
        o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
        return self._add(o, mat)

    def caixa(self, centro, tam, mat, bevel=0.08, rot=None):
        bpy.ops.mesh.primitive_cube_add(size=1, location=centro)
        o = bpy.context.active_object
        o.scale = tam
        if rot is not None:
            o.rotation_euler = rot
        bpy.ops.object.transform_apply(scale=True)
        if bevel:
            m = o.modifiers.new("b", "BEVEL")
            m.width = min(bevel, min(tam) * 0.45)
            m.segments = 2
            m.limit_method = "ANGLE"
        return self._add(o, mat, liso=False)

    def viga(self, a, b, larg, esp, mat, bevel=0.04):
        """Perfil retangular de a até b (estrutura de máquina)."""
        a, b = Vector(a), Vector(b)
        d = b - a
        L = max(d.length, 1e-3)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
        o = bpy.context.active_object
        o.scale = (larg, esp, L)
        bpy.ops.object.transform_apply(scale=True)
        if bevel:
            m = o.modifiers.new("b", "BEVEL")
            m.width = min(bevel, larg * 0.4, esp * 0.4)
            m.segments = 2
        o.matrix_world = Matrix.Translation((a + b) / 2) @ _alinhar(CIMA, d)
        return self._add(o, mat, liso=False)

    def esfera(self, c, r, mat):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=c, segments=32, ring_count=16)
        return self._add(bpy.context.active_object, mat)

    def toro(self, c, r1, r2, mat, eixo=(1, 0, 0)):
        bpy.ops.mesh.primitive_torus_add(major_radius=r1, minor_radius=r2, location=c, major_segments=40, minor_segments=10)
        o = bpy.context.active_object
        o.rotation_euler = Vector(eixo).to_track_quat("Z", "Y").to_euler()
        return self._add(o, mat)

    def disco(self, c, r, esp, mat, eixo=(1, 0, 0), verts=40):
        e = Vector(eixo).normalized() * esp / 2
        o = self.cil(Vector(c) - e, Vector(c) + e, r, mat, verts)
        m = o.modifiers.new("b", "BEVEL")
        m.width = min(0.06, esp * 0.3)
        m.segments = 2
        m.limit_method = "ANGLE"
        return o

    # ---- móveis
    def cil_movel(self, r, mat, verts=12):
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=1.0, location=(0, 0, 0))
        o = bpy.context.active_object
        return self._add(o, mat)

    @staticmethod
    def por_cil(o, a, b):
        a, b = Vector(a), Vector(b)
        d = b - a
        L = max(d.length, 1e-4)
        o.matrix_world = Matrix.Translation((a + b) / 2) @ _alinhar(CIMA, d if L > 1e-4 else CIMA) @ Matrix.Diagonal((1, 1, L, 1))

    def grupo_movel(self, objs):
        """Junta objetos fixos criados na origem num único objeto móvel (eixo local X = eixo da peça)."""
        bpy.ops.object.select_all(action="DESELECT")
        for o in objs:
            bpy.context.view_layer.objects.active = o
            for m in list(o.modifiers):
                bpy.ops.object.modifier_apply(modifier=m.name)
        for o in objs:
            o.select_set(True)
        bpy.context.view_layer.objects.active = objs[0]
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        bpy.context.view_layer.objects.active = objs[0]
        bpy.ops.object.join()
        o = bpy.context.active_object
        for x in objs[1:]:
            if x in self.objs:
                self.objs.remove(x)
        return o

    def atualizar(self, est):
        for f in self.moveis:
            f(est)

    def pontos(self, lo=None, hi=None, margem=2.5):
        """Cantos das peças (mundo). Com lo/hi (caixa do corpo), só o implemento nas mãos entra inteiro; o resto
        (torres, pórticos, esteira) é recortado à caixa do corpo + margem e pode sair pela borda do quadro."""
        out = []
        for o in self.objs:
            if o.hide_render:
                continue
            M = o.matrix_world
            cs = np.array([tuple(M @ Vector(c)) for c in o.bound_box])
            if lo is not None and not o.get("foco"):
                cs = np.clip(cs, np.asarray(lo) - margem, np.asarray(hi) + margem)
            out.extend(cs.tolist())
        return np.array(out) if out else np.zeros((0, 3))


# ------------------------------------------------------------------ peças compostas (criadas na origem, eixo X)

def barra_olimpica(kit, R, curta=False):
    meia = 7.6 if curta else 11.0
    luva = 5.2 if curta else 6.5
    ps = [kit.cil((-luva, 0, 0), (luva, 0, 0), 0.14, kit.metal, 20)]
    for s in (-1, 1):
        ps.append(kit.cil((s * luva, 0, 0), (s * meia, 0, 0), 0.25, kit.metal, 20))
        ps.append(kit.cil((s * (luva - 0.05), 0, 0), (s * (luva + 0.18), 0, 0), 0.42, kit.metal, 24))
        x0 = luva + 0.2
        esp = 0.62 if not curta else 0.36
        ps.append(kit.disco((s * (x0 + esp / 2), 0, 0), R, esp, kit.borracha, verts=56))
        ps.append(kit.toro((s * (x0 + esp / 2), 0, 0), R * 0.55, 0.05, kit.brasa))
        ps.append(kit.disco((s * (x0 + esp + 0.15), 0, 0), 0.5, 0.25, kit.metal, verts=24))
    return kit.grupo_movel(ps)


def halter_peca(kit):
    ps = [kit.cil((-0.65, 0, 0), (0.65, 0, 0), 0.15, kit.metal, 16)]
    for s in (-1, 1):
        ps.append(kit.cil((s * 0.62, 0, 0), (s * 1.15, 0, 0), 0.62, kit.borracha, 6))
        ps.append(kit.cil((s * 0.6, 0, 0), (s * 0.66, 0, 0), 0.4, kit.brasa, 6))
    return kit.grupo_movel(ps)


# ------------------------------------------------------------------ pegadores (mãos fechadas em aparelhos)

MAQ_ASSENTO = ("leg-press", "extensora", "cadeira-flexora", "abdutora", "adutora")


def maos_em_pegadores(ctx):
    """Lados cujas mãos seguram um pegador/guidão/manopla/corrimão do aparelho (o motor faz a IK até ele)."""
    idd, t = ctx.id, ctx.tipos
    if ("bike" in t or "roda" in t or "treno" in t or "eliptico" in t or "escada" in t
            or any(s_ in idd for s_ in MAQ_ASSENTO + ("mesa-flexora", "panturrilha-sentado", "eliptico", "escada", "sled",
                                                      "roda-abdominal"))
            or idd.startswith("hack")):
        return {"f", "t"}
    return set()


def raio_pega(ctx):
    """Raio da empunhadura (dm) que cada mão segura: define a curvatura calibrada dos dedos."""
    t, idd = ctx.tipos, ctx.id
    r = 0.15
    if "barra_fixa" in t or "barra" in t:
        r = 0.15
    elif "kettlebell" in t:
        r = 0.13
    elif "cabo" in t:
        r = 0.12 if tipo_cabo(ctx) == "corda" else 0.15
    elif "elastico" in t or "corda" in t:
        r = 0.15
    elif "bike" in t or "roda" in t or _tipo_pegador(ctx) is not None:
        r = 0.2
    elif any(x in idd for x in ("supino-maquina", "peck-deck", "voador", "desenvolvimento-maquina")):
        r = 0.2
    return {".L": r, ".R": r}


def _tipo_pegador(ctx):
    idd = ctx.id
    if "roda" in ctx.tipos or "roda-abdominal" in idd:
        return "roda"
    if "treno" in ctx.tipos or "sled" in idd:
        return "treno"
    if "escada" in ctx.tipos or "escada" in idd:
        return "escada"
    if "eliptico" in ctx.tipos or "eliptico" in idd:
        return "eliptico"
    if "mesa-flexora" in idd:
        return "mesa"
    if "panturrilha-sentado" in idd:
        return "coxa"
    if idd.startswith("hack"):
        return "hack"
    if any(s_ in idd for s_ in MAQ_ASSENTO):
        return "assento"
    return None


def preparar_pegadores(ctx, h):
    """Pegadores fixos no mundo (calculados no quadro-chave 0) ou presos ao corpo/aparelho móvel (calculados por quadro).
    ctx.pegadores = {"tipo": .., ".L"/".R": (posição, eixo)} para os fixos."""
    tipo = _tipo_pegador(ctx)
    ctx.pegadores = None
    if tipo is None or not ctx.chaves:
        return
    c0 = ctx.chaves[0]
    h.restaurar(c0["est"])
    T = c0["T"]
    r = T @ h.cabeca("root")
    cfg = {"tipo": tipo}
    if tipo == "assento":
        # barras laterais do assento, ao lado do quadril (pegada neutra)
        # leg press (encosto reclinado, braço para a frente): pegador transversal; cadeiras (braço pendente): longitudinal
        e = Vector((1, 0, 0)) if "leg-press" in ctx.id else Vector((0, 1, 0))
        for sf, sx in ((".L", 1), (".R", -1)):
            cfg[sf] = (Vector((sx * 2.55, r.y - 0.1, r.z - 0.55)), e)
    elif tipo == "mesa":
        b = [pr for pr in ctx.props if pr.get("tipo") == "banco"]
        b = b[0] if b else {"x": 0, "w": 8, "h": 4}
        a_, b_ = ctx.p3(b.get("x", 0), 0), ctx.p3(b.get("x", 0) + b.get("w", 8), 0)
        y_fr = min(a_.y, b_.y)
        zt = (b.get("y", 0) + b.get("h", 4)) * ctx.k
        for sf, sx in ((".L", 1), (".R", -1)):
            cfg[sf] = (Vector((sx * 1.9, y_fr + 0.9, zt - 0.9)), Vector((1, 0, 0)))
    elif tipo == "escada":
        zs = [(T @ h.pegada(sf)).z for sf in (".L", ".R")]
        ys = [(T @ h.pegada(sf)).y for sf in (".L", ".R")]
        z = min(max(sum(zs) / 2, r.z + 0.6), r.z + 2.6)
        for sf, sx in ((".L", 1), (".R", -1)):
            cfg[sf] = (Vector((sx * 2.7, sum(ys) / 2, z)), Vector((0, 1, 0)))
    elif tipo == "eliptico":
        mq = [pr for pr in ctx.props if pr.get("tipo") == "maquina"]
        toes = []
        zs = []
        for ch in ctx.chaves:
            h.restaurar(ch["est"])
            toes += [(ch["T"] @ h.cauda("toe3-1" + sf)).y for sf in (".L", ".R")]
            zs += [(ch["T"] @ h.cabeca("spine01")).z]
        h.restaurar(c0["est"])
        yc = min(toes) - 1.6
        if mq:
            yc = min(yc, ctx.p3(mq[0].get("x", 4), 0).y)
        cfg["yc"] = yc
        cfg["zc"] = sum(zs) / len(zs) - 1.0
        cfg["piv"] = {sf: Vector((sx * 1.7, yc - 0.2, cfg["zc"] - 4.5)) for sf, sx in ((".L", 1), (".R", -1))}
    elif tipo == "treno":
        ys, zs = [], []
        for ch in ctx.chaves:
            h.restaurar(ch["est"])
            for sf in (".L", ".R"):
                g = ch["T"] @ h.pegada(sf)
                ys.append(g.y)
                zs.append(g.z)
        h.restaurar(c0["est"])
        y = sum(ys) / len(ys)
        z = min(max(sum(zs) / len(zs), 6.0), 13.0)
        for sf, sx in ((".L", 1), (".R", -1)):
            cfg[sf] = (Vector((sx * 2.1, y, z)), Vector((0, 0, 1)))
    ctx.pegadores = cfg


def _alvo_pegador(ctx, h, T, sf, sx):
    """(posição no mundo, eixo no mundo) do pegador desta mão neste quadro, ou None."""
    cfg = ctx.pegadores
    if not cfg:
        return None
    tipo = cfg["tipo"]
    if sf in cfg:
        return cfg[sf]
    if tipo == "coxa":
        # alavanca da panturrilha sentado: pegadores sobre a almofada das coxas (acompanham os joelhos)
        j = T @ h.cabeca("lowerleg01" + sf)
        q = T @ h.cabeca("upperleg01" + sf)
        c = j + (q - j) * 0.16
        return (Vector((sx * 3.0, c.y, c.z + 1.1)), Vector((0, 1, 0)))
    if tipo == "hack":
        S = T @ h.cabeca("upperarm01" + sf)
        u = (T @ h.cabeca("neck01") - T @ h.cabeca("root")).normalized()
        nb = u.cross(Vector((1, 0, 0))).normalized()
        if nb.y < 0:
            nb = -nb
        return (S - u * 1.2 + Vector((sx * 1.9, 0, 0)) - nb * 0.4, u)
    if tipo == "roda":
        g = (T @ h.pegada(".L") + T @ h.pegada(".R")) / 2
        return (Vector((sx * 1.18, g.y, ctx.z0 + RAIO_RODA)), Vector((1, 0, 0)))
    return None


RAIO_RODA = 0.95


def ik_pegadores(ctx, h, T):
    """Mãos fechadas nos pegadores/guidão/manoplas do aparelho (IK do braço, punho alinhado ao pegador)."""
    if not getattr(ctx, "pegadores", None):
        return
    Ti = T.inverted()
    Ti3 = Ti.to_3x3()
    for _ in range(2):
        for sf, sx in ((".L", 1), (".R", -1)):
            a = _alvo_pegador(ctx, h, T, sf, sx)
            if a is None:
                continue
            pos, eixo = a
            alvo_l = Ti @ pos
            R = h.rot_pegada(sf, Ti3 @ eixo, None if abs(eixo.x) < 0.7 else False, f=(h.cabeca("wrist" + sf) - h.cabeca("lowerarm01" + sf)).normalized())
            h.ik("braco", sf, alvo_l - R @ h.off_peg[sf], R)


def depois_ik(ctx, h, T, tau, extras):
    """No fim de cada quadro (posição final do corpo): mãos presas a pegadores fixos no mundo, implementos de duas mãos."""
    ik_pegadores(ctx, h, T)
    pegada_implementos(ctx, h, T, tau, extras)
    halteres_fora_do_corpo(ctx, h, T)


def halteres_fora_do_corpo(ctx, h, T, raio=0.66):
    """Halter (um por mão) não entra na coxa/tronco: a mão é afastada para fora (IK) o que faltar."""
    if "halter" not in ctx.tipos or "halter_unico" in (getattr(ctx, "impl", None) or {}):
        return
    pr = [p for p in ctx.props if p.get("tipo") == "halter"][0]
    lados = {"f": (".L",), "t": (".R",)}.get(_qual_mao(pr), (".L", ".R"))
    P = h.proxy(T)
    corpo = h.px_partes["tronco"] | h.px_partes["coxa_f"] | h.px_partes["coxa_t"] | h.px_partes["canela_f"] | h.px_partes["canela_t"]
    Q = P[corpo]
    Ti = T.inverted()
    for sf in lados:
        sx = 1 if sf == ".L" else -1
        for _ in range(3):
            g = T @ h.pegada(sf)
            e = (T.to_3x3() @ h.eixo_pegada(sf)).normalized()
            pior = 0.0
            for s_ in (-0.9, 0.9):
                c = np.array(g + e * s_)
                d = float(np.linalg.norm(Q - c, axis=1).min())
                pior = max(pior, raio - d)
            if pior <= 0.01:
                break
            lat = (T.to_3x3() @ Vector((sx, 0, 0))).normalized()
            alvo = Ti @ (T @ h.cabeca("wrist" + sf) + lat * (pior + 0.03))
            h.ik("braco", sf, alvo, h.rot("wrist" + sf))


def pegar_em(h, T, sf, pos, eixo, supinada=None, passes=2):
    """Leva a pegada da mão até 'pos' (mundo), fechada em volta de um cabo de eixo 'eixo' (mundo)."""
    Ti = T.inverted()
    Ti3 = Ti.to_3x3()
    alvo_l = Ti @ pos
    for _ in range(passes):
        R = h.rot_pegada(sf, Ti3 @ eixo, supinada, f=(h.cabeca("wrist" + sf) - h.cabeca("lowerarm01" + sf)).normalized())
        h.ik("braco", sf, alvo_l - R @ h.off_peg[sf], R)


def preparar_implementos(ctx, h):
    """Implementos seguros com as duas mãos e pegadores de cabo: configuração usada em pegada_implementos."""
    cfg = {}
    for pr in ctx.props:
        tp = pr.get("tipo")
        if tp == "bola" and pr.get("em", "maos") == "maos" and "roda" not in ctx.tipos and "roda-abdominal" not in ctx.id:
            cfg["bola"] = pr
        elif tp == "kettlebell" and _qual_mao(pr) == "ambas":
            cfg["kettlebell"] = pr
        elif tp == "halter" and (pr.get("unico") or "triceps-frances" in ctx.id) and _qual_mao(pr) == "ambas":
            cfg["halter_unico"] = pr
        elif tp == "cabo" and isinstance(pr.get("ate"), list):
            cfg["cabo"] = pr
    ctx.impl = cfg
    ctx.bola_voo = None
    if "bola" in cfg and cfg["bola"].get("voo"):
        i0, i1 = cfg["bola"]["voo"][:2]
        t0 = ctx.trilhas.t0
        ctx.bola_voo = (float(t0[int(i0) % len(ctx.chaves)]), float(t0[int(i1) % len(ctx.chaves)]), cfg["bola"].get("quica"))


RAIO_BOLA = 1.1


def bola_no_ar(ctx, tau):
    """(no ar?, fração do voo) para a bola com "voo": [chave_soltura, chave_retomada]."""
    v = getattr(ctx, "bola_voo", None)
    if not v:
        return False, 0.0
    a, b, _ = v
    T = ctx.trilhas.T
    d = (b - a) % T
    x = (tau - a) % T
    return (0.0 < x < d), (x / d if d > 1e-6 else 0.0)


def tipo_cabo(ctx):
    if "triangulo" in ctx.id or "remada-baixa" in ctx.id:
        return "triangulo"
    if any(s_ in ctx.id for s_ in ("triceps", "face", "abdominal")):
        return "corda"
    if "crossover" in ctx.id:
        return "dupla"
    return "barra"


def _palmas_na_bola(ctx, h, T):
    """Palmas abertas encostadas nos lados da bola (raio fixo): a bola fica entre as palmas; mãos afastadas demais
    convergem por IK até a distância do diâmetro."""
    Ti = T.inverted()
    pc = {sf: T @ h.palma_c(sf) for sf in (".L", ".R")}
    d = pc[".L"] - pc[".R"]
    meio = (pc[".L"] + pc[".R"]) / 2
    e = d.normalized() if d.length > 1e-4 else Vector((1, 0, 0))
    R = RAIO_BOLA + 0.08
    nrm = Vector()
    for sf in (".L", ".R"):
        Rr = h.rot("wrist" + sf) @ h.rest_inv["wrist" + sf].to_3x3()
        nrm += T.to_3x3() @ (Rr @ h.ref_mao[sf].col[2])
    if d.length >= 2 * R or nrm.length < 1e-3:
        c = meio
    else:
        n_ = nrm - e * nrm.dot(e)
        n_ = n_.normalized() if n_.length > 1e-3 else Vector((0, -1, 0))
        c = meio + n_ * math.sqrt(max(R * R - (d.length / 2) ** 2, 0.0))
    for sf, sx in ((".L", 1), (".R", -1)):
        alvo = c + e * (R * sx) if d.length >= 2 * R else pc[sf]
        nn = (c - alvo).normalized()  # palma de frente para o centro da bola
        ante = T.to_3x3() @ (h.cabeca("wrist" + sf) - h.cabeca("lowerarm01" + sf)).normalized()
        dd = ante - nn * ante.dot(nn)
        if dd.length < 1e-3:
            dd = Vector((0, 0, 1))
        Rl = h.rot_mao(sf, Ti.to_3x3() @ dd.normalized(), Ti.to_3x3() @ nn)
        alvo = c - nn * R
        for _ in range(2):
            h.ik("braco", sf, Ti @ alvo - Rl @ h.off_palma[sf], Rl)
    return c


def _lateral(h, T, gL, gR):
    """Eixo entre as mãos; com as mãos juntas (direção instável) mistura com o lateral do corpo, sem saltos."""
    lat_c = (T.to_3x3() @ Vector((1, 0, 0))).normalized()
    d = gL - gR
    w = mov_suave(d.length, 0.4, 1.6)
    if w <= 0:
        return lat_c
    v = d.normalized() * w + lat_c * (1 - w)
    if v.dot(lat_c) < 0 and w < 1:
        v = lat_c
    return v.normalized()


def pegada_implementos(ctx, h, T, tau, extras):
    cfg = getattr(ctx, "impl", None) or {}
    if "bola" in cfg:
        no_ar, _ = bola_no_ar(ctx, tau)
        if not no_ar:
            extras["bola"] = _palmas_na_bola(ctx, h, T)
    if "kettlebell" in cfg:
        gL, gR = T @ h.pegada(".L"), T @ h.pegada(".R")
        c = (gL + gR) / 2
        # duas mãos lado a lado na alça (no goblet o sino fica embaixo, encostado no peito)
        e = _lateral(h, T, gL, gR)
        for sf, sx in ((".L", 1), (".R", -1)):
            pegar_em(h, T, sf, c + e * (0.3 * sx), e, False)
        extras["kb"] = (c, e)
    if "halter_unico" in cfg:
        # um halter seguro pelas duas mãos (tríceps francês): punhos lado a lado no mesmo cabo, sem dois halteres
        gL, gR = T @ h.pegada(".L"), T @ h.pegada(".R")
        c = (gL + gR) / 2
        d = _lateral(h, T, gL, gR)
        pegar_em(h, T, ".L", c + d * 0.33, d, False)
        pegar_em(h, T, ".R", c - d * 0.33, d, False)
        extras["halter_unico"] = (c, d)
    if "cabo" in cfg:
        tc = tipo_cabo(ctx)
        A = ctx.p3(*cfg["cabo"]["ate"][:3])
        gL, gR = T @ h.pegada(".L"), T @ h.pegada(".R")
        c = (gL + gR) / 2
        lat = _lateral(h, T, gL, gR)
        if tc == "triangulo":
            cab = (A - c).normalized()
            eixo = cab.cross(lat).normalized()
            for sf, sx in ((".L", 1), (".R", -1)):
                pegar_em(h, T, sf, c + lat * (0.7 * sx), eixo)
            extras["triangulo"] = (c, lat, eixo)
        elif tc == "corda":
            no = c + (A - c).normalized() * 1.2
            for sf, g in ((".L", gL), (".R", gR)):
                pegar_em(h, T, sf, g, (g - no).normalized(), passes=1)
        elif tc == "barra":
            for sf, g in ((".L", gL), (".R", gR)):
                pegar_em(h, T, sf, g, lat, passes=1)
    pc = getattr(ctx, "pegadores", None)
    if pc and pc.get("tipo") == "eliptico":
        for sf, sx in ((".L", 1), (".R", -1)):
            g = T @ h.pegada(sf)
            pv = pc["piv"][sf]
            pegar_em(h, T, sf, g, (g - pv).normalized(), passes=1)


# ------------------------------------------------------------------ preparação (antes das poses)

def preparar(ctx, h):
    ctx.bike = None
    ctx.parede = None
    ctx.alavancas = preparar_alavancas(ctx, h)
    preparar_pegadores(ctx, h)
    preparar_implementos(ctx, h)
    for pr in ctx.props:
        if pr.get("tipo") == "parede":
            ctx.parede = _preparar_parede(ctx, h, pr)
    if "bike" not in ctx.tipos:
        return
    pr = [p for p in ctx.props if p.get("tipo") == "bike"][0]
    if "eixo" in pr:
        c = ctx.p3(*pr["eixo"][:2])
        ctx.bike = {"c": c, "r": float(pr.get("raio_pedivela", 1.75)) * ctx.k,
                    "selim": ctx.p3(*pr["selim"][:2]) if "selim" in pr else None,
                    "guidao": ctx.p3(*pr["guidao"][:2]) if "guidao" in pr else None,
                    "em_pe": bool(pr.get("em_pe"))}
        return
    # círculo dos pedais: onde os antepés passam ao longo do ciclo
    pts = {".L": [], ".R": []}
    for j in range(24):
        tau = j * ctx.trilhas.T / 24
        q = ctx.trilhas(tau)
        q["_qb"] = 0.0
        h.posar(q, None)
        pos, rq = ctx.rigido(tau)
        T = Matrix.Translation(Vector(pos)) @ Quaternion(rq).to_matrix().to_4x4() @ Matrix.Translation(-ctx.root0)
        for sf in pts:
            pts[sf].append(np.array(T @ _antepe(h, sf)))
    allp = np.concatenate([np.array(v) for v in pts.values()])
    c = allp.mean(axis=0)
    r = np.linalg.norm(allp[:, 1:] - c[1:], axis=1).mean()
    ctx.bike = {"c": Vector(c), "r": float(max(1.4, min(r, 2.0))), "selim": None, "guidao": None, "em_pe": False}


def _preparar_parede(ctx, h, pr):
    """Batente/parede onde uma mão se apoia (alongamentos): a mão fica presa no ponto do quadro-chave 'chave'."""
    sf = ".L" if pr.get("mao", "f") == "f" else ".R"
    ch = ctx.chaves[int(pr.get("chave", len(ctx.chaves) - 1)) % len(ctx.chaves)]
    h.restaurar(ch["est"])
    T = ch["T"]
    return {"sf": sf, "pos": T @ h.cabeca("wrist" + sf), "rot": (T.to_3x3() @ h.rot("wrist" + sf)).to_quaternion(),
            "palma": T @ h.pegada(sf), "pr": pr}


def _antepe(h, sf):
    """Antepé (bola do pé) no espaço do esqueleto: entre a cabeça dos dedos e o tornozelo, na sola."""
    t3 = h.cabeca("toe3-1" + sf)
    a = h.cabeca("foot" + sf)
    return a + (t3 - a) * 0.78


def antes_ik(ctx, h, T, tau, extras):
    ik_alavancas(ctx, h, T)
    if ctx.parede is not None:
        pa = ctx.parede
        Ti = T.inverted()
        h.ik("braco", pa["sf"], Ti @ pa["pos"], Ti.to_3x3() @ pa["rot"].to_matrix())
    if ctx.bike is None:
        return
    c, r = ctx.bike["c"], ctx.bike["r"]
    Ti = T.inverted()
    ped = {}
    fase = None
    for sf in (".L", ".R"):
        b = T @ _antepe(h, sf)
        ang = math.atan2(b.z - c.z, b.y - c.y)
        if sf == ".L":
            fase = ang
        else:
            # pedais opostos (180°)
            ang = fase + math.pi
        alvo = Vector((b.x, c.y + r * math.cos(ang), c.z + r * math.sin(ang)))
        anc = T @ h.cabeca("foot" + sf)
        h.ik("perna", sf, Ti @ (anc + (alvo - b)), h.rot("foot" + sf))
        ped[sf] = alvo
    extras["pedais"] = ped
    extras["fixos"] = {"pe_f", "pe_t"}
    g = ctx.bike.get("guidao")
    if g is not None:
        # mãos fechadas nas manoplas do guidão (pegada pronada, barra ao longo do eixo lateral)
        gx = ctx.bike.setdefault("gx", max(1.7, min(2.3, abs((T @ h.pegada(".L")).x))))
        Ti3 = Ti.to_3x3()
        for _ in range(2):
            for sf, sx in ((".L", 1), (".R", -1)):
                R = h.rot_pegada(sf, Ti3 @ X)
                alvo = Ti @ Vector((sx * gx, g.y, g.z)) - R @ h.off_peg[sf]
                h.ik("braco", sf, alvo, R)


# ------------------------------------------------------------------ montagem

def _amostras(ctx, h, estados):
    """Informações do corpo ao longo do ciclo (mundo): pegadas, tornozelos, joelhos, quadril, pés."""
    out = []
    for est in estados:
        h.restaurar(est["est"])
        T = est["T"]
        d = {"T": T, "gL": T @ h.pegada(".L"), "gR": T @ h.pegada(".R"), "root": T @ h.cabeca("root"),
             "aL": T @ h.cabeca("foot.L"), "aR": T @ h.cabeca("foot.R"), "jL": T @ h.cabeca("lowerleg01.L"),
             "jR": T @ h.cabeca("lowerleg01.R"), "pesc": T @ h.cabeca("neck01")}
        out.append(d)
    return out


def _plataforma(h, T, n_pes=("pe_f", "pe_t")):
    P = h.proxy(T)
    m = h.px_partes[n_pes[0]] | h.px_partes[n_pes[1]]
    pts = P[m]
    Tq = T.to_3x3()
    nrm = Vector((0, 0, 0))
    for sf in (".L", ".R"):
        R = h.rot("foot" + sf) @ h.rest_inv["foot" + sf].to_3x3()
        nrm += Tq @ (R @ Vector((0, 0, -1)))
    nrm.normalize()
    # centro = média dos centros das DUAS solas (cada pé separado), no plano da sola mais avançada
    cs, lims = [], []
    for ef in n_pes:
        q = P[h.px_partes[ef]]
        pj = q @ np.array(nrm)
        lm = pj.max()
        cs.append(q[pj > lm - 0.25].mean(axis=0))
        lims.append(lm)
    lim = max(lims)
    c = Vector(np.mean(cs, axis=0))
    c = c + nrm * (lim - float(np.array(c) @ np.array(nrm)))
    _ = pts
    return c, nrm


def _rot_placa(n):
    """Placa com a normal -n, eixo X da placa = lateral do corpo (X do mundo) e Y = projeção da subida."""
    up = (-n).normalized()
    xa = X - up * X.dot(up)
    xa.normalize()
    ya = up.cross(xa)
    return Matrix((xa, ya, up)).transposed().to_4x4()


def montar(kit, ctx, h, estados):
    ctx._estados = estados
    am = _amostras(ctx, h, estados)
    kit_estados = estados
    idd = ctx.id
    root_y = sum(a["root"].y for a in am) / len(am)
    xmax = max(max(abs(a["gL"].x), abs(a["gR"].x)) for a in am)
    blocos = []
    for pr in ctx.props:
        tp = pr.get("tipo")
        if tp in ("banco", "maquina", "caixa"):
            blocos.append(pr)
    _blocos(kit, ctx, h, blocos, am)
    for pr in ctx.props:
        tp = pr.get("tipo")
        if tp == "barra_fixa":
            c = ctx.ref.get("barra3") or ctx.p3(pr.get("x", 0), pr.get("y", 21))
            if ctx.paralelas:
                # barras centradas nas mãos (o corpo fica no meio das duas, longe dos montantes)
                c = Vector((c.x, sum((a["gL"].y + a["gR"].y) / 2 for a in am) / len(am) + 0.5, c.z))
                for s in (-1, 1):
                    xb = s * max(2.8, min(xmax, 3.4))  # largas o bastante para o quadril passar entre elas
                    kit.cil((xb, c.y - 6.6, c.z), (xb, c.y + 6.6, c.z), 0.2, kit.metal)
                    for dy in (-6.0, 6.0):
                        kit.cil((xb, c.y + dy, 0), (xb, c.y + dy, c.z - 0.1), 0.22, kit.quadro, 16)
                        kit.caixa((xb, c.y + dy, 0.08), (1.6, 0.6, 0.16), kit.quadro, 0.04)
            else:
                mb = max(5.0, xmax + 1.6)
                kit.cil((-mb - 0.4, c.y, c.z), (mb + 0.4, c.y, c.z), 0.16, kit.metal)
                for dx in (-mb, mb):
                    kit.viga((dx, c.y, 0), (dx, c.y, c.z + 0.5), 0.5, 0.5, kit.quadro)
                    kit.caixa((dx, c.y, 0.1), (0.7, 5.0, 0.2), kit.quadro, 0.05)
        elif tp == "saco":
            _saco(kit, ctx, h, pr, estados)
        elif tp == "esteira":
            _esteira(kit, ctx, root_y, am)
        elif tp == "tapete":
            pp = []
            for est in estados[:: max(1, len(estados) // 6)]:
                h.restaurar(est["est"])
                P = h.proxy(est["T"])
                pp.append(P[P[:, 2] < ctx.z0 + 1.2])
            pp = np.concatenate(pp) if pp else np.zeros((0, 3))
            if len(pp) < 5:
                pp = np.array([[0, root_y - 8, 0], [0, root_y + 8, 0]])
            lo, hi = pp.min(axis=0), pp.max(axis=0)
            cx, cy = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
            lx, ly = max(6.5, hi[0] - lo[0] + 2.0), max(16.0, hi[1] - lo[1] + 3.0)
            kit.caixa((cx, cy, ALTURA_TAPETE / 2), (lx, ly, ALTURA_TAPETE), kit.chao, 0.03)
        elif tp == "rolo":
            c = ctx.p3(pr.get("x", 0), pr.get("y", 0.8))
            r = 0.75
            z = max(c.z, r + ctx.z0)
            kit.cil((-3, c.y, z), (3, c.y, z), r, kit.brasa, 32)
        elif tp == "bike":
            _bike(kit, ctx, h, am)
        elif tp == "cabo" and isinstance(pr.get("ate"), list):
            _polia(kit, ctx, pr, am)
        elif tp == "elastico":
            _elastico(kit, ctx, h, pr, am)
        elif tp == "barra":
            _barra(kit, ctx, h)
        elif tp == "halter":
            _halteres(kit, ctx, h, _qual_mao(pr))
        elif tp == "apoio_tornozelo":
            _apoio_tornozelo(kit, ctx, pr, am)
        elif tp == "kettlebell":
            _kettlebell(kit, ctx, h, _qual_mao(pr))
        elif tp == "bola":
            _bola(kit, ctx, h)
        elif tp == "corda":
            _corda(kit, ctx, h)
        elif tp == "parede" and ctx.parede is not None:
            _parede(kit, ctx, h)
    _extras_maquina(kit, ctx, h, am, estados)


def _qual_mao(pr):
    m = pr.get("maos")
    if m in ("f", "t"):
        return m
    em = pr.get("em", "")
    return em[-1] if em in ("mao_f", "mao_t") else "ambas"


def _meio_corpo(am):
    ys = [a["root"].y for a in am] + [a["pesc"].y for a in am] + [a["aL"].y for a in am]
    return (max(ys) + min(ys)) / 2 - sum(a["root"].y for a in am) / len(am)


# ---- bancos, cadeiras, máquinas

def _blocos(kit, ctx, h, blocos, am):
    k = ctx.k
    rects = []
    for pr in blocos:
        x, w, y, hh = pr.get("x", 0), pr.get("w", 8), pr.get("y", 0), pr.get("h", 4)
        a, b = ctx.p3(x, 0), ctx.p3(x + w, 0)
        rects.append({"y0": min(a.y, b.y), "y1": max(a.y, b.y), "zb": y * k, "zt": (y + hh) * k, "w": w * k, "h": hh * k, "pr": pr})
    # largura do estofado: cobre mãos/pés apoiados nele
    for r in rects:
        r["lx"] = 1.45
        r["xc"] = r["pr"].get("z", 0.0) * k
        if "larg" in r["pr"]:
            r["lx"] = r["pr"]["larg"] * k / 2
            continue
        for ch in ctx.chaves:
            for ef in ch["ef"].values():
                p = ef["baixo"]
                if ef["contato"] and r["y0"] - 0.3 <= p.y <= r["y1"] + 0.3 and abs(p.z - r["zt"]) < 0.5:
                    r["lx"] = max(r["lx"], abs(p.x) + 0.7)
    idd = ctx.id
    ctx.encosto = None
    for r in rects:
        n_antes = len(kit.objs)
        _bloco(kit, ctx, h, r, rects, am, idd, k)
        if abs(r["xc"]) > 1e-4:
            for o in kit.objs[n_antes:]:
                o.matrix_world = Matrix.Translation((r["xc"], 0, 0)) @ o.matrix_world


def _bloco(kit, ctx, h, r, rects, am, idd, k):
    if True:
        y0, y1, zb, zt, lx = r["y0"], r["y1"], r["zb"], r["zt"], r["lx"]
        inc = r["pr"].get("inc")
        if inc:
            # encosto inclinado saindo da borda de trás (lado -x 2D = +y no mundo) do assento
            comp = r["pr"].get("enc", 7.0) * k
            a = math.radians(float(inc))
            base = Vector((0, y1 - 0.2, zt - 0.35))
            topo = base + Vector((0, math.cos(a) * comp, math.sin(a) * comp))
            meio = (base + topo) / 2
            o = kit.caixa((0, 0, 0), (lx * 2, comp, 0.7), kit.estofado, 0.22)
            o.matrix_world = Matrix.Translation(meio) @ Matrix.Rotation(a, 4, "X")
            kit.viga(Vector((0, (base.y + topo.y) / 2 + 0.3, 0.3)), meio - Vector((0, 0, 0.5)), 0.55, 0.55, kit.quadro)
            kit.viga(Vector((0, y0 + 0.6, 0.3)), Vector((0, topo.y, 0.3)), 0.5, 0.4, kit.quadro)
            kit.viga((-1.7, topo.y - 0.4, 0.12), (1.7, topo.y - 0.4, 0.12), 0.55, 0.3, kit.quadro)
            ctx.encosto = (meio.y, topo.z)
        cy = (y0 + y1) / 2
        L = y1 - y0
        alto = r["h"] >= 6.5 and L <= 2.6
        if alto:
            # encosto/coluna/parede
            assento = [s for s in rects if s is not r and s["h"] < 6.5 and abs((s["y0"] + s["y1"]) / 2 - cy) < (s["y1"] - s["y0"]) / 2 + L + 1.0]
            if r["h"] >= 14:
                # espaldar (barras de parede): vazado, não esconde o corpo
                xm = max(4.0, max(max(abs(a["gL"].x), abs(a["gR"].x)) for a in am) + 1.2)
                for sx in (-1, 1):
                    kit.viga((sx * xm, cy, 0), (sx * xm, cy, zt), 0.5, 0.7, kit.madeira)
                zz = 1.2
                while zz < zt - 0.3:
                    kit.cil((-xm, cy, zz), (xm, cy, zz), 0.16, kit.madeira, 12)
                    zz += 1.6
                return
            if assento:
                zs = max(s["zt"] for s in assento)
                ctx.encosto = (cy, zt)
                kit.caixa((0, cy, (zs + zt) / 2 + 0.2), (lx * 2, max(L, 0.7), zt - zs - 0.4), kit.estofado, 0.25)
                kit.viga((0, cy + (0.6 if cy > assento[0]["y0"] else -0.6), 0.2), (0, cy + 0.6, zt - 1.0), 0.6, 0.6, kit.quadro)
            elif "scott" in idd:
                kit.viga((0, cy, 0.2), (0, cy, zt - 1.4), 0.6, 0.6, kit.quadro)
                kit.caixa((0, cy - 0.5, zt - 0.7), (lx * 2, 2.6, 0.7), kit.estofado, 0.25, rot=(math.radians(-35), 0, 0))
                kit.caixa((0, cy, 0.1), (3.0, 4.0, 0.2), kit.quadro, 0.05)
            elif any(x in idd for x in ("eliptico", "escada", "sled")):
                return  # aparelho dedicado (desenhado em _extras_maquina)
            else:
                # coluna de máquina (hack etc.): poste + console
                kit.viga((0, cy, 0.2), (0, cy, zt - 1.2), 0.7, 0.9, kit.quadro)
                kit.caixa((0, cy, zt - 0.6), (3.0, 1.2, 1.2), kit.preto, 0.2)
                kit.caixa((0, cy, 0.1), (4.0, 3.0, 0.2), kit.quadro, 0.05)
            return
        esp = min(0.75, max(0.3, r["h"] * 0.5))
        if any(s in idd for s in ("box-jump", "step")) and r["zb"] < 0.1:
            kit.caixa((0, cy, zt / 2), (5.0, L, zt), kit.madeira, 0.12)
            return
        if r["zb"] > 0.4:
            # almofada elevada (apoio de joelho/quadril) sobre um poste
            kit.caixa((0, cy, (zb + zt) / 2), (lx * 2, max(L, 0.8), max(zt - zb, 0.4)), kit.estofado, 0.25)
            kit.viga((0, cy, 0.15), (0, cy, zb), 0.55, 0.55, kit.quadro)
            kit.caixa((0, cy, 0.08), (3.0, 2.0, 0.16), kit.quadro, 0.05)
            return
        if r["h"] < 1.2:
            kit.caixa((0, cy, zt / 2), (lx * 2, L, zt), kit.quadro if "remo" in idd else kit.borracha, 0.06)
            return
        # banco/assento: estofado + estrutura
        kit.caixa((0, cy, zt - esp / 2), (lx * 2, L, esp), kit.estofado, 0.22)
        kit.caixa((0, cy, zt - esp - 0.12), (lx * 1.4, L * 0.9, 0.24), kit.quadro, 0.05)
        if L > 5.5:
            for yy in (y0 + 0.9, y1 - 0.9):
                kit.viga((0, yy, 0.25), (0, yy, zt - esp - 0.2), 0.55, 0.55, kit.quadro)
                kit.viga((-1.7, yy, 0.12), (1.7, yy, 0.12), 0.55, 0.3, kit.quadro)
            kit.viga((0, y0 + 0.9, 0.5), (0, y1 - 0.9, 0.5), 0.4, 0.4, kit.quadro)
        else:
            kit.viga((0, cy, 0.25), (0, cy, zt - esp - 0.2), 0.6, 0.6, kit.quadro)
            kit.viga((-1.6, cy, 0.12), (1.6, cy, 0.12), 0.55, 0.3, kit.quadro)
            kit.viga((0, cy - L / 2 + 0.3, 0.12), (0, cy + L / 2 - 0.3, 0.12), 0.55, 0.3, kit.quadro)


def _apoio_tornozelo(kit, ctx, pr, am):
    if "x" in pr:
        c = ctx.p3(pr.get("x", 0), pr.get("y", 1.0))
    else:
        a = am[0]
        c = (a["aL"] + a["aR"]) / 2 + Vector((0, 0.5, 0.35))
    kit.cil((-2.6, c.y, c.z), (2.6, c.y, c.z), 0.45, kit.estofado, 24)
    for sx in (-1, 1):
        kit.viga((sx * 2.9, c.y, 0.1), (sx * 2.9, c.y, c.z), 0.45, 0.45, kit.quadro)
    kit.caixa((0, c.y, 0.08), (6.4, 1.6, 0.16), kit.quadro, 0.04)


def preparar_alavancas(ctx, h):
    """Alavancas RÍGIDAS das máquinas (supino, voador/peck-deck, desenvolvimento): pivô fixo e comprimento constante.
    A mão é levada (IK, em todo quadro) ao ponto do arco da alavanca mais próximo da pose. Devolve {sf: (piv, eixo, L)}."""
    idd = ctx.id
    if "supino-maquina" in idd:
        tipo = "supino"
    elif "peck-deck" in idd or "voador" in idd:
        tipo = "peck"
    elif "desenvolvimento-maquina" in idd:
        tipo = "des"
    else:
        return None
    grips = {".L": [], ".R": []}
    omb = {}
    for i, c in enumerate(ctx.chaves):
        h.restaurar(c["est"])
        T = c["T"]
        for sf in grips:
            grips[sf].append(T @ h.pegada(sf))
            if i == 0:
                omb[sf] = T @ h.cabeca("upperarm01" + sf)
    cfg = {"tipo": tipo}
    for sf, sx in ((".L", 1), (".R", -1)):
        G = grips[sf]
        o = omb[sf]
        if tipo == "supino":
            ax = X.copy()
            piv = Vector((sx * (abs(o.x) + 3.2), o.y + 0.8, o.z - 1.0))  # por fora e abaixo do braço (não corta o ombro)
        elif tipo == "peck":
            ax = CIMA.copy()
            piv = Vector((sx * 1.9, o.y + 0.4, 0.0))
        else:
            ax = Vector((0, 1, 0))
            A, B = min(G, key=lambda p: p.z), max(G, key=lambda p: p.z)
            M = (A + B) / 2
            d = Vector((B.x - A.x, 0, B.z - A.z))
            nrm = Vector((d.z, 0, -d.x)).normalized() if d.length > 1e-3 else Vector((sx, 0, 0))
            if nrm.x * sx < 0:
                nrm = -nrm
            alvo_x = max(abs(p.x) for p in G) + 2.2
            t = (alvo_x - abs(M.x)) / max(abs(nrm.x), 0.2)
            piv = M + nrm * t
            piv.y = o.y + 1.4
        dist = []
        for g in G:
            r = g - piv
            dist.append((r - ax * r.dot(ax)).length)
        cfg[sf] = (piv, ax, sum(dist) / len(dist))
    return cfg


def _proj_alavanca(c, g):
    piv, ax, L = c
    r = g - piv
    a = r.dot(ax)
    rp = r - ax * a
    if rp.length < 1e-6:
        return g
    return piv + ax * a + rp.normalized() * L


def ik_alavancas(ctx, h, T):
    cfg = getattr(ctx, "alavancas", None)
    if not cfg:
        return
    Ti3 = T.inverted().to_3x3()
    for _ in range(2):
        for sf in (".L", ".R"):
            g = T @ h.pegada(sf)
            gn = _proj_alavanca(cfg[sf], g)
            h.ik("braco", sf, h.cabeca("wrist" + sf) + Ti3 @ (gn - g), h.rot("wrist" + sf))


def _bracos_maquina(kit, ctx, h, encosto):
    """Supino/peck-deck/desenvolvimento na máquina: pórtico atrás do encosto e alavancas rígidas (pivô fixo, comprimento
    constante, sempre por fora da largura dos ombros)."""
    y, zt = encosto
    cfg = getattr(ctx, "alavancas", None)
    for sx in (-1, 1):
        kit.viga((sx * 3.4, y + 1.2, 0.1), (sx * 3.4, y + 1.2, zt + 2.0), 0.5, 0.7, kit.quadro)
    kit.viga((-3.6, y + 1.2, zt + 2.0), (3.6, y + 1.2, zt + 2.0), 0.6, 0.7, kit.quadro)
    kit.caixa((0, y + 1.2, 0.1), (7.6, 2.6, 0.2), kit.quadro, 0.05)
    if not cfg:
        return
    tipo = cfg["tipo"]
    pega = {sf: kit.cil_movel(0.2, kit.preto, 14) for sf in (".L", ".R")}
    liga = {sf: kit.cil_movel(0.15, kit.metal, 12) for sf in (".L", ".R")}
    alav = {sf: kit.cil_movel(0.22, kit.quadro, 12) for sf in (".L", ".R")}
    eixo = {sf: kit.cil_movel(0.22, kit.quadro, 12) for sf in (".L", ".R")}
    zarm = {}
    for sf, sx in ((".L", 1), (".R", -1)):
        piv, ax, L = cfg[sf]
        if tipo == "supino":
            kit.disco(piv, 0.5, 0.6, kit.quadro, verts=20)
            kit.viga(piv, Vector((sx * 3.4, y + 1.2, piv.z)), 0.4, 0.4, kit.quadro)
            kit.viga(Vector((sx * 3.4, y + 1.2, piv.z)), Vector((sx * 3.4, y + 1.2, 0.1)), 0.45, 0.45, kit.quadro)
        elif tipo == "peck":
            h.restaurar(ctx.chaves[0]["est"])
            zarm[sf] = (ctx.chaves[0]["T"] @ h.pegada(sf)).z + 0.3  # alavanca na altura da mão (não cruza o bíceps)
            topo = Vector((piv.x, piv.y, zt + 2.0))
            kit.viga(topo, Vector((sx * 3.4, y + 1.2, zt + 2.0)), 0.5, 0.5, kit.quadro)
            kit.disco(topo - Vector((0, 0, 0.2)), 0.45, 0.5, kit.quadro, eixo=(0, 0, 1), verts=20)
            kit.cil(topo, Vector((piv.x, piv.y, zarm[sf])), 0.22, kit.quadro, 12)
        else:
            kit.disco(piv, 0.5, 0.6, kit.quadro, eixo=(0, 1, 0), verts=20)
            kit.viga(piv, Vector((piv.x, y + 1.2, piv.z)), 0.4, 0.4, kit.quadro)
            kit.viga(Vector((piv.x, y + 1.2, piv.z)), Vector((piv.x, y + 1.2, 0.1)), 0.45, 0.45, kit.quadro)

    def upd(est):
        h.restaurar(est["est"])
        T = est["T"]
        for sf, sx in ((".L", 1), (".R", -1)):
            piv, ax, L = cfg[sf]
            g = T @ h.pegada(sf)
            e = (T.to_3x3() @ h.eixo_polegar(sf)).normalized()
            if e.z < 0:
                e = -e
            Kit.por_cil(pega[sf], g - e * 0.75, g + e * 0.75)
            eixo[sf].hide_render = True
            if tipo == "supino":
                base = g - e * 0.7
                E = Vector((piv.x, base.y, base.z))
                Kit.por_cil(liga[sf], base, E)
                Kit.por_cil(alav[sf], E, piv)
            elif tipo == "peck":
                topo_m = g + e * 0.7
                cot = Vector((g.x, g.y, zarm[sf]))
                Kit.por_cil(liga[sf], topo_m, cot)
                Kit.por_cil(alav[sf], cot, Vector((piv.x, piv.y, zarm[sf])))
            else:
                E = Vector((g.x, piv.y, g.z))
                Kit.por_cil(liga[sf], g, E)
                Kit.por_cil(alav[sf], E, piv)
    kit.moveis.append(upd)


def _extras_maquina(kit, ctx, h, am, estados):
    idd = ctx.id
    if any(s in idd for s in ("supino-maquina", "peck-deck", "desenvolvimento-maquina", "voador")) and ctx.encosto is not None:
        _bracos_maquina(kit, ctx, h, ctx.encosto)
    if "leg-press" in idd or (idd.startswith("hack") and "hack" not in ctx.tipos):
        _plataforma_movel(kit, ctx, h, estados)
    if "hack" in ctx.tipos:
        _hack(kit, ctx, h, estados)
    if "extensora" in idd or "flexora" in idd and "mesa" not in idd:
        _rolo_canela(kit, ctx, h, frente="extensora" in idd)
    if "cadeira-flexora" in idd:
        _almofada_coxa(kit, ctx, h)
    if "mesa-flexora" in idd:
        _rolo_canela(kit, ctx, h, frente=False, prono=True)
    if "hiperextensao" in idd and "apoio_tornozelo" not in ctx.tipos:
        _rolo_aquiles(kit, ctx, h)
    if "abdutora" in idd or "adutora" in idd:
        _almofadas_joelho(kit, ctx, h, fora="abdutora" in idd)
    if "remo-ergometro" in idd:
        _assento_remo(kit, ctx, h)
    if "eliptico" in idd or "eliptico" in ctx.tipos:
        _eliptico(kit, ctx, h, am)
    if "scott" in idd:
        _apoio_scott(kit, ctx, h)
    _pegadores(kit, ctx, h)
    if "roda" in ctx.tipos:
        _roda(kit, ctx, h)


def _pegadores(kit, ctx, h):
    """Pegadores das máquinas/aparelhos onde as mãos se fecham (fixos no mundo ou presos à alavanca)."""
    cfg = getattr(ctx, "pegadores", None)
    if not cfg:
        return
    tipo = cfg["tipo"]
    Y, Z = Vector((0, 1, 0)), Vector((0, 0, 1))
    if tipo == "assento":
        for sf, sx in ((".L", 1), (".R", -1)):
            p, e = cfg[sf]
            if abs(e.x) > 0.5:
                kit.cil(p - X * 1.0, p + X * 1.0, 0.2, kit.preto, 16)
                kit.viga(p - X * (sx * 1.0), Vector((sx * 1.2, p.y + 0.9, p.z - 0.8)), 0.3, 0.3, kit.quadro)
            else:
                kit.cil(p - e * 1.2, p + e * 1.2, 0.2, kit.preto, 16)
                kit.viga(p + e * 1.2, Vector((sx * 1.5, p.y + 1.2, p.z - 0.7)), 0.3, 0.3, kit.quadro)
                kit.viga(p - e * 1.2, Vector((sx * 1.5, p.y - 1.2, p.z - 0.7)), 0.3, 0.3, kit.quadro)
    elif tipo == "mesa":
        for sf, sx in ((".L", 1), (".R", -1)):
            p, e = cfg[sf]
            kit.cil(p - e * 0.7, p + e * 0.7, 0.2, kit.preto, 16)
            kit.viga(p - e * sx * 0.7, Vector((sx * 0.9, p.y, p.z + 0.85)), 0.3, 0.3, kit.quadro)
    elif tipo == "escada":
        for sf, sx in ((".L", 1), (".R", -1)):
            p, e = cfg[sf]
            a, b = p - Y * 3.2, p + Y * 2.2
            kit.cil(a, b, 0.17, kit.metal, 16)
            kit.cil(Vector((a.x, a.y, a.z)), Vector((a.x, a.y - 0.6, 0.2)), 0.2, kit.quadro, 12)
            kit.cil(Vector((b.x, b.y, b.z)), Vector((b.x, b.y, 0.2)), 0.2, kit.quadro, 12)
        _escada(kit, ctx, h, cfg)
    elif tipo == "treno":
        _treno(kit, ctx, h, cfg)
    elif tipo == "coxa":
        pad = kit.cil_movel(0.55, kit.estofado, 24)
        peg = {sf: kit.cil_movel(0.2, kit.preto, 14) for sf in (".L", ".R")}
        hastes = [kit.cil_movel(0.16, kit.quadro, 12) for _ in range(2)]

        def upd(est):
            h.restaurar(est["est"])
            T = est["T"]
            jL, jR = T @ h.cabeca("lowerleg01.L"), T @ h.cabeca("lowerleg01.R")
            qL = T @ h.cabeca("upperleg01.L")
            j = (jL + jR) / 2
            c = j + (qL - jL) * 0.16
            P = h.proxy(T)
            mm = (h.px_partes["coxa_f"] | h.px_partes["coxa_t"]) & (np.abs(P[:, 1] - c.y) < 0.6)
            ztop = float(P[mm, 2].max()) if mm.any() else c.z + 0.6
            c = Vector((0, c.y, ztop + 0.56))
            Kit.por_cil(pad, Vector((-2.4, c.y, c.z)), Vector((2.4, c.y, c.z)))
            for (sf, sx), o in zip(((".L", 1), (".R", -1)), hastes):
                a_ = _alvo_pegador(ctx, h, T, sf, sx)
                Kit.por_cil(peg[sf], a_[0] - a_[1] * 0.7, a_[0] + a_[1] * 0.7)
                Kit.por_cil(o, Vector((sx * 2.2, c.y - 0.3, c.z - 0.3)), Vector((sx * 2.2, c.y - 2.4, 0.2)))
        kit.moveis.append(upd)
    elif tipo == "hack":
        pass  # pegadores desenhados em _hack (presos às ombreiras)


def _roda(kit, ctx, h):
    """Roda abdominal: disco no chão sob as mãos, eixo lateral com manoplas; gira conforme anda (ângulo = desloc./raio)."""
    R = RAIO_RODA
    ps = [kit.disco((0, 0, 0), R, 0.55, kit.borracha, verts=40), kit.disco((0, 0, 0), R * 0.62, 0.6, kit.brasa, verts=32)]
    for a in range(3):
        ang = a * math.pi / 3
        ps.append(kit.caixa((0, 0, 0), (0.62, 2 * R * 0.6, 0.1), kit.metal, 0.02, rot=(ang, 0, 0)))
    disco = kit.grupo_movel(ps)
    eixo = kit.cil_movel(0.08, kit.metal, 10)
    mans = {sf: kit.cil_movel(0.2, kit.preto, 14) for sf in (".L", ".R")}
    y0 = {}

    def upd(est):
        h.restaurar(est["est"])
        T = est["T"]
        g = (T @ h.pegada(".L") + T @ h.pegada(".R")) / 2
        c = Vector((0, g.y, ctx.z0 + R))
        y0.setdefault("y", g.y)
        ang = (g.y - y0["y"]) / R
        disco.matrix_world = Matrix.Translation(c) @ Matrix.Rotation(ang, 4, "X")
        Kit.por_cil(eixo, c - X * 1.35, c + X * 1.35)
        for sf, sx in ((".L", 1), (".R", -1)):
            Kit.por_cil(mans[sf], c + X * (sx * 0.45), c + X * (sx * 1.75))
    kit.moveis.append(upd)


def _treno(kit, ctx, h, cfg):
    """Trenó (sled): base com esquis no chão, dois postes verticais (onde as mãos seguram) e anilhas sobre a base."""
    pL, _ = cfg[".L"]
    y = pL.y
    zt = pL.z + 1.6
    yb = y - 2.0
    for sx in (-1, 1):
        kit.viga((sx * 2.0, yb - 2.2, 0.12), (sx * 2.0, yb + 2.2, 0.12), 0.35, 0.24, kit.metal)  # esquis
        kit.cil((sx * 2.1, y, 0.3), (sx * 2.1, y, zt), 0.19, kit.metal, 16)  # postes (pegadores)
        kit.cil((sx * 2.1, y, 0.5), (sx * 1.4, yb, 0.5), 0.15, kit.quadro, 12)
    kit.caixa((0, yb, 0.4), (4.0, 3.6, 0.3), kit.quadro, 0.05)
    kit.cil((0, yb, 0.55), (0, yb, 2.4), 0.2, kit.metal, 12)
    for i in range(3):
        kit.disco((0, yb, 0.8 + i * 0.45), 2.0, 0.4, kit.borracha, eixo=(0, 0, 1), verts=40)
    kit.cil((-2.1, y, zt - 0.2), (2.1, y, zt - 0.2), 0.15, kit.quadro, 12)


def _escada(kit, ctx, h, cfg):
    """Stair climber: escada rolante de degraus largos à frente; os pés pisam sempre num degrau (o degrau acompanha o pé)."""
    p, _ = cfg[".L"]
    est0 = ctx._estados
    ys = []
    for est in est0[:: max(1, len(est0) // 8)]:
        h.restaurar(est["est"])
        ys += [(est["T"] @ h.cabeca("toe3-1" + sf)).y for sf in (".L", ".R")]
    yf = min(ys) - 1.4
    # estrutura: laterais inclinadas + console na altura do peito
    for sx in (-1, 1):
        kit.viga((sx * 2.9, yf, 0.2), (sx * 2.9, yf - 0.6, p.z + 2.0), 0.5, 0.6, kit.quadro)
        kit.viga((sx * 2.9, yf + 5.5, 0.15), (sx * 2.9, yf - 0.4, 0.15), 0.5, 0.3, kit.quadro)
    kit.caixa((0, yf - 0.6, p.z + 2.3), (5.4, 1.2, 1.0), kit.preto, 0.2, rot=(math.radians(-25), 0, 0))
    kit.caixa((0, yf - 0.3, 2.5), (4.6, 0.8, 5.0), kit.quadro, 0.1)
    degs = {sf: kit.caixa((0, 0, 0), (2.2, 2.6, 0.3), kit.borracha, 0.05) for sf in (".L", ".R")}
    rods = {sf: kit.cil_movel(0.15, kit.metal, 10) for sf in (".L", ".R")}

    def upd(est):
        h.restaurar(est["est"])
        T = est["T"]
        P = h.proxy(T)
        for sf, ef, sx in ((".L", "pe_f", 1), (".R", "pe_t", -1)):
            pts = P[h.px_partes[ef]]
            z = float(pts[:, 2].min())
            sol = pts[pts[:, 2] < z + 0.25].mean(axis=0)
            c = Vector((sx * 1.15, sol[1] - 0.2, z - 0.15))
            degs[sf].matrix_world = Matrix.Translation(c)
            Kit.por_cil(rods[sf], c + Vector((0, -1.0, 0)), Vector((sx * 1.15, yf - 0.2, c.z * 0.5 + 0.3)))
    kit.moveis.append(upd)


def _apoio_scott(kit, ctx, h):
    """Banco Scott: almofada inclinada sob os braços (na direção do braço da 1ª chave), sobre a coluna."""
    h.restaurar(ctx.chaves[0]["est"])
    T = ctx.chaves[0]["T"]
    omb = [T @ h.cabeca("upperarm01" + sf) for sf in (".L", ".R")]
    cot = [T @ h.cabeca("lowerarm01" + sf) for sf in (".L", ".R")]
    meio = sum((o + c for o, c in zip(omb, cot)), Vector()) / 4
    d = (sum(cot, Vector()) / 2 - sum(omb, Vector()) / 2)
    d.x = 0
    d.normalize()
    nrm = d.cross(X)
    if nrm.z < 0:
        nrm = -nrm
    centro = meio - nrm * 1.0 + d * 0.2
    o = kit.caixa((0, 0, 0), (5.6, 4.2, 0.9), kit.estofado, 0.3)
    o.matrix_world = Matrix.Translation(centro) @ _alinhar(Vector((0, 1, 0)), d).to_3x3().to_4x4() @ Matrix.Identity(4)
    # garante que o "cima" da almofada é a normal
    up = (o.matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized()
    if up.dot(nrm) < 0:
        o.matrix_world = o.matrix_world @ Matrix.Rotation(math.pi, 4, "Y")
    kit.viga(Vector((0, centro.y - d.y * 1.0, 0.1)), centro - nrm * 0.3 - d * 1.0, 0.6, 0.6, kit.quadro)
    kit.caixa((0, centro.y, 0.1), (3.0, 3.0, 0.2), kit.quadro, 0.05)


def _eliptico(kit, ctx, h, am):
    """Elíptico: coluna e console à frente dos pés (na altura do peito), trilho no chão, pedais sob os pés (o pé nunca sai
    do pedal) com bielas até a roda da frente e alças móveis que as mãos seguram (pivô no alto da coluna)."""
    cfg = ctx.pegadores or {}
    yc, piv = cfg.get("yc", am[0]["root"].y - 5), cfg.get("piv", {})
    ytr = max(a["root"].y for a in am) + 4.0
    kit.viga((0, yc + 0.4, 0.25), (0, ytr, 0.25), 0.9, 0.4, kit.quadro)
    kit.caixa((0, ytr, 0.15), (3.8, 1.2, 0.3), kit.quadro, 0.05)
    kit.caixa((0, yc, 0.15), (3.8, 1.6, 0.3), kit.quadro, 0.05)
    zc = cfg.get("zc", 13.0)
    kit.viga((0, yc, 0.3), (0, yc - 0.8, zc - 0.6), 0.8, 0.9, kit.quadro)
    kit.caixa((0, yc - 0.9, zc), (2.6, 1.0, 1.0), kit.preto, 0.2, rot=(math.radians(-30), 0, 0))
    kit.disco((0, yc + 0.6, 1.6), 1.4, 1.0, kit.preto, verts=40)
    ped = {sf: kit.caixa((0, 0, 0), (1.3, 3.2, 0.25), kit.borracha, 0.05) for sf in (".L", ".R")}
    biela = {sf: kit.cil_movel(0.16, kit.quadro, 10) for sf in (".L", ".R")}
    alca = {sf: kit.cil_movel(0.17, kit.metal, 12) for sf in (".L", ".R")}
    alca_b = {sf: kit.cil_movel(0.16, kit.quadro, 10) for sf in (".L", ".R")}

    def upd(est):
        h.restaurar(est["est"])
        T = est["T"]
        P = h.proxy(T)
        for sf, ef, sx in ((".L", "pe_f", 1), (".R", "pe_t", -1)):
            pts = P[h.px_partes[ef]]
            sol = pts[pts[:, 2] < pts[:, 2].min() + 0.25].mean(axis=0)
            c = Vector((sx * 1.0, sol[1], pts[:, 2].min() - 0.13))
            ped[sf].matrix_world = Matrix.Translation(c)
            Kit.por_cil(biela[sf], c + Vector((0, -1.4, 0)), Vector((sx * 0.9, yc + 0.6, 1.6)))
            g = T @ h.pegada(sf)
            pv = piv.get(sf, Vector((sx * 1.6, yc, 7.0)))
            e = (g - pv).normalized()
            Kit.por_cil(alca[sf], pv, g + e * 0.9)
            Kit.por_cil(alca_b[sf], pv, Vector((sx * 0.9, c.y - 1.2, c.z + 0.2)))
    kit.moveis.append(upd)


def _eixos_tronco(h, T):
    """(quadril, eixo do tronco u (quadril->pescoço), normal das costas nb) no mundo."""
    r = T @ h.cabeca("root")
    u = (T @ h.cabeca("neck01") - r).normalized()
    nb = u.cross(X).normalized()
    if nb.y < 0:
        nb = -nb
    return r, u, nb


def _hack(kit, ctx, h, estados):
    """Hack squat: encosto inclinado e ombreiras num carrinho que corre em trilhos paralelos ao tronco,
    plataforma inclinada fixa sob os pés, pegadores ao lado das ombreiras."""
    # espessura das costas atrás do eixo do tronco (quadro-chave 0)
    h.restaurar(ctx.chaves[0]["est"])
    T0 = ctx.chaves[0]["T"]
    r0, u0, nb0 = _eixos_tronco(h, T0)
    P = h.proxy(T0)
    m = h.px_partes["tronco"] & (np.abs(P[:, 0]) < 1.6)
    Q = P[m] - np.array(r0)
    off = float((Q @ np.array(nb0)).max()) if len(Q) else 1.2
    dims = (3.4, 6.4, 0.7)
    encosto = kit.caixa((0, 0, 0), dims, kit.estofado, 0.25)
    carro = kit.caixa((0, 0, 0), (2.8, 7.0, 0.35), kit.quadro, 0.06)
    ombro = {sf: kit.cil_movel(0.5, kit.estofado, 20) for sf in (".L", ".R")}
    haste = {sf: kit.cil_movel(0.16, kit.quadro, 12) for sf in (".L", ".R")}
    pega = {sf: kit.cil_movel(0.17, kit.preto, 12) for sf in (".L", ".R")}
    braco_p = {sf: kit.cil_movel(0.14, kit.quadro, 12) for sf in (".L", ".R")}

    def geo(est):
        h.restaurar(est["est"])
        T = est["T"]
        r, u, nb = _eixos_tronco(h, T)
        c = r + u * 2.5 + nb * (off + dims[2] / 2 + 0.05)
        return T, r, u, nb, c

    cs = [geo(e)[4] for e in estados]
    _, _, u_m, nb_m, _ = geo(estados[0])
    proj = [float((c - cs[0]).dot(u_m)) for c in cs]
    lo, hi = cs[int(np.argmin(proj))], cs[int(np.argmax(proj))]
    base_tr = nb_m * (dims[2] / 2 + 0.6)
    a_tr = lo - u_m * (dims[1] / 2 + 1.0) + base_tr
    b_tr = hi + u_m * (dims[1] / 2 + 1.6) + base_tr
    if a_tr.z < 0.4:
        a_tr = a_tr + u_m * ((0.4 - a_tr.z) / max(u_m.z, 0.2))
    for sx in (-1, 1):
        kit.viga(a_tr + X * sx * 1.7, b_tr + X * sx * 1.7, 0.45, 0.55, kit.metal)
        kit.viga(Vector((sx * 1.7, b_tr.y, 0.1)), b_tr + X * sx * 1.7 + Vector((0, 0, 0.3)), 0.6, 0.6, kit.quadro)
        kit.viga(Vector((sx * 1.7, a_tr.y, 0.1)), a_tr + X * sx * 1.7, 0.6, 0.6, kit.quadro)
    kit.viga(b_tr + Vector((-2.1, 0, 0.3)), b_tr + Vector((2.1, 0, 0.3)), 0.5, 0.5, kit.quadro)
    # plataforma inclinada sob os pés (fixa) + base no chão até os trilhos
    pc, pn = _plataforma(h, T0)
    up = -pn
    f_dir = (FRENTE - up * FRENTE.dot(up)).normalized()
    centro = pc + up * (-0.17) + f_dir * 0.4
    Rp = Matrix((X, f_dir, up)).transposed().to_4x4()
    plat = kit.caixa((0, 0, 0), (7.0, 5.2, 0.34), kit.quadro, 0.06)
    plat.matrix_world = Matrix.Translation(centro) @ Rp
    bor = kit.caixa((0, 0, 0), (6.6, 4.8, 0.06), kit.borracha, 0.02)
    bor.matrix_world = Matrix.Translation(centro + up * 0.18) @ Rp
    y_fr = centro.y - 2.6
    if centro.z > 0.5:
        for sx in (-1, 1):
            kit.viga(Vector((sx * 3.0, centro.y, 0.1)), centro + Vector((sx * 3.0, 0, -0.2)), 0.5, 0.5, kit.quadro)
    for sx in (-1, 1):
        kit.viga(Vector((sx * 2.3, y_fr, 0.2)), Vector((sx * 2.3, b_tr.y + 0.6, 0.2)), 0.5, 0.4, kit.quadro)
    for yy in (y_fr, b_tr.y + 0.6):
        kit.viga(Vector((-2.8, yy, 0.18)), Vector((2.8, yy, 0.18)), 0.6, 0.36, kit.quadro)
    estado_ini = estados[0]

    def upd(est):
        T, r, u, nb, c = geo(est)
        R = Matrix((X, u, nb)).transposed().to_4x4()
        encosto.matrix_world = Matrix.Translation(c) @ R
        carro.matrix_world = Matrix.Translation(c + nb * (dims[2] / 2 + 0.25)) @ R
        for sf, sx in ((".L", 1), (".R", -1)):
            S = T @ h.cabeca("upperarm01" + sf)
            topo = S + u * 0.95
            Kit.por_cil(ombro[sf], topo + nb * 0.9, topo - nb * 1.5)
            Kit.por_cil(haste[sf], topo + nb * 0.8, c + X * sx * 1.3 + u * (dims[1] / 2 - 0.4) + nb * 0.6)
            g = T @ h.pegada(sf)
            e = T.to_3x3() @ h.eixo_polegar(sf)
            Kit.por_cil(pega[sf], g - e * 0.6, g + e * 0.6)
            lado = c + u * float((g - c).dot(u)) + X * sx * (dims[0] / 2 - 0.2) + nb * 0.2
            Kit.por_cil(braco_p[sf], g + X * sx * 0.3, lado)
    kit.moveis.append(upd)
    _ = estado_ini


def _plataforma_movel(kit, ctx, h, estados):
    cs = []
    for est in estados:
        h.restaurar(est["est"])
        cs.append(_plataforma(h, est["T"]))
    c0 = min(cs, key=lambda c: c[0].z)[0]
    c1 = max(cs, key=lambda c: (c[0] - c0).length)[0]
    d = (c1 - c0)
    if d.length < 0.5:
        d = cs[0][1].copy()
    d.normalize()
    n0 = cs[0][1]
    # trilho só do lado de cima (não passa pelas pernas, no lado do assento) e por fora da placa larga
    ext0, ext1 = c0 + n0 * 0.8, c1 + d * 3.0 + n0 * 0.8
    for p in (ext0, ext1):
        if p.z < 0.3:
            # não deixa o trilho entrar no chão
            t = (0.3 - p.z) / max(abs(d.z), 1e-3)
            p += d * (t if p is ext0 else -t) if abs(d.z) > 1e-3 else Vector((0, 0, 0.3 - p.z))
    for s in (-1, 1):
        kit.viga(ext0 + X * s * 4.4, ext1 + X * s * 4.4, 0.45, 0.45, kit.quadro)
    for p in (ext0, ext1):
        if p.z > 0.4:
            for s in (-1, 1):
                kit.viga((s * 4.4, p.y, 0.1), (s * 4.4, p.y, p.z), 0.45, 0.45, kit.quadro)
    ps = [kit.caixa((0, 0, 0.15), (8.0, 5.4, 0.3), kit.quadro, 0.06), kit.caixa((0, 0, -0.02), (7.6, 5.0, 0.06), kit.borracha, 0.02)]
    for s in (-1, 1):
        ps.append(kit.caixa((s * 4.1, 0, 0.3), (0.7, 1.4, 0.5), kit.quadro, 0.05))  # guias da placa nos trilhos
    pl = kit.grupo_movel(ps)

    def upd(est):
        h.restaurar(est["est"])
        c, n = _plataforma(h, est["T"])
        pl.matrix_world = Matrix.Translation(Vector((0, c.y, c.z))) @ _rot_placa(n)
    kit.moveis.append(upd)


def _rolo_canela(kit, ctx, h, frente=True, prono=False):
    rolo = kit.cil_movel(0.5, kit.estofado, 24)
    bracos = [kit.cil_movel(0.18, kit.quadro, 12) for _ in range(2)]
    eixo = kit.cil((-3.4, 0, 0), (3.4, 0, 0), 0.25, kit.quadro, 16)
    eixo.hide_render = True

    def upd(est):
        h.restaurar(est["est"])
        T = est["T"]
        aL, aR = T @ h.cabeca("foot.L"), T @ h.cabeca("foot.R")
        jL, jR = T @ h.cabeca("lowerleg01.L"), T @ h.cabeca("lowerleg01.R")
        a = (aL + aR) / 2
        j = (jL + jR) / 2
        s = (a - j).normalized()
        if prono:
            # de bruços: o rolo fica sobre o tendão de Aquiles (lado de cima/posterior da perna, longe do banco)
            f = Vector((0, 0, 1)) - s * s.z
            f = f.normalized() if f.length > 1e-3 else Vector((0, 0, 1))
        else:
            fw = T.to_3x3() @ FRENTE
            f = (fw - s * fw.dot(s)).normalized()
            f = f if frente else -f
        c = a - s * 0.55 + f * 0.85
        Kit.por_cil(rolo, c - X * 2.6, c + X * 2.6)
        for o, sx in zip(bracos, (-1, 1)):
            Kit.por_cil(o, Vector((sx * 2.9, j.y, j.z)), Vector((sx * 2.9, c.y, c.z)))
    kit.moveis.append(upd)


def _rolo_aquiles(kit, ctx, h):
    """Hiperextensão (banco romano): rolo que trava os tornozelos por trás, logo acima dos calcanhares."""
    h.restaurar(ctx.chaves[0]["est"])
    T = ctx.chaves[0]["T"]
    a = (T @ h.cabeca("foot.L") + T @ h.cabeca("foot.R")) / 2
    j = (T @ h.cabeca("lowerleg01.L") + T @ h.cabeca("lowerleg01.R")) / 2
    t3 = (T @ h.cabeca("toe3-1.L") + T @ h.cabeca("toe3-1.R")) / 2
    s_ = (a - j).normalized()
    fr = (t3 - a)
    fr = (fr - s_ * fr.dot(s_)).normalized()
    c = a - s_ * 0.9 - fr * 0.95
    kit.cil((-2.4, c.y, c.z), (2.4, c.y, c.z), 0.45, kit.estofado, 24)
    for sx in (-1, 1):
        kit.viga((sx * 2.7, c.y, c.z), (sx * 2.7, c.y, 0.1), 0.4, 0.4, kit.quadro)


def _almofada_coxa(kit, ctx, h):
    """Cadeira flexora: almofada fixa sobre as coxas, logo acima dos joelhos (segura o quadril no assento)."""
    h.restaurar(ctx.chaves[0]["est"])
    T = ctx.chaves[0]["T"]
    j = (T @ h.cabeca("lowerleg01.L") + T @ h.cabeca("lowerleg01.R")) / 2
    q = (T @ h.cabeca("upperleg01.L") + T @ h.cabeca("upperleg01.R")) / 2
    c = q + (j - q) * 0.78
    zs = []
    for est in ctx._estados[:: max(1, len(ctx._estados) // 12)]:
        h.restaurar(est["est"])
        P = h.proxy(est["T"])
        m = (h.px_partes["coxa_f"] | h.px_partes["coxa_t"]) & (np.abs(P[:, 1] - c.y) < 1.1)
        if m.any():
            zs.append(float(P[m, 2].max()) + 0.06)
    zt = max(zs) if zs else c.z + 0.8
    kit.cil((-2.6, c.y, zt + 0.55), (2.6, c.y, zt + 0.55), 0.55, kit.estofado, 24)
    for sx in (-1, 1):
        kit.viga((sx * 2.9, c.y, zt + 0.55), (sx * 2.9, c.y + 1.5, 0.4), 0.4, 0.4, kit.quadro)


def _almofadas_joelho(kit, ctx, h, fora=True):
    pads = [kit.cil_movel(0.9, kit.estofado, 24) for _ in range(2)]

    def upd(est):
        h.restaurar(est["est"])
        T = est["T"]
        for o, sf, sx in zip(pads, (".L", ".R"), (1, -1)):
            j = T @ h.cabeca("lowerleg01" + sf)
            q = T @ h.cabeca("upperleg02" + sf)
            c = q + (j - q) * 0.85
            off = X * sx * (0.95 if fora else -0.95)
            Kit.por_cil(o, c + off - X * sx * 0.2, c + off + X * sx * 0.25)
    kit.moveis.append(upd)


def _assento_remo(kit, ctx, h):
    """Remo: assento com rodinhas que desliza no trilho, sempre sob os ísquios (topo = pele mais baixa da pelve)."""
    banco = kit.caixa((0, 0, 0), (2.4, 2.6, 0.5), kit.estofado, 0.2)
    carro = kit.caixa((0, 0, 0), (1.6, 2.2, 0.3), kit.quadro, 0.05)

    def upd(est):
        h.restaurar(est["est"])
        T = est["T"]
        P = h.proxy(T)
        m = h.px_partes["tronco"] & (np.abs(P[:, 0]) < 1.3)
        Q = P[m]
        zb = float(Q[:, 2].min())
        y = float(Q[Q[:, 2] < zb + 0.3][:, 1].mean())
        banco.matrix_world = Matrix.Translation((0, y, zb - 0.25))
        carro.matrix_world = Matrix.Translation((0, y, max(zb - 0.65, 0.5)))
    kit.moveis.append(upd)


# ---- cardio

def _esteira(kit, ctx, root_y, am):
    zt = ALTURA_ESTEIRA
    cy = root_y + 1.0
    kit.caixa((0, cy, zt / 2 - 0.03), (5.6, 17, zt - 0.06), kit.quadro, 0.12)
    kit.caixa((0, cy, zt - 0.02), (4.4, 16.2, 0.04), kit.borracha, 0.01)
    for s in (-1, 1):
        kit.caixa((s * 2.6, cy, zt), (0.5, 17, 0.12), kit.cinza, 0.04)
    frente = cy - 8.5
    kit.caixa((0, frente - 0.4, 0.55), (5.8, 2.0, 1.1), kit.quadro, 0.3)
    topo = 11.5
    for s in (-1, 1):
        kit.viga((s * 2.5, frente - 0.6, 0.9), (s * 2.5, frente - 1.4, topo), 0.45, 0.6, kit.quadro)
        kit.cil((s * 2.6, frente - 1.2, 9.6), (s * 2.6, frente + 3.2, 9.6), 0.16, kit.metal, 16)
    kit.caixa((0, frente - 1.5, topo + 0.3), (5.6, 1.4, 1.1), kit.preto, 0.25, rot=(math.radians(-25), 0, 0))
    kit.caixa((0, frente - 1.0, topo - 0.3), (5.2, 0.2, 0.5), kit.brasa, 0.05)


def _bike(kit, ctx, h, am):
    """Bicicleta ergométrica (spinning): volante na frente, quadro, canote inclinado com selim, guidão à frente do selim."""
    b = ctx.bike or {"c": am[0]["root"] + Vector((0, -3, -5)), "r": 1.7}
    c, r = b["c"], b["r"]
    a0 = am[0]
    selim = b.get("selim") or Vector((0, a0["root"].y + 0.3, a0["root"].z - 0.95))
    # sentado: o selim fica sob os ísquios (o 2D não conhece a espessura da pelve)
    h.restaurar(ctx.chaves[0]["est"])
    P = h.proxy(ctx.chaves[0]["T"])
    m = h.px_partes["tronco"] & (np.abs(P[:, 0]) < 1.3)
    if m.any() and not b.get("em_pe"):
        Q = P[m]
        zb = Q[:, 2].min()
        fundo = Q[Q[:, 2] < zb + 0.3]
        if b.get("selim") is None or zb - b["selim"].z < 1.5:
            selim = Vector((0, float(fundo[:, 1].mean()), zb - 0.02))
    guidao = b.get("guidao") or (a0["gL"] + a0["gR"]) / 2
    gx = b.get("gx", 2.0)
    cx = Vector((0, c.y, c.z))
    # volante na frente do movimento central, entre as canelas
    fw = Vector((0, min(c.y - 3.1, guidao.y + 1.2), c.z + 0.7))
    rv = 2.25
    y_tras = selim.y + 2.6
    y_fr = fw.y - 1.6
    for yy in (y_tras, y_fr):
        kit.viga((-2.5, yy, 0.18), (2.5, yy, 0.18), 0.7, 0.36, kit.quadro)
        for s_ in (-1, 1):
            kit.caixa((s_ * 2.3, yy, 0.05), (0.6, 0.8, 0.1), kit.borracha, 0.03)
    # quadro: base, perna de trás até o movimento central, garfo do volante
    kit.viga((0, y_tras, 0.3), (0, y_fr, 0.3), 0.6, 0.45, kit.quadro)
    kit.viga((0, y_tras - 0.3, 0.4), cx, 0.6, 0.6, kit.quadro)
    kit.viga((0, y_fr + 0.3, 0.4), fw, 0.55, 0.55, kit.quadro)
    # coluna da frente (do volante ao guidão) e tubo diagonal até o movimento central
    topo_g = Vector((0, guidao.y - 0.9, guidao.z - 1.1))
    base_g = Vector((0, fw.y + 0.4, fw.z + rv + 0.3))
    kit.viga(cx, base_g, 0.75, 0.6, kit.quadro)
    kit.viga(fw, base_g, 0.5, 0.5, kit.quadro)
    kit.viga(base_g, topo_g, 0.7, 0.7, kit.quadro)
    # canote inclinado para trás, saindo do movimento central até o selim
    sel_base = selim - Vector((0, 0, 0.45))
    kit.viga(cx + Vector((0, 0.2, 0.3)), sel_base, 0.7, 0.7, kit.quadro)
    kit.cil(sel_base - (sel_base - cx).normalized() * 1.2, sel_base + Vector((0, 0, 0.2)), 0.2, kit.metal, 16)
    # selim: traseira larga + bico estreito para a frente (topo em selim.z)
    kit.caixa(selim + Vector((0, 0.45, -0.2)), (1.9, 1.3, 0.4), kit.estofado, 0.18)
    kit.caixa(selim + Vector((0, -0.55, -0.22)), (0.8, 1.6, 0.34), kit.estofado, 0.15)
    # guidão: mesa saindo da coluna, travessa e manoplas onde as mãos seguram
    kit.viga(topo_g, topo_g + Vector((0, 0, 0.5)), 0.5, 0.5, kit.quadro)
    mesa = topo_g + Vector((0, 0, 0.5))
    kit.cil(Vector((-gx + 0.2, mesa.y, mesa.z)), Vector((gx - 0.2, mesa.y, mesa.z)), 0.17, kit.metal, 16)
    for s_ in (-1, 1):
        kit.cil(Vector((s_ * (gx - 0.2), mesa.y, mesa.z)), Vector((s_ * gx, guidao.y, guidao.z)), 0.16, kit.metal, 16)
        kit.cil(Vector((s_ * (gx - 0.7), guidao.y, guidao.z)), Vector((s_ * (gx + 0.7), guidao.y, guidao.z)), 0.2, kit.preto, 16)
    kit.caixa(mesa + Vector((0, -0.3, 0.45)), (1.2, 0.4, 0.8), kit.preto, 0.1, rot=(math.radians(-25), 0, 0))
    # volante (carenagem preta, aro metálico, detalhe laranja) e eixo
    kit.disco(fw, rv, 0.45, kit.preto, verts=56)
    for s_ in (-1, 1):
        kit.toro(fw + Vector((s_ * 0.24, 0, 0)), rv - 0.08, 0.07, kit.metal)
        kit.toro(fw + Vector((s_ * 0.25, 0, 0)), rv * 0.55, 0.06, kit.brasa)
    kit.disco(fw, 0.35, 0.8, kit.metal, verts=24)
    kit.disco(cx, 0.42, 1.3, kit.quadro, verts=24)  # movimento central
    kit.disco(cx + Vector((0.5, 0, 0)), 1.0, 0.08, kit.preto, verts=40)  # coroa
    kit.toro(cx + Vector((0.5, 0, 0)), 0.97, 0.05, kit.metal)
    bracos = {sf: kit.cil_movel(0.14, kit.metal, 12) for sf in (".L", ".R")}
    pedais = {sf: kit.cil_movel(0.12, kit.preto, 8) for sf in (".L", ".R")}

    def upd(est):
        ped = est["extras"].get("pedais")
        if not ped:
            return
        for sf, sx in ((".L", 1), (".R", -1)):
            p = ped[sf]
            pc = Vector((sx * 0.75, p.y, p.z - 0.25))
            Kit.por_cil(bracos[sf], Vector((sx * 0.75, c.y, c.z)), pc)
            q = Vector((p.x, p.y, p.z - 0.25))
            Kit.por_cil(pedais[sf], Vector((sx * 0.7, q.y, q.z)), Vector((sx * max(abs(q.x) + 0.6, 1.6), q.y, q.z)))
    kit.moveis.append(upd)


# ---- polias e elásticos

def _maos(h, est):
    h.restaurar(est["est"])
    T = est["T"]
    return T @ h.pegada(".L"), T @ h.pegada(".R")


def _polia(kit, ctx, pr, am):
    A = ctx.p3(*pr["ate"][:3])
    h = ctx.h
    hip = am[0]["root"]
    corda = tipo_cabo(ctx) == "corda"
    dupla = "crossover" in ctx.id or bool(pr.get("dupla"))
    remo = "remo" in ctx.id
    polias = []
    if remo:
        kit.disco(A, 1.7, 1.2, kit.quadro, verts=48)
        kit.toro(A + Vector((0.65, 0, 0)), 1.3, 0.07, kit.brasa)
        tras = ctx.p3(-11, 0.8)
        kit.viga(Vector((0, A.y, 0.6)), Vector((0, tras.y, 0.6)), 1.0, 0.35, kit.quadro)
        kit.caixa((0, A.y, 0.15), (5.0, 1.2, 0.3), kit.quadro, 0.05)
        kit.caixa((0, tras.y, 0.15), (4.0, 1.0, 0.3), kit.quadro, 0.05)
        polias.append(A + Vector((0, 0.9, 0.4)))
    elif dupla:
        for s in (-1, 1):
            xc = s * 13.0  # torres bem afastadas: braços abertos não chegam nas colunas
            _torre(kit, Vector((xc, A.y, 0)), max(A.z + 2, 20), A.z, s)
            polias.append(Vector((xc - s * 0.9, A.y, A.z)))
    else:
        d = A.y - hip.y
        sent = 1.0 if d > 0 else -1.0
        if abs(d) < 1.5:
            sent = -1.0  # polia sobre a cabeça: torre à frente
        base = Vector((A.x, A.y + sent * 2.0, 0))
        ys = [p.y for a in am for p in (a["root"], a["pesc"], a["gL"], a["gR"], a["jL"], a["jR"])]
        # topo da cabeça (pescoço + 1,9 na direção da cabeça) também entra na folga da torre
        ys += [(a["pesc"] + (a["pesc"] - a["root"]).normalized() * 1.9).y for a in am]
        y_antes = base.y
        if sent < 0:
            base.y = min(base.y, min(ys) - 3.2)  # a torre não pode atravessar o corpo
        else:
            base.y = max(base.y, max(ys) + 3.2)
        if abs(A.x) <= 2.0 and abs(base.y - y_antes) > 1e-3:
            A = Vector((A.x, A.y + (base.y - y_antes), A.z))  # a polia vai junto com a torre (cabo nunca sai do nada)
        if abs(A.x) > 2.0:
            base = Vector((A.x + math.copysign(2.0, A.x), A.y, 0))  # polia lateral (pallof): torre ao lado
        alto = max(A.z + 1.5, 20)
        _torre(kit, base, alto, A.z, None)
        braco = Vector((base.x, base.y - sent * 0.4 if abs(A.x) <= 2.0 else base.y, A.z + 0.55))
        if abs(A.x) > 2.0:
            braco.x = base.x - math.copysign(0.4, A.x)
        if (Vector((A.x, A.y, A.z + 0.55)) - braco).length > 0.3:
            kit.viga(braco, Vector((A.x, A.y, A.z + 0.55)), 0.45, 0.45, kit.quadro)
        kit.disco(A, 0.48, 0.18, kit.metal, verts=24)
        kit.disco(A, 0.32, 0.26, kit.quadro, verts=16)
        polias.append(A)
    ctx.polia3 = polias[0] if polias else A
    cabos = [kit.cil_movel(0.045, kit.cabo_m, 8) for _ in polias]
    fio = _fio(kit, 8, 0.045, kit.cabo_m)
    if len(polias) == 2:
        for o in fio:
            o.hide_render = True
    tipo = tipo_cabo(ctx)
    if remo:
        tipo = "barra"
    alca = kit.cil_movel(0.13, kit.preto, 12)
    cordas = [kit.cil_movel(0.11, kit.preto, 10) for _ in range(2)]
    puxador = kit.cil_movel(0.13, kit.metal, 12)
    tri = [kit.cil_movel(0.15, kit.preto, 12) for _ in range(2)] + [kit.cil_movel(0.1, kit.metal, 10) for _ in range(3)]
    dalc = [kit.cil_movel(0.15, kit.preto, 12) for _ in range(2)]

    def upd(est):
        gL, gR = _maos(h, est)
        for o in tri + dalc:
            o.hide_render = True
        if len(polias) == 2:
            h.restaurar(est["est"])
            T = est["T"]
            for i_, (cab, p, g, sf) in enumerate(zip(cabos, polias, ((gR if polias[0].x < 0 else gL), (gL if polias[0].x < 0 else gR)),
                                                    ((".R" if polias[0].x < 0 else ".L"), (".L" if polias[0].x < 0 else ".R")))):
                e = (T.to_3x3() @ h.eixo_pegada(sf)).normalized()
                Kit.por_cil(dalc[i_], g - e * 0.6, g + e * 0.6)
                dalc[i_].hide_render = False
                Kit.por_cil(cab, p, g)
            for o in [alca, puxador] + cordas:
                o.hide_render = True
            return
        h.restaurar(est["est"])
        T = est["T"]

        def cabo_ate(p_fim):
            pts = [polias[0].lerp(p_fim, i_ / 8) for i_ in range(9)]
            _por_fio(fio, contornar(h, T, pts, ("mao_f", "mao_t", "antebraco_f", "antebraco_t"), folga=0.35))
            cabos[0].hide_render = True
        if tipo == "triangulo":
            c, lat, eixo = est["extras"].get("triangulo", ((gL + gR) / 2, (gL - gR).normalized(), Vector((0, 1, 0))))
            topo = c + (polias[0] - c).normalized() * 1.1
            for i_, (o, s_) in enumerate(zip(tri[:2], (1, -1))):
                m_ = c + lat * (0.7 * s_)
                Kit.por_cil(o, m_ - eixo * 0.6, m_ + eixo * 0.6)
                Kit.por_cil(tri[2 + i_], m_ + eixo * 0.6 * (1 if eixo.dot(polias[0] - c) > 0 else -1), topo)
                o.hide_render = tri[2 + i_].hide_render = False
            Kit.por_cil(tri[4], c + lat * 0.7 - eixo * 0.6 * (1 if eixo.dot(polias[0] - c) > 0 else -1),
                        c - lat * 0.7 - eixo * 0.6 * (1 if eixo.dot(polias[0] - c) > 0 else -1))
            tri[4].hide_render = False
            cabo_ate(topo)
            for o in cordas + [alca, puxador]:
                o.hide_render = True
            return
        meio = (gL + gR) / 2
        lado = gL - gR
        dist = lado.length
        if tipo == "barra" or (dist > 3.5 and not corda):
            ext = lado.normalized() * (max(dist, 2.6) / 2 + 0.9)
            Kit.por_cil(puxador, meio - ext, meio + ext)
            puxador.hide_render = False
            cabo_ate(meio)
            for o in cordas + [alca]:
                o.hide_render = True
        else:
            no = meio + (polias[0] - meio).normalized() * max(1.1, dist * 0.45)
            cabo_ate(no)
            Kit.por_cil(cordas[0], no, gL)
            Kit.por_cil(cordas[1], no, gR)
            for o in cordas:
                o.hide_render = False
            puxador.hide_render = True
            alca.hide_render = True
    kit.moveis.append(upd)


def _torre(kit, base, alto, z_polia, lado):
    """Estação de polia: dois montantes, pilha de anilhas, travessa no topo."""
    for s in (-1, 1):
        kit.viga(base + Vector((s * 1.1, 0, 0.1)), base + Vector((s * 1.1, 0, alto)), 0.45, 0.6, kit.quadro)
    kit.viga(base + Vector((-1.4, 0, alto)), base + Vector((1.4, 0, alto)), 0.6, 0.6, kit.quadro)
    kit.caixa(base + Vector((0, 0, 0.12)), (3.4, 3.4, 0.24), kit.quadro, 0.05)
    for i in range(12):
        kit.caixa(base + Vector((0, 0, 0.5 + i * 0.36)), (1.7, 1.1, 0.3), kit.preto if i % 2 else kit.borracha, 0.04)
    kit.cil(base + Vector((0, 0, 0.5)), base + Vector((0, 0, alto)), 0.05, kit.metal, 8)
    kit.caixa(base + Vector((0, 0, 9.0)), (2.0, 1.2, 0.5), kit.brasa, 0.06)


def _fio(kit, n, r, mat):
    return [kit.cil_movel(r, mat, 10) for _ in range(n)]


def _por_fio(segs, pts):
    """Polilinha pts desenhada nos n segmentos (reamostrada pelo comprimento)."""
    P = np.array([list(p) for p in pts])
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))]
    L = d[-1] if d[-1] > 1e-6 else 1.0
    ss = np.linspace(0, L, len(segs) + 1)
    Q = np.stack([np.interp(ss, d, P[:, k]) for k in range(3)], axis=1)
    for o, a, b in zip(segs, Q[:-1], Q[1:]):
        Kit.por_cil(o, Vector(a), Vector(b))


def contornar(h, T, pts, excl=(), folga=0.45, iters=3):
    """Cabo/elástico não atravessa o corpo: pontos internos da polilinha que caem dentro da pele (proxy) são empurrados
    para fora pela normal local (centro dos pontos de pele vizinhos -> ponto), com folga."""
    P = h.proxy(T)
    m = np.ones(len(P), bool)
    for k_ in excl:
        m &= ~h.px_partes[k_]
    Q = P[m][::2]
    pts = [Vector(p) for p in pts]
    for _ in range(iters):
        mexeu = False
        for i in range(1, len(pts) - 1):
            p = np.array(pts[i])
            d = np.linalg.norm(Q - p, axis=1)
            viz = d < 1.4
            if not viz.any() or d.min() > folga:
                continue
            c = Q[viz].mean(axis=0)
            n = p - c
            nl = np.linalg.norm(n)
            if nl < 1e-6:
                continue
            n /= nl
            # anda pela normal até a pele mais próxima ficar a 'folga'
            for passo in np.linspace(0.05, 2.5, 50):
                q = p + n * passo
                if np.linalg.norm(Q - q, axis=1).min() >= folga:
                    pts[i] = Vector(q)
                    mexeu = True
                    break
        if not mexeu:
            break
    return pts


def _alca(kit):
    return kit.cil_movel(0.14, kit.preto, 12)


def _por_alca(o, h, T, sf, larg=0.55):
    g = T @ h.pegada(sf)
    e = (T.to_3x3() @ h.eixo_pegada(sf)).normalized()
    Kit.por_cil(o, g - e * larg, g + e * larg)
    return g, e


def _ponto_sola(h, T, sf, P, ef, fora=0.0):
    """Ponto sob o arco do pé (entre o calcanhar e a base dos dedos), na sola; fora: deslocamento lateral (+ = por fora)."""
    a = T @ h.cabeca("foot" + sf)
    t3 = T @ h.cabeca("toe3-1" + sf)
    c = a + (t3 - a) * 0.45
    pts = P[h.px_partes[ef]]
    z = float(pts[:, 2].min())
    sx = 1 if sf == ".L" else -1
    return Vector((c.x + sx * fora, c.y, z + 0.03))


def _elastico(kit, ctx, h, pr, am):
    ate = pr.get("ate")
    if "battle" in ctx.id or pr.get("naval"):
        _corda_naval(kit, ctx, h, pr)
        return
    if pr.get("de") == "pernas":
        _miniband(kit, ctx, h, pr)
        return
    if isinstance(ate, list) and pr.get("abre"):
        _elastico_duplo(kit, ctx, h, pr)
        return
    lados = {"f": (".L",), "t": (".R",)}.get(_qual_mao(pr) if pr.get("maos") else "ambas", (".L", ".R"))
    if pr.get("de") == "mao_f":
        lados = (".L",)
    elif pr.get("de") == "mao_t":
        lados = (".R",)
    if ctx.barra is not None and (pr.get("de") == "barra" or "assistida" in ctx.id):
        _elastico_barra(kit, ctx, h, pr)
        return
    if isinstance(ate, list):
        A = ctx.p3(*ate[:3])
        if A.z > 1.2:
            kit.viga(Vector((A.x, A.y, 0.1)), Vector((A.x, A.y, A.z + 0.6)), 0.5, 0.5, kit.quadro)
            kit.caixa(Vector((A.x, A.y, 0.08)), (2.0, 2.0, 0.16), kit.quadro, 0.04)
            kit.toro(A, 0.3, 0.07, kit.metal, (0, 0, 1))
        else:
            A.z = max(A.z, 0.3)
            kit.toro(A, 0.35, 0.08, kit.metal)
        segs = {sf: _fio(kit, 10, 0.08, kit.brasa) for sf in lados}
        tri = {sf: _fio(kit, 2, 0.06, kit.brasa) for sf in lados}
        alcas = {sf: _alca(kit) for sf in lados}

        def upd(est):
            h.restaurar(est["est"])
            T = est["T"]
            for sf in lados:
                g, e = _por_alca(alcas[sf], h, T, sf)
                fimA = A + X * (0.25 if sf == ".L" else -0.25)
                q = g + (fimA - g).normalized() * 0.75
                Kit.por_cil(tri[sf][0], g + e * 0.5, q)
                Kit.por_cil(tri[sf][1], g - e * 0.5, q)
                pts = [q.lerp(fimA, i / 8) for i in range(9)]
                _por_fio(segs[sf], contornar(h, T, pts, ("mao_f", "mao_t", "antebraco_f", "antebraco_t")))
        kit.moveis.append(upd)
        return
    if ate == "pes":
        segs = {sf: _fio(kit, 8, 0.08, kit.brasa) for sf in lados}
        sola = {sf: kit.cil_movel(0.08, kit.brasa, 10) for sf in lados}
        alcas = {sf: _alca(kit) for sf in lados}

        def upd(est):
            h.restaurar(est["est"])
            T = est["T"]
            P = h.proxy(T)
            for sf, ef in ((".L", "pe_f"), (".R", "pe_t")):
                if sf not in lados:
                    continue
                g, e = _por_alca(alcas[sf], h, T, sf)
                fora = _ponto_sola(h, T, sf, P, ef, 0.6)
                dentro = _ponto_sola(h, T, sf, P, ef, -0.6)
                Kit.por_cil(sola[sf], fora, dentro)  # passa sob a sola, no arco do pé
                sobe = fora + Vector((0, 0, 0.35))
                pts = [g.lerp(sobe, i / 7) for i in range(8)] + [fora]
                _por_fio(segs[sf], contornar(h, T, pts, ("mao_f", "mao_t", "antebraco_f", "antebraco_t", "pe_f", "pe_t")))
        kit.moveis.append(upd)
        return
    if pr.get("de") == "costas":
        n = 16
        segs = _fio(kit, n, 0.11, kit.brasa)
        alcas = {sf: _alca(kit) for sf in (".L", ".R")}

        def upd_c(est):
            # mão -> axila -> escápulas -> outra axila -> outra mão (por fora dos braços, sem passar pelo cotovelo)
            h.restaurar(est["est"])
            T = est["T"]
            R_up = h.rot("spine01") @ h.rest_inv["spine01"].to_3x3()
            tras = (T.to_3x3() @ (R_up @ Vector((0, 1, 0)))).normalized()
            cima = (T.to_3x3() @ (R_up @ Vector((0, 0, 1)))).normalized()
            for sf in (".L", ".R"):
                _por_alca(alcas[sf], h, T, sf)
            ctrl = [T @ h.pegada(".L"), T @ h.cabeca("upperarm01.L") + tras * 1.1 - cima * 0.5,
                    T @ h.cabeca("spine01") + tras * 1.3, T @ h.cabeca("upperarm01.R") + tras * 1.1 - cima * 0.5, T @ h.pegada(".R")]
            pts = []
            m = len(ctrl)
            por = 6
            for i in range(m - 1):
                p0, p1, p2, p3 = ctrl[max(i - 1, 0)], ctrl[i], ctrl[i + 1], ctrl[min(i + 2, m - 1)]
                for j in range(por):
                    t = j / por
                    t2, t3 = t * t, t * t * t
                    pts.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
            pts.append(ctrl[-1])
            _por_fio(segs, contornar(h, T, pts, ("mao_f", "mao_t")))
        kit.moveis.append(upd_c)
        return
    # entre as mãos (band pull-apart): contorna o peito quando as mãos passam do plano dos ombros
    segs = _fio(kit, 10, 0.09, kit.brasa)

    def upd(est):
        h.restaurar(est["est"])
        T = est["T"]
        gL, gR = T @ h.pegada(".L"), T @ h.pegada(".R")
        pts = [gL.lerp(gR, i / 10) for i in range(11)]
        _por_fio(segs, contornar(h, T, pts, ("mao_f", "mao_t"), folga=0.25))
    kit.moveis.append(upd)


def _elastico_barra(kit, ctx, h, pr):
    """Barra assistida: elástico em laço preso no centro da barra, descendo até o pé (ou joelho) apoiado nele."""
    b3 = ctx.ref.get("barra3") or ctx.p3(*ctx.barra)
    ef, sf = ("pe_t", ".R") if pr.get("ate", "pe_t") != "pe_f" else ("pe_f", ".L")
    segs = [_fio(kit, 10, 0.1, kit.brasa) for _ in range(2)]
    sola = kit.cil_movel(0.1, kit.brasa, 10)
    no = kit.toro(b3, 0.3, 0.1, kit.brasa, (0, 1, 0))
    _ = no

    def upd(est):
        h.restaurar(est["est"])
        T = est["T"]
        P = h.proxy(T)
        a = _ponto_sola(h, T, sf, P, ef, 0.55)
        b = _ponto_sola(h, T, sf, P, ef, -0.55)
        Kit.por_cil(sola, a, b)
        for seg, top, bot in zip(segs, (b3 + X * 0.3, b3 - X * 0.3), (a, b)):
            pts = [top.lerp(bot, i / 9) for i in range(10)]
            _por_fio(seg, contornar(h, T, pts, ("pe_f", "pe_t"), folga=0.3))
    kit.moveis.append(upd)


def _corda_naval(kit, ctx, h, pr):
    """Corda naval: dois cabos grossos ancorados longe à frente, deitados no chão, com a onda que a mão gera viajando até
    a âncora (amplitude = sobe-desce da mão, defasada pela distância; lados alternados conforme a mão)."""
    ate = pr.get("ate") or [15, 0.3]
    A = ctx.p3(*ate[:2])
    A.z = ctx.z0 + 0.25
    kit.cil((-1.2, A.y, ctx.z0 + 0.25), (1.2, A.y, ctx.z0 + 0.25), 0.3, kit.metal, 16)
    kit.caixa((0, A.y, ctx.z0 + 0.15), (3.0, 1.0, 0.3), kit.quadro, 0.05)
    estados = ctx._estados
    T_ = ctx.trilhas.T
    hist = {}
    for sf in (".L", ".R"):
        tz = []
        for est in estados:
            h.restaurar(est["est"])
            tz.append((est["tau"] % T_, (est["T"] @ h.pegada(sf)).z))
        tz.sort()
        ts, zs = np.array([t for t, _ in tz]), np.array([z for _, z in tz])
        hist[sf] = (ts, zs, float(zs.mean()))
    segs = {sf: _fio(kit, 28, 0.2, kit.preto) for sf in (".L", ".R")}
    v_onda = 18.0  # dm/s

    def zmao(sf, t):
        ts, zs, m = hist[sf]
        return float(np.interp(t % T_, ts, zs, period=T_)) - m

    def upd(est):
        h.restaurar(est["est"])
        T = est["T"]
        for sf, sx in ((".L", 1), (".R", -1)):
            g = T @ h.pegada(sf)
            fim = Vector((sx * 0.8, A.y, A.z))
            L = (fim - g).length
            pts = []
            for i in range(29):
                sv = i / 28
                p = g.lerp(fim, sv)
                chao = mov_suave(sv, 0.0, 0.22)
                p.z = g.z * (1 - chao) + A.z * chao
                atraso = sv * L / v_onda
                p.z += zmao(sf, est["tau"] - atraso) * math.exp(-1.6 * sv) * chao * 1.3
                p.z = max(p.z, ctx.z0 + 0.2)
                pts.append(p)
            _por_fio(segs[sf], pts)
    kit.moveis.append(upd)


def mov_suave(u, a=0.0, b=1.0):
    t = min(1.0, max(0.0, (u - a) / (b - a)))
    return t * t * (3 - 2 * t)


def _elastico_duplo(kit, ctx, h, pr):
    """Elástico ancorado atrás em dois pontos (um por mão), num rack/espaldar com travessa: crucifixo/abertura."""
    A = ctx.p3(*pr["ate"][:2])
    w = float(pr["abre"]) * ctx.k
    zt = max(A.z + 2.5, 14.0)
    for sx in (-1, 1):
        kit.viga(Vector((sx * (w + 0.7), A.y, 0.1)), Vector((sx * (w + 0.7), A.y, zt)), 0.55, 0.55, kit.quadro)
        kit.caixa(Vector((sx * (w + 0.7), A.y, 0.08)), (1.4, 2.4, 0.16), kit.quadro, 0.04)
    kit.viga(Vector((-(w + 1.0), A.y, zt)), Vector((w + 1.0, A.y, zt)), 0.55, 0.55, kit.quadro)
    kit.viga(Vector((-(w + 0.7), A.y, A.z)), Vector((w + 0.7, A.y, A.z)), 0.4, 0.4, kit.quadro)
    ancora = {}
    for sf, sx in ((".L", 1), (".R", -1)):
        ancora[sf] = Vector((sx * w, A.y - 0.25, A.z))
        kit.toro(ancora[sf], 0.28, 0.07, kit.metal, (0, 1, 0))
    segs = {sf: kit.cil_movel(0.085, kit.brasa, 10) for sf in (".L", ".R")}
    alcas = {sf: kit.cil_movel(0.14, kit.preto, 10) for sf in (".L", ".R")}

    def upd(est):
        h.restaurar(est["est"])
        T = est["T"]
        for sf in (".L", ".R"):
            g = T @ h.pegada(sf)
            e = T.to_3x3() @ h.eixo_polegar(sf)
            Kit.por_cil(alcas[sf], g - e * 0.5, g + e * 0.5)
            Kit.por_cil(segs[sf], g, ancora[sf])
    kit.moveis.append(upd)


def _miniband(kit, ctx, h, pr):
    """Mini-band em volta das duas pernas (acima do tornozelo ou do joelho): duas faixas ligando as canelas."""
    frac = 0.75 if pr.get("em", "tornozelos") == "tornozelos" else 0.12
    aneis = {sf: kit.cil_movel(0.62, kit.brasa, 20) for sf in (".L", ".R")}
    faixas = [kit.cil_movel(0.09, kit.brasa, 10) for _ in range(2)]

    def upd(est):
        h.restaurar(est["est"])
        T = est["T"]
        c, d = {}, {}
        for sf in (".L", ".R"):
            j, a = T @ h.cabeca("lowerleg01" + sf), T @ h.cabeca("foot" + sf)
            c[sf] = j + (a - j) * frac
            d[sf] = (a - j).normalized()
            Kit.por_cil(aneis[sf], c[sf] - d[sf] * 0.12, c[sf] + d[sf] * 0.12)
        fw = (T.to_3x3() @ FRENTE).normalized()
        for o, s_ in zip(faixas, (1, -1)):
            Kit.por_cil(o, c[".L"] + fw * 0.45 * s_, c[".R"] + fw * 0.45 * s_)
    kit.moveis.append(upd)


def _parede(kit, ctx, h):
    """Batente de porta + parede onde a mão/antebraço se apoia (alongamento de peitoral)."""
    pa = ctx.parede
    sf = pa["sf"]
    s_ = 1 if sf == ".L" else -1
    p = pa["palma"]
    # o batente fica à frente da palma; a parede continua para fora (lado oposto ao corpo)
    yb = p.y - 0.75
    xb = p.x
    alto = max(p.z + 4.0, 20.0)
    kit.caixa(Vector((xb + s_ * 0.2, yb, alto / 2)), (1.2, 1.0, alto), kit.madeira, 0.08)
    kit.caixa(Vector((xb + s_ * 2.8, yb - 0.1, alto / 2)), (4.0, 0.8, alto), kit.cinza, 0.04)
    kit.caixa(Vector((xb + s_ * 0.2 - s_ * 4.2, yb, alto - 0.6)), (8.4, 1.0, 1.2), kit.madeira, 0.08)


# ---- pesos nas mãos

def _barra(kit, ctx, h):
    R = raio_anilha(ctx)
    curta = R < 1.5
    b = barra_olimpica(kit, R, curta)
    b["foco"] = 1

    def upd(est):
        if "barra" in est["extras"]:
            c, e = est["extras"]["barra"]
        else:
            gL, gR = _maos(h, est)
            c, e = (gL + gR) / 2, (gL - gR)
            e = e.normalized() if e.length > 1e-3 else X
        b.matrix_world = Matrix.Translation(c) @ _alinhar(X, e)
    kit.moveis.append(upd)


def _halteres(kit, ctx, h, maos="ambas"):
    if "halter_unico" in (getattr(ctx, "impl", None) or {}):
        o = halter_peca(kit)
        o["foco"] = 1

        def upd_u(est):
            if "halter_unico" in est["extras"]:
                c, d = est["extras"]["halter_unico"]
            else:
                gL, gR = _maos(h, est)
                c, d = (gL + gR) / 2, (gL - gR).normalized()
            o.matrix_world = Matrix.Translation(c) @ _alinhar(X, d)
        kit.moveis.append(upd_u)
        return
    lados = {"f": (".L",), "t": (".R",)}.get(maos, (".L", ".R"))
    hs = {sf: halter_peca(kit) for sf in lados}
    for o in hs.values():
        o["foco"] = 1

    def upd(est):
        h.restaurar(est["est"])
        T = est["T"]
        for sf, o in hs.items():
            g = T @ h.pegada(sf)
            e = T.to_3x3() @ h.eixo_polegar(sf)
            o.matrix_world = Matrix.Translation(g) @ _alinhar(X, e)
    kit.moveis.append(upd)


def _fourier(taus, vals, T, nh=8):
    """Série de Fourier periódica (mínimos quadrados) de amostras vetoriais: devolve f(t) e f''(t)."""
    t = np.asarray(taus, float)
    V = np.asarray(vals, float)
    nh = max(1, min(nh, (len(t) - 1) // 2))
    w = 2 * math.pi / T
    cols = [np.ones_like(t)]
    for n in range(1, nh + 1):
        cols += [np.cos(n * w * t), np.sin(n * w * t)]
    A = np.stack(cols, axis=1)
    coef, *_ = np.linalg.lstsq(A, V, rcond=None)

    def f(tt, der=0):
        out = coef[0] * (1.0 if der == 0 else 0.0)
        for n in range(1, nh + 1):
            c, s_ = coef[2 * n - 1], coef[2 * n]
            if der == 0:
                out = out + c * math.cos(n * w * tt) + s_ * math.sin(n * w * tt)
            else:
                k2 = -(n * w) ** 2
                out = out + k2 * (c * math.cos(n * w * tt) + s_ * math.sin(n * w * tt))
        return out
    return f


def _kettlebell(kit, ctx, h, maos="ambas"):
    ps = [kit.esfera((0, 0, -1.15), 0.95, kit.preto), kit.toro((0, 0, -0.05), 0.5, 0.12, kit.preto, (1, 0, 0))]
    kb = kit.grupo_movel(ps)
    kb["foco"] = 1
    lados = {"f": (".L",), "t": (".R",)}.get(maos, (".L", ".R"))

    def alvo(est):
        h.restaurar(est["est"])
        T = est["T"]
        c = sum((T @ h.pegada(sf) for sf in lados), Vector()) / len(lados)
        alvo.e = (T @ h.pegada(".L") - T @ h.pegada(".R")).normalized() if len(lados) == 2 else (T.to_3x3() @ h.eixo_pegada(lados[0])).normalized()
        ante = T.to_3x3() @ sum(((h.cabeca("wrist" + sf) - h.cabeca("lowerarm01" + sf)) for sf in lados), Vector()).normalized()
        return c, ante
    dirs = None
    estados = getattr(ctx, "_estados", None)
    pendulo = any(x in ctx.id for x in ("swing", "terra-uma-perna")) and estados and len(estados) >= 6
    if pendulo:
        # follow-through: a direção do kettlebell segue a linha dos braços com atraso (2ª ordem amortecida, laço periódico)
        T = ctx.trilhas.T
        taus, alvos = [], []
        for est in estados:
            c, ante = alvo(est)
            d = (Vector((0, 0, -1)) * 0.25 + ante * 0.75).normalized()
            taus.append(est["tau"] % T)
            alvos.append(list(d))
        f = _fourier(taus, alvos, T, 10)
        om, ze, dt = 13.0, 0.42, 1.0 / 600
        d = np.array(f(0.0)); v = np.zeros(3)
        amostra = {}
        nps = int(round(T / dt))
        for volta in range(4):
            for j in range(nps):
                tt = j * dt
                a_ = om * om * (np.array(f(tt)) - d) - 2 * ze * om * v
                v = v + a_ * dt
                d = d + v * dt
                d = d / max(np.linalg.norm(d), 1e-9)
                if volta == 3:
                    amostra[j] = d.copy()
        dirs = {id(est): Vector(amostra[int(round((est["tau"] % T) / dt)) % nps]) for est in estados}

    goblet = "goblet" in ctx.id

    def por_kb(c, d, e):
        # -Z local = direção do sino, Y local = eixo da alça (entre as mãos); a barra de cima da alça (z local 0,45) na pegada
        zl = (-d).normalized()
        yl = e - zl * e.dot(zl)
        yl = yl.normalized() if yl.length > 1e-4 else zl.orthogonal().normalized()
        xl = yl.cross(zl)
        M = Matrix((xl, yl, zl)).transposed().to_4x4()
        kb.matrix_world = Matrix.Translation(c - zl * 0.45) @ M

    def upd(est):
        c, ante = alvo(est)
        e = alvo.e
        if goblet:
            # goblet: sino abaixo das mãos, encostado no peito
            h.restaurar(est["est"])
            T = est["T"]
            Rs = T.to_3x3() @ h.rot("spine01") @ h.rest_inv["spine01"].to_3x3()
            tras = (Rs @ Vector((0, 1, 0))).normalized()
            por_kb(c, (Vector((0, 0, -1)) + tras * 0.35).normalized(), e)
            return
        if dirs is not None and id(est) in dirs:
            d = dirs[id(est)]
        else:
            d = (Vector((0, 0, -1)) * 0.65 + ante * 0.35).normalized()
        por_kb(c, d, e)
    kit.moveis.append(upd)


def _saco(kit, ctx, h, pr, estados):
    """Saco de pancada pendurado: pêndulo amortecido que recebe um impulso a cada golpe (laço periódico)."""
    c = ctx.p3(pr.get("x", 9), 0)
    piv = Vector((0, c.y, 24.0))
    ps = [kit.cil((0, c.y, 5.5 * ctx.k), (0, c.y, 17.5 * ctx.k), 1.5, kit.preto, 32),
          kit.cil((0, c.y, 17.5 * ctx.k), (0, c.y, 24), 0.05, kit.metal, 8),
          kit.toro((0, c.y, 11.5 * ctx.k), 1.52, 0.06, kit.brasa, (0, 0, 1))]
    saco = kit.grupo_movel(ps)
    T = ctx.trilhas.T
    ang = {}
    if estados:
        dist = []
        for est in estados:
            h.restaurar(est["est"])
            Tm = est["T"]
            r = min(math.hypot((Tm @ h.pegada(sf)).x, (Tm @ h.pegada(sf)).y - c.y) for sf in (".L", ".R")) - 1.5
            dist.append((est["tau"] % T, r))
        dist.sort()
        golpes = []
        n = len(dist)
        for j in range(n):
            t0, r = dist[j]
            if r < 0.45 and r <= dist[(j - 1) % n][1] and r <= dist[(j + 1) % n][1]:
                golpes.append(t0)
        om, ze, dt = math.sqrt(98.1 / 12.5), 0.12, 1.0 / 600
        th, w = 0.0, 0.0
        nps = int(round(T / dt))
        gi = set(int(round(g / dt)) % nps for g in golpes)
        amostra = {}
        for volta in range(6):
            for j in range(nps):
                if j in gi:
                    w += 0.22
                w += (-om * om * th - 2 * ze * om * w) * dt
                th += w * dt
                if volta == 5:
                    amostra[j] = th
        for est in estados:
            ang[id(est)] = amostra[int(round((est["tau"] % T) / dt)) % nps]

    def upd(est):
        a = ang.get(id(est), 0.0)
        # golpe empurra o saco para longe do atleta (atleta em +y em relação ao saco)
        saco.matrix_world = Matrix.Translation(piv) @ Matrix.Rotation(-a, 4, "X") @ Matrix.Translation(-piv)
    kit.moveis.append(upd)


def _bola(kit, ctx, h):
    """Medicine ball entre as palmas (centro calculado em pegada_implementos); com "voo": [i, j] a bola sai das mãos na
    chave i, voa em parábola (ou quica no chão / no ponto "quica": [x, y]) e volta às mãos na chave j."""
    b = kit.esfera((0, 0, 0), RAIO_BOLA, kit.brasa)
    b["foco"] = 1
    estados = getattr(ctx, "_estados", None) or []
    T_ = ctx.trilhas.T

    def centro_maos(est):
        if "bola" in est["extras"]:
            return est["extras"]["bola"]
        h.restaurar(est["est"])
        T = est["T"]
        return (T @ h.palma_c(".L") + T @ h.palma_c(".R")) / 2

    voo = getattr(ctx, "bola_voo", None)
    if voo and estados:
        a, bb, quica = voo

        def perto(t):
            return min(estados, key=lambda e: min(abs(e["tau"] - t) % T_, T_ - abs(e["tau"] - t) % T_))
        # soltura/retomada: últimos/primeiros quadros com a bola nas mãos
        p0 = centro_maos(perto(a))
        p1 = centro_maos(perto(bb))
        D = (bb - a) % T_
        g = 98.1
        if quica is not None:
            q = ctx.p3(*quica[:2]) if isinstance(quica, list) else (p0 + p1) / 2
            if not isinstance(quica, list):
                q.z = ctx.z0 + RAIO_BOLA
            pernas = [(p0, q, D * 0.5), (q, p1, D * 0.5)]
        else:
            pernas = [(p0, p1, D)]

        def no_voo(x):
            for pa, pb, d in pernas:
                if x <= d or (pa, pb, d) == pernas[-1]:
                    x = min(x, d)
                    v0 = (pb - pa) / d - Vector((0, 0, -g)) * (0.5 * d)
                    return pa + v0 * x + Vector((0, 0, -g)) * (0.5 * x * x)
                x -= d
            return p1
    else:
        no_voo = None

    def upd(est):
        no_ar, _ = bola_no_ar(ctx, est["tau"])
        if no_ar and no_voo is not None:
            x = (est["tau"] - voo[0]) % T_
            c = no_voo(x)
        else:
            c = centro_maos(est)
        c = Vector((c.x, c.y, max(c.z, ctx.z0 + RAIO_BOLA)))
        b.matrix_world = Matrix.Translation(c)
    kit.moveis.append(upd)


def _picos_salto(ctx):
    """Instantes de pico dos saltos no ciclo (meio das fases de voo; sem voo: chaves de maior 'ay')."""
    if getattr(ctx, "voos", None):
        T_ = ctx.trilhas.T
        return sorted(((a + ((b - a) % T_) / 2) % T_) for a, b in ctx.voos)
    ays = [c["q"]["ay"] for c in ctx.chaves]
    m = max(ays)
    if m <= 0:
        return [0.0]
    return [float(ctx.trilhas.t0[i]) for i, v in enumerate(ays) if v >= m * 0.8]


def _corda(kit, ctx, h):
    """Corda de pular: manoplas nas mãos; a corda sai de cada mão para fora dos ombros e gira em volta do corpo num círculo
    (eixo lateral na altura das mãos), uma volta por salto, passando sob os pés só no pico do voo (nunca pelo corpo)."""
    n = 26
    segs = [kit.cil_movel(0.05, kit.brasa, 8) for _ in range(n)]
    mans = {sf: kit.cil_movel(0.15, kit.preto, 12) for sf in (".L", ".R")}
    picos = _picos_salto(ctx)
    T_ = ctx.trilhas.T

    def fase(tau):
        t = tau % T_
        ps = picos + [picos[0] + T_]
        for k_ in range(len(ps) - 1):
            a, b = ps[k_], ps[k_ + 1]
            if a <= t < b or (k_ == 0 and t < a):
                if t < a:
                    t += T_
                    a, b = ps[-2], ps[-1]
                return 2 * math.pi * (t - a) / (b - a)
        return 0.0

    def upd(est):
        h.restaurar(est["est"])
        T = est["T"]
        gL, _ = _por_alca(mans[".L"], h, T, ".L", 0.6)
        gR, _ = _por_alca(mans[".R"], h, T, ".R", 0.6)
        C = (gL + gR) / 2
        R = max(C.z - ctx.z0 - 0.08, 3.0)
        phi = fase(est["tau"])  # 0 = corda embaixo (pico do salto); gira para a frente
        d = Vector((0, -math.sin(phi), -math.cos(phi)))
        W = max(abs(gL.x - gR.x) / 2 + 0.5, 2.4)
        pts = []
        for i in range(n + 1):
            sv = i / n
            bb = math.sin(math.pi * sv) ** 0.5
            arco = Vector((0, C.y, C.z)) + X * (W * math.cos(math.pi * sv)) + d * R
            p = gL.lerp(gR, sv) * (1 - bb) + arco * bb
            p.z = max(p.z, ctx.z0 + 0.05)
            pts.append(p)
        for o, a_, b_ in zip(segs, pts[:-1], pts[1:]):
            Kit.por_cil(o, a_, b_)
    kit.moveis.append(upd)
