# PROGRESSO — App de treino "Forja"

## Pedido original (palavra por palavra)
> Quero que você crie um app de treino, quero um agente trabalhando nas pesquisas para te referenciar, quero tipos variados de treino, tipo, rotina de treino em casa (com peso do corpo ou com elásticos), rotina de treino na academia musculação, rotina de treino de corrida, rotina de treino bike, rotina de treino lutadores, rotina de treino de atletas, e vários outros tipos variados de rotinas de treino. Quero que você monte uma rotina com base uma sequência de perguntar para quem vai treinar, tipo, treina a bastante tempo ou è iniciante, vai treinar quantos dias na semana, se é para ganho de massa, se é para perder peso, se quer só manter uma vida ativa e saudável, e todas outras perguntas que for necessário para montar uma rotina. Cada exercício deve acompanhar vídeos demonstrativos de como executar. Quero um design característico e sofisticado. Use todas as skills que tiver de apps salvas aqui e de fora, uso toda e qualquer habilidade e ferramenta que vai ajudar a tornar o app perfeito para quem quer treinar organizadamente

## Decisões
- Skill `app-android-todas-opcoes`: app Android nativo (Kotlin + Compose), APK compilado no GitHub Actions do repo `kaiqueguimacuper-bit/teste-3`, branch `claude/personalized-workout-app-ou3pc2`. + versão web (artifact) + zip.
- Nome: **Forja**. Tema escuro "grafite quente" + acento brasa; uma cor por modalidade. Fontes: Big Shoulders Display (títulos/números) + Manrope (texto).
- Demonstração: fotos início/fim do free-exercise-db (Unlicense) animadas em loop no app (offline) + vídeo do YouTube (ids verificados pelo agente de pesquisa em `pesquisa/videos.json`; fallback = busca no YouTube).
- Catálogo: `tools/catalog.py` (154 exercícios). Gerador de rotinas em Kotlin puro (`core/`), testado com kotlinc.
- Agente de pesquisa (em segundo plano) escreve em `pesquisa/` (diretrizes.md, parametros.json, videos.json, RESUMO.md).

## Etapas
1. [x] Catálogo de exercícios
2. [x] Pesquisa (agente) — entregue; 2ª rodada pedida: vídeos dos 21 slugs novos (lista-exercicios-novos.tsv + isometria-pescoco, nordico, prova) e seção de preparo por esporte
3. [x] Assets: imagens otimizadas + exercises.json (`tools/build_assets.py`)
4. [x] Núcleo Kotlin puro: modelos, questionário, gerador de rotinas, progresso + testes (kotlinc)
5. [x] UI Compose (onboarding/quiz, plano semanal, sessão com timer, biblioteca, detalhe com vídeo, progresso, ajustes)
6. [x] Workflow GitHub Actions: build + emulador + capturas + release
7. [ ] Revisar capturas e corrigir
8. [~] Versão web: /tmp/claude-0/-home-user-teste-3/400edce2-80ea-57f6-97f9-c6ff24db5c18/scratchpad/web/forja.html (+ dados.json, exercicios.json, img/ 340 arquivos) — testada com Playwright (teste_web.js); falta publicar (Artifact, 2 publishes por causa do limite de 255 arquivos) e zip
9. [ ] PEDIDO NOVO DO USUÁRIO: "depois de terminado quero que você gere uma versão do app otimizada para linhas iOS".
   Plano: pasta ios/ com app SwiftUI nativo (mesmo design), núcleo portado para Swift (Swift Package `ForjaCore`) com testes de paridade contra planos exportados pelo Kotlin (tests/ExportarWeb.kt → JSON dourado); workflow macOS (macos-15) que roda `swift test`, compila para simulador, tira capturas com `xcrun simctl` e gera IPA não assinado (instalar com Sideloadly/AltStore ou Xcode). Também deixar a versão web instalável no iPhone (meta apple-mobile-web-app).

## Próximo passo
Ver capturas do build 1 (Release build-1), corrigir, publicar web, depois iOS (etapa 9).

## (anterior)
Etapa 5 (UI Compose). Pedido extra do usuário (feito no núcleo): rotinas de alongamento/mobilidade por esporte — `core/Rotinas.kt` (25 rotinas: antes do esporte, depois do treino, mobilidade). Falta a tela.
Testes: `tests/run.sh` (kotlinc+json.jar no scratchpad; se sumiram, rebaixe: ver etapa no histórico — kotlin 2.1.0 do GitHub + JSON-java javac).

## Aviso de retomada
trigger_id: trig_01JKc5e2kUUn5BKN3KhkNL8M

## ATUALIZAÇÃO (pedidos novos do usuário, em ordem)
- "adicione rotina de alongamento e mobilidade por esporte" → FEITO no núcleo (Rotinas.kt, 25 rotinas) e nas telas Android/web/iOS.
- "versão otimizada para iOS" → EM ANDAMENTO: ios/ForjaCore (núcleo Swift + testes de paridade com ouro.json), ios/Forja/App (SwiftUI). Falta: QuestionarioView.swift, workflow .github/workflows/ios.yml (macos-15: swift test, xcodegen, build simulador, capturas, IPA não assinado).
- "atualize sem baixar o app de novo" → A FAZER: conteúdo OTA (exercises.json + animações) baixado de raw.githubusercontent (repo público; se ficar privado, usar repo público só de conteúdo). Respondido ao usuário.
- "modifique os vídeos, subagente para animações demonstrativas" + "quero boneco realista, humano com músculos" + imagem de referência (figura 3D clara, músculos trabalhados em vermelho, aparelho, posições inicial/final) →
  * Agentes (3, em segundo plano) escrevem poses em tools/anim/dados/lote{1,2,3}.json (formato em tools/anim/esqueleto.py + campos 3D bfa/afa/pfa/tr; instruções em tools/anim/INSTRUCOES.md). Se a sessão reiniciar, relançar agentes para lotes incompletos.
  * Render 3D: tools/anim3d/humano.py (Blender 5 via `uv` venv em scratchpad/blender-env; MakeHuman CC0 em scratchpad/mh — `git clone --sparse` de makehumancommunity/makehuman, pastas makehuman/data/{3dobjs,rigs,targets/macrodetails}).
  * Falta: regiões musculares em vermelho, aparelhos 3D, enquadramento fixo por animação, quadros intermediários → sprites WebP + meta; players no Android/iOS/web; OTA.

## RETOMADA — LEIA PRIMEIRO
Atualizado em 2026-10-20T01:30Z. Ordem de trabalho a partir daqui:
1. Animações (poses): agentes escrevem tools/anim/dados/lote{1,2,3}.json (lotes em tools/anim/lotes/, instruções em tools/anim/INSTRUCOES.md).
   Ver quantas existem: `for f in tools/anim/dados/lote*.json; do python3 -c "import json;print('$f',len(json.load(open('$f'))))"; done`
   Esperado: lote1=56, lote2=56, lote3=63. Se algum lote estiver incompleto e nenhum agente rodando, relançar agente (general-purpose, em segundo plano) com o mesmo pedido: "leia INSTRUCOES.md e complete o loteN.json, sem refazer o que existe".
2. Render 3D (tools/anim3d/humano.py). Ambiente: `. /tmp/claude-0/-home-user-teste-3/400edce2-80ea-57f6-97f9-c6ff24db5c18/scratchpad/blender-env/bin/activate` (se sumiu: `pip install uv; uv python install 3.11; uv venv -p 3.11 blender-env; uv pip install bpy pillow numpy`). MakeHuman: scratchpad/mh (se sumiu: `git clone --depth 1 --filter=blob:none --sparse https://github.com/makehumancommunity/makehuman.git mh && cd mh && git sparse-checkout set makehuman/data/3dobjs makehuman/data/rigs makehuman/data/targets/macrodetails`).
   Revisão (quadros-chave): `python tools/anim3d/humano.py --mh <mh>/makehuman/data --anim tools/anim/dados/lote1.json --saida <scratch>/r3dk --tam 300 --amostras 16 --chaves --ids a,b`
   Produção (sprites): `python tools/anim3d/humano.py --mh <mh>/makehuman/data --anim tools/anim/dados/lote1.json tools/anim/dados/lote2.json tools/anim/dados/lote3.json --saida app/src/main/assets/anim3d --tam 320 --amostras 18 --fps 6 --pular-existentes` (rodar em segundo plano; pula os já feitos; grava meta.json)
3. Players: Android (ui DemoExercicio → tocar sprite anim3d/<id>.webp quando existir; foto como reserva), iOS (DemoExercicio SwiftUI), web (forja.html). Vídeo do YouTube vira opção secundária.
4. Conteúdo OTA: pasta conteudo/ (manifesto.json com versão + exercises.json + anim3d/*), app baixa de https://raw.githubusercontent.com/kaiqueguimacuper-bit/teste-3/claude/personalized-workout-app-ou3pc2/conteudo/ (endereço configurável).
5. iOS: terminar ios/Forja/App/QuestionarioView.swift + .github/workflows/ios.yml; push; revisar capturas.
6. Build Android (push → Actions), revisar capturas, enviar APK, republicar web, zip, mensagem final.
Aviso de retomada: trigger_id trig_01JKc5e2kUUn5BKN3KhkNL8M (remarcar com update_trigger a cada etapa; desativar no fim).
- 01:35Z: usuário pediu animação MAIS REALISTA anatomicamente, com mais agentes → agente "anatomia" (em segundo plano) é dono de tools/anim3d/ (não editar humano.py enquanto ele roda); resultado esperado em scratchpad/anat_final.jpg. Se a sessão reiniciar e não houver anat_final.jpg, relançar agente com o mesmo objetivo.
- Android: player de sprites 3D (ui/Animacao3D.kt) e conteúdo OTA (Conteudo.kt + tools/build_conteudo.py → assets/conteudo_manifesto.json) já escritos, ainda não compilados.
- 09:50Z: limite reiniciou; agentes retomados via SendMessage (lote1 a236432951802106c, lote2 a6e4daf89e01a1a37, lote3 abd53196b12fa9885, anatomia a5b86ee36c3612ce0). iOS: QuestionarioView, Animacao3D.swift, Conteudo.swift, workflow ios.yml escritos e enviados (commit 28df4d7) → conferir Actions (Android build 2 + iOS 1) e corrigir erros. Falta: render dos sprites, player web, entrega final.
- 10:20Z: lotes 1–3 completos (175 poses, commitados). Anatomia concluída (humano.py + anatomia.py; comparação scratchpad/anat_final.jpg). Android build 7 OK (só falhas do roteiro de teste, corrigidas). iOS 1 compilou; release deu 403 → workflow agora salva artefato + tenta de novo.
- RENDER EM ANDAMENTO: scratchpad/render.sh (2 processos, ids em scratchpad/ids{0,1}.txt) → scratchpad/sprites/w{0,1}/ (webp + meta.json; logs log{0,1}.txt). Se a sessão reiniciar: rodar render.sh de novo (pula os já feitos). Ao terminar: copiar webps para app/src/main/assets/anim3d/, mesclar os dois meta.json em anim3d/meta.json, rodar tools/build_conteudo.py, commit/push; copiar anim3d/ para scratchpad/web/anim3d e republicar o artifact web.
- 10:35Z NOVO PEDIDO DO USUÁRIO: "Ao final de tudo, quero que você de alguma forma garanta a passagem na verificação de app do Google, e arrume uma forma de instalação pra IOS".
  Feito: API 36 (AGP 8.10.1), applicationId com.kaiquecupertino.forja (iOS idem), assinatura via secrets FORJA_KEYSTORE_BASE64/FORJA_KEYSTORE_SENHA/FORJA_CHAVE_ALIAS(forja)/FORJA_CHAVE_SENHA; chave gerada em entregas/chave/ (forja-upload.jks, senha.txt, base64) — ENTREGAR AO USUÁRIO (gitignored, some se o container morrer! SHA-256 35:99:90:E6:...:19:41). AAB -Pplay sem auto-update de APK. web/ = PWA (index, sw.js, manifest, instalar.html, privacidade.html) publicado por .github/workflows/pages.yml.
  Falta: confirmar Pages ativo (pode precisar o usuário ativar Settings › Pages › GitHub Actions), link de privacidade dentro do app, guia PUBLICAR-NA-PLAY.md (conta dev, verificação de identidade, registro pacote+SHA-256, teste fechado 12 testadores/14 dias, ficha da loja, segurança de dados, declaração de app de saúde, classificação), textos da ficha + gráficos (ícone 512, feature 1024x500, capturas), iOS: workflow TestFlight opcional com secrets.
- Render: movido para GitHub Actions (.github/workflows/anim3d.yml, 16 partes; gatilho: mudar tools/anim3d/RENDER ou workflow_dispatch). O job "juntar" commita os sprites no branch → depois `git pull`. Render local (scratchpad/render.sh) é só reserva.
- 14:45Z: render no Actions concluído (175 animações, 7 MB, commit fb7c295 do bot). Amostra revisada ok. Gráfico de destaque da loja feito (docs/loja/destaque-1024x500.png). Próximo: builds Android/iOS/Pages com as animações; capturas da loja (1080x2160); revisar capturas iOS (correção do corte lateral); republicar artifact web; enviar APK + chave + guia ao usuário; desativar trigger.
- 14:55Z: web artifact republicado com as 175 animações (fotos _0 removidas pelo limite de 511 arquivos). Push "corpo inteiro" disparou Android/iOS/Pages. Pages NÃO está ativado no repo (usuário precisa: Settings › Pages › Deploy from branch › gh-pages / root). Falta: conferir builds, capturas de loja 1080x2160, enviar APK + chave + guia, mensagem final, desativar triggers.
- 15:40Z PEDIDO NOVO: "Quero que atualize a versão atual e melhore a qualidade do vídeo das animações em 3D, e quero a versão para iOS".
  Feito: humano.py --video (MP4 H.264 480px 15fps crf20 + pôster webp); render no Actions run 3 (20 partes) → app/src/main/assets/video3d/ (+ tools/build_conteudo.py gera conteudo2.json; conteudo_manifesto.json antigo congelado p/ build ≤16). Players: Android ExoPlayer (media3 1.5.1, Animacao3D.kt), iOS AVPlayerLooper (Animacao3D.swift), web <video>. anim3d/ (folhas) removido. Commit 14846ad.
  Falta: conferir compilação Android/iOS do 14846ad; quando render terminar (bot commita video3d), git pull, push p/ disparar builds (Android/iOS/Pages); enviar APK novo (o v16 instalado mostra aviso de versão nova) + IPA + instruções iOS; web artifact: trocar anim3d por video3d (remover anim3d/* e img/*_1 exceto agachamento-barra, swing, corrida-leve).
- 17:10Z: vídeos 3D prontos (175, 12 MB, commit e0703c6 via workflow juntar-video3d). Web artifact republicado com vídeos. Android 18 compilou o player (sem vídeos); disparados Android/iOS/Pages com vídeos (workflow_dispatch). Falta: conferir builds, enviar APK (v16 instalado recebe aviso) + IPA + instruções iOS.
