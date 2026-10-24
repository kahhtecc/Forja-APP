# Progresso: animações 3D profissionais (ANIMADOR)

Referência: `pesquisa/animacao-3d-profissional.md`. Scratch: `<scratchpad>/an/` (base = antes, folhas de contato).

## Etapas
- [x] 1. Motor: curvas (tangentes, easing, amostragem uniforme, atraso, vida, slerp dos braços, balística)
- [x] 2. Motor: pops (barra_modo, plantar, livre contínuo, dedos dos pés, apoio explícito)
- [x] 3. Motor: câmera por família, chão com marcas, piso rolante, motion blur/30 fps, pontilhado fixo, encode
- [x] 4. Aparelhos: alavancas rígidas, kettlebell em pêndulo, enquadramento sem torres
- [~] 5. qa.py criado; rodada nos 175 em andamento
- [ ] 6. Dados: face-pull, monster-walk, supino-maquina, salto-distancia e famílias
- [ ] 7. Revisão visual dos 175
- [ ] 8. Render de produção no CI + conferência

## Notas
- IK refinado (ossos intermediários não colineares davam até 6 cm de erro: era a causa de pés/mãos escorregando).
- FK preguiçosa (só recalcula a cadeia que mudou): QA ~10 s/exercício.
- Âncora única por apoio contínuo (antepé/pegada fixos), assentar_apoios por quadro, polo do joelho/cotovelo contínuo.
- Ângulos sem desenrolar (como a prévia 2D): braço de -45 a 150 passa pela frente.
- Dados já corrigidos: face-pull, monster-walk, supino-maquina (cam), crucifixo, peck-deck, alongamento-triceps, salto-distancia (volta andando).
- Dados: um exercício por linha (tools/anim/dados/*.json); helper em <scratch>/an/tools/dados.py.
