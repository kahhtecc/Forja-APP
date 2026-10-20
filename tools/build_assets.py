"""Gera os assets do app a partir do catálogo.

Uso: python3 tools/build_assets.py <pasta com as fotos do free-exercise-db (Id_0.jpg, Id_1.jpg)>
- app/src/main/assets/exercises.json  (catálogo + vídeos de pesquisa/videos.json)
- app/src/main/assets/img/<slug>_0.webp / _1.webp  (fotos em duotone, 560 px)
"""
import json
import os
import sys

from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from catalog import E  # noqa: E402
from patterns import PADROES, EVITAR  # noqa: E402

SHADOW = (20, 17, 14)
LIGHT = (239, 230, 216)


def duotone(path, out):
    im = Image.open(path).convert("L")
    w = 560
    im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    im = ImageOps.autocontrast(im, cutoff=1)
    im = ImageOps.colorize(im, SHADOW, LIGHT)
    im.save(out, "WEBP", quality=70, method=6)


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else None
    videos_path = os.path.join(ROOT, "pesquisa", "videos.json")
    videos = json.load(open(videos_path)) if os.path.exists(videos_path) else {}
    out_img = os.path.join(ROOT, "app/src/main/assets/img")
    os.makedirs(out_img, exist_ok=True)
    data = []
    for e in E:
        d = {k: e[k] for k in ("id", "nome", "equip", "grupo", "tipo", "nivel", "dicas", "busca")}
        d["padroes"] = PADROES.get(e["id"], [])
        d["evitar"] = EVITAR.get(e["id"], [])
        d["img"] = bool(e["fdb"])
        v = videos.get(e["id"])
        if v and v.get("id") and len(v["id"]) == 11:
            d["video"] = {"id": v["id"], "titulo": v.get("titulo", ""), "canal": v.get("canal", ""),
                          "idioma": v.get("idioma", "")}
        data.append(d)
        if src and e["fdb"]:
            for i in (0, 1):
                p = os.path.join(src, f"{e['fdb']}_{i}.jpg")
                o = os.path.join(out_img, f"{e['id']}_{i}.webp")
                if not os.path.exists(o) or os.path.getmtime(o) < os.path.getmtime(p):
                    duotone(p, o)
    missing = [e["id"] for e in E if e["id"] not in PADROES]
    if missing:
        sys.exit(f"Exercícios sem padrão de movimento: {missing}")
    with open(os.path.join(ROOT, "app/src/main/assets/exercises.json"), "w") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print(f"{len(data)} exercícios, {sum(1 for d in data if 'video' in d)} com vídeo")


if __name__ == "__main__":
    main()
