// Núcleo do Forja para a versão web: tradução fiel de app/src/main/java/com/forja/app/core/*.kt
// (questionário, perfil, gerador de planos, rotinas, roteiro do treino, progresso e loja).
// Mesmas respostas => mesmo plano do Android e do iPhone (conferido por tools/web/paridade.js contra o ouro do Kotlin).
(function (raiz) {
  "use strict";

  // ------------------------------------------------------------------ utilidades
  const mod = (a, n) => ((a % n) + n) % n;
  const roundToInt = x => Math.round(x); // Kotlin roundToInt (meio para cima, só valores >= 0 aqui)
  const coerce = (x, lo, hi) => Math.min(Math.max(x, lo), hi);
  const pad2 = n => String(n).padStart(2, "0");
  const um = (r, id) => (r[id] && r[id].length ? r[id][0] : null);
  const num = (r, id) => { const v = um(r, id); if (v == null || !/^-?\d+$/.test(v.trim())) return null; return parseInt(v, 10); };
  const cmpStr = (a, b) => (a < b ? -1 : a > b ? 1 : 0);
  const naoNulos = l => l.filter(x => x != null);

  // ------------------------------------------------------------------ modelo
  const MODALIDADES = [
    ["casa_corpo", "Em casa · peso do corpo", "Casa"], ["casa_elastico", "Em casa · elásticos", "Elásticos"], ["academia", "Academia · musculação", "Musculação"],
    ["corrida", "Corrida", "Corrida"], ["bike", "Bike · ciclismo", "Bike"], ["luta", "Lutadores", "Luta"], ["atleta", "Atletas · performance", "Atleta"],
    ["hiit", "HIIT & funcional", "HIIT"], ["hibrido", "Híbrido · força + corrida", "Híbrido"], ["mobilidade", "Mobilidade & alongamento", "Mobilidade"],
    ["longevidade", "50+ · força e equilíbrio", "50+"],
  ].map(([id, nome, curto]) => ({ id, nome, curto }));
  const OBJETIVOS = [
    ["massa", "Ganhar massa muscular"], ["emagrecer", "Perder gordura"], ["saude", "Saúde e vida ativa"],
    ["forca", "Ficar mais forte"], ["resistencia", "Resistência e fôlego"], ["performance", "Performance no esporte"],
  ].map(([id, nome]) => ({ id, nome }));
  const NIVEIS = [["iniciante", "Iniciante"], ["intermediario", "Intermediário"], ["avancado", "Avançado"]].map(([id, nome]) => ({ id, nome }));
  const Modalidade = id => MODALIDADES.find(m => m.id === id) || null;
  const Objetivo = id => OBJETIVOS.find(o => o.id === id) || null;
  const Nivel = id => NIVEIS.find(n => n.id === id) || null;

  const TEMPO_IDS = new Set(["prancha", "prancha-lateral", "isometria-pescoco", "farmer-walk", "equilibrio-unipodal", "monster-walk"]);
  function exercicio(o) {
    const e = {
      id: o.id, nome: o.nome, equip: o.equip || [], grupo: o.grupo, tipo: o.tipo, nivel: o.nivel == null ? 1 : o.nivel,
      dicas: o.dicas || [], busca: o.busca == null ? o.nome : o.busca, padroes: o.padroes || [], evitar: o.evitar || [],
      temImagem: !!o.img, video: o.video ? { id: o.video.id, titulo: o.video.titulo || "", canal: o.video.canal || "", idioma: o.video.idioma || "" } : null,
    };
    e.porTempo = ["cardio", "mobilidade", "tecnica"].includes(e.tipo) || TEMPO_IDS.has(e.id);
    return e;
  }

  const TB = { AQUECIMENTO: "AQUECIMENTO", PRINCIPAL: "PRINCIPAL", CIRCUITO: "CIRCUITO", INTERVALADO: "INTERVALADO", DESAQUECIMENTO: "DESAQUECIMENTO" };
  const Item = (exId, series, o = {}) => ({
    exId, series, reps: o.reps == null ? null : o.reps, trabalhoSeg: o.trabalhoSeg == null ? null : o.trabalhoSeg,
    descansoSeg: o.descansoSeg == null ? 60 : o.descansoSeg, intensidade: o.intensidade == null ? null : o.intensidade, nota: o.nota == null ? null : o.nota,
  });
  const Bloco = (nome, tipo, itens, o = {}) => ({ nome, tipo, itens, voltas: o.voltas == null ? 1 : o.voltas, nota: o.nota == null ? null : o.nota });
  const Sessao = (titulo, foco, tipo, minutos, blocos, diaSemana) => ({ titulo, foco, tipo, minutos, blocos, diaSemana });

  class Catalogo {
    constructor(lista) { this.exercicios = lista.map(exercicio); this.porId = new Map(this.exercicios.map(e => [e.id, e])); }
    get(id) { return this.porId.get(id) || null; }
    exigir(id) { const e = this.get(id); if (!e) throw new Error("Exercício desconhecido: " + id); return e; }
    alternativas(ex, equip, evitar) {
      return this.exercicios.filter(o => o.id !== ex.id && o.padroes.some(p => ex.padroes.includes(p)) && o.equip.some(q => equip.has(q)) && !o.evitar.some(v => evitar.has(v)));
    }
    grupos() { return [...new Set(this.exercicios.map(e => e.grupo))]; }
  }

  // ------------------------------------------------------------------ questionário
  const modR = r => Modalidade(um(r, "modalidade"));
  const emCasaR = r => {
    const m = modR(r)?.id;
    if (m === "casa_corpo" || m === "casa_elastico") return true;
    if (["luta", "atleta", "hibrido", "hiit", "longevidade"].includes(m)) return um(r, "local") === "casa";
    return false;
  };
  const corre = r => modR(r)?.id === "corrida" || (modR(r)?.id === "hibrido" && um(r, "hibrido_cardio") !== "bike");
  const op = (valor, titulo, descricao = null) => ({ valor, titulo, descricao });
  const P = (id, secao, titulo, subtitulo, tipo, o = {}) => ({
    id, secao, titulo, subtitulo, tipo, opcoes: o.opcoes || [], min: o.min || 0, max: o.max || 0, passo: o.passo || 1,
    padrao: o.padrao == null ? null : o.padrao, unidade: o.unidade || "", opcional: !!o.opcional, exclusiva: o.exclusiva || null, visivel: o.visivel || (() => true),
  });

  const DIAS_NOMES = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"];
  const PERGUNTAS = [
    P("nome", "Você", "Como podemos te chamar?", "Opcional — só para personalizar o app.", "TEXTO", { opcional: true }),
    P("modalidade", "Treino", "Que tipo de treino você quer fazer?", "Você pode trocar quando quiser refazendo o questionário.", "UNICA", { opcoes: [
      op("academia", "Academia · musculação", "Máquinas, barras e halteres"), op("casa_corpo", "Em casa · peso do corpo", "Sem equipamento ou com o que tiver"),
      op("casa_elastico", "Em casa · elásticos", "Faixas e tubos elásticos"), op("corrida", "Corrida", "Do primeiro trote à maratona"),
      op("bike", "Bike · ciclismo", "Rolo, estrada, MTB ou ergométrica"), op("luta", "Lutadores", "Boxe, muay thai, MMA, jiu-jitsu, judô…"),
      op("atleta", "Atletas · performance", "Força, potência, velocidade e prevenção"), op("hiit", "HIIT & funcional", "Circuitos intensos e curtos"),
      op("hibrido", "Híbrido", "Força + corrida ou bike na mesma semana"), op("mobilidade", "Mobilidade & alongamento", "Postura, flexibilidade e recuperação"),
      op("longevidade", "50+ · força e equilíbrio", "Autonomia, ossos e equilíbrio"),
    ] }),
    P("objetivo", "Treino", "Qual é o seu objetivo principal?", null, "UNICA", { opcoes: [
      op("massa", "Ganhar massa muscular", "Hipertrofia e definição"), op("emagrecer", "Perder gordura", "Gasto calórico e manutenção da massa magra"),
      op("saude", "Saúde e vida ativa", "Disposição, coração e articulações"), op("forca", "Ficar mais forte", "Mais carga nos movimentos básicos"),
      op("resistencia", "Resistência e fôlego", "Aguentar mais tempo com menos cansaço"), op("performance", "Performance", "Render mais no seu esporte ou prova"),
    ], visivel: r => modR(r)?.id !== "mobilidade" }),
    P("experiencia", "Treino", "Há quanto tempo você treina?", "Seja sincero: isso define volume e intensidade.", "UNICA", { opcoes: [
      op("iniciante", "Estou começando", "Nunca treinei ou estou parado há mais de 6 meses"), op("intermediario", "Já treino", "Com regularidade, de 6 meses a 2 anos"),
      op("avancado", "Treino há bastante tempo", "Mais de 2 anos e domino a técnica"),
    ] }),
    P("dias", "Agenda", "Quantos dias por semana você vai treinar?", "Consistência vale mais que volume.", "NUMERO", { min: 2, max: 6, padrao: 3, unidade: "dias" }),
    P("dias_semana", "Agenda", "Em quais dias?", "Escolha exatamente a quantidade de dias que você marcou.", "DIAS"),
    P("minutos", "Agenda", "Quanto tempo por sessão?", "Incluindo aquecimento e alongamento.", "UNICA", { opcoes: ["20", "30", "45", "60", "75", "90"].map(m => op(m, m + " min")) }),
    P("local", "Equipamento", "Onde você vai fazer a parte de força?", null, "UNICA", {
      opcoes: [op("academia", "Academia", "Acesso a máquinas, barras e halteres"), op("casa", "Em casa", "Com o que eu tiver disponível")],
      visivel: r => ["luta", "atleta", "hibrido", "hiit", "longevidade"].includes(modR(r)?.id) }),
    P("equipamentos", "Equipamento", "O que você tem em casa?", "Marque tudo o que tiver. Nada? Tudo bem, o peso do corpo resolve.", "MULTIPLA", { opcoes: [
      op("halter", "Halteres"), op("kettlebell", "Kettlebell"), op("elastico", "Elásticos / mini-band"), op("barra_fixa", "Barra fixa"), op("banco", "Banco ou cadeira firme"),
      op("corda", "Corda de pular"), op("bola", "Medicine ball"), op("rolo", "Rolo de liberação"), op("saco", "Saco de pancada"), op("bike", "Bike ergométrica / rolo"), op("esteira", "Esteira"),
    ], opcional: true, visivel: r => emCasaR(r) }),
    P("hibrido_cardio", "Específico", "Qual cardio entra no seu híbrido?", null, "UNICA", { opcoes: [op("corrida", "Corrida"), op("bike", "Bike")], visivel: r => modR(r)?.id === "hibrido" }),
    P("corrida_meta", "Corrida", "Qual é a sua meta na corrida?", null, "UNICA", { opcoes: [
      op("comecar", "Começar a correr", "Sair do zero até 30 minutos contínuos"), op("5k", "5 km"), op("10k", "10 km"), op("21k", "Meia maratona · 21 km"),
      op("42k", "Maratona · 42 km"), op("ritmo", "Ficar mais rápido", "Sem prova específica"), op("saude", "Correr por saúde", "Constância e prazer"),
    ], visivel: r => corre(r) }),
    P("corrida_continuo", "Corrida", "Hoje você consegue correr 20 minutos sem parar?", null, "UNICA", { opcoes: [op("sim", "Sim"), op("nao", "Ainda não")],
      visivel: r => corre(r) && um(r, "corrida_meta") !== "comecar" }),
    P("corrida_5k", "Corrida", "Seu tempo atual nos 5 km", "Opcional. Usamos para calcular seus ritmos de treino.", "NUMERO", { min: 15, max: 60, padrao: 32, unidade: "min", opcional: true,
      visivel: r => corre(r) && um(r, "corrida_meta") !== "comecar" && um(r, "corrida_continuo") === "sim" }),
    P("bike_tipo", "Bike", "Onde você pedala?", null, "UNICA", { opcoes: [op("indoor", "Rolo / indoor"), op("estrada", "Estrada · speed"), op("mtb", "Mountain bike"), op("ergometrica", "Ergométrica / spinning")],
      visivel: r => modR(r)?.id === "bike" || (modR(r)?.id === "hibrido" && um(r, "hibrido_cardio") === "bike") }),
    P("bike_ftp", "Bike", "Você sabe o seu FTP?", "Potência que você sustenta por ~1 hora, em watts. Não sabe? Pule — usamos a percepção de esforço.", "NUMERO",
      { min: 80, max: 450, passo: 5, padrao: 200, unidade: "W", opcional: true, visivel: r => modR(r)?.id === "bike" }),
    P("luta_arte", "Luta", "Qual é a sua luta?", null, "UNICA", { opcoes: [
      op("boxe", "Boxe"), op("muay", "Muay thai · kickboxing"), op("mma", "MMA"), op("bjj", "Jiu-jitsu"), op("judo", "Judô"), op("wrestling", "Wrestling · luta olímpica"), op("karate", "Karatê · taekwondo"),
    ], visivel: r => modR(r)?.id === "luta" }),
    P("luta_tecnicos", "Luta", "Quantos treinos técnicos de luta você faz por semana?", "Treinos no tatame/ringue. A preparação física se ajusta a eles.", "NUMERO",
      { min: 0, max: 7, padrao: 3, unidade: "treinos", visivel: r => modR(r)?.id === "luta" }),
    P("luta_marcada", "Luta", "Tem luta ou campeonato marcado?", null, "UNICA", { opcoes: [op("nao", "Não"), op("4", "Em ~4 semanas"), op("6", "Em ~6 semanas"), op("8", "Em ~8 semanas"), op("12", "Em ~12 semanas")],
      visivel: r => modR(r)?.id === "luta" }),
    P("atleta_esporte", "Esporte", "Qual é o perfil do seu esporte?", null, "UNICA", { opcoes: [
      op("coletivo", "Coletivo", "Futebol, basquete, vôlei, handebol"), op("raquete", "Raquete", "Tênis, padel, beach tennis"), op("velocidade", "Velocidade e saltos", "Atletismo, sprint, saltos"),
      op("resistencia", "Resistência", "Triathlon, corrida longa, remo, natação"), op("forca", "Força", "Levantamentos, crossfit, arremessos"),
    ], visivel: r => modR(r)?.id === "atleta" }),
    P("atleta_fase", "Esporte", "Em que fase da temporada você está?", null, "UNICA", { opcoes: [
      op("fora", "Fora de temporada", "Tempo para construir força e massa"), op("pre", "Pré-temporada", "Converter força em potência e velocidade"), op("em", "Em temporada", "Manter, sem atrapalhar jogos e provas"),
    ], visivel: r => modR(r)?.id === "atleta" }),
    P("idade", "Você", "Qual a sua idade?", null, "NUMERO", { min: 14, max: 90, padrao: 30, unidade: "anos" }),
    P("sexo", "Você", "Sexo", "Usado só para estimativas (ex.: gasto calórico).", "UNICA", { opcoes: [op("f", "Feminino"), op("m", "Masculino"), op("x", "Prefiro não dizer")] }),
    P("altura", "Você", "Sua altura", null, "NUMERO", { min: 120, max: 220, padrao: 170, unidade: "cm" }),
    P("peso", "Você", "Seu peso", null, "NUMERO", { min: 35, max: 220, padrao: 70, unidade: "kg" }),
    P("gestante", "Saúde", "Você está grávida ou teve bebê há menos de 6 meses?", null, "UNICA", { opcoes: [op("nao", "Não"), op("sim", "Sim")], visivel: r => um(r, "sexo") === "f" }),
    P("limitacoes", "Saúde", "Alguma dor ou limitação?", "Adaptamos os exercícios. Dor forte ou persistente pede avaliação profissional.", "MULTIPLA", { opcoes: [
      op("joelho", "Joelho"), op("lombar", "Lombar / coluna"), op("ombro", "Ombro"), op("punho", "Punho"), op("nenhuma", "Nenhuma"),
    ], exclusiva: "nenhuma" }),
    P("parq", "Saúde", "Triagem de segurança (PAR-Q+)", "Marque o que for verdade para você.", "MULTIPLA", { opcoes: [
      op("coracao", "Um médico já disse que tenho problema no coração ou pressão alta"), op("dor_peito", "Sinto dor no peito em repouso, no dia a dia ou ao me exercitar"),
      op("tontura", "Perdi o equilíbrio por tontura ou desmaiei nos últimos 12 meses"), op("cronica", "Tenho outra doença crônica diagnosticada (além de coração/pressão)"),
      op("remedio", "Tomo remédio prescrito para doença crônica"), op("osso", "Tenho problema ósseo, articular ou de tecido mole que piora com exercício"),
      op("supervisao", "Um médico disse que só devo me exercitar com supervisão"), op("nenhuma", "Nenhuma das anteriores"),
    ], exclusiva: "nenhuma" }),
  ];

  function respondida(q, r) {
    const v = r[q.id] || [];
    switch (q.tipo) {
      case "DIAS": return v.length === (num(r, "dias") || 0);
      case "MULTIPLA": return q.opcional || v.length > 0;
      case "TEXTO": return q.opcional || (v[0] || "").trim() !== "";
      default: return q.opcional || v.length > 0;
    }
  }
  const Questionario = {
    perguntas: PERGUNTAS, DIAS_NOMES, respondida,
    visiveis: r => PERGUNTAS.filter(q => q.visivel(r)),
    limpar(r) { const ids = new Set(this.visiveis(r).map(q => q.id)); const o = {}; for (const k of Object.keys(r)) if (ids.has(k)) o[k] = r[k]; return o; },
    completo(r) { return this.visiveis(r).every(q => respondida(q, r)); },
    diasSugeridos(n) {
      return ({ 1: [1], 2: [2, 5], 3: [1, 3, 5], 4: [1, 2, 4, 5], 5: [1, 2, 3, 5, 6], 6: [1, 2, 3, 4, 5, 6] })[n] || [1, 2, 3, 4, 5, 6, 7];
    },
  };

  // ------------------------------------------------------------------ perfil
  const ACADEMIA_EQ = ["corpo", "barra", "halter", "maquina", "polia", "banco", "kettlebell", "barra_fixa", "elastico", "bola", "corda", "rolo", "bike", "esteira", "outro", "rua", "pista"];
  function perfilDe(r) {
    const m = Modalidade(um(r, "modalidade")) || Modalidade("casa_corpo");
    const emCasa = m.id === "casa_corpo" || m.id === "casa_elastico" || um(r, "local") === "casa";
    const extras = r["equipamentos"] || [];
    const equip = new Set();
    if (emCasa) {
      equip.add("corpo"); equip.add("rua"); extras.forEach(x => equip.add(x));
      if (m.id === "casa_elastico") equip.add("elastico");
    } else ACADEMIA_EQ.forEach(x => equip.add(x));
    if (m.id === "luta") { equip.add("saco"); equip.add("corpo"); }
    if (m.id === "bike") equip.add("bike");
    if (m.id === "corrida") { equip.add("rua"); equip.add("pista"); }
    if (m.id === "hibrido" && um(r, "hibrido_cardio") === "bike") equip.add("bike");
    const lim = new Set((r["limitacoes"] || []).filter(x => x !== "nenhuma"));
    const nivel = Nivel(um(r, "experiencia")) || Nivel("iniciante");
    const idade = num(r, "idade") ?? 30, altura = num(r, "altura") ?? 170, peso = num(r, "peso") ?? 70;
    const imc = peso / ((altura / 100) * (altura / 100));
    if (idade >= 60 || (nivel.id === "iniciante" && imc >= 32) || lim.has("joelho") || um(r, "gestante") === "sim") lim.add("impacto");
    let dias = (r["dias_semana"] || []).map(x => (/^-?\d+$/.test(x) ? parseInt(x, 10) : null)).filter(x => x != null).sort((a, b) => a - b);
    if (!dias.length) dias = Questionario.diasSugeridos(num(r, "dias") ?? 3);
    const objPadrao = ["mobilidade", "longevidade"].includes(m.id) ? "saude" : ["atleta", "luta"].includes(m.id) ? "performance" : ["corrida", "bike"].includes(m.id) ? "resistencia" : "massa";
    const lm = um(r, "luta_marcada");
    return {
      nome: (um(r, "nome") || "").trim(), modalidade: m, objetivo: Objetivo(um(r, "objetivo")) || Objetivo(objPadrao), nivel, dias,
      minutos: num(r, "minutos") ?? 45, equip, evitar: lim, idade, sexo: um(r, "sexo") || "x", alturaCm: altura, pesoKg: peso,
      gestante: um(r, "gestante") === "sim", parq: new Set((r["parq"] || []).filter(x => x !== "nenhuma")), emCasa,
      cardioHibrido: um(r, "hibrido_cardio") || "corrida", corridaMeta: um(r, "corrida_meta") || "saude",
      correContinuo: um(r, "corrida_continuo") !== "nao" && um(r, "corrida_meta") !== "comecar", tempo5kMin: num(r, "corrida_5k"),
      bikeTipo: um(r, "bike_tipo") || "indoor", ftp: num(r, "bike_ftp"), lutaArte: um(r, "luta_arte") || "mma", lutaTecnicos: num(r, "luta_tecnicos") ?? 3,
      lutaSemanas: lm != null && /^-?\d+$/.test(lm) ? parseInt(lm, 10) : null, atletaEsporte: um(r, "atleta_esporte") || "coletivo", atletaFase: um(r, "atleta_fase") || "fora",
      get imc() { return this.pesoKg / ((this.alturaCm / 100) * (this.alturaCm / 100)); },
    };
  }
  const copiaPerfil = (p, mud) => { const n = Object.create(Object.getPrototypeOf(p)); Object.defineProperties(n, Object.getOwnPropertyDescriptors(p)); return Object.assign(n, mud); };

  // ------------------------------------------------------------------ roteiro
  const SEG_SERIE_REPS = 40;
  const Roteiro = {
    SEG_SERIE_REPS,
    passos(s, cat) {
      const out = [];
      s.blocos.forEach((b, bi) => {
        if (b.tipo === TB.CIRCUITO) {
          for (let v = 1; v <= b.voltas; v++) b.itens.forEach((it, ii) => {
            const ex = cat.get(it.exId); if (!ex) return;
            const ultimo = ii === b.itens.length - 1;
            const desc = ultimo && v < b.voltas ? Math.max(it.descansoSeg, 60) : it.descansoSeg;
            out.push(passo(bi, ii, b, ex, it, v, b.voltas, true, desc));
          });
        } else {
          b.itens.forEach((it, ii) => {
            const ex = cat.get(it.exId); if (!ex) return;
            for (let sr = 1; sr <= it.series; sr++) out.push(passo(bi, ii, b, ex, it, sr, it.series, false, it.descansoSeg));
          });
        }
      });
      if (out.length) out[out.length - 1] = { ...out[out.length - 1], descansoDepois: 0 };
      return out;
    },
    segundosItem: (it) => { const t = it.trabalhoSeg ?? SEG_SERIE_REPS; return it.series * t + Math.max(it.series - 1, 0) * it.descansoSeg; },
    segundos: ps => ps.reduce((a, p) => a + (p.item.trabalhoSeg ?? SEG_SERIE_REPS) + p.descansoDepois, 0),
    minutos(s, cat) {
      const p = this.passos(s, cat);
      const trocas = new Set(p.map(x => x.blocoIdx + "|" + x.itemIdx)).size * 15;
      return Math.max(Math.ceil((this.segundos(p) + trocas) / 60), 5);
    },
    exerciciosDaSessao: s => [...new Set(s.blocos.flatMap(b => b.itens.map(i => i.exId)))],
    formatarTempo(seg) {
      if (seg >= 3600) return Math.floor(seg / 3600) + "h" + pad2(Math.floor((seg % 3600) / 60));
      if (seg >= 60 && seg % 60 === 0) return seg / 60 + " min";
      if (seg >= 60) return Math.floor(seg / 60) + ":" + pad2(seg % 60);
      return seg + " s";
    },
    prescricao(it, circuito = false, voltas = 1) {
      const n = circuito ? voltas : it.series;
      if (circuito) return it.reps ?? (it.trabalhoSeg != null ? this.formatarTempo(it.trabalhoSeg) : "");
      if (it.reps != null) return `${n} × ${it.reps}`;
      if (it.trabalhoSeg != null && n === 1) return this.formatarTempo(it.trabalhoSeg);
      if (it.trabalhoSeg != null && it.descansoSeg > 0) return `${n} × ${this.formatarTempo(it.trabalhoSeg)} / ${this.formatarTempo(it.descansoSeg)}`;
      if (it.trabalhoSeg != null) return `${n} × ${this.formatarTempo(it.trabalhoSeg)}`;
      return `${n} séries`;
    },
  };
  function passo(bi, ii, b, ex, item, serie, total, circuito, desc) {
    return {
      blocoIdx: bi, itemIdx: ii, blocoNome: b.nome, tipoBloco: b.tipo, ex, item, serie, totalSeries: total, circuito, descansoDepois: desc,
      get porTempo() { return this.item.trabalhoSeg != null; },
      get rotulo() { return this.circuito ? `Volta ${this.serie} de ${this.totalSeries}` : this.totalSeries > 1 ? `Série ${this.serie} de ${this.totalSeries}` : "Série única"; },
    };
  }

  // ------------------------------------------------------------------ gerador
  const BILATERAL = new Set(["flexor-quadril", "alongamento-quadriceps", "alongamento-panturrilha", "alongamento-posterior", "maior-alongamento", "alongamento-peito", "rotacao-toracica", "rolo-it", "rolo-panturrilha"]);
  const CLASSICOS = new Set([
    "supino-reto", "supino-halteres", "agachamento-barra", "leg-press", "stiff", "remada-curvada", "remada-baixa", "remada-unilateral",
    "puxada-frente", "barra-fixa", "desenvolvimento-halteres", "elevacao-lateral", "rosca-direta", "triceps-polia", "flexao",
    "agachamento-livre", "agachamento-goblet", "ponte-gluteo", "elevacao-quadril", "afundo", "prancha", "crucifixo", "mesa-flexora",
    "panturrilha-pe", "face-pull", "remada-elastico", "supino-elastico", "agachamento-elastico", "desenvolvimento-elastico",
  ]);
  const FALLBACK = {
    puxar_v: ["puxar_h", "ombro_post"], puxar_h: ["puxar_v", "ombro_post"], empurrar_v: ["empurrar_h", "ombro_lat"], empurrar_h: ["empurrar_v"],
    dobradica: ["gluteo", "posterior"], posterior: ["dobradica", "gluteo"], quadriceps: ["agachar", "unilateral"], unilateral: ["agachar", "gluteo"], agachar: ["unilateral", "gluteo"],
    peito_iso: ["empurrar_h"], ombro_lat: ["ombro_post", "empurrar_v"], ombro_post: ["puxar_h"], trapezio: ["ombro_post"], biceps: ["puxar_h"], triceps: ["empurrar_h"],
    gluteo: ["dobradica", "unilateral"], pliometria: ["condicionamento"], potencia: ["pliometria", "condicionamento"], potencia_sup: ["empurrar_h"],
    potencia_rot: ["core"], carregar: ["core"], condicionamento: ["core"],
  };
  const DICAS_GERAIS = ["Pare imediatamente se sentir dor no peito, falta de ar desproporcional, tontura ou palpitações.", "Durma bem e beba água: recuperação é parte do treino."];

  const FULL_A = ["agachar", "empurrar_h", "puxar_h", "gluteo", "empurrar_v", "ombro_post", "core"];
  const FULL_B = ["dobradica", "puxar_v", "empurrar_v:1", "unilateral", "biceps", "triceps", "core:1"];
  const FULL_C = ["unilateral:1", "empurrar_h:1", "puxar_h:1", "gluteo:1", "ombro_lat", "panturrilha", "core:2"];
  const UPPER_A = ["empurrar_h", "puxar_h", "empurrar_v", "puxar_v", "ombro_lat", "biceps", "triceps"];
  const LOWER_A = ["agachar", "dobradica", "unilateral", "posterior", "panturrilha", "core"];
  const UPPER_B = ["puxar_v:1", "empurrar_h:1", "puxar_h:1", "empurrar_v:1", "ombro_post", "triceps:1", "biceps:1"];
  const LOWER_B = ["dobradica:1", "agachar:1", "gluteo", "quadriceps", "panturrilha:1", "core:1"];
  const PUSH = ["empurrar_h", "empurrar_v", "empurrar_h:1", "peito_iso", "ombro_lat", "triceps", "triceps:1"];
  const PULL = ["puxar_v", "puxar_h", "puxar_h:1", "ombro_post", "trapezio", "biceps", "biceps:1"];
  const LEGS = ["agachar", "dobradica", "unilateral", "quadriceps", "posterior", "gluteo", "panturrilha"];
  const Modelo = (titulo, foco, aq, slots, variante = 0) => ({ titulo, foco, aq, slots, variante });

  const Fase = (nome, nota, extraSerie, deload, variante, volume) => ({ nome, nota, extraSerie, deload, variante, volume });
  function faseForca(semana, n) {
    switch (semana) {
      case 1: return Fase("Adaptação", "Cargas confortáveis: foque na técnica e no ritmo (2 s descendo).", false, false, 0, 1.0);
      case 2: return Fase("Construção", "Dupla progressão: bateu o topo das repetições em todas as séries? Suba 2–5% a carga.", false, false, 0, 1.0);
      case 3: return Fase("Construção", "+1 série nos exercícios principais. Mantenha a margem de repetições (RIR).", n.id !== "iniciante", false, 0, 1.0);
      case 4: return Fase("Semana leve", "Deload: ~40% menos séries e carga um pouco menor. Recuperar também é treino.", false, true, 0, 0.6);
      case 5: return Fase("Intensificação", "Novas variações de exercícios. Recomece com cargas que deixem 2–3 repetições de reserva.", false, false, 1, 1.0);
      case 6: return Fase("Intensificação", "Progrida a carga sempre que completar o topo da faixa.", false, false, 1, 1.0);
      case 7: return Fase("Pico", "+1 série nos principais. Semana mais exigente do bloco.", true, false, 1, 1.0);
      default: return Fase("Semana leve & reteste", "Volume reduzido. No último treino, teste suas cargas para o próximo bloco.", false, true, 1, 0.6);
    }
  }
  const Dose = (series, rMin, rMax, descanso, rir) => ({ series, rMin, rMax, descanso, rir });
  function dose(obj, n, principal) {
    const N = n.id;
    switch (obj.id) {
      case "massa":
        if (N === "iniciante") return Dose(3, 10, 12, 75, "RIR 2–3");
        if (N === "intermediario") return principal ? Dose(4, 6, 10, 120, "RIR 1–2") : Dose(3, 10, 12, 75, "RIR 1–2");
        return principal ? Dose(4, 6, 8, 150, "RIR 0–2") : Dose(3, 10, 15, 75, "RIR 0–1");
      case "forca": case "performance":
        if (N === "iniciante") return principal ? Dose(3, 6, 8, 120, "RIR 2–3") : Dose(2, 10, 12, 75, "RIR 2");
        if (N === "intermediario") return principal ? Dose(4, 4, 6, 180, "RIR 1–2") : Dose(3, 8, 10, 90, "RIR 2");
        return principal ? Dose(5, 3, 5, 210, "RIR 1–2") : Dose(3, 6, 10, 120, "RIR 1–2");
      case "emagrecer":
        if (N === "iniciante") return Dose(2, 12, 15, 45, "RIR 2–3");
        if (N === "intermediario") return Dose(3, 10, 15, 45, "RIR 1–2");
        return Dose(principal ? 4 : 3, 8, 12, 60, "RIR 1–2");
      case "saude":
        if (N === "iniciante") return Dose(2, 10, 15, 60, "RIR 3");
        if (N === "intermediario") return Dose(3, 10, 12, 60, "RIR 2");
        return Dose(3, 8, 12, 75, "RIR 1–2");
      default: return Dose(N === "iniciante" ? 2 : 3, 15, 20, 40, "RIR 2");
    }
  }
  const repsDe = d => (d.rMin === d.rMax ? `${d.rMin}` : `${d.rMin}–${d.rMax}`);
  const pace = seg => `${Math.floor(seg / 60)}:${pad2(seg % 60)}`;

  class Gerador {
    constructor(cat) { this.cat = cat; }

    gerar(p) {
      const m = p.modalidade.id;
      const plano = ["academia", "casa_corpo", "casa_elastico"].includes(m) ? this.planoForca(p) : m === "corrida" ? this.planoCorrida(p) : m === "bike" ? this.planoBike(p)
        : m === "luta" ? this.planoLuta(p) : m === "atleta" ? this.planoAtleta(p) : m === "hiit" ? this.planoHiit(p) : m === "hibrido" ? this.planoHibrido(p)
        : m === "mobilidade" ? this.planoMobilidade(p) : this.planoLongevidade(p);
      const semanas = plano.semanas.map(s => ({ ...s, sessoes: s.sessoes.map(x => ({ ...x, minutos: Roteiro.minutos(x, this.cat) })) }));
      const sem1 = semanas[0].sessoes;
      const meta = `${sem1.length} treinos · ~${sem1.reduce((a, x) => a + x.minutos, 0)} min por semana`;
      return { ...plano, semanas, alertas: [...this.alertas(p), ...plano.alertas], dicas: [...plano.dicas, ...DICAS_GERAIS], metaSemanal: meta };
    }

    // ---------------------------------------------------------- seleção
    seletor(p, equip = p.equip, nivelMax = this.nivelMaximo(p)) {
      const cat = this.cat;
      const disponivel = e => {
        if (e.evitar.some(v => p.evitar.has(v))) return false;
        if (e.nivel > nivelMax) return false;
        if (e.equip.includes("barra_fixa") && !e.equip.includes("corpo")) return equip.has("barra_fixa");
        return e.equip.some(q => equip.has(q));
      };
      const academia = !p.emCasa && !["casa_corpo", "casa_elastico"].includes(p.modalidade.id);
      const pontos = e => {
        let s = 0;
        for (const q of e.equip) {
          let v = 0;
          switch (q) {
            case "barra": v = academia ? 4 : 0; break;
            case "maquina": case "polia": v = academia ? 3 : 0; break;
            case "halter": v = 3; break;
            case "kettlebell": v = 2; break;
            case "elastico": v = p.modalidade.id === "casa_elastico" ? 5 : academia ? -2 : 1; break;
            case "barra_fixa": v = 3; break;
            case "corpo": v = academia ? 0 : 2; break;
          }
          s = Math.max(s, v);
        }
        if (CLASSICOS.has(e.id)) s += 2;
        if (p.nivel.id === "iniciante" && e.nivel === 1) s += 2;
        if (p.nivel.id === "avancado" && e.nivel >= 2) s += 1;
        return s;
      };
      const pool = padrao => cat.exercicios.filter(e => e.padroes.includes(padrao) && disponivel(e))
        .map(e => [e, pontos(e)]).sort((a, b) => (b[1] - a[1]) || (a[0].nivel - b[0].nivel) || cmpStr(a[0].id, b[0].id)).map(x => x[0]);
      return {
        escolher(padrao, variante, usados) {
          for (const pd of [padrao, ...(FALLBACK[padrao] || [])]) {
            const pl = pool(pd).filter(e => !usados.has(e.id));
            if (pl.length) { const e = pl[mod(variante, pl.length)]; usados.add(e.id); return e; }
          }
          return null;
        },
        primeiro(ids, usados = new Set()) {
          const e = ids.map(id => cat.get(id)).filter(Boolean).find(x => disponivel(x) && !usados.has(x.id));
          if (e) usados.add(e.id);
          return e || null;
        },
      };
    }

    nivelMaximo(p) {
      if (p.modalidade.id === "longevidade" && p.nivel.id === "iniciante") return 1;
      if (p.nivel.id === "iniciante" || p.gestante || p.idade >= 65) return 2;
      return 3;
    }

    // ---------------------------------------------------------- blocos padrão
    aquecimento(p, foco, usados) {
      const sel = this.seletor(p, p.equip, 3);
      const cat = this.cat;
      const imp = p.evitar.has("impacto");
      const cardio = (p.equip.has("bike") && (imp || !p.emCasa)) ? cat.get("bike-leve") : (!p.emCasa && !imp) ? cat.get("eliptico")
        : (!imp && p.equip.has("corda")) ? cat.get("corda") : !imp ? cat.get("polichinelo") : cat.get("caminhada");
      const itens = [Item(cardio.id, 1, { trabalhoSeg: 180, descansoSeg: 0, intensidade: "Leve · 3/10", nota: cardio.id === "caminhada" ? "Pode ser marcha no lugar" : null })];
      const mob = foco === "superior" ? ["circulos-braco", "rotacao-toracica", "band-pull-apart"] : foco === "inferior" ? ["circulos-quadril", "maior-alongamento", "ponte-gluteo"]
        : foco === "corrida" ? ["circulos-quadril", "maior-alongamento", "educativos-corrida"] : ["circulos-quadril", "maior-alongamento", "circulos-braco"];
      for (const id of mob) {
        const e = sel.primeiro([id], usados); if (!e) continue;
        itens.push(e.porTempo ? Item(e.id, 1, { trabalhoSeg: 45, descansoSeg: 0 }) : Item(e.id, 1, { reps: "12", descansoSeg: 15, intensidade: "Ativação" }));
      }
      return Bloco("Aquecimento", TB.AQUECIMENTO, itens, { nota: "Eleve a temperatura e prepare as articulações." });
    }

    desaquecimento(foco) {
      const ids = foco === "superior" ? ["alongamento-peito", "postura-crianca"] : (foco === "inferior" || foco === "corrida") ? ["alongamento-panturrilha", "flexor-quadril", "alongamento-posterior"]
        : foco === "bike" ? ["flexor-quadril", "alongamento-quadriceps", "alongamento-posterior"] : ["postura-crianca", "flexor-quadril", "alongamento-posterior"];
      return Bloco("Volta à calma", TB.DESAQUECIMENTO, ids.map(id => Item(id, 1, { trabalhoSeg: BILATERAL.has(id) ? 60 : 40, descansoSeg: 0, nota: BILATERAL.has(id) ? "30 s cada lado" : null })));
    }

    blocoForca(p, slots, fase, minutosPrincipal, usados, o = {}) {
      const sel = o.sel || this.seletor(p), obj = o.obj || p.objetivo, principais = o.principais ?? 2, nome = o.nome || "Treino principal";
      const itens = [];
      let tempo = 0;
      for (let i = 0; i < slots.length; i++) {
        const partes = slots[i].split(":");
        const padrao = partes[0], v = partes[1] != null && /^-?\d+$/.test(partes[1]) ? parseInt(partes[1], 10) : 0;
        const e = sel.escolher(padrao, v + fase.variante, usados); if (!e) continue;
        const principal = i < principais;
        const d = dose(obj, p.nivel, principal);
        let series = d.series + (fase.extraSerie && principal ? 1 : 0);
        if (fase.deload) series = Math.max(1, Math.ceil(series * fase.volume));
        series = Math.min(series, 5);
        let item;
        if (e.porTempo) {
          const seg = e.id === "farmer-walk" ? 40 : p.nivel.id === "iniciante" ? 25 : p.nivel.id === "intermediario" ? 40 : 50;
          item = Item(e.id, series, { trabalhoSeg: seg, descansoSeg: Math.min(d.descanso, 60), intensidade: fase.deload ? "Leve" : "Firme, sem perder a postura" });
        } else {
          const semCarga = e.equip.every(q => ["corpo", "banco", "barra_fixa"].includes(q));
          item = Item(e.id, series, { reps: repsDe(d), descansoSeg: d.descanso, intensidade: fase.deload ? (semCarga ? "Mais leve · RIR 4" : "RIR 4 · carga −10%") : d.rir });
        }
        const custo = Roteiro.segundosItem(item) + 60;
        if (itens.length >= 3 && tempo + custo > minutosPrincipal * 60) break;
        tempo += custo;
        itens.push(item);
      }
      return Bloco(nome, TB.PRINCIPAL, itens, { nota: "Descanse o tempo indicado entre as séries." });
    }

    finalizador(p, usados, voltas, trabalho = 30, descanso = 30) {
      const sel = this.seletor(p);
      const ids = naoNulos([sel.escolher("condicionamento", 0, usados), sel.escolher("core", 1, usados), sel.escolher("condicionamento", 1, usados)]);
      if (ids.length < 2) return null;
      return Bloco("Finalizador metabólico", TB.CIRCUITO, ids.map(e => Item(e.id, 1, { trabalhoSeg: trabalho, descansoSeg: descanso, intensidade: "Forte · 8/10" })),
        { voltas, nota: `${trabalho} s de esforço, ${descanso} s de pausa. Mantenha a técnica.` });
    }

    sessaoCardioLeve(p, dia, minutos, titulo = "Cardio Z2", nota = "Ritmo em que você consegue conversar.") {
      const imp = p.evitar.has("impacto");
      const ex = (!p.emCasa && imp) ? "bike-leve" : !p.emCasa ? (p.nivel.id === "iniciante" ? "eliptico" : "corrida-leve") : p.equip.has("bike") ? "bike-leve"
        : (p.equip.has("esteira") && !imp && p.nivel.id !== "iniciante") ? "corrida-leve" : "caminhada";
      const corpo = Math.max(15, minutos - 5);
      return Sessao(titulo, "Base aeróbica", "cardio", minutos, [
        Bloco("Cardio contínuo", TB.PRINCIPAL, [Item(ex, 1, { trabalhoSeg: corpo * 60, descansoSeg: 0, intensidade: "Zona 2 · 3–4/10", nota })]),
        this.desaquecimento("inferior"),
      ], dia);
    }

    sessaoMobilidade(p, dia, foco, hold, titulo = null) {
      const fluxos = [
        ["Coluna & quadril", ["gato-camelo", "maior-alongamento", "flexor-quadril", "rotacao-toracica", "postura-crianca", "alongamento-adutores"]],
        ["Ombros & torácica", ["circulos-braco", "rotacao-toracica", "alongamento-peito", "band-pull-apart", "gato-camelo", "postura-crianca"]],
        ["Pernas & posterior", ["circulos-quadril", "alongamento-posterior", "alongamento-quadriceps", "alongamento-panturrilha", "alongamento-adutores", "flexor-quadril"]],
        ["Fluxo completo", ["inchworm", "maior-alongamento", "gato-camelo", "rotacao-toracica", "flexor-quadril", "alongamento-posterior", "postura-crianca"]],
        ["Liberação & equilíbrio", ["rolo-quadriceps", "rolo-panturrilha", "rolo-it", "equilibrio-unipodal", "alongamento-adutores", "postura-crianca"]],
      ];
      const [nome, ids] = fluxos[mod(foco, fluxos.length)];
      const sel = this.seletor(p, p.equip, 3);
      const usados = new Set();
      const escolhidos = naoNulos(ids.map(id => sel.primeiro([id], usados)));
      const porVolta = escolhidos.reduce((a, e) => a + (!e.porTempo ? 40 : BILATERAL.has(e.id) ? hold * 2 : hold) + 15, 0);
      const series = coerce(roundToInt(p.minutos * 60 / Math.max(porVolta, 1)), 2, 4);
      const itens = escolhidos.map(e => e.porTempo
        ? Item(e.id, series, { trabalhoSeg: BILATERAL.has(e.id) ? hold * 2 : hold, descansoSeg: 10, intensidade: "Alongamento confortável", nota: BILATERAL.has(e.id) ? `${hold} s cada lado` : null })
        : Item(e.id, series, { reps: "10–12", descansoSeg: 20, intensidade: "Controle" }));
      return Sessao(titulo ?? `Mobilidade · ${nome}`, nome, "mobilidade", 0, [
        Bloco("Fluxo de mobilidade", TB.PRINCIPAL, itens, { nota: "Respire fundo e solte o ar devagar em cada posição. Sem dor." }),
      ], dia);
    }

    // ---------------------------------------------------------- musculação
    divisao(dias) {
      if (dias <= 2) return ["Full body A/B", [Modelo("Corpo inteiro A", "Corpo inteiro", "total", FULL_A), Modelo("Corpo inteiro B", "Corpo inteiro", "total", FULL_B)]];
      if (dias === 3) return ["Full body A/B/C", [Modelo("Corpo inteiro A", "Corpo inteiro", "total", FULL_A), Modelo("Corpo inteiro B", "Corpo inteiro", "total", FULL_B), Modelo("Corpo inteiro C", "Corpo inteiro", "total", FULL_C)]];
      if (dias === 4) return ["Superior/Inferior", [Modelo("Superiores A", "Peito, costas e ombros", "superior", UPPER_A), Modelo("Inferiores A", "Pernas e glúteos", "inferior", LOWER_A),
        Modelo("Superiores B", "Costas, peito e braços", "superior", UPPER_B), Modelo("Inferiores B", "Posterior e glúteos", "inferior", LOWER_B)]];
      if (dias === 5) return ["Superior/Inferior + Push/Pull/Legs", [Modelo("Superiores", "Peito, costas e ombros", "superior", UPPER_A), Modelo("Inferiores", "Pernas e glúteos", "inferior", LOWER_A),
        Modelo("Empurrar", "Peito, ombros e tríceps", "superior", PUSH, 1), Modelo("Puxar", "Costas e bíceps", "superior", PULL, 1), Modelo("Pernas", "Quadríceps, posterior e glúteos", "inferior", LEGS, 1)]];
      return ["Push/Pull/Legs 2x", [Modelo("Empurrar A", "Peito, ombros e tríceps", "superior", PUSH), Modelo("Puxar A", "Costas e bíceps", "superior", PULL), Modelo("Pernas A", "Quadríceps, posterior e glúteos", "inferior", LEGS),
        Modelo("Empurrar B", "Peito, ombros e tríceps", "superior", PUSH, 1), Modelo("Puxar B", "Costas e bíceps", "superior", PULL, 1), Modelo("Pernas B", "Posterior, glúteos e quadríceps", "inferior", LEGS, 1)]];
    }

    sessaoForca(p, m, dia, fase, o = {}) {
      const minutos = o.minutos ?? p.minutos, finalizar = !!o.finalizar, obj = o.obj || p.objetivo;
      const usados = new Set();
      const aq = this.aquecimento(p, m.aq, usados);
      const fin = finalizar && minutos >= 40 && !fase.deload ? 8 : 0;
      const disponivel = Math.max(10, minutos - 7 - 4 - fin);
      const slots = m.slots.map(s => {
        if (m.variante === 0) return s;
        const pt = s.split(":"); const v = pt[1] != null && /^-?\d+$/.test(pt[1]) ? parseInt(pt[1], 10) : 0;
        return `${pt[0]}:${v + m.variante}`;
      });
      const principal = this.blocoForca(p, slots, fase, disponivel, usados, { obj });
      const blocos = [aq, principal];
      if (fin > 0) { const f = this.finalizador(p, usados, p.nivel.id === "iniciante" ? 3 : 4); if (f) blocos.push(f); }
      blocos.push(this.desaquecimento(m.aq));
      return Sessao(m.titulo, m.foco, "forca", minutos, blocos, dia);
    }

    planoForca(p) {
      const n = p.dias.length;
      let diasForca = p.objetivo.id === "saude" ? Math.min(n, 3) : (p.objetivo.id === "emagrecer" || p.objetivo.id === "resistencia") ? Math.min(n, n >= 5 ? 3 : Math.max(2, n - 1))
        : p.nivel.id === "iniciante" ? Math.min(n, 4) : n;
      diasForca = Math.max(diasForca, Math.min(n, 2));
      const [nomeDiv, modelos] = this.divisao(diasForca);
      const indicesForca = new Set([...Array(diasForca).keys()].map(k => Math.min(roundToInt(k * n / diasForca), n - 1)));
      const semanas = [];
      for (let w = 1; w <= 8; w++) {
        const fase = faseForca(w, p.nivel);
        let f = 0, c = 0;
        const sessoes = p.dias.map((dia, i) => {
          const forca = indicesForca.has(i);
          if (forca && f < diasForca) { const m = modelos[f % modelos.length]; f++; return this.sessaoForca(p, m, dia, fase, { finalizar: p.objetivo.id === "emagrecer" }); }
          c++;
          const hiit = p.objetivo.id === "emagrecer" && c % 2 === 0 && p.nivel.id !== "iniciante" && !p.evitar.has("impacto");
          return hiit ? this.sessaoHiitCurta(p, dia, fase, w) : this.sessaoCardioLeve(p, dia, Math.min(p.minutos, fase.deload ? 30 : 45));
        });
        semanas.push({ numero: w, fase: fase.nome, nota: fase.nota, sessoes });
      }
      const local = p.modalidade.id === "casa_corpo" ? "em casa" : p.modalidade.id === "casa_elastico" ? "com elásticos" : "na academia";
      return {
        nome: `${p.objetivo.nome} ${local}`,
        resumo: `${nomeDiv} · ${diasForca}x força${n > diasForca ? ` + ${n - diasForca}x cardio` : ""} · 8 semanas com semana leve na 4 e na 8.`,
        modalidade: p.modalidade, objetivo: p.objetivo, nivel: p.nivel, semanas,
        dicas: naoNulos([
          "RIR = repetições em reserva. RIR 2 significa terminar a série sentindo que faria mais 2.",
          "Progrida sempre que completar o topo da faixa de repetições em todas as séries.",
          p.modalidade.id !== "academia" ? "Ficou fácil? Desça mais devagar (3–4 s), pause no fundo ou use a variação mais difícil." : null,
          p.objetivo.id === "massa" ? "Para hipertrofia: proteína ~1,6 g/kg/dia e sono de 7–9 h fazem diferença." : null,
          p.objetivo.id === "emagrecer" ? "O treino de força preserva a massa magra no déficit calórico; some passos no dia a dia (7–10 mil)." : null,
          p.objetivo.id === "saude" ? "Meta da OMS: 150–300 min de atividade moderada por semana + força 2x." : null,
        ]),
        alertas: [], metaSemanal: "",
      };
    }

    sessaoHiitCurta(p, dia, fase, w) {
      const usados = new Set();
      const sel = this.seletor(p);
      const ids = naoNulos([sel.escolher("condicionamento", w, usados), sel.escolher("agachar", w, usados), sel.escolher("condicionamento", w + 1, usados), sel.escolher("core", w, usados)]);
      const voltas = fase.deload ? 3 : 4 + (p.nivel.id === "avancado" ? 1 : 0);
      return Sessao("HIIT curto", "Condicionamento", "hiit", 0, [
        this.aquecimento(p, "total", usados),
        Bloco("Circuito 40/20", TB.CIRCUITO, ids.map(e => Item(e.id, 1, { trabalhoSeg: 40, descansoSeg: 20, intensidade: "Forte · 8/10" })), { voltas, nota: "40 s de esforço, 20 s de pausa. 1 min entre voltas se precisar." }),
        this.desaquecimento("total"),
      ], dia);
    }

    // ---------------------------------------------------------- corrida
    faixaPace(p, de, ate) { const t = p.tempo5kMin; if (t == null) return null; const base = Math.trunc(t * 60 / 5); return `${pace(base + de)}–${pace(base + ate)} /km`; }
    semanasCorrida(meta) { return ({ "10k": 10, "21k": 12, "42k": 16 })[meta] || 8; }
    longaoMin(meta, n) {
      const t = {
        "5k": { iniciante: [30, 45], intermediario: [40, 55], avancado: [45, 65] }, "10k": { iniciante: [40, 70], intermediario: [50, 80], avancado: [60, 90] },
        "21k": { iniciante: [60, 120], intermediario: [70, 130], avancado: [80, 140] }, "42k": { iniciante: [75, 190], intermediario: [90, 200], avancado: [100, 210] },
      };
      return (t[meta] || { iniciante: [30, 50], intermediario: [40, 65], avancado: [50, 80] })[n.id];
    }
    taper(meta) { return meta === "42k" ? 3 : meta === "21k" ? 2 : 1; }
    fatorCorrida(w, total, meta) {
      const tp = this.taper(meta), pico = total - tp;
      if (w > pico) { const k = w - pico; const f = (tp === 3 ? [0.75, 0.6, 0.4] : tp === 2 ? [0.7, 0.45] : [0.55])[k - 1]; return [f, w === total ? "Semana de prova" : "Polimento"]; }
      if (w % 4 === 0) return [-1.0, "Recuperação"];
      return [(w - 1) / Math.max(1, pico - 1), w <= Math.trunc(pico / 2) ? "Base" : "Construção"];
    }
    tiros(n, w) {
      const T = (reps, trabalho, pausa, nome) => ({ reps, trabalho, pausa, nome });
      const l = n.id === "iniciante" ? [T(6, 60, 120, "6 × 1 min"), T(8, 60, 90, "8 × 1 min"), T(6, 120, 120, "6 × 2 min"), T(5, 180, 120, "5 × 3 min")]
        : n.id === "intermediario" ? [T(8, 90, 90, "8 × 400 m (~90 s)"), T(6, 180, 120, "6 × 800 m (~3 min)"), T(5, 240, 120, "5 × 1 km (~4 min)"), T(10, 60, 60, "10 × 1 min")]
        : [T(10, 90, 60, "10 × 400 m"), T(6, 240, 90, "6 × 1 km"), T(5, 300, 120, "5 × 1200 m (~5 min)"), T(12, 60, 60, "12 × 1 min"), T(4, 480, 120, "4 × 2 km (~8 min)")];
      return l[mod(w - 1, l.length)];
    }
    intens(zona, pc) { return pc != null ? `${zona} · ${pc}` : zona; }

    sessaoCorrida(p, dia, tipo, w, total, meta, forcaExtra = false) {
      const [lo, hi] = this.longaoMin(meta, p.nivel);
      const [fator] = this.fatorCorrida(w, total, meta);
      const tp = this.taper(meta);
      let longao = fator < 0 ? roundToInt((lo + (hi - lo) * (w - 2) / Math.max(1, total - tp - 1)) * 0.75)
        : w > total - tp ? roundToInt(hi * fator) : roundToInt(lo + (hi - lo) * fator);
      longao = Math.max(longao, 20);
      const leve = coerce(roundToInt(longao * 0.6), 20, Math.max(20, p.minutos - 10));
      const recup = fator < 0 || w > total - tp;
      const aqCorrida = Bloco("Aquecimento", TB.AQUECIMENTO, [
        Item("corrida-leve", 1, { trabalhoSeg: 600, descansoSeg: 0, intensidade: "Bem leve · 2–3/10", nota: "Comece caminhando se precisar" }),
        Item("educativos-corrida", 1, { trabalhoSeg: 180, descansoSeg: 0, nota: "Skipping, anfersen e dribling" }),
      ]);
      const ultima = w === total && tipo === "L" && ["5k", "10k", "21k", "42k"].includes(meta);
      const blocos = [];
      let titulo, foco;
      if (ultima) {
        const km = meta.replace(/k$/, "");
        titulo = `Dia da prova · ${km} km`; foco = "Prova";
        blocos.push(Bloco("Aquecimento", TB.AQUECIMENTO, [Item("corrida-leve", 1, { trabalhoSeg: 600, descansoSeg: 0, intensidade: "Leve" })]));
        blocos.push(Bloco("Prova", TB.PRINCIPAL, [Item("prova", 1, { trabalhoSeg: this.longaoMin(meta, p.nivel)[1] * 60, descansoSeg: 0, intensidade: "Ritmo de prova", nota: "Largue controlado; acelere na segunda metade." })]));
      } else if (tipo === "L") {
        titulo = "Longão"; foco = "Resistência aeróbica";
        blocos.push(Bloco("Corrida longa", TB.PRINCIPAL, [Item("longao", 1, { trabalhoSeg: longao * 60, descansoSeg: 0, intensidade: this.intens("Zona 2 · conversa", this.faixaPace(p, 70, 105)),
          nota: longao >= 75 ? "Leve água e carboidrato a partir de 60 min." : null })]));
      } else if (tipo === "Q" && !recup) {
        const corridaLonga = meta === "21k" || meta === "42k";
        if (corridaLonga && w % 2 === 0) {
          const blocosMin = Math.min(20, 8 + w), reps = meta === "42k" ? 3 : 2;
          titulo = "Ritmo de prova"; foco = "Ritmo específico";
          blocos.push(aqCorrida);
          blocos.push(Bloco("Blocos no ritmo de prova", TB.INTERVALADO, [Item("tempo-run", reps, { trabalhoSeg: blocosMin * 60, descansoSeg: 120,
            intensidade: this.intens("Ritmo de prova · 6–7/10", this.faixaPace(p, meta === "42k" ? 40 : 25, meta === "42k" ? 55 : 40)), nota: "Recupere trotando 2 min" })]));
        } else {
          const t = this.tiros(p.nivel, Math.trunc((w + 1) / 2));
          titulo = `Intervalado · ${t.nome}`; foco = "Velocidade e VO2";
          blocos.push(aqCorrida);
          blocos.push(Bloco("Tiros", TB.INTERVALADO, [Item("tiros", t.reps, { trabalhoSeg: t.trabalho, descansoSeg: t.pausa,
            intensidade: this.intens("Forte · 8/10", this.faixaPace(p, -10, 0)), nota: "Recuperação trotando ou caminhando" })]));
        }
      } else if (tipo === "T" && !recup) {
        const dur = Math.min(p.nivel.id === "iniciante" ? 10 + w : p.nivel.id === "intermediario" ? 15 + w * 2 : 20 + w * 2, 40);
        titulo = "Corrida de limiar"; foco = "Limiar";
        blocos.push(aqCorrida);
        blocos.push(Bloco("Limiar contínuo", TB.PRINCIPAL, [Item("tempo-run", 1, { trabalhoSeg: dur * 60, descansoSeg: 0, intensidade: this.intens("Confortavelmente difícil · 7/10", this.faixaPace(p, 15, 25)) })]));
      } else if (tipo === "R") {
        titulo = "Regenerativo"; foco = "Recuperação";
        blocos.push(Bloco("Corrida leve", TB.PRINCIPAL, [Item("corrida-leve", 1, { trabalhoSeg: Math.min(30, leve) * 60, descansoSeg: 0, intensidade: this.intens("Muito leve · 2/10", this.faixaPace(p, 90, 120)) })]));
      } else {
        titulo = forcaExtra ? "Leve + força" : "Corrida leve"; foco = "Base aeróbica";
        const strides = p.nivel.id !== "iniciante" && !recup ? [Item("tiros", 4, { trabalhoSeg: 20, descansoSeg: 60, intensidade: "Acelerações · 85%", nota: "Strides: soltas, sem forçar" })] : [];
        blocos.push(Bloco("Corrida leve", TB.PRINCIPAL, [Item("corrida-leve", 1, { trabalhoSeg: leve * 60, descansoSeg: 0, intensidade: this.intens("Zona 2 · conversa", this.faixaPace(p, 60, 90)) }), ...strides]));
      }
      if (forcaExtra) blocos.push(this.forcaCorredor(p, w));
      blocos.push(this.desaquecimento("corrida"));
      return Sessao(titulo, foco, "corrida", 0, blocos, dia);
    }

    forcaCorredor(p, w, nome = "Força para corredores") {
      const pesos = (p.modalidade.id === "corrida" || p.modalidade.id === "bike") ? [] : ["elastico", "halter", "kettlebell"].filter(x => p.equip.has(x));
      const sel = this.seletor(p, new Set(["corpo", ...pesos]));
      const usados = new Set();
      const ids = naoNulos([sel.escolher("unilateral", w, usados), sel.escolher("gluteo", w, usados), sel.escolher("panturrilha", 0, usados), sel.escolher("core", w, usados)]);
      return Bloco(nome, TB.CIRCUITO, ids.map(e => e.porTempo ? Item(e.id, 1, { trabalhoSeg: 40, descansoSeg: 20 }) : Item(e.id, 1, { reps: "10–12", descansoSeg: 20, intensidade: "RIR 2" })),
        { voltas: p.nivel.id === "iniciante" ? 2 : 3, nota: "Previne lesões e melhora a economia de corrida." });
    }

    sessaoCaminhaCorre(p, dia, w, k) {
      const tabela = [[60, 90, 8], [90, 90, 7], [120, 90, 6], [180, 90, 5], [300, 120, 4], [480, 120, 3], [720, 120, 2]];
      let principal;
      if (w >= 8) {
        const min = [25, 28, 30][coerce(k, 0, 2)];
        principal = Item("corrida-leve", 1, { trabalhoSeg: min * 60, descansoSeg: 0, intensidade: "Zona 2 · conversa", nota: "Corrida contínua! Devagar está ótimo." });
      } else {
        const [correS, caminha, reps] = tabela[w - 1];
        principal = Item("caminhada-corrida", reps, { trabalhoSeg: correS, descansoSeg: caminha, intensidade: "Trote leve · 4–5/10", nota: "No descanso, caminhe rápido" });
      }
      return Sessao(w >= 8 ? "Corrida contínua" : "Caminhada + corrida", "Construção de base", "corrida", 0, [
        Bloco("Aquecimento", TB.AQUECIMENTO, [Item("caminhada", 1, { trabalhoSeg: 300, descansoSeg: 0, intensidade: "Caminhada rápida" })]),
        Bloco("Corre & caminha", TB.INTERVALADO, [principal]),
        Bloco("Volta à calma", TB.DESAQUECIMENTO, [Item("caminhada", 1, { trabalhoSeg: 300, descansoSeg: 0 }), ...this.desaquecimento("corrida").itens]),
      ], dia);
    }

    planoCorrida(p) {
      let meta = p.corridaMeta;
      const alertas = [];
      if (!p.correContinuo) {
        if (["10k", "21k", "42k"].includes(meta)) alertas.push(`Antes de buscar os ${meta.replace(/k$/, "")} km, este plano constrói sua base até 30 minutos contínuos. Depois, refaça o questionário.`);
        meta = "comecar";
      }
      const n = p.dias.length;
      if (meta === "comecar") {
        const semanas = [];
        for (let w = 1; w <= 8; w++) {
          let k = 0;
          const sessoes = p.dias.map((dia, i) => {
            const corrida = n <= 3 || i % 2 === 0 || (k < 3 && n - i <= 3 - k);
            if (corrida && k < 3) return this.sessaoCaminhaCorre(p, dia, w, k++);
            if (i % 2 === 1 && n >= 4) return Sessao("Força para corredores", "Prevenção", "forca", 0, [this.aquecimento(p, "inferior", new Set()), this.forcaCorredor(p, w, "Circuito de força"), this.desaquecimento("inferior")], dia);
            return this.sessaoCardioLeve(copiaPerfil(p, { emCasa: true }), dia, 30, "Caminhada rápida", "Passo firme: respiração acelerada, mas dá para conversar.");
          });
          semanas.push({ numero: w, fase: w < 4 ? "Base" : w < 8 ? "Construção" : "30 minutos!", nota: "Corrida e caminhada intercaladas. Repita a semana se sentir que precisa — tudo bem.", sessoes });
        }
        return { nome: "Do zero aos 30 minutos", resumo: "8 semanas de corrida e caminhada intercaladas até 30 min contínuos (≈ 5 km).", modalidade: p.modalidade, objetivo: p.objetivo, nivel: p.nivel, semanas,
          dicas: ["Ritmo certo é o que deixa você conversar. Correr devagar é correr certo.", "Tênis confortável e superfície regular nas primeiras semanas.", "Dor articular que piora ao correr = pare e descanse; dor muscular leve no dia seguinte é normal."],
          alertas, metaSemanal: "" };
      }
      const total = this.semanasCorrida(meta);
      const base = n === 2 ? ["Q", "L"] : n === 3 ? ["Q", "E", "L"] : n === 4 ? ["Q", "E", p.nivel.id === "iniciante" ? "E" : "T", "L"] : n === 5 ? ["Q", "E", "T", "E", "L"] : ["Q", "E", "T", "E", "R", "L"];
      const modelo = base.map(t => (meta === "saude" && p.nivel.id === "iniciante" && t === "Q" ? "E" : t));
      const semanas = [];
      for (let w = 1; w <= total; w++) {
        const [, fase] = this.fatorCorrida(w, total, meta);
        let forcas = 0;
        const sessoes = p.dias.map((dia, i) => {
          const t = modelo[Math.min(i, modelo.length - 1)];
          const forca = t === "E" && forcas < (n >= 5 ? 2 : 1) && n >= 3;
          if (forca) forcas++;
          return this.sessaoCorrida(p, dia, t, w, total, meta, forca);
        });
        const nota = fase === "Recuperação" ? "Semana mais leve para absorver o treino. Volume ~25% menor." : fase === "Polimento" ? "Menos volume, mantendo um pouco de intensidade: chegue descansado."
          : fase === "Semana de prova" ? "Durma bem, nada de novidade em tênis ou comida. Confie no treino!" : fase === "Base" ? "80% dos treinos em ritmo leve (Seiler). A intensidade fica nos dias de qualidade."
          : "Volume subindo aos poucos. Respeite os ritmos — leve é leve.";
        semanas.push({ numero: w, fase, nota, sessoes });
      }
      const nome = ({ "5k": "5 km", "10k": "10 km", "21k": "Meia maratona", "42k": "Maratona", ritmo: "Mais velocidade" })[meta] || "Correr por saúde";
      return { nome: `${nome} em ${total} semanas`, resumo: `${n}x por semana · distribuição 80/20 · longão progressivo com semanas de recuperação.`, modalidade: p.modalidade, objetivo: p.objetivo, nivel: p.nivel, semanas,
        dicas: naoNulos([
          p.tempo5kMin == null ? "Sem tempo de 5 km informado, os ritmos estão por percepção de esforço (escala 0–10)." : `Ritmos calculados a partir dos seus ${p.tempo5kMin} min nos 5 km. Refaça um teste a cada 6–8 semanas.`,
          "Cadência alta (passos curtos) reduz o impacto. Mire em ~170–180 passos por minuto.",
          meta === "21k" || meta === "42k" ? "Treine a hidratação e os géis nos longões, nunca teste novidade no dia da prova." : null,
        ]), alertas, metaSemanal: "" };
    }

    // ---------------------------------------------------------- bike
    zona(p, z) { const ftp = p.ftp; return ftp != null ? `${z.nome} · ${roundToInt(ftp * z.de / 100)}–${roundToInt(ftp * z.ate / 100)} W` : `${z.nome} · ${z.rpe}`; }

    sessaoBike(p, dia, tipo, w, fase) {
      const Z = (nome, de, ate, rpe) => ({ nome, de, ate, rpe });
      const Z1 = Z("Z1 Recuperação", 0, 55, "2/10"), Z2 = Z("Z2 Endurance", 56, 75, "3–4/10"), Z3 = Z("Z3 Tempo", 76, 90, "5–6/10"),
        SS = Z("Sweet spot", 88, 94, "6–7/10"), Z4 = Z("Z4 Limiar", 91, 105, "7–8/10"), Z5 = Z("Z5 VO2máx", 106, 120, "9/10");
      const leve = fase.deload, ini = p.nivel.id === "iniciante";
      const aq = Bloco("Aquecimento", TB.AQUECIMENTO, [Item("bike-leve", 1, { trabalhoSeg: 600, descansoSeg: 0, intensidade: this.zona(p, Z2), nota: "Suba a intensidade aos poucos" })]);
      const volta = Bloco("Volta à calma", TB.DESAQUECIMENTO, [Item("bike-leve", 1, { trabalhoSeg: 300, descansoSeg: 0, intensidade: this.zona(p, Z1) }), ...this.desaquecimento("bike").itens]);
      const k = w <= 4 ? w : w - 4;
      const intervalo = (titulo, foco, ex, reps, trab, pausa, z, nota = null) => Sessao(titulo, foco, "bike", 0, [aq,
        Bloco("Série principal", TB.INTERVALADO, [Item(ex, reps, { trabalhoSeg: trab, descansoSeg: pausa, intensidade: this.zona(p, z), nota: nota ?? "Pausa pedalando leve" })]), volta], dia);
      switch (tipo) {
        case "SS":
          if (leve) return intervalo("Sweet spot leve", "Limiar", "bike-intervalado", 2, 480, 240, ini ? Z3 : SS);
          if (ini) return intervalo("Tempo", "Resistência", "bike-intervalado", 3, (5 + k) * 60, 240, Z3);
          return intervalo("Sweet spot", "Limiar", "bike-intervalado", k >= 3 ? 2 : 3, [8, 10, 15, 20][Math.min(k, 3)] * 60, 300, SS);
        case "LIM":
          if (leve || ini) return this.sessaoBike(p, dia, "SS", w, fase);
          return intervalo("Limiar", "FTP", "bike-intervalado", k >= 3 ? 3 : 4, [6, 8, 10, 12][Math.min(k, 3)] * 60, 240, Z4);
        case "VO2":
          if (leve) return intervalo("Ativação curta", "Manutenção", "bike-intervalado", 4, 60, 120, Z4);
          if (ini) return intervalo("Intervalado curto", "Potência aeróbica", "bike-intervalado", 6 + k, 60, 120, Z4);
          return intervalo("VO2máx", "Potência aeróbica", "bike-intervalado", [5, 6, 5, 4][Math.min(k, 3)], [180, 180, 240, 300][Math.min(k, 3)], 180, Z5, "Recupere o mesmo tempo pedalando leve");
        case "CAD":
          return Sessao("Endurance + cadência", "Técnica", "bike", 0, [aq,
            Bloco("Drills de cadência", TB.INTERVALADO, [Item("bike-cadencia", 6, { trabalhoSeg: 30, descansoSeg: 90, intensidade: "Leve · 110+ rpm", nota: "Quadril parado no selim" })]),
            Bloco("Endurance", TB.PRINCIPAL, [Item("bike-leve", 1, { trabalhoSeg: Math.max(15, p.minutos - 30) * 60, descansoSeg: 0, intensidade: this.zona(p, Z2) })]), volta], dia);
        case "SUB": return intervalo("Subida · força no pedal", "Força específica", "bike-subida", leve ? 3 : 4 + Math.trunc(k / 2), 360, 180, Z3, "60–70 rpm, marcha pesada");
        case "REC": return Sessao("Recuperação ativa", "Recuperação", "bike", 0, [Bloco("Giro leve", TB.PRINCIPAL, [Item("bike-leve", 1, { trabalhoSeg: 35 * 60, descansoSeg: 0, intensidade: this.zona(p, Z1) })]), this.desaquecimento("bike")], dia);
        case "Z2": return Sessao("Endurance", "Base aeróbica", "bike", 0, [Bloco("Endurance", TB.PRINCIPAL, [Item("bike-leve", 1, { trabalhoSeg: Math.max(30, p.minutos - 5) * 60, descansoSeg: 0, intensidade: this.zona(p, Z2) })]), this.desaquecimento("bike")], dia);
        case "F": return Sessao("Força para ciclistas", "Prevenção e potência", "forca", 0, [this.aquecimento(p, "inferior", new Set()), this.forcaCorredor(p, w, "Circuito de força"), this.desaquecimento("inferior")], dia);
        default: {
          const [lo, hi] = ini ? [60, 105] : p.nivel.id === "intermediario" ? [90, 150] : [120, 210];
          const prog = w <= 3 ? w - 1 : (w >= 5 && w <= 7) ? w - 2 : 0;
          const min = leve ? lo : roundToInt(lo + (hi - lo) * prog / 5);
          return Sessao("Longo de fim de semana", "Resistência", "bike", 0, [Bloco("Pedal longo", TB.PRINCIPAL, [Item("bike-leve", 1, { trabalhoSeg: min * 60, descansoSeg: 0, intensidade: this.zona(p, Z2), nota: "Coma e beba a cada 20–30 min acima de 90 min" })]), this.desaquecimento("bike")], dia);
        }
      }
    }

    planoBike(p) {
      const n = p.dias.length;
      const modelo = n === 2 ? ["SS", "LONGO"] : n === 3 ? ["SS", "CAD", "LONGO"] : n === 4 ? ["VO2", "CAD", "SS", "LONGO"] : n === 5 ? ["VO2", "F", "LIM", "REC", "LONGO"]
        : ["VO2", "F", "SS", p.bikeTipo === "mtb" || p.bikeTipo === "estrada" ? "SUB" : "CAD", "REC", "LONGO"];
      const semanas = [];
      for (let w = 1; w <= 8; w++) {
        const b = faseForca(w, p.nivel);
        const fase = b.deload ? { ...b, nome: "Recuperação", nota: "Semana leve: volume menor e só uma sessão intensa curta." }
          : { ...b, nota: `Progressão de tempo em zona. ${p.ftp == null ? "Sem FTP: guie-se pela percepção de esforço." : `Zonas calculadas a partir do FTP de ${p.ftp} W.`}` };
        semanas.push({ numero: w, fase: fase.deload ? fase.nome : w < 4 ? "Base" : "Construção", nota: fase.nota, sessoes: p.dias.map((dia, i) => this.sessaoBike(p, dia, modelo[Math.min(i, modelo.length - 1)], w, fase)) });
      }
      return { nome: `Ciclismo · ${p.objetivo.nome.toLowerCase()}`, resumo: `${n}x por semana · zonas de Coggan · sweet spot, VO2 e longo progressivo.`, modalidade: p.modalidade, objetivo: p.objetivo, nivel: p.nivel, semanas,
        dicas: naoNulos([
          p.ftp == null ? "Para descobrir o FTP: após aquecer, pedale 20 min no máximo sustentável; FTP ≈ 95% da potência média." : null,
          "Ajuste da bike: joelho levemente flexionado no ponto mais baixo do pedal.",
          "Acima de 90 min, consuma 30–60 g de carboidrato por hora.",
        ]), alertas: [], metaSemanal: "" };
    }

    // ---------------------------------------------------------- lutas
    round(arte) {
      const R = (trabalho, pausa, rounds, grappling) => ({ trabalho, pausa, rounds, grappling });
      return ({ boxe: R(180, 60, 3, false), muay: R(180, 120, 5, false), mma: R(300, 60, 3, false), bjj: R(360, 60, 4, true), judo: R(240, 60, 4, true), wrestling: R(180, 30, 2, true) })[arte] || R(120, 60, 3, false);
    }
    faseLuta(w, total, marcada) {
      if (!marcada) { const it = faseForca(w, Nivel("intermediario")); return { ...it, nome: it.deload ? "Semana leve" : w <= 4 ? "Preparação geral" : "Preparação específica" }; }
      const polimento = total >= 6 ? 2 : 1;
      if (w === total) return Fase("Semana da luta", "Volume mínimo, só manter a velocidade. Durma e se hidrate bem.", false, true, 1, 0.4);
      if (w > total - polimento) return Fase("Polimento", "Volume cai, intensidade fica: chegue rápido e descansado.", false, true, 1, 0.6);
      if (w <= Math.trunc((total - polimento) / 2)) return Fase("Preparação geral", "Base de força e condicionamento.", false, false, 0, 1.0);
      return Fase("Preparação específica", "Força vira potência; rounds no ritmo da luta.", true, false, 1, 1.0);
    }

    sessaoRounds(p, dia, fase, w, variante) {
      const r = this.round(p.lutaArte);
      const sel = this.seletor(p, p.equip, 3);
      const drills = r.grappling ? ["sprawl", "fuga-quadril", "ponte-pescoco", "bear-crawl", "burpee", "farmer-walk"] : ["sombra", "saco-combinacoes", "sprawl", "burpee", "battle-rope", "corda"];
      let disponiveis = naoNulos(drills.map(id => sel.primeiro([id])));
      if (!disponiveis.length) disponiveis = naoNulos([this.cat.get("sombra")]);
      const rounds = (fase.deload ? Math.max(2, roundToInt(r.rounds * fase.volume)) : fase.extraSerie ? r.rounds + 1 : r.rounds) + (p.nivel.id === "avancado" && !fase.deload ? 1 : 0);
      const itens = [...Array(rounds).keys()].map(i => {
        const e = disponiveis[mod(i + variante + w, disponiveis.length)];
        return Item(e.id, 1, { trabalhoSeg: r.trabalho, descansoSeg: r.pausa, intensidade: "Ritmo de luta · 8/10",
          nota: r.grappling ? "Alterne 30 s explosivos e 30 s de controle" : "Picos de 10 s em máxima velocidade a cada 30 s" });
      });
      const pausaMin = r.pausa / 60;
      const usados = new Set(disponiveis.map(e => e.id));
      let core = [];
      if (p.minutos >= 45 && !fase.deload) {
        const a = sel.escolher("core", w, usados), b = sel.escolher("core", w + 1, usados);
        const pesc = sel.primeiro(["isometria-pescoco"], usados);
        core = naoNulos([a, b, p.lutaArte !== "karate" ? pesc : null]);
      }
      return Sessao("Condicionamento em rounds", "Específico de luta", "luta", 0, naoNulos([
        this.aquecimento(p, "total", new Set()),
        Bloco("Rounds", TB.INTERVALADO, itens, { nota: `${rounds} rounds de ${Math.trunc(r.trabalho / 60)} min com ${pausaMin < 1 ? `${r.pausa} s` : `${roundToInt(pausaMin)} min`} de pausa — o formato da sua luta.` }),
        core.length ? Bloco("Core & pescoço", TB.CIRCUITO, core.map(e => e.porTempo ? Item(e.id, 1, { trabalhoSeg: 30, descansoSeg: 15 }) : Item(e.id, 1, { reps: "12", descansoSeg: 15 })), { voltas: 3 }) : null,
        this.desaquecimento("total"),
      ]), dia);
    }

    sessaoPotencia(p, dia, fase, titulo = "Potência & velocidade", comPrevencao = false) {
      const sel = this.seletor(p, p.equip, 3);
      const usados = new Set();
      const aq = this.aquecimento(p, "total", usados);
      const ex = naoNulos([sel.escolher("pliometria", fase.variante, usados), sel.escolher("potencia", fase.variante, usados), sel.escolher("potencia_sup", 0, usados), sel.escolher("potencia_rot", 0, usados)]);
      const series = fase.deload ? 2 : p.nivel.id === "iniciante" ? 3 : 4;
      const itens = ex.map(e => Item(e.id, series, { reps: e.padroes.includes("pliometria") ? "4–6" : "3–5", descansoSeg: 90, intensidade: "Máxima velocidade", nota: "Pare antes de perder qualidade" }));
      const blocos = [aq, Bloco("Potência", TB.PRINCIPAL, itens, { nota: "Cada repetição o mais rápida possível. Qualidade > cansaço." })];
      if (comPrevencao) blocos.push(this.blocoPrevencao(p, fase));
      else {
        const a = sel.escolher("core", 0, usados), b = sel.escolher("core", 2, usados), pesc = sel.primeiro(["isometria-pescoco"], usados);
        const core = naoNulos([a, b, p.modalidade.id === "luta" ? pesc : null]);
        blocos.push(Bloco("Core", TB.PRINCIPAL, core.map(e => e.porTempo ? Item(e.id, 3, { trabalhoSeg: 30, descansoSeg: 30 }) : Item(e.id, 3, { reps: "10–12", descansoSeg: 45 }))));
      }
      blocos.push(this.desaquecimento("total"));
      return Sessao(titulo, "Explosão", "forca", 0, blocos, dia);
    }

    blocoPrevencao(p, fase) {
      const sel = this.seletor(p, p.equip, 3);
      const usados = new Set();
      const ex = naoNulos([sel.primeiro(["nordico", "mesa-flexora", "stiff-halteres"], usados), sel.primeiro(["monster-walk", "ponte-unilateral"], usados),
        sel.primeiro(["rotacao-externa", "face-pull", "band-pull-apart"], usados), sel.primeiro(["panturrilha-pe", "panturrilha-elastico"], usados),
        sel.primeiro(["prancha-lateral"], usados), sel.primeiro(["equilibrio-unipodal"], usados)]);
      const s = fase.deload ? 1 : 2;
      return Bloco("Prevenção de lesões", TB.PRINCIPAL, ex.map(e => e.porTempo ? Item(e.id, s, { trabalhoSeg: 30, descansoSeg: 20 }) : Item(e.id, s, { reps: e.id === "nordico" ? "4–6" : "10–12", descansoSeg: 45, intensidade: "Controle" })),
        { nota: "Posterior, quadril, ombro e tornozelo: onde mais acontecem lesões no esporte." });
    }

    planoLuta(p) {
      const marcada = p.lutaSemanas != null, total = p.lutaSemanas ?? 8, n = p.dias.length, muitosTecnicos = p.lutaTecnicos >= 5;
      const base = n === 2 ? ["FP", "R"] : n === 3 ? ["F", "R", "P"] : n === 4 ? ["F", "R", "P", "A"] : n === 5 ? ["F", "R", "P", "A", "M"] : ["F", "R", "P", "A", "R2", "M"];
      const modelo = base.map(t => (muitosTecnicos && t === "R2" ? "M" : t));
      const forcaSlots = ["agachar", "dobradica", "empurrar_h", "puxar_v", "puxar_h", "carregar", "core"];
      const semanas = [];
      for (let w = 1; w <= total; w++) {
        const fase = this.faseLuta(w, total, marcada);
        const sessoes = p.dias.map((dia, i) => {
          const t = modelo[Math.min(i, modelo.length - 1)];
          if (t === "F" || t === "FP") {
            const usados = new Set();
            const aq = this.aquecimento(p, "total", usados);
            const pre = modelo[i] === "FP" ? naoNulos([this.seletor(p).escolher("pliometria", 0, usados)]).map(e => Item(e.id, 3, { reps: "4–5", descansoSeg: 90, intensidade: "Máxima velocidade" })) : [];
            const principal = this.blocoForca(p, forcaSlots, fase, Math.max(15, p.minutos - 15), usados, { obj: Objetivo("forca") });
            const pesc = p.lutaArte !== "karate" && !p.evitar.has("impacto") ? this.cat.get("isometria-pescoco") : null;
            return Sessao(modelo[i] === "FP" ? "Força & potência" : "Força máxima", "Força", "forca", 0, naoNulos([aq,
              pre.length ? Bloco("Potência", TB.PRINCIPAL, pre) : null, principal,
              pesc ? Bloco("Pescoço", TB.PRINCIPAL, [Item(pesc.id, 2, { trabalhoSeg: 60, descansoSeg: 30, intensidade: "Progressivo, sem dor", nota: "15 s em cada direção" })]) : null,
              this.desaquecimento("total")]), dia);
          }
          if (t === "R") return this.sessaoRounds(p, dia, fase, w, 0);
          if (t === "R2") return this.sessaoRounds(p, dia, fase, w, 2);
          if (t === "P") return this.sessaoPotencia(p, dia, fase);
          if (t === "A") return this.sessaoCardioLeve(copiaPerfil(p, { emCasa: p.emCasa }), dia, Math.min(45, p.minutos), "Base aeróbica", "Melhora a recuperação entre os rounds. Ritmo de conversa.");
          return this.sessaoMobilidade(p, dia, w, 40, "Mobilidade & recuperação");
        });
        semanas.push({ numero: w, fase: fase.nome, nota: fase.nota, sessoes });
      }
      const arte = PERGUNTAS.find(q => q.id === "luta_arte").opcoes.find(o => o.valor === p.lutaArte).titulo;
      return { nome: `Preparação física · ${arte}`, resumo: (marcada ? `Camp de ${total} semanas até a luta` : "Bloco de 8 semanas") + " · força, potência e rounds no formato da sua luta.",
        modalidade: p.modalidade, objetivo: p.objetivo, nivel: p.nivel, semanas,
        dicas: naoNulos([
          "Os treinos técnicos de luta continuam sendo a prioridade: encaixe a força longe dos sparrings mais duros.",
          muitosTecnicos ? `Com ${p.lutaTecnicos} treinos técnicos por semana, reduzimos o condicionamento extra para não acumular fadiga.` : null,
          "Corte de peso agressivo prejudica o desempenho: planeje com nutricionista.",
        ]), alertas: [], metaSemanal: "" };
    }

    // ---------------------------------------------------------- atletas
    planoAtleta(p) {
      const n = p.dias.length, emTemporada = p.atletaFase === "em";
      const objF = p.atletaFase === "fora" ? Objetivo("massa") : Objetivo("forca");
      const forcaA = ["agachar", "dobradica", "empurrar_h", "puxar_h", "unilateral", "core"];
      const forcaB = ["dobradica:1", "unilateral:1", "empurrar_v", "puxar_v", "posterior", "core:1"];
      const base = n === 2 ? ["A+P", "B+PREV"] : n === 3 ? ["A", "V+P", "B+PREV"] : n === 4 ? ["A", "V", "B", "P+PREV"] : n === 5 ? ["A", "V", "B", "P+PREV", "C"] : ["A", "V", "B", "P+PREV", "C", "M"];
      const modelo = base.map(t => (emTemporada && (t === "C" || t === "V") && n >= 4 ? "M" : t));
      const semanas = [];
      for (let w = 1; w <= 8; w++) {
        const b = faseForca(w, p.nivel);
        const fase = { ...b,
          nome: b.deload ? "Semana leve" : p.atletaFase === "em" ? "Manutenção" : w <= 3 ? (p.atletaFase === "fora" ? "Hipertrofia funcional" : "Força") : (p.atletaFase === "fora" ? "Força" : "Potência"),
          nota: emTemporada ? "Em temporada: pouco volume, alta qualidade. Nunca treine pesado na véspera de jogo." : b.nota };
        const obj = w > 4 && p.atletaFase === "fora" ? Objetivo("forca") : objF;
        const sessoes = p.dias.map((dia, i) => {
          const t = modelo[Math.min(i, modelo.length - 1)];
          if (["A", "A+P", "B", "B+PREV"].includes(t)) {
            const m = modelo[i];
            const usados = new Set();
            const aq = this.aquecimento(p, "total", usados);
            const pot = m === "A+P" ? naoNulos([this.seletor(p).escolher("pliometria", 0, usados)]).map(e => Item(e.id, 3, { reps: "4–5", descansoSeg: 90, intensidade: "Máxima velocidade" })) : [];
            const minutos = emTemporada ? Math.min(p.minutos, 45) : p.minutos;
            const principal = this.blocoForca(p, m.startsWith("A") ? forcaA : forcaB, emTemporada ? { ...fase, deload: true, volume: 0.6 } : fase,
              Math.max(15, minutos - 15 - (m === "B+PREV" ? 8 : 0)), usados, { obj, nome: "Força" });
            return Sessao(m.startsWith("A") ? "Força A" : "Força B", "Força", "forca", 0, naoNulos([aq, pot.length ? Bloco("Potência", TB.PRINCIPAL, pot) : null,
              principal, m === "B+PREV" ? this.blocoPrevencao(p, fase) : null, this.desaquecimento("total")]), dia);
          }
          if (t === "V" || t === "V+P") return this.sessaoVelocidade(p, dia, fase, modelo[i] === "V+P");
          if (t === "P+PREV") return this.sessaoPotencia(p, dia, fase, "Potência & prevenção", true);
          if (t === "C") return this.sessaoCondicionamentoEsporte(p, dia, fase);
          return this.sessaoMobilidade(p, dia, w, 40, "Mobilidade & recuperação");
        });
        semanas.push({ numero: w, fase: fase.nome, nota: fase.nota, sessoes });
      }
      const esporte = PERGUNTAS.find(q => q.id === "atleta_esporte").opcoes.find(o => o.valor === p.atletaEsporte).titulo;
      const faseNome = PERGUNTAS.find(q => q.id === "atleta_fase").opcoes.find(o => o.valor === p.atletaFase).titulo;
      return { nome: `Performance · ${esporte}`, resumo: `${faseNome} · força, potência, velocidade e prevenção em 8 semanas.`, modalidade: p.modalidade, objetivo: p.objetivo, nivel: p.nivel, semanas,
        dicas: ["Treine força/potência longe (24–48 h) dos jogos e treinos táticos mais intensos.", "Pliometria: qualidade de aterrissagem antes de altura ou volume.", "Durma 8–10 h: é quando a adaptação acontece."],
        alertas: [], metaSemanal: "" };
    }

    sessaoVelocidade(p, dia, fase, comPotencia) {
      const sel = this.seletor(p, p.equip, 3);
      const usados = new Set();
      const itens = [
        Item("educativos-corrida", 1, { trabalhoSeg: 240, descansoSeg: 30, nota: "Skipping, anfersen, dribling" }),
        Item("tiros", fase.deload ? 4 : 6 + fase.variante * 2, { trabalhoSeg: 6, descansoSeg: 90, intensidade: "Máxima velocidade", nota: "Sprints de 20–30 m. Recuperação completa" }),
      ];
      naoNulos([sel.primeiro(["bound-lateral"], usados), sel.primeiro(["salto-distancia"], usados)]).forEach(e => itens.push(Item(e.id, 3, { reps: "4–6", descansoSeg: 75, intensidade: "Explosivo" })));
      const blocos = [this.aquecimento(p, "corrida", usados), Bloco("Velocidade & agilidade", TB.PRINCIPAL, itens, { nota: "Velocidade se treina descansado: pausa longa é parte do treino." })];
      if (comPotencia) { const e = sel.escolher("potencia_sup", 0, usados); if (e) blocos.push(Bloco("Potência de tronco", TB.PRINCIPAL, [Item(e.id, 3, { reps: "5", descansoSeg: 75 })])); }
      blocos.push(this.desaquecimento("corrida"));
      return Sessao("Velocidade & agilidade", "Velocidade", "atleta", 0, blocos, dia);
    }

    sessaoCondicionamentoEsporte(p, dia, fase) {
      if (p.atletaEsporte === "resistencia") return this.sessaoCardioLeve(p, dia, p.minutos, "Endurance Z2", "Volume aeróbico de base.");
      if (p.atletaEsporte === "forca") return { ...this.sessaoHiitCurta(p, dia, fase, 1), titulo: "Condicionamento metabólico" };
      return Sessao("Condicionamento intermitente", "Repetição de sprints", "atleta", 0, [
        this.aquecimento(p, "corrida", new Set()),
        Bloco("Intermitente 15/15", TB.INTERVALADO, [Item("tiros", fase.deload ? 8 : 12, { trabalhoSeg: 15, descansoSeg: 15, intensidade: "Forte · 85–90%", nota: "Simula as ações repetidas do jogo" })],
          { nota: "Faça 2 séries com 3 min de pausa se estiver em boa forma." }),
        this.desaquecimento("corrida"),
      ], dia);
    }

    // ---------------------------------------------------------- HIIT
    planoHiit(p) {
      const [trab, pausa, voltasBase] = p.nivel.id === "iniciante" ? [30, 30, 3] : p.nivel.id === "intermediario" ? [40, 20, 4] : [45, 15, 5];
      const semanas = [];
      for (let w = 1; w <= 8; w++) {
        const fase = faseForca(w, p.nivel);
        const voltas = fase.deload ? Math.max(2, voltasBase - 1) : (w === 3 || w === 7) ? voltasBase + 1 : voltasBase;
        const sessoes = p.dias.map((dia, i) => {
          const tipo = p.dias.length >= 5 && i === p.dias.length - 1 ? 3 : i % 3;
          const usados = new Set();
          const sel = this.seletor(p);
          if (tipo === 0) {
            const ex = naoNulos([sel.escolher("agachar", w, usados), sel.escolher("empurrar_h", w, usados), sel.escolher("dobradica", w, usados), sel.escolher("puxar_h", w, usados), sel.escolher("core", w, usados), sel.escolher("condicionamento", w, usados)]);
            return Sessao("Circuito de força", "Força + fôlego", "hiit", 0, [this.aquecimento(p, "total", usados),
              Bloco(`Circuito ${trab}/${pausa}`, TB.CIRCUITO, ex.map(e => Item(e.id, 1, { trabalhoSeg: trab, descansoSeg: pausa, intensidade: "Forte · 7–8/10" })), { voltas, nota: "Descanse 1 min entre as voltas." }),
              this.desaquecimento("total")], dia);
          }
          if (tipo === 1) {
            const pares = naoNulos([sel.escolher("condicionamento", w, usados), sel.escolher("agachar", w + 1, usados), sel.escolher("condicionamento", w + 1, usados), sel.escolher("core", w + 1, usados)]);
            const tabatas = fase.deload ? 2 : p.nivel.id === "iniciante" ? 2 : Math.min(4, pares.length);
            return Sessao("Tabata", "Intervalado máximo", "hiit", 0, [this.aquecimento(p, "total", usados),
              ...pares.slice(0, tabatas).map((e, k) => Bloco(`Tabata ${k + 1}`, TB.INTERVALADO, [Item(e.id, 8, { trabalhoSeg: 20, descansoSeg: 10, intensidade: "Máximo · 9/10" })], { nota: "8 × 20 s / 10 s. 1 min de pausa entre os tabatas." })),
              this.desaquecimento("total")], dia);
          }
          if (tipo === 2) {
            const ex = naoNulos([sel.escolher("potencia", w, usados), sel.escolher("unilateral", w, usados), sel.escolher("empurrar_v", w, usados), sel.escolher("condicionamento", w + 2, usados), sel.escolher("core", w + 2, usados)]);
            return Sessao("EMOM funcional", "Potência e ritmo", "hiit", 0, [this.aquecimento(p, "total", usados),
              Bloco("A cada minuto", TB.CIRCUITO, ex.map(e => Item(e.id, 1, { trabalhoSeg: 40, descansoSeg: 20, intensidade: "Ritmo constante" })), { voltas, nota: "Um exercício por minuto: trabalhe 40 s e use o resto do minuto para respirar." }),
              this.desaquecimento("total")], dia);
          }
          return this.sessaoMobilidade(p, dia, w, 40, "Mobilidade ativa");
        });
        semanas.push({ numero: w, fase: fase.nome, nota: fase.deload ? "Semana leve: menos voltas, mesma qualidade." : "Mais voltas nas semanas 3 e 7. Respeite as pausas.", sessoes });
      }
      return { nome: "HIIT & funcional", resumo: `Circuitos ${trab}/${pausa}, Tabata e EMOM · ${p.dias.length}x por semana.`, modalidade: p.modalidade, objetivo: p.objetivo, nivel: p.nivel, semanas,
        dicas: ["HIIT é intenso: 2–4 sessões por semana costumam bastar; nos outros dias, prefira atividades leves.", "Técnica primeiro. Se perder a forma, reduza o ritmo, não a amplitude."],
        alertas: [], metaSemanal: "" };
    }

    // ---------------------------------------------------------- híbrido
    planoHibrido(p) {
      const n = p.dias.length, bike = p.cardioHibrido === "bike";
      const modelo = n === 2 ? ["FA", "CL"] : n === 3 ? ["FA", "CQ", "FB"] : n === 4 ? ["U", "CQ", "L", "CL"] : n === 5 ? ["U", "CQ", "L", "CE", "FC"] : ["U", "CQ", "L", "CE", "FC", "CL"];
      const meta = ["5k", "10k"].includes(p.corridaMeta) ? p.corridaMeta : "ritmo";
      const semanas = [];
      for (let w = 1; w <= 8; w++) {
        const fase = faseForca(w, p.nivel);
        const sessoes = p.dias.map((dia, i) => {
          switch (modelo[Math.min(i, modelo.length - 1)]) {
            case "FA": return this.sessaoForca(p, Modelo("Força · corpo inteiro A", "Corpo inteiro", "total", FULL_A), dia, fase);
            case "FB": return this.sessaoForca(p, Modelo("Força · corpo inteiro B", "Corpo inteiro", "total", FULL_B), dia, fase);
            case "FC": return this.sessaoForca(p, Modelo("Força · corpo inteiro C", "Corpo inteiro", "total", FULL_C), dia, fase);
            case "U": return this.sessaoForca(p, Modelo("Força · superiores", "Peito, costas e ombros", "superior", UPPER_A), dia, fase);
            case "L": return this.sessaoForca(p, Modelo("Força · inferiores", "Pernas e glúteos", "inferior", LOWER_A), dia, fase);
            case "CQ": return bike ? this.sessaoBike(p, dia, w % 2 === 0 ? "VO2" : "SS", w, fase) : p.correContinuo ? this.sessaoCorrida(p, dia, w % 2 === 0 ? "T" : "Q", w, 8, meta) : this.sessaoCaminhaCorre(p, dia, w, 0);
            case "CE": return bike ? this.sessaoBike(p, dia, "Z2", w, fase) : p.correContinuo ? this.sessaoCorrida(p, dia, "E", w, 8, meta) : this.sessaoCaminhaCorre(p, dia, w, 1);
            default: return bike ? this.sessaoBike(p, dia, "LONGO", w, fase) : p.correContinuo ? this.sessaoCorrida(p, dia, "L", w, 8, meta) : this.sessaoCaminhaCorre(p, dia, w, 2);
          }
        });
        semanas.push({ numero: w, fase: fase.nome, nota: `Separe força de pernas e treinos intensos de ${bike ? "bike" : "corrida"} por pelo menos 24 h quando possível.`, sessoes });
      }
      return { nome: `Híbrido · força + ${bike ? "bike" : "corrida"}`, resumo: `${n}x por semana · força 2–3x e cardio estruturado · 8 semanas.`, modalidade: p.modalidade, objetivo: p.objetivo, nivel: p.nivel, semanas,
        dicas: ["Treino concorrente funciona: só evite colocar o cardio intenso logo antes do treino de pernas.", "Mantenha a maior parte do cardio em intensidade leve (zona 2)."],
        alertas: [], metaSemanal: "" };
    }

    // ---------------------------------------------------------- mobilidade e 50+
    planoMobilidade(p) {
      const inicial = p.nivel.id === "iniciante" ? 30 : p.nivel.id === "intermediario" ? 40 : 50;
      const semanas = [];
      for (let w = 1; w <= 8; w++) {
        const hold = Math.min(inicial + (w >= 3 ? 10 : 0) + (w >= 6 ? 10 : 0), 75);
        semanas.push({ numero: w, fase: w <= 2 ? "Consciência" : w <= 5 ? "Amplitude" : "Controle", nota: `Segure cada posição por ~${hold} s, respirando devagar. Nunca force até doer.`,
          sessoes: p.dias.map((dia, i) => this.sessaoMobilidade(p, dia, i + w, hold)) });
      }
      return { nome: "Mobilidade & alongamento", resumo: `${p.dias.length} sessões por semana de coluna, quadril, ombros e pernas · 8 semanas.`, modalidade: p.modalidade, objetivo: p.objetivo, nivel: p.nivel, semanas,
        dicas: ["Alongamento estático rende mais depois do treino ou em sessão separada (ACSM: 10–30 s, 2–4 repetições).", "Antes de treinar, prefira mobilidade dinâmica."],
        alertas: [], metaSemanal: "" };
    }

    planoLongevidade(p) {
      const n = p.dias.length;
      const a = ["agachar", "empurrar_h", "puxar_h", "gluteo", "panturrilha", "carregar"];
      const b = ["unilateral", "empurrar_v", "puxar_v", "dobradica", "core", "ombro_post"];
      const modelo = n === 2 ? ["A", "B"] : n === 3 ? ["A", "CAM", "B"] : n === 4 ? ["A", "CAM", "B", "MOB"] : n === 5 ? ["A", "CAM", "B", "CAM", "MOB"] : ["A", "CAM", "B", "CAM", "A2", "MOB"];
      const semanas = [];
      for (let w = 1; w <= 8; w++) {
        const fase = faseForca(w, Nivel("iniciante"));
        const sessoes = p.dias.map((dia, i) => {
          const t = modelo[Math.min(i, modelo.length - 1)];
          if (t === "A" || t === "A2" || t === "B") {
            const usados = new Set();
            const aq = this.aquecimento(p, "total", usados);
            const principal = this.blocoForca(p, t === "B" ? b : a, { ...fase, variante: fase.variante + (t === "A2" ? 1 : 0) }, Math.max(15, p.minutos - 15), usados, { obj: Objetivo("saude"), principais: 3 });
            const eq = this.cat.get("equilibrio-unipodal");
            return Sessao(t === "B" ? "Força funcional B" : "Força funcional A", "Força e equilíbrio", "forca", 0, [aq, principal,
              Bloco("Equilíbrio", TB.PRINCIPAL, [Item(eq.id, 2, { trabalhoSeg: 60, descansoSeg: 20, nota: "30 s cada perna, perto de um apoio" })]),
              this.desaquecimento("total")], dia);
          }
          if (t === "CAM") {
            const equip = new Set(p.equip); equip.delete("esteira");
            return this.sessaoCardioLeve(copiaPerfil(p, { emCasa: true, equip }), dia, Math.min(p.minutos, 20 + w * 3), "Caminhada", "Passo firme: dá para conversar, mas não para cantar.");
          }
          return this.sessaoMobilidade(p, dia, w, 30, "Mobilidade & equilíbrio");
        });
        semanas.push({ numero: w, fase: fase.nome, nota: "Força 2x por semana preserva músculos, ossos e autonomia (OMS 2020).", sessoes });
      }
      return { nome: "Força, equilíbrio e longevidade", resumo: `${n}x por semana · força funcional, equilíbrio e caminhada.`, modalidade: p.modalidade, objetivo: p.objetivo, nivel: p.nivel, semanas,
        dicas: ["Levante-se devagar após exercícios no chão para evitar tontura.", "Prefira calçado firme e um apoio por perto nos exercícios de equilíbrio."],
        alertas: [], metaSemanal: "" };
    }

    alertas(p) {
      const out = [];
      if (p.parq.size) out.push("Você marcou itens da triagem PAR-Q+. Procure liberação médica antes de começar e comece com intensidade leve.");
      if (p.gestante) out.push("Gestação ou pós-parto: treine somente com liberação médica. Evite impacto, esforço máximo e longos períodos deitada de barriga para cima após o 1º trimestre. Removemos exercícios de impacto.");
      const lim = [...p.evitar].filter(x => x !== "impacto");
      if (lim.length) out.push(`Adaptamos os exercícios para: ${lim.join(", ")}. Se a dor aumentar durante ou após o treino, pare e procure um fisioterapeuta.`);
      if (p.idade < 18) out.push("Menor de 18 anos: treine com supervisão de um profissional, priorizando técnica antes da carga.");
      if (p.nivel.id === "iniciante" && p.imc >= 32 && !["mobilidade", "bike"].includes(p.modalidade.id)) out.push("Priorizamos exercícios de baixo impacto para proteger as articulações no começo.");
      return out;
    }
  }

  // ------------------------------------------------------------------ rotinas avulsas
  const ANTES = "Antes do esporte", DEPOIS = "Depois do treino", MOBILIDADE = "Mobilidade & bem-estar";
  const t = (id, seg, nota = null, series = 1) => Item(id, series, { trabalhoSeg: seg, descansoSeg: 5, nota });
  const r = (id, reps, nota = null, series = 1) => Item(id, series, { reps, descansoSeg: 10, nota });
  const e = (id, seg = 30, lados = true) => Item(id, 2, { trabalhoSeg: lados ? seg * 2 : seg, descansoSeg: 10, intensidade: "Alongamento confortável", nota: lados ? `${seg} s cada lado` : null });
  const rotina = (id, categoria, titulo, sub, tema, nota, ...itens) => ({ id, categoria, titulo, subtitulo: sub, tema,
    sessao: Sessao(titulo, sub, "mobilidade", 0, [Bloco(categoria === DEPOIS ? "Alongamento estático" : categoria === ANTES ? "Preparo dinâmico" : "Mobilidade", TB.PRINCIPAL, itens, { nota })], 0) });
  const DIN = "Movimentos controlados, amplitude crescendo a cada repetição. Nada de forçar.";
  const EST = "Segure sem balançar, respirando devagar. Desconforto leve, nunca dor.";
  const TODAS = [
    rotina("pre-corrida", ANTES, "Antes de correr", "Tornozelos, quadril e posterior acordados", "corrida", DIN,
      t("circulos-tornozelo", 40, "20 s cada pé"), r("balanco-pernas", "10 cada perna", "Frente-trás e lado a lado"), t("circulos-quadril", 40),
      r("maior-alongamento", "5 cada lado"), t("chute-gluteo", 30), t("educativos-corrida", 120, "Skipping, anfersen e dribling"), t("carioca", 40, "20 s para cada lado")),
    rotina("pre-bike", ANTES, "Antes de pedalar", "Quadril, coluna e joelhos prontos para o selim", "bike", DIN,
      t("circulos-quadril", 40), r("gato-camelo", "8"), r("balanco-pernas", "10 cada perna"), t("circulos-joelho", 30),
      t("circulos-tornozelo", 30), r("rotacao-toracica", "6 cada lado"), t("flexor-quadril", 40, "20 s cada lado — curto antes do treino")),
    rotina("pre-inferiores", ANTES, "Antes de treinar pernas", "Quadril e joelhos para agachar e levantar", "academia", DIN,
      t("circulos-quadril", 40), r("balanco-pernas", "10 cada perna"), r("maior-alongamento", "5 cada lado"),
      r("agachamento-livre", "10", "Lento, descendo fundo"), r("ponte-gluteo", "12", "Aperte o glúteo no topo"), t("monster-walk", 40)),
    rotina("pre-superiores", ANTES, "Antes de treinar superiores", "Ombros e escápulas para empurrar e puxar", "academia", DIN,
      t("circulos-ombro", 30), t("circulos-braco", 40), r("abertura-peito-dinamica", "12"), r("band-pull-apart", "15"),
      r("rotacao-externa", "12 cada lado"), r("rotacao-toracica", "6 cada lado"), r("flexao-inclinada", "8", "Série leve de ativação")),
    rotina("pre-luta-pe", ANTES, "Antes de lutar em pé", "Boxe, muay thai, MMA, karatê", "luta", DIN,
      t("corda", 120, "Ou polichinelo"), t("circulos-ombro", 30), t("circulos-punho", 30), t("alongamento-pescoco", 30, "15 s cada lado, sem forçar"),
      r("balanco-pernas", "10 cada perna", "Frontal e lateral para os chutes"), t("circulos-quadril", 30), t("sombra", 120, "Comece solto, acelere no fim")),
    rotina("pre-luta-solo", ANTES, "Antes de lutar no chão", "Jiu-jitsu, judô e wrestling", "luta", DIN,
      r("gato-camelo", "8"), t("fuga-quadril", 60, "Pelo tatame"), r("ponte-pescoco", "6 cada lado"), t("circulos-quadril", 30),
      r("spider", "5 cada lado"), t("isometria-pescoco", 40, "Leve: 10 s em cada direção"), r("inchworm", "5")),
    rotina("pre-coletivos", ANTES, "Antes do futebol e coletivos", "Inspirado na parte 1 do FIFA 11+", "atleta", DIN,
      t("corrida-leve", 120, "Trote leve"), t("carioca", 40, "20 s para cada lado"), r("balanco-pernas", "10 cada perna"), t("chute-gluteo", 30),
      t("circulos-quadril", 30, "Abrindo e fechando o portão"), r("maior-alongamento", "4 cada lado"), r("tiros", "4", "Acelerações progressivas de 15 m")),
    rotina("pre-raquete", ANTES, "Antes do tênis e padel", "Ombro, punho e rotação de tronco", "atleta", DIN,
      t("circulos-ombro", 30), t("circulos-punho", 30), r("rotacao-externa", "12 cada lado"), r("moinho", "10"),
      r("rotacao-toracica", "6 cada lado"), t("carioca", 40), r("bound-lateral", "6", "Saltos laterais leves")),
    rotina("pre-natacao", ANTES, "Antes de nadar", "Ombros soltos e caixa torácica aberta", "atleta", DIN,
      t("circulos-braco", 40, "Para frente e para trás"), t("circulos-ombro", 30), r("abertura-peito-dinamica", "12"), r("band-pull-apart", "15"),
      r("rotacao-externa", "12 cada lado"), r("rotacao-toracica", "6 cada lado"), t("circulos-tornozelo", 30)),
    rotina("pre-hiit", ANTES, "Antes do HIIT e funcional", "Corpo todo pronto para intensidade", "hiit", DIN,
      t("polichinelo", 60), r("inchworm", "5"), r("maior-alongamento", "4 cada lado"), r("agachamento-livre", "10"),
      t("circulos-punho", 30), t("circulos-ombro", 30), r("spider", "4 cada lado")),
    rotina("pre-caminhada", ANTES, "Antes da caminhada ou trilha", "Rápida e suave para qualquer idade", "longevidade", DIN,
      t("circulos-tornozelo", 40), t("circulos-joelho", 30), t("circulos-quadril", 40), r("balanco-pernas", "8 cada perna", "Com apoio"), t("circulos-braco", 30)),
    rotina("pos-corrida", DEPOIS, "Depois de correr", "Panturrilha, posterior, quadríceps e quadril", "corrida", EST,
      e("alongamento-panturrilha"), e("alongamento-posterior"), e("alongamento-quadriceps"), e("flexor-quadril"), e("alongamento-gluteo"), e("alongamento-adutores", 40, false)),
    rotina("pos-bike", DEPOIS, "Depois de pedalar", "Abre o quadril e devolve a postura", "bike", EST,
      e("flexor-quadril"), e("alongamento-quadriceps"), e("alongamento-gluteo"), e("alongamento-posterior"), e("alongamento-peito"), e("torcao-coluna")),
    rotina("pos-superiores", DEPOIS, "Depois de treinar superiores", "Peito, costas, braços e pescoço", "academia", EST,
      e("alongamento-peito"), e("alongamento-triceps"), e("alongamento-dorsal", 30, false), e("alongamento-pescoco", 20), e("alongamento-antebraco", 30, false)),
    rotina("pos-inferiores", DEPOIS, "Depois de treinar pernas", "Quadríceps, posterior, glúteo e adutores", "academia", EST,
      e("alongamento-quadriceps"), e("alongamento-posterior"), e("alongamento-gluteo"), e("alongamento-adutores", 40, false), e("alongamento-panturrilha"), e("postura-crianca", 45, false)),
    rotina("pos-luta", DEPOIS, "Depois da luta", "Pescoço, quadril, lombar e antebraços", "luta", EST,
      e("alongamento-pescoco", 20), e("alongamento-peito"), e("alongamento-adutores", 40, false), e("alongamento-gluteo"), e("abraco-joelhos", 40, false), e("alongamento-antebraco", 30, false)),
    rotina("pos-geral", DEPOIS, "Volta à calma completa", "Depois de qualquer treino", "mobilidade", EST,
      e("postura-crianca", 40, false), e("flexor-quadril"), e("alongamento-posterior"), e("alongamento-peito"), e("torcao-coluna"), e("abraco-joelhos", 40, false)),
    rotina("mob-diaria", MOBILIDADE, "Mobilidade diária · 10 min", "O básico para o corpo todo", "mobilidade", DIN,
      r("gato-camelo", "10"), r("maior-alongamento", "5 cada lado"), r("rotacao-toracica", "8 cada lado"), t("circulos-quadril", 40), r("inchworm", "5"), e("postura-crianca", 45, false)),
    rotina("mob-escritorio", MOBILIDADE, "Postura & escritório", "Pescoço, ombros e quadril depois de horas sentado", "mobilidade", DIN,
      e("alongamento-pescoco", 20), t("circulos-ombro", 30), r("abertura-peito-dinamica", "12"), e("alongamento-peito"), e("alongamento-lateral", 20), e("torcao-coluna", 20), e("flexor-quadril")),
    rotina("mob-quadril", MOBILIDADE, "Quadril destravado", "Para agachar melhor e aliviar a lombar", "mobilidade", DIN,
      t("circulos-quadril", 40), r("spider", "5 cada lado"), r("maior-alongamento", "5 cada lado"), e("flexor-quadril", 40), e("alongamento-gluteo", 40), e("alongamento-adutores", 45, false), r("ponte-gluteo", "12")),
    rotina("mob-ombros", MOBILIDADE, "Ombros saudáveis", "Amplitude e estabilidade das escápulas", "mobilidade", DIN,
      t("circulos-ombro", 30), r("band-pull-apart", "15"), r("rotacao-externa", "12 cada lado"), r("rotacao-toracica", "8 cada lado"), e("alongamento-peito"), e("alongamento-dorsal", 30, false)),
    rotina("mob-coluna", MOBILIDADE, "Coluna & lombar", "Movimento suave para costas tensas", "mobilidade", DIN,
      r("gato-camelo", "10"), e("abraco-joelhos", 40, false), r("dead-bug", "8 cada lado"), e("torcao-coluna"), r("rotacao-toracica", "8 cada lado"), e("postura-crianca", 60, false)),
    rotina("mob-dormir", MOBILIDADE, "Antes de dormir", "Relaxe o corpo e desacelere a respiração", "mobilidade", "Inspire em 4 s, solte o ar em 6 s. Luz baixa, sem pressa.",
      e("postura-crianca", 60, false), e("abraco-joelhos", 45, false), e("alongamento-gluteo", 40), e("torcao-coluna", 40), e("alongamento-adutores", 60, false)),
    rotina("mob-acordar", MOBILIDADE, "Ao acordar", "5 minutos para tirar a rigidez da manhã", "mobilidade", DIN,
      e("alongamento-lateral", 20), r("gato-camelo", "8"), r("moinho", "10"), t("circulos-quadril", 30), t("circulos-ombro", 30)),
    rotina("mob-tornozelos", MOBILIDADE, "Tornozelos & pés", "Base firme para correr, saltar e se equilibrar", "mobilidade", DIN,
      t("circulos-tornozelo", 40, "20 s cada pé"), e("alongamento-panturrilha", 30), r("panturrilha-pe", "15", "Lento, 2 s em cima"), t("equilibrio-unipodal", 60, "30 s cada perna")),
  ];
  const Rotinas = {
    ANTES, DEPOIS, MOBILIDADE, CATEGORIAS: [ANTES, DEPOIS, MOBILIDADE], todas: TODAS,
    porId: id => TODAS.find(x => x.id === id) || null,
    recomendadas(m, p = null) {
      let ids;
      switch (m?.id) {
        case "corrida": ids = ["pre-corrida", "pos-corrida", "mob-tornozelos"]; break;
        case "bike": ids = ["pre-bike", "pos-bike", "mob-quadril"]; break;
        case "academia": case "casa_corpo": case "casa_elastico": ids = ["pre-inferiores", "pre-superiores", "pos-inferiores", "pos-superiores"]; break;
        case "luta": ids = ["bjj", "judo", "wrestling"].includes(p?.lutaArte) ? ["pre-luta-solo", "pos-luta", "mob-quadril"] : ["pre-luta-pe", "pos-luta", "mob-ombros"]; break;
        case "atleta": ids = p?.atletaEsporte === "raquete" ? ["pre-raquete", "pos-geral", "mob-ombros"] : p?.atletaEsporte === "resistencia" ? ["pre-natacao", "pre-corrida", "pos-corrida"] : ["pre-coletivos", "pos-inferiores", "mob-quadril"]; break;
        case "hiit": ids = ["pre-hiit", "pos-geral", "mob-diaria"]; break;
        case "hibrido": ids = [p?.cardioHibrido === "bike" ? "pre-bike" : "pre-corrida", "pre-inferiores", "pos-geral"]; break;
        case "longevidade": ids = ["pre-caminhada", "mob-acordar", "mob-tornozelos"]; break;
        default: ids = ["mob-diaria", "mob-escritorio", "mob-dormir"];
      }
      return ids.map(id => this.porId(id)).filter(Boolean);
    },
  };

  // ------------------------------------------------------------------ datas e progresso
  const Datas = {
    diaSemana: d => mod(d + 3, 7) + 1,
    segunda(d) { return d - (this.diaSemana(d) - 1); },
    hoje() { const n = new Date(); return Math.floor(Date.UTC(n.getFullYear(), n.getMonth(), n.getDate()) / 86400000); },
    data: d => new Date(d * 86400000),
  };
  const epley = (kg, reps) => (reps <= 1 ? kg : kg * (1 + reps / 30));
  const fmtKg = kg => (kg % 1 === 0 ? String(Math.trunc(kg)) : kg.toFixed(1).replace(".", ","));
  const Progresso = {
    semanaAtual: (inicio, hoje, total) => coerce(Math.trunc(Math.max(hoje - inicio, 0) / 7) + 1, 1, Math.max(total, 1)),
    feitas: (regs, semana) => new Set(regs.filter(r => r.semana === semana).map(r => r.sessaoIdx)),
    sequenciaSemanas(regs, plano, semanaAtual) {
      const completa = w => { const s = plano.semanas[w - 1]; return s ? this.feitas(regs, w).size >= s.sessoes.length : false; };
      let w = completa(semanaAtual) ? semanaAtual : semanaAtual - 1, n = 0;
      while (w >= 1 && completa(w)) { n++; w--; }
      return n;
    },
    sequenciaDias(regs, hoje) {
      const dias = new Set(regs.map(r => r.epochDay));
      let d = dias.has(hoje) ? hoje : hoje - 1, n = 0;
      while (dias.has(d)) { n++; d--; }
      return n;
    },
    minutosPorSemana(regs, hoje, semanas = 8) {
      const seg = Datas.segunda(hoje), out = [];
      for (let k = semanas - 1; k >= 0; k--) { const ini = seg - 7 * k; out.push([ini, Math.trunc(regs.filter(r => r.epochDay >= ini && r.epochDay < ini + 7).reduce((a, r) => a + r.duracaoSeg, 0) / 60)]); }
      return out;
    },
    volumeKg: r => r.series.reduce((a, s) => a + s.kg * s.reps, 0),
    epley, fmtKg,
    recordes(regs) {
      const por = new Map();
      for (const r of regs) for (const s of r.series) {
        if (!(s.kg > 0 && s.reps > 0)) continue;
        const v = epley(s.kg, s.reps), atual = por.get(s.exId);
        if (!atual || v > atual.rm1) por.set(s.exId, { exId: s.exId, kg: s.kg, reps: s.reps, rm1: v, epochDay: r.epochDay });
      }
      return [...por.values()].sort((a, b) => b.epochDay - a.epochDay);
    },
    ultimas(regs, exId) {
      const r = [...regs].sort((a, b) => b.epochDay - a.epochDay).find(x => x.series.some(s => s.exId === exId));
      return r ? r.series.filter(s => s.exId === exId) : [];
    },
    sugestao(regs, item) {
      const ult = this.ultimas(regs, item.exId).filter(s => s.kg > 0);
      if (!ult.length || item.reps == null) return null;
      const ultimo = item.reps.split(/[–-]/).pop().trim();
      if (!/^\d+$/.test(ultimo)) return null;
      const topo = parseInt(ultimo, 10);
      const kg = Math.max(...ult.map(s => s.kg));
      if (ult.every(s => s.reps >= topo)) {
        const novo = Math.round(kg * 1.05 / 0.5) * 0.5;
        return `Você bateu o topo da faixa com ${fmtKg(kg)} kg. Tente ${fmtKg(Math.max(novo, kg + 1))} kg.`;
      }
      return `Última vez: ${ult.map(s => `${s.reps}×${fmtKg(s.kg)}`).join(" · ")} kg. Busque mais repetições.`;
    },
  };

  // ------------------------------------------------------------------ loja (estado + localStorage)
  const K = { RESP: "respostas", INICIO: "inicio", TROCAS: "trocas", REG: "registros", PESOS: "pesos", AJ: "ajustes" };
  class Loja {
    constructor(cat, arm, hoje = Datas.hoje) { this.cat = cat; this.arm = arm; this.hojeFn = hoje; this.gerador = new Gerador(cat); this.ouvintes = []; this.estado = this.carregar(); }
    hoje() { return this.hojeFn(); }
    ouvir(f) { this.ouvintes.push(f); }
    publicar() { this.estado = this.carregar(); this.ouvintes.forEach(f => f(this.estado)); }
    salvarRespostas(r, manterHistorico = true) {
      this.arm.gravar(K.RESP, JSON.stringify(Questionario.limpar(r)));
      this.arm.gravar(K.INICIO, String(Datas.segunda(this.hoje())));
      this.arm.gravar(K.TROCAS, null);
      if (!manterHistorico) this.arm.gravar(K.REG, null);
      this.publicar();
    }
    recomecarPlano() { this.arm.gravar(K.INICIO, String(Datas.segunda(this.hoje()))); this.publicar(); }
    registrar(r) { this.arm.gravar(K.REG, JSON.stringify([...this.estado.registros, r].map(registroJson))); this.publicar(); }
    apagarRegistro(r) { this.arm.gravar(K.REG, JSON.stringify(this.estado.registros.filter(x => x !== r).map(registroJson))); this.publicar(); }
    trocar(sessaoIdx, original, novo) {
      const tr = { ...this.estado.trocas }, chave = `${sessaoIdx}|${original}`;
      if (novo == null || novo === original) delete tr[chave]; else tr[chave] = novo;
      this.arm.gravar(K.TROCAS, JSON.stringify(tr)); this.publicar();
    }
    registrarPeso(kg) {
      const d = this.hoje();
      const l = [...this.estado.pesos.filter(p => p[0] !== d), [d, kg]].sort((a, b) => a[0] - b[0]);
      this.arm.gravar(K.PESOS, JSON.stringify(l)); this.publicar();
    }
    salvarAjustes(a) { this.arm.gravar(K.AJ, JSON.stringify({ som: a.som, vibracao: a.vibracao, tela: a.telaLigada })); this.publicar(); }
    apagarTudo() { Object.values(K).forEach(k => this.arm.gravar(k, null)); this.publicar(); }
    semanaAtual() { const e = this.estado; return Progresso.semanaAtual(e.inicio, this.hoje(), e.plano ? e.plano.semanas.length : 1); }
    sessaoDeHoje() {
      const p = this.estado.plano; if (!p) return null;
      const dia = Datas.diaSemana(this.hoje()), s = p.semanas[this.semanaAtual() - 1].sessoes, i = s.findIndex(x => x.diaSemana === dia);
      return i >= 0 ? [i, s[i]] : null;
    }
    proximaSessao() {
      const e = this.estado, p = e.plano; if (!p) return null;
      const w = this.semanaAtual(), feitas = Progresso.feitas(e.registros, w), dia = Datas.diaSemana(this.hoje()), s = p.semanas[w - 1].sessoes;
      const pend = s.map((v, i) => [i, v]).filter(([i]) => !feitas.has(i));
      const x = pend.find(([, v]) => v.diaSemana >= dia) || pend[0];
      return x || null;
    }
    carregar() {
      const ler = (k, f, padrao) => { try { const s = this.arm.ler(k); return s == null ? padrao : f(s); } catch { return padrao; } };
      const resp = ler(K.RESP, JSON.parse, {});
      const inicio = ler(K.INICIO, s => { const n = parseInt(s, 10); return isNaN(n) ? Datas.segunda(this.hoje()) : n; }, Datas.segunda(this.hoje()));
      const trocas = ler(K.TROCAS, JSON.parse, {});
      const registros = ler(K.REG, s => JSON.parse(s).map(registroDeJson), []);
      const pesos = ler(K.PESOS, JSON.parse, []);
      const aj = ler(K.AJ, s => { const o = JSON.parse(s); return { som: o.som !== false, vibracao: o.vibracao !== false, telaLigada: o.tela !== false }; }, { som: true, vibracao: true, telaLigada: true });
      const perfil = Object.keys(resp).length && Questionario.completo(resp) ? perfilDe(resp) : null;
      const plano = perfil ? this.aplicarTrocas(this.gerador.gerar(perfil), trocas) : null;
      return { respostas: resp, inicio, trocas, registros, pesos, ajustes: aj, perfil, plano, temPlano: !!plano };
    }
    aplicarTrocas(p, trocas) {
      if (!Object.keys(trocas).length) return p;
      return { ...p, semanas: p.semanas.map(s => ({ ...s, sessoes: s.sessoes.map((ses, i) => ({ ...ses, blocos: ses.blocos.map(b => ({ ...b, itens: b.itens.map(it => {
        const novo = trocas[`${i}|${it.exId}`];
        if (novo != null && this.cat.get(novo)) {
          const ex = this.cat.exigir(novo);
          if (ex.porTempo && it.reps != null) return { ...it, exId: novo, reps: null, trabalhoSeg: 40 };
          if (!ex.porTempo && it.reps == null && b.tipo === TB.PRINCIPAL) return { ...it, exId: novo, reps: "10–12", trabalhoSeg: null };
          return { ...it, exId: novo };
        }
        return it;
      }) })) })) })) };
    }
  }
  function registroJson(r) {
    const o = { d: r.epochDay, w: r.semana, i: r.sessaoIdx, t: r.titulo, tp: r.tipo, s: r.duracaoSeg, e: r.esforco, n: r.nota, x: r.series.map(s => [s.exId, s.reps, s.kg, s.seg || 0]) };
    if (r.fcMedia > 0) { o.fm = r.fcMedia; o.fx = r.fcMax; }
    if (r.fimMs > 0) o.f = r.fimMs;
    return o;
  }
  function registroDeJson(o) {
    return { epochDay: o.d, semana: o.w, sessaoIdx: o.i, titulo: o.t || "", tipo: o.tp || "", duracaoSeg: o.s || 0,
      series: (o.x || []).map(s => ({ exId: s[0], reps: s[1], kg: s[2], seg: s[3] || 0 })), esforco: o.e || 0, nota: o.n || "", fcMedia: o.fm || 0, fcMax: o.fx || 0, fimMs: o.f || 0 };
  }
  const armLocal = (prefixo = "forja.") => ({
    ler: k => { try { return localStorage.getItem(prefixo + k); } catch { return null; } },
    gravar: (k, v) => { try { if (v == null) localStorage.removeItem(prefixo + k); else localStorage.setItem(prefixo + k, v); } catch {} },
  });

  raiz.Forja = { Catalogo, Questionario, perfilDe, Gerador, Roteiro, Rotinas, Datas, Progresso, Loja, armLocal, TB, MODALIDADES, OBJETIVOS, NIVEIS, Modalidade, Objetivo, Nivel };
})(typeof window !== "undefined" ? window : globalThis);
