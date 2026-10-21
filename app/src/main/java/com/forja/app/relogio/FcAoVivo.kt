package com.forja.app.relogio

import android.content.Context
import kotlinx.coroutines.flow.MutableStateFlow

/** Frequência cardíaca ao vivo (cinta/relógio por Bluetooth) e amostras do treino em andamento. */
object FcAoVivo {
    val bpm = MutableStateFlow<Int?>(null)
    @Volatile var ultimoMs = 0L
        private set
    @Volatile var fonte: String? = null
        private set
    private val amostras = mutableListOf<Int>()
    @Volatile private var gravando = false

    fun receber(v: Int, origem: String) {
        if (v !in 25..240) return
        ultimoMs = System.currentTimeMillis()
        fonte = origem
        bpm.value = v
        if (gravando) synchronized(amostras) { amostras += v }
    }

    /** BPM se a última leitura tiver menos de 10 s. */
    fun atual(agora: Long = System.currentTimeMillis()): Int? = bpm.value?.takeIf { agora - ultimoMs < 10_000 }

    fun comecarTreino() = synchronized(amostras) { amostras.clear(); gravando = true }

    /** Média e máxima das leituras do treino (0 quando não houve leitura). */
    fun resumo(): Pair<Int, Int> = synchronized(amostras) {
        if (amostras.isEmpty()) 0 to 0 else amostras.average().toInt() to amostras.max()
    }

    fun pararTreino() { gravando = false }
}

/** Preferências do relógio / saúde (fora do núcleo: são deste aparelho). */
object PrefsRelogio {
    private fun sp(ctx: Context) = ctx.getSharedPreferences("forja_relogio", Context.MODE_PRIVATE)
    fun mostrar(ctx: Context) = sp(ctx).getBoolean("mostrar", true)
    fun setMostrar(ctx: Context, v: Boolean) = sp(ctx).edit().putBoolean("mostrar", v).apply()
    fun pediuPermissoes(ctx: Context) = sp(ctx).getBoolean("pediu", false)
    fun marcarPediu(ctx: Context) = sp(ctx).edit().putBoolean("pediu", true).apply()
    fun ble(ctx: Context): Pair<String, String>? = sp(ctx).getString("ble_end", null)?.let { it to (sp(ctx).getString("ble_nome", null) ?: "Monitor cardíaco") }
    fun setBle(ctx: Context, endereco: String?, nome: String?) = sp(ctx).edit().putString("ble_end", endereco).putString("ble_nome", nome).apply()
}
