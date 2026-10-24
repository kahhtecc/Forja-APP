# Como criar as animações demonstrativas do Forja

Você vai escrever poses-chave de um boneco articulado (vista lateral, olhando para a DIREITA) para cada exercício do seu lote. O app interpola as poses em loop suave. O objetivo: qualquer pessoa entender o movimento só olhando.

## Arquivos
- Formato completo, ângulos e acessórios: `tools/anim/esqueleto.py` (leia o docstring no topo).
- Exemplos prontos e conferidos: `tools/anim/dados/exemplos.json` (agachamento-livre, flexao, rosca-direta).
- Seu lote: `tools/anim/lotes/loteN.txt` (slug | nome | grupo | equipamentos | dicas de execução).
- Escreva TODAS as animações do lote em `tools/anim/dados/loteN.json` (lista JSON). Salve a cada ~10 exercícios.

## Pré-visualizar (obrigatório)
    python3 tools/anim/previa.py tools/anim/dados/loteN.json [slug ...] --apoios --saida <pasta-scratch>
Gera `<slug>.png` (quadros-chave lado a lado) e `<slug>.gif`, imprime avisos de anatomia e a altura (y) dos pontos de contato.
OLHE as imagens PNG (ferramenta Read) de cada exercício e corrija até ficar convincente. Monte folhas de várias imagens com PIL para revisar mais rápido.

## Regras de qualidade
1. Ângulos absolutos: 0 = para baixo, 90 = para frente (direita), 180 = para cima, -90 = para trás.
2. Pés que devem estar no chão TÊM que estar no chão (y≈0 em `--apoios`), mãos apoiadas idem. O corpo é apoiado automaticamente pelo ponto mais baixo; ajuste os ângulos para que os OUTROS apoios também toquem o chão (trigonometria simples com os comprimentos do esqueleto).
3. Exercícios em pé/apoiados nos pés: use `"fixo": "pes"`. Apoiados nas mãos (flexão, prancha alta, mountain climber, pendurado na barra): `"fixo": "maos"`.
4. Movimento com amplitude correta e técnica segura (coluna neutra, joelho na linha do pé, etc.), coerente com as dicas de execução.
5. `destaque`: segmentos dos músculos-alvo (tronco, braco, antebraco, coxa, perna, gluteo).
6. Acessórios coerentes com o equipamento (barra, halter, kettlebell, banco, barra_fixa, elastico, cabo, bola, bike, esteira, saco, corda, tapete, rolo, maquina). Máquina: use "maquina"/"banco" como bloco + "cabo" quando houver polia.
7. Tempos realistas: descida controlada (1.2–2 s), subida 0.8–1.2 s; isometrias (prancha) com 2 quadros quase iguais (respiração sutil); cardio contínuo (corrida, bike, polichinelo) ciclos de 0.3–0.6 s por quadro; alongamentos: entrar e segurar.
8. Use 2 a 6 quadros. `tempos` tem o MESMO número de itens que `quadros` (o último é a volta ao primeiro). Para movimentos alternados (passada, escalador, corrida), use 4 quadros trocando os lados.
9. Membros "f" (frente, perto da câmera) e "t" (trás). Em movimentos simétricos, deixe os dois parecidos mas não idênticos (desloque 3–5° o de trás) para dar profundidade.
10. Para exercícios deitados (supino, ponte, abdominal), o tronco fica perto de 90/-90; use banco quando houver.

Não altere outros arquivos além do seu `loteN.json` e das suas prévias. Ao terminar, responda só: quantas animações, quantas sem aviso, e os slugs que você acha que ficaram fracos.

## Boneco 3D (atualização)
As poses agora vestem um **humano 3D realista** (renderizado no Blender, câmera em 3/4). Além dos campos do esqueleto, cada pose aceita campos 3D opcionais:
- `"bfa"`/`"bta"`: abdução do braço da frente/trás em graus (0 = plano lateral como antes; 90 = braço aberto para o lado). Direção final = cos(abd)·(direção sagital) + sin(abd)·(para fora do corpo).
- `"afa"`/`"ata"`: abdução do antebraço (padrão = mesmo valor do braço).
- `"pfa"`/`"pta"`: abdução da perna.
- `"tr"`: torção do tronco em graus.
Exemplos: elevação lateral = `bf [0,0]` com `bfa` 0 → 85; crucifixo/voador = `bf [90,90]` com `bfa` 85 (aberto) → 10 (fechado); face pull/abertura com elástico = braços à frente (90) e `bfa` 0 → 70; abdutora/caminhada lateral = `pfa` ~5 → 30; polichinelo = `bfa` 10 → 160 e `pfa` 5 → 25; giro russo/rotacionais = `tr` -35 → 35.
A prévia 2D ignora esses campos — tudo bem. Use-os sempre que o movimento não for só "para frente e para trás".

## Boneco 3D: campos profissionais (2026-10)
Veja o docstring de `tools/anim3d/humano.py` (lista completa). Regras novas:
1. **Nunca dois quadros idênticos.** Pausas e isometrias ganham "vida" automática, mas mude ao menos 0,5–1° em `t` ou `c`.
2. Cadência por família (excêntrica mais lenta que a concêntrica); use `"ease"` quando o padrão automático não servir.
3. `"apoio"` por quadro quando a detecção errar (mãos atrás da cabeça no abdominal NÃO são apoio; flexões: as quatro).
4. Pés/mãos no banco ou na caixa: deixe `y` de fora (o motor apoia no topo da superfície; antepé na borda do degrau vale).
5. Ângulos seguem os valores escritos (sem "atalho" de 360°): braço de -45 a 150 passa pela frente; para passar por cima
   escreva -94 → -262. Nunca deixe um membro atravessar o chão no caminho.
6. Câmera pelo plano do movimento (`cam`, `cam_el`); rosto e mãos sempre visíveis. Rode `tools/anim3d/qa.py` antes do render.
