"""Pré-visualização das animações: gera uma folha com os quadros-chave + quadros intermediários e um GIF.

Uso:
  python3 tools/anim/previa.py tools/anim/dados/lote1.json [slug ...] [--saida pasta]
Imprime avisos de anatomia/formato. As imagens vão para --saida (padrão: pasta 'previas' ao lado do JSON).
"""
import json
import math
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from esqueleto import L, apoios, completar, interpolar, pontos_anim, validar  # noqa: E402

FUNDO = (22, 20, 18)
CHAO = (53, 48, 42)
OSSO = (242, 235, 224)
LONGE = (122, 112, 100)
DESTAQUE = (255, 91, 34)
PROP = (168, 158, 144)
ESC = 18  # px por unidade
W, H = 460, 460


def tela(x, y, ox):
    return (W / 2 + (x - ox) * ESC, H - 50 - y * ESC)


def desenhar(anim, pose, ox=0.0):
    im = Image.new("RGB", (W, H), FUNDO)
    d = ImageDraw.Draw(im)
    pts = pontos_anim(anim, pose)
    T = lambda k: tela(*pts[k], ox)  # noqa: E731
    dest = set(anim.get("destaque", []))
    # chão e sombra
    d.line([(0, H - 50), (W, H - 50)], fill=CHAO, width=2)
    hx = T("quadril")[0]
    d.ellipse((hx - 70, H - 56, hx + 70, H - 44), fill=(30, 28, 25))
    props = anim.get("props", [])
    # acessórios de fundo
    for pr in props:
        tp = pr.get("tipo")
        if tp in ("banco", "maquina", "caixa"):
            x0, y0 = tela(pr.get("x", 0), pr.get("y", 0) + pr.get("h", 4), ox)
            x1, y1 = tela(pr.get("x", 0) + pr.get("w", 8), pr.get("y", 0), ox)
            d.rounded_rectangle((x0, y0, x1, y1), radius=6, outline=PROP, width=3, fill=(40, 36, 32))
        elif tp == "barra_fixa":
            bx, by = tela(pr.get("x", 0), pr.get("y", 21), ox)
            d.line([(bx - 60, by), (bx + 60, by)], fill=PROP, width=5)
            d.ellipse((bx - 6, by - 6, bx + 6, by + 6), fill=PROP)
        elif tp == "saco":
            sx, sy = tela(pr.get("x", 9), 19, ox)
            d.line([(sx, 0), (sx, sy)], fill=PROP, width=2)
            d.rounded_rectangle((sx - 22, sy, sx + 22, sy + 150), radius=16, fill=(60, 54, 48), outline=PROP, width=2)
        elif tp == "esteira":
            d.rounded_rectangle((W / 2 - 170, H - 56, W / 2 + 170, H - 44), radius=6, fill=(45, 41, 36))
        elif tp == "tapete":
            d.rectangle((W / 2 - 190, H - 53, W / 2 + 190, H - 47), fill=(60, 40, 32))
        elif tp == "bike":
            bx, by = tela(pr.get("x", 0), 0, ox)
            for cx in (bx - 70, bx + 80):
                d.ellipse((cx - 38, by - 76, cx + 38, by), outline=PROP, width=3)
            q = T("quadril")
            d.line([q, (bx - 70, by - 38), (bx + 80, by - 38), (q[0] + 70, q[1] - 30)], fill=PROP, width=3)
        elif tp == "rolo":
            rx, ry = tela(pr.get("x", 0), pr.get("y", 0.8), ox)
            d.ellipse((rx - 15, ry - 15, rx + 15, ry + 15), fill=(70, 64, 58), outline=PROP, width=2)

    def seg(a, b, cor, larg):
        d.line([T(a), T(b)], fill=cor, width=larg, joint="curve")
        for k in (a, b):
            x, y = T(k)
            r = larg / 2
            d.ellipse((x - r, y - r, x + r, y + r), fill=cor)

    def cor_seg(nome, base):
        return DESTAQUE if nome in dest else base

    # membros de trás
    seg("ombro", "cotovelo_t", LONGE, 12); seg("cotovelo_t", "mao_t", LONGE, 10)
    seg("quadril", "joelho_t", LONGE, 15); seg("joelho_t", "tornozelo_t", LONGE, 12); seg("calcanhar_t", "ponta_t", LONGE, 9)
    # tronco e cabeça
    seg("quadril", "pescoco", cor_seg("tronco", OSSO), 20)
    if "gluteo" in dest:
        x, y = T("quadril"); d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=DESTAQUE)
    cx, cy = T("cabeca")
    r = L["cabeca"] * ESC
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=OSSO)
    # perna e braço da frente
    seg("quadril", "joelho_f", cor_seg("coxa", OSSO), 16); seg("joelho_f", "tornozelo_f", cor_seg("perna", OSSO), 13); seg("calcanhar_f", "ponta_f", OSSO, 9)
    seg("ombro", "cotovelo_f", cor_seg("braco", OSSO), 13); seg("cotovelo_f", "mao_f", cor_seg("antebraco", OSSO), 11)
    # acessórios na frente
    mf, mt = T("mao_f"), T("mao_t")
    for pr in props:
        tp = pr.get("tipo")
        if tp == "barra":
            d.ellipse((mf[0] - 30, mf[1] - 30, mf[0] + 30, mf[1] + 30), outline=PROP, width=6)
            d.ellipse((mf[0] - 6, mf[1] - 6, mf[0] + 6, mf[1] + 6), fill=PROP)
        elif tp == "halter":
            for m in (mt, mf):
                d.rounded_rectangle((m[0] - 16, m[1] - 9, m[0] + 16, m[1] + 9), radius=4, fill=PROP)
        elif tp in ("kettlebell", "bola"):
            m = ((mf[0] + mt[0]) / 2, (mf[1] + mt[1]) / 2 + (14 if tp == "kettlebell" else 0))
            rr = 16 if tp == "kettlebell" else 20
            d.ellipse((m[0] - rr, m[1] - rr, m[0] + rr, m[1] + rr), fill=PROP)
        elif tp in ("elastico", "cabo"):
            ate = pr.get("ate")
            if ate is None or pr.get("de") == "costas":
                a = T("ombro")  # elástico pelas costas: só indica a ligação com o tronco
            elif ate == "pes":
                a = T("tornozelo_f")
            else:
                a = tela(ate[0], ate[1], ox)
            d.line([mf, a], fill=DESTAQUE if tp == "elastico" else PROP, width=3)
            if tp == "cabo":
                d.ellipse((a[0] - 9, a[1] - 9, a[0] + 9, a[1] + 9), outline=PROP, width=3)
        elif tp == "corda":
            pf = T("ponta_f")
            d.line([mf, (pf[0], pf[1] + 8), mt], fill=PROP, width=2)
    return im


def amostras(anim, n_inter=2):
    q = anim["quadros"]
    out = []
    for i in range(len(q)):
        a, b = q[i], q[(i + 1) % len(q)]
        out.append(("chave", completar(a)))
        for k in range(1, n_inter + 1):
            out.append(("inter", interpolar(a, b, k / (n_inter + 1))))
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    saida = None
    if "--saida" in sys.argv:
        saida = sys.argv[sys.argv.index("--saida") + 1]
        args = [a for a in args if a != saida]
    arq = args[0]
    filtro = set(args[1:])
    dados = json.load(open(arq))
    lista = dados if isinstance(dados, list) else dados.get("animacoes", [])
    saida = saida or os.path.join(os.path.dirname(os.path.abspath(arq)), "previas")
    os.makedirs(saida, exist_ok=True)
    for anim in lista:
        if filtro and anim["id"] not in filtro:
            continue
        av = validar(anim)
        q = anim["quadros"]
        ox = sum(pontos_anim(anim, p)["quadril"][0] for p in q) / max(1, len(q))
        # folha: quadros-chave em cima
        chaves = [desenhar(anim, p, ox) for p in q]
        folha = Image.new("RGB", (W * len(chaves), H), FUNDO)
        for i, c in enumerate(chaves):
            ImageDraw.Draw(c).text((10, 10), f"{anim['id']}  quadro {i}", fill=OSSO)
            folha.paste(c, (i * W, 0))
        folha.save(os.path.join(saida, f"{anim['id']}.png"))
        frames = []
        tempos = anim.get("tempos", [1.0] * len(q))
        for i in range(len(q)):
            n = max(4, int(tempos[i % len(tempos)] * 12))
            for k in range(n):
                frames.append(desenhar(anim, interpolar(q[i], q[(i + 1) % len(q)], k / n), ox).resize((230, 230)))
        frames[0].save(os.path.join(saida, f"{anim['id']}.gif"), save_all=True, append_images=frames[1:], duration=83, loop=0)
        print(f"{anim['id']}: {'OK' if not av else '; '.join(av)}")
        if "--apoios" in sys.argv:
            for i, p in enumerate(q):
                print(f"   quadro {i} apoios: {apoios(anim, p)}")


if __name__ == "__main__":
    main()
