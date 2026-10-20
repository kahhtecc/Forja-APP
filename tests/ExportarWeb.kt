import com.forja.app.core.*
import org.json.JSONArray
import org.json.JSONObject
import java.io.File

/**
 * Gera os dados da versão web de demonstração usando o MESMO gerador do app.
 * Uso: java ... ExportarWebKt <exercises.json> <saida.json>
 */
fun itemJson(it: Item) = JSONObject().apply {
    put("e", it.exId); put("s", it.series)
    it.reps?.let { r -> put("r", r) }; it.trabalhoSeg?.let { t -> put("t", t) }
    put("d", it.descansoSeg); it.intensidade?.let { x -> put("i", x) }; it.nota?.let { n -> put("n", n) }
}

fun sessaoJson(s: Sessao) = JSONObject().apply {
    put("titulo", s.titulo); put("foco", s.foco); put("tipo", s.tipo); put("min", s.minutos); put("dia", s.diaSemana)
    put("blocos", JSONArray(s.blocos.map { b ->
        JSONObject().put("nome", b.nome).put("tipo", b.tipo.name).put("voltas", b.voltas).put("nota", b.nota ?: "").put("itens", JSONArray(b.itens.map { itemJson(it) }))
    }))
}

fun main(args: Array<String>) {
    val cat = Catalogo.deJson(File(args[0]).readText())
    val ger = Gerador(cat)
    val planos = JSONObject()
    val forcaObj = setOf("academia", "casa_corpo", "casa_elastico", "hibrido", "hiit")
    for (m in Modalidade.entries) for (n in Nivel.entries) for (d in 2..6) {
        val objs = if (m.id in forcaObj) Objetivo.entries.map { it.id } else listOf("_")
        val metas = if (m == Modalidade.CORRIDA) listOf("comecar", "5k", "10k", "21k", "42k", "saude") else listOf("_")
        for (o in objs) for (meta in metas) {
            val r = mutableMapOf(
                "modalidade" to listOf(m.id), "experiencia" to listOf(n.id), "dias" to listOf("$d"),
                "dias_semana" to Questionario.diasSugeridos(d).map { "$it" }, "minutos" to listOf("60"),
                "idade" to listOf("30"), "sexo" to listOf("x"), "altura" to listOf("172"), "peso" to listOf("72"),
                "limitacoes" to listOf("nenhuma"), "parq" to listOf("nenhuma"), "local" to listOf("academia"),
            )
            if (o != "_") r["objetivo"] = listOf(o)
            if (meta != "_") { r["corrida_meta"] = listOf(meta); r["corrida_continuo"] = listOf(if (meta == "comecar") "nao" else "sim") }
            val p = ger.gerar(Perfil.de(r))
            val chave = "${m.id}|${n.id}|$d|$o|$meta"
            planos.put(chave, JSONObject().apply {
                put("nome", p.nome); put("resumo", p.resumo); put("meta", p.metaSemanal)
                put("dicas", JSONArray(p.dicas)); put("alertas", JSONArray(p.alertas))
                put("semanas", JSONArray(p.semanas.map { JSONObject().put("fase", it.fase).put("nota", it.nota) }))
                put("s1", JSONArray(p.semanas[0].sessoes.map { sessaoJson(it) }))
            })
        }
    }
    val rotinas = JSONArray(Rotinas.todas.map { JSONObject().put("id", it.id).put("cat", it.categoria).put("titulo", it.titulo).put("sub", it.subtitulo).put("tema", it.tema).put("sessao", sessaoJson(it.sessao.copy(minutos = Roteiro.minutos(it.sessao, cat)))) })
    val perguntas = JSONArray(Questionario.perguntas.map { q ->
        JSONObject().put("id", q.id).put("secao", q.secao).put("titulo", q.titulo).put("sub", q.subtitulo ?: "").put("tipo", q.tipo.name)
            .put("opcoes", JSONArray(q.opcoes.map { JSONObject().put("v", it.valor).put("t", it.titulo).put("d", it.descricao ?: "") }))
            .put("min", q.min).put("max", q.max).put("passo", q.passo).put("padrao", q.padrao ?: q.min).put("unidade", q.unidade).put("opcional", q.opcional).put("exclusiva", q.exclusiva ?: "")
    })
    File(args[1]).writeText(JSONObject().put("planos", planos).put("rotinas", rotinas).put("perguntas", perguntas).toString())
    println("planos: ${planos.length()} · ${File(args[1]).length() / 1024} KB")
}
