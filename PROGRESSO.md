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
