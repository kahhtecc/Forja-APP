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
5. [ ] UI Compose (onboarding/quiz, plano semanal, sessão com timer, biblioteca, detalhe com vídeo, progresso, ajustes)
6. [ ] Workflow GitHub Actions: build + emulador + capturas + release
7. [ ] Revisar capturas e corrigir
8. [ ] Versão web (artifact) + zip + entrega

## Próximo passo
Etapa 5 (UI Compose). Pedido extra do usuário (feito no núcleo): rotinas de alongamento/mobilidade por esporte — `core/Rotinas.kt` (25 rotinas: antes do esporte, depois do treino, mobilidade). Falta a tela.
Testes: `tests/run.sh` (kotlinc+json.jar no scratchpad; se sumiram, rebaixe: ver etapa no histórico — kotlin 2.1.0 do GitHub + JSON-java javac).

## Aviso de retomada
trigger_id: trig_01JKc5e2kUUn5BKN3KhkNL8M
