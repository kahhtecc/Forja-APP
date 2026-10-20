package com.forja.app.core

import kotlin.math.roundToInt

object Datas {
    /** 1 = segunda ... 7 = domingo (1970-01-01 foi quinta). */
    fun diaSemana(epochDay: Long): Int = (Math.floorMod(epochDay + 3, 7L) + 1).toInt()
    fun segunda(epochDay: Long): Long = epochDay - (diaSemana(epochDay) - 1)
}

data class Recorde(val exId: String, val kg: Double, val reps: Int, val rm1: Double, val epochDay: Long)

object Progresso {
    fun semanaAtual(inicio: Long, hoje: Long, total: Int): Int =
        (((hoje - inicio).coerceAtLeast(0) / 7) + 1).toInt().coerceIn(1, total.coerceAtLeast(1))

    fun feitas(registros: List<Registro>, semana: Int): Set<Int> =
        registros.filter { it.semana == semana }.map { it.sessaoIdx }.toSet()

    /** Semanas seguidas (até a atual ou a anterior) em que todas as sessões previstas foram feitas. */
    fun sequenciaSemanas(registros: List<Registro>, plano: Plano, semanaAtual: Int): Int {
        fun completa(w: Int) = plano.semanas.getOrNull(w - 1)?.let { s -> feitas(registros, w).size >= s.sessoes.size } ?: false
        var w = if (completa(semanaAtual)) semanaAtual else semanaAtual - 1
        var n = 0
        while (w >= 1 && completa(w)) { n++; w-- }
        return n
    }

    /** Dias seguidos com treino registrado, contando a partir de hoje ou ontem. */
    fun sequenciaDias(registros: List<Registro>, hoje: Long): Int {
        val dias = registros.map { it.epochDay }.toSet()
        var d = if (hoje in dias) hoje else hoje - 1
        var n = 0
        while (d in dias) { n++; d-- }
        return n
    }

    fun minutosPorSemana(registros: List<Registro>, hoje: Long, semanas: Int = 8): List<Pair<Long, Int>> {
        val seg = Datas.segunda(hoje)
        return (semanas - 1 downTo 0).map { k ->
            val ini = seg - 7L * k
            ini to registros.filter { it.epochDay in ini until ini + 7 }.sumOf { it.duracaoSeg } / 60
        }
    }

    fun volumeKg(r: Registro): Double = r.series.sumOf { it.kg * it.reps }

    fun epley(kg: Double, reps: Int): Double = if (reps <= 1) kg else kg * (1 + reps / 30.0)

    fun recordes(registros: List<Registro>): List<Recorde> =
        registros.flatMap { r -> r.series.filter { it.kg > 0 && it.reps > 0 }.map { r.epochDay to it } }
            .groupBy { it.second.exId }
            .map { (id, l) ->
                val (dia, s) = l.maxBy { epley(it.second.kg, it.second.reps) }
                Recorde(id, s.kg, s.reps, epley(s.kg, s.reps), dia)
            }
            .sortedByDescending { it.epochDay }

    fun ultimas(registros: List<Registro>, exId: String): List<SerieFeita> =
        registros.sortedByDescending { it.epochDay }.firstOrNull { r -> r.series.any { it.exId == exId } }
            ?.series?.filter { it.exId == exId }.orEmpty()

    /** Sugestão de carga pela dupla progressão. */
    fun sugestao(registros: List<Registro>, item: Item): String? {
        val ult = ultimas(registros, item.exId).filter { it.kg > 0 }
        if (ult.isEmpty() || item.reps == null) return null
        val topo = item.reps.split("–", "-").lastOrNull()?.trim()?.toIntOrNull() ?: return null
        val kg = ult.maxOf { it.kg }
        val bateu = ult.all { it.reps >= topo }
        return if (bateu) {
            val novo = (kg * 1.05 / 0.5).roundToInt() * 0.5
            "Você bateu o topo da faixa com ${fmtKg(kg)} kg. Tente ${fmtKg(maxOf(novo, kg + 1.0))} kg."
        } else "Última vez: ${ult.joinToString(" · ") { "${it.reps}×${fmtKg(it.kg)}" }} kg. Busque mais repetições."
    }

    fun fmtKg(kg: Double): String = if (kg % 1.0 == 0.0) kg.toInt().toString() else "%.1f".format(kg).replace('.', ',')
}
