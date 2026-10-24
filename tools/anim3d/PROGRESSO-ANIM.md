# Progresso: animações 3D profissionais (ANIMADOR)

Referência: `pesquisa/animacao-3d-profissional.md`. Scratch: `<scratchpad>/an/` (base = antes, folhas de contato).

## Etapas
- [x] 1. Motor: curvas (tangentes, easing, amostragem uniforme, atraso, vida, slerp dos braços, balística)
- [x] 2. Motor: pops (barra_modo, plantar, livre contínuo, dedos dos pés, apoio explícito)
- [x] 3. Motor: câmera por família, chão com marcas, piso rolante, motion blur/30 fps, pontilhado fixo, encode
- [x] 4. Aparelhos: alavancas rígidas, kettlebell em pêndulo, enquadramento sem torres
- [x] 5. qa.py criado (também no CI, só avisa); rodadas completas: <scratch>/an/tools/qa_all.sh <tag>
- [x] 6. Dados (rodadas 1 e 2, ver commits): face-pull, monster-walk, supino-maquina, salto-distancia e famílias
- [x] 7. Revisão visual dos 175 (rodadas 1 e 2 completas com folhas de contato)
- [ ] 8. Render de produção no CI + conferência

## Notas
- IK refinado (ossos intermediários não colineares davam até 6 cm de erro: era a causa de pés/mãos escorregando).
- FK preguiçosa (só recalcula a cadeia que mudou): QA ~10 s/exercício.
- Âncora única por apoio contínuo (antepé/pegada fixos), assentar_apoios por quadro, polo do joelho/cotovelo contínuo.
- Ângulos sem desenrolar (como a prévia 2D): braço de -45 a 150 passa pela frente.
- Dados já corrigidos: face-pull, monster-walk, supino-maquina (cam), crucifixo, peck-deck, alongamento-triceps, salto-distancia (volta andando).
- Dados: um exercício por linha (tools/anim/dados/*.json); helper em <scratch>/an/tools/dados.py.
- Desfoque: 4 subquadros pré-multiplicados (2 subquadros davam "fantasma" e chuvisco).
- QA motor antigo (bea8da2): 81 erros, 44 avisos, 50 limpos (233 skate, 88 pop, 59 flutua, 28 barra, 26 congelado, 24 chão, 19 idênticas, 8 rosto).
- plantar re-chamado (alcançar/sem_atravessar) acumulava o peso 1-(1-w)^n: agora mistura da pose livre guardada (box-jump 4,6 cm resolvido).
- Pendências conhecidas: inchworm (mãos andam num passo longo por trecho; skate 3,4 mm/quadro).
