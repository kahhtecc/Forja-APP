"""Gera app/src/main/assets/conteudo2.json (versão + SHA-1 de cada arquivo atualizável).

Rode depois de mudar exercícios/vídeos e faça push: os apps instalados baixam o que mudou
(ver Conteudo.kt / Conteudo.swift). A versão só sobe quando algum arquivo mudou.

conteudo_manifesto.json é o manifesto antigo (animações em folha de quadros, até o build 16): fica congelado
para esses apps não baixarem vídeos que não sabem tocar. Eles recebem o aviso de versão nova do app.
"""
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "app", "src", "main", "assets")
SAIDA = os.path.join(ASSETS, "conteudo2.json")


def sha1(p):
    return hashlib.sha1(open(p, "rb").read()).hexdigest()


def main():
    arquivos = {}
    for rel in ("exercises.json", "fontes.json"):
        if os.path.exists(os.path.join(ASSETS, rel)):
            arquivos[rel] = sha1(os.path.join(ASSETS, rel))
    pasta = os.path.join(ASSETS, "video3d")
    if os.path.isdir(pasta):
        for f in sorted(os.listdir(pasta)):
            if f.endswith((".mp4", ".webp", ".json")):
                arquivos[f"video3d/{f}"] = sha1(os.path.join(pasta, f))
    anterior = json.load(open(SAIDA)) if os.path.exists(SAIDA) else {"versao": 0, "arquivos": {}}
    versao = anterior["versao"] + (1 if anterior.get("arquivos") != arquivos else 0)
    json.dump({"versao": versao, "arquivos": arquivos}, open(SAIDA, "w"), indent=0, sort_keys=True)
    print(f"versão {versao} · {len(arquivos)} arquivos")


if __name__ == "__main__":
    main()
