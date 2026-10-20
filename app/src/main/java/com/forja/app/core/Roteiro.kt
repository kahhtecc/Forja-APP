package com.forja.app.core

/** Um passo do player: uma série (ou rodada) de um exercício, seguida de descanso. */
data class Passo(
    val blocoIdx: Int,
    val itemIdx: Int,
    val blocoNome: String,
    val tipoBloco: TipoBloco,
    val ex: Exercicio,
    val item: Item,
    /** Série atual (ou volta, em circuitos) começando em 1. */
    val serie: Int,
    val totalSeries: Int,
    val circuito: Boolean,
    val descansoDepois: Int,
) {
    val porTempo: Boolean get() = item.trabalhoSeg != null
    val rotulo: String get() = if (circuito) "Volta $serie de $totalSeries" else if (totalSeries > 1) "Série $serie de $totalSeries" else "Série única"
}

object Roteiro {
    /** Tempo médio de uma série por repetições (execução + preparo). */
    const val SEG_SERIE_REPS = 40

    fun passos(s: Sessao, cat: Catalogo): List<Passo> {
        val out = mutableListOf<Passo>()
        s.blocos.forEachIndexed { bi, b ->
            if (b.tipo == TipoBloco.CIRCUITO) {
                for (v in 1..b.voltas) b.itens.forEachIndexed { ii, it ->
                    val ex = cat[it.exId] ?: return@forEachIndexed
                    val ultimoDaVolta = ii == b.itens.lastIndex
                    val desc = if (ultimoDaVolta && v < b.voltas) maxOf(it.descansoSeg, 60) else it.descansoSeg
                    out += Passo(bi, ii, b.nome, b.tipo, ex, it, v, b.voltas, true, desc)
                }
            } else {
                b.itens.forEachIndexed { ii, it ->
                    val ex = cat[it.exId] ?: return@forEachIndexed
                    for (sr in 1..it.series) out += Passo(bi, ii, b.nome, b.tipo, ex, it, sr, it.series, false, it.descansoSeg)
                }
            }
        }
        if (out.isNotEmpty()) out[out.lastIndex] = out.last().copy(descansoDepois = 0)
        return out
    }

    fun segundosItem(it: Item, ex: Exercicio?): Int {
        val trabalho = it.trabalhoSeg ?: SEG_SERIE_REPS
        return it.series * trabalho + (it.series - 1).coerceAtLeast(0) * it.descansoSeg
    }

    fun segundos(passos: List<Passo>): Int = passos.sumOf { (it.item.trabalhoSeg ?: SEG_SERIE_REPS) + it.descansoDepois }

    fun minutos(s: Sessao, cat: Catalogo): Int {
        val p = passos(s, cat)
        // + ~15 s de transição por exercício diferente
        val trocas = p.map { it.blocoIdx to it.itemIdx }.distinct().size * 15
        return ((segundos(p) + trocas) / 60.0).let { kotlin.math.ceil(it).toInt() }.coerceAtLeast(5)
    }

    fun exerciciosDaSessao(s: Sessao): List<String> = s.blocos.flatMap { b -> b.itens.map { it.exId } }.distinct()

    fun formatarTempo(seg: Int): String = when {
        seg >= 3600 -> "%dh%02d".format(seg / 3600, (seg % 3600) / 60)
        seg >= 60 && seg % 60 == 0 -> "${seg / 60} min"
        seg >= 60 -> "%d:%02d".format(seg / 60, seg % 60)
        else -> "$seg s"
    }

    /** Texto curto da prescrição: "4 × 8–12", "6 × 1 min / 2 min", "45 min". */
    fun prescricao(it: Item, circuito: Boolean = false, voltas: Int = 1): String {
        val n = if (circuito) voltas else it.series
        if (circuito) return it.reps ?: it.trabalhoSeg?.let { t -> formatarTempo(t) } ?: ""
        return when {
            it.reps != null -> "$n × ${it.reps}"
            it.trabalhoSeg != null && n == 1 -> formatarTempo(it.trabalhoSeg)
            it.trabalhoSeg != null && it.descansoSeg > 0 && !circuito -> "$n × ${formatarTempo(it.trabalhoSeg)} / ${formatarTempo(it.descansoSeg)}"
            it.trabalhoSeg != null -> "$n × ${formatarTempo(it.trabalhoSeg)}"
            else -> "$n séries"
        }
    }
}
