package com.forja.app.core

import kotlin.math.ceil
import kotlin.math.max
import kotlin.math.min
import kotlin.math.roundToInt

/**
 * Monta a rotina a partir do perfil. Determinístico: o mesmo perfil gera sempre o mesmo plano
 * (assim só as respostas precisam ser salvas).
 * Parâmetros baseados em ACSM (2009, 2021), OMS (2020), Schoenfeld et al. (2017), Seiler (2010),
 * zonas de Coggan e NSCA — ver "Base científica" no app.
 */
class Gerador(private val cat: Catalogo) {

    fun gerar(p: Perfil): Plano {
        val plano = when (p.modalidade) {
            Modalidade.ACADEMIA, Modalidade.CASA_CORPO, Modalidade.CASA_ELASTICO -> planoForca(p)
            Modalidade.CORRIDA -> planoCorrida(p)
            Modalidade.BIKE -> planoBike(p)
            Modalidade.LUTA -> planoLuta(p)
            Modalidade.ATLETA -> planoAtleta(p)
            Modalidade.HIIT -> planoHiit(p)
            Modalidade.HIBRIDO -> planoHibrido(p)
            Modalidade.MOBILIDADE -> planoMobilidade(p)
            Modalidade.LONGEVIDADE -> planoLongevidade(p)
        }
        val semanas = plano.semanas.map { s -> s.copy(sessoes = s.sessoes.map { it.copy(minutos = Roteiro.minutos(it, cat)) }) }
        val sem1 = semanas.first().sessoes
        val meta = "${sem1.size} treinos · ~${sem1.sumOf { it.minutos }} min por semana"
        return plano.copy(semanas = semanas, alertas = alertas(p) + plano.alertas, dicas = plano.dicas + DICAS_GERAIS, metaSemanal = meta)
    }

    // ------------------------------------------------------------------ seleção de exercícios

    private inner class Seletor(val p: Perfil, val equip: Set<String> = p.equip, val nivelMax: Int = nivelMaximo(p)) {
        private fun disponivel(e: Exercicio): Boolean {
            if (e.evitar.any { it in p.evitar }) return false
            if (e.nivel > nivelMax) return false
            if ("barra_fixa" in e.equip && "corpo" !in e.equip) return "barra_fixa" in equip
            return e.equip.any { it in equip }
        }

        private fun pontos(e: Exercicio): Int {
            var s = 0
            val academia = !p.emCasa && p.modalidade !in setOf(Modalidade.CASA_CORPO, Modalidade.CASA_ELASTICO)
            for (q in e.equip) s = max(s, when (q) {
                "barra" -> if (academia) 4 else 0
                "maquina", "polia" -> if (academia) 3 else 0
                "halter" -> if (academia) 3 else 3
                "kettlebell" -> 2
                "elastico" -> if (p.modalidade == Modalidade.CASA_ELASTICO) 5 else if (academia) -2 else 1
                "barra_fixa" -> 3
                "corpo" -> if (academia) 0 else 2
                else -> 0
            })
            if (e.id in CLASSICOS) s += 2
            if (p.nivel == Nivel.INICIANTE && e.nivel == 1) s += 2
            if (p.nivel == Nivel.AVANCADO && e.nivel >= 2) s += 1
            return s
        }

        fun pool(padrao: String): List<Exercicio> =
            cat.exercicios.filter { padrao in it.padroes && disponivel(it) }
                .sortedWith(compareByDescending<Exercicio> { pontos(it) }.thenBy { it.nivel }.thenBy { it.id })

        /** Escolhe um exercício do padrão, usando a variante para alternar entre opções. */
        fun escolher(padrao: String, variante: Int, usados: MutableSet<String>): Exercicio? {
            for (pd in listOf(padrao) + FALLBACK[padrao].orEmpty()) {
                val pl = pool(pd).filter { it.id !in usados }
                if (pl.isNotEmpty()) {
                    val e = pl[variante.mod(pl.size)]
                    usados += e.id
                    return e
                }
            }
            return null
        }

        fun primeiro(vararg ids: String, usados: MutableSet<String> = mutableSetOf()): Exercicio? =
            ids.mapNotNull { cat[it] }.firstOrNull { disponivel(it) && it.id !in usados }?.also { usados += it.id }
    }

    private fun nivelMaximo(p: Perfil) = when {
        p.modalidade == Modalidade.LONGEVIDADE && p.nivel == Nivel.INICIANTE -> 1
        p.nivel == Nivel.INICIANTE || p.gestante || p.idade >= 65 -> 2
        else -> 3
    }

    // ------------------------------------------------------------------ doses de força

    data class Dose(val series: Int, val rMin: Int, val rMax: Int, val descanso: Int, val rir: String)

    private fun dose(obj: Objetivo, n: Nivel, principal: Boolean): Dose = when (obj) {
        Objetivo.MASSA -> when (n) {
            Nivel.INICIANTE -> Dose(3, 10, 12, 75, "RIR 2–3")
            Nivel.INTERMEDIARIO -> if (principal) Dose(4, 6, 10, 120, "RIR 1–2") else Dose(3, 10, 12, 75, "RIR 1–2")
            Nivel.AVANCADO -> if (principal) Dose(4, 6, 8, 150, "RIR 0–2") else Dose(3, 10, 15, 75, "RIR 0–1")
        }
        Objetivo.FORCA, Objetivo.PERFORMANCE -> when (n) {
            Nivel.INICIANTE -> if (principal) Dose(3, 6, 8, 120, "RIR 2–3") else Dose(2, 10, 12, 75, "RIR 2")
            Nivel.INTERMEDIARIO -> if (principal) Dose(4, 4, 6, 180, "RIR 1–2") else Dose(3, 8, 10, 90, "RIR 2")
            Nivel.AVANCADO -> if (principal) Dose(5, 3, 5, 210, "RIR 1–2") else Dose(3, 6, 10, 120, "RIR 1–2")
        }
        Objetivo.EMAGRECER -> when (n) {
            Nivel.INICIANTE -> Dose(2, 12, 15, 45, "RIR 2–3")
            Nivel.INTERMEDIARIO -> Dose(3, 10, 15, 45, "RIR 1–2")
            Nivel.AVANCADO -> Dose(if (principal) 4 else 3, 8, 12, 60, "RIR 1–2")
        }
        Objetivo.SAUDE -> when (n) {
            Nivel.INICIANTE -> Dose(2, 10, 15, 60, "RIR 3")
            Nivel.INTERMEDIARIO -> Dose(3, 10, 12, 60, "RIR 2")
            Nivel.AVANCADO -> Dose(3, 8, 12, 75, "RIR 1–2")
        }
        Objetivo.RESISTENCIA -> Dose(if (n == Nivel.INICIANTE) 2 else 3, 15, 20, 40, "RIR 2")
    }

    /** Fase de cada semana de um bloco de 8 semanas (deload na 4 e na 8). */
    data class FaseSemana(val nome: String, val nota: String, val extraSerie: Boolean, val deload: Boolean, val variante: Int, val volume: Double)

    private fun faseForca(semana: Int, n: Nivel): FaseSemana = when (semana) {
        1 -> FaseSemana("Adaptação", "Cargas confortáveis: foque na técnica e no ritmo (2 s descendo).", false, false, 0, 1.0)
        2 -> FaseSemana("Construção", "Dupla progressão: bateu o topo das repetições em todas as séries? Suba 2–5% a carga.", false, false, 0, 1.0)
        3 -> FaseSemana("Construção", "+1 série nos exercícios principais. Mantenha a margem de repetições (RIR).", n != Nivel.INICIANTE, false, 0, 1.0)
        4 -> FaseSemana("Semana leve", "Deload: ~40% menos séries e carga um pouco menor. Recuperar também é treino.", false, true, 0, 0.6)
        5 -> FaseSemana("Intensificação", "Novas variações de exercícios. Recomece com cargas que deixem 2–3 repetições de reserva.", false, false, 1, 1.0)
        6 -> FaseSemana("Intensificação", "Progrida a carga sempre que completar o topo da faixa.", false, false, 1, 1.0)
        7 -> FaseSemana("Pico", "+1 série nos principais. Semana mais exigente do bloco.", true, false, 1, 1.0)
        else -> FaseSemana("Semana leve & reteste", "Volume reduzido. No último treino, teste suas cargas para o próximo bloco.", false, true, 1, 0.6)
    }

    private fun reps(d: Dose) = if (d.rMin == d.rMax) "${d.rMin}" else "${d.rMin}–${d.rMax}"

    // ------------------------------------------------------------------ blocos padrão

    private fun aquecimento(p: Perfil, foco: String, usados: MutableSet<String>): Bloco {
        val sel = Seletor(p, nivelMax = 3)
        val cardio = when {
            "bike" in p.equip && ("impacto" in p.evitar || !p.emCasa) -> cat["bike-leve"]
            !p.emCasa && "impacto" !in p.evitar -> cat["eliptico"]
            "impacto" !in p.evitar && "corda" in p.equip -> cat["corda"]
            "impacto" !in p.evitar -> cat["polichinelo"]
            else -> cat["caminhada"]
        }!!
        val itens = mutableListOf(Item(cardio.id, 1, trabalhoSeg = 180, descansoSeg = 0, intensidade = "Leve · 3/10", nota = if (cardio.id == "caminhada") "Pode ser marcha no lugar" else null))
        val mob = when (foco) {
            "superior" -> listOf("circulos-braco", "rotacao-toracica", "band-pull-apart")
            "inferior" -> listOf("circulos-quadril", "maior-alongamento", "ponte-gluteo")
            "corrida" -> listOf("circulos-quadril", "maior-alongamento", "educativos-corrida")
            else -> listOf("circulos-quadril", "maior-alongamento", "circulos-braco")
        }
        for (id in mob) {
            val e = sel.primeiro(id, usados = usados) ?: continue
            itens += if (e.porTempo) Item(e.id, 1, trabalhoSeg = 45, descansoSeg = 0) else Item(e.id, 1, reps = "12", descansoSeg = 15, intensidade = "Ativação")
        }
        return Bloco("Aquecimento", TipoBloco.AQUECIMENTO, itens, nota = "Eleve a temperatura e prepare as articulações.")
    }

    private fun desaquecimento(foco: String): Bloco {
        val ids = when (foco) {
            "superior" -> listOf("alongamento-peito", "postura-crianca")
            "inferior", "corrida" -> listOf("alongamento-panturrilha", "flexor-quadril", "alongamento-posterior")
            "bike" -> listOf("flexor-quadril", "alongamento-quadriceps", "alongamento-posterior")
            else -> listOf("postura-crianca", "flexor-quadril", "alongamento-posterior")
        }
        return Bloco("Volta à calma", TipoBloco.DESAQUECIMENTO, ids.map { Item(it, 1, trabalhoSeg = if (it in BILATERAL) 60 else 40, descansoSeg = 0, nota = if (it in BILATERAL) "30 s cada lado" else null) })
    }

    /** Bloco principal de força a partir de padrões ("padrao" ou "padrao:variante"). */
    private fun blocoForca(
        p: Perfil, slots: List<String>, fase: FaseSemana, minutosPrincipal: Int, usados: MutableSet<String>,
        sel: Seletor = Seletor(p), obj: Objetivo = p.objetivo, principais: Int = 2, nome: String = "Treino principal",
    ): Bloco {
        val itens = mutableListOf<Item>()
        var tempo = 0
        for ((i, slot) in slots.withIndex()) {
            val (padrao, v) = slot.split(":").let { it[0] to (it.getOrNull(1)?.toIntOrNull() ?: 0) }
            val e = sel.escolher(padrao, v + fase.variante, usados) ?: continue
            val principal = i < principais
            val d = dose(obj, p.nivel, principal)
            var series = d.series + if (fase.extraSerie && principal) 1 else 0
            if (fase.deload) series = max(1, ceil(series * fase.volume).toInt())
            series = min(series, 5)
            val item = if (e.porTempo) {
                val seg = when {
                    e.id == "farmer-walk" -> 40
                    p.nivel == Nivel.INICIANTE -> 25
                    p.nivel == Nivel.INTERMEDIARIO -> 40
                    else -> 50
                }
                Item(e.id, series, trabalhoSeg = seg, descansoSeg = min(d.descanso, 60), intensidade = if (fase.deload) "Leve" else "Firme, sem perder a postura")
            } else {
                val semCarga = e.equip.all { it in setOf("corpo", "banco", "barra_fixa") }
                Item(e.id, series, reps = reps(d), descansoSeg = d.descanso, intensidade = if (fase.deload) (if (semCarga) "Mais leve · RIR 4" else "RIR 4 · carga −10%") else d.rir)
            }
            val custo = Roteiro.segundosItem(item, e) + 60
            if (itens.size >= 3 && tempo + custo > minutosPrincipal * 60) break
            tempo += custo
            itens += item
        }
        return Bloco(nome, TipoBloco.PRINCIPAL, itens, nota = "Descanse o tempo indicado entre as séries.")
    }

    private fun finalizador(p: Perfil, usados: MutableSet<String>, voltas: Int, trabalho: Int = 30, descanso: Int = 30): Bloco? {
        val sel = Seletor(p)
        val ids = listOfNotNull(
            sel.escolher("condicionamento", 0, usados), sel.escolher("core", 1, usados), sel.escolher("condicionamento", 1, usados),
        )
        if (ids.size < 2) return null
        return Bloco("Finalizador metabólico", TipoBloco.CIRCUITO, ids.map { Item(it.id, 1, trabalhoSeg = trabalho, descansoSeg = descanso, intensidade = "Forte · 8/10") }, voltas = voltas,
            nota = "$trabalho s de esforço, $descanso s de pausa. Mantenha a técnica.")
    }

    private fun sessaoCardioLeve(p: Perfil, dia: Int, minutos: Int, titulo: String = "Cardio Z2", nota: String = "Ritmo em que você consegue conversar."): Sessao {
        val ex = when {
            !p.emCasa && "impacto" in p.evitar -> "bike-leve"
            !p.emCasa -> if (p.nivel == Nivel.INICIANTE) "eliptico" else "corrida-leve"
            "bike" in p.equip -> "bike-leve"
            "esteira" in p.equip && "impacto" !in p.evitar && p.nivel != Nivel.INICIANTE -> "corrida-leve"
            else -> "caminhada"
        }
        val corpo = max(15, minutos - 5)
        return Sessao(titulo, "Base aeróbica", "cardio", minutos, listOf(
            Bloco("Cardio contínuo", TipoBloco.PRINCIPAL, listOf(Item(ex, 1, trabalhoSeg = corpo * 60, descansoSeg = 0, intensidade = "Zona 2 · 3–4/10", nota = nota))),
            desaquecimento("inferior"),
        ), dia)
    }

    private fun sessaoMobilidade(p: Perfil, dia: Int, foco: Int, hold: Int, titulo: String? = null): Sessao {
        val fluxos = listOf(
            "Coluna & quadril" to listOf("gato-camelo", "maior-alongamento", "flexor-quadril", "rotacao-toracica", "postura-crianca", "alongamento-adutores"),
            "Ombros & torácica" to listOf("circulos-braco", "rotacao-toracica", "alongamento-peito", "band-pull-apart", "gato-camelo", "postura-crianca"),
            "Pernas & posterior" to listOf("circulos-quadril", "alongamento-posterior", "alongamento-quadriceps", "alongamento-panturrilha", "alongamento-adutores", "flexor-quadril"),
            "Fluxo completo" to listOf("inchworm", "maior-alongamento", "gato-camelo", "rotacao-toracica", "flexor-quadril", "alongamento-posterior", "postura-crianca"),
            "Liberação & equilíbrio" to listOf("rolo-quadriceps", "rolo-panturrilha", "rolo-it", "equilibrio-unipodal", "alongamento-adutores", "postura-crianca"),
        )
        val (nome, ids) = fluxos[foco.mod(fluxos.size)]
        val sel = Seletor(p, nivelMax = 3)
        val usados = mutableSetOf<String>()
        val escolhidos = ids.mapNotNull { id -> sel.primeiro(id, usados = usados) }
        val porVolta = escolhidos.sumOf { e -> (if (!e.porTempo) 40 else if (e.id in BILATERAL) hold * 2 else hold) + 15 }
        val series = (p.minutos * 60.0 / porVolta.coerceAtLeast(1)).roundToInt().coerceIn(2, 4)
        val itens = escolhidos.map { e ->
                if (e.porTempo) Item(e.id, series, trabalhoSeg = if (e.id in BILATERAL) hold * 2 else hold, descansoSeg = 10, intensidade = "Alongamento confortável", nota = if (e.id in BILATERAL) "${hold} s cada lado" else null)
                else Item(e.id, series, reps = "10–12", descansoSeg = 20, intensidade = "Controle")
            }
        return Sessao(titulo ?: "Mobilidade · $nome", nome, "mobilidade", 0, listOf(
            Bloco("Fluxo de mobilidade", TipoBloco.PRINCIPAL, itens, nota = "Respire fundo e solte o ar devagar em cada posição. Sem dor."),
        ), dia)
    }

    // ------------------------------------------------------------------ musculação (academia / casa)

    private val FULL_A = listOf("agachar", "empurrar_h", "puxar_h", "gluteo", "empurrar_v", "ombro_post", "core")
    private val FULL_B = listOf("dobradica", "puxar_v", "empurrar_v:1", "unilateral", "biceps", "triceps", "core:1")
    private val FULL_C = listOf("unilateral:1", "empurrar_h:1", "puxar_h:1", "gluteo:1", "ombro_lat", "panturrilha", "core:2")
    private val UPPER_A = listOf("empurrar_h", "puxar_h", "empurrar_v", "puxar_v", "ombro_lat", "biceps", "triceps")
    private val LOWER_A = listOf("agachar", "dobradica", "unilateral", "posterior", "panturrilha", "core")
    private val UPPER_B = listOf("puxar_v:1", "empurrar_h:1", "puxar_h:1", "empurrar_v:1", "ombro_post", "triceps:1", "biceps:1")
    private val LOWER_B = listOf("dobradica:1", "agachar:1", "gluteo", "quadriceps", "panturrilha:1", "core:1")
    private val PUSH = listOf("empurrar_h", "empurrar_v", "empurrar_h:1", "peito_iso", "ombro_lat", "triceps", "triceps:1")
    private val PULL = listOf("puxar_v", "puxar_h", "puxar_h:1", "ombro_post", "trapezio", "biceps", "biceps:1")
    private val LEGS = listOf("agachar", "dobradica", "unilateral", "quadriceps", "posterior", "gluteo", "panturrilha")

    private data class Modelo(val titulo: String, val foco: String, val aq: String, val slots: List<String>, val variante: Int = 0)

    private fun divisao(dias: Int): Pair<String, List<Modelo>> = when (dias) {
        1, 2 -> "Full body A/B" to listOf(Modelo("Corpo inteiro A", "Corpo inteiro", "total", FULL_A), Modelo("Corpo inteiro B", "Corpo inteiro", "total", FULL_B))
        3 -> "Full body A/B/C" to listOf(Modelo("Corpo inteiro A", "Corpo inteiro", "total", FULL_A), Modelo("Corpo inteiro B", "Corpo inteiro", "total", FULL_B), Modelo("Corpo inteiro C", "Corpo inteiro", "total", FULL_C))
        4 -> "Superior/Inferior" to listOf(Modelo("Superiores A", "Peito, costas e ombros", "superior", UPPER_A), Modelo("Inferiores A", "Pernas e glúteos", "inferior", LOWER_A),
            Modelo("Superiores B", "Costas, peito e braços", "superior", UPPER_B), Modelo("Inferiores B", "Posterior e glúteos", "inferior", LOWER_B))
        5 -> "Superior/Inferior + Push/Pull/Legs" to listOf(Modelo("Superiores", "Peito, costas e ombros", "superior", UPPER_A), Modelo("Inferiores", "Pernas e glúteos", "inferior", LOWER_A),
            Modelo("Empurrar", "Peito, ombros e tríceps", "superior", PUSH, 1), Modelo("Puxar", "Costas e bíceps", "superior", PULL, 1), Modelo("Pernas", "Quadríceps, posterior e glúteos", "inferior", LEGS, 1))
        else -> "Push/Pull/Legs 2x" to listOf(Modelo("Empurrar A", "Peito, ombros e tríceps", "superior", PUSH), Modelo("Puxar A", "Costas e bíceps", "superior", PULL), Modelo("Pernas A", "Quadríceps, posterior e glúteos", "inferior", LEGS),
            Modelo("Empurrar B", "Peito, ombros e tríceps", "superior", PUSH, 1), Modelo("Puxar B", "Costas e bíceps", "superior", PULL, 1), Modelo("Pernas B", "Posterior, glúteos e quadríceps", "inferior", LEGS, 1))
    }

    private fun sessaoForca(p: Perfil, m: Modelo, dia: Int, fase: FaseSemana, minutos: Int = p.minutos, finalizar: Boolean = false, obj: Objetivo = p.objetivo): Sessao {
        val usados = mutableSetOf<String>()
        val aq = aquecimento(p, m.aq, usados)
        val fin = if (finalizar && minutos >= 40 && !fase.deload) 8 else 0
        val disponivel = max(10, minutos - 7 - 4 - fin)
        val slots = m.slots.map { s -> if (m.variante == 0) s else s.split(":").let { "${it[0]}:${(it.getOrNull(1)?.toIntOrNull() ?: 0) + m.variante}" } }
        val principal = blocoForca(p, slots, fase, disponivel, usados, obj = obj)
        val blocos = mutableListOf(aq, principal)
        if (fin > 0) finalizador(p, usados, if (p.nivel == Nivel.INICIANTE) 3 else 4)?.let { blocos += it }
        blocos += desaquecimento(m.aq)
        return Sessao(m.titulo, m.foco, "forca", minutos, blocos, dia)
    }

    private fun planoForca(p: Perfil): Plano {
        val n = p.dias.size
        // Quantos dias de força: iniciante até 4; saúde/emagrecimento/resistência deixam dias para cardio.
        val diasForca = when (p.objetivo) {
            Objetivo.SAUDE -> min(n, 3)
            Objetivo.EMAGRECER, Objetivo.RESISTENCIA -> min(n, if (n >= 5) 3 else max(2, n - 1))
            else -> if (p.nivel == Nivel.INICIANTE) min(n, 4) else n
        }.coerceAtLeast(min(n, 2))
        val (nomeDiv, modelos) = divisao(diasForca)
        val indicesForca = (0 until diasForca).map { k -> (k * n.toDouble() / diasForca).roundToInt().coerceAtMost(n - 1) }.toSet()
        val semanas = (1..8).map { w ->
            val fase = faseForca(w, p.nivel)
            var f = 0
            var c = 0
            val sessoes = p.dias.mapIndexed { i, dia ->
                // espalha os dias de força entre os dias escolhidos (começando pelo primeiro)
                val forca = i in indicesForca
                if (forca && f < diasForca) {
                    val m = modelos[f % modelos.size]; f++
                    sessaoForca(p, m, dia, fase, finalizar = p.objetivo == Objetivo.EMAGRECER)
                } else {
                    c++
                    val hiit = p.objetivo == Objetivo.EMAGRECER && c % 2 == 0 && p.nivel != Nivel.INICIANTE && "impacto" !in p.evitar
                    if (hiit) sessaoHiitCurta(p, dia, fase, w) else sessaoCardioLeve(p, dia, min(p.minutos, if (fase.deload) 30 else 45))
                }
            }
            Semana(w, fase.nome, fase.nota, sessoes)
        }
        val local = when (p.modalidade) { Modalidade.CASA_CORPO -> "em casa"; Modalidade.CASA_ELASTICO -> "com elásticos"; else -> "na academia" }
        return Plano(
            nome = "${p.objetivo.nome} $local",
            resumo = "$nomeDiv · ${diasForca}x força${if (n > diasForca) " + ${n - diasForca}x cardio" else ""} · 8 semanas com semana leve na 4 e na 8.",
            modalidade = p.modalidade, objetivo = p.objetivo, nivel = p.nivel, semanas = semanas,
            dicas = listOfNotNull(
                "RIR = repetições em reserva. RIR 2 significa terminar a série sentindo que faria mais 2.",
                "Progrida sempre que completar o topo da faixa de repetições em todas as séries.",
                if (p.modalidade != Modalidade.ACADEMIA) "Ficou fácil? Desça mais devagar (3–4 s), pause no fundo ou use a variação mais difícil." else null,
                if (p.objetivo == Objetivo.MASSA) "Para hipertrofia: proteína ~1,6 g/kg/dia e sono de 7–9 h fazem diferença." else null,
                if (p.objetivo == Objetivo.EMAGRECER) "O treino de força preserva a massa magra no déficit calórico; some passos no dia a dia (7–10 mil)." else null,
                if (p.objetivo == Objetivo.SAUDE) "Meta da OMS: 150–300 min de atividade moderada por semana + força 2x." else null,
            ),
            alertas = emptyList(), metaSemanal = "",
        )
    }

    private fun sessaoHiitCurta(p: Perfil, dia: Int, fase: FaseSemana, w: Int): Sessao {
        val usados = mutableSetOf<String>()
        val sel = Seletor(p)
        val ids = listOfNotNull(sel.escolher("condicionamento", w, usados), sel.escolher("agachar", w, usados), sel.escolher("condicionamento", w + 1, usados), sel.escolher("core", w, usados))
        val voltas = if (fase.deload) 3 else 4 + (if (p.nivel == Nivel.AVANCADO) 1 else 0)
        return Sessao("HIIT curto", "Condicionamento", "hiit", 0, listOf(
            aquecimento(p, "total", usados),
            Bloco("Circuito 40/20", TipoBloco.CIRCUITO, ids.map { Item(it.id, 1, trabalhoSeg = 40, descansoSeg = 20, intensidade = "Forte · 8/10") }, voltas = voltas, nota = "40 s de esforço, 20 s de pausa. 1 min entre voltas se precisar."),
            desaquecimento("total"),
        ), dia)
    }

    // ------------------------------------------------------------------ corrida

    private fun pace(seg: Int): String = "%d:%02d".format(seg / 60, seg % 60)
    private fun faixaPace(p: Perfil, de: Int, ate: Int): String? {
        val t = p.tempo5kMin ?: return null
        val base = t * 60 / 5
        return "${pace(base + de)}–${pace(base + ate)} /km"
    }

    private fun intensidade(zona: String, pace: String?) = if (pace != null) "$zona · $pace" else zona

    private fun semanasCorrida(meta: String) = when (meta) { "10k" -> 10; "21k" -> 12; "42k" -> 16; else -> 8 }

    private fun longaoMin(meta: String, n: Nivel): Pair<Int, Int> = when (meta) {
        "5k" -> when (n) { Nivel.INICIANTE -> 30 to 45; Nivel.INTERMEDIARIO -> 40 to 55; Nivel.AVANCADO -> 45 to 65 }
        "10k" -> when (n) { Nivel.INICIANTE -> 40 to 70; Nivel.INTERMEDIARIO -> 50 to 80; Nivel.AVANCADO -> 60 to 90 }
        "21k" -> when (n) { Nivel.INICIANTE -> 60 to 120; Nivel.INTERMEDIARIO -> 70 to 130; Nivel.AVANCADO -> 80 to 140 }
        "42k" -> when (n) { Nivel.INICIANTE -> 75 to 190; Nivel.INTERMEDIARIO -> 90 to 200; Nivel.AVANCADO -> 100 to 210 }
        else -> when (n) { Nivel.INICIANTE -> 30 to 50; Nivel.INTERMEDIARIO -> 40 to 65; Nivel.AVANCADO -> 50 to 80 }
    }

    private fun taper(meta: String) = when (meta) { "42k" -> 3; "21k" -> 2; else -> 1 }

    /** Fator de volume da semana: progressão até o pico, semana de recuperação a cada 4 e polimento no fim. */
    private fun fatorCorrida(w: Int, total: Int, meta: String): Pair<Double, String> {
        val tp = taper(meta)
        val pico = total - tp
        return when {
            w > pico -> {
                val k = w - pico
                val f = when (tp) { 3 -> listOf(0.75, 0.6, 0.4); 2 -> listOf(0.7, 0.45); else -> listOf(0.55) }[k - 1]
                f to (if (w == total) "Semana de prova" else "Polimento")
            }
            w % 4 == 0 -> -1.0 to "Recuperação"
            else -> (w - 1).toDouble() / max(1, pico - 1) to (if (w <= pico / 2) "Base" else "Construção")
        }
    }

    private data class Tiro(val reps: Int, val trabalho: Int, val pausa: Int, val nome: String)

    private fun tiros(n: Nivel, w: Int): Tiro {
        val l = when (n) {
            Nivel.INICIANTE -> listOf(Tiro(6, 60, 120, "6 × 1 min"), Tiro(8, 60, 90, "8 × 1 min"), Tiro(6, 120, 120, "6 × 2 min"), Tiro(5, 180, 120, "5 × 3 min"))
            Nivel.INTERMEDIARIO -> listOf(Tiro(8, 90, 90, "8 × 400 m (~90 s)"), Tiro(6, 180, 120, "6 × 800 m (~3 min)"), Tiro(5, 240, 120, "5 × 1 km (~4 min)"), Tiro(10, 60, 60, "10 × 1 min"))
            Nivel.AVANCADO -> listOf(Tiro(10, 90, 60, "10 × 400 m"), Tiro(6, 240, 90, "6 × 1 km"), Tiro(5, 300, 120, "5 × 1200 m (~5 min)"), Tiro(12, 60, 60, "12 × 1 min"), Tiro(4, 480, 120, "4 × 2 km (~8 min)"))
        }
        return l[(w - 1).mod(l.size)]
    }

    private fun sessaoCorrida(
        p: Perfil, dia: Int, tipo: String, w: Int, total: Int, meta: String, forcaExtra: Boolean = false,
    ): Sessao {
        val (lo, hi) = longaoMin(meta, p.nivel)
        val (fator, _) = fatorCorrida(w, total, meta)
        val longao = when {
            fator < 0 -> ((lo + (hi - lo) * (w - 2).toDouble() / max(1, total - taper(meta) - 1)) * 0.75).roundToInt()
            w > total - taper(meta) -> (hi * fator).roundToInt()
            else -> (lo + (hi - lo) * fator).roundToInt()
        }.coerceAtLeast(20)
        val leve = (longao * 0.6).roundToInt().coerceIn(20, max(20, p.minutos - 10))
        val recup = fator < 0 || w > total - taper(meta)
        val aqCorrida = Bloco("Aquecimento", TipoBloco.AQUECIMENTO, listOf(
            Item("corrida-leve", 1, trabalhoSeg = 600, descansoSeg = 0, intensidade = "Bem leve · 2–3/10", nota = "Comece caminhando se precisar"),
            Item("educativos-corrida", 1, trabalhoSeg = 180, descansoSeg = 0, nota = "Skipping, anfersen e dribling"),
        ))
        val ultima = w == total && tipo == "L" && meta in setOf("5k", "10k", "21k", "42k")
        val blocos = mutableListOf<Bloco>()
        val titulo: String
        val foco: String
        when {
            ultima -> {
                val km = meta.removeSuffix("k")
                titulo = "Dia da prova · $km km"; foco = "Prova"
                blocos += Bloco("Aquecimento", TipoBloco.AQUECIMENTO, listOf(Item("corrida-leve", 1, trabalhoSeg = 600, descansoSeg = 0, intensidade = "Leve")))
                blocos += Bloco("Prova", TipoBloco.PRINCIPAL, listOf(Item("prova", 1, trabalhoSeg = longaoMin(meta, p.nivel).second * 60, descansoSeg = 0, intensidade = "Ritmo de prova", nota = "Largue controlado; acelere na segunda metade.")))
            }
            tipo == "L" -> {
                titulo = "Longão"; foco = "Resistência aeróbica"
                blocos += Bloco("Corrida longa", TipoBloco.PRINCIPAL, listOf(Item("longao", 1, trabalhoSeg = longao * 60, descansoSeg = 0, intensidade = intensidade("Zona 2 · conversa", faixaPace(p, 70, 105)),
                    nota = if (longao >= 75) "Leve água e carboidrato a partir de 60 min." else null)))
            }
            tipo == "Q" && !recup -> {
                val corridaLonga = meta == "21k" || meta == "42k"
                if (corridaLonga && w % 2 == 0) {
                    val blocosMin = min(20, 8 + w)
                    val reps = if (meta == "42k") 3 else 2
                    titulo = "Ritmo de prova"; foco = "Ritmo específico"
                    blocos += aqCorrida
                    blocos += Bloco("Blocos no ritmo de prova", TipoBloco.INTERVALADO, listOf(Item("tempo-run", reps, trabalhoSeg = blocosMin * 60, descansoSeg = 120,
                        intensidade = intensidade("Ritmo de prova · 6–7/10", faixaPace(p, if (meta == "42k") 40 else 25, if (meta == "42k") 55 else 40)), nota = "Recupere trotando 2 min")))
                } else {
                    val t = tiros(p.nivel, (w + 1) / 2)
                    titulo = "Intervalado · ${t.nome}"; foco = "Velocidade e VO2"
                    blocos += aqCorrida
                    blocos += Bloco("Tiros", TipoBloco.INTERVALADO, listOf(Item("tiros", t.reps, trabalhoSeg = t.trabalho, descansoSeg = t.pausa,
                        intensidade = intensidade("Forte · 8/10", faixaPace(p, -10, 0)), nota = "Recuperação trotando ou caminhando")))
                }
            }
            tipo == "T" && !recup -> {
                val dur = when (p.nivel) { Nivel.INICIANTE -> 10 + w; Nivel.INTERMEDIARIO -> 15 + w * 2; Nivel.AVANCADO -> 20 + w * 2 }.coerceAtMost(40)
                titulo = "Corrida de limiar"; foco = "Limiar"
                blocos += aqCorrida
                blocos += Bloco("Limiar contínuo", TipoBloco.PRINCIPAL, listOf(Item("tempo-run", 1, trabalhoSeg = dur * 60, descansoSeg = 0, intensidade = intensidade("Confortavelmente difícil · 7/10", faixaPace(p, 15, 25)))))
            }
            tipo == "R" -> {
                titulo = "Regenerativo"; foco = "Recuperação"
                blocos += Bloco("Corrida leve", TipoBloco.PRINCIPAL, listOf(Item("corrida-leve", 1, trabalhoSeg = min(30, leve) * 60, descansoSeg = 0, intensidade = intensidade("Muito leve · 2/10", faixaPace(p, 90, 120)))))
            }
            else -> {
                titulo = if (forcaExtra) "Leve + força" else "Corrida leve"; foco = "Base aeróbica"
                val strides = if (p.nivel != Nivel.INICIANTE && !recup) listOf(Item("tiros", 4, trabalhoSeg = 20, descansoSeg = 60, intensidade = "Acelerações · 85%", nota = "Strides: soltas, sem forçar")) else emptyList()
                blocos += Bloco("Corrida leve", TipoBloco.PRINCIPAL, listOf(Item("corrida-leve", 1, trabalhoSeg = leve * 60, descansoSeg = 0, intensidade = intensidade("Zona 2 · conversa", faixaPace(p, 60, 90)))) + strides)
            }
        }
        if (forcaExtra) blocos += forcaCorredor(p, w)
        blocos += desaquecimento("corrida")
        return Sessao(titulo, foco, "corrida", 0, blocos, dia)
    }

    private fun forcaCorredor(p: Perfil, w: Int, nome: String = "Força para corredores"): Bloco {
        val pesos = if (p.modalidade == Modalidade.CORRIDA || p.modalidade == Modalidade.BIKE) emptySet() else p.equip.intersect(setOf("elastico", "halter", "kettlebell"))
        val sel = Seletor(p, equip = setOf("corpo") + pesos)
        val usados = mutableSetOf<String>()
        val ids = listOfNotNull(sel.escolher("unilateral", w, usados), sel.escolher("gluteo", w, usados), sel.escolher("panturrilha", 0, usados), sel.escolher("core", w, usados))
        return Bloco(nome, TipoBloco.CIRCUITO, ids.map { e ->
            if (e.porTempo) Item(e.id, 1, trabalhoSeg = 40, descansoSeg = 20) else Item(e.id, 1, reps = "10–12", descansoSeg = 20, intensidade = "RIR 2")
        }, voltas = if (p.nivel == Nivel.INICIANTE) 2 else 3, nota = "Previne lesões e melhora a economia de corrida.")
    }

    private fun sessaoCaminhaCorre(p: Perfil, dia: Int, w: Int, k: Int): Sessao {
        // Progressão no estilo "do sofá aos 5 km": corrida/caminhada em segundos e repetições.
        val tabela = listOf(Triple(60, 90, 8), Triple(90, 90, 7), Triple(120, 90, 6), Triple(180, 90, 5), Triple(300, 120, 4), Triple(480, 120, 3), Triple(720, 120, 2))
        val principal = if (w >= 8) {
            val min = listOf(25, 28, 30)[k.coerceIn(0, 2)]
            Item("corrida-leve", 1, trabalhoSeg = min * 60, descansoSeg = 0, intensidade = "Zona 2 · conversa", nota = "Corrida contínua! Devagar está ótimo.")
        } else {
            val (corre, caminha, reps) = tabela[w - 1]
            Item("caminhada-corrida", reps, trabalhoSeg = corre, descansoSeg = caminha, intensidade = "Trote leve · 4–5/10", nota = "No descanso, caminhe rápido")
        }
        return Sessao(if (w >= 8) "Corrida contínua" else "Caminhada + corrida", "Construção de base", "corrida", 0, listOf(
            Bloco("Aquecimento", TipoBloco.AQUECIMENTO, listOf(Item("caminhada", 1, trabalhoSeg = 300, descansoSeg = 0, intensidade = "Caminhada rápida"))),
            Bloco("Corre & caminha", TipoBloco.INTERVALADO, listOf(principal)),
            Bloco("Volta à calma", TipoBloco.DESAQUECIMENTO, listOf(Item("caminhada", 1, trabalhoSeg = 300, descansoSeg = 0)) + desaquecimento("corrida").itens),
        ), dia)
    }

    private fun planoCorrida(p: Perfil): Plano {
        var meta = p.corridaMeta
        val alertas = mutableListOf<String>()
        if (!p.correContinuo) {
            if (meta in setOf("10k", "21k", "42k")) alertas += "Antes de buscar os ${meta.removeSuffix("k")} km, este plano constrói sua base até 30 minutos contínuos. Depois, refaça o questionário."
            meta = "comecar"
        }
        val n = p.dias.size
        if (meta == "comecar") {
            val semanas = (1..8).map { w ->
                var k = 0
                val sessoes = p.dias.mapIndexed { i, dia ->
                    val corrida = n <= 3 || i % 2 == 0 || k < 3 && n - i <= 3 - k
                    if (corrida && k < 3) sessaoCaminhaCorre(p, dia, w, k++)
                    else if (i % 2 == 1 && n >= 4) Sessao("Força para corredores", "Prevenção", "forca", 0, listOf(aquecimento(p, "inferior", mutableSetOf()), forcaCorredor(p, w, "Circuito de força"), desaquecimento("inferior")), dia)
                    else sessaoCardioLeve(p.copy(emCasa = true), dia, 30, "Caminhada rápida", "Passo firme: respiração acelerada, mas dá para conversar.")
                }
                Semana(w, if (w < 4) "Base" else if (w < 8) "Construção" else "30 minutos!", "Corrida e caminhada intercaladas. Repita a semana se sentir que precisa — tudo bem.", sessoes)
            }
            return Plano("Do zero aos 30 minutos", "8 semanas de corrida e caminhada intercaladas até 30 min contínuos (≈ 5 km).", p.modalidade, p.objetivo, p.nivel, semanas,
                listOf("Ritmo certo é o que deixa você conversar. Correr devagar é correr certo.", "Tênis confortável e superfície regular nas primeiras semanas.", "Dor articular que piora ao correr = pare e descanse; dor muscular leve no dia seguinte é normal."),
                alertas, "")
        }
        val total = semanasCorrida(meta)
        val modelo = when (n) {
            2 -> listOf("Q", "L")
            3 -> listOf("Q", "E", "L")
            4 -> listOf("Q", "E", if (p.nivel == Nivel.INICIANTE) "E" else "T", "L")
            5 -> listOf("Q", "E", "T", "E", "L")
            else -> listOf("Q", "E", "T", "E", "R", "L")
        }.map { if (meta == "saude" && p.nivel == Nivel.INICIANTE && it == "Q") "E" else it }
        val semanas = (1..total).map { w ->
            val (_, fase) = fatorCorrida(w, total, meta)
            var forcas = 0
            val sessoes = p.dias.mapIndexed { i, dia ->
                val t = modelo[i.coerceAtMost(modelo.size - 1)]
                val forca = t == "E" && forcas < (if (n >= 5) 2 else 1) && n >= 3
                if (forca) forcas++
                sessaoCorrida(p, dia, t, w, total, meta, forca)
            }
            val nota = when (fase) {
                "Recuperação" -> "Semana mais leve para absorver o treino. Volume ~25% menor."
                "Polimento" -> "Menos volume, mantendo um pouco de intensidade: chegue descansado."
                "Semana de prova" -> "Durma bem, nada de novidade em tênis ou comida. Confie no treino!"
                "Base" -> "80% dos treinos em ritmo leve (Seiler). A intensidade fica nos dias de qualidade."
                else -> "Volume subindo aos poucos. Respeite os ritmos — leve é leve."
            }
            Semana(w, fase, nota, sessoes)
        }
        val nome = when (meta) { "5k" -> "5 km"; "10k" -> "10 km"; "21k" -> "Meia maratona"; "42k" -> "Maratona"; "ritmo" -> "Mais velocidade"; else -> "Correr por saúde" }
        return Plano("$nome em $total semanas", "${n}x por semana · distribuição 80/20 · longão progressivo com semanas de recuperação.", p.modalidade, p.objetivo, p.nivel, semanas,
            listOfNotNull(
                if (p.tempo5kMin == null) "Sem tempo de 5 km informado, os ritmos estão por percepção de esforço (escala 0–10)." else "Ritmos calculados a partir dos seus ${p.tempo5kMin} min nos 5 km. Refaça um teste a cada 6–8 semanas.",
                "Cadência alta (passos curtos) reduz o impacto. Mire em ~170–180 passos por minuto.",
                if (meta == "21k" || meta == "42k") "Treine a hidratação e os géis nos longões, nunca teste novidade no dia da prova." else null,
            ), alertas, "")
    }

    // ------------------------------------------------------------------ bike

    private data class ZonaBike(val nome: String, val de: Int, val ate: Int, val rpe: String)

    private val Z1 = ZonaBike("Z1 Recuperação", 0, 55, "2/10")
    private val Z2 = ZonaBike("Z2 Endurance", 56, 75, "3–4/10")
    private val Z3 = ZonaBike("Z3 Tempo", 76, 90, "5–6/10")
    private val SS = ZonaBike("Sweet spot", 88, 94, "6–7/10")
    private val Z4 = ZonaBike("Z4 Limiar", 91, 105, "7–8/10")
    private val Z5 = ZonaBike("Z5 VO2máx", 106, 120, "9/10")

    private fun zona(p: Perfil, z: ZonaBike): String {
        val ftp = p.ftp
        return if (ftp != null) "${z.nome} · ${(ftp * z.de / 100.0).roundToInt()}–${(ftp * z.ate / 100.0).roundToInt()} W" else "${z.nome} · ${z.rpe}"
    }

    private fun sessaoBike(p: Perfil, dia: Int, tipo: String, w: Int, fase: FaseSemana): Sessao {
        val leve = fase.deload
        val ini = p.nivel == Nivel.INICIANTE
        val aq = Bloco("Aquecimento", TipoBloco.AQUECIMENTO, listOf(Item("bike-leve", 1, trabalhoSeg = 600, descansoSeg = 0, intensidade = zona(p, Z2), nota = "Suba a intensidade aos poucos")))
        val volta = Bloco("Volta à calma", TipoBloco.DESAQUECIMENTO, listOf(Item("bike-leve", 1, trabalhoSeg = 300, descansoSeg = 0, intensidade = zona(p, Z1))) + desaquecimento("bike").itens)
        val k = if (w <= 4) w else w - 4
        fun intervalo(titulo: String, foco: String, ex: String, reps: Int, trab: Int, pausa: Int, z: ZonaBike, nota: String? = null) =
            Sessao(titulo, foco, "bike", 0, listOf(aq, Bloco("Série principal", TipoBloco.INTERVALADO, listOf(Item(ex, reps, trabalhoSeg = trab, descansoSeg = pausa, intensidade = zona(p, z), nota = nota ?: "Pausa pedalando leve"))), volta), dia)
        return when (tipo) {
            "SS" -> if (leve) intervalo("Sweet spot leve", "Limiar", "bike-intervalado", 2, 480, 240, if (ini) Z3 else SS)
            else if (ini) intervalo("Tempo", "Resistência", "bike-intervalado", 3, (5 + k) * 60, 240, Z3)
            else intervalo("Sweet spot", "Limiar", "bike-intervalado", if (k >= 3) 2 else 3, listOf(8, 10, 15, 20)[min(k, 3)] * 60, 300, SS)
            "LIM" -> if (leve || ini) sessaoBike(p, dia, "SS", w, fase)
            else intervalo("Limiar", "FTP", "bike-intervalado", if (k >= 3) 3 else 4, listOf(6, 8, 10, 12)[min(k, 3)] * 60, 240, Z4)
            "VO2" -> if (leve) intervalo("Ativação curta", "Manutenção", "bike-intervalado", 4, 60, 120, Z4)
            else if (ini) intervalo("Intervalado curto", "Potência aeróbica", "bike-intervalado", 6 + k, 60, 120, Z4)
            else intervalo("VO2máx", "Potência aeróbica", "bike-intervalado", listOf(5, 6, 5, 4)[min(k, 3)], listOf(180, 180, 240, 300)[min(k, 3)], 180, Z5, "Recupere o mesmo tempo pedalando leve")
            "CAD" -> Sessao("Endurance + cadência", "Técnica", "bike", 0, listOf(aq,
                Bloco("Drills de cadência", TipoBloco.INTERVALADO, listOf(Item("bike-cadencia", 6, trabalhoSeg = 30, descansoSeg = 90, intensidade = "Leve · 110+ rpm", nota = "Quadril parado no selim"))),
                Bloco("Endurance", TipoBloco.PRINCIPAL, listOf(Item("bike-leve", 1, trabalhoSeg = max(15, p.minutos - 30) * 60, descansoSeg = 0, intensidade = zona(p, Z2)))), volta), dia)
            "SUB" -> intervalo("Subida · força no pedal", "Força específica", "bike-subida", if (leve) 3 else 4 + k / 2, 360, 180, Z3, "60–70 rpm, marcha pesada")
            "REC" -> Sessao("Recuperação ativa", "Recuperação", "bike", 0, listOf(Bloco("Giro leve", TipoBloco.PRINCIPAL, listOf(Item("bike-leve", 1, trabalhoSeg = 35 * 60, descansoSeg = 0, intensidade = zona(p, Z1)))), desaquecimento("bike")), dia)
            "Z2" -> Sessao("Endurance", "Base aeróbica", "bike", 0, listOf(Bloco("Endurance", TipoBloco.PRINCIPAL, listOf(Item("bike-leve", 1, trabalhoSeg = max(30, p.minutos - 5) * 60, descansoSeg = 0, intensidade = zona(p, Z2)))), desaquecimento("bike")), dia)
            "F" -> Sessao("Força para ciclistas", "Prevenção e potência", "forca", 0, listOf(aquecimento(p, "inferior", mutableSetOf()), forcaCorredor(p, w, "Circuito de força"), desaquecimento("inferior")), dia)
            else -> { // longo
                val (lo, hi) = when (p.nivel) { Nivel.INICIANTE -> 60 to 105; Nivel.INTERMEDIARIO -> 90 to 150; Nivel.AVANCADO -> 120 to 210 }
                val prog = if (w <= 3) w - 1 else if (w in 5..7) w - 2 else 0
                val min = if (leve) lo else (lo + (hi - lo) * prog / 5.0).roundToInt()
                Sessao("Longo de fim de semana", "Resistência", "bike", 0, listOf(Bloco("Pedal longo", TipoBloco.PRINCIPAL, listOf(Item("bike-leve", 1, trabalhoSeg = min * 60, descansoSeg = 0, intensidade = zona(p, Z2), nota = "Coma e beba a cada 20–30 min acima de 90 min"))), desaquecimento("bike")), dia)
            }
        }
    }

    private fun planoBike(p: Perfil): Plano {
        val n = p.dias.size
        val modelo = when (n) {
            2 -> listOf("SS", "LONGO")
            3 -> listOf("SS", "CAD", "LONGO")
            4 -> listOf("VO2", "CAD", "SS", "LONGO")
            5 -> listOf("VO2", "F", "LIM", "REC", "LONGO")
            else -> listOf("VO2", "F", "SS", if (p.bikeTipo == "mtb" || p.bikeTipo == "estrada") "SUB" else "CAD", "REC", "LONGO")
        }
        val semanas = (1..8).map { w ->
            val fase = faseForca(w, p.nivel).let { if (it.deload) it.copy(nome = "Recuperação", nota = "Semana leve: volume menor e só uma sessão intensa curta.") else it.copy(nota = "Progressão de tempo em zona. ${if (p.ftp == null) "Sem FTP: guie-se pela percepção de esforço." else "Zonas calculadas a partir do FTP de ${p.ftp} W."}") }
            Semana(w, if (fase.deload) fase.nome else if (w < 4) "Base" else "Construção", fase.nota, p.dias.mapIndexed { i, dia -> sessaoBike(p, dia, modelo[i.coerceAtMost(modelo.size - 1)], w, fase) })
        }
        return Plano("Ciclismo · ${p.objetivo.nome.lowercase()}", "${n}x por semana · zonas de Coggan · sweet spot, VO2 e longo progressivo.", p.modalidade, p.objetivo, p.nivel, semanas,
            listOfNotNull(
                if (p.ftp == null) "Para descobrir o FTP: após aquecer, pedale 20 min no máximo sustentável; FTP ≈ 95% da potência média." else null,
                "Ajuste da bike: joelho levemente flexionado no ponto mais baixo do pedal.",
                "Acima de 90 min, consuma 30–60 g de carboidrato por hora.",
            ), emptyList(), "")
    }

    // ------------------------------------------------------------------ lutas

    private data class Round(val trabalho: Int, val pausa: Int, val rounds: Int, val grappling: Boolean)

    private fun round(arte: String) = when (arte) {
        "boxe" -> Round(180, 60, 3, false)
        "muay" -> Round(180, 120, 5, false)
        "mma" -> Round(300, 60, 3, false)
        "bjj" -> Round(360, 60, 4, true)
        "judo" -> Round(240, 60, 4, true)
        "wrestling" -> Round(180, 30, 2, true)
        else -> Round(120, 60, 3, false)
    }

    private fun faseLuta(w: Int, total: Int, marcada: Boolean): FaseSemana {
        if (!marcada) return faseForca(w, Nivel.INTERMEDIARIO).let { it.copy(nome = if (it.deload) "Semana leve" else if (w <= 4) "Preparação geral" else "Preparação específica") }
        val polimento = if (total >= 6) 2 else 1
        return when {
            w == total -> FaseSemana("Semana da luta", "Volume mínimo, só manter a velocidade. Durma e se hidrate bem.", false, true, 1, 0.4)
            w > total - polimento -> FaseSemana("Polimento", "Volume cai, intensidade fica: chegue rápido e descansado.", false, true, 1, 0.6)
            w <= (total - polimento) / 2 -> FaseSemana("Preparação geral", "Base de força e condicionamento.", false, false, 0, 1.0)
            else -> FaseSemana("Preparação específica", "Força vira potência; rounds no ritmo da luta.", true, false, 1, 1.0)
        }
    }

    private fun sessaoRounds(p: Perfil, dia: Int, fase: FaseSemana, w: Int, variante: Int): Sessao {
        val r = round(p.lutaArte)
        val sel = Seletor(p, nivelMax = 3)
        val drills = if (r.grappling) listOf("sprawl", "fuga-quadril", "ponte-pescoco", "bear-crawl", "burpee", "farmer-walk")
        else listOf("sombra", "saco-combinacoes", "sprawl", "burpee", "battle-rope", "corda")
        val disponiveis = drills.mapNotNull { id -> sel.primeiro(id) }.ifEmpty { listOfNotNull(cat["sombra"]) }
        val rounds = when {
            fase.deload -> max(2, (r.rounds * fase.volume).roundToInt())
            fase.extraSerie -> r.rounds + 1
            else -> r.rounds
        } + if (p.nivel == Nivel.AVANCADO && !fase.deload) 1 else 0
        val itens = (0 until rounds).map { i ->
            val e = disponiveis[(i + variante + w).mod(disponiveis.size)]
            Item(e.id, 1, trabalhoSeg = r.trabalho, descansoSeg = r.pausa, intensidade = "Ritmo de luta · 8/10",
                nota = if (r.grappling) "Alterne 30 s explosivos e 30 s de controle" else "Picos de 10 s em máxima velocidade a cada 30 s")
        }
        val pausaMin = r.pausa / 60.0
        val usados = disponiveis.map { it.id }.toMutableSet()
        val core = if (p.minutos >= 45 && !fase.deload) listOfNotNull(sel.escolher("core", w, usados), sel.escolher("core", w + 1, usados),
            sel.primeiro("isometria-pescoco", usados = usados).takeIf { p.lutaArte != "karate" }) else emptyList()
        return Sessao("Condicionamento em rounds", "Específico de luta", "luta", 0, listOfNotNull(
            aquecimento(p, "total", mutableSetOf()),
            Bloco("Rounds", TipoBloco.INTERVALADO, itens, nota = "$rounds rounds de ${r.trabalho / 60} min com ${if (pausaMin < 1) "${r.pausa} s" else "${pausaMin.roundToInt()} min"} de pausa — o formato da sua luta."),
            if (core.isNotEmpty()) Bloco("Core & pescoço", TipoBloco.CIRCUITO, core.map { if (it.porTempo) Item(it.id, 1, trabalhoSeg = 30, descansoSeg = 15) else Item(it.id, 1, reps = "12", descansoSeg = 15) }, voltas = 3) else null,
            desaquecimento("total"),
        ), dia)
    }

    private fun sessaoPotencia(p: Perfil, dia: Int, fase: FaseSemana, titulo: String = "Potência & velocidade", comPrevencao: Boolean = false): Sessao {
        val sel = Seletor(p, nivelMax = 3)
        val usados = mutableSetOf<String>()
        val aq = aquecimento(p, "total", usados)
        val ex = listOfNotNull(sel.escolher("pliometria", fase.variante, usados), sel.escolher("potencia", fase.variante, usados),
            sel.escolher("potencia_sup", 0, usados), sel.escolher("potencia_rot", 0, usados))
        val series = if (fase.deload) 2 else if (p.nivel == Nivel.INICIANTE) 3 else 4
        val itens = ex.map { Item(it.id, series, reps = if ("pliometria" in it.padroes) "4–6" else "3–5", descansoSeg = 90, intensidade = "Máxima velocidade", nota = "Pare antes de perder qualidade") }
        val blocos = mutableListOf(aq, Bloco("Potência", TipoBloco.PRINCIPAL, itens, nota = "Cada repetição o mais rápida possível. Qualidade > cansaço."))
        if (comPrevencao) blocos += blocoPrevencao(p, fase)
        else {
            val core = listOfNotNull(sel.escolher("core", 0, usados), sel.escolher("core", 2, usados), sel.primeiro("isometria-pescoco", usados = usados).takeIf { p.modalidade == Modalidade.LUTA })
            blocos += Bloco("Core", TipoBloco.PRINCIPAL, core.map { if (it.porTempo) Item(it.id, 3, trabalhoSeg = 30, descansoSeg = 30) else Item(it.id, 3, reps = "10–12", descansoSeg = 45) })
        }
        blocos += desaquecimento("total")
        return Sessao(titulo, "Explosão", "forca", 0, blocos, dia)
    }

    private fun blocoPrevencao(p: Perfil, fase: FaseSemana): Bloco {
        val sel = Seletor(p, nivelMax = 3)
        val usados = mutableSetOf<String>()
        val ex = listOfNotNull(sel.primeiro("nordico", "mesa-flexora", "stiff-halteres", usados = usados), sel.primeiro("monster-walk", "ponte-unilateral", usados = usados),
            sel.primeiro("rotacao-externa", "face-pull", "band-pull-apart", usados = usados), sel.primeiro("panturrilha-pe", "panturrilha-elastico", usados = usados),
            sel.primeiro("prancha-lateral", usados = usados), sel.primeiro("equilibrio-unipodal", usados = usados))
        val s = if (fase.deload) 1 else 2
        return Bloco("Prevenção de lesões", TipoBloco.PRINCIPAL, ex.map { if (it.porTempo) Item(it.id, s, trabalhoSeg = 30, descansoSeg = 20) else Item(it.id, s, reps = if (it.id == "nordico") "4–6" else "10–12", descansoSeg = 45, intensidade = "Controle") },
            nota = "Posterior, quadril, ombro e tornozelo: onde mais acontecem lesões no esporte.")
    }

    private fun planoLuta(p: Perfil): Plano {
        val marcada = p.lutaSemanas != null
        val total = p.lutaSemanas ?: 8
        val n = p.dias.size
        val muitosTecnicos = p.lutaTecnicos >= 5
        val modelo = when (n) {
            2 -> listOf("FP", "R")
            3 -> listOf("F", "R", "P")
            4 -> listOf("F", "R", "P", "A")
            5 -> listOf("F", "R", "P", "A", "M")
            else -> listOf("F", "R", "P", "A", "R2", "M")
        }.map { if (muitosTecnicos && it == "R2") "M" else it }
        val forcaSlots = listOf("agachar", "dobradica", "empurrar_h", "puxar_v", "puxar_h", "carregar", "core")
        val semanas = (1..total).map { w ->
            val fase = faseLuta(w, total, marcada)
            val sessoes = p.dias.mapIndexed { i, dia ->
                when (modelo[i.coerceAtMost(modelo.size - 1)]) {
                    "F", "FP" -> {
                        val usados = mutableSetOf<String>()
                        val aq = aquecimento(p, "total", usados)
                        val pre = if (modelo[i] == "FP") listOfNotNull(Seletor(p).escolher("pliometria", 0, usados)).map { Item(it.id, 3, reps = "4–5", descansoSeg = 90, intensidade = "Máxima velocidade") } else emptyList()
                        val principal = blocoForca(p, forcaSlots, fase, max(15, p.minutos - 15), usados, obj = Objetivo.FORCA)
                        val pescoco = cat["isometria-pescoco"]!!.takeIf { p.lutaArte != "karate" && "impacto" !in p.evitar }
                        Sessao(if (modelo[i] == "FP") "Força & potência" else "Força máxima", "Força", "forca", 0, listOfNotNull(aq,
                            if (pre.isNotEmpty()) Bloco("Potência", TipoBloco.PRINCIPAL, pre) else null,
                            principal,
                            pescoco?.let { Bloco("Pescoço", TipoBloco.PRINCIPAL, listOf(Item(it.id, 2, trabalhoSeg = 60, descansoSeg = 30, intensidade = "Progressivo, sem dor", nota = "15 s em cada direção"))) },
                            desaquecimento("total")), dia)
                    }
                    "R" -> sessaoRounds(p, dia, fase, w, 0)
                    "R2" -> sessaoRounds(p, dia, fase, w, 2)
                    "P" -> sessaoPotencia(p, dia, fase)
                    "A" -> sessaoCardioLeve(p.copy(emCasa = p.emCasa), dia, min(45, p.minutos), "Base aeróbica", "Melhora a recuperação entre os rounds. Ritmo de conversa.")
                    else -> sessaoMobilidade(p, dia, w, 40, "Mobilidade & recuperação")
                }
            }
            Semana(w, fase.nome, fase.nota, sessoes)
        }
        val arte = Questionario.perguntas.first { it.id == "luta_arte" }.opcoes.first { it.valor == p.lutaArte }.titulo
        return Plano("Preparação física · $arte", (if (marcada) "Camp de $total semanas até a luta" else "Bloco de 8 semanas") + " · força, potência e rounds no formato da sua luta.",
            p.modalidade, p.objetivo, p.nivel, semanas,
            listOfNotNull(
                "Os treinos técnicos de luta continuam sendo a prioridade: encaixe a força longe dos sparrings mais duros.",
                if (muitosTecnicos) "Com ${p.lutaTecnicos} treinos técnicos por semana, reduzimos o condicionamento extra para não acumular fadiga." else null,
                "Corte de peso agressivo prejudica o desempenho: planeje com nutricionista.",
            ), emptyList(), "")
    }

    // ------------------------------------------------------------------ atletas

    private fun planoAtleta(p: Perfil): Plano {
        val n = p.dias.size
        val emTemporada = p.atletaFase == "em"
        val objF = when (p.atletaFase) { "fora" -> Objetivo.MASSA; else -> Objetivo.FORCA }
        val forcaA = listOf("agachar", "dobradica", "empurrar_h", "puxar_h", "unilateral", "core")
        val forcaB = listOf("dobradica:1", "unilateral:1", "empurrar_v", "puxar_v", "posterior", "core:1")
        val modelo = when (n) {
            2 -> listOf("A+P", "B+PREV")
            3 -> listOf("A", "V+P", "B+PREV")
            4 -> listOf("A", "V", "B", "P+PREV")
            5 -> listOf("A", "V", "B", "P+PREV", "C")
            else -> listOf("A", "V", "B", "P+PREV", "C", "M")
        }.map { if (emTemporada && it in setOf("C", "V") && n >= 4) "M" else it }
        val semanas = (1..8).map { w ->
            val base = faseForca(w, p.nivel)
            val fase = base.copy(nome = when {
                base.deload -> "Semana leve"
                p.atletaFase == "em" -> "Manutenção"
                w <= 3 -> if (p.atletaFase == "fora") "Hipertrofia funcional" else "Força"
                else -> if (p.atletaFase == "fora") "Força" else "Potência"
            }, nota = if (emTemporada) "Em temporada: pouco volume, alta qualidade. Nunca treine pesado na véspera de jogo." else base.nota)
            val obj = if (w > 4 && p.atletaFase == "fora") Objetivo.FORCA else objF
            val sessoes = p.dias.mapIndexed { i, dia ->
                when (modelo[i.coerceAtMost(modelo.size - 1)]) {
                    "A", "A+P", "B", "B+PREV" -> {
                        val m = modelo[i]
                        val usados = mutableSetOf<String>()
                        val aq = aquecimento(p, "total", usados)
                        val pot = if (m == "A+P") listOfNotNull(Seletor(p).escolher("pliometria", 0, usados)).map { Item(it.id, 3, reps = "4–5", descansoSeg = 90, intensidade = "Máxima velocidade") } else emptyList()
                        val minutos = if (emTemporada) min(p.minutos, 45) else p.minutos
                        val principal = blocoForca(p, if (m.startsWith("A")) forcaA else forcaB, if (emTemporada) fase.copy(deload = true, volume = 0.6) else fase, max(15, minutos - 15 - if (m == "B+PREV") 8 else 0), usados, obj = obj, nome = "Força")
                        Sessao(if (m.startsWith("A")) "Força A" else "Força B", "Força", "forca", 0, listOfNotNull(aq,
                            if (pot.isNotEmpty()) Bloco("Potência", TipoBloco.PRINCIPAL, pot) else null,
                            principal, if (m == "B+PREV") blocoPrevencao(p, fase) else null, desaquecimento("total")), dia)
                    }
                    "V", "V+P" -> sessaoVelocidade(p, dia, fase, modelo[i] == "V+P")
                    "P+PREV" -> sessaoPotencia(p, dia, fase, "Potência & prevenção", comPrevencao = true)
                    "C" -> sessaoCondicionamentoEsporte(p, dia, fase)
                    else -> sessaoMobilidade(p, dia, w, 40, "Mobilidade & recuperação")
                }
            }
            Semana(w, fase.nome, fase.nota, sessoes)
        }
        val esporte = Questionario.perguntas.first { it.id == "atleta_esporte" }.opcoes.first { it.valor == p.atletaEsporte }.titulo
        val faseNome = Questionario.perguntas.first { it.id == "atleta_fase" }.opcoes.first { it.valor == p.atletaFase }.titulo
        return Plano("Performance · $esporte", "$faseNome · força, potência, velocidade e prevenção em 8 semanas.", p.modalidade, p.objetivo, p.nivel, semanas,
            listOf("Treine força/potência longe (24–48 h) dos jogos e treinos táticos mais intensos.", "Pliometria: qualidade de aterrissagem antes de altura ou volume.", "Durma 8–10 h: é quando a adaptação acontece."),
            emptyList(), "")
    }

    private fun sessaoVelocidade(p: Perfil, dia: Int, fase: FaseSemana, comPotencia: Boolean): Sessao {
        val sel = Seletor(p, nivelMax = 3)
        val usados = mutableSetOf<String>()
        val itens = mutableListOf(
            Item("educativos-corrida", 1, trabalhoSeg = 240, descansoSeg = 30, nota = "Skipping, anfersen, dribling"),
            Item("tiros", if (fase.deload) 4 else 6 + fase.variante * 2, trabalhoSeg = 6, descansoSeg = 90, intensidade = "Máxima velocidade", nota = "Sprints de 20–30 m. Recuperação completa"),
        )
        listOfNotNull(sel.primeiro("bound-lateral", usados = usados), sel.primeiro("salto-distancia", usados = usados)).forEach { itens += Item(it.id, 3, reps = "4–6", descansoSeg = 75, intensidade = "Explosivo") }
        val blocos = mutableListOf(aquecimento(p, "corrida", usados), Bloco("Velocidade & agilidade", TipoBloco.PRINCIPAL, itens, nota = "Velocidade se treina descansado: pausa longa é parte do treino."))
        if (comPotencia) sel.escolher("potencia_sup", 0, usados)?.let { blocos += Bloco("Potência de tronco", TipoBloco.PRINCIPAL, listOf(Item(it.id, 3, reps = "5", descansoSeg = 75))) }
        blocos += desaquecimento("corrida")
        return Sessao("Velocidade & agilidade", "Velocidade", "atleta", 0, blocos, dia)
    }

    private fun sessaoCondicionamentoEsporte(p: Perfil, dia: Int, fase: FaseSemana): Sessao = when (p.atletaEsporte) {
        "resistencia" -> sessaoCardioLeve(p, dia, p.minutos, "Endurance Z2", "Volume aeróbico de base.")
        "forca" -> sessaoHiitCurta(p, dia, fase, 1).copy(titulo = "Condicionamento metabólico")
        else -> Sessao("Condicionamento intermitente", "Repetição de sprints", "atleta", 0, listOf(
            aquecimento(p, "corrida", mutableSetOf()),
            Bloco("Intermitente 15/15", TipoBloco.INTERVALADO, listOf(Item("tiros", if (fase.deload) 8 else 12, trabalhoSeg = 15, descansoSeg = 15, intensidade = "Forte · 85–90%", nota = "Simula as ações repetidas do jogo")),
                nota = "Faça 2 séries com 3 min de pausa se estiver em boa forma."),
            desaquecimento("corrida"),
        ), dia)
    }

    // ------------------------------------------------------------------ HIIT

    private fun planoHiit(p: Perfil): Plano {
        val (trab, pausa, voltasBase) = when (p.nivel) { Nivel.INICIANTE -> Triple(30, 30, 3); Nivel.INTERMEDIARIO -> Triple(40, 20, 4); Nivel.AVANCADO -> Triple(45, 15, 5) }
        val semanas = (1..8).map { w ->
            val fase = faseForca(w, p.nivel)
            val voltas = when { fase.deload -> max(2, voltasBase - 1); w in setOf(3, 7) -> voltasBase + 1; else -> voltasBase }
            val sessoes = p.dias.mapIndexed { i, dia ->
                val tipo = if (p.dias.size >= 5 && i == p.dias.size - 1) 3 else i % 3
                val usados = mutableSetOf<String>()
                val sel = Seletor(p)
                when (tipo) {
                    0 -> {
                        val ex = listOfNotNull(sel.escolher("agachar", w, usados), sel.escolher("empurrar_h", w, usados), sel.escolher("dobradica", w, usados),
                            sel.escolher("puxar_h", w, usados), sel.escolher("core", w, usados), sel.escolher("condicionamento", w, usados))
                        Sessao("Circuito de força", "Força + fôlego", "hiit", 0, listOf(aquecimento(p, "total", usados),
                            Bloco("Circuito $trab/$pausa", TipoBloco.CIRCUITO, ex.map { Item(it.id, 1, trabalhoSeg = trab, descansoSeg = pausa, intensidade = "Forte · 7–8/10") }, voltas = voltas, nota = "Descanse 1 min entre as voltas."),
                            desaquecimento("total")), dia)
                    }
                    1 -> {
                        val pares = listOfNotNull(sel.escolher("condicionamento", w, usados), sel.escolher("agachar", w + 1, usados), sel.escolher("condicionamento", w + 1, usados), sel.escolher("core", w + 1, usados))
                        val tabatas = if (fase.deload) 2 else if (p.nivel == Nivel.INICIANTE) 2 else min(4, pares.size)
                        Sessao("Tabata", "Intervalado máximo", "hiit", 0, listOf(aquecimento(p, "total", usados)) +
                            pares.take(tabatas).mapIndexed { k, e -> Bloco("Tabata ${k + 1}", TipoBloco.INTERVALADO, listOf(Item(e.id, 8, trabalhoSeg = 20, descansoSeg = 10, intensidade = "Máximo · 9/10")), nota = "8 × 20 s / 10 s. 1 min de pausa entre os tabatas.") } +
                            desaquecimento("total"), dia)
                    }
                    2 -> {
                        val ex = listOfNotNull(sel.escolher("potencia", w, usados), sel.escolher("unilateral", w, usados), sel.escolher("empurrar_v", w, usados),
                            sel.escolher("condicionamento", w + 2, usados), sel.escolher("core", w + 2, usados))
                        Sessao("EMOM funcional", "Potência e ritmo", "hiit", 0, listOf(aquecimento(p, "total", usados),
                            Bloco("A cada minuto", TipoBloco.CIRCUITO, ex.map { Item(it.id, 1, trabalhoSeg = 40, descansoSeg = 20, intensidade = "Ritmo constante") }, voltas = voltas, nota = "Um exercício por minuto: trabalhe 40 s e use o resto do minuto para respirar."),
                            desaquecimento("total")), dia)
                    }
                    else -> sessaoMobilidade(p, dia, w, 40, "Mobilidade ativa")
                }
            }
            Semana(w, fase.nome, if (fase.deload) "Semana leve: menos voltas, mesma qualidade." else "Mais voltas nas semanas 3 e 7. Respeite as pausas.", sessoes)
        }
        return Plano("HIIT & funcional", "Circuitos $trab/$pausa, Tabata e EMOM · ${p.dias.size}x por semana.", p.modalidade, p.objetivo, p.nivel, semanas,
            listOf("HIIT é intenso: 2–4 sessões por semana costumam bastar; nos outros dias, prefira atividades leves.", "Técnica primeiro. Se perder a forma, reduza o ritmo, não a amplitude."),
            emptyList(), "")
    }

    // ------------------------------------------------------------------ híbrido

    private fun planoHibrido(p: Perfil): Plano {
        val n = p.dias.size
        val bike = p.cardioHibrido == "bike"
        val modelo = when (n) {
            2 -> listOf("FA", "CL")
            3 -> listOf("FA", "CQ", "FB")
            4 -> listOf("U", "CQ", "L", "CL")
            5 -> listOf("U", "CQ", "L", "CE", "FC")
            else -> listOf("U", "CQ", "L", "CE", "FC", "CL")
        }
        val meta = if (p.corridaMeta in setOf("5k", "10k")) p.corridaMeta else "ritmo"
        val semanas = (1..8).map { w ->
            val fase = faseForca(w, p.nivel)
            val sessoes = p.dias.mapIndexed { i, dia ->
                when (modelo[i.coerceAtMost(modelo.size - 1)]) {
                    "FA" -> sessaoForca(p, Modelo("Força · corpo inteiro A", "Corpo inteiro", "total", FULL_A), dia, fase)
                    "FB" -> sessaoForca(p, Modelo("Força · corpo inteiro B", "Corpo inteiro", "total", FULL_B), dia, fase)
                    "FC" -> sessaoForca(p, Modelo("Força · corpo inteiro C", "Corpo inteiro", "total", FULL_C), dia, fase)
                    "U" -> sessaoForca(p, Modelo("Força · superiores", "Peito, costas e ombros", "superior", UPPER_A), dia, fase)
                    "L" -> sessaoForca(p, Modelo("Força · inferiores", "Pernas e glúteos", "inferior", LOWER_A), dia, fase)
                    "CQ" -> if (bike) sessaoBike(p, dia, if (w % 2 == 0) "VO2" else "SS", w, fase) else if (p.correContinuo) sessaoCorrida(p, dia, if (w % 2 == 0) "T" else "Q", w, 8, meta) else sessaoCaminhaCorre(p, dia, w, 0)
                    "CE" -> if (bike) sessaoBike(p, dia, "Z2", w, fase) else if (p.correContinuo) sessaoCorrida(p, dia, "E", w, 8, meta) else sessaoCaminhaCorre(p, dia, w, 1)
                    else -> if (bike) sessaoBike(p, dia, "LONGO", w, fase) else if (p.correContinuo) sessaoCorrida(p, dia, "L", w, 8, meta) else sessaoCaminhaCorre(p, dia, w, 2)
                }
            }
            Semana(w, fase.nome, "Separe força de pernas e treinos intensos de ${if (bike) "bike" else "corrida"} por pelo menos 24 h quando possível.", sessoes)
        }
        return Plano("Híbrido · força + ${if (bike) "bike" else "corrida"}", "${n}x por semana · força 2–3x e cardio estruturado · 8 semanas.", p.modalidade, p.objetivo, p.nivel, semanas,
            listOf("Treino concorrente funciona: só evite colocar o cardio intenso logo antes do treino de pernas.", "Mantenha a maior parte do cardio em intensidade leve (zona 2)."),
            emptyList(), "")
    }

    // ------------------------------------------------------------------ mobilidade e 50+

    private fun planoMobilidade(p: Perfil): Plano {
        val inicial = when (p.nivel) { Nivel.INICIANTE -> 30; Nivel.INTERMEDIARIO -> 40; Nivel.AVANCADO -> 50 }
        val semanas = (1..8).map { w ->
            val hold = (inicial + (if (w >= 3) 10 else 0) + (if (w >= 6) 10 else 0)).coerceAtMost(75)
            Semana(w, if (w <= 2) "Consciência" else if (w <= 5) "Amplitude" else "Controle", "Segure cada posição por ~$hold s, respirando devagar. Nunca force até doer.",
                p.dias.mapIndexed { i, dia -> sessaoMobilidade(p, dia, i + w, hold) })
        }
        return Plano("Mobilidade & alongamento", "${p.dias.size} sessões por semana de coluna, quadril, ombros e pernas · 8 semanas.", p.modalidade, p.objetivo, p.nivel, semanas,
            listOf("Alongamento estático rende mais depois do treino ou em sessão separada (ACSM: 10–30 s, 2–4 repetições).", "Antes de treinar, prefira mobilidade dinâmica."),
            emptyList(), "")
    }

    private fun planoLongevidade(p: Perfil): Plano {
        val n = p.dias.size
        val a = listOf("agachar", "empurrar_h", "puxar_h", "gluteo", "panturrilha", "carregar")
        val b = listOf("unilateral", "empurrar_v", "puxar_v", "dobradica", "core", "ombro_post")
        val modelo = when (n) {
            2 -> listOf("A", "B")
            3 -> listOf("A", "CAM", "B")
            4 -> listOf("A", "CAM", "B", "MOB")
            5 -> listOf("A", "CAM", "B", "CAM", "MOB")
            else -> listOf("A", "CAM", "B", "CAM", "A2", "MOB")
        }
        val semanas = (1..8).map { w ->
            val fase = faseForca(w, Nivel.INICIANTE)
            val sessoes = p.dias.mapIndexed { i, dia ->
                when (val t = modelo[i.coerceAtMost(modelo.size - 1)]) {
                    "A", "A2", "B" -> {
                        val usados = mutableSetOf<String>()
                        val aq = aquecimento(p, "total", usados)
                        val principal = blocoForca(p, if (t == "B") b else a, fase.copy(variante = fase.variante + if (t == "A2") 1 else 0), max(15, p.minutos - 15), usados, obj = Objetivo.SAUDE, principais = 3)
                        val eq = cat["equilibrio-unipodal"]!!
                        Sessao(if (t == "B") "Força funcional B" else "Força funcional A", "Força e equilíbrio", "forca", 0, listOf(aq, principal,
                            Bloco("Equilíbrio", TipoBloco.PRINCIPAL, listOf(Item(eq.id, 2, trabalhoSeg = 60, descansoSeg = 20, nota = "30 s cada perna, perto de um apoio"))),
                            desaquecimento("total")), dia)
                    }
                    "CAM" -> sessaoCardioLeve(p.copy(emCasa = true, equip = p.equip - "esteira"), dia, min(p.minutos, 20 + w * 3), "Caminhada", "Passo firme: dá para conversar, mas não para cantar.")
                    else -> sessaoMobilidade(p, dia, w, 30, "Mobilidade & equilíbrio")
                }
            }
            Semana(w, fase.nome, "Força 2x por semana preserva músculos, ossos e autonomia (OMS 2020).", sessoes)
        }
        return Plano("Força, equilíbrio e longevidade", "${n}x por semana · força funcional, equilíbrio e caminhada.", p.modalidade, p.objetivo, p.nivel, semanas,
            listOf("Levante-se devagar após exercícios no chão para evitar tontura.", "Prefira calçado firme e um apoio por perto nos exercícios de equilíbrio."),
            emptyList(), "")
    }

    // ------------------------------------------------------------------ alertas

    private fun alertas(p: Perfil): List<String> = buildList {
        if (p.parq.isNotEmpty()) add("Você marcou itens da triagem PAR-Q+. Procure liberação médica antes de começar e comece com intensidade leve.")
        if (p.gestante) add("Gestação ou pós-parto: treine somente com liberação médica. Evite impacto, esforço máximo e longos períodos deitada de barriga para cima após o 1º trimestre. Removemos exercícios de impacto.")
        val lim = p.evitar - "impacto"
        if (lim.isNotEmpty()) add("Adaptamos os exercícios para: ${lim.joinToString(", ")}. Se a dor aumentar durante ou após o treino, pare e procure um fisioterapeuta.")
        if (p.idade < 18) add("Menor de 18 anos: treine com supervisão de um profissional, priorizando técnica antes da carga.")
        if (p.nivel == Nivel.INICIANTE && p.imc >= 32 && p.modalidade !in setOf(Modalidade.MOBILIDADE, Modalidade.BIKE)) add("Priorizamos exercícios de baixo impacto para proteger as articulações no começo.")
    }

    companion object {
        private val BILATERAL = setOf("flexor-quadril", "alongamento-quadriceps", "alongamento-panturrilha", "alongamento-posterior", "maior-alongamento", "alongamento-peito", "rotacao-toracica", "rolo-it", "rolo-panturrilha")

        /** Exercícios básicos preferidos como primeira opção do padrão. */
        private val CLASSICOS = setOf(
            "supino-reto", "supino-halteres", "agachamento-barra", "leg-press", "stiff", "remada-curvada", "remada-baixa", "remada-unilateral",
            "puxada-frente", "barra-fixa", "desenvolvimento-halteres", "elevacao-lateral", "rosca-direta", "triceps-polia", "flexao",
            "agachamento-livre", "agachamento-goblet", "ponte-gluteo", "elevacao-quadril", "afundo", "prancha", "crucifixo", "mesa-flexora",
            "panturrilha-pe", "face-pull", "remada-elastico", "supino-elastico", "agachamento-elastico", "desenvolvimento-elastico",
        )

        private val FALLBACK = mapOf(
            "puxar_v" to listOf("puxar_h", "ombro_post"), "puxar_h" to listOf("puxar_v", "ombro_post"),
            "empurrar_v" to listOf("empurrar_h", "ombro_lat"), "empurrar_h" to listOf("empurrar_v"),
            "dobradica" to listOf("gluteo", "posterior"), "posterior" to listOf("dobradica", "gluteo"),
            "quadriceps" to listOf("agachar", "unilateral"), "unilateral" to listOf("agachar", "gluteo"), "agachar" to listOf("unilateral", "gluteo"),
            "peito_iso" to listOf("empurrar_h"), "ombro_lat" to listOf("ombro_post", "empurrar_v"), "ombro_post" to listOf("puxar_h"),
            "trapezio" to listOf("ombro_post"), "biceps" to listOf("puxar_h"), "triceps" to listOf("empurrar_h"), "gluteo" to listOf("dobradica", "unilateral"),
            "pliometria" to listOf("condicionamento"), "potencia" to listOf("pliometria", "condicionamento"), "potencia_sup" to listOf("empurrar_h"),
            "potencia_rot" to listOf("core"), "carregar" to listOf("core"), "condicionamento" to listOf("core"),
        )

        val DICAS_GERAIS = listOf(
            "Pare imediatamente se sentir dor no peito, falta de ar desproporcional, tontura ou palpitações.",
            "Durma bem e beba água: recuperação é parte do treino.",
        )
    }
}
