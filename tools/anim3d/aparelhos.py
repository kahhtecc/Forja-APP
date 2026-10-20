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
        self.chao = _mat("tapete", (0.20, 0.08, 0.05), 0.0, 0.9)
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

    def pontos(self):
        out = []
        for o in self.objs:
            if o.hide_render:
                continue
            M = o.matrix_world
            for c in o.bound_box:
                out.append(tuple(M @ Vector(c)))
        return np.array(out) if out else np.zeros((0, 3))


# ------------------------------------------------------------------ peças compostas (criadas na origem, eixo X)

def barra_olimpica(kit, R, curta=False):
    meia = 6.6 if curta else 11.0
    luva = 4.2 if curta else 6.5
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


# ------------------------------------------------------------------ preparação (antes das poses)

def preparar(ctx, h):
    ctx.bike = None
    if "bike" not in ctx.tipos:
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
    ctx.bike = {"c": Vector(c), "r": float(max(1.4, min(r, 2.0)))}


def _antepe(h, sf):
    """Antepé (bola do pé) no espaço do esqueleto: entre a cabeça dos dedos e o tornozelo, na sola."""
    t3 = h.cabeca("toe3-1" + sf)
    a = h.cabeca("foot" + sf)
    return a + (t3 - a) * 0.78


def antes_ik(ctx, h, T, tau, extras):
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
    proj = pts @ np.array(nrm)
    lim = proj.max()
    sola = pts[proj > lim - 0.25]
    c = Vector(sola.mean(axis=0))
    c = c + nrm * (lim - float(np.array(c) @ np.array(nrm)))
    return c, nrm


def montar(kit, ctx, h, estados):
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
                for s in (-1, 1):
                    xb = s * max(1.8, min(xmax, 3.2))
                    kit.cil((xb, c.y - 4.5, c.z), (xb, c.y + 4.5, c.z), 0.2, kit.metal)
                    for dy in (-4.0, 4.0):
                        kit.cil((xb, c.y + dy, 0), (xb, c.y + dy, c.z - 0.1), 0.22, kit.quadro, 16)
                        kit.caixa((xb, c.y + dy, 0.08), (1.6, 0.6, 0.16), kit.quadro, 0.04)
            else:
                mb = max(5.0, xmax + 1.6)
                kit.cil((-mb - 0.4, c.y, c.z), (mb + 0.4, c.y, c.z), 0.16, kit.metal)
                for dx in (-mb, mb):
                    kit.viga((dx, c.y, 0), (dx, c.y, c.z + 0.5), 0.5, 0.5, kit.quadro)
                    kit.caixa((dx, c.y, 0.1), (0.7, 5.0, 0.2), kit.quadro, 0.05)
        elif tp == "saco":
            c = ctx.p3(pr.get("x", 9), 0)
            kit.cil((0, c.y, 5.5 * ctx.k), (0, c.y, 17.5 * ctx.k), 1.5, kit.preto, 32)
            kit.cil((0, c.y, 17.5 * ctx.k), (0, c.y, 24), 0.05, kit.metal, 8)
            kit.toro((0, c.y, 11.5 * ctx.k), 1.52, 0.06, kit.brasa, (0, 0, 1))
        elif tp == "esteira":
            _esteira(kit, ctx, root_y, am)
        elif tp == "tapete":
            ys = []
            for est in estados[:: max(1, len(estados) // 6)]:
                h.restaurar(est["est"])
                P = h.proxy(est["T"])
                ys.append(P[P[:, 2] < ctx.z0 + 1.5][:, 1])
            ys = np.concatenate(ys) if ys else np.array([root_y])
            y0, y1 = (float(ys.min()), float(ys.max())) if len(ys) else (root_y - 8, root_y + 8)
            comp = max(16.0, y1 - y0 + 3.0)
            kit.caixa((0, (y0 + y1) / 2, ALTURA_TAPETE / 2), (6.5, comp, ALTURA_TAPETE), kit.chao, 0.03)
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
            _halteres(kit, ctx, h)
        elif tp == "kettlebell":
            _kettlebell(kit, ctx, h)
        elif tp == "bola":
            _bola(kit, ctx, h)
        elif tp == "corda":
            _corda(kit, ctx, h)
    _extras_maquina(kit, ctx, h, am, estados)


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
        for ch in ctx.chaves:
            for ef in ch["ef"].values():
                p = ef["baixo"]
                if ef["contato"] and r["y0"] - 0.3 <= p.y <= r["y1"] + 0.3 and abs(p.z - r["zt"]) < 0.5:
                    r["lx"] = max(r["lx"], abs(p.x) + 0.7)
    idd = ctx.id
    for r in rects:
        y0, y1, zb, zt, lx = r["y0"], r["y1"], r["zb"], r["zt"], r["lx"]
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
                continue
            if assento:
                zs = max(s["zt"] for s in assento)
                kit.caixa((0, cy, (zs + zt) / 2 + 0.2), (lx * 2, max(L, 0.7), zt - zs - 0.4), kit.estofado, 0.25)
                kit.viga((0, cy + (0.6 if cy > assento[0]["y0"] else -0.6), 0.2), (0, cy + 0.6, zt - 1.0), 0.6, 0.6, kit.quadro)
            elif "scott" in idd:
                kit.viga((0, cy, 0.2), (0, cy, zt - 1.4), 0.6, 0.6, kit.quadro)
                kit.caixa((0, cy - 0.5, zt - 0.7), (lx * 2, 2.6, 0.7), kit.estofado, 0.25, rot=(math.radians(-35), 0, 0))
                kit.caixa((0, cy, 0.1), (3.0, 4.0, 0.2), kit.quadro, 0.05)
            else:
                # coluna de máquina (elíptico, escada, hack): poste + console
                kit.viga((0, cy, 0.2), (0, cy, zt - 1.2), 0.7, 0.9, kit.quadro)
                kit.caixa((0, cy, zt - 0.6), (3.0, 1.2, 1.2), kit.preto, 0.2)
                kit.caixa((0, cy, 0.1), (4.0, 3.0, 0.2), kit.quadro, 0.05)
            continue
        esp = min(0.75, max(0.3, r["h"] * 0.5))
        if any(s in idd for s in ("box-jump", "step")) and r["zb"] < 0.1:
            kit.caixa((0, cy, zt / 2), (5.0, L, zt), kit.madeira, 0.12)
            continue
        if r["zb"] > 0.4:
            # almofada elevada (apoio de joelho/quadril) sobre um poste
            kit.caixa((0, cy, (zb + zt) / 2), (lx * 2, max(L, 0.8), max(zt - zb, 0.4)), kit.estofado, 0.25)
            kit.viga((0, cy, 0.15), (0, cy, zb), 0.55, 0.55, kit.quadro)
            kit.caixa((0, cy, 0.08), (3.0, 2.0, 0.16), kit.quadro, 0.05)
            continue
        if r["h"] < 1.2:
            kit.caixa((0, cy, zt / 2), (lx * 2, L, zt), kit.quadro if "remo" in idd else kit.borracha, 0.06)
            continue
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


def _extras_maquina(kit, ctx, h, am, estados):
    idd = ctx.id
    if "leg-press" in idd or idd.startswith("hack"):
        _plataforma_movel(kit, ctx, h, estados)
    if "extensora" in idd or "flexora" in idd and "mesa" not in idd:
        _rolo_canela(kit, ctx, h, frente="extensora" in idd)
    if "mesa-flexora" in idd:
        _rolo_canela(kit, ctx, h, frente=False)
    if "abdutora" in idd or "adutora" in idd:
        _almofadas_joelho(kit, ctx, h, fora="abdutora" in idd)
    if "remo-ergometro" in idd:
        _assento_remo(kit, ctx, h)


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
    for s in (-1, 1):
        a = c0 - d * 3.0 + n0 * 0.8 + X * s * 3.2
        b = c1 + d * 3.0 + n0 * 0.8 + X * s * 3.2
        kit.viga(a, b, 0.45, 0.45, kit.quadro)
    for p in (c0 - d * 3.0 + n0 * 0.8, c1 + d * 3.0 + n0 * 0.8):
        if p.z > 0.4:
            for s in (-1, 1):
                kit.viga((s * 3.2, p.y, 0.1), (s * 3.2, p.y, p.z), 0.45, 0.45, kit.quadro)
    ps = [kit.caixa((0, 0, 0.15), (7.0, 5.0, 0.3), kit.quadro, 0.06), kit.caixa((0, 0, -0.02), (6.6, 4.6, 0.06), kit.borracha, 0.02)]
    pl = kit.grupo_movel(ps)

    def upd(est):
        h.restaurar(est["est"])
        c, n = _plataforma(h, est["T"])
        up = Vector((0, 0, 1)) if abs(n.z) < 0.9 else Vector((0, 1, 0))
        R = (-n).to_track_quat("Z", "Y" if abs(n.y) < 0.9 else "X").to_matrix().to_4x4()
        _ = up
        pl.matrix_world = Matrix.Translation(c) @ R
    kit.moveis.append(upd)


def _rolo_canela(kit, ctx, h, frente=True):
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
        fw = T.to_3x3() @ FRENTE
        f = (fw - s * fw.dot(s)).normalized()
        c = a - s * 0.55 + f * (0.85 if frente else -0.85)
        Kit.por_cil(rolo, c - X * 2.6, c + X * 2.6)
        for o, sx in zip(bracos, (-1, 1)):
            Kit.por_cil(o, Vector((sx * 2.9, j.y, j.z)), Vector((sx * 2.9, c.y, c.z)))
    kit.moveis.append(upd)


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
    banco = kit.caixa((0, 0, 0), (2.4, 2.6, 0.5), kit.estofado, 0.2)

    def upd(est):
        h.restaurar(est["est"])
        r = est["T"] @ h.cabeca("root")
        banco.matrix_world = Matrix.Translation((0, r.y + 0.3, 1.05))
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
    b = ctx.bike or {"c": am[0]["root"] + Vector((0, -3, -5)), "r": 1.7}
    c, r = b["c"], b["r"]
    a0 = am[0]
    selim = Vector((0, a0["root"].y + 0.3, a0["root"].z - 0.95))
    guidao = (a0["gL"] + a0["gR"]) / 2
    cx = Vector((0, c.y, c.z))
    y_tras = selim.y + 2.5
    y_fr = min(c.y, guidao.y) - 3.0
    for yy in (y_tras, y_fr):
        kit.viga((-2.4, yy, 0.18), (2.4, yy, 0.18), 0.7, 0.36, kit.quadro)
    kit.viga((0, y_tras, 0.3), (0, y_fr, 0.3), 0.6, 0.5, kit.quadro)
    # coluna do selim (inclinada) e do guidão
    base_selim = Vector((0, c.y + 1.4, 0.4))
    kit.viga(base_selim, selim - Vector((0, 0, 0.35)), 0.6, 0.6, kit.quadro)
    kit.caixa(selim, (1.3, 2.4, 0.45), kit.estofado, 0.2)
    base_g = Vector((0, y_fr + 1.0, 0.4))
    topo_g = Vector((0, guidao.y + 0.9, guidao.z - 0.7))
    kit.viga(base_g, topo_g, 0.7, 0.7, kit.quadro)
    kit.viga(cx, base_g.lerp(topo_g, 0.25), 0.5, 0.5, kit.quadro)
    kit.viga(cx, base_selim.lerp(selim, 0.3), 0.5, 0.5, kit.quadro)
    kit.cil(Vector((-2.0, guidao.y, guidao.z - 0.15)), Vector((2.0, guidao.y, guidao.z - 0.15)), 0.16, kit.metal, 16)
    kit.viga(topo_g, Vector((0, guidao.y, guidao.z - 0.15)), 0.4, 0.4, kit.quadro)
    volante = base_g.lerp(topo_g, 0.22) + Vector((0, -0.6, 0))
    kit.disco(volante, 1.9, 0.45, kit.preto, verts=48)
    kit.toro(volante + Vector((0.25, 0, 0)), 1.85, 0.07, kit.metal)
    kit.toro(volante + Vector((0.26, 0, 0)), 1.0, 0.06, kit.brasa)
    kit.disco(cx, 0.75, 0.4, kit.metal, verts=32)
    bracos = {sf: kit.cil_movel(0.14, kit.metal, 12) for sf in (".L", ".R")}
    pedais = {sf: kit.cil_movel(0.12, kit.preto, 8) for sf in (".L", ".R")}

    def upd(est):
        ped = est["extras"].get("pedais")
        if not ped:
            return
        for sf, sx in ((".L", 1), (".R", -1)):
            p = ped[sf]
            pc = Vector((sx * 1.0, p.y, p.z - 0.25))
            Kit.por_cil(bracos[sf], Vector((sx * 1.0, c.y, c.z)), pc)
            q = Vector((p.x, p.y, p.z - 0.25))
            Kit.por_cil(pedais[sf], Vector((sx * 0.9, q.y, q.z)), Vector((sx * max(abs(q.x) + 0.6, 1.6), q.y, q.z)))
    kit.moveis.append(upd)


# ---- polias e elásticos

def _maos(h, est):
    h.restaurar(est["est"])
    T = est["T"]
    return T @ h.pegada(".L"), T @ h.pegada(".R")


def _polia(kit, ctx, pr, am):
    A = ctx.p3(pr["ate"][0], pr["ate"][1])
    h = ctx.h
    hip = am[0]["root"]
    dupla = "crossover" in ctx.id or max(abs(a["gL"].x - a["gR"].x) for a in am) > 6.5 and "puxada" not in ctx.id
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
            xc = s * 8.0
            _torre(kit, Vector((xc, A.y, 0)), max(A.z + 2, 20), A.z, s)
            polias.append(Vector((xc - s * 0.9, A.y, A.z)))
    else:
        d = A.y - hip.y
        sent = 1.0 if d > 0 else -1.0
        if abs(d) < 1.5:
            sent = -1.0  # polia sobre a cabeça: torre à frente
        base = Vector((0, A.y + sent * 2.0, 0))
        alto = max(A.z + 1.5, 20)
        _torre(kit, base, alto, A.z, None)
        braco_y = base.y - sent * 0.4
        if abs(A.y - braco_y) > 0.3:
            kit.viga(Vector((0, braco_y, A.z + 0.55)), Vector((0, A.y, A.z + 0.55)), 0.45, 0.45, kit.quadro)
        kit.disco(A, 0.48, 0.18, kit.metal, verts=24)
        kit.disco(A, 0.32, 0.26, kit.quadro, verts=16)
        polias.append(A)
    cabos = [kit.cil_movel(0.045, kit.cabo_m, 8) for _ in polias]
    tipo = "corda" if any(s in ctx.id for s in ("triceps", "face", "abdominal")) else "barra"
    if remo:
        tipo = "barra"
    alca = kit.cil_movel(0.13, kit.preto, 12)
    cordas = [kit.cil_movel(0.11, kit.preto, 10) for _ in range(2)]
    puxador = kit.cil_movel(0.13, kit.metal, 12)

    def upd(est):
        gL, gR = _maos(h, est)
        if len(polias) == 2:
            for cab, p, g in zip(cabos, polias, ((gR if polias[0].x < 0 else gL), (gL if polias[0].x < 0 else gR))):
                Kit.por_cil(cab, p, g)
            for o in [alca, puxador] + cordas:
                o.hide_render = True
            return
        meio = (gL + gR) / 2
        lado = gL - gR
        dist = lado.length
        if dist > 3.5 or tipo == "barra":
            ext = lado.normalized() * (max(dist, 2.6) / 2 + 0.9)
            Kit.por_cil(puxador, meio - ext, meio + ext)
            puxador.hide_render = False
            Kit.por_cil(cabos[0], polias[0], meio)
            for o in cordas + [alca]:
                o.hide_render = True
        else:
            no = meio + (polias[0] - meio).normalized() * 1.1
            Kit.por_cil(cabos[0], polias[0], no)
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


def _elastico(kit, ctx, h, pr, am):
    ate = pr.get("ate")
    bat = "battle" in ctx.id
    if isinstance(ate, list):
        A = ctx.p3(ate[0], ate[1])
        if A.z > 1.2:
            kit.viga(Vector((0, A.y, 0.1)), Vector((0, A.y, A.z + 0.6)), 0.5, 0.5, kit.quadro)
            kit.caixa(Vector((0, A.y, 0.08)), (2.0, 2.0, 0.16), kit.quadro, 0.04)
        else:
            A.z = max(A.z, 0.3)
            kit.toro(A, 0.35, 0.08, kit.metal)
        n = 14 if bat else 1
        segs = {sf: [kit.cil_movel(0.2 if bat else 0.08, kit.preto if bat else kit.brasa, 10) for _ in range(n)] for sf in (".L", ".R")}

        def upd(est):
            gL, gR = _maos(h, est)
            fase = est["tau"] / max(ctx.trilhas.T, 1e-3) * 2 * math.pi
            for sf, g in ((".L", gL), (".R", gR)):
                fimA = A + X * (0.25 if sf == ".L" else -0.25)
                pts = []
                for i in range(n + 1):
                    s = i / n
                    p = g.lerp(fimA, s)
                    if bat:
                        p.z += math.sin(fase * 2 - s * 9) * 0.9 * (1 - s) * min(1, s * 4)
                        p.z = max(p.z, 0.2)
                    pts.append(p)
                for o, p, q in zip(segs[sf], pts[:-1], pts[1:]):
                    Kit.por_cil(o, p, q)
        kit.moveis.append(upd)
        return
    if ate == "pes":
        segs = {sf: kit.cil_movel(0.08, kit.brasa, 10) for sf in (".L", ".R")}

        def upd(est):
            h.restaurar(est["est"])
            T = est["T"]
            P = h.proxy(T)
            for sf, ef in ((".L", "pe_f"), (".R", "pe_t")):
                g = T @ h.pegada(sf)
                pts = P[h.px_partes[ef]]
                c = pts[pts[:, 2] < pts[:, 2].min() + 0.2].mean(axis=0)
                Kit.por_cil(segs[sf], g, Vector(c) + Vector((0, 0, 0.05)))
        kit.moveis.append(upd)
        return
    # entre as mãos
    a1, a2 = kit.cil_movel(0.09, kit.brasa, 10), kit.cil_movel(0.09, kit.brasa, 10)

    def upd(est):
        gL, gR = _maos(h, est)
        meio = (gL + gR) / 2
        Kit.por_cil(a1, gL, meio)
        Kit.por_cil(a2, meio, gR)
    kit.moveis.append(upd)


# ---- pesos nas mãos

def _barra(kit, ctx, h):
    R = raio_anilha(ctx)
    curta = R < 1.5
    b = barra_olimpica(kit, R, curta)

    def upd(est):
        if "barra" in est["extras"]:
            c, e = est["extras"]["barra"]
        else:
            gL, gR = _maos(h, est)
            c, e = (gL + gR) / 2, (gL - gR)
            e = e.normalized() if e.length > 1e-3 else X
        b.matrix_world = Matrix.Translation(c) @ _alinhar(X, e)
    kit.moveis.append(upd)


def _halteres(kit, ctx, h):
    hs = {sf: halter_peca(kit) for sf in (".L", ".R")}

    def upd(est):
        h.restaurar(est["est"])
        T = est["T"]
        for sf, o in hs.items():
            g = T @ h.pegada(sf)
            e = T.to_3x3() @ h.eixo_polegar(sf)
            o.matrix_world = Matrix.Translation(g) @ _alinhar(X, e)
    kit.moveis.append(upd)


def _kettlebell(kit, ctx, h):
    ps = [kit.esfera((0, 0, -1.15), 0.95, kit.preto), kit.toro((0, 0, -0.05), 0.5, 0.12, kit.preto, (1, 0, 0))]
    kb = kit.grupo_movel(ps)

    def upd(est):
        h.restaurar(est["est"])
        T = est["T"]
        gL, gR = T @ h.pegada(".L"), T @ h.pegada(".R")
        c = (gL + gR) / 2
        ante = T.to_3x3() @ ((h.cabeca("wrist.L") - h.cabeca("lowerarm01.L")) + (h.cabeca("wrist.R") - h.cabeca("lowerarm01.R"))).normalized()
        d = (Vector((0, 0, -1)) * 0.65 + ante * 0.35).normalized()
        kb.matrix_world = Matrix.Translation(c) @ _alinhar(Vector((0, 0, -1)), d)
    kit.moveis.append(upd)


def _bola(kit, ctx, h):
    b = kit.esfera((0, 0, 0), 1.1, kit.brasa)

    def upd(est):
        h.restaurar(est["est"])
        T = est["T"]
        gL, gR = T @ h.pegada(".L"), T @ h.pegada(".R")
        pal = Vector((0, 0, 0))
        for sf, sx in ((".L", 1), (".R", -1)):
            R = h.rot("wrist" + sf) @ h.rest_inv["wrist" + sf].to_3x3()
            pal += T.to_3x3() @ (R @ h.ref_mao[sf].col[2])
        c = (gL + gR) / 2 + (pal / 2) * 0.9
        b.matrix_world = Matrix.Translation(c)
    kit.moveis.append(upd)


def _corda(kit, ctx, h):
    n = 18
    segs = [kit.cil_movel(0.05, kit.brasa, 8) for _ in range(n)]

    def upd(est):
        h.restaurar(est["est"])
        T = est["T"]
        gL, gR = T @ h.pegada(".L"), T @ h.pegada(".R")
        r = T @ h.cabeca("root")
        fase = est["tau"] / max(ctx.trilhas.T / 2, 1e-3) * 2 * math.pi
        C = Vector((0, r.y, r.z + 0.6))
        R = r.z + 0.45 - ctx.z0
        M = C + Vector((0, -math.sin(fase) * R * 0.75, -math.cos(fase) * R))
        M.z = max(M.z, ctx.z0 + 0.06)
        meio = (gL + gR) / 2
        ctrl = M * 2 - meio
        pts = []
        for i in range(n + 1):
            s = i / n
            p = gL * (1 - s) ** 2 + ctrl * (2 * s * (1 - s)) + gR * s * s
            # abre lateralmente para passar por fora do corpo
            p.x += math.sin(s * math.pi) * 0.0
            pts.append(p)
        for o, p, q in zip(segs, pts[:-1], pts[1:]):
            Kit.por_cil(o, p, q)
    kit.moveis.append(upd)
