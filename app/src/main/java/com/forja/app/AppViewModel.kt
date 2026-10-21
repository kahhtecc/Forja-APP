package com.forja.app

import android.app.Application
import android.content.Context
import androidx.lifecycle.AndroidViewModel
import com.forja.app.core.Armazenamento
import com.forja.app.core.Catalogo
import com.forja.app.core.Datas
import com.forja.app.core.Loja
import com.forja.app.core.Questionario
import com.forja.app.core.Registro
import com.forja.app.core.Roteiro
import com.forja.app.core.SerieFeita
import com.forja.app.ui.Animacoes3D
import org.json.JSONArray
import java.time.LocalDate
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class Preferencias(ctx: Context, nome: String) : Armazenamento {
    private val sp = ctx.getSharedPreferences(nome, Context.MODE_PRIVATE)
    override fun ler(chave: String): String? = sp.getString(chave, null)
    override fun gravar(chave: String, valor: String?) {
        sp.edit().apply { if (valor == null) remove(chave) else putString(chave, valor) }.apply()
    }
}

data class Fonte(val id: String, val titulo: String, val ano: Int, val url: String)

class AppViewModel(app: Application) : AndroidViewModel(app) {
    var catalogo: Catalogo = carregarCatalogo()
        private set
    var fontes: List<Fonte> = carregarFontes()
        private set

    /** Muda quando chega conteúdo novo pela internet — a interface é recriada com ele. */
    var versaoConteudo by mutableIntStateOf(Conteudo.versaoAtual(app))
        private set
    var aviso by mutableStateOf<String?>(null)
    var novaVersao by mutableStateOf<Conteudo.NovaVersao?>(null)
        private set

    private fun carregarCatalogo(): Catalogo =
        Catalogo.deJson((Conteudo.abrir(getApplication(), "exercises.json") ?: getApplication<Application>().assets.open("exercises.json")).bufferedReader().use { it.readText() })

    private fun carregarFontes(): List<Fonte> = runCatching {
        val a = JSONArray(Conteudo.abrir(getApplication(), "fontes.json")!!.bufferedReader().use { it.readText() })
        (0 until a.length()).map { a.getJSONObject(it).let { o -> Fonte(o.optString("id"), o.optString("titulo"), o.optInt("ano"), o.optString("url")) } }
    }.getOrDefault(emptyList())

    /** Procura exercícios/animações novos e versão nova do app, em segundo plano. */
    fun verificarAtualizacoes() {
        viewModelScope.launch {
            val n = withContext(Dispatchers.IO) { runCatching { Conteudo.atualizar(getApplication()) }.getOrDefault(0) }
            if (n > 0) {
                catalogo = carregarCatalogo()
                fontes = carregarFontes()
                Animacoes3D.limpar()
                loja = Loja(catalogo, Preferencias(getApplication(), if (demo) "forja_demo" else "forja")) { LocalDate.now().toEpochDay() }
                versaoConteudo = Conteudo.versaoAtual(getApplication())
                aviso = "Conteúdo atualizado: novos exercícios e animações já disponíveis."
            }
            novaVersao = withContext(Dispatchers.IO) { Conteudo.novaVersaoDoApp() }
        }
    }

    /** Salva o treino concluído e, se o Health Connect estiver conectado, grava a sessão de exercício nele. */
    fun salvarTreino(r: Registro) {
        loja.registrar(r)
        if (demo) return
        viewModelScope.launch(Dispatchers.IO) { runCatching { com.forja.app.relogio.Saude.gravarTreino(getApplication(), r) } }
    }

    /** Treino em andamento (EstadoTreino), mantido ao abrir o vídeo ou girar a tela. */
    var treino: Any? = null

    var demo: Boolean = false
        private set
    lateinit var loja: Loja
        private set

    fun iniciar(demo: Boolean) {
        if (this::loja.isInitialized && this.demo == demo) return
        this.demo = demo
        val arm = Preferencias(getApplication(), if (demo) "forja_demo" else "forja")
        loja = Loja(catalogo, arm) { LocalDate.now().toEpochDay() }
        if (demo) semearDemo() else verificarAtualizacoes()
    }

    /** Perfil e histórico de exemplo para o modo demonstração (capturas e apresentação). */
    private fun semearDemo() {
        if (loja.estado.value.temPlano) return
        val r = mapOf(
            "nome" to listOf("Kaique"), "modalidade" to listOf("academia"), "objetivo" to listOf("massa"), "experiencia" to listOf("intermediario"),
            "dias" to listOf("4"), "dias_semana" to Questionario.diasSugeridos(4).map { "$it" }, "minutos" to listOf("60"),
            "idade" to listOf("29"), "sexo" to listOf("m"), "altura" to listOf("178"), "peso" to listOf("80"),
            "limitacoes" to listOf("nenhuma"), "parq" to listOf("nenhuma"),
        )
        loja.salvarRespostas(r)
        val hoje = loja.hoje()
        // começa duas semanas atrás para já existir histórico
        val inicio = Datas.segunda(hoje) - 14
        val plano = loja.estado.value.plano ?: return
        val arm = Preferencias(getApplication(), "forja_demo")
        arm.gravar(Loja.K_INICIO, inicio.toString())
        for (w in 1..3) {
            plano.semanas[w - 1].sessoes.forEachIndexed { i, s ->
                val dia = inicio + (w - 1) * 7 + (s.diaSemana - 1)
                if (dia >= hoje) return@forEachIndexed
                val series = Roteiro.passos(s, catalogo).filter { it.item.reps != null && it.blocoNome != "Aquecimento" }.map {
                    SerieFeita(it.ex.id, 10 + (w % 2), kgExemplo(it.ex.id) + (w - 1) * 2.5)
                }
                loja.registrar(Registro(dia, w, i, s.titulo, s.tipo, s.minutos * 60, series, 7 + (i % 2), ""))
            }
        }
        listOf(81.2, 80.8, 80.5, 80.1).forEachIndexed { k, kg -> pesoEm(hoje - (3 - k) * 7L, kg) }
        iniciarDeNovo()
    }

    private fun pesoEm(dia: Long, kg: Double) {
        val arm = Preferencias(getApplication(), "forja_demo")
        val a = runCatching { JSONArray(arm.ler(Loja.K_PESOS) ?: "[]") }.getOrDefault(JSONArray())
        a.put(JSONArray().put(dia).put(kg))
        arm.gravar(Loja.K_PESOS, a.toString())
    }

    private fun iniciarDeNovo() {
        loja = Loja(catalogo, Preferencias(getApplication(), "forja_demo")) { LocalDate.now().toEpochDay() }
    }

    private fun kgExemplo(id: String): Double = when {
        "agachamento" in id || "leg" in id || "terra" in id || "stiff" in id -> 60.0
        "supino" in id || "remada" in id || "puxada" in id -> 40.0
        "desenvolvimento" in id -> 20.0
        else -> 12.0
    }
}
