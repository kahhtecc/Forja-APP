// Forja · versão web. Mesmas telas, opções e regras do app Android/iPhone (ver app/src/main/java/com/forja/app/ui).
// O núcleo (questionário, gerador, rotinas, progresso, loja) vem de nucleo.js, tradução fiel do Kotlin.
"use strict";
const F = window.Forja;
const { Questionario, Roteiro, Rotinas, Datas, Progresso, TB } = F;

// ------------------------------------------------------------------ tema
const COR = {
  fundo: "#0E0D0C", sup1: "#161412", sup2: "#1E1B18", sup3: "#28241F", borda: "#35302A", texto: "#F2EBE0", texto2: "#A89E90", texto3: "#6E665C",
  brasa: "#FF5B22", brasaClara: "#FF8A50", ok: "#34D399", alerta: "#FBBF24", perigo: "#F43F5E",
};
const COR_MOD = { academia: COR.brasa, casa_corpo: "#F2B24C", casa_elastico: "#E879A6", corrida: "#34D399", bike: "#38BDF8", luta: "#F43F5E", atleta: "#A78BFA", hiit: "#FACC15", hibrido: "#FB923C", mobilidade: "#5EEAD4", longevidade: "#A3E635" };
const corMod = m => (m ? COR_MOD[m.id || m] || COR.brasa : COR.brasa);
const corTipo = (tipo, padrao) => ({ corrida: COR_MOD.corrida, bike: COR_MOD.bike, luta: COR_MOD.luta, hiit: COR_MOD.hiit, mobilidade: COR_MOD.mobilidade, cardio: "#7DD3FC", atleta: COR_MOD.atleta })[tipo] || padrao;
const corTema = id => COR_MOD[id] || COR_MOD.mobilidade;

// Ícones (traços no estilo Material Rounded)
const ICO = {
  voltar: "M15 18l-6-6 6-6", fechar: "M6 6l12 12M18 6L6 18", seta: "M5 12h14M13 6l6 6-6 6", play: "M8 5v14l11-7z", check: "M5 12.5l4.5 4.5L19 7",
  chevron: "M9 6l6 6-6 6", troca: "M7 7h11l-3-3M17 17H6l3 3", relogio: "M12 7v5l3 2M12 21a9 9 0 110-18 9 9 0 010 18z", busca: "M11 18a7 7 0 110-14 7 7 0 010 14zM16.5 16.5L21 21",
  mais: "M12 5v14M5 12h14", menos: "M5 12h14", repetir: "M17 2l4 4-4 4M3 11V9a3 3 0 013-3h15M7 22l-4-4 4-4M21 13v2a3 3 0 01-3 3H3", proximo: "M6 6l9 6-9 6zM18 6v12", anterior: "M18 6l-9 6 9 6zM6 6v12",
  pausa: "M8 5v14M16 5v14", trofeu: "M8 4h8v5a4 4 0 01-8 0zM4 5h4v2a3 3 0 01-3 3M20 5h-4v2a3 3 0 003 3M12 13v4M8 20h8", lixo: "M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3",
  alerta: "M12 3l10 18H2zM12 10v4M12 17.5v.5", lampada: "M9 18h6M10 21h4M12 3a6 6 0 00-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0012 3z", lua: "M20 14.5A8 8 0 019.5 4 8 8 0 1020 14.5z",
  editar: "M4 20h4L19 9l-4-4L4 16zM14 6l4 4", recomecar: "M4 12a8 8 0 108-8 8 8 0 00-6 2.7M4 4v4h4", sino: "M6 16V11a6 6 0 1112 0v5l2 2H4zM10 21h4", ciencia: "M9 3h6M10 3v6l-5 9a2 2 0 002 3h10a2 2 0 002-3l-5-9V3",
  escudo: "M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z", apagar: "M4 7h16M6 7l1 13h10l1-13M9 7V4h6v3M10 11l4 4M14 11l-4 4", externo: "M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 01-1 1H5a1 1 0 01-1-1V7a1 1 0 011-1h5",
  coracao: "M12 20s-7-4.5-7-10a4 4 0 017-2.6A4 4 0 0119 10c0 5.5-7 10-7 10z", bluetooth: "M7 7l10 10-5 4V3l5 4L7 17", calendario: "M4 6h16v14H4zM4 10h16M8 3v4M16 3v4", peso: "M5 8h14l-2 12H7zM9 8a3 3 0 016 0",
  instalar: "M12 3v12M7 10l5 5 5-5M5 21h14", grafico: "M4 20V10M10 20V4M16 20v-7M22 20H2",
  // abas
  fogo: "M12 3c1 4 5 5.5 5 10a5 5 0 01-10 0c0-2.5 1.5-3.5 2-5 .6 1.5 1.5 2 2.5 2C11 7.5 11 5 12 3z", plano: "M4 5h16v15H4zM4 9h16M9 9v11", alongar: "M12 6a2 2 0 100-4 2 2 0 000 4zM4 9l8 2 8-2M12 11v4l-4 6M12 15l4 6",
  haltere: "M3 9v6M6 7v10M18 7v10M21 9v6M6 12h12", evolucao: "M3 17l6-6 4 4 8-8M15 7h6v6",
};
const ico = (n, tam = 22, cor = "currentColor", larg = 2) => `<svg width="${tam}" height="${tam}" viewBox="0 0 24 24" fill="none" stroke="${cor}" stroke-width="${larg}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="${ICO[n]}"/></svg>`;
const ICO_MOD = { academia: "haltere", casa_corpo: "fogo", casa_elastico: "repetir", corrida: "evolucao", bike: "relogio", luta: "escudo", atleta: "trofeu", hiit: "fogo", hibrido: "troca", mobilidade: "alongar", longevidade: "coracao" };
const icoMod = m => ICO_MOD[m?.id || m] || "haltere";

// ------------------------------------------------------------------ utilidades
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const $app = document.getElementById("app"), $abas = document.getElementById("abas");
const PT = "pt-BR";
const DIAS = Questionario.DIAS_NOMES;
const plural = (n, um, varios) => `${n} ${n === 1 ? um : varios}`;
const relogio = seg => (seg >= 60 ? `${Math.floor(seg / 60)}:${String(seg % 60).padStart(2, "0")}` : `${seg}`);
const fmtData = (d, o) => new Intl.DateTimeFormat(PT, { timeZone: "UTC", ...o }).format(Datas.data(d));
const EQUIP_NOMES = { corpo: "Peso do corpo", elastico: "Elástico", halter: "Halteres", barra: "Barra", maquina: "Máquina", polia: "Polia", kettlebell: "Kettlebell", banco: "Banco", barra_fixa: "Barra fixa", bola: "Medicine ball", corda: "Corda", rolo: "Rolo", saco: "Saco de pancada", bike: "Bike", esteira: "Esteira", rua: "Rua", pista: "Pista", outro: "Outros" };
const TIPO_NOMES = { forca: "Força", cardio: "Cardio", pliometria: "Pliometria", potencia: "Potência", mobilidade: "Mobilidade", tecnica: "Técnica" };
const PRIVACIDADE = "privacidade.html";

// Ações: cada render registra funções e o HTML guarda só o índice (data-a); um ouvinte delegado dispara.
let ACOES = [];
const a = fn => { ACOES.push(fn); return `data-a="${ACOES.length - 1}"`; };
document.addEventListener("click", ev => {
  const el = ev.target.closest("[data-a]");
  if (!el) return;
  const fn = ACOES[+el.dataset.a];
  if (fn) { ev.preventDefault(); fn(ev, el); }
});

// ------------------------------------------------------------------ componentes
let ANIM = {};
function demo(ex, o = {}) {
  const cor = o.cor || COR.brasa, cantos = o.cantos ?? 20, animar = o.animar !== false;
  const estilo = `border-radius:${cantos}px;--c:${cor};${o.estilo || ""}`;
  if (!ex) return `<div class="demo ${o.cls || ""}" style="${estilo}"></div>`;
  if (ANIM[ex.id]) {
    const rot = `Animação 3D de ${esc(ex.nome)}`;
    const midia = animar
      ? `<video src="video3d/${ex.id}.mp4" poster="video3d/${ex.id}.webp" autoplay muted loop playsinline disablepictureinpicture preload="metadata" aria-label="${rot}"></video>`
      : `<img src="video3d/${ex.id}.webp" alt="${rot}" loading="lazy" decoding="async">`;
    return `<div class="demo a3d ${o.cls || ""}" style="${estilo}">${midia}</div>`;
  }
  return `<div class="demo ${o.cls || ""}" style="${estilo}"><div class="sem">${esc(ex.nome[0])}</div></div>`;
}
const etq = (t, cor = COR.brasa, o = {}) => `<span class="etq${o.cheia ? " cheia" : ""}${o.foto ? " foto" : ""}" style="--c:${cor}">${o.ico ? ico(o.ico, 15) : ""}${esc(t)}</span>`;
const rotulo = (t, cor) => `<div class="rotulo"${cor ? ` style="color:${cor}"` : ""}>${esc(t)}</div>`;
const secao = (t, acao, fn) => `<div class="secao"><h3>${esc(t)}</h3>${acao ? `<button ${a(fn)}>${esc(acao)}</button>` : ""}</div>`;
const btn = (t, fn, o = {}) => `<button class="btn${o.cls ? " " + o.cls : ""}" ${o.cor && o.cor !== COR.brasa ? `style="--c:${o.cor}" data-cor` : ""} ${o.desativado ? "disabled" : a(fn)}>${o.ico ? ico(o.ico, 20) : ""}${esc(t)}</button>`;
const btn2 = (t, fn, o = {}) => `<button class="btn2${o.cls ? " " + o.cls : ""}" ${a(fn)}${o.cor ? ` style="color:${o.cor}"` : ""}>${o.ico ? ico(o.ico, 18) : ""}${esc(t)}</button>`;
const btnIco = (n, rot, fn, o = {}) => `<button class="ico${o.cls ? " " + o.cls : ""}" aria-label="${esc(rot)}" ${a(fn)} style="${o.tam ? `width:${o.tam}px;height:${o.tam}px;` : ""}${o.fundo ? `background:${o.fundo};` : ""}${o.cor ? `color:${o.cor};` : ""}">${ico(n, o.icoTam || 22)}</button>`;
const icoRedondo = (n, cor, tam = 40) => `<span class="icoR" style="--c:${cor};width:${tam}px;height:${tam}px">${ico(n, Math.round(tam * 0.5), cor)}</span>`;
const estat = (v, r, cor = COR.texto) => `<div class="estat"><b class="num" style="color:${cor}">${esc(v)}</b><span>${esc(r)}</span></div>`;
function anel(prog, tam, cor, esp, dentro) {
  const r = (tam - esp) / 2, c = 2 * Math.PI * r, p = Math.max(0, Math.min(1, prog || 0));
  return `<div class="anel" style="width:${tam}px;height:${tam}px"><svg viewBox="0 0 ${tam} ${tam}"><circle cx="${tam / 2}" cy="${tam / 2}" r="${r}" stroke="${COR.sup3}" stroke-width="${esp}" fill="none"/>` +
    `<circle class="arco" cx="${tam / 2}" cy="${tam / 2}" r="${r}" stroke="${cor}" stroke-width="${esp}" fill="none" stroke-linecap="round" stroke-dasharray="${c}" stroke-dashoffset="${c * (1 - p)}"/></svg><div class="dentro">${dentro}</div></div>`;
}
const aviso = t => `<div class="aviso">${ico("alerta", 20, COR.alerta)}<span>${esc(t)}</span></div>`;
const topo = (titulo, sub, voltar) => `<div class="topoT">${btnIco("voltar", "Voltar", voltar)}<div class="cresce">${rotulo(sub)}<h1>${esc(titulo)}</h1></div></div>`;
const linhaAcao = (n, t, sub, fn, cor = COR.brasa) => `<button class="cartao linhaAcao" ${a(fn)}>${icoRedondo(n, cor)}<div class="cresce"><b${cor === COR.perigo ? ` style="color:${COR.perigo}"` : ""}>${esc(t)}</b><small>${esc(sub)}</small></div>${ico("chevron", 20, COR.texto3)}</button>`;
const alternar = (t, v, fn) => `<label class="alternar"><span>${esc(t)}</span><input type="checkbox" role="switch" ${v ? "checked" : ""} ${a(fn)}><i></i></label>`;
function dialogo(titulo, texto, botoes) {
  const d = document.createElement("div");
  d.className = "dialogo"; d.setAttribute("role", "dialog"); d.setAttribute("aria-modal", "true");
  d.innerHTML = `<div class="caixa"><h3>${esc(titulo)}</h3><p class="mut">${esc(texto)}</p><div class="botoes">${botoes.map((b, i) => `<button data-i="${i}" style="color:${b.cor || COR.texto2}">${esc(b.t)}</button>`).join("")}</div></div>`;
  d.addEventListener("click", ev => {
    const b = ev.target.closest("[data-i]");
    if (b) { d.remove(); botoes[+b.dataset.i].fn?.(); } else if (ev.target === d) d.remove();
  });
  document.body.appendChild(d);
  d.querySelector("button")?.focus();
}
let avisoTimer;
function avisar(t) {
  let el = document.getElementById("toast");
  if (!el) { el = document.createElement("div"); el.id = "toast"; el.setAttribute("role", "status"); document.body.appendChild(el); }
  el.textContent = t; el.classList.add("on");
  clearTimeout(avisoTimer); avisoTimer = setTimeout(() => el.classList.remove("on"), 3500);
}

// ------------------------------------------------------------------ navegação
const ABAS = [["hoje", "Hoje", "fogo"], ["plano", "Plano", "plano"], ["mob", "Mobilidade", "alongar"], ["ex", "Exercícios", "haltere"], ["prog", "Progresso", "evolucao"]];
let loja, cat, fontes = [], aba = "hoje", pilha = [{ r: "abas" }], treino = null, tick = null, quiz = null;
const atual = () => pilha[pilha.length - 1];
function ir(rota) { atual().y = window.scrollY; pilha.push(rota); render(true); }
function voltar() {
  if (pilha.length > 1) { pilha.pop(); render(false); return true; }
  if (aba !== "hoje") { aba = "hoje"; render(true); return true; }
  return false;
}
function raiz(rota) { pilha = [rota]; render(true); }
function substituir(rota) { pilha[pilha.length - 1] = rota; render(true); }
window.addEventListener("popstate", () => { if (!voltar()) history.back(); else history.pushState(null, ""); });

function render(topoPagina) {
  ACOES = [];
  const r = atual();
  if (r.r !== "treino" && tick) { clearInterval(tick); tick = null; }
  const temPlano = loja.estado.temPlano;
  if (!temPlano && !["quiz", "fontes"].includes(r.r)) { pilha = [{ r: "quiz" }]; return render(true); }
  let html;
  switch (r.r) {
    case "abas": html = aba === "hoje" ? telaHoje() : aba === "plano" ? telaPlano() : aba === "mob" ? telaMobilidade() : aba === "ex" ? telaBiblioteca() : telaProgresso(); break;
    case "quiz": html = telaQuiz(); break;
    case "perfil": html = telaPerfil(); break;
    case "fontes": html = telaFontes(); break;
    case "sessao": html = telaSessao(r.w, r.i); break;
    case "rotina": html = telaRotina(r.id); break;
    case "treino": html = telaTreino(r); break;
    case "exercicio": html = telaExercicio(r.id, r.troca); break;
    case "video": html = telaVideo(r.id); break;
    case "concluido": html = telaConcluido(r.reg); break;
    default: html = "";
  }
  $app.className = "tela-" + r.r;
  $app.innerHTML = html;
  const mostrarAbas = r.r === "abas";
  $abas.hidden = !mostrarAbas;
  if (mostrarAbas) $abas.innerHTML = `<nav aria-label="Seções">${ABAS.map(([id, nome, i]) => `<button ${a(() => { aba = id; render(true); })} aria-current="${id === aba ? "page" : "false"}">${ico(i, 22)}<span>${nome}</span></button>`).join("")}</nav>`;
  window.scrollTo(0, topoPagina ? 0 : r.y || 0);
  if (r.r === "treino") montarTreino();
  ligarEntradas();
  wakeLock(r.r === "treino" && loja.estado.ajustes.telaLigada);
}

// ------------------------------------------------------------------ questionário (boas-vindas, perguntas, gerando)
function telaQuiz() {
  if (!quiz) quiz = { resp: { ...loja.estado.respostas }, etapa: Object.keys(loja.estado.respostas).length ? 0 : -1, gerando: 0 };
  const podeVoltar = loja.estado.temPlano;
  const sair = () => { quiz = null; voltar(); };
  if (quiz.gerando) return telaGerando();
  if (quiz.etapa < 0) return telaBoasVindas(podeVoltar ? sair : null);
  const resp = quiz.resp;
  const vis = Questionario.visiveis(resp);
  const idx = Math.min(Math.max(quiz.etapa, 0), vis.length - 1);
  const p = vis[idx];
  if (p.tipo === "NUMERO" && !p.opcional && !(resp[p.id] || []).length) resp[p.id] = [String(p.padrao ?? p.min)];
  if (p.tipo === "DIAS") { const n = numR(resp, "dias") ?? 3; if ((resp[p.id] || []).length !== n) resp[p.id] = Questionario.diasSugeridos(n).map(String); }
  const avancar = () => { if (idx >= vis.length - 1) { quiz.gerando = 1; render(true); } else { quiz.etapa = idx + 1; render(true); } };
  const voltarQ = () => { if (idx === 0) { if (podeVoltar) sair(); else { quiz.etapa = -1; render(true); } } else { quiz.etapa = idx - 1; render(true); } };
  const pular = p.opcional && !(resp[p.id] || []).length;
  return `<div class="quiz">
    <div class="quizTopo">${btnIco("voltar", "Voltar", voltarQ)}<div class="cresce"><div class="linha">${rotulo(p.secao, COR.brasa)}<span class="cresce"></span>${rotulo(`${idx + 1} / ${vis.length}`)}</div>
      <div class="barra" style="margin-top:8px"><i style="width:${((idx + 1) / vis.length) * 100}%"></i></div></div></div>
    <div class="quizCorpo"><h1>${esc(p.titulo)}</h1>${p.subtitulo ? `<p class="mut" style="margin-top:10px">${esc(p.subtitulo)}</p>` : ""}<div style="margin-top:24px">${corpoPergunta(p, resp, avancar)}</div></div>
    <div class="fixo">${btn(idx === vis.length - 1 ? "Montar minha rotina" : pular ? "Pular" : "Continuar", avancar, { ico: "seta", desativado: !Questionario.respondida(p, resp) })}</div>
  </div>`;
}
const numR = (r, id) => { const v = (r[id] || [])[0]; return v != null && /^\d+$/.test(v) ? parseInt(v, 10) : null; };

function corpoPergunta(p, resp, avancar) {
  const atualV = resp[p.id] || [];
  const mudar = v => { quiz.resp = { ...resp, [p.id]: v }; render(false); };
  const escolhaUnica = v => { quiz.resp = { ...resp, [p.id]: [v] }; render(false); setTimeout(() => { if (quiz && !quiz.gerando) avancar(); }, 260); };
  switch (p.tipo) {
    case "UNICA":
      if (p.id === "minutos") return `<div class="pilulas">${p.opcoes.map(o => `<button class="pilula" aria-pressed="${atualV.includes(o.valor)}" ${a(() => escolhaUnica(o.valor))}>${esc(o.titulo)}</button>`).join("")}</div>`;
      return `<div class="pilha" style="gap:10px">${p.opcoes.map(o => {
        const m = p.id === "modalidade" ? o.valor : null, cor = m ? corMod(m) : COR.brasa;
        return cartaoOpcao(o, atualV.includes(o.valor), false, cor, m ? icoMod(m) : null, () => escolhaUnica(o.valor));
      }).join("")}</div>`;
    case "MULTIPLA":
      return `<div class="pilha" style="gap:10px">${p.id === "parq" ? aviso("Qualquer “sim” não impede o treino, mas pede conversa com um médico antes de aumentar a intensidade.") : ""}${p.opcoes.map(o => {
        const marcado = atualV.includes(o.valor);
        return cartaoOpcao(o, marcado, true, COR.brasa, null, () => mudar(marcado ? atualV.filter(x => x !== o.valor) : o.valor === p.exclusiva ? [o.valor] : [...atualV.filter(x => x !== p.exclusiva), o.valor]));
      }).join("")}</div>`;
    case "NUMERO": {
      const valor = numR(resp, p.id), v = valor ?? p.padrao ?? p.min;
      const set = n => {
        const r = { ...resp, [p.id]: n == null ? [] : [String(n)] };
        if (p.id === "dias" && n != null) r.dias_semana = Questionario.diasSugeridos(n).map(String);
        quiz.resp = r; render(false);
      };
      const vazio = valor == null && p.opcional;
      const dica = p.id === "dias" ? ({ 2: "Ótimo para começar e manter.", 3: "O ponto ideal para a maioria.", 4: "Permite dividir em superiores e inferiores.", 5: "Volume alto — durma bem." })[v] || "Para quem já tem rotina consolidada." : null;
      return `<div class="seletorNum">
        <div class="linha" style="justify-content:center;gap:22px">${btnIco("menos", "Diminuir", () => set(Math.max(v - p.passo, p.min)), { tam: 58 })}
          <div style="width:150px;text-align:center"><div class="numero${vazio ? " vazio" : ""}">${vazio ? "—" : v}</div>${rotulo(p.unidade, COR.brasa)}</div>
          ${btnIco("mais", "Aumentar", () => set(Math.min(v + p.passo, p.max)), { tam: 58 })}</div>
        <input type="range" min="${p.min}" max="${p.max}" step="${p.passo}" value="${v}" data-in="num" aria-label="${esc(p.titulo)}">
        ${dica ? `<p class="mut" style="text-align:center;margin-top:12px">${dica}</p>` : ""}
        ${p.opcional && valor != null ? `<button class="limpar" ${a(() => set(null))}>Limpar</button>` : ""}</div>`;
    }
    case "DIAS": {
      const n = numR(resp, "dias") ?? 3;
      return `<div class="diasSel">${DIAS.map((nome, i) => {
        const v = String(i + 1), sel = atualV.includes(v);
        return `<button aria-pressed="${sel}" aria-label="${nome}${sel ? ", selecionado" : ""}" ${a(() => {
          const novo = sel ? atualV.filter(x => x !== v) : atualV.length < n ? [...atualV, v] : [...atualV.slice(1), v];
          mudar(novo.sort((x, y) => x - y));
        })}>${nome}</button>`;
      }).join("")}</div>
        <p style="margin-top:16px;font-weight:800;color:${atualV.length === n ? COR.ok : COR.texto2}">${atualV.length} de ${n} dias escolhidos</p>
        <p class="peq mut3" style="margin-top:8px">Dica: deixe pelo menos um dia de descanso entre treinos pesados do mesmo grupo.</p>`;
    }
    case "TEXTO":
      return `<input type="text" class="campoNome" maxlength="24" placeholder="Seu nome" value="${esc(atualV[0] || "")}" data-in="nome" autocomplete="given-name" autocapitalize="words" enterkeyhint="done">`;
  }
  return "";
}
function cartaoOpcao(o, sel, multipla, cor, icone, fn) {
  return `<button class="opc${multipla ? " multi" : ""}" style="--c:${cor}" aria-pressed="${sel}" ${a(fn)}>${icone ? icoRedondo(icone, cor, 42) : ""}
    <span class="cresce"><b>${esc(o.titulo)}</b>${o.descricao ? `<small>${esc(o.descricao)}</small>` : ""}</span><span class="marca">${sel ? ico("check", 16, COR.fundo, 3) : ""}</span></button>`;
}

function telaBoasVindas(cancelar) {
  return `<div class="boas">
    <div class="mosaico"><img src="img/agachamento-barra_1.webp" alt=""><div class="col"><img src="img/swing_1.webp" alt=""><img src="img/corrida-leve_1.webp" alt=""></div></div>
    <div class="boasTexto"><div class="linhaBrasa" style="width:56px"></div>
      <div class="marcaForja">FORJA</div><h2 style="color:${COR.brasa}">Treino sob medida.</h2>
      <p class="mut" style="margin-top:14px">Responda algumas perguntas e receba uma rotina completa — musculação, casa, corrida, bike, lutas, atletas, mobilidade e mais — com vídeo de cada exercício.</p>
      <div style="margin-top:24px">${btn("Montar minha rotina", () => { quiz.etapa = 0; render(true); }, { ico: "seta" })}</div>
      ${cancelar ? `<div style="margin-top:10px">${btn2("Cancelar", cancelar, { cls: "largo" })}</div>` : ""}
      <p class="peq mut3" style="text-align:center;margin-top:8px">Leva cerca de 2 minutos · baseado em diretrizes do ACSM, OMS e NSCA</p></div></div>`;
}

function telaGerando() {
  const passos = ["Analisando seu perfil", "Aplicando a triagem de segurança", "Escolhendo os exercícios", "Ajustando volume e intensidade", "Organizando as semanas"];
  let plano = null;
  try { plano = new F.Gerador(cat).gerar(F.perfilDe(quiz.resp)); } catch (e) { console.error(e); }
  const feito = Math.min(quiz.gerando - 1, passos.length);
  if (feito < passos.length) setTimeout(() => { if (quiz?.gerando) { quiz.gerando++; render(false); } }, feito === 0 ? 300 : 430);
  const cor = corMod(plano?.modalidade);
  const pronto = () => { loja.salvarRespostas(quiz.resp); quiz = null; aba = "hoje"; raiz({ r: "abas" }); };
  return `<div class="gerando">${anel(feito / passos.length, 96, cor, 8, ico(icoMod(plano?.modalidade), 38, cor))}
    <h1 style="margin-top:26px">${feito < passos.length ? "Forjando sua rotina…" : "Sua rotina está pronta"}</h1>
    <div class="pilha" style="gap:12px;margin-top:18px">${passos.map((s, i) => `<div class="linha"><span class="bolinha${i < feito ? " ok" : ""}">${i < feito ? ico("check", 14, COR.fundo, 3) : ""}</span><span style="color:${i < feito ? COR.texto : COR.texto3}">${s}</span></div>`).join("")}</div>
    ${feito >= passos.length && plano ? `<div class="cartao" style="margin-top:22px">${etq(plano.modalidade.nome, cor, { ico: icoMod(plano.modalidade) })}<h2 style="margin-top:12px">${esc(plano.nome)}</h2>
      <p class="peq mut" style="margin-top:6px">${esc(plano.resumo)}</p><b class="peq" style="display:block;margin-top:12px;color:${cor}">${esc(plano.metaSemanal)}</b></div>
      ${plano.alertas.map(t => `<div style="margin-top:10px">${aviso(t)}</div>`).join("")}
      <div style="margin-top:24px">${btn("Ver meu plano", pronto, { ico: "seta" })}</div>` : ""}</div>`;
}

// ------------------------------------------------------------------ hoje
const capaSessao = s => { const b = s.blocos.find(x => x.tipo !== TB.AQUECIMENTO) || s.blocos[0]; return b?.itens[0]?.exId; };
const nExercicios = s => s.blocos.filter(b => b.tipo !== TB.AQUECIMENTO && b.tipo !== TB.DESAQUECIMENTO).reduce((n, b) => n + b.itens.length, 0);

function telaHoje() {
  const e = loja.estado, plano = e.plano, hoje = loja.hoje(), w = loja.semanaAtual(), semana = plano.semanas[w - 1];
  const feitas = Progresso.feitas(e.registros, w), deHoje = loja.sessaoDeHoje(), proxima = loja.proximaSessao(), corM = corMod(plano.modalidade);
  const nome = e.perfil?.nome || "";
  const minutosSemana = Math.trunc(e.registros.filter(r => r.epochDay >= Datas.segunda(hoje)).reduce((s, r) => s + r.duracaoSeg, 0) / 60);
  const h = new Date().getHours(), saud = h < 12 ? "Bom dia" : h < 18 ? "Boa tarde" : "Boa noite";
  const [idx, ses] = deHoje || proxima || [null, null];
  let cartao;
  if (ses && idx != null && !feitas.has(idx)) cartao = heroi(ses, w, semana.fase, corM, deHoje?.[0] === idx, () => ir({ r: "treino", w, i: idx }), () => ir({ r: "sessao", w, i: idx }));
  else if (deHoje && feitas.has(deHoje[0])) cartao = `<div class="cartao" style="background:${COR.ok}14;border-color:${COR.ok}66"><div class="linha">${ico("check", 34, COR.ok, 2.5)}<div>${rotulo("Treino de hoje concluído", COR.ok)}<h2>${esc(deHoje[1].titulo)}</h2></div></div>
      <p class="peq mut" style="margin-top:10px">Recupere bem: hidratação, proteína e sono. ${proxima ? `O próximo é ${esc(proxima[1].titulo)} (${DIAS[proxima[1].diaSemana - 1]}).` : ""}</p>
      ${proxima ? `<div style="margin-top:14px">${btn2("Ver próximo treino", () => ir({ r: "sessao", w, i: proxima[0] }), { cls: "largo" })}</div>` : ""}</div>`;
  else {
    const fim = w >= plano.semanas.length;
    cartao = `<div class="cartao"><div class="linha">${icoRedondo("lua", corM, 48)}<div>${rotulo(fim ? "Plano concluído" : "Semana completa", corM)}<h2>${fim ? "Você fechou o ciclo!" : "Tudo feito por aqui"}</h2></div></div>
      <p class="peq mut" style="margin-top:10px">${fim ? "Refaça o questionário no perfil para gerar o próximo bloco com novos estímulos." : "Aproveite para descansar ou faça uma rotina de mobilidade."}</p>
      <div style="margin-top:14px">${btn2("Ver plano", () => { aba = "plano"; render(true); }, { cls: "largo" })}</div></div>`;
  }
  const seq = Progresso.sequenciaSemanas(e.registros, plano, w);
  const dicas = plano.dicas;
  return `<div class="pag">
    <div class="linha" style="padding:8px 0"><div class="cresce">${rotulo(fmtData(hoje, { weekday: "long", day: "numeric", month: "long" }))}<h1 class="umaLinha">${esc(nome ? `${saud}, ${nome}` : saud)}</h1></div>
      <button class="avatar" aria-label="Perfil e ajustes" ${a(() => ir({ r: "perfil" }))}>${esc((nome[0] || "F").toUpperCase())}</button></div>
    <div style="margin-top:14px">${cartao}</div>
    ${secao("Esta semana", "Ver plano", () => { aba = "plano"; render(true); })}
    ${faixa7Dias(semana.sessoes, feitas, Datas.diaSemana(hoje), corM, i => ir({ r: "sessao", w, i }))}
    <div class="duas" style="margin-top:14px"><div class="cartao p16"><div class="linha">${anel(feitas.size / semana.sessoes.length, 54, corM, 7, `<b class="peq">${feitas.size}/${semana.sessoes.length}</b>`)}<div><b>Treinos</b><small class="mut blk">semana ${w} de ${plano.semanas.length}</small></div></div></div>
      <div class="cartao p16">${estat(minutosSemana, "minutos ativos nesta semana")}</div></div>
    <div class="duas" style="margin-top:12px"><div class="cartao p16">${estat(seq, seq === 1 ? "semana completa seguida" : "semanas completas seguidas", corM)}</div><div class="cartao p16">${estat(e.registros.length, "treinos concluídos no total")}</div></div>
    ${secao("Mobilidade para você", "Ver todas", () => { aba = "mob"; render(true); })}
    <div class="trilho">${Rotinas.recomendadas(plano.modalidade, e.perfil).map(r => cartaoRotinaPequeno(r)).join("")}</div>
    ${plano.alertas.length ? `<div class="pilha" style="gap:8px;margin-top:18px">${plano.alertas.map(aviso).join("")}</div>` : ""}
    ${dicas.length ? `${secao("Dica do dia")}<div class="cartao"><div class="linha" style="align-items:flex-start">${icoRedondo("lampada", COR.alerta)}<p>${esc(dicas[hoje % dicas.length])}</p></div></div>` : ""}
  </div>`;
}

function heroi(s, w, fase, corM, ehHoje, comecar, detalhes) {
  const cor = corTipo(s.tipo, corM), capa = cat.get(capaSessao(s)), n = nExercicios(s);
  return `<div class="heroi" role="button" tabindex="0" aria-label="Detalhes do treino ${esc(s.titulo)}" ${a((ev) => { if (!ev.target.closest(".btn")) detalhes(); })}>
    ${capa ? demo(capa, { cls: "heroiDemo", cantos: 0, cor }) : ""}<div class="veu" style="--c:${cor}"></div>
    <div class="topoH">${etq(ehHoje ? "HOJE" : "PRÓXIMO", cor, { cheia: true })}${etq(`Semana ${w} · ${fase}`, COR.texto, { foto: true })}</div>
    <div class="baseH"><h1>${esc(s.titulo)}</h1><p class="mut" style="margin-top:6px">${esc(s.foco)}</p>
      <div class="linha" style="gap:8px;margin-top:14px">${etq(`${s.minutos} min`, cor, { ico: "relogio", foto: true })}${etq(plural(n, "exercício", "exercícios"), cor, { ico: "haltere", foto: true })}</div>
      <div style="margin-top:18px">${btn("Começar treino", comecar, { ico: "play", cor })}</div></div></div>`;
}

function faixa7Dias(sessoes, feitas, hojeDia, cor, fn) {
  let h = '<div class="dias">';
  for (let d = 1; d <= 7; d++) {
    const i = sessoes.findIndex(s => s.diaSemana === d), feita = feitas.has(i), ehHoje = d === hojeDia;
    const corS = i >= 0 ? corTipo(sessoes[i].tipo, cor) : COR.texto3;
    const fundo = feita ? corS : ehHoje ? COR.sup3 : COR.sup1;
    const borda = i >= 0 && !feita ? (ehHoje ? corS : corS + "99") : ehHoje ? COR.texto : COR.borda;
    const dentro = feita ? ico("check", 20, COR.fundo, 3) : i >= 0 ? `<b style="width:8px;height:8px;border-radius:50%;background:${corS}"></b>` : `<span style="color:${COR.texto3}">·</span>`;
    h += `<${i >= 0 ? "button" : "div"} class="dia${ehHoje ? " hoje" : ""}" ${i >= 0 ? `aria-label="${DIAS[d - 1]}: ${esc(sessoes[i].titulo)}" ${a(() => fn(i))}` : ""}><span>${DIAS[d - 1]}</span><i style="background:${fundo};border:${ehHoje ? 2 : 1}px solid ${borda}">${dentro}</i></${i >= 0 ? "button" : "div"}>`;
  }
  return h + "</div>";
}

function exRotina(r) { const its = r.sessao.blocos[0].itens; return cat.get((its[1] || its[0]).exId); }
function cartaoRotinaPequeno(r) {
  const cor = corTema(r.tema);
  return `<button class="rotinaP" ${a(() => ir({ r: "rotina", id: r.id }))}><div class="capa">${demo(exRotina(r), { cor, animar: false, cantos: 0 })}<span class="etqCapa">${etq(r.categoria, cor, { cheia: true })}</span></div>
    <div style="padding:14px"><b class="umaLinha">${esc(r.titulo)}</b><small class="mut duasLinhas">${Roteiro.minutos(r.sessao, cat)} min · ${esc(r.subtitulo)}</small></div></button>`;
}

// ------------------------------------------------------------------ plano
let semanaSel = null;
function telaPlano() {
  const e = loja.estado, plano = e.plano, atualW = loja.semanaAtual();
  if (semanaSel == null || semanaSel > plano.semanas.length) semanaSel = atualW;
  const sel = semanaSel, semana = plano.semanas[sel - 1], feitas = Progresso.feitas(e.registros, sel), corM = corMod(plano.modalidade);
  setTimeout(() => document.querySelector(".semanas")?.children[Math.max(0, atualW - 2)]?.scrollIntoView({ inline: "start", block: "nearest" }), 0);
  return `<div class="pag">
    <div style="padding:10px 0"><div class="linha" style="gap:8px">${etq(plano.modalidade.curto, corM, { ico: icoMod(plano.modalidade) })}${etq(plano.nivel.nome, COR.texto2)}</div>
      <h1 style="margin-top:12px">${esc(plano.nome)}</h1><p class="mut" style="margin-top:8px">${esc(plano.resumo)}</p><b class="peq" style="display:block;margin-top:6px;color:${corM}">${esc(plano.metaSemanal)}</b></div>
    <div class="trilho semanas" style="margin-top:14px">${plano.semanas.map((s, i) => {
      const n = i + 1, completa = Progresso.feitas(e.registros, n).size >= s.sessoes.length, ativo = n === sel;
      return `<button class="semana" style="--c:${corM};${n === atualW && !ativo ? `border-color:${corM}` : ""}" aria-pressed="${ativo}" aria-label="Semana ${n}" ${a(() => { semanaSel = n; render(false); })}>
        <span class="num">S${String(n).padStart(2, "0")}</span>${completa ? ico("check", 16, ativo ? COR.fundo : COR.ok, 3) : `<small>${esc(n === atualW ? "atual" : s.fase.slice(0, 10))}</small>`}</button>`;
    }).join("")}</div>
    <div class="cartao" style="margin-top:16px;background:${corM}12;border-color:${corM}4d">${rotulo(`Semana ${sel} · ${semana.fase}`, corM)}<p style="margin-top:6px">${esc(semana.nota)}</p></div>
    <div class="pilha" style="gap:12px;margin-top:14px">${semana.sessoes.map((s, i) => cartaoSessao(s, feitas.has(i), corM, () => ir({ r: "sessao", w: sel, i }))).join("")}</div>
    ${secao("Como progredir")}<div class="pilha" style="gap:10px">${plano.dicas.map(d => `<div class="linha" style="align-items:flex-start"><b class="ponto" style="background:${corM}"></b><p class="mut">${esc(d)}</p></div>`).join("")}</div>
  </div>`;
}
function cartaoSessao(s, feita, corM, fn) {
  const cor = corTipo(s.tipo, corM), n = nExercicios(s);
  return `<button class="cartao sessaoC" aria-label="${esc(s.titulo)}, ${DIAS[s.diaSemana - 1]}" ${a(fn)}><div class="mini72">${demo(cat.get(capaSessao(s)), { cor, animar: false, cantos: 16 })}${feita ? `<span class="feitaV">${ico("check", 30, "#fff", 3)}</span>` : ""}</div>
    <div class="cresce">${rotulo(`${DIAS[s.diaSemana - 1]} · ${s.foco}`, cor)}<h3 class="duasLinhas" style="margin-top:2px">${esc(s.titulo)}</h3><small class="mut blk" style="margin-top:4px">${s.minutos} min · ${plural(n, "exercício", "exercícios")}</small></div>${ico("chevron", 22, COR.texto3)}</button>`;
}

// ------------------------------------------------------------------ detalhe da sessão / rotina
function telaSessao(w, i) {
  const e = loja.estado, plano = e.plano, s = plano.semanas[w - 1]?.sessoes[i];
  if (!s) { setTimeout(voltar); return ""; }
  const corM = corMod(plano.modalidade), cor = corTipo(s.tipo, corM);
  const feito = [...e.registros].reverse().find(r => r.semana === w && r.sessaoIdx === i);
  const recs = Rotinas.recomendadas(plano.modalidade, e.perfil).slice(0, 2);
  const extra = recs.length ? `${secao("Preparo e volta à calma")}${recs.map(r => `<button class="cartao linhaAcao" style="margin-bottom:10px" ${a(() => ir({ r: "rotina", id: r.id }))}>${icoRedondo("alongar", corTema(r.tema))}<div class="cresce"><b>${esc(r.titulo)}</b><small>${Roteiro.minutos(r.sessao, cat)} min · ${esc(r.categoria)}</small></div>${ico("chevron", 20, COR.texto3)}</button>`).join("")}` : "";
  return detalheSessao(s, cor, `Semana ${w} · ${DIAS[s.diaSemana - 1]}`, feito ? `Concluído · ${Math.trunc(feito.duracaoSeg / 60)} min · esforço ${feito.esforco}/10` : null,
    (tipo, exId) => (tipo === TB.PRINCIPAL || tipo === TB.CIRCUITO ? { sessaoIdx: i, original: exId } : null), feito ? "Treinar de novo" : "Começar treino", () => ir({ r: "treino", w, i }), null, extra);
}
function telaRotina(id) {
  const r = Rotinas.porId(id); if (!r) { setTimeout(voltar); return ""; }
  return detalheSessao(r.sessao, corTema(r.tema), r.categoria, null, () => null, "Começar rotina", () => ir({ r: "treino", rotina: r.id }), r.subtitulo, "");
}
function detalheSessao(s, cor, cabecalho, avisoTxt, troca, rotuloBtn, comecar, sub, extra) {
  const capa = cat.get(capaSessao(s));
  return `<div class="detalhe"><div class="capaD">${capa ? demo(capa, { cantos: 0, cor }) : ""}<div class="veuD"></div>
      <div class="voltarFlut">${btnIco("voltar", "Voltar", voltar, { fundo: "rgba(14,13,12,.6)" })}</div>
      <div class="baseD">${rotulo(cabecalho, cor)}<h1 style="margin-top:4px">${esc(s.titulo)}</h1><p class="mut" style="margin-top:6px">${esc(sub ?? s.foco)}</p></div></div>
    <div class="pag"><div class="linha" style="gap:8px;padding:8px 0">${etq(`${Roteiro.minutos(s, cat)} min`, cor, { ico: "relogio" })}${etq(`${Roteiro.exerciciosDaSessao(s).length} exercícios`, cor)}</div>
      ${avisoTxt ? `<div class="okBox">${ico("check", 18, COR.ok, 3)}<b>${esc(avisoTxt)}</b></div>` : ""}
      ${s.blocos.map(b => `<div class="bloco"><div class="linha" style="padding:22px 0 4px"><span class="linhaBrasa" style="--c:${cor}"></span><h3 class="cresce">${esc(b.nome)}</h3>${b.voltas > 1 ? etq(`${b.voltas} voltas`, cor, { ico: "repetir" }) : ""}</div>
        ${b.nota ? `<p class="peq mut" style="margin-bottom:6px">${esc(b.nota)}</p>` : ""}
        ${b.itens.map(it => {
          const ex = cat.get(it.exId); if (!ex) return "";
          const t = troca(b.tipo, it.exId), pres = Roteiro.prescricao(it, b.tipo === TB.CIRCUITO, b.voltas);
          return `<button class="item" aria-label="${esc(ex.nome)}, ${esc(pres)}" ${a(() => ir({ r: "exercicio", id: ex.id, troca: t }))}><div class="mini">${demo(ex, { cor, animar: false, cantos: 14 })}</div>
            <div class="cresce"><b class="duasLinhas">${esc(ex.nome)}</b><small class="blk umaLinha"><b style="color:${cor}">${esc(pres)}</b>${it.intensidade ? `<span class="mut">  ·  ${esc(it.intensidade)}</span>` : ""}</small>${it.nota ? `<small class="mut3 blk duasLinhas">${esc(it.nota)}</small>` : ""}</div>
            ${t ? `<span title="Pode trocar" aria-label="Pode trocar">${ico("troca", 20, COR.texto3)}</span>` : ico("chevron", 20, COR.texto3)}</button>`;
        }).join("")}</div>`).join("")}
      ${extra}</div>
    <div class="fixo pag">${btn(rotuloBtn, comecar, { ico: "play", cor })}</div></div>`;
}

// ------------------------------------------------------------------ mobilidade
let filtroMob = "Todas";
function telaMobilidade() {
  const e = loja.estado, lista = Rotinas.todas.filter(r => filtroMob === "Todas" || r.categoria === filtroMob), recs = Rotinas.recomendadas(e.plano?.modalidade, e.perfil);
  const grupos = []; lista.forEach(r => { let g = grupos.find(x => x[0] === r.categoria); if (!g) grupos.push(g = [r.categoria, []]); g[1].push(r); });
  return `<div class="pag"><div style="padding:10px 0">${rotulo("Alongamento & mobilidade", COR_MOD.mobilidade)}<h1>Prepare o corpo,<br>recupere melhor.</h1>
      <p class="mut" style="margin-top:8px">Antes do esporte, movimento dinâmico. Depois do treino, alongamento estático de 20–30 s. E mobilidade para o dia a dia.</p></div>
    ${recs.length ? `${secao("Para o seu treino")}<div class="trilho">${recs.map(cartaoRotinaPequeno).join("")}</div>` : ""}
    <div class="trilho" style="margin-top:22px">${["Todas", ...Rotinas.CATEGORIAS].map(c => chip(c, c === filtroMob, () => { filtroMob = c; render(false); })).join("")}</div>
    ${grupos.map(([c, rs]) => `${secao(c)}<div class="pilha" style="gap:10px">${rs.map(r => {
      const cor = corTema(r.tema);
      return `<button class="cartao linhaRot" ${a(() => ir({ r: "rotina", id: r.id }))}><div class="mini76">${demo(exRotina(r), { cor, animar: false, cantos: 16 })}</div><div class="cresce">
        <div class="linha" style="gap:6px"><b class="ponto" style="background:${cor}"></b>${rotulo(`${Roteiro.minutos(r.sessao, cat)} min · ${r.sessao.blocos[0].itens.length} movimentos`, cor)}</div>
        <b class="umaLinha blk" style="margin-top:3px">${esc(r.titulo)}</b><small class="mut duasLinhas">${esc(r.subtitulo)}</small></div>${ico("chevron", 22, COR.texto3)}</button>`;
    }).join("")}</div>`).join("")}</div>`;
}
const chip = (t, sel, fn, cor = COR.brasa) => `<button class="chip" style="--c:${cor}" aria-pressed="${sel}" ${a(fn)}>${esc(t)}</button>`;

// ------------------------------------------------------------------ biblioteca
let busca = "", grupoSel = "Todos", semEquip = false;
function telaBiblioteca() {
  const termo = busca.trim().toLowerCase();
  const lista = cat.exercicios.filter(e => (grupoSel === "Todos" || e.grupo === grupoSel) && (!semEquip || e.equip.some(q => q === "corpo" || q === "elastico")) &&
    (!termo || e.nome.toLowerCase().includes(termo) || e.grupo.toLowerCase().includes(termo) || e.equip.some(q => (EQUIP_NOMES[q] || q).toLowerCase().includes(termo))));
  return `<div class="pag"><div style="padding:10px 0">${rotulo(`${cat.exercicios.length} exercícios com demonstração e vídeo`, COR.brasa)}<h1>Biblioteca</h1>
      <div class="buscaC" style="margin-top:14px">${ico("busca", 20, COR.texto3)}<input type="text" inputmode="search" enterkeyhint="search" placeholder="Buscar exercício, músculo ou equipamento" value="${esc(busca)}" data-in="busca" aria-label="Buscar exercício">${busca ? `<button aria-label="Limpar busca" ${a(() => { busca = ""; render(false); })}>${ico("fechar", 20, COR.texto3)}</button>` : ""}</div>
      <div class="trilho" style="margin-top:12px">${chip("Sem equipamento", semEquip, () => { semEquip = !semEquip; render(false); })}${["Todos", ...cat.grupos()].map(g => chip(g, g === grupoSel, () => { grupoSel = g; render(false); })).join("")}</div></div>
    ${lista.length ? `<div class="grade">${lista.map(e => `<button ${a(() => ir({ r: "exercicio", id: e.id }))}>${demo(e, { animar: false, cantos: 0, cls: "gradeDemo" })}<b class="duasLinhas">${esc(e.nome)}</b><small class="umaLinha">${esc(e.grupo)} · ${esc(EQUIP_NOMES[e.equip[0]] || e.equip[0])}</small></button>`).join("")}</div>`
      : `<div class="vazio">${ico("busca", 40, COR.texto3)}<h3>Nada encontrado</h3><p class="mut">Tente outro termo ou limpe os filtros.</p></div>`}</div>`;
}

// ------------------------------------------------------------------ exercício
function telaExercicio(id, troca) {
  const e = cat.get(id); if (!e) { setTimeout(voltar); return ""; }
  const est = loja.estado, perfil = est.perfil;
  const origem = troca ? (Object.entries(est.trocas).find(([k, v]) => k.startsWith(`${troca.sessaoIdx}|`) && v === id)?.[0].split("|")[1] ?? id) : id;
  const trocado = troca && origem !== id;
  const recorde = Progresso.recordes(est.registros).find(r => r.exId === id), ultimas = Progresso.ultimas(est.registros, id), cor = COR.brasa;
  let trocaHtml = "";
  if (troca && perfil) {
    const orig = cat.get(origem) || e;
    const alts = cat.alternativas(orig, perfil.equip, perfil.evitar).filter(x => x.id !== id);
    trocaHtml = `${secao("Trocar neste treino")}<p class="peq mut">Não tem o aparelho ou não se adaptou? Escolha uma alternativa com o mesmo padrão de movimento. A troca vale para este treino em todas as semanas.</p>
      ${trocado ? `<div style="margin-top:10px">${btn2(`Voltar ao original: ${orig.nome}`, () => { loja.trocar(troca.sessaoIdx, origem, null); voltar(); }, { cls: "largo", ico: "recomecar" })}</div>` : ""}
      <div class="pilha" style="gap:10px;margin-top:10px">${alts.slice(0, 12).map(x => `<button class="alt" aria-label="Trocar por ${esc(x.nome)}" ${a(() => { loja.trocar(troca.sessaoIdx, origem, x.id); voltar(); })}><div class="mini56">${demo(x, { animar: false, cantos: 12 })}</div>
        <div class="cresce"><b class="duasLinhas">${esc(x.nome)}</b><small class="mut3 umaLinha blk">${x.equip.map(q => esc(EQUIP_NOMES[q] || q)).join(" · ")}</small></div>${ico("troca", 22, COR.brasa)}</button>`).join("")}
      ${alts.length ? "" : `<p class="peq mut3">Sem alternativas com o seu equipamento.</p>`}</div>`;
  }
  const v = e.video;
  return `<div class="detalheEx"><div class="capaEx">${demo(e, { cantos: 0, cor })}<div class="voltarFlut">${btnIco("voltar", "Voltar", voltar, { fundo: "rgba(14,13,12,.6)" })}</div></div>
    <div class="pag" style="padding-top:16px">${rotulo(e.grupo, cor)}<h1>${esc(e.nome)}</h1>
      <div class="trilho" style="margin-top:12px">${e.equip.map(q => etq(EQUIP_NOMES[q] || q, COR.texto2)).join("")}${etq(TIPO_NOMES[e.tipo] || e.tipo, cor)}${etq(["", "Básico", "Intermediário", "Avançado"][Math.min(Math.max(e.nivel, 1), 3)], COR.texto2)}</div>
      <div style="margin-top:18px">${btn(v ? "Assistir vídeo demonstrativo" : "Buscar vídeo no YouTube", () => ir({ r: "video", id: e.id }), { ico: "play" })}</div>
      ${v ? `<p class="peq mut3 duasLinhas" style="margin-top:6px">${esc(v.titulo)}${v.canal && v.canal !== "não identificado" ? ` · ${esc(v.canal)}` : ""}${v.idioma === "en" ? " · em inglês" : ""}</p>` : ""}
      ${secao("Como executar")}<div class="pilha" style="gap:12px">${e.dicas.map((d, k) => `<div class="linha" style="align-items:flex-start"><span class="numDica">${k + 1}</span><p style="padding-top:3px">${esc(d)}</p></div>`).join("")}</div>
      ${recorde || ultimas.length ? `${secao("Seu histórico")}<div class="cartao">${recorde ? `<div class="linha" style="gap:10px">${ico("trofeu", 22, COR.alerta)}<b class="peq">Recorde: ${recorde.reps} × ${Progresso.fmtKg(recorde.kg)} kg · 1RM estimado ${Progresso.fmtKg(Math.round(recorde.rm1 * 2) / 2)} kg</b></div>` : ""}
        ${ultimas.length ? `<p class="peq mut" style="margin-top:8px">Última vez: ${ultimas.map(s => (s.kg > 0 ? `${s.reps}×${Progresso.fmtKg(s.kg)}` : s.seg > 0 ? `${s.seg}s` : `${s.reps}`)).join(" · ")}</p>` : ""}</div>` : ""}
      ${trocaHtml}<div style="height:40px"></div></div></div>`;
}

// ------------------------------------------------------------------ vídeo
const idYoutubeValido = id => /^[A-Za-z0-9_-]{11}$/.test(id || "");
function telaVideo(id) {
  const e = cat.get(id); if (!e) { setTimeout(voltar); return ""; }
  const v = e.video && idYoutubeValido(e.video.id) ? e.video : null;
  const buscaUrl = "https://www.youtube.com/results?search_query=" + encodeURIComponent(e.busca);
  const link = (t, url, icone, primario) => `<a class="${primario ? "btn" : "btn2 largo"}" href="${esc(url)}" target="_blank" rel="noopener noreferrer">${ico(icone, 18)}${esc(t)}</a>`;
  return `<div class="pag">${topo(e.nome, "Vídeo demonstrativo", voltar)}
    ${v ? `<div class="video"><iframe src="https://www.youtube-nocookie.com/embed/${v.id}?playsinline=1&rel=0&modestbranding=1" title="${esc(v.titulo)}" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture; fullscreen" allowfullscreen referrerpolicy="strict-origin-when-cross-origin"></iframe></div>
      <div style="padding:20px 0"><b>${esc(v.titulo)}</b>${v.canal && v.canal !== "não identificado" ? `<p class="peq mut">${esc(v.canal)}</p>` : ""}${v.idioma === "en" ? `<p class="peq mut3">Vídeo em inglês — ative as legendas automáticas em português.</p>` : ""}
        <div class="pilha" style="gap:10px;margin-top:18px">${link("Abrir no YouTube", `https://www.youtube.com/watch?v=${v.id}`, "externo")}${link("Ver outros vídeos", buscaUrl, "busca")}</div>
        <p class="peq mut3" style="margin-top:18px">O vídeo não carregou? Alguns canais bloqueiam a reprodução fora do YouTube — use “Abrir no YouTube”.</p></div>`
      : `<div style="padding:20px 0">${demo(e, { estilo: "aspect-ratio:1.4" })}<div style="margin-top:18px">${link("Buscar no YouTube", buscaUrl, "busca", true)}</div></div>`}
    ${secao("Pontos-chave")}<div class="pilha" style="gap:8px">${e.dicas.map(d => `<div class="linha" style="align-items:flex-start">${ico("check", 18, COR.brasa, 2.5)}<p class="peq mut">${esc(d)}</p></div>`).join("")}</div><div style="height:30px"></div></div>`;
}

// ------------------------------------------------------------------ treino ao vivo
const temCarga = p => p.ex.equip.some(q => ["barra", "halter", "kettlebell", "maquina", "polia", "bola"].includes(q));
const repsAlvo = p => { const s = (p.item.reps || "").split("–")[0].split("-")[0].trim().split(" ")[0]; return /^\d+$/.test(s) ? parseInt(s, 10) : 10; };

class EstadoTreino {
  constructor(chave, passos, sessao, semana, idx) {
    Object.assign(this, { chave, passos, sessao, semana, idx, inicioMs: Date.now(), i: 0, descansando: false, fimMs: null, pausadoRestante: null, reps: 0, kg: 0, preparadoPara: -1, ultimoBip: -1, feitas: new Map() });
  }
  get passo() { return this.passos[Math.min(Math.max(this.i, 0), this.passos.length - 1)]; }
  preparar() {
    if (this.preparadoPara === this.i) return;
    this.preparadoPara = this.i;
    const p = this.passo;
    const anterior = [...this.feitas.entries()].filter(([k]) => this.passos[k].ex.id === p.ex.id).pop()?.[1];
    this.reps = anterior?.reps ?? repsAlvo(p);
    const ult = Progresso.ultimas(loja.estado.registros, p.ex.id).map(s => s.kg);
    this.kg = anterior?.kg ?? (ult.length ? Math.max(...ult) : 0);
  }
  irPara(n, auto = false) {
    this.descansando = false; this.fimMs = null; this.pausadoRestante = null;
    if (n > this.passos.length - 1) { finalizarTreino(); return; }
    const anterior = this.passos[this.i];
    this.i = Math.max(n, 0);
    const novo = this.passos[this.i];
    if (auto && novo.porTempo && anterior && anterior.porTempo && anterior.blocoIdx === novo.blocoIdx) { this.fimMs = Date.now() + (novo.item.trabalhoSeg || 0) * 1000; this.ultimoBip = -1; }
    this.preparar();
    montarTreino();
  }
  concluirSerie() {
    const p = this.passo;
    this.feitas.set(this.i, p.porTempo ? { exId: p.ex.id, reps: 0, kg: 0, seg: p.item.trabalhoSeg || 0 } : { exId: p.ex.id, reps: this.reps, kg: temCarga(p) ? this.kg : 0, seg: 0 });
    if (this.i === this.passos.length - 1) { finalizarTreino(); return; }
    if (p.descansoDepois > 0) { this.descansando = true; this.fimMs = Date.now() + p.descansoDepois * 1000; this.pausadoRestante = null; montarTreino(); }
    else this.irPara(this.i + 1);
  }
  iniciarTempo() { this.fimMs = Date.now() + (this.passo.item.trabalhoSeg || 0) * 1000; this.pausadoRestante = null; this.ultimoBip = -1; montarTreino(); }
  pausar() { if (this.fimMs != null) this.pausadoRestante = Math.max(this.fimMs - Date.now(), 0); montarTreino(); }
  continuar() { if (this.pausadoRestante != null) this.fimMs = Date.now() + this.pausadoRestante; this.pausadoRestante = null; montarTreino(); }
  ajustarDescanso(d) { const agora = Date.now(); this.fimMs = Math.max((this.fimMs ?? agora) + d, agora + 1000); atualizarTreino(); }
}

function telaTreino(r) {
  let sessao, semana = 0, idx = -1;
  if (r.rotina) { const ro = Rotinas.porId(r.rotina); sessao = ro?.sessao; }
  else { sessao = loja.estado.plano?.semanas[r.w - 1]?.sessoes[r.i]; semana = r.w; idx = r.i; }
  if (!sessao) { setTimeout(voltar); return ""; }
  const chave = `${semana}|${idx}|${sessao.titulo}`;
  if (!treino || treino.chave !== chave) treino = new EstadoTreino(chave, Roteiro.passos(sessao, cat), sessao, semana, idx);
  if (!treino.passos.length) { treino = null; setTimeout(voltar); return ""; }
  return `<div id="treino"></div>`;
}

// Monta a tela do treino (só quando muda de passo/estado) e atualiza os números a cada 200 ms sem recriar o vídeo.
function montarTreino() {
  const t = treino, el = document.getElementById("treino");
  if (!t || !el) return;
  ACOES = ACOES.slice(0, 0);
  t.preparar();
  const p = t.passo, cor = corTipo(t.sessao.tipo, corMod(loja.estado.plano?.modalidade));
  const grupos = [];
  const chaveG = (k, porBloco) => (porBloco ? `${t.passos[k].blocoIdx}` : `${t.passos[k].blocoIdx}|${t.passos[k].itemIdx}`);
  let porBloco = new Set(t.passos.map((_, k) => chaveG(k, false))).size > 24;
  t.passos.forEach((_, k) => { const c = chaveG(k, porBloco); let g = grupos.find(x => x.c === c); if (!g) grupos.push(g = { c, ks: [] }); g.ks.push(k); });
  const sug = !p.porTempo ? Progresso.sugestao(loja.estado.registros, p.item) : null;
  const rodando = t.fimMs != null && t.pausadoRestante == null;
  const prox = t.passos[t.i + 1];
  el.innerHTML = `<div class="treinoTopo">${btnIco("fechar", "Sair do treino", confirmarSaida)}<div class="cresce" style="text-align:center"><div class="num" id="decorrido" style="font-size:24px">0:00</div>${rotulo(p.blocoNome, cor)}</div>
      ${btnIco("play", `Ver vídeo de ${p.ex.nome}`, () => ir({ r: "video", id: p.ex.id }), { cor })}</div>
    <div class="segmentos">${grupos.map(g => `<div class="barra" style="flex:${Math.min(g.ks.length, 4)};--c:${cor}"><i style="width:${(g.ks.filter(k => k < t.i || t.feitas.has(k)).length / g.ks.length) * 100}%"></i></div>`).join("")}</div>
    <div class="treinoCorpo">${demo(p.ex, { cor, cantos: 26, estilo: "aspect-ratio:1.45" })}
      <div class="linha" style="margin-top:16px">${rotulo(p.rotulo, cor)}<span class="cresce"></span><small class="mut3">${t.i + 1} / ${t.passos.length}</small></div>
      <h1 style="margin-top:4px">${esc(p.ex.nome)}</h1>
      <div class="linha" style="gap:8px;margin-top:10px;flex-wrap:wrap">${etq(p.porTempo ? Roteiro.formatarTempo(p.item.trabalhoSeg || 0) : `${p.item.reps} reps`, cor, { cheia: true })}${p.item.intensidade ? etq(p.item.intensidade, cor) : ""}</div>
      ${p.item.nota ? `<p class="peq mut" style="margin-top:8px">${esc(p.item.nota)}</p>` : ""}
      <div style="margin-top:18px">${p.porTempo ? `<div id="anelTempo" style="display:grid;place-items:center"></div>`
        : `<div class="duas">${contador("Repetições", t.reps, () => { t.reps = Math.max(t.reps - 1, 0); montarTreino(); }, () => { t.reps++; montarTreino(); })}${temCarga(p) ? contador("Carga (kg)", Progresso.fmtKg(t.kg), () => { t.kg = Math.max(t.kg - 2.5, 0); montarTreino(); }, () => { t.kg += 2.5; montarTreino(); }) : ""}</div>
          ${sug ? `<p class="peq mut" style="margin-top:10px">${esc(sug)}</p>` : ""}`}</div>
      <div class="cartao p16" style="margin-top:18px">${rotulo("Execução", cor)}<div class="pilha" style="gap:6px;margin-top:8px">${p.ex.dicas.map((d, k) => `<div class="linha" style="align-items:flex-start;gap:6px"><b class="peq" style="color:${cor};width:18px;flex:none">${k + 1}</b><span class="peq">${esc(d)}</span></div>`).join("")}</div></div>
    </div>
    <div class="treinoControles">${btnIco("anterior", "Anterior", () => t.irPara(t.i - 1), { tam: 54 })}
      <div class="cresce">${p.porTempo ? btn(rodando ? "Pausar" : t.pausadoRestante != null ? "Continuar" : "Iniciar", () => (rodando ? t.pausar() : t.pausadoRestante != null ? t.continuar() : t.iniciarTempo()), { ico: rodando ? "pausa" : "play", cor })
        : btn(t.i === t.passos.length - 1 ? "Finalizar treino" : "Concluir série", () => { vibrar(60); t.concluirSerie(); }, { ico: "check", cor })}</div>
      ${btnIco("proximo", p.porTempo ? "Concluir agora" : "Pular", () => (p.porTempo ? t.concluirSerie() : t.irPara(t.i + 1)), { tam: 54 })}</div>
    ${t.descansando ? `<div class="descanso"><div class="linha" style="justify-content:center;margin-top:30px">${rotulo(prox && prox.tipoBloco === TB.INTERVALADO && prox.ex.id === p.ex.id ? "Recuperação" : "Descanso", cor)}</div>
      <div id="anelDescanso" style="display:grid;place-items:center;margin-top:20px"></div>
      <div class="linha" style="justify-content:center;gap:12px;margin-top:24px">${btn2("−15 s", () => t.ajustarDescanso(-15000))}${btn2("+15 s", () => t.ajustarDescanso(15000))}</div>
      <div class="cresce"></div>
      ${prox ? `${rotulo("A seguir")}<div class="aSeguir"><div class="mini70">${demo(prox.ex, { cor, animar: false, cantos: 14 })}</div><div class="cresce"><b class="duasLinhas">${esc(prox.ex.nome)}</b><small class="mut blk">${esc(prox.rotulo)} · ${esc(Roteiro.prescricao(prox.item).split("× ").pop())}</small></div></div>` : ""}
      ${btn("Pular descanso", () => t.irPara(t.i + 1), { ico: "proximo", cor })}</div>` : ""}`;
  if (!tick) tick = setInterval(atualizarTreino, 200);
  atualizarTreino();
}
const contador = (rot, v, menos, mais) => `<div class="cartao p12">${rotulo(rot)}<div class="linha" style="margin-top:6px">${btnIco("menos", `Menos ${rot}`, menos, { tam: 40, icoTam: 18 })}<b class="num cresce" style="font-size:36px;text-align:center">${esc(v)}</b>${btnIco("mais", `Mais ${rot}`, mais, { tam: 40, icoTam: 18 })}</div></div>`;

function atualizarTreino() {
  const t = treino; if (!t || atual().r !== "treino") return;
  const agora = Date.now(), p = t.passo, cor = corTipo(t.sessao.tipo, corMod(loja.estado.plano?.modalidade)), aj = loja.estado.ajustes;
  const dec = Math.trunc((agora - t.inicioMs) / 1000);
  const elD = document.getElementById("decorrido");
  if (elD) elD.textContent = dec >= 3600 ? `${Math.trunc(dec / 3600)}:${String(Math.trunc(dec % 3600 / 60)).padStart(2, "0")}:${String(dec % 60).padStart(2, "0")}` : `${Math.trunc(dec / 60)}:${String(dec % 60).padStart(2, "0")}`;
  const restanteMs = t.pausadoRestante ?? (t.fimMs != null ? Math.max(t.fimMs - agora, 0) : null);
  const restanteSeg = restanteMs != null ? Math.trunc((restanteMs + 999) / 1000) : null;
  const elT = document.getElementById("anelTempo");
  if (elT) {
    const total = (p.item.trabalhoSeg || 1) * 1000, prog = restanteMs == null || t.descansando ? 0 : 1 - restanteMs / total;
    const seg = t.descansando || restanteSeg == null ? p.item.trabalhoSeg || 0 : restanteSeg;
    elT.innerHTML = anel(prog, 190, cor, 12, `<div style="text-align:center"><div class="num" style="font-size:64px">${relogio(seg)}</div><small class="mut">${t.fimMs == null && t.pausadoRestante == null ? "toque em iniciar" : t.pausadoRestante != null ? "pausado" : "em andamento"}</small></div>`);
  }
  const elR = document.getElementById("anelDescanso");
  if (elR) elR.innerHTML = anel(p.descansoDepois > 0 ? (restanteSeg || 0) / p.descansoDepois : 0, 250, cor, 14, `<div class="num" style="font-size:92px">${relogio(restanteSeg || 0)}</div>`);
  // bipes e fim do cronômetro
  if (restanteSeg == null || t.pausadoRestante != null) return;
  if (restanteSeg >= 1 && restanteSeg <= 3 && t.ultimoBip !== restanteSeg) { t.ultimoBip = restanteSeg; if (aj.som) bip(880, 0.12); if (aj.vibracao) vibrar(30); }
  if (restanteSeg === 0 && t.ultimoBip !== 0) {
    t.ultimoBip = 0;
    if (aj.som) bip(1320, 0.35); if (aj.vibracao) vibrar([200, 80, 200]);
    if (t.descansando) t.irPara(t.i + 1, true); else t.concluirSerie();
  }
  if (restanteSeg > 3) t.ultimoBip = -1;
}

let audio;
function bip(freq, dur) {
  try {
    audio = audio || new (window.AudioContext || window.webkitAudioContext)();
    const o = audio.createOscillator(), g = audio.createGain();
    o.frequency.value = freq; g.gain.value = 0.18; o.connect(g); g.connect(audio.destination);
    o.start(); g.gain.exponentialRampToValueAtTime(0.0001, audio.currentTime + dur); o.stop(audio.currentTime + dur + 0.02);
  } catch {}
}
const vibrar = padrao => { try { if (loja.estado.ajustes.vibracao) navigator.vibrate?.(padrao); } catch {} };
let trava = null;
async function wakeLock(ligar) {
  try {
    if (ligar && !trava && navigator.wakeLock) { trava = await navigator.wakeLock.request("screen"); trava.addEventListener("release", () => { trava = null; }); }
    if (!ligar && trava) { await trava.release(); trava = null; }
  } catch {}
}
document.addEventListener("visibilitychange", () => { if (document.visibilityState === "visible" && atual()?.r === "treino") wakeLock(loja.estado.ajustes.telaLigada); });

function finalizarTreino() {
  const t = treino; if (!t) return;
  const series = [...t.feitas.entries()].sort((x, y) => x[0] - y[0]).map(x => x[1]);
  const fim = Date.now();
  const reg = { epochDay: loja.hoje(), semana: t.semana, sessaoIdx: t.idx, titulo: t.sessao.titulo, tipo: t.sessao.tipo, duracaoSeg: Math.trunc((fim - t.inicioMs) / 1000), series, esforco: 7, nota: "", fcMedia: FC.media(), fcMax: FC.max(), fimMs: fim };
  treino = null; FC.parar();
  substituir({ r: "concluido", reg, esforco: 7, nota: "" });
}
function confirmarSaida() {
  const t = treino, n = t ? t.feitas.size : 0;
  const sair = () => { treino = null; FC.parar(); voltar(); };
  dialogo("Sair do treino?", n === 0 ? "Nada foi registrado ainda." : `Você pode salvar o que já fez (${n} séries) ou descartar.`,
    n === 0 ? [{ t: "Continuar treinando" }, { t: "Sair", cor: COR.brasa, fn: sair }] : [{ t: "Descartar", fn: sair }, { t: "Salvar e sair", cor: COR.brasa, fn: finalizarTreino }]);
}

// ------------------------------------------------------------------ concluído
const ESCALA = ["Muito leve", "Muito leve", "Leve", "Leve", "Moderado", "Moderado", "Difícil", "Difícil", "Muito difícil", "Quase máximo", "Máximo"];
function telaConcluido(reg) {
  const r = atual(), est = loja.estado, cor = corTipo(reg.tipo, corMod(est.plano?.modalidade)), volume = Progresso.volumeKg(reg);
  const antes = new Map(Progresso.recordes(est.registros).map(x => [x.exId, x]));
  const novos = Progresso.recordes([reg]).filter(x => antes.has(x.exId) && x.rm1 > antes.get(x.exId).rm1 + 0.01);
  const fechar = () => { aba = "hoje"; raiz({ r: "abas" }); };
  return `<div class="pag concluido"><div class="selo" style="--c:${cor}"><span>${ico("check", 44, COR.fundo, 3)}</span></div>
    ${rotulo("Treino concluído", cor)}<h1 style="text-align:center">${esc(reg.titulo)}</h1>
    <div class="tres" style="margin-top:22px"><div class="cartao p14">${estat(Math.trunc(reg.duracaoSeg / 60), "minutos")}</div><div class="cartao p14">${estat(reg.series.length, "séries feitas")}</div><div class="cartao p14">${estat(volume > 0 ? Progresso.fmtKg(volume) : "—", "kg de volume")}</div></div>
    ${reg.fcMedia > 0 ? `<div class="cartao p14" style="margin-top:12px;width:100%"><div class="linha">${ico("coracao", 28, COR.perigo)}<div class="cresce"><b>Frequência cardíaca</b><small class="mut blk">via monitor cardíaco</small></div>${estat(reg.fcMedia, "média")}${estat(reg.fcMax, "máxima")}</div></div>` : ""}
    ${novos.length ? `<div class="cartao" style="margin-top:12px;width:100%;background:${COR.alerta}14;border-color:${COR.alerta}66"><div class="linha">${ico("trofeu", 28, COR.alerta)}<div><b>Novo recorde!</b>${novos.map(x => `<small class="mut blk">${esc(cat.get(x.exId)?.nome || x.exId)}: ${x.reps} × ${Progresso.fmtKg(x.kg)} kg</small>`).join("")}</div></div></div>` : ""}
    <h3 style="margin-top:26px">Como foi o esforço?</h3><b style="color:${cor};margin-top:4px">${r.esforco}/10 · ${ESCALA[r.esforco]}</b>
    <div class="esforco">${[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(n => `<button aria-label="Esforço ${n}" aria-pressed="${n === r.esforco}" style="${n <= r.esforco ? `background:color-mix(in srgb, ${cor} ${Math.round((0.25 + n * 0.07) * 100)}%, transparent);color:${COR.texto}` : ""}" ${a(() => { r.esforco = n; render(false); })}>${n}</button>`).join("")}</div>
    <textarea class="nota" maxlength="200" placeholder="Anotação (opcional): como se sentiu, dores, ajustes…" data-in="nota" aria-label="Anotação">${esc(r.nota)}</textarea>
    <div style="margin-top:26px;width:100%">${btn("Salvar treino", () => { loja.registrar({ ...reg, esforco: r.esforco, nota: r.nota.trim() }); fechar(); }, { ico: "check", cor })}</div>
    <button class="descartar" aria-label="Descartar treino" ${a(fechar)}>Descartar</button></div>`;
}

// ------------------------------------------------------------------ progresso
function telaProgresso() {
  const est = loja.estado, regs = est.registros, hoje = loja.hoje(), corM = corMod(est.plano?.modalidade), semanas = Progresso.minutosPorSemana(regs, hoje);
  const totalKg = regs.reduce((s, r) => s + Progresso.volumeKg(r), 0);
  const max = Math.max(...semanas.map(s => s[1]), 60);
  const W = 320, H = 150, gap = 10, n = semanas.length, bw = (W - gap * (n - 1)) / n, yMeta = H * (1 - 150 / max);
  const barras = semanas.map(([, m], i) => { const h = Math.max(H * m / max, 4); return `<rect x="${i * (bw + gap)}" y="${H - h}" width="${bw}" height="${h}" rx="8" fill="${i === n - 1 ? "url(#gBrasa)" : "url(#gMod)"}"/>`; }).join("");
  const grafico = `<svg viewBox="0 0 ${W} ${H}" width="100%" height="150" preserveAspectRatio="none" role="img" aria-label="Minutos de treino nas últimas 8 semanas"><defs>
      <linearGradient id="gBrasa" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${COR.brasaClara}"/><stop offset="1" stop-color="${COR.brasa}"/></linearGradient>
      <linearGradient id="gMod" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${corM}" stop-opacity=".55"/><stop offset="1" stop-color="${corM}" stop-opacity=".3"/></linearGradient></defs>
    ${150 <= max ? `<line x1="0" x2="${W}" y1="${yMeta}" y2="${yMeta}" stroke="${COR.texto3}" stroke-dasharray="4 4"/>` : ""}${barras}</svg>`;
  const rec = Progresso.recordes(regs).slice(0, 8);
  return `<div class="pag"><div style="padding:10px 0">${rotulo("Sua evolução", corM)}<h1>Progresso</h1></div>
    <div class="tres"><div class="cartao p14">${estat(regs.length, "treinos")}</div><div class="cartao p14">${estat(`${Math.trunc(regs.reduce((s, r) => s + r.duracaoSeg, 0) / 3600)}h`, "treinando")}</div>
      <div class="cartao p14">${estat(totalKg >= 1000 ? (totalKg / 1000).toFixed(1).replace(".", ",") + "t" : Progresso.fmtKg(totalKg), "volume total")}</div></div>
    ${secao("Minutos por semana")}<div class="cartao">${grafico}<div class="eixo">${semanas.map(([ini, m], i) => `<div><b style="color:${i === n - 1 ? COR.texto : COR.texto2}">${m}</b><small>${fmtData(ini, { day: "numeric", month: "numeric" })}</small></div>`).join("")}</div>
      <p class="peq mut3" style="margin-top:8px">Linha tracejada: 150 min/semana, mínimo recomendado pela OMS.</p></div>
    ${est.plano ? `${secao("Consistência no plano")}<div class="cartao"><div class="consist">${est.plano.semanas.map(s => { const f = Progresso.feitas(regs, s.numero).size; return `<div><div class="col">${s.sessoes.map((_, k) => `<i style="background:${s.sessoes.length - 1 - k < f ? corM : COR.sup3}"></i>`).join("")}</div><small>S${s.numero}</small></div>`; }).join("")}</div></div>` : ""}
    ${pesoCorporal()}
    ${rec.length ? `${secao("Recordes")}<div class="cartao" style="padding:6px 16px">${rec.map(r => `<div class="linha" style="padding:10px 0;gap:10px">${ico("trofeu", 20, COR.alerta)}<b class="peq cresce umaLinha">${esc(cat.get(r.exId)?.nome || r.exId)}</b><b class="peq" style="color:${corM}">${r.reps}×${Progresso.fmtKg(r.kg)} kg</b></div>`).join("")}</div>` : ""}
    ${secao("Histórico")}
    ${regs.length ? `<div class="pilha" style="gap:10px">${[...regs].sort((x, y) => y.epochDay - x.epochDay).slice(0, 60).map(r => `<div class="hist"><b class="ponto" style="background:${corTipo(r.tipo, corM)};width:10px;height:10px"></b>
      <div class="cresce"><b class="umaLinha blk">${esc(r.titulo)}</b><small class="mut umaLinha blk">${fmtData(r.epochDay, { weekday: "short", day: "numeric", month: "short" })} · ${Math.trunc(r.duracaoSeg / 60)} min · esforço ${r.esforco}/10${r.series.length ? ` · ${r.series.length} séries` : ""}</small>${r.nota ? `<small class="mut3 duasLinhas">“${esc(r.nota)}”</small>` : ""}</div>
      <button aria-label="Apagar registro" ${a(() => dialogo("Apagar este treino?", r.titulo, [{ t: "Cancelar" }, { t: "Apagar", cor: COR.perigo, fn: () => loja.apagarRegistro(r) }]))}>${ico("lixo", 22, COR.texto3)}</button></div>`).join("")}</div>`
      : `<div class="vazio">${ico("grafico", 40, COR.texto3)}<h3>Nenhum treino ainda</h3><p class="mut">Conclua seu primeiro treino para começar a ver sua evolução aqui.</p></div>`}</div>`;
}
let pesoNovo = null;
function pesoCorporal() {
  const est = loja.estado, pesos = est.pesos, atualKg = pesos.length ? pesos[pesos.length - 1][1] : est.perfil?.pesoKg ?? 70;
  if (pesoNovo == null) pesoNovo = atualKg;
  const corM = corMod(est.plano?.modalidade);
  let linha = "";
  if (pesos.length >= 2) {
    const mn = Math.min(...pesos.map(p => p[1])) - 0.5, mx = Math.max(...pesos.map(p => p[1])) + 0.5, W = 320, H = 90;
    const pts = pesos.map(([, kg], i) => [W * i / (pesos.length - 1), H * (1 - (kg - mn) / (mx - mn))]);
    linha = `<svg viewBox="-6 -6 ${W + 12} ${H + 12}" width="100%" height="90" style="margin-top:12px"><path d="${pts.map((p, i) => `${i ? "L" : "M"}${p[0]},${p[1]}`).join("")}" stroke="${corM}" stroke-width="2.5" fill="none" stroke-linecap="round"/>${pts.map(p => `<circle cx="${p[0]}" cy="${p[1]}" r="4" fill="${corM}"/>`).join("")}</svg>`;
  }
  const dif = pesos.length >= 2 ? pesos[pesos.length - 1][1] - pesos[0][1] : 0;
  return `${secao("Peso corporal")}<div class="cartao"><div class="linha">${icoRedondo("peso", corM, 44)}<div class="cresce"><h2>${Progresso.fmtKg(atualKg)} kg</h2>
      <small class="mut">${pesos.length >= 2 ? `${dif > 0 ? "+" : ""}${Progresso.fmtKg(Math.round(dif * 10) / 10)} kg desde o primeiro registro` : "Registre seu peso uma vez por semana, no mesmo horário."}</small></div></div>${linha}
    <div class="linha" style="margin-top:14px">${btnIco("menos", "Diminuir peso", () => { pesoNovo = Math.round((pesoNovo - 0.1) * 10) / 10; render(false); }, { tam: 42 })}<h3 class="cresce" style="text-align:center">${Progresso.fmtKg(pesoNovo)} kg</h3>
      ${btnIco("mais", "Aumentar peso", () => { pesoNovo = Math.round((pesoNovo + 0.1) * 10) / 10; render(false); }, { tam: 42 })}${btn2("Registrar", () => { loja.registrarPeso(pesoNovo); pesoNovo = null; }, { cor: COR.brasa })}</div></div>`;
}

// ------------------------------------------------------------------ perfil
function telaPerfil() {
  const est = loja.estado, p = est.perfil, plano = est.plano, aj = est.ajustes, cor = corMod(plano?.modalidade);
  const lem = lembrete();
  return `<div class="pag">${topo("Perfil", "Você e seus ajustes", voltar)}
    <div class="cartao"><div class="linha"><span class="avatar grande">${esc((p?.nome?.[0] || "F").toUpperCase())}</span><div><h2>${esc(p?.nome || "Atleta Forja")}</h2>
      ${p ? `<small class="mut">${p.idade} anos · ${p.alturaCm} cm · ${p.pesoKg} kg · IMC ${p.imc.toFixed(1).replace(".", ",")}</small>` : ""}</div></div>
      ${p && plano ? `<div class="linha" style="flex-wrap:wrap;gap:8px;margin-top:14px">${etq(p.modalidade.curto, cor, { ico: icoMod(p.modalidade) })}${etq(p.objetivo.nome, COR.texto2)}${etq(p.nivel.nome, COR.texto2)}${etq(`${p.dias.length}x · ${p.dias.map(d => DIAS[d - 1]).join(" ")}`, COR.texto2)}${etq(`${p.minutos} min`, COR.texto2)}</div>` : ""}</div>
    ${secao("Plano")}
    ${linhaAcao("editar", "Refazer questionário", "Mude modalidade, objetivo, dias ou limitações", () => { quiz = null; ir({ r: "quiz" }); })}
    ${linhaAcao("recomecar", "Recomeçar da semana 1", "Mantém o histórico de treinos", () => dialogo("Recomeçar o plano?", "A semana atual passa a ser a semana 1. Seus treinos registrados continuam no histórico.", [{ t: "Cancelar" }, { t: "Recomeçar", cor: COR.brasa, fn: () => loja.recomecarPlano() }]))}
    ${secao("Treino ao vivo")}<div class="cartao" style="padding:6px 16px">
      ${alternar("Sons do cronômetro", aj.som, () => loja.salvarAjustes({ ...aj, som: !aj.som }))}
      ${alternar("Vibração", aj.vibracao, () => loja.salvarAjustes({ ...aj, vibracao: !aj.vibracao }))}
      ${alternar("Manter a tela ligada", aj.telaLigada, () => loja.salvarAjustes({ ...aj, telaLigada: !aj.telaLigada }))}</div>
    ${secao("Relógio e saúde")}
    ${FC.suportado() ? linhaAcao("bluetooth", "Conectar cinta/relógio por Bluetooth", FC.nome ? `Conectado: ${FC.nome}${FC.bpm ? ` · ${FC.bpm} bpm` : ""}` : "Cintas e relógios com “transmitir FC” (Polar, Garmin, Coros, Amazfit…)", () => FC.conectar())
      : `<div class="cartao"><p class="peq mut">Treino no relógio, Health Connect / app Saúde e cinta cardíaca Bluetooth funcionam no app Forja para Android e iPhone. Neste navegador, o treino fica na tela do celular com sons e vibração.</p></div>`}
    ${secao("Lembretes")}<div class="cartao"><div class="linha">${ico("sino", 22, COR.brasa)}<div class="cresce"><b>Avisar nos dias de treino</b><small class="mut blk">Adiciona os treinos ao calendário do celular, com alarme no horário escolhido</small></div></div>
      <div class="linha" style="flex-wrap:wrap;gap:8px;margin-top:12px">${[6, 7, 8, 12, 17, 18, 19, 20].map(h => chip(`${h}h`, h === lem, () => { lembrete(h); render(false); })).join("")}</div>
      <div style="margin-top:12px">${btn2("Adicionar ao calendário", () => exportarCalendario(lem), { cls: "largo", ico: "calendario" })}</div></div>
    ${secao("Sobre")}
    ${linhaAcao("ciencia", "Base científica", `Diretrizes e ${fontes.length} referências usadas para montar as rotinas`, () => ir({ r: "fontes" }))}
    ${linhaAcao("escudo", "Política de privacidade", "Nada sai do seu aparelho: sem cadastro, anúncios ou rastreamento", () => window.open(PRIVACIDADE, "_blank", "noopener"))}
    ${linhaAcao("instalar", "Instalar o app", "Android (APK) e iPhone: passo a passo", () => window.open("instalar.html", "_blank", "noopener"))}
    <div class="cartao" style="margin-top:4px"><b>Forja · versão web</b><p class="peq mut" style="margin-top:6px">Animações 3D feitas com o MakeHuman (CC0) e o Blender. Fotos: free-exercise-db (domínio público). Fontes Big Shoulders e Manrope (SIL OFL). Vídeos dos respectivos canais no YouTube.</p>
      <p class="peq mut3" style="margin-top:8px">O Forja orienta com base em diretrizes reconhecidas, mas não substitui avaliação médica nem acompanhamento de um profissional de educação física.</p></div>
    <div style="margin-top:14px">${linhaAcao("apagar", "Apagar todos os dados", "Respostas, plano e histórico", () => dialogo("Apagar tudo?", "Isso remove suas respostas, o plano e todo o histórico deste aparelho. Não dá para desfazer.", [{ t: "Cancelar" }, { t: "Apagar", cor: COR.perigo, fn: () => { treino = null; quiz = null; loja.apagarTudo(); raiz({ r: "quiz" }); } }]), COR.perigo)}</div>
    <div style="height:30px"></div></div>`;
}
function lembrete(h) {
  try { if (h != null) localStorage.setItem("forja.lembrete.hora", String(h)); return parseInt(localStorage.getItem("forja.lembrete.hora") || "18", 10); } catch { return h ?? 18; }
}
// Lembretes: arquivo de calendário (.ics) com um evento semanal por dia de treino e alarme — funciona no iPhone e no Android.
function exportarCalendario(hora) {
  const p = loja.estado.perfil; if (!p) return;
  const BY = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"];
  const hoje = Datas.hoje(), pad = n => String(n).padStart(2, "0");
  const linhas = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Forja//Treinos//PT-BR", "CALSCALE:GREGORIAN"];
  p.dias.forEach(d => {
    let dia = hoje; while (Datas.diaSemana(dia) !== d) dia++;
    const dt = Datas.data(dia), data = `${dt.getUTCFullYear()}${pad(dt.getUTCMonth() + 1)}${pad(dt.getUTCDate())}`;
    linhas.push("BEGIN:VEVENT", `UID:forja-${d}-${hoje}@forja`, `DTSTAMP:${data}T000000Z`, `DTSTART:${data}T${pad(hora)}0000`, `DURATION:PT${p.minutos}M`, `RRULE:FREQ=WEEKLY;BYDAY=${BY[d - 1]}`,
      "SUMMARY:Treino Forja", "DESCRIPTION:Seu treino de hoje está pronto no Forja. Bora forjar!", "BEGIN:VALARM", "ACTION:DISPLAY", "DESCRIPTION:Hoje tem treino", "TRIGGER:PT0M", "END:VALARM", "END:VEVENT");
  });
  linhas.push("END:VCALENDAR");
  const url = URL.createObjectURL(new Blob([linhas.join("\r\n")], { type: "text/calendar" }));
  const l = document.createElement("a"); l.href = url; l.download = "forja-treinos.ics"; document.body.appendChild(l); l.click(); l.remove();
  setTimeout(() => URL.revokeObjectURL(url), 5000);
  avisar("Abra o arquivo para adicionar os treinos ao seu calendário.");
}

// ------------------------------------------------------------------ base científica
const PRINCIPIOS = [
  ["Musculação", "Hipertrofia: ~6–12 repetições (faixas mais amplas também funcionam) perto da falha (RIR 0–3), 10+ séries semanais por grupo muscular e cada grupo 2x por semana. Força: cargas altas, 3–6 repetições e descansos de 2–5 min. Progressão por dupla progressão e semana leve a cada 4–6 semanas."],
  ["Saúde e emagrecimento", "OMS 2020: 150–300 min de atividade moderada (ou 75–150 vigorosa) por semana e força pelo menos 2 dias. No déficit calórico, a musculação preserva a massa magra."],
  ["Corrida", "Cerca de 80% do volume em intensidade leve (Seiler). Longão progressivo, semanas de recuperação a cada 3–4 e polimento antes da prova. Iniciantes alternam caminhada e corrida."],
  ["Ciclismo", "Zonas por % do FTP (Coggan): Z2 56–75%, sweet spot 88–94%, limiar 91–105%, VO2máx 106–120%. FTP ≈ 95% da potência média de 20 min."],
  ["Lutas e atletas", "Força máxima e potência longe dos treinos técnicos pesados, condicionamento no formato dos rounds, pliometria com volume controlado e prevenção (ex.: flexão nórdica, FIFA 11+)."],
  ["Mobilidade", "Antes do treino, mobilidade dinâmica (estático curto, até ~60 s por grupo). Depois, alongamento estático de 10–30 s, 2–4 vezes, pelo menos 2–3 dias por semana."],
  ["Segurança", "Triagem PAR-Q+, adaptação conservadora para joelho, lombar e ombro, e liberação médica na gestação. Pare se sentir dor no peito, tontura ou falta de ar desproporcional."],
];
const linkSeguro = u => { try { const x = new URL(u); return x.protocol === "https:" ? x.href : null; } catch { return null; } };
function telaFontes() {
  return `<div class="pag">${topo("Base científica", "Como o Forja monta sua rotina", voltar)}
    <div class="pilha" style="gap:10px">${PRINCIPIOS.map(([t, d]) => `<div class="cartao">${rotulo(t, COR.brasa)}<p style="margin-top:6px">${esc(d)}</p></div>`).join("")}</div>
    ${secao(`Referências (${fontes.length})`)}<div class="pilha" style="gap:0">${fontes.map(f => { const u = linkSeguro(f.url); return `<a class="fonte" ${u ? `href="${esc(u)}" target="_blank" rel="noopener noreferrer"` : ""}><b style="color:${COR.brasa}">${esc(f.ano)}</b><span class="peq mut cresce">${esc(f.titulo)}</span>${ico("externo", 16, COR.texto3)}</a>`; }).join("")}</div><div style="height:30px"></div></div>`;
}

// ------------------------------------------------------------------ frequência cardíaca (Web Bluetooth, onde o navegador suporta)
const FC = {
  dev: null, nome: null, bpm: null, amostras: [],
  suportado: () => !!(navigator.bluetooth && window.isSecureContext),
  async conectar() {
    try {
      const dev = await navigator.bluetooth.requestDevice({ filters: [{ services: ["heart_rate"] }] });
      const gatt = await dev.gatt.connect();
      const car = await (await gatt.getPrimaryService("heart_rate")).getCharacteristic("heart_rate_measurement");
      car.addEventListener("characteristicvaluechanged", ev => {
        const v = ev.target.value, f = v.getUint8(0), bpm = f & 1 ? v.getUint16(1, true) : v.getUint8(1);
        if (bpm > 25 && bpm < 250) { FC.bpm = bpm; if (treino) FC.amostras.push(bpm); }
      });
      await car.startNotifications();
      dev.addEventListener("gattserverdisconnected", () => { FC.nome = null; FC.bpm = null; });
      FC.dev = dev; FC.nome = dev.name || "Monitor cardíaco";
      avisar(`${FC.nome} conectado. A FC aparece no resumo do treino.`);
      render(false);
    } catch (e) { if (e && e.name !== "NotFoundError") avisar("Não deu para conectar ao monitor cardíaco."); }
  },
  media: () => (FC.amostras.length ? Math.round(FC.amostras.reduce((s, x) => s + x, 0) / FC.amostras.length) : 0),
  max: () => (FC.amostras.length ? Math.max(...FC.amostras) : 0),
  parar() { FC.amostras = []; },
};

// ------------------------------------------------------------------ entradas de texto e controles deslizantes
function ligarEntradas() {
  document.querySelectorAll("[data-in]").forEach(el => {
    const tipo = el.dataset.in;
    if (tipo === "nome") el.addEventListener("input", () => {
      const v = el.value.slice(0, 24);
      quiz.resp = { ...quiz.resp, nome: v ? [v] : [] };
      const b = document.querySelector(".fixo .btn"); // "Pular" ↔ "Continuar" sem recriar o campo (mantém o teclado aberto)
      if (b && b.lastChild && b.lastChild.nodeType === 3 && b.lastChild.textContent !== "Montar minha rotina") b.lastChild.textContent = v ? "Continuar" : "Pular";
    });
    if (tipo === "num") el.addEventListener("input", () => {
      const vis = Questionario.visiveis(quiz.resp), p = vis[Math.min(Math.max(quiz.etapa, 0), vis.length - 1)];
      const n = Math.min(Math.max(Math.round(+el.value / p.passo) * p.passo, p.min), p.max);
      const r = { ...quiz.resp, [p.id]: [String(n)] };
      if (p.id === "dias") r.dias_semana = Questionario.diasSugeridos(n).map(String);
      quiz.resp = r;
      const num = document.querySelector(".numero"); if (num) { num.textContent = n; num.classList.remove("vazio"); }
    });
    if (tipo === "num") el.addEventListener("change", () => render(false));
    if (tipo === "busca") el.addEventListener("input", () => { busca = el.value; const pos = el.selectionStart; render(false); const n = document.querySelector('[data-in="busca"]'); if (n) { n.focus(); n.setSelectionRange(pos, pos); } });
    if (tipo === "nota") el.addEventListener("input", () => { atual().nota = el.value.slice(0, 200); });
  });
  const nome = document.querySelector('[data-in="nome"]');
  if (nome) nome.addEventListener("keydown", ev => { if (ev.key === "Enter") document.querySelector(".fixo .btn")?.click(); });
}

// ------------------------------------------------------------------ início
(async function iniciar() {
  try {
    const [ex, fo, meta] = await Promise.all([
      fetch("exercises.json").then(r => r.json()),
      fetch("fontes.json").then(r => r.json()).catch(() => []),
      fetch("video3d/meta.json").then(r => (r.ok ? r.json() : {})).catch(() => ({})),
    ]);
    cat = new F.Catalogo(ex); fontes = fo; ANIM = meta;
    loja = new F.Loja(cat, F.armLocal());
    migrarVersaoAntiga();
    loja.ouvir(() => { if (atual().r !== "treino") render(false); });
    history.pushState(null, "");
    if (!loja.estado.temPlano) pilha = [{ r: "quiz" }];
    render(true);
  } catch (e) {
    console.error(e);
    $app.innerHTML = `<div class="carregando">Não deu para carregar o Forja. Verifique a conexão e recarregue a página.</div>`;
  }
  if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js").catch(() => {});
})();

// Quem usou a versão web antiga (6 perguntas) refaz a anamnese completa; o histórico antigo não é compatível.
function migrarVersaoAntiga() {
  try { ["forja_resp", "forja_hist", "forja_treinos", "forja_semana"].forEach(k => localStorage.removeItem(k)); } catch {}
}
