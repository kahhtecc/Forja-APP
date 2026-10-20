"""Renderizador anatômico do Forja: atleta "esculpido em bronze" com musculatura definida;
os músculos trabalhados acendem em brasa. Usa as poses de esqueleto.py.

Uso: python3 tools/anim/anatomico.py <dados.json> [slug ...] --saida pasta [--sprites] [--tam 288]
  sem --sprites: gera <slug>.png (quadros-chave) e <slug>.gif para revisão
  com --sprites: gera <slug>.webp (grade de quadros) + meta.json para o app
"""
import io
import json
import math
import os
import sys

import cairo
from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from esqueleto import L, completar, interpolar, pontos_anim  # noqa: E402

# Paleta
FUNDO_TOPO = (0.105, 0.094, 0.082)
FUNDO_BASE = (0.055, 0.051, 0.047)
BRONZE = (0.50, 0.31, 0.19)
BRONZE_CLARO = (0.80, 0.54, 0.34)
BRONZE_BRILHO = (1.00, 0.86, 0.66)
BRONZE_SOMBRA = (0.13, 0.08, 0.05)
BRASA = (1.0, 0.36, 0.13)
BRASA_CLARA = (1.0, 0.70, 0.42)
SHORT = (0.10, 0.10, 0.11)
SHORT_CLARO = (0.22, 0.22, 0.24)
TENIS = (0.12, 0.11, 0.11)
METAL = (0.55, 0.53, 0.50)
METAL_CLARO = (0.85, 0.83, 0.80)

# Perfis de largura (t ao longo do segmento, largura frente, largura trás) em unidades
PERFIS = {
    "coxa": [(-0.08, 0.98, 1.05), (0.12, 1.12, 1.15), (0.36, 1.18, 1.00), (0.58, 1.05, 0.92), (0.82, 0.78, 0.66), (1.0, 0.58, 0.56), (1.08, 0.50, 0.50)],
    "canela": [(-0.06, 0.52, 0.56), (0.15, 0.48, 0.86), (0.32, 0.45, 0.84), (0.56, 0.38, 0.52), (0.84, 0.29, 0.31), (1.0, 0.26, 0.28), (1.04, 0.24, 0.26)],
    "braco": [(-0.08, 0.66, 0.66), (0.20, 0.60, 0.66), (0.50, 0.66, 0.62), (0.78, 0.50, 0.46), (1.0, 0.38, 0.38), (1.08, 0.34, 0.34)],
    "antebraco": [(-0.08, 0.40, 0.42), (0.22, 0.52, 0.46), (0.56, 0.36, 0.33), (1.0, 0.24, 0.25), (1.05, 0.23, 0.23)],
    "tronco": [(-0.04, 1.06, 1.30), (0.12, 1.04, 1.26), (0.30, 1.04, 1.00), (0.47, 1.12, 1.12), (0.62, 1.34, 1.30), (0.76, 1.46, 1.40), (0.89, 1.20, 1.24), (1.0, 0.62, 0.78)],
}

# Linhas de definição muscular: (segmento, lado, t0, t1, deslocamento relativo da borda)
DEFINICAO = {
    "coxa": [("f", 0.30, 0.92, 0.42), ("b", 0.20, 0.75, 0.30), ("f", 0.72, 0.95, 0.15)],
    "canela": [("b", 0.08, 0.55, 0.45)],
    "braco": [("m", 0.18, 0.92, 0.0)],
    "antebraco": [("f", 0.08, 0.55, 0.35)],
}


def _dir(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    ln = math.hypot(dx, dy) or 1e-6
    return dx / ln, dy / ln, ln


def contorno(a, b, perfil, frente_para_cima=False):
    """Pontos do contorno de um segmento (mundo). Normal da frente: rotação da direção."""
    ux, uy, ln = _dir(a, b)
    nx, ny = uy, -ux  # perpendicular
    # Para segmentos que apontam para baixo/frente, a 'frente' anatômica é a direita da direção de descida
    nx, ny = -nx, -ny
    if frente_para_cima:
        nx, ny = -nx, -ny
    frente, tras = [], []
    for t, wf, wb in perfil:
        cx, cy = a[0] + ux * ln * t, a[1] + uy * ln * t
        frente.append((cx + nx * wf, cy + ny * wf))
        tras.append((cx - nx * wb, cy - ny * wb))
    return frente, tras, (nx, ny), (ux, uy, ln)


def catmull(ctx, pts, fechado=True):
    n = len(pts)
    if n < 3:
        return
    ctx.move_to(*pts[0])
    rng = range(n) if fechado else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (fechado or i > 0) else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (fechado or i + 2 < n) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        ctx.curve_to(c1[0], c1[1], c2[0], c2[1], p2[0], p2[1])
    if fechado:
        ctx.close_path()


def escurecer(c, f):
    return tuple(x * f for x in c)


class Pintor:
    def __init__(self, tam, caixa):
        self.tam = tam
        self.sup = cairo.ImageSurface(cairo.FORMAT_ARGB32, tam, tam)
        self.ctx = cairo.Context(self.sup)
        self.brilho = cairo.ImageSurface(cairo.FORMAT_ARGB32, tam, tam)
        self.cb = cairo.Context(self.brilho)
        x0, y0, x1, y1 = caixa
        margem = 0.10
        esc = min(tam * (1 - 2 * margem) / max(x1 - x0, 1e-3), tam * (1 - 2 * margem - 0.06) / max(y1 - y0, 1e-3))
        self.esc = esc
        self.ox = tam / 2 - (x0 + x1) / 2 * esc
        self.chao = tam * (1 - margem)
        for c in (self.ctx, self.cb):
            c.translate(self.ox, self.chao)
            c.scale(esc, -esc)

    # ----- fundo
    def fundo(self, cx_quadril):
        c = self.ctx
        c.save(); c.identity_matrix()
        g = cairo.LinearGradient(0, 0, 0, self.tam)
        g.add_color_stop_rgb(0, *FUNDO_TOPO); g.add_color_stop_rgb(1, *FUNDO_BASE)
        c.set_source(g); c.paint()
        # holofote
        rg = cairo.RadialGradient(self.tam * 0.5, self.tam * 0.35, 0, self.tam * 0.5, self.tam * 0.35, self.tam * 0.7)
        rg.add_color_stop_rgba(0, 1, 0.75, 0.55, 0.07); rg.add_color_stop_rgba(1, 0, 0, 0, 0)
        c.set_source(rg); c.paint()
        # chão
        c.set_source_rgba(1, 1, 1, 0.06); c.set_line_width(1.5)
        c.move_to(0, self.chao); c.line_to(self.tam, self.chao); c.stroke()
        c.restore()
        # sombra
        c.save()
        c.translate(cx_quadril, 0); c.scale(1, 0.12)
        sg = cairo.RadialGradient(0, 0, 0, 0, 0, 6)
        sg.add_color_stop_rgba(0, 0, 0, 0, 0.55); sg.add_color_stop_rgba(1, 0, 0, 0, 0)
        c.set_source(sg); c.arc(0, 0, 6, 0, 2 * math.pi); c.fill()
        c.restore()

    # ----- preenchimento de músculo com volume
    def volume(self, caminho, frente, tras, base, longe=False, destaque=False):
        c = self.ctx
        f = 0.55 if longe else 1.0
        claro, medio, sombra = escurecer(BRONZE_CLARO, f), escurecer(base, f), escurecer(BRONZE_SOMBRA, f)
        # gradiente da borda de trás (sombra) para a da frente (luz)
        mf = frente[len(frente) // 2]; mt = tras[len(tras) // 2]
        g = cairo.LinearGradient(mt[0], mt[1], mf[0], mf[1])
        g.add_color_stop_rgb(0, *sombra); g.add_color_stop_rgb(0.45, *medio); g.add_color_stop_rgb(0.85, *claro); g.add_color_stop_rgb(1, *escurecer(BRONZE_BRILHO, f))
        caminho(c); c.set_source(g); c.fill()
        if destaque and not longe:
            caminho(c)
            gd = cairo.LinearGradient(mt[0], mt[1], mf[0], mf[1])
            gd.add_color_stop_rgba(0, *BRASA, 0.55); gd.add_color_stop_rgba(1, *BRASA_CLARA, 0.85)
            c.set_source(gd); c.fill()
            caminho(self.cb); self.cb.set_source_rgba(*BRASA, 0.9); self.cb.fill()

    def segmento(self, nome, a, b, longe=False, destaque=False, frente_para_cima=False):
        frente, tras, n, (ux, uy, ln) = contorno(a, b, PERFIS[nome], frente_para_cima)
        pts = frente + list(reversed(tras))
        self.volume(lambda c: catmull(c, pts), frente, tras, BRONZE, longe, destaque)
        # definição muscular
        c = self.ctx
        for lado, t0, t1, rel in DEFINICAO.get(nome, []):
            linha = []
            for k in range(7):
                t = t0 + (t1 - t0) * k / 6
                ix = min(int(t * (len(PERFIS[nome]) - 1)), len(PERFIS[nome]) - 2)
                p0, p1 = PERFIS[nome][ix], PERFIS[nome][ix + 1]
                lt = (t - p0[0]) / max(p1[0] - p0[0], 1e-6)
                wf = p0[1] + (p1[1] - p0[1]) * lt
                wb = p0[2] + (p1[2] - p0[2]) * lt
                cx, cy = a[0] + ux * ln * t, a[1] + uy * ln * t
                off = (wf * (1 - rel)) if lado == "f" else (-wb * (1 - rel) if lado == "b" else (wf - wb) * 0.5)
                linha.append((cx + n[0] * off, cy + n[1] * off))
            catmull(c, linha, fechado=False)
            c.set_source_rgba(*escurecer(BRONZE_SOMBRA, 0.7), 0.45 if not longe else 0.25); c.set_line_width(0.07); c.stroke()
        return frente, tras, n

    def articulacao(self, p, r, longe=False):
        return
        c = self.ctx
        f = 0.55 if longe else 1.0
        g = cairo.RadialGradient(p[0] + r * 0.3, p[1] + r * 0.3, 0, p[0], p[1], r)
        g.add_color_stop_rgb(0, *escurecer(BRONZE_CLARO, f)); g.add_color_stop_rgb(1, *escurecer(BRONZE, f * 0.9))
        c.set_source(g); c.arc(p[0], p[1], r, 0, 2 * math.pi); c.fill()

    def deltoide(self, ombro, cotovelo, longe=False, destaque=False):
        ux, uy, ln = _dir(ombro, cotovelo)
        nx, ny = -uy, ux
        cx, cy = ombro[0] + ux * 0.55, ombro[1] + uy * 0.55
        pts = [(ombro[0] - ux * 0.35 + nx * 0.2, ombro[1] - uy * 0.35 + ny * 0.2), (cx + nx * 0.78, cy + ny * 0.78), (cx + ux * 1.15 + nx * 0.35, cy + uy * 1.15 + ny * 0.35),
               (cx + ux * 1.25 - nx * 0.3, cy + uy * 1.25 - ny * 0.3), (cx - nx * 0.72, cy - ny * 0.72), (ombro[0] - ux * 0.35 - nx * 0.25, ombro[1] - uy * 0.35 - ny * 0.25)]
        self.volume(lambda c: catmull(c, pts), [pts[1]], [pts[4]], BRONZE, longe, destaque)

    def mao(self, cot, mao, longe=False):
        ux, uy, _ = _dir(cot, mao)
        c = self.ctx
        p = (mao[0] + ux * 0.25, mao[1] + uy * 0.25)
        f = 0.55 if longe else 1.0
        g = cairo.RadialGradient(p[0] + 0.1, p[1] + 0.1, 0, p[0], p[1], 0.42)
        g.add_color_stop_rgb(0, *escurecer(BRONZE_CLARO, f)); g.add_color_stop_rgb(1, *escurecer(BRONZE, f * 0.85))
        c.save(); c.translate(*p); c.rotate(math.atan2(uy, ux)); c.scale(1.25, 0.95)
        c.arc(0, 0, 0.36, 0, 2 * math.pi); c.restore()
        c.set_source(g); c.fill()

    def pe(self, tornozelo, ponta, calcanhar, longe=False):
        c = self.ctx
        ux, uy, ln = _dir(calcanhar, ponta)
        nx, ny = -uy, ux
        if ny < 0:
            nx, ny = -nx, -ny  # 'para cima' do pé
        pts = [(calcanhar[0] - ux * 0.15, calcanhar[1] - uy * 0.15), (calcanhar[0] + nx * 0.55, calcanhar[1] + ny * 0.55),
               (tornozelo[0] + nx * 0.45 + ux * 0.25, tornozelo[1] + ny * 0.45 + uy * 0.25), (ponta[0] - ux * 0.35 + nx * 0.32, ponta[1] - uy * 0.35 + ny * 0.32),
               (ponta[0] + ux * 0.1, ponta[1] + uy * 0.1), (ponta[0] - ux * 0.2 - nx * 0.05, ponta[1] - uy * 0.2 - ny * 0.05), (calcanhar[0] - nx * 0.05, calcanhar[1] - ny * 0.05)]
        f = 0.55 if longe else 1.0
        catmull(c, pts)
        g = cairo.LinearGradient(calcanhar[0] - nx, calcanhar[1] - ny, calcanhar[0] + nx, calcanhar[1] + ny)
        g.add_color_stop_rgb(0, *escurecer(TENIS, f)); g.add_color_stop_rgb(1, *escurecer((0.30, 0.29, 0.28), f))
        c.set_source(g); c.fill()
        # solado em brasa
        c.move_to(calcanhar[0] - ux * 0.1, calcanhar[1] - uy * 0.1); c.line_to(ponta[0], ponta[1])
        c.set_source_rgba(*BRASA, 0.85 if not longe else 0.4); c.set_line_width(0.14); c.stroke()

    def tronco(self, quadril, pescoco, destaque, olhar):
        frente, tras, n, (ux, uy, ln) = contorno(quadril, pescoco, PERFIS["tronco"], frente_para_cima=True)
        pts = frente + list(reversed(tras))
        dest = bool(destaque & {"tronco", "peito", "abdomen", "costas"})
        self.volume(lambda c: catmull(c, pts), frente, tras, BRONZE, False, dest)
        c = self.ctx

        def ponto(t, off):
            return (quadril[0] + ux * ln * t + n[0] * off, quadril[1] + uy * ln * t + n[1] * off)
        # peitoral (linha inferior), abdômen (gomos), oblíquo, dorsal
        linhas = [
            [ponto(0.66, 1.15), ponto(0.70, 0.75), ponto(0.73, 0.35)],
            [ponto(0.50, 0.98), ponto(0.50, 0.70)], [ponto(0.38, 0.97), ponto(0.38, 0.70)], [ponto(0.26, 0.96), ponto(0.26, 0.70)],
            [ponto(0.58, 0.86), ponto(0.42, 0.60), ponto(0.18, 0.55)],
            [ponto(0.80, -1.10), ponto(0.62, -0.70), ponto(0.42, -0.85)],
        ]
        for l in linhas:
            catmull(c, l, fechado=False) if len(l) > 2 else (c.move_to(*l[0]), c.line_to(*l[1]))
            c.set_source_rgba(*escurecer(BRONZE_SOMBRA, 0.7), 0.45); c.set_line_width(0.07); c.stroke()
        # short
        sp = [ponto(-0.02, 1.08), ponto(0.16, 1.02), ponto(0.18, -1.18), ponto(-0.02, -1.28)]
        return frente, tras, sp

    def short(self, quadril, joelho_f, joelho_t, sp):
        c = self.ctx
        pts = []
        for jo in (joelho_t, joelho_f):
            ux, uy, ln = _dir(quadril, jo)
        # contorno: cintura (do tronco) + coxa até 38%
        def coxa_pontos(jo):
            fr, tr, _, _ = contorno(quadril, jo, [(0.0, 1.05, 1.12), (0.2, 1.1, 1.14), (0.38, 1.12, 0.98)])
            return fr, tr
        frf, trf = coxa_pontos(joelho_f)
        frt, trt = coxa_pontos(joelho_t)
        pts = [sp[1], sp[0], frf[1], frf[2], trf[2], trf[1], trt[2], sp[3], sp[2]]
        catmull(c, pts)
        mid = frf[2]
        g = cairo.LinearGradient(sp[3][0], sp[3][1], sp[0][0], sp[0][1])
        g.add_color_stop_rgb(0, *SHORT); g.add_color_stop_rgb(1, *SHORT_CLARO)
        c.set_source(g); c.fill_preserve()
        c.set_source_rgba(0, 0, 0, 0.5); c.set_line_width(0.05); c.stroke()
        # faixa lateral em brasa
        c.move_to(*sp[1]); c.line_to(mid[0] * 0.5 + trf[2][0] * 0.5, mid[1] * 0.5 + trf[2][1] * 0.5)
        c.set_source_rgba(*BRASA, 0.8); c.set_line_width(0.12); c.stroke()

    def cabeca(self, pescoco, cabeca, olhar_dir):
        c = self.ctx
        # pescoço
        frente, tras, _, _ = contorno(pescoco, cabeca, [(0.0, 0.52, 0.60), (0.5, 0.40, 0.45), (0.8, 0.40, 0.42)], frente_para_cima=True)
        pts = frente + list(reversed(tras))
        self.volume(lambda cc: catmull(cc, pts), frente, tras, BRONZE)
        ux, uy, _ = _dir(pescoco, cabeca)
        ang = math.atan2(uy, ux) - math.pi / 2  # rotação da cabeça (0 = em pé)
        c.save(); c.translate(*cabeca); c.rotate(ang)
        # crânio + rosto de perfil (olhando para +x)
        perfil = [(-0.95, 0.15), (-0.80, 0.80), (-0.15, 1.12), (0.55, 0.95), (0.88, 0.45), (0.92, 0.05), (1.10, -0.12), (0.90, -0.30),
                  (0.95, -0.50), (0.70, -0.80), (0.35, -0.98), (-0.10, -0.92), (-0.55, -0.55), (-0.90, -0.25)]
        catmull(c, perfil)
        g = cairo.LinearGradient(-1, 0, 1, 0.3)
        g.add_color_stop_rgb(0, *BRONZE_SOMBRA); g.add_color_stop_rgb(0.5, *BRONZE); g.add_color_stop_rgb(0.9, *BRONZE_CLARO); g.add_color_stop_rgb(1, *BRONZE_BRILHO)
        c.set_source(g); c.fill()
        # cabelo curto
        cabelo = [(-0.98, 0.10), (-0.85, 0.85), (-0.15, 1.18), (0.55, 1.00), (0.70, 0.70), (0.20, 0.78), (-0.40, 0.62), (-0.62, 0.15)]
        catmull(c, cabelo); c.set_source_rgb(0.10, 0.08, 0.07); c.fill()
        # orelha e sobrancelha
        c.save(); c.translate(-0.15, 0.05); c.scale(0.18, 0.28); c.arc(0, 0, 1, 0, 2 * math.pi); c.restore()
        c.set_source_rgba(*BRONZE_SOMBRA, 0.8); c.fill()
        c.move_to(0.55, 0.32); c.line_to(0.85, 0.30); c.set_source_rgba(0.1, 0.08, 0.07, 0.8); c.set_line_width(0.08); c.stroke()
        c.restore()

    def finalizar(self):
        """Compõe o brilho (glow) dos músculos ativos e devolve uma imagem PIL."""
        base = Image.frombuffer("RGBA", (self.tam, self.tam), bytes(self.sup.get_data()), "raw", "BGRA", 0, 1)
        brilho = Image.frombuffer("RGBA", (self.tam, self.tam), bytes(self.brilho.get_data()), "raw", "BGRA", 0, 1)
        if brilho.getbbox():
            glow = brilho.filter(ImageFilter.GaussianBlur(self.tam / 40))
            r, g, b, a = glow.split()
            a = a.point(lambda v: int(v * 0.55))
            glow.putalpha(a)
            fundo = Image.new("RGBA", base.size, (0, 0, 0, 0))
            fundo.alpha_composite(glow)
            fundo.alpha_composite(base)
            base = Image.alpha_composite(Image.new("RGBA", base.size, (0, 0, 0, 255)), base)
            base = Image.blend(base, Image.alpha_composite(base, glow), 0.6)
        return base.convert("RGB")


def caixa_anim(anim):
    xs, ys = [], [0.0]
    q = anim["quadros"]
    tempos = anim.get("tempos", [1.0] * len(q))
    for i in range(len(q)):
        for k in range(6):
            p = pontos_anim(anim, interpolar(q[i], q[(i + 1) % len(q)], k / 6))
            for nome, v in p.items():
                r = 1.3 if nome != "cabeca" else 1.2
                xs += [v[0] - r, v[0] + r]; ys += [v[1] + r]
    for pr in anim.get("props", []):
        tp = pr.get("tipo")
        if tp in ("banco", "maquina", "caixa"):
            xs += [pr.get("x", 0), pr.get("x", 0) + pr.get("w", 8)]; ys += [pr.get("y", 0) + pr.get("h", 4)]
        elif tp == "barra_fixa":
            ys += [pr.get("y", 21) + 0.6]; xs += [pr.get("x", 0) - 2.5, pr.get("x", 0) + 2.5]
        elif tp == "saco":
            xs += [pr.get("x", 9) + 1.6]
    w = max(xs) - min(xs); h = max(ys)
    lado = max(w, h, 12)
    cx = (max(xs) + min(xs)) / 2
    return (cx - lado / 2, 0, cx + lado / 2, lado)


def desenhar_props(pt, anim, pts, fase):
    c = pt.ctx
    for pr in anim.get("props", []):
        tp = pr.get("tipo")
        if fase == "fundo":
            if tp in ("banco", "maquina", "caixa"):
                x, y, w, h = pr.get("x", 0), pr.get("y", 0), pr.get("w", 8), pr.get("h", 4)
                # pés/estrutura
                c.set_source_rgb(*METAL); c.set_line_width(0.25)
                for xx in (x + 0.8, x + w - 0.8):
                    c.move_to(xx, y); c.line_to(xx, y + h - 0.6); c.stroke()
                g = cairo.LinearGradient(0, y + h, 0, y + h - 0.9)
                g.add_color_stop_rgb(0, 0.30, 0.27, 0.25); g.add_color_stop_rgb(1, 0.13, 0.12, 0.11)
                c.rectangle(x, y + h - 0.9, w, 0.9); c.set_source(g); c.fill()
                if tp == "maquina":
                    c.rectangle(x + w - 1.0, y, 1.0, h + 4); c.set_source_rgb(0.18, 0.17, 0.16); c.fill()
            elif tp == "barra_fixa":
                x, y = pr.get("x", 0), pr.get("y", 21)
                c.set_source_rgb(*METAL); c.set_line_width(0.22)
                c.move_to(x - 2.5, y); c.line_to(x + 2.5, y); c.stroke()
                c.set_line_width(0.3)
                for xx in (x - 2.5, x + 2.5):
                    c.move_to(xx, y); c.line_to(xx, y + 2); c.stroke()
            elif tp == "saco":
                x = pr.get("x", 9)
                c.set_source_rgb(*METAL); c.set_line_width(0.08); c.move_to(x, 30); c.line_to(x, 17.5); c.stroke()
                g = cairo.LinearGradient(x - 1.5, 0, x + 1.5, 0)
                g.add_color_stop_rgb(0, 0.10, 0.09, 0.09); g.add_color_stop_rgb(0.6, 0.30, 0.12, 0.08); g.add_color_stop_rgb(1, 0.15, 0.08, 0.06)
                c.save(); c.translate(x, 11.5)
                c.rectangle(-1.5, -6, 3, 12); c.restore(); c.set_source(g); c.fill()
            elif tp == "esteira":
                c.rectangle(-9, 0, 18, 0.35); c.set_source_rgb(0.16, 0.15, 0.14); c.fill()
                c.set_source_rgb(*METAL); c.set_line_width(0.2); c.move_to(8, 0.35); c.line_to(9.5, 9); c.stroke()
            elif tp == "tapete":
                c.rectangle(-10, 0, 20, 0.18); c.set_source_rgb(0.30, 0.13, 0.08); c.fill()
            elif tp == "bike":
                q = pts["quadril"]
                c.set_source_rgb(*METAL); c.set_line_width(0.22)
                for cx in (q[0] - 5.5, q[0] + 6.5):
                    c.arc(cx, 2.6, 2.6, 0, 2 * math.pi); c.stroke()
                c.move_to(q[0] - 0.3, q[1] - 0.6); c.line_to(q[0] + 1.2, 2.6); c.line_to(q[0] - 5.5, 2.6); c.stroke()
                c.move_to(q[0] + 1.2, 2.6); c.line_to(q[0] + 5.2, q[1] + 2.2); c.line_to(q[0] + 6.5, 2.6); c.stroke()
                c.rectangle(q[0] - 1.1, q[1] - 0.75, 2.0, 0.35); c.set_source_rgb(0.12, 0.11, 0.11); c.fill()
            elif tp == "rolo":
                x, y = pr.get("x", 0), pr.get("y", 0.8)
                g = cairo.RadialGradient(x - 0.2, y + 0.2, 0, x, y, 0.8)
                g.add_color_stop_rgb(0, 0.45, 0.20, 0.12); g.add_color_stop_rgb(1, 0.18, 0.08, 0.05)
                c.arc(x, y, 0.8, 0, 2 * math.pi); c.set_source(g); c.fill()
            elif tp in ("elastico", "cabo"):
                ate = pr.get("ate")
                a = pts["tornozelo_f"] if ate == "pes" else (ate[0], ate[1])
                m = pts["mao_f"]
                c.move_to(*m); c.line_to(*a)
                c.set_source_rgba(*(BRASA if tp == "elastico" else METAL_CLARO), 0.9); c.set_line_width(0.14 if tp == "elastico" else 0.07); c.stroke()
                if tp == "cabo":
                    c.arc(a[0], a[1], 0.45, 0, 2 * math.pi); c.set_source_rgb(*METAL); c.set_line_width(0.15); c.stroke()
        else:
            mf, mt = pts["mao_f"], pts["mao_t"]
            if tp == "barra":
                # barra vista de lado: anilha com brilho
                R = 1.7
                g = cairo.RadialGradient(mf[0] - 0.4, mf[1] + 0.4, 0, mf[0], mf[1], R)
                g.add_color_stop_rgba(0, 0.28, 0.27, 0.26, 0.96); g.add_color_stop_rgba(1, 0.06, 0.06, 0.06, 0.96)
                c.arc(mf[0], mf[1], R, 0, 2 * math.pi); c.set_source(g); c.fill()
                c.arc(mf[0], mf[1], R * 0.62, 0, 2 * math.pi); c.set_source_rgba(1, 1, 1, 0.06); c.set_line_width(0.08); c.stroke()
                c.arc(mf[0], mf[1], R, 0, 2 * math.pi); c.set_source_rgba(*BRASA, 0.9); c.set_line_width(0.10); c.stroke()
                c.arc(mf[0], mf[1], 0.35, 0, 2 * math.pi); c.set_source_rgb(*METAL_CLARO); c.fill()
            elif tp == "halter":
                for m, f in ((mt, 0.55), (mf, 1.0)):
                    c.save(); c.translate(*m)
                    for dx in (-0.55, 0.55):
                        c.rectangle(dx - 0.22, -0.75, 0.44, 1.5)
                    c.set_source_rgb(*escurecer((0.20, 0.19, 0.18), f)); c.fill()
                    c.rectangle(-0.55, -0.12, 1.1, 0.24); c.set_source_rgb(*escurecer(METAL, f)); c.fill()
                    c.restore()
            elif tp in ("kettlebell", "bola"):
                m = ((mf[0] + mt[0]) / 2, (mf[1] + mt[1]) / 2 - (0.9 if tp == "kettlebell" else 0))
                r = 0.95 if tp == "kettlebell" else 1.1
                g = cairo.RadialGradient(m[0] - 0.3, m[1] + 0.3, 0, m[0], m[1], r)
                cor = (0.20, 0.19, 0.18) if tp == "kettlebell" else (0.45, 0.18, 0.10)
                g.add_color_stop_rgb(0, *escurecer(cor, 1.8)); g.add_color_stop_rgb(1, *cor)
                c.arc(m[0], m[1], r, 0, 2 * math.pi); c.set_source(g); c.fill()
                if tp == "kettlebell":
                    c.arc(m[0], m[1] + 1.0, 0.45, 0, math.pi); c.set_source_rgb(0.2, 0.19, 0.18); c.set_line_width(0.2); c.stroke()
            elif tp == "corda":
                pf = pts["ponta_f"]
                c.move_to(*mf); c.curve_to(mf[0] + 1, pf[1] - 1, pf[0] + 1, pf[1] - 0.6, mt[0], mt[1])
                c.set_source_rgba(*BRASA, 0.9); c.set_line_width(0.08); c.stroke()


def forma(nome, a, b, frente_para_cima=False, mais=0.0, t1=None):
    perfil = PERFIS[nome]
    if t1 is not None:
        perfil = [x for x in perfil if x[0] <= t1] + [(t1,) + tuple(_largura(perfil, t1))]
    perfil = [(t, wf + mais, wb + mais) for t, wf, wb in perfil]
    fr, tr, n, d = contorno(a, b, perfil, frente_para_cima)
    return fr + list(reversed(tr)), fr, tr


def _largura(perfil, t):
    for (t0, f0, b0), (t1, f1, b1) in zip(perfil, perfil[1:]):
        if t0 <= t <= t1:
            k = (t - t0) / max(t1 - t0, 1e-6)
            return f0 + (f1 - f0) * k, b0 + (b1 - b0) * k
    return perfil[-1][1], perfil[-1][2]


def tecido(c, pts, fr, tr, longe=False):
    f = 0.6 if longe else 1.0
    catmull(c, pts)
    mf, mt = fr[len(fr) // 2], tr[len(tr) // 2]
    g = cairo.LinearGradient(mt[0], mt[1], mf[0], mf[1])
    g.add_color_stop_rgb(0, *escurecer(SHORT, f * 0.7)); g.add_color_stop_rgb(0.7, *escurecer(SHORT_CLARO, f)); g.add_color_stop_rgb(1, *escurecer((0.30, 0.30, 0.32), f))
    c.set_source(g); c.fill()


def desenhar(anim, pose, tam, caixa):
    pts = pontos_anim(anim, pose)
    pt = Pintor(tam, caixa)
    c = pt.ctx
    pt.fundo(pts["quadril"][0])
    dest = set(anim.get("destaque", []))
    desenhar_props(pt, anim, pts, "fundo")
    P = pts

    def silhueta(formas, larg=0.22, alfa=0.85):
        for f in formas:
            catmull(c, f)
            c.set_source_rgba(0.03, 0.02, 0.015, alfa); c.set_line_width(larg); c.stroke_preserve(); c.fill()

    # ---- membros de trás (mais escuros), com silhueta própria
    lado_t = [forma("braco", P["ombro"], P["cotovelo_t"])[0], forma("antebraco", P["cotovelo_t"], P["mao_t"])[0],
              forma("coxa", P["quadril"], P["joelho_t"])[0], forma("canela", P["joelho_t"], P["tornozelo_t"])[0]]
    silhueta(lado_t, 0.16, 0.7)
    pt.segmento("coxa", P["quadril"], P["joelho_t"], longe=True)
    pt.segmento("canela", P["joelho_t"], P["tornozelo_t"], longe=True)
    pt.pe(P["tornozelo_t"], P["ponta_t"], P["calcanhar_t"], longe=True)
    ps, fr, tr = forma("coxa", P["quadril"], P["joelho_t"], mais=0.07, t1=0.42)
    tecido(c, ps, fr, tr, longe=True)
    pt.segmento("braco", P["ombro"], P["cotovelo_t"], longe=True)
    pt.segmento("antebraco", P["cotovelo_t"], P["mao_t"], longe=True)
    pt.mao(P["cotovelo_t"], P["mao_t"], longe=True)

    # ---- corpo principal: silhueta unificada
    frente = [forma("tronco", P["quadril"], P["pescoco"], True)[0], forma("coxa", P["quadril"], P["joelho_f"])[0],
              forma("canela", P["joelho_f"], P["tornozelo_f"])[0], forma("braco", P["ombro"], P["cotovelo_f"])[0],
              forma("antebraco", P["cotovelo_f"], P["mao_f"])[0]]
    silhueta(frente)
    _, _, sp = pt.tronco(P["quadril"], P["pescoco"], dest, None)
    # cintura/short no tronco
    ps, fr, tr = forma("tronco", P["quadril"], P["pescoco"], True, mais=0.06, t1=0.17)
    tecido(c, ps, fr, tr)
    if "gluteo" in dest:
        _, frt, trt = forma("tronco", P["quadril"], P["pescoco"], True)
        g0 = trt[1]; fx, fy = frt[1]
        cx, cy = g0[0] * 0.72 + fx * 0.28, g0[1] * 0.72 + fy * 0.28
        for cc, a in ((pt.ctx, 0.65), (pt.cb, 0.9)):
            gg = cairo.RadialGradient(cx, cy, 0, cx, cy, 1.0)
            gg.add_color_stop_rgba(0, *BRASA_CLARA, a); gg.add_color_stop_rgba(1, *BRASA, 0)
            cc.arc(cx, cy, 1.0, 0, 2 * math.pi); cc.set_source(gg); cc.fill()
    pt.cabeca(P["pescoco"], P["cabeca"], 1)
    pt.segmento("coxa", P["quadril"], P["joelho_f"], destaque="coxa" in dest)
    pt.segmento("canela", P["joelho_f"], P["tornozelo_f"], destaque="perna" in dest)
    pt.pe(P["tornozelo_f"], P["ponta_f"], P["calcanhar_f"])
    ps, fr, tr = forma("coxa", P["quadril"], P["joelho_f"], mais=0.07, t1=0.42)
    tecido(c, ps, fr, tr)
    if "gluteo" in dest:
        catmull(c, ps); c.set_source_rgba(*BRASA, 0.18); c.fill()
    pt.segmento("braco", P["ombro"], P["cotovelo_f"], destaque="braco" in dest)
    pt.deltoide(P["ombro"], P["cotovelo_f"], destaque="ombro" in dest)
    pt.segmento("antebraco", P["cotovelo_f"], P["mao_f"], destaque="antebraco" in dest)
    pt.mao(P["cotovelo_f"], P["mao_f"])
    desenhar_props(pt, anim, pts, "frente")
    return pt.finalizar()


def quadros_loop(anim, fps=10):
    q = anim["quadros"]
    tempos = anim.get("tempos", [1.0] * len(q))
    out = []
    for i in range(len(q)):
        n = max(3, round(tempos[i % len(tempos)] * fps))
        for k in range(n):
            out.append(interpolar(q[i], q[(i + 1) % len(q)], k / n))
    return out


def main():
    args = sys.argv[1:]
    saida = args[args.index("--saida") + 1] if "--saida" in args else "anim_saida"
    tam = int(args[args.index("--tam") + 1]) if "--tam" in args else 288
    sprites = "--sprites" in args
    pos = [a for i, a in enumerate(args) if not a.startswith("--") and (i == 0 or args[i - 1] not in ("--saida", "--tam"))]
    arqs = [a for a in pos if a.endswith(".json")]
    filtro = set(a for a in pos if not a.endswith(".json"))
    os.makedirs(saida, exist_ok=True)
    meta = {}
    for arq in arqs:
        for anim in json.load(open(arq)):
            if filtro and anim["id"] not in filtro:
                continue
            caixa = caixa_anim(anim)
            if sprites:
                fps = 10
                frames = quadros_loop(anim, fps)
                cols = 8
                linhas = math.ceil(len(frames) / cols)
                folha = Image.new("RGB", (cols * tam, linhas * tam), (14, 13, 12))
                for k, p in enumerate(frames):
                    folha.paste(desenhar(anim, p, tam * 2, caixa).resize((tam, tam), Image.LANCZOS), ((k % cols) * tam, (k // cols) * tam))
                folha.save(os.path.join(saida, f"{anim['id']}.webp"), "WEBP", quality=62, method=6)
                meta[anim["id"]] = {"f": len(frames), "c": cols, "s": tam, "fps": fps}
                print(anim["id"], len(frames), "quadros")
            else:
                chaves = [desenhar(anim, completar(p), tam * 2, caixa).resize((tam, tam), Image.LANCZOS) for p in anim["quadros"]]
                folha = Image.new("RGB", (tam * len(chaves), tam))
                for i, cimg in enumerate(chaves):
                    folha.paste(cimg, (i * tam, 0))
                folha.save(os.path.join(saida, f"{anim['id']}.png"))
                frames = [desenhar(anim, p, tam * 2, caixa).resize((tam, tam), Image.LANCZOS) for p in quadros_loop(anim, 10)]
                frames[0].save(os.path.join(saida, f"{anim['id']}.gif"), save_all=True, append_images=frames[1:], duration=100, loop=0)
                print(anim["id"], "ok")
    if sprites:
        with open(os.path.join(saida, "meta.json"), "w") as f:
            json.dump(meta, f, separators=(",", ":"))


if __name__ == "__main__":
    main()
