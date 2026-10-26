"""Verificação automática das animações 3D (sem renderizar): roda o motor (preparar_anim + quadro em cada instante
do vídeo) e mede, no espaço do mundo (1 unidade = 1 dm):

ERROS (reprovam):
  pop        salto de pose num quadro: deslocamento máximo de junta > 2,2x a mediana dos 4 vizinhos e > 4 cm
  emenda     o mesmo teste na volta do laço (último quadro -> primeiro)
  skate      pé/mão apoiado escorregando (antepé / pegada): > 3 mm/quadro a 24 fps (descontado o piso rolante)
             ou apoio que muda < 16 cm entre chaves (escorrega em vez de dar passo)
  chao       pele abaixo do chão: > 8 mm (sola do tênis na proxy)
  barra      centro da barra salta num quadro isolado: > 2,5x os vizinhos e > 5 cm
  alavanca   alavanca de máquina com comprimento variando > 2 mm
  rosto      mão (ou pegada do implemento) na frente do rosto, cobrindo > 15 % da área da cabeça projetada
AVISOS:
  congelado  sequência de > 6 quadros sem movimento (< 0,5 mm)
  flutua     pé/mão apoiado fora de [-8 mm, +8 mm] da superfície
  chaves     quadros-chave consecutivos idênticos

Uso (python do ambiente com bpy):
  python tools/anim3d/qa.py --mh <makehuman/data> --anim lote1.json lote2.json lote3.json [--ids a,b] [--saida qa.json] [--fps 24]
Sai com código 1 se algum exercício tiver erro (use --so-avisar para nunca falhar).
"""
import argparse
import json
import math
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

import bpy  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Vector  # noqa: E402

import humano as H  # noqa: E402
import aparelhos  # noqa: E402
import qa_corpo as QC  # noqa: E402

OSSOS = ("root", "spine03", "neck01", "head", "upperarm01.L", "upperarm01.R", "lowerarm01.L", "lowerarm01.R", "wrist.L",
         "wrist.R", "upperleg01.L", "upperleg01.R", "lowerleg01.L", "lowerleg01.R", "foot.L", "foot.R")


def pops(D, lim_rel=2.2, lim_abs=0.4):
    """D[j] = deslocamento máximo do quadro j para j+1 (laço). Índices com salto isolado."""
    n = len(D)
    out = []
    if n < 6:
        return out
    for j in range(n):
        viz = [D[(j + d) % n] for d in (-2, -1, 1, 2)]
        med = float(np.median(viz))
        if D[j] > lim_abs and D[j] > lim_rel * max(med, 1e-3):
            out.append(j)
    return out


def avaliar(h, anim, k, grupo, fps, corpo=None, kit=None, so_motor=False):
    ctx = H.preparar_anim(h, anim, k, grupo)
    taus = ctx.trilhas.instantes(fps)
    estados = [H.quadro(h, ctx, t) for t in taus]
    n = len(estados)
    J, faces, maos, barra, efs, zmin_corpo, alav = [], [], [], [], [], [], []
    cam, el = H.camera_familia(anim, ctx) if hasattr(H, "camera_familia") else (anim.get("cam", 64), 10.0)
    dirc, direita, cima = H.base_camera(H.azimute_de_cam(cam), el)
    for est in estados:
        h.restaurar(est["est"])
        T = est["T"]
        J.append([list(T @ h.cabeca(o)) for o in OSSOS])
        cab = (T @ h.cabeca("head") + T @ h.cauda("head")) / 2
        faces.append(cab)
        maos.append([T @ h.pegada(".L"), T @ h.pegada(".R")])
        if "barra" in est["extras"]:
            barra.append(list(est["extras"]["barra"][0]))
        P = h.proxy(T)
        zmin_corpo.append(float(P[:, 2].min()))
        e = {}
        for ef, membro, sf in H.EFETORES:
            inf = H.info_efetor(h, ctx, T, ef, membro, sf, P)
            if "pesos" in est:
                w = est["pesos"].get(ef, 0.0)
            else:  # motor antigo (comparação): apoio nas duas chaves do trecho
                i_, u_ = ctx.trilhas.segmento(est["tau"])
                c1, c2 = ctx.chaves[i_]["ef"][ef], ctx.chaves[(i_ + 1) % len(ctx.chaves)]["ef"][ef]
                w = 1.0 if c1["contato"] and c2["contato"] and (c1["baixo"] - c2["baixo"]).length < 1.6 else 0.0
            # ponto rígido do pé/mão (tornozelo + base dos dedos): a pele do calcanhar deforma com a canela
            cen = inf.get("ponta", inf["pos"])  # antepé (pivô do apoio, rígido no osso do pé) ou centro da pegada
            e[ef] = (cen, inf["zmin"], w, inf["baixo"], inf.get("zbola", inf["zmin"]))
        efs.append(e)
        cfg = getattr(ctx, "alavancas", None)
        if cfg:
            ls = []
            for sf in (".L", ".R"):
                piv, ax, L = cfg[sf]
                r = T @ h.pegada(sf) - piv
                ls.append((r - ax * r.dot(ax)).length)
            alav.append(ls)
    J = np.array(J)
    DJ = np.linalg.norm(np.roll(J, -1, axis=0) - J, axis=2)
    D = DJ.max(axis=1)
    erros, avisos = [], []
    ps = pops(D, lim_abs=0.4 * 24.0 / fps)
    # confirma com meio passo: num salto de verdade a metade do deslocamento NÃO cai pela metade
    confirmados = []
    for j in ps:
        t0, t1 = taus[j], (taus[j + 1] if j + 1 < n else ctx.trilhas.T)
        pm = []
        for tt in (t0, (t0 + t1) / 2, t1):
            est = H.quadro(h, ctx, tt)
            h.restaurar(est["est"])
            pm.append(np.array([list(est["T"] @ h.cabeca(o)) for o in OSSOS]))
        d1 = np.linalg.norm(pm[1] - pm[0], axis=1).max()
        d2 = np.linalg.norm(pm[2] - pm[1], axis=1).max()
        if max(d1, d2) > 0.72 * max(D[j], 1e-6):
            confirmados.append(j)
    ps = confirmados
    for j in ps:
        erros.append(f"{'emenda' if j == n - 1 else 'pop'} no quadro {j} ({D[j] * 10:.1f} cm, {OSSOS[int(DJ[j].argmax())]})")
    # congelado
    run = best = 0
    for d in D:
        run = run + 1 if d < 0.005 else 0
        best = max(best, run)
    if best > 6:
        avisos.append(f"congelado {best} quadros")
    # chão
    zc = min(zmin_corpo) - ctx.z0
    if zc < -0.08:
        erros.append(f"chao: pele {abs(zc) * 10:.1f} cm abaixo do chão")
    # skate e flutuar
    vel = getattr(ctx, "vel_rolar", (0.0, 0.0))
    if not isinstance(vel, tuple):
        vel = (0.0, vel)
    dt = ctx.trilhas.T / n
    pior = {}
    for j in range(n):
        a, b = efs[j], efs[(j + 1) % n]
        for ef in a:
            pa, za, wa, ba = a[ef][:4]
            pb, zb, wb, bb = b[ef][:4]
            if wa > 0.999 and wb > 0.999:
                rola = ef.startswith("pe") or (getattr(ctx, "rolar", False) and za < ctx.z0 + 0.5)
                vx, vy = vel if rola else (0.0, 0.0)
                d = Vector((pb.x - pa.x - vx * dt, pb.y - pa.y - vy * dt, 0)).length
                pior[ef] = max(pior.get(ef, 0.0), d)
            if wa > 0.999 and not (ef.startswith("mao") and ctx.barra is not None):
                zs = ctx.superficie_em(ba, za)
                gap = za - zs
                if ef.startswith("pe"):  # antepé na borda do degrau (calcanhar no ar) também é apoio
                    zbo = a[ef][4]
                    gap = min(abs(gap), abs(zbo - ctx.superficie_em(pa, zbo)))
                if not -0.08 <= gap <= 0.08:
                    pior["_f_" + ef] = max(pior.get("_f_" + ef, 0.0), abs(gap))
    for ef, d in pior.items():
        if ef.startswith("_f_"):
            avisos.append(f"flutua {ef[3:]} {d * 10:.1f} cm")
        elif d * fps / 24.0 > 0.03:
            erros.append(f"skate {ef} {d * 100 * fps / 24.0:.1f} mm/quadro(24fps)")
    ch = ctx.chaves
    for i, c in enumerate(ch):
        c2 = ch[(i + 1) % len(ch)]
        for ef in c["ef"]:
            a, b = c["ef"][ef], c2["ef"][ef]
            pa_, pb_ = a.get("ponta", a["pos"]), b.get("ponta", b["pos"])
            dd = Vector((pa_.x - pb_.x, pa_.y - pb_.y, 0)).length
            if a["contato"] and b["contato"] and 0.15 < dd < 1.6 and not getattr(ctx, "rolar", False):
                erros.append(f"skate {ef} {dd * 10:.1f} cm no trecho {i}")
    # barra
    if len(barra) == n:
        B = np.array(barra)
        dB = np.linalg.norm(np.roll(B, -1, axis=0) - B, axis=1)
        for j in pops(dB, lim_rel=2.5, lim_abs=0.5 * 24.0 / fps):
            erros.append(f"barra salta no quadro {j} ({dB[j] * 10:.1f} cm)")
    # alavanca
    if alav:
        A = np.array(alav)
        var = float((A.max(axis=0) - A.min(axis=0)).max())
        if var > 0.02:
            erros.append(f"alavanca varia {var * 100:.1f} mm")
    # rosto
    dc, dr, cm = np.array(dirc), np.array(direita), np.array(cima)
    pior_r = 0.0
    for cab, ms in zip(faces, maos):
        c = np.array(cab)
        for m in ms:
            m = np.array(m)
            if np.dot(m - c, dc) < 0.3:  # mão atrás da cabeça (em relação à câmera)
                continue
            d = math.hypot(np.dot(m - c, dr), np.dot(m - c, cm))
            R1, R2 = 1.05, 0.55
            if d >= R1 + R2:
                continue
            if d <= R1 - R2:
                frac = (R2 / R1) ** 2
            else:
                a1 = R1 * R1 * math.acos((d * d + R1 * R1 - R2 * R2) / (2 * d * R1))
                a2 = R2 * R2 * math.acos((d * d + R2 * R2 - R1 * R1) / (2 * d * R2))
                a3 = 0.5 * math.sqrt(max(0.0, (-d + R1 + R2) * (d + R1 - R2) * (d - R1 + R2) * (d + R1 + R2)))
                frac = (a1 + a2 - a3) / (math.pi * R1 * R1)
            pior_r = max(pior_r, frac)
    if pior_r > 0.15 and not anim.get("rosto_ok"):  # rosto_ok: a mão no rosto É o exercício (isometria de pescoço)
        erros.append(f"rosto coberto {pior_r * 100:.0f}%")
    # chaves idênticas
    for i, q in enumerate(anim["quadros"]):
        q2 = anim["quadros"][(i + 1) % len(anim["quadros"])]
        if q == q2:
            avisos.append(f"chaves {i} e {(i + 1) % len(anim['quadros'])} idênticas")
    achados = [{"tipo": "motor", "sub": m_.split(" ")[0], "nivel": "erro", "msg": m_} for m_ in erros]
    achados += [{"tipo": "motor", "sub": m_.split(" ")[0], "nivel": "aviso", "msg": m_} for m_ in avisos]
    if corpo is not None and not so_motor:
        kit.limpar()
        aparelhos.montar(kit, ctx, h, estados)
        bpy.context.view_layer.update()
        novos = QC.avaliar_corpo(h, corpo, ctx, estados, taus, fps, kit)
        kit.limpar()
        achados += novos
        for a_ in novos:
            (erros if a_["nivel"] == "erro" else avisos).append(a_["msg"])
    return {"erros": erros, "avisos": avisos, "achados": achados, "quadros": n, "T": round(float(ctx.trilhas.T), 2)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mh", required=True)
    ap.add_argument("--anim", required=True, nargs="+")
    ap.add_argument("--ex", default=os.path.join(AQUI, "..", "..", "app", "src", "main", "assets", "exercises.json"))
    ap.add_argument("--ids", default="")
    ap.add_argument("--saida", default="")
    ap.add_argument("--fps", type=float, default=24)
    ap.add_argument("--so-avisar", action="store_true")
    ap.add_argument("--retomar", action="store_true", help="pula os ids que já estão no arquivo --saida (gravado a cada exercício)")
    ap.add_argument("--so-motor", action="store_true", help="só as verificações antigas (sem pegada/ROM/apoio)")
    a = ap.parse_args(sys.argv[1:])
    bpy.ops.wm.read_factory_settings(use_empty=True)
    H.cena(64, 1)
    h = H.Humano(a.mh)
    grupos = {e["id"]: e for e in json.load(open(a.ex))}
    k = (h.juntas[h.ossos["upperleg01.L"]["head"]][2] - h.juntas[h.ossos["foot.L"]["head"]][2]) / 8.7
    corpo = None if a.so_motor else QC.Corpo(h)
    kit = None if a.so_motor else aparelhos.Kit()
    ids = set(x for x in a.ids.split(",") if x)
    res = {}
    if a.retomar and a.saida and os.path.exists(a.saida):
        res = json.load(open(a.saida))
    for arq in a.anim:
        for anim in json.load(open(arq)):
            if ids and anim["id"] not in ids:
                continue
            if anim["id"] in res and a.retomar:
                continue
            try:
                r = avaliar(h, anim, k, grupos.get(anim["id"], {}).get("grupo", ""), a.fps, corpo, kit, a.so_motor)
            except Exception as e:  # noqa: BLE001
                import traceback
                traceback.print_exc()
                r = {"erros": [f"exceção: {e!r}"], "avisos": [], "achados": [{"tipo": "motor", "sub": "exceção", "nivel": "erro", "msg": repr(e)}]}
            res[anim["id"]] = r
            marca = "ERRO " if r["erros"] else ("aviso" if r["avisos"] else "ok   ")
            print(marca, anim["id"], "; ".join(r["erros"] + r["avisos"]), flush=True)
            if a.saida:
                json.dump(res, open(a.saida, "w"), indent=1, ensure_ascii=False)
    ne = sum(1 for r in res.values() if r["erros"])
    na = sum(1 for r in res.values() if r["avisos"] and not r["erros"])
    print(f"QA: {len(res)} exercícios, {ne} com erro, {na} só com aviso, {len(res) - ne - na} limpos")
    if a.saida:
        json.dump(res, open(a.saida, "w"), indent=1, ensure_ascii=False)
    sys.exit(1 if ne and not a.so_avisar else 0)


if __name__ == "__main__":
    main()
