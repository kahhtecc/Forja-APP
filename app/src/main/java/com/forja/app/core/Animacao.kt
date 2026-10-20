package com.forja.app.core

import org.json.JSONArray
import org.json.JSONObject
import kotlin.math.PI
import kotlin.math.cos
import kotlin.math.min
import kotlin.math.sin

/**
 * Animações demonstrativas: esqueleto 2D com ângulos absolutos (0 = para baixo, 90 = para frente).
 * Mesmo modelo de tools/anim/esqueleto.py (as prévias dos agentes usam o mesmo cálculo).
 */
data class Pose(
    val x: Double = 0.0,
    val y: Double? = null,
    val ay: Double = 0.0,
    val t: Double = 180.0,
    val c: Double = 180.0,
    val bf: DoubleArray = doubleArrayOf(0.0, 0.0),
    val bt: DoubleArray = doubleArrayOf(0.0, 0.0),
    val pf: DoubleArray = doubleArrayOf(0.0, 0.0, 90.0),
    val pt: DoubleArray = doubleArrayOf(0.0, 0.0, 90.0),
)

data class Acessorio(val tipo: String, val x: Double, val y: Double, val w: Double, val h: Double, val ate: Pair<Double, Double>?, val atePes: Boolean)

data class Animacao(
    val id: String,
    val quadros: List<Pose>,
    val tempos: List<Double>,
    val destaque: Set<String>,
    val props: List<Acessorio>,
    val fixo: String?,
) {
    val duracao: Double get() = tempos.sum().coerceAtLeast(0.1)
}

object Esqueleto {
    const val TRONCO = 5.2
    const val PESCOCO = 0.7
    const val CABECA = 1.0
    const val BRACO = 3.0
    const val ANTEBRACO = 2.7
    const val COXA = 4.4
    const val CANELA = 4.3
    const val PE = 1.5

    private fun v(ang: Double, comp: Double): Pair<Double, Double> {
        val r = ang * PI / 180.0
        return sin(r) * comp to -cos(r) * comp
    }

    private operator fun Pair<Double, Double>.plus(o: Pair<Double, Double>) = (first + o.first) to (second + o.second)

    /** Articulações da pose, já apoiadas no chão. Chaves iguais às do Python. */
    fun pontos(p: Pose, fixo: String? = null, refX: Double? = null): Map<String, Pair<Double, Double>> {
        val quadril = p.x to 0.0
        val pescoco = quadril + v(p.t, TRONCO)
        val ombro = quadril + v(p.t, TRONCO * 0.92)
        val cabeca = pescoco + v(p.c, PESCOCO + CABECA)
        val j = linkedMapOf("quadril" to quadril, "pescoco" to pescoco, "ombro" to ombro, "cabeca" to cabeca)
        for ((lado, b, pr) in listOf(Triple("f", p.bf, p.pf), Triple("t", p.bt, p.pt))) {
            val cot = ombro + v(b[0], BRACO)
            val mao = cot + v(b[1], ANTEBRACO)
            val joe = quadril + v(pr[0], COXA)
            val tor = joe + v(pr[1], CANELA)
            val ponta = tor + v(pr[2], PE)
            val calc = tor + v(pr[2] + 180, PE * 0.25)
            j["cotovelo_$lado"] = cot; j["mao_$lado"] = mao; j["joelho_$lado"] = joe
            j["tornozelo_$lado"] = tor; j["ponta_$lado"] = ponta; j["calcanhar_$lado"] = calc
        }
        var dy = p.y ?: -(j.filterKeys { it != "cabeca" }.values.minOf { it.second }.coerceAtMost(cabeca.second - CABECA))
        dy += p.ay
        var dx = 0.0
        if ((fixo == "pes" || fixo == "maos") && refX != null) dx = refX - j[if (fixo == "pes") "tornozelo_f" else "mao_f"]!!.first
        return j.mapValues { (_, v) -> (v.first + dx) to (v.second + dy) }
    }

    fun pontos(a: Animacao, p: Pose): Map<String, Pair<Double, Double>> {
        val ref = if (a.fixo == "pes" || a.fixo == "maos") pontos(a.quadros[0])[if (a.fixo == "pes") "tornozelo_f" else "mao_f"]!!.first else null
        return pontos(p, a.fixo, ref)
    }

    private fun lerp(a: Double, b: Double, e: Double) = a + (b - a) * e
    private fun lerp(a: DoubleArray, b: DoubleArray, e: Double) = DoubleArray(a.size) { lerp(a[it], b.getOrElse(it) { a[it] }, e) }

    fun interpolar(a: Pose, b: Pose, t: Double): Pose {
        val e = t * t * (3 - 2 * t)
        return Pose(
            lerp(a.x, b.x, e), if (a.y == null || b.y == null) null else lerp(a.y, b.y, e), lerp(a.ay, b.ay, e),
            lerp(a.t, b.t, e), lerp(a.c, b.c, e), lerp(a.bf, b.bf, e), lerp(a.bt, b.bt, e), lerp(a.pf, b.pf, e), lerp(a.pt, b.pt, e),
        )
    }

    /** Pose no instante [seg] do loop. */
    fun poseEm(a: Animacao, seg: Double): Pose {
        val n = a.quadros.size
        if (n == 1) return a.quadros[0]
        var t = seg % a.duracao
        for (i in 0 until n) {
            val d = a.tempos.getOrElse(i) { 1.0 }.coerceAtLeast(0.05)
            if (t <= d) return interpolar(a.quadros[i], a.quadros[(i + 1) % n], t / d)
            t -= d
        }
        return a.quadros[0]
    }

    /** Caixa que contém todas as poses (para enquadrar a animação). xmin, ymin, xmax, ymax. */
    fun caixa(a: Animacao): DoubleArray {
        var x0 = Double.MAX_VALUE; var y0 = 0.0; var x1 = -Double.MAX_VALUE; var y1 = -Double.MAX_VALUE
        val amostras = (0..23).map { poseEm(a, a.duracao * it / 24.0) }
        for (p in amostras) {
            val pts = pontos(a, p)
            for ((k, v) in pts) {
                val r = if (k == "cabeca") CABECA else 0.4
                x0 = min(x0, v.first - r); x1 = maxOf(x1, v.first + r); y1 = maxOf(y1, v.second + r)
            }
        }
        for (pr in a.props) when (pr.tipo) {
            "banco", "maquina", "caixa" -> { x0 = min(x0, pr.x); x1 = maxOf(x1, pr.x + pr.w); y1 = maxOf(y1, pr.y + pr.h) }
            "barra_fixa" -> { y1 = maxOf(y1, pr.y + 0.5); x0 = min(x0, pr.x - 2); x1 = maxOf(x1, pr.x + 2) }
            "saco" -> { x1 = maxOf(x1, pr.x + 1.5) }
            else -> {}
        }
        return doubleArrayOf(x0, y0, x1, y1)
    }
}

object Animacoes {
    fun deJson(texto: String): Map<String, Animacao> {
        val arr = JSONArray(texto)
        val out = LinkedHashMap<String, Animacao>()
        for (i in 0 until arr.length()) {
            val o = arr.getJSONObject(i)
            runCatching { lerAnimacao(o) }.getOrNull()?.let { out[it.id] = it }
        }
        return out
    }

    private fun nums(o: JSONObject, k: String, padrao: DoubleArray): DoubleArray {
        val a = o.optJSONArray(k) ?: return padrao
        return DoubleArray(padrao.size) { if (it < a.length()) a.optDouble(it, padrao[it]) else padrao[it] }
    }

    fun lerAnimacao(o: JSONObject): Animacao {
        val qs = o.getJSONArray("quadros")
        val quadros = (0 until qs.length()).map { i ->
            val q = qs.getJSONObject(i)
            Pose(
                x = q.optDouble("x", 0.0), y = if (q.has("y") && !q.isNull("y")) q.getDouble("y") else null, ay = q.optDouble("ay", 0.0),
                t = q.optDouble("t", 180.0), c = q.optDouble("c", 180.0),
                bf = nums(q, "bf", doubleArrayOf(0.0, 0.0)), bt = nums(q, "bt", doubleArrayOf(0.0, 0.0)),
                pf = nums(q, "pf", doubleArrayOf(0.0, 0.0, 90.0)), pt = nums(q, "pt", doubleArrayOf(0.0, 0.0, 90.0)),
            )
        }
        require(quadros.isNotEmpty())
        val tp = o.optJSONArray("tempos")
        val tempos = (0 until quadros.size).map { tp?.optDouble(it, 1.0) ?: 1.0 }
        val ds = o.optJSONArray("destaque")
        val props = o.optJSONArray("props")?.let { a ->
            (0 until a.length()).map { i ->
                val p = a.getJSONObject(i)
                val ate = p.opt("ate")
                Acessorio(
                    p.optString("tipo"), p.optDouble("x", 0.0), p.optDouble("y", 0.0), p.optDouble("w", 8.0), p.optDouble("h", 4.0),
                    (ate as? JSONArray)?.let { it.optDouble(0) to it.optDouble(1) }, ate == "pes",
                )
            }
        }.orEmpty()
        return Animacao(
            o.getString("id"), quadros, tempos,
            ds?.let { d -> (0 until d.length()).map { d.getString(it) }.toSet() }.orEmpty(), props,
            o.optString("fixo").takeIf { it == "pes" || it == "maos" },
        )
    }
}
