# Forja — Diretrizes de prescrição baseadas em evidência

> Documento de referência para o gerador de rotinas do app. Em PT-BR.
> Cada afirmação traz a fonte entre colchetes `[id]`; a lista completa (autor, ano, link) está no fim, e os mesmos ids existem em `parametros.json → fontes`.
>
> **Grau de confiança.** Onde o número vem de diretriz/consenso ou meta-análise, está indicado. Onde é **prática corrente de treinadores** (sem número fixado por estudo), está marcado como *(convenção)* — o app pode usar, mas não deve apresentar como "comprovado".
>
> **Limitação desta pesquisa:** a ferramenta de leitura de páginas estava bloqueada no ambiente; os números foram conferidos pelos resumos/abstracts retornados nas buscas e por referências clássicas conhecidas (livros-texto NSCA, Allen & Coggan). Itens que não foi possível conferir no texto integral estão sinalizados.

---

## 0. Princípios gerais (aplicam-se a todas as modalidades)

- **O maior ganho vem de sair do zero.** A atualização de 2026 do posicionamento do ACSM sobre treino resistido (primeira desde 2009) enfatiza que treinar todos os grandes grupos musculares **pelo menos 2x/semana** importa mais do que buscar o plano "perfeito" [acsm2026].
- **Sobrecarga progressiva** e especificidade: aumentar carga quando o praticante supera em 1–2 repetições a faixa-alvo; incremento de **2–10%** da carga [acsm2009].
- **Frequência por nível (ACSM 2009):** iniciante 2–3 dias/sem; intermediário 3–4; avançado 4–5 [acsm2009].
- **Autorregulação por RIR/RPE:** a escala de RPE baseada em "repetições em reserva" (RIR) é válida para estimar intensidade; RPE 10 = falha (0 RIR), RPE 9 = 1 RIR, RPE 8 = 2 RIR etc. [zourdos2016; helms2016]. Iniciantes tendem a errar mais a estimativa de RIR do que treinados [zourdos2016] → no app, para iniciantes usar RIR 2–3 (margem de segurança).

---

## 1. Musculação

### 1.1 Variáveis por objetivo (referência NSCA + ACSM)

| Objetivo | Carga | Reps | Séries/exercício | Descanso | Fonte |
|---|---|---|---|---|---|
| Força máxima | ≥85% 1RM | ≤6 | 2–6 | 2–5 min | [nsca2016] |
| Potência (esforço único / múltiplo) | 80–90% / 75–85% 1RM | 1–2 / 3–5 | 3–5 | 2–5 min | [nsca2016] |
| Hipertrofia | 67–85% 1RM | 6–12 | 3–6 | 30–90 s | [nsca2016] |
| Resistência muscular | ≤67% 1RM | ≥12 | 2–3 | ≤30 s | [nsca2016] |

- **ACSM 2009:** iniciantes 8–12 RM; intermediários/avançados 1–12 RM periodizado, com ênfase em cargas pesadas (1–6 RM) e descanso de 3–5 min para força [acsm2009].
- **Nuance moderna (hipertrofia):** ganhos de massa ocorrem numa faixa ampla de cargas (≈30–85% 1RM) desde que as séries sejam levadas perto da falha; força máxima continua favorecida por cargas altas [schoenfeld2021]. Por isso o app pode usar 6–15 reps (ou até 20–30 em casa/elástico) para hipertrofia, desde que o RIR seja baixo.
- **Descanso para hipertrofia:** em treinados, 3 min entre séries produziu mais força e hipertrofia que 1 min (volume-equalizado não) [schoenfeld2016rest] → para exercícios compostos pesados preferir 2–3 min; 60–90 s em isoladores/máquinas *(convenção alinhada à NSCA)*.
- **Proximidade da falha:** hipertrofia melhora à medida que as séries se aproximam da falha; força parece pouco sensível a isso [robinson2024]. Recomendação prática: hipertrofia RIR 0–3; força RIR 1–3 em compostos (evitar falha em agachamento/terra).

### 1.2 Volume semanal por grupo muscular

- **Dose-resposta (Schoenfeld 2017):** cada série semanal adicional associou-se a +0,37% de ganho; ≥10 séries/semana tenderam a superar <5 e 5–9 (tendência, P=0,074) [schoenfeld2017].
- **ACSM 2026 (cobertura secundária):** mínimo de ~**10 séries/grupo/semana** para otimizar hipertrofia, com possível dose-resposta acima disso [acsm2026].
- **Faixas para o app** *(derivadas das fontes acima; os limites superiores são convenção)*:
  - Iniciante: 6–10 séries/grupo/semana (ganhos grandes com pouco volume).
  - Intermediário: 10–16.
  - Avançado: 12–20 (aumentar gradualmente; mais volume ≠ sempre melhor).
  - Saúde/manutenção: 1–3 séries por exercício, 8–10 exercícios para grandes grupos, 2x/semana ≈ 4–6 séries/grupo/semana [garber2011; bull2020].

### 1.3 Frequência por grupo

- Com volume equalizado, a frequência **não** altera significativamente a hipertrofia; com volume não equalizado, maior frequência favorece (porque soma mais séries) [schoenfeld2019].
- Recomendação: cada grupo **≥2x/semana** [acsm2026; schoenfeld2019]; distribuir o volume para não passar de ~8–10 séries "duras" por grupo numa mesma sessão *(convenção)*.

### 1.4 Divisões por dias/semana *(convenção, coerente com ≥2x/grupo)*

| Dias | Divisão sugerida |
|---|---|
| 2 | Full body A / B |
| 3 | Full body A/B/A (iniciante) ou Full body ×3 com ênfases (intermediário) |
| 4 | Upper / Lower ×2 |
| 5 | Upper / Lower / Push / Pull / Legs (ou Upper/Lower + Full body) |
| 6 | Push / Pull / Legs ×2 (intermediário/avançado) |

### 1.5 Progressão

- **Dupla progressão:** manter a carga até completar o topo da faixa de reps em todas as séries com o RIR-alvo; então subir a carga (2–10%) e voltar ao piso da faixa [acsm2009].
- **Periodização:** planos periodizados têm efeito moderado sobre 1RM vs não periodizados, maior em não treinados [williams2017]; com volume igual, o modelo (linear vs ondulatório) importa pouco.
- **Deload:** consenso Delphi define deload como período de redução do estresse de treino para gerir fadiga e melhorar prontidão [bell2023]. Em levantamento com 246 atletas de força/físico, o deload típico durou **6,4 ± 1,7 dias**, a cada **5,6 ± 2,3 semanas**, geralmente reduzindo volume e mantendo frequência [rogerson2024]. App: deload a cada 4–8 semanas (iniciantes podem dispensar), cortando ~40–50% das séries e mantendo carga moderada *(convenção)*.

---

## 2. Emagrecimento (perda de gordura)

- **Atividade aeróbica:** 150–250 min/sem de atividade moderada previne ganho de peso; **>250 min/sem** associa-se a perda de peso clinicamente significativa e pode ser necessário para evitar reganho [donnelly2009].
- **OMS 2020:** adultos 150–300 min/sem moderado **ou** 75–150 min vigoroso (ou combinação) + fortalecimento muscular ≥2 dias/sem [bull2020].
- **Força:** manter treino resistido ≥2x/sem (preserva massa magra durante déficit) [bull2020; acsm2026].
- **HIIT vs contínuo:** reduções semelhantes de gordura corporal; HIIT exigiu ~40% menos tempo [wewege2017]. Use HIIT como opção para quem tem pouco tempo, não como superior.
- Parâmetros sugeridos de força: 2–4 séries, 8–15 reps, RIR 1–3, descanso 60–90 s (circuitos permitidos) *(convenção, dentro das faixas NSCA de hipertrofia/resistência)*.

---

## 3. Saúde / vida ativa e 50+

- **Adultos (OMS 2020):** 150–300 min moderado ou 75–150 min vigoroso/sem; fortalecimento de intensidade moderada ou maior, todos os grandes grupos, ≥2 dias/sem; reduzir tempo sentado [bull2020].
- **Idosos (≥65, OMS 2020):** as mesmas metas + **atividade multicomponente** com ênfase em **equilíbrio funcional e força**, intensidade moderada ou maior, **≥3 dias/sem**, para prevenir quedas [bull2020].
- **Quedas:** exercício reduz a taxa de quedas em **23%**; programas de equilíbrio/funcionais em **24%**; múltiplos tipos combinados provavelmente **34%**; Tai Chi pode reduzir 19% [sherrington2019].
- **Força em idosos (NSCA 2019):** 2–3x/sem, 1–3 séries por exercício, 8–12 reps a 70–85% 1RM (iniciar mais leve e progredir), incluir exercícios de potência (fase concêntrica rápida) e equilíbrio [fragala2019].
- **ACSM 2009 idosos:** combinar aeróbio, fortalecimento, flexibilidade e equilíbrio [chodzkozajko2009].
- **Flexibilidade/neuromotor (adultos):** neuromotor 2–3 dias/sem, 20–30 min [garber2011].

---

## 4. Corrida

### 4.1 Distribuição de intensidade e zonas

- Atletas de endurance competitivos convergem para ~**80% das sessões em baixa intensidade** (≈2 mM de lactato) e ~20% em alta [seiler2010]. É descrição de atletas treinando 10–13x/sem, não regra rígida para amadores — mas a recomendação prática "a maior parte do volume leve" é amplamente usada.
- **Teste da fala:** conseguir falar confortavelmente indica intensidade abaixo do limiar ventilatório/lactato; não conseguir indica acima [reedpipe2014].
- **Zonas por percepção (para o app)** — combinação de teste da fala + RPE 0–10 *(mapeamento por convenção, ancorado em [seiler2010; reedpipe2014])*:

| Zona | Nome | Teste da fala | RPE (0–10) | Uso |
|---|---|---|---|---|
| Z1 | Muito leve / recuperação | Conversa fácil | 2–3 | Aquecimento, regenerativo |
| Z2 | Leve / aeróbio | Frases completas | 3–4 | Rodagem, longão (base do 80%) |
| Z3 | Moderado / limiar (tempo run) | Frases curtas | 5–7 | Tempo run, ritmo de prova longa |
| Z4 | Forte / VO2 | Poucas palavras | 8–9 | Tiros 2–5 min |
| Z5 | Máximo | Não fala | 9–10 | Tiros curtos/sprints |

### 4.2 Progressão de volume

- A "regra dos 10%" **não** preveniu lesões em ensaio randomizado com 532 iniciantes (20,8% vs 20,3%) [buist2008].
- Em coorte com 874 iniciantes, aumentar >30% a distância semanal em 2 semanas mostrou tendência a mais lesões por distância (HR 1,59; P=0,07) [nielsen2014].
- App: aumentar volume semanal de forma gradual (≤10–20%/sem é conservador), com 1 semana mais leve a cada 3–4 *(convenção)*.

### 4.3 Iniciante: caminhada → corrida (estilo Couch to 5K)

- NHS Couch to 5K: **3 sessões/semana, 9 semanas**, dia de descanso entre corridas; semana 1 = caminhada 5 min de aquecimento + alternar **60 s correndo / 90 s caminhando** por 20 min + 5 min de desaquecimento; meta final: **30 min de corrida contínua** [nhsc25k].

### 4.4 Estrutura de planos por distância *(convenção de treinadores; não há estudo que fixe semanas)*

| Distância | Iniciante | Intermediário | Avançado | Longão (pico) | Sessões de qualidade |
|---|---|---|---|---|---|
| 5k | 8–9 sem (C25K) 3x/sem | 6–8 sem 3–4x | 6–8 sem 4–6x | 6–10 km | 1–2 (tiros 400 m–1 km, tempo) |
| 10k | 8–10 sem 3x | 8–10 sem 4x | 8–10 sem 5–6x | 10–16 km | 1–2 |
| 21k | 12 sem 3–4x | 12 sem 4–5x | 12–14 sem 5–6x | 16–20 km | 1–2 (tempo, ritmo de prova) |
| 42k | 16–20 sem 4x | 16–18 sem 4–5x | 16–18 sem 5–6x | 30–35 km | 1–2 (ritmo de maratona, tempo) |

- Pré-requisitos sugeridos: 21k → conseguir correr ~10 km; 42k → base de ~30 km/sem e já ter feito 21k *(convenção)*.
- **Polimento (taper):** redução de **41–60% do volume**, mantendo intensidade, por **8–14 dias**, gerou o maior efeito sobre desempenho (meta-análise com corredores, nadadores, ciclistas) [bosquet2007]. Maratona: comum usar 2–3 semanas *(convenção)*.

---

## 5. Ciclismo

### 5.1 Zonas de potência de Coggan (% FTP) [allencoggan2019]

| Nível | Nome | % FTP |
|---|---|---|
| 1 | Recuperação ativa | < 55% |
| 2 | Endurance | 56–75% |
| 3 | Tempo | 76–90% |
| 4 | Limiar de lactato | 91–105% |
| 5 | VO2máx | 106–120% |
| 6 | Capacidade anaeróbia | 121–150% |
| 7 | Neuromuscular | máximo (>150%) |

- **Sweet spot:** ~88–94% FTP (topo do Z3 / início do Z4) [allencoggan2019].
- **Teste de FTP de 20 min:** aquecer bem, pedalar 20 min no máximo sustentável; **FTP ≈ 95% da potência média** [allencoggan2019]. Ressalva: o fator 95% pode superestimar o limiar real em parte dos ciclistas.
- **Sem medidor de potência:** usar RPE / teste da fala com as mesmas zonas da corrida (Z2 ≈ conversa; sweet spot ≈ RPE 6–7; VO2 ≈ RPE 8–9) *(convenção)*.

### 5.2 Treinos típicos *(convenção, nos limites das zonas acima)*

- Endurance Z2: 45 min–3 h contínuos (56–75%).
- Sweet spot: 2–3 × 10–20 min a 88–94%, 5 min de recuperação.
- Limiar: 2 × 20 min ou 3 × 10–12 min a 95–105%.
- VO2máx: **5 × 3–5 min** a 106–120%, recuperação igual ao esforço.
- Anaeróbio/sprints: 6–10 × 30 s forte / 4 min leve.
- Cadência: 4–6 × 1 min a 100–110 rpm com carga leve.

### 5.3 Estrutura semanal *(convenção + 80/20 [seiler2010])*
- Iniciante (2–3x): 1 sessão de qualidade (sweet spot ou tempo) + 1–2 de endurance.
- Intermediário (3–4x): 1 limiar/sweet spot + 1 VO2 + 1–2 endurance (longo no fim de semana).
- Avançado (5–6x): 2 sessões de qualidade + endurance longo + regenerativos; ~80% do tempo em Z1–Z2.

---

## 6. Lutadores (esportes de combate)

- **Perfil físico:** força, potência neuromuscular e capacidade anaeróbia distinguem atletas de combate de nível mais alto; esforços anaeróbios mais longos caracterizam bons grapplers, e esforços mais curtos, os golpeadores [james2016].
- **Boxe amador:** combina demandas aeróbias e anaeróbias altas; potência de membros superiores e inferiores e capacidade aeróbia são atributos relevantes [chaabene2015].
- **Muay Thai:** justificativa e modelo de programa de força e condicionamento baseado em evidência [turner2009]. **MMA:** o esporte pode exigir todos os sistemas energéticos; recomendações gerais de S&C [labounty2011].
- **Diretrizes práticas para o app** *(convenção de S&C, coerente com as fontes acima e NSCA)*:
  - Força 2–3x/sem (compostos 3–5 séries de 3–6 reps, RIR 2) + potência (arremessos de medicine ball, saltos, 3–5 × 3–5 reps, descanso completo).
  - Condicionamento específico em **rounds** que imitam a luta: boxe/muay thai 3 min trabalho / 1 min descanso; MMA 5 min / 1 min; jiu-jitsu/judô/wrestling intervalos de 5–6 min (ou duração da luta da federação).
  - Base aeróbia 1–2x/sem (Z2) para recuperação entre rounds.
  - **Pescoço:** força de pescoço foi associada a menor risco de concussão em atletas escolares (cada libra extra de força ≈ 5% menos chance) [collins2014] — evidência associativa; incluir isométricos de pescoço progressivos, sem pontes de pescoço com carga para iniciantes.
  - **Perto da luta:** reduzir volume progressivamente nos últimos 7–14 dias mantendo intensidade (princípio de polimento) [bosquet2007]; não introduzir exercícios novos na semana da luta *(convenção)*.

---

## 7. Atletas (performance esportiva)

- **Periodização:** linear, ondulatória e em blocos são opções; planos periodizados > não periodizados para 1RM (efeito moderado) [williams2017].
- **Pliometria — contatos por sessão:** iniciante **80–100**, intermediário **100–120**, avançado **120–140** [potachchu2008]; recomendações posteriores permitem até ~200 contatos de alta intensidade em adultos treinados [chumyer2013]. Ressalva: não há pesquisa que defina o volume ótimo. Descanso entre séries: completo (5–10x o tempo de trabalho é a convenção NSCA).
- **Velocidade/agilidade:** sprints curtos (10–40 m) com recuperação completa, 6–10 repetições; antes de treinos de força, no início da sessão *(convenção NSCA)*.
- **Prevenção de lesão:**
  - **FIFA 11+** (aquecimento estruturado, ~20 min, 2–3x/sem): reduziu lesões em jovens jogadoras em ECR [soligard2008].
  - **Nordic hamstring:** programas com o exercício reduziram lesões de posteriores em até **51%** (8.459 atletas) [vandyk2019] — magnitude contestada em reanálises, mas efeito protetor é o mais consistente disponível.

---

## 8. HIIT / funcional / Tabata

- **Tabata (1996):** 7–8 esforços de **20 s a ~170% do VO2máx** com **10 s** de pausa (≈4 min), em cicloergômetro; aumentou VO2máx e capacidade anaeróbia em 6 semanas [tabata1996]. Atenção: o protocolo original é supramáximo; "Tabata" com exercícios de peso corporal é uma adaptação menos intensa.
- **HIIT vs contínuo:** perda de gordura semelhante com ~40% menos tempo [wewege2017].
- Recomendação para o app *(convenção)*: HIIT 2–3x/sem, nunca em dias consecutivos para iniciantes; sessões de 10–25 min de parte principal; iniciantes começam com razão trabalho:pausa 1:2 (ex.: 20 s/40 s) e progridem para 1:1 e 2:1.

---

## 9. Mobilidade e alongamento

- **Dose (ACSM):** alongar cada grande grupo ≥2–3 dias/sem, manter **10–30 s** por alongamento, **2–4 repetições**, acumulando ~60 s por exercício [garber2011] *(números do posicionamento ACSM; o abstract não os traz — conferido via referência clássica)*.
- **Antes do treino:** alongamento estático ≥60 s por grupo reduz o desempenho (−4,6%) mais do que <60 s (−1,1%); dinâmico tende a melhorar (+1,3%); se seguido de atividade dinâmica, o efeito negativo some [behm2016]. → No aquecimento, preferir mobilidade dinâmica; estático curto (<60 s/grupo) é aceitável; estático longo fica para o fim ou sessões próprias.
- Ganho de amplitude agudo dura tipicamente <30 min [behm2016].

---

## 10. Aquecimento (RAMP) e desaquecimento

- **RAMP** [jeffreys2007]:
  1. **R**aise — elevar temperatura, FC e fluxo sanguíneo (3–5 min de cardio leve).
  2. **A**ctivate e **M**obilise — ativar músculos da sessão e mobilizar articulações e amplitudes usadas.
  3. **P**otentiate — séries progressivas/específicas que aproximam a intensidade do treino (ex.: séries de aproximação, acelerações).
- Duração sugerida: 5–10 min (15–20 min para atletas/esportes) *(convenção)*.
- **Desaquecimento:** 5 min de caminhada/pedal leve (incluído no protocolo NHS C25K [nhsc25k]) + alongamento estático opcional [garber2011].

---

## 11. Triagem de saúde — PAR-Q+

### 11.1 As 7 perguntas gerais (tradução livre do PAR-Q+ oficial; existe versão brasileira validada [schwartz2021])

1. Algum médico já disse que você tem um problema no coração **ou** pressão alta?
2. Você sente dor no peito em repouso, nas atividades do dia a dia **ou** quando faz atividade física?
3. Você perde o equilíbrio por causa de tontura **ou** perdeu a consciência nos últimos 12 meses? (Responda NÃO se a tontura foi por respirar rápido demais, inclusive em exercício intenso.)
4. Você já foi diagnosticado(a) com outra doença crônica (além de doença cardíaca ou pressão alta)?
5. Você toma atualmente remédios prescritos para alguma doença crônica?
6. Você tem atualmente (ou teve nos últimos 12 meses) problema em osso, articulação ou tecido mole (músculo, ligamento ou tendão) que poderia piorar se você ficasse mais ativo(a)? (Responda NÃO se o problema foi no passado e não limita sua atividade atual.)
7. Algum médico já disse que você só deve fazer atividade física com supervisão médica?

[parq2023; schwartz2021]

### 11.2 Regras para o app
- **Todas "não":** liberado para começar de forma gradual (o PAR-Q+ orienta começar devagar e progredir) [parq2023].
- **Qualquer "sim":** o PAR-Q+ completo encaminha para perguntas de acompanhamento ou para avaliação por profissional qualificado/médico (ePARmed-X+) [parq2023]. App: **recomendar avaliação médica antes de treino vigoroso**, oferecer apenas plano leve (caminhada, mobilidade) e exibir aviso; nunca bloquear de forma diagnóstica.
- **Adiar** o início se: doença aguda/febre, gravidez sem liberação, mudança recente de estado de saúde [parq2023].

### 11.3 Sinais de alerta — parar o exercício imediatamente
Dor/aperto no peito, falta de ar desproporcional, tontura ou quase desmaio, palpitações/batimento irregular, náusea intensa, confusão, palidez/suor frio, dor articular aguda. Se não melhorar com repouso → procurar atendimento de emergência (SAMU 192). [acsmgetp2021; acog2020 para gestantes]

---

## 12. Adaptações para limitações (conservador, não diagnóstico)

Princípio: exercício terapêutico (fortalecimento + aeróbio) é recomendado para osteoartrite de joelho/quadril [nice_ng226] e exercício é a primeira linha para lombalgia [nice_ng59]. Dor leve durante o exercício pode ser aceitável se ≤ 5/10 e voltar ao basal em 24 h (modelo de monitoramento de dor) [silbernagel2007]. Dor aguda, inchaço, travamento, falseio, dor irradiada com formigamento/fraqueza → parar e procurar profissional.

| Limitação | Evitar/reduzir inicialmente | Substituir por |
|---|---|---|
| **Joelho** | Saltos (agachamento com salto, box jump, tuck jump, burpee), afundo/passada profundos, agachamento profundo com barra, cadeira extensora com carga alta no final da amplitude | Agachamento em caixa/sentar-levantar com amplitude confortável, leg press com amplitude parcial, ponte de glúteo/hip thrust, step-up baixo, mesa flexora, bike, elíptico |
| **Lombar** | Terra com barra pesado, stiff pesado, remada curvada, abdominal supra/canivete repetitivo, giro russo com carga, good morning | Ponte de glúteo, hip thrust, dead bug, prancha, prancha lateral, bird-dog, pallof, remada apoiada (máquina/unilateral com apoio), leg press, caminhada |
| **Ombro** | Desenvolvimento atrás da nuca, desenvolvimento com barra pesado, mergulho nas paralelas/banco, supino com barra amplitude total pesada, elevação lateral acima de 90°, pike push-up | Supino com halteres pegada neutra, flexão inclinada, landmine press, remadas, face pull, rotação externa com elástico, elevação lateral até 60–90° com carga leve |

*(As substituições são convenção clínica conservadora, coerente com [nice_ng226; nice_ng59]; não substituem avaliação de fisioterapeuta/médico.)*

---

## 13. Gestação (somente alertas)

- O app **não gera plano para gestantes**. Mostrar: "Na ausência de complicações, atividade física na gestação é segura e recomendada, mas exige **liberação do seu obstetra**" [acog2020]. Meta de referência: 150 min/sem moderado [acog2020; bull2020].
- **Sinais para parar** (ACOG): sangramento vaginal, contrações dolorosas regulares, perda de líquido amniótico, falta de ar antes de começar, tontura, dor de cabeça, dor no peito, fraqueza muscular que afete o equilíbrio, dor ou inchaço na panturrilha [acog2020] *(lista conferida via resumo secundário do ACOG 804)*.
- Evitar esportes de contato/risco de queda e decúbito dorsal prolongado após o 1º trimestre *(orientação ACOG amplamente citada; conferir no texto integral)*.

---

## Fontes

| id | Referência | Link |
|---|---|---|
| acsm2009 | Ratamess NA et al. (ACSM). Progression models in resistance training for healthy adults. *Med Sci Sports Exerc* 2009;41(3):687–708 | https://doi.org/10.1249/MSS.0b013e3181915670 |
| acsm2026 | ACSM. Position Stand on resistance training (Phillips SM, autor principal), 2026 — cobertura de imprensa | https://www.newswise.com/articles/acsm-unveils-landmark-2026-resistance-training-guidelines-first-update-in-17-years |
| nsca2016 | Haff GG, Triplett NT (eds). *Essentials of Strength Training and Conditioning*, 4ª ed. NSCA/Human Kinetics, 2016 | https://www.nsca.com/store/product-detail/INV/9781492501626/9781492501626 |
| schoenfeld2017 | Schoenfeld BJ, Ogborn D, Krieger JW. Dose-response relationship between weekly resistance training volume and increases in muscle mass. *J Sports Sci* 2017;35(11):1073–1082 | https://doi.org/10.1080/02640414.2016.1210197 |
| schoenfeld2019 | Schoenfeld BJ, Grgic J, Krieger J. How many times per week should a muscle be trained to maximize muscle hypertrophy? *J Sports Sci* 2019;37(11):1286–1295 | https://doi.org/10.1080/02640414.2018.1555906 |
| schoenfeld2021 | Schoenfeld BJ, Grgic J, Van Every DW, Plotkin DL. Loading recommendations for muscle strength, hypertrophy, and local endurance: a re-examination of the repetition continuum. *Sports* 2021;9(2):32 | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7927075/ |
| schoenfeld2016rest | Schoenfeld BJ et al. Longer interset rest periods enhance muscle strength and hypertrophy in resistance-trained men. *J Strength Cond Res* 2016;30(7):1805–1812 | https://doi.org/10.1519/JSC.0000000000001272 |
| robinson2024 | Robinson ZP et al. Exploring the dose–response relationship between estimated resistance training proximity to failure, strength gain, and muscle hypertrophy. *Sports Med* 2024 | https://doi.org/10.1007/s40279-024-02069-2 |
| zourdos2016 | Zourdos MC et al. Novel resistance training-specific RPE scale measuring repetitions in reserve. *J Strength Cond Res* 2016;30(1):267–275 | https://doi.org/10.1519/JSC.0000000000001049 |
| helms2016 | Helms ER, Cronin J, Storey A, Zourdos MC. Application of the repetitions in reserve-based RPE scale for resistance training. *Strength Cond J* 2016;38(4):42–49 | https://doi.org/10.1519/SSC.0000000000000218 |
| williams2017 | Williams TD et al. Comparison of periodized and non-periodized resistance training on maximal strength: a meta-analysis. *Sports Med* 2017;47:2083–2100 | https://doi.org/10.1007/s40279-017-0734-y |
| bell2023 | Bell L et al. Integrating deloading into strength and physique sports training programmes: an international Delphi consensus approach. *Sports Med Open* 2023 | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10511399/ |
| rogerson2024 | Rogerson D, ..., Bell L. Deloading practices in strength and physique sports: a cross-sectional survey. *Sports Med Open* 2024 | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10948666/ |
| bull2020 | Bull FC et al. World Health Organization 2020 guidelines on physical activity and sedentary behaviour. *Br J Sports Med* 2020;54(24):1451–1462 | https://doi.org/10.1136/bjsports-2020-102955 |
| garber2011 | Garber CE et al. (ACSM). Quantity and quality of exercise for developing and maintaining cardiorespiratory, musculoskeletal, and neuromotor fitness in apparently healthy adults. *Med Sci Sports Exerc* 2011;43(7):1334–1359 | https://doi.org/10.1249/MSS.0b013e318213fefb |
| donnelly2009 | Donnelly JE et al. (ACSM). Appropriate physical activity intervention strategies for weight loss and prevention of weight regain for adults. *Med Sci Sports Exerc* 2009;41(2):459–471 | https://doi.org/10.1249/MSS.0b013e3181949333 |
| wewege2017 | Wewege M et al. The effects of HIIT vs. moderate-intensity continuous training on body composition in overweight and obese adults: a systematic review and meta-analysis. *Obes Rev* 2017;18(6):635–646 | https://doi.org/10.1111/obr.12532 |
| sherrington2019 | Sherrington C et al. Exercise for preventing falls in older people living in the community. *Cochrane Database Syst Rev* 2019;(1):CD012424 | https://doi.org/10.1002/14651858.CD012424.pub2 |
| fragala2019 | Fragala MS et al. Resistance training for older adults: position statement from the NSCA. *J Strength Cond Res* 2019;33(8):2019–2052 | https://doi.org/10.1519/JSC.0000000000003230 |
| chodzkozajko2009 | Chodzko-Zajko WJ et al. (ACSM). Exercise and physical activity for older adults. *Med Sci Sports Exerc* 2009;41(7):1510–1530 | https://doi.org/10.1249/MSS.0b013e3181a0c95c |
| seiler2010 | Seiler S. What is best practice for training intensity and duration distribution in endurance athletes? *Int J Sports Physiol Perform* 2010;5(3):276–291 | https://pubmed.ncbi.nlm.nih.gov/20861519/ |
| reedpipe2014 | Reed JL, Pipe AL. The talk test: a useful tool for prescribing and monitoring exercise intensity. *Curr Opin Cardiol* 2014;29(5):475–480 | https://doi.org/10.1097/HCO.0000000000000097 |
| buist2008 | Buist I et al. No effect of a graded training program on the number of running-related injuries in novice runners: a randomized controlled trial. *Am J Sports Med* 2008;36(1):33–39 | https://doi.org/10.1177/0363546507307505 |
| nielsen2014 | Nielsen RO et al. Excessive progression in weekly running distance and risk of running-related injuries. *J Orthop Sports Phys Ther* 2014;44(10):739–747 | https://doi.org/10.2519/jospt.2014.5164 |
| nhsc25k | NHS. Couch to 5K running plan | https://www.nhs.uk/better-health/get-active/get-running-with-couch-to-5k/couch-to-5k-running-plan/ |
| bosquet2007 | Bosquet L, Montpetit J, Arvisais D, Mujika I. Effects of tapering on performance: a meta-analysis. *Med Sci Sports Exerc* 2007;39(8):1358–1365 | https://doi.org/10.1249/mss.0b013e31806010e0 |
| allencoggan2019 | Allen H, Coggan AR, McGregor S. *Training and Racing with a Power Meter*, 3ª ed. VeloPress, 2019 (níveis de potência) | https://www.trainingpeaks.com/learn/articles/power-training-levels/ |
| james2016 | James LP, Haff GG, Kelly VG, Beckman EM. Towards a determination of the physiological characteristics distinguishing successful mixed martial arts athletes: a systematic review of combat sport literature. *Sports Med* 2016;46(10):1525–1551 | https://doi.org/10.1007/s40279-016-0493-1 |
| chaabene2015 | Chaabène H et al. Amateur boxing: physical and physiological attributes. *Sports Med* 2015;45(3):337–352 | https://doi.org/10.1007/s40279-014-0274-7 |
| turner2009 | Turner AN. Strength and conditioning for Muay Thai athletes. *Strength Cond J* 2009;31(6):78–92 | https://doi.org/10.1519/SSC.0b013e3181b99603 |
| labounty2011 | La Bounty P, Campbell BI, Galvan E, Cooke M, Antonio J. Strength and conditioning considerations for mixed martial arts. *Strength Cond J* 2011;33(1):56–67 | https://latech.elsevierpure.com/en/publications/strength-and-conditioning-considerations-for-mixed-martial-arts/ |
| collins2014 | Collins CL et al. Neck strength: a protective factor reducing risk for concussion in high school sports. *J Prim Prev* 2014;35(5):309–319 | https://doi.org/10.1007/s10935-014-0355-2 |
| potachchu2008 | Potach DH, Chu DA. Plyometric training. In: Baechle TR, Earle RW (eds). *Essentials of Strength Training and Conditioning*, 3ª ed. 2008 (citado em revisão) | https://ojs.ub.uni-konstanz.de/cpa/article/view/6015/5496 |
| chumyer2013 | Chu DA, Myer GD. *Plyometrics*. Human Kinetics, 2013 | https://ojs.ub.uni-konstanz.de/cpa/article/view/6015/5496 |
| soligard2008 | Soligard T et al. Comprehensive warm-up programme to prevent injuries in young female footballers: cluster randomised controlled trial. *BMJ* 2008;337:a2469 | https://doi.org/10.1136/bmj.a2469 |
| vandyk2019 | van Dyk N, Behan FP, Whiteley R. Including the Nordic hamstring exercise in injury prevention programmes halves the rate of hamstring injuries: a systematic review and meta-analysis of 8459 athletes. *Br J Sports Med* 2019;53(21):1362–1370 | https://bjsm.bmj.com/content/53/21/1362 |
| tabata1996 | Tabata I et al. Effects of moderate-intensity endurance and high-intensity intermittent training on anaerobic capacity and VO2max. *Med Sci Sports Exerc* 1996;28(10):1327–1330 | https://doi.org/10.1097/00005768-199610000-00018 |
| behm2016 | Behm DG et al. Acute effects of muscle stretching on physical performance, range of motion, and injury incidence in healthy active individuals. *Appl Physiol Nutr Metab* 2016;41(1):1–11 | https://doi.org/10.1139/apnm-2015-0235 |
| jeffreys2007 | Jeffreys I. Warm-up revisited: the RAMP method of optimizing warm-ups. *Professional Strength and Conditioning* 2007;(6):12–18 | https://www.scienceforsport.com/warm-ups/ |
| parq2023 | PAR-Q+ Collaboration. The Physical Activity Readiness Questionnaire for Everyone (PAR-Q+), 2023 | https://eparmedx.com/ |
| schwartz2021 | Schwartz J et al. Translation, cultural adaptation, and reproducibility of the PAR-Q+ for Brazilian Portuguese. *Front Cardiovasc Med* 2021;8:712696 | https://doi.org/10.3389/fcvm.2021.712696 |
| acsmgetp2021 | ACSM's Guidelines for Exercise Testing and Prescription, 11ª ed. Wolters Kluwer, 2021 | https://www.acsm.org/education-resources/books/guidelines-exercise-testing-prescription |
| acog2020 | ACOG Committee Opinion No. 804: Physical activity and exercise during pregnancy and the postpartum period. *Obstet Gynecol* 2020;135(4):e178–e188 | https://doi.org/10.1097/AOG.0000000000003772 |
| nice_ng226 | NICE NG226. Osteoarthritis in over 16s: diagnosis and management (2022) | https://www.nice.org.uk/guidance/ng226/chapter/Recommendations |
| nice_ng59 | NICE NG59. Low back pain and sciatica in over 16s: assessment and management | https://www.nice.org.uk/guidance/ng59 |
| silbernagel2007 | Silbernagel KG et al. Continued sports activity, using a pain-monitoring model, during rehabilitation in patients with Achilles tendinopathy. *Am J Sports Med* 2007;35(6):897–906 | https://doi.org/10.1177/0363546506298279 |
