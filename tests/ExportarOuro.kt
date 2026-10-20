import com.forja.app.core.*
import org.json.JSONArray
import org.json.JSONObject
import java.io.File

/**
 * Gabarito para o iOS: planos completos gerados pelo núcleo Kotlin para vários perfis.
 * O núcleo Swift precisa gerar exatamente o mesmo JSON (teste de paridade).
 * Uso: java ... ExportarOuroKt <exercises.json> <saida.json>
 */
fun planoCompletoJson(p: Plano) = JSONObject().apply {
    put("nome", p.nome); put("resumo", p.resumo); put("modalidade", p.modalidade.id); put("objetivo", p.objetivo.id); put("nivel", p.nivel.id)
    put("meta", p.metaSemanal); put("dicas", JSONArray(p.dicas)); put("alertas", JSONArray(p.alertas))
    put("semanas", JSONArray(p.semanas.map { w -> JSONObject().put("n", w.numero).put("fase", w.fase).put("nota", w.nota).put("sessoes", JSONArray(w.sessoes.map { sessaoJson(it) })) }))
}

fun main(args: Array<String>) {
    val cat = Catalogo.deJson(File(args[0]).readText())
    val ger = Gerador(cat)
    val casos = JSONArray()
    fun caso(r: Map<String, List<String>>) {
        val limpo = Questionario.limpar(r)
        check(Questionario.completo(limpo)) { "incompleto: $r" }
        casos.put(JSONObject().put("respostas", Loja.respostasJson(limpo)).put("plano", planoCompletoJson(ger.gerar(Perfil.de(limpo)))))
    }
    fun base(m: String, o: String, n: String, d: Int, min: Int = 60, extra: Map<String, List<String>> = emptyMap()) = mutableMapOf(
        "nome" to listOf("Teste"), "modalidade" to listOf(m), "objetivo" to listOf(o), "experiencia" to listOf(n), "dias" to listOf("$d"),
        "dias_semana" to Questionario.diasSugeridos(d).map { "$it" }, "minutos" to listOf("$min"), "idade" to listOf("34"), "sexo" to listOf("m"),
        "altura" to listOf("176"), "peso" to listOf("79"), "limitacoes" to listOf("nenhuma"), "parq" to listOf("nenhuma"), "local" to listOf("academia"),
        "equipamentos" to listOf(), "hibrido_cardio" to listOf("corrida"), "corrida_meta" to listOf("10k"), "corrida_continuo" to listOf("sim"),
        "bike_tipo" to listOf("estrada"), "luta_arte" to listOf("mma"), "luta_tecnicos" to listOf("3"), "luta_marcada" to listOf("nao"),
        "atleta_esporte" to listOf("coletivo"), "atleta_fase" to listOf("pre"),
    ).apply { putAll(extra) }
    val niveis = listOf("iniciante", "intermediario", "avancado")
    // todas as modalidades × níveis × alguns dias
    for (m in Modalidade.entries) for ((k, n) in niveis.withIndex()) for (d in listOf(2 + k, 4 + k / 2, 6)) {
        val obj = listOf("massa", "emagrecer", "saude", "forca", "resistencia", "performance")[(m.ordinal + d + k) % 6]
        caso(base(m.id, obj, n, d, listOf(30, 45, 60, 75, 90)[(m.ordinal + d) % 5]))
    }
    // casos especiais
    caso(base("casa_corpo", "emagrecer", "iniciante", 4, 30, mapOf("limitacoes" to listOf("joelho"))))
    caso(base("casa_elastico", "massa", "intermediario", 4, 45, mapOf("limitacoes" to listOf("ombro", "punho"))))
    caso(base("casa_corpo", "massa", "avancado", 5, 60, mapOf("equipamentos" to listOf("halter", "barra_fixa", "banco"))))
    caso(base("academia", "forca", "avancado", 5, 75, mapOf("limitacoes" to listOf("lombar"))))
    caso(base("corrida", "saude", "iniciante", 3, 30, mapOf("corrida_meta" to listOf("comecar"))))
    caso(base("corrida", "saude", "iniciante", 5, 30, mapOf("corrida_meta" to listOf("comecar"))))
    caso(base("corrida", "performance", "iniciante", 4, 60, mapOf("corrida_meta" to listOf("42k"), "corrida_continuo" to listOf("nao"))))
    caso(base("corrida", "performance", "avancado", 6, 90, mapOf("corrida_meta" to listOf("42k"), "corrida_5k" to listOf("20"))))
    caso(base("corrida", "performance", "intermediario", 4, 60, mapOf("corrida_meta" to listOf("21k"), "corrida_5k" to listOf("27"))))
    caso(base("corrida", "performance", "intermediario", 3, 45, mapOf("corrida_meta" to listOf("5k"), "corrida_5k" to listOf("31"))))
    caso(base("bike", "performance", "avancado", 6, 90, mapOf("bike_ftp" to listOf("260"), "bike_tipo" to listOf("mtb"))))
    caso(base("bike", "emagrecer", "iniciante", 3, 45))
    caso(base("luta", "performance", "avancado", 5, 60, mapOf("luta_arte" to listOf("bjj"), "luta_marcada" to listOf("6"), "luta_tecnicos" to listOf("5"))))
    caso(base("luta", "performance", "intermediario", 4, 45, mapOf("luta_arte" to listOf("boxe"), "local" to listOf("casa"), "equipamentos" to listOf("saco", "corda"))))
    caso(base("luta", "performance", "intermediario", 3, 60, mapOf("luta_arte" to listOf("judo"), "luta_marcada" to listOf("4"))))
    caso(base("atleta", "performance", "avancado", 5, 60, mapOf("atleta_fase" to listOf("em"), "atleta_esporte" to listOf("raquete"))))
    caso(base("atleta", "performance", "intermediario", 6, 60, mapOf("atleta_fase" to listOf("fora"), "atleta_esporte" to listOf("resistencia"))))
    caso(base("hiit", "emagrecer", "avancado", 5, 30, mapOf("local" to listOf("casa"), "equipamentos" to listOf("kettlebell"))))
    caso(base("hibrido", "resistencia", "intermediario", 6, 60, mapOf("hibrido_cardio" to listOf("bike"))))
    caso(base("hibrido", "massa", "iniciante", 4, 60, mapOf("corrida_continuo" to listOf("nao"))))
    caso(base("longevidade", "saude", "iniciante", 3, 45, mapOf("idade" to listOf("68"), "local" to listOf("casa"), "equipamentos" to listOf("elastico", "banco"))))
    caso(base("casa_corpo", "saude", "iniciante", 3, 30, mapOf("sexo" to listOf("f"), "gestante" to listOf("sim"))))
    caso(base("academia", "saude", "iniciante", 2, 45, mapOf("parq" to listOf("coracao", "remedio"), "idade" to listOf("16"))))
    caso(base("academia", "emagrecer", "iniciante", 5, 60, mapOf("peso" to listOf("120"), "altura" to listOf("170"))))
    val rotinas = JSONArray(Rotinas.todas.map { JSONObject().put("id", it.id).put("min", Roteiro.minutos(it.sessao, cat)).put("sessao", sessaoJson(it.sessao)) })
    File(args[1]).writeText(JSONObject().put("casos", casos).put("rotinas", rotinas).toString())
    println("casos: ${casos.length()} · ${File(args[1]).length() / 1024} KB")
}
