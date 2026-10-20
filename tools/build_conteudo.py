"""Gera app/src/main/assets/conteudo_manifesto.json (versão + SHA-1 de cada arquivo atualizável).

Rode depois de mudar exercícios/animações e faça push: os apps instalados baixam o que mudou
(ver app/src/main/java/com/forja/app/Conteudo.kt). A versão só sobe quando algum arquivo mudou.
"""
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "app", "src", "main", "assets")
SAIDA = os.path.join(ASSETS, "conteudo_manifesto.json")


def sha1(p):
    return hashlib.sha1(open(p, "rb").read()).hexdigest()


def main():
    arquivos = {}
    for rel in ("exercises.json", "fontes.json"):
        if os.path.exists(os.path.join(ASSETS, rel)):
            arquivos[rel] = sha1(os.path.join(ASSETS, rel))
    pasta = os.path.join(ASSETS, "anim3d")
    if os.path.isdir(pasta):
        for f in sorted(os.listdir(pasta)):
            if f.endswith((".webp", ".json")):
                arquivos[f"anim3d/{f}"] = sha1(os.path.join(pasta, f))
    anterior = json.load(open(SAIDA)) if os.path.exists(SAIDA) else {"versao": 0, "arquivos": {}}
    versao = anterior["versao"] + (1 if anterior.get("arquivos") != arquivos else 0)
    json.dump({"versao": versao, "arquivos": arquivos}, open(SAIDA, "w"), indent=0, sort_keys=True)
    print(f"versão {versao} · {len(arquivos)} arquivos")


if __name__ == "__main__":
    main()
