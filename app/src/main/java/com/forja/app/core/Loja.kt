package com.forja.app.core

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import org.json.JSONArray
import org.json.JSONObject

interface Armazenamento {
    fun ler(chave: String): String?
    fun gravar(chave: String, valor: String?)
}

data class Ajustes(val som: Boolean = true, val vibracao: Boolean = true, val telaLigada: Boolean = true)

data class Estado(
    val respostas: Respostas = emptyMap(),
    /** Segunda-feira da semana 1 (epochDay). */
    val inicio: Long = 0,
    /** "sessaoIdx|exercícioOriginal" -> exercício escolhido. */
    val trocas: Map<String, String> = emptyMap(),
    val registros: List<Registro> = emptyList(),
    val pesos: List<Pair<Long, Double>> = emptyList(),
    val ajustes: Ajustes = Ajustes(),
    val perfil: Perfil? = null,
    val plano: Plano? = null,
) {
    val temPlano get() = plano != null
}

/** Estado do app + persistência. Sem dependências de Android (testável na JVM). */
class Loja(private val cat: Catalogo, private val arm: Armazenamento, private val hoje: () -> Long) {
    private val gerador = Gerador(cat)
    private val _estado = MutableStateFlow(carregar())
    val estado: StateFlow<Estado> = _estado

    val catalogo get() = cat
    fun hoje(): Long = hoje.invoke()

    // ------------------------------------------------------------- ações

    fun salvarRespostas(r: Respostas, manterHistorico: Boolean = true) {
        val limpas = Questionario.limpar(r)
        arm.gravar(K_RESP, respostasJson(limpas).toString())
        arm.gravar(K_INICIO, Datas.segunda(hoje()).toString())
        arm.gravar(K_TROCAS, null)
        if (!manterHistorico) arm.gravar(K_REG, null)
        _estado.value = carregar()
    }

    fun recomecarPlano() {
        arm.gravar(K_INICIO, Datas.segunda(hoje()).toString())
        _estado.value = carregar()
    }

    fun registrar(r: Registro) {
        val l = _estado.value.registros + r
        arm.gravar(K_REG, JSONArray(l.map { registroJson(it) }).toString())
        _estado.value = carregar()
    }

    fun apagarRegistro(r: Registro) {
        val l = _estado.value.registros - r
        arm.gravar(K_REG, JSONArray(l.map { registroJson(it) }).toString())
        _estado.value = carregar()
    }

    fun trocar(sessaoIdx: Int, original: String, novo: String?) {
        val t = _estado.value.trocas.toMutableMap()
        val chave = "$sessaoIdx|$original"
        if (novo == null || novo == original) t.remove(chave) else t[chave] = novo
        arm.gravar(K_TROCAS, JSONObject(t as Map<*, *>).toString())
        _estado.value = carregar()
    }

    fun registrarPeso(kg: Double) {
        val d = hoje()
        val l = _estado.value.pesos.filter { it.first != d } + (d to kg)
        arm.gravar(K_PESOS, JSONArray(l.sortedBy { it.first }.map { JSONArray().put(it.first).put(it.second) }).toString())
        _estado.value = carregar()
    }

    fun salvarAjustes(a: Ajustes) {
        arm.gravar(K_AJ, JSONObject().put("som", a.som).put("vibracao", a.vibracao).put("tela", a.telaLigada).toString())
        _estado.value = _estado.value.copy(ajustes = a)
    }

    fun apagarTudo() {
        listOf(K_RESP, K_INICIO, K_TROCAS, K_REG, K_PESOS, K_AJ).forEach { arm.gravar(it, null) }
        _estado.value = carregar()
    }

    // ------------------------------------------------------------- consultas

    fun semanaAtual(): Int {
        val e = _estado.value
        return Progresso.semanaAtual(e.inicio, hoje(), e.plano?.semanas?.size ?: 1)
    }

    /** Sessão marcada para hoje (índice na semana atual), se houver. */
    fun sessaoDeHoje(): Pair<Int, Sessao>? {
        val p = _estado.value.plano ?: return null
        val dia = Datas.diaSemana(hoje())
        val s = p.semanas[semanaAtual() - 1].sessoes
        val i = s.indexOfFirst { it.diaSemana == dia }
        return if (i >= 0) i to s[i] else null
    }

    /** Próxima sessão ainda não feita na semana atual. */
    fun proximaSessao(): Pair<Int, Sessao>? {
        val e = _estado.value
        val p = e.plano ?: return null
        val w = semanaAtual()
        val feitas = Progresso.feitas(e.registros, w)
        val dia = Datas.diaSemana(hoje())
        val s = p.semanas[w - 1].sessoes
        return s.withIndex().filter { it.index !in feitas }.let { pend -> pend.firstOrNull { it.value.diaSemana >= dia } ?: pend.firstOrNull() }?.let { it.index to it.value }
    }

    // ------------------------------------------------------------- carga

    private fun carregar(): Estado {
        val resp = arm.ler(K_RESP)?.let { runCatching { respostasDeJson(JSONObject(it)) }.getOrNull() } ?: emptyMap()
        val inicio = arm.ler(K_INICIO)?.toLongOrNull() ?: Datas.segunda(hoje())
        val trocas = arm.ler(K_TROCAS)?.let { s ->
            runCatching { JSONObject(s).let { o -> o.keys().asSequence().associateWith { o.getString(it) } } }.getOrNull()
        } ?: emptyMap()
        val regs = arm.ler(K_REG)?.let { s -> runCatching { JSONArray(s).let { a -> (0 until a.length()).map { registroDeJson(a.getJSONObject(it)) } } }.getOrNull() } ?: emptyList()
        val pesos = arm.ler(K_PESOS)?.let { s -> runCatching { JSONArray(s).let { a -> (0 until a.length()).map { a.getJSONArray(it).let { p -> p.getLong(0) to p.getDouble(1) } } } }.getOrNull() } ?: emptyList()
        val aj = arm.ler(K_AJ)?.let { s -> runCatching { JSONObject(s).let { Ajustes(it.optBoolean("som", true), it.optBoolean("vibracao", true), it.optBoolean("tela", true)) } }.getOrNull() } ?: Ajustes()
        val perfil = if (resp.isNotEmpty() && Questionario.completo(resp)) Perfil.de(resp) else null
        val plano = perfil?.let { aplicarTrocas(gerador.gerar(it), trocas) }
        return Estado(resp, inicio, trocas, regs, pesos, aj, perfil, plano)
    }

    private fun aplicarTrocas(p: Plano, trocas: Map<String, String>): Plano {
        if (trocas.isEmpty()) return p
        return p.copy(semanas = p.semanas.map { s ->
            s.copy(sessoes = s.sessoes.mapIndexed { i, ses ->
                ses.copy(blocos = ses.blocos.map { b ->
                    b.copy(itens = b.itens.map { it ->
                        val novo = trocas["$i|${it.exId}"]
                        if (novo != null && cat[novo] != null) {
                            val ex = cat.exigir(novo)
                            // Ajusta a prescrição quando a troca muda de repetições para tempo (ou vice-versa).
                            when {
                                ex.porTempo && it.reps != null -> it.copy(exId = novo, reps = null, trabalhoSeg = 40)
                                !ex.porTempo && it.reps == null && b.tipo == TipoBloco.PRINCIPAL -> it.copy(exId = novo, reps = "10–12", trabalhoSeg = null)
                                else -> it.copy(exId = novo)
                            }
                        } else it
                    })
                })
            })
        })
    }

    companion object {
        const val K_RESP = "respostas"
        const val K_INICIO = "inicio"
        const val K_TROCAS = "trocas"
        const val K_REG = "registros"
        const val K_PESOS = "pesos"
        const val K_AJ = "ajustes"

        fun respostasJson(r: Respostas) = JSONObject().apply { r.forEach { (k, v) -> put(k, JSONArray(v)) } }
        fun respostasDeJson(o: JSONObject): Respostas = o.keys().asSequence().associateWith { k ->
            val a = o.getJSONArray(k); (0 until a.length()).map { a.getString(it) }
        }

        fun registroJson(r: Registro) = JSONObject()
            .put("d", r.epochDay).put("w", r.semana).put("i", r.sessaoIdx).put("t", r.titulo).put("tp", r.tipo)
            .put("s", r.duracaoSeg).put("e", r.esforco).put("n", r.nota)
            .put("x", JSONArray(r.series.map { JSONArray().put(it.exId).put(it.reps).put(it.kg).put(it.seg) }))
            .apply { if (r.fcMedia > 0) put("fm", r.fcMedia).put("fx", r.fcMax); if (r.fimMs > 0) put("f", r.fimMs) }

        fun registroDeJson(o: JSONObject): Registro {
            val x = o.optJSONArray("x") ?: JSONArray()
            return Registro(
                o.getLong("d"), o.getInt("w"), o.getInt("i"), o.optString("t"), o.optString("tp"), o.optInt("s"),
                (0 until x.length()).map { x.getJSONArray(it).let { s -> SerieFeita(s.getString(0), s.getInt(1), s.getDouble(2), s.optInt(3)) } },
                o.optInt("e"), o.optString("n"),
                o.optInt("fm"), o.optInt("fx"), o.optLong("f"),
            )
        }
    }
}
