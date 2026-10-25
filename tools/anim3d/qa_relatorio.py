"""Relatório legível (Markdown) a partir do JSON do qa.py.

Uso: python tools/anim3d/qa_relatorio.py qa-resultado.json pesquisa/qa-resultado.md
"""
import json
import math
import sys
from collections import Counter, defaultdict

TIPOS = ("pegada", "rom", "apoio", "motor")
NOME_TIPO = {"pegada": "Pegada", "rom": "Amplitude (ROM)", "apoio": "Apoio / interpenetração", "motor": "Motor (pops, skate, chão...)"}


def gravidade(a):
    if a.get("nivel") != "erro":
        return 0.0
    if a["tipo"] == "motor":
        return 2.0
    lim = a.get("limite") or 1.0
    r = min(5.0, max(1.0, float(a["valor"]) / max(float(lim), 1e-6)))
    return r * (1.0 + math.log(max(1, a.get("n_quadros", 1))) / 3)


def resumo_curto(a):
    if a["tipo"] == "motor":
        return a["msg"]
    v = a["valor"]
    u = a.get("unidade", "")
    vs = f"{v:.1f} cm" if u == "cm" else (f"{v:.0f}{u}" if u else f"{v}")
    return f"{a['sub']} {a['parte']} {vs}"


def main(js, md):
    res = json.load(open(js))
    ids = list(res)
    cont_ex = Counter()  # exercícios com erro de cada tipo
    cont_av = Counter()
    cont_sub = Counter()
    por_ex = {}
    for i in ids:
        ach = res[i].get("achados", [])
        er = [a for a in ach if a["nivel"] == "erro"]
        av = [a for a in ach if a["nivel"] == "aviso"]
        for t in TIPOS:
            if any(a["tipo"] == t for a in er):
                cont_ex[t] += 1
            elif any(a["tipo"] == t for a in av):
                cont_av[t] += 1
        for a in er:
            cont_sub[(a["tipo"], a["sub"])] += 1
        por_ex[i] = (er, av, sum(gravidade(a) for a in er))
    ne = sum(1 for i in ids if por_ex[i][0])
    na = sum(1 for i in ids if not por_ex[i][0] and por_ex[i][1])
    L = []
    L.append("# Resultado do QA das animações 3D (pegada, amplitude articular, apoio)\n")
    L.append(f"Gerado por `tools/anim3d/qa.py` + `tools/anim3d/qa_relatorio.py` sobre os {len(ids)} exercícios. "
             "Critérios, limiares e método de validação em `tools/anim3d/qa_corpo.py` e na seção final.\n")
    L.append(f"**{ne} exercícios com erro, {na} só com aviso, {len(ids) - ne - na} limpos.**\n")
    L.append("## Exercícios com defeito, por tipo\n")
    L.append("| Tipo | Exercícios com erro | Só aviso |")
    L.append("|---|---|---|")
    for t in TIPOS:
        L.append(f"| {NOME_TIPO[t]} | {cont_ex[t]} | {cont_av[t]} |")
    L.append("\n## Erros por verificação (nº de exercícios)\n")
    L.append("| Tipo | Verificação | Exercícios |")
    L.append("|---|---|---|")
    for (t, s), c in sorted(cont_sub.items(), key=lambda x: (-x[1], x[0])):
        L.append(f"| {t} | {s} | {c} |")
    L.append("\n## Os piores (gravidade = soma de valor/limite dos erros, pesada pela duração)\n")
    pior = sorted(ids, key=lambda i: -por_ex[i][2])
    L.append("| # | Exercício | Gravidade | Principais erros |")
    L.append("|---|---|---|---|")
    for n_, i in enumerate(pior[:25], 1):
        er = sorted(por_ex[i][0], key=lambda a: -gravidade(a))
        L.append(f"| {n_} | {i} | {por_ex[i][2]:.1f} | " + "; ".join(resumo_curto(a) for a in er[:5]) + " |")
    L.append("\n## Tabela dos exercícios\n")
    L.append("Colunas: nº de verificações com erro (e aviso) por tipo; defeitos = os erros mais graves (verificação, parte, valor).\n")
    L.append("| Exercício | Pegada | ROM | Apoio | Motor | Defeitos |")
    L.append("|---|---|---|---|---|---|")
    for i in ids:
        er, av, g = por_ex[i]
        cel = []
        for t in TIPOS:
            e_ = sum(1 for a in er if a["tipo"] == t)
            a_ = sum(1 for a in av if a["tipo"] == t)
            cel.append((f"**{e_}**" if e_ else "0") + (f" ({a_})" if a_ else ""))
        top = sorted(er, key=lambda a: -gravidade(a))[:4]
        txt = "; ".join(resumo_curto(a) for a in top) if top else ("só avisos" if av else "ok")
        L.append(f"| {i} | " + " | ".join(cel) + f" | {txt} |")
    L.append("")
    open(md, "w").write("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
