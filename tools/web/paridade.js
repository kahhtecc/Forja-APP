// Garante que o núcleo da versão web (web/nucleo.js) gera exatamente os mesmos planos do Kotlin (Android) e do Swift (iPhone).
// Uso: node tools/web/paridade.js   (ouro exportado por tests/ExportarOuro.kt, o mesmo usado em ios/ForjaCore/Tests)
const fs = require("fs"), path = require("path");
const raiz = path.join(__dirname, "..", "..");
require(path.join(raiz, "web", "nucleo.js"));
const F = globalThis.Forja;
const res = f => JSON.parse(fs.readFileSync(path.join(raiz, "ios/ForjaCore/Tests/ForjaCoreTests/Resources", f), "utf8"));
const cat = new F.Catalogo(res("exercises.json"));
const ouro = res("ouro.json");

const itemJson = it => { const o = { e: it.exId, s: it.series, d: it.descansoSeg }; if (it.reps != null) o.r = it.reps; if (it.trabalhoSeg != null) o.t = it.trabalhoSeg; if (it.intensidade != null) o.i = it.intensidade; if (it.nota != null) o.n = it.nota; return o; };
const sessaoJson = s => ({ titulo: s.titulo, foco: s.foco, tipo: s.tipo, min: s.minutos, dia: s.diaSemana,
  blocos: s.blocos.map(b => ({ nome: b.nome, tipo: b.tipo, voltas: b.voltas, nota: b.nota ?? "", itens: b.itens.map(itemJson) })) });
const planoJson = p => ({ nome: p.nome, resumo: p.resumo, modalidade: p.modalidade.id, objetivo: p.objetivo.id, nivel: p.nivel.id, meta: p.metaSemanal,
  dicas: p.dicas, alertas: p.alertas, semanas: p.semanas.map(w => ({ n: w.numero, fase: w.fase, nota: w.nota, sessoes: w.sessoes.map(sessaoJson) })) });

function dif(a, b, c = "") {
  if (Array.isArray(a) || Array.isArray(b)) {
    if (!Array.isArray(a) || !Array.isArray(b)) return `${c}: tipo diferente`;
    if (a.length !== b.length) return `${c}: tamanho ${a.length} (JS) vs ${b.length} (Kotlin)`;
    for (let i = 0; i < a.length; i++) { const d = dif(a[i], b[i], `${c}[${i}]`); if (d) return d; }
    return null;
  }
  if (a && typeof a === "object" && b && typeof b === "object") {
    for (const k of [...new Set([...Object.keys(a), ...Object.keys(b)])].sort()) {
      if (!(k in a)) return `${c}.${k}: ausente no JS (Kotlin=${JSON.stringify(b[k]).slice(0, 80)})`;
      if (!(k in b)) return `${c}.${k}: sobra no JS = ${JSON.stringify(a[k]).slice(0, 80)}`;
      const d = dif(a[k], b[k], `${c}.${k}`); if (d) return d;
    }
    return null;
  }
  return a === b ? null : `${c}: JS=${JSON.stringify(a)} Kotlin=${JSON.stringify(b)}`;
}

const ger = new F.Gerador(cat);
let falhas = 0;
ouro.casos.forEach((c, i) => {
  let d;
  try { d = dif(planoJson(ger.gerar(F.perfilDe(c.respostas))), c.plano); } catch (e) { d = "EXCEÇÃO " + e.stack.split("\n").slice(0, 3).join(" | "); }
  if (d) { falhas++; if (falhas <= 12) console.log(`caso ${i} ${c.respostas.modalidade} ${c.respostas.experiencia} ${c.respostas.dias}: ${d}`); }
});
let falhasRot = 0;
F.Rotinas.todas.forEach((r, k) => {
  const o = ouro.rotinas[k];
  const d = o.id !== r.id ? `id ${r.id} vs ${o.id}` : o.min !== F.Roteiro.minutos(r.sessao, cat) ? `min ${F.Roteiro.minutos(r.sessao, cat)} vs ${o.min}` : dif(sessaoJson(r.sessao), o.sessao);
  if (d) { falhasRot++; console.log(`rotina ${r.id}: ${d}`); }
});
if (ouro.rotinas.length !== F.Rotinas.todas.length) { falhasRot++; console.log(`rotinas: ${F.Rotinas.todas.length} vs ${ouro.rotinas.length}`); }
// questionário e loja
const ok = (cond, msg) => { if (!cond) { falhas++; console.log("FALHA " + msg); } };
let r = { modalidade: ["corrida"], corrida_meta: ["comecar"] };
ok(!F.Questionario.visiveis(r).some(q => q.id === "corrida_continuo"), "corrida_continuo oculto");
r.modalidade = ["casa_corpo"]; ok(F.Questionario.visiveis(r).some(q => q.id === "equipamentos"), "equipamentos visível em casa");
ok(F.Datas.diaSemana(0) === 4, "1970-01-01 = quinta");
const mem = {}; const arm = { ler: k => mem[k] ?? null, gravar: (k, v) => { if (v == null) delete mem[k]; else mem[k] = v; } };
let dia = 20382; const loja = new F.Loja(cat, arm, () => dia);
loja.salvarRespostas({ modalidade: ["academia"], objetivo: ["massa"], experiencia: ["intermediario"], dias: ["4"], dias_semana: ["1", "2", "4", "5"], minutos: ["60"], idade: ["30"], sexo: ["m"], altura: ["175"], peso: ["78"], limitacoes: ["nenhuma"], parq: ["nenhuma"] });
ok(loja.estado.plano?.semanas.length === 8, "plano com 8 semanas");
const ex = loja.estado.plano.semanas[0].sessoes[0].blocos[1].itens[0].exId;
const alt = cat.alternativas(cat.exigir(ex), loja.estado.perfil.equip, loja.estado.perfil.evitar);
loja.trocar(0, ex, alt[0].id);
ok(loja.estado.plano.semanas[0].sessoes[0].blocos[1].itens[0].exId === alt[0].id, "troca aplicada");
loja.registrar({ epochDay: dia, semana: 1, sessaoIdx: 0, titulo: "A", tipo: "forca", duracaoSeg: 3000, series: [{ exId: alt[0].id, reps: 12, kg: 40 }, { exId: alt[0].id, reps: 12, kg: 40 }], esforco: 7, nota: "" });
const loja2 = new F.Loja(cat, arm, () => dia);
ok(loja2.estado.registros.length === 1 && Object.keys(loja2.estado.trocas).length === 1, "persistência");
ok((F.Progresso.sugestao(loja2.estado.registros, { exId: alt[0].id, reps: "8–12" }) || "").includes("42"), "sugestão de carga 42 kg");
dia += 7; ok(loja2.semanaAtual() === 2, "semana 2");
loja2.apagarTudo(); ok(!loja2.estado.temPlano, "apagar tudo");
console.log(`${ouro.casos.length - (falhas)} de ${ouro.casos.length} planos idênticos ao Kotlin · rotinas com diferença: ${falhasRot}`);
process.exit(falhas || falhasRot ? 1 : 0);
