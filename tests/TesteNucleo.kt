import com.forja.app.core.*
import java.io.File

var ok = 0
val falhas = mutableListOf<String>()

fun check(cond: Boolean, msg: () -> String) {
    if (cond) ok++ else falhas += msg()
}

class Memoria : Armazenamento {
    val m = mutableMapOf<String, String>()
    override fun ler(chave: String) = m[chave]
    override fun gravar(chave: String, valor: String?) { if (valor == null) m.remove(chave) else m[chave] = valor }
}

fun respostas(
    mod: String, obj: String = "massa", exp: String = "intermediario", dias: Int = 3, min: Int = 60,
    extra: Map<String, List<String>> = emptyMap(),
): Respostas {
    val r = mutableMapOf(
        "modalidade" to listOf(mod), "objetivo" to listOf(obj), "experiencia" to listOf(exp),
        "dias" to listOf("$dias"), "dias_semana" to Questionario.diasSugeridos(dias).map { "$it" },
        "minutos" to listOf("$min"), "idade" to listOf("32"), "sexo" to listOf("m"), "altura" to listOf("175"), "peso" to listOf("78"),
        "limitacoes" to listOf("nenhuma"), "parq" to listOf("nenhuma"),
        "local" to listOf("academia"), "equipamentos" to listOf(), "hibrido_cardio" to listOf("corrida"),
        "corrida_meta" to listOf("10k"), "corrida_continuo" to listOf("sim"), "corrida_5k" to listOf(),
        "bike_tipo" to listOf("estrada"), "bike_ftp" to listOf(), "luta_arte" to listOf("mma"), "luta_tecnicos" to listOf("3"),
        "luta_marcada" to listOf("nao"), "atleta_esporte" to listOf("coletivo"), "atleta_fase" to listOf("pre"),
    )
    r.putAll(extra)
    return Questionario.limpar(r)
}

fun validarPlano(nome: String, p: Perfil, plano: Plano, cat: Catalogo) {
    check(plano.semanas.isNotEmpty()) { "$nome: sem semanas" }
    for (s in plano.semanas) {
        check(s.sessoes.size == p.dias.size) { "$nome S${s.numero}: ${s.sessoes.size} sessões, esperado ${p.dias.size}" }
        check(s.sessoes.map { it.diaSemana } == p.dias) { "$nome S${s.numero}: dias ${s.sessoes.map { it.diaSemana }} != ${p.dias}" }
        for (ses in s.sessoes) {
            val itens = ses.blocos.flatMap { it.itens }
            check(itens.isNotEmpty()) { "$nome S${s.numero} ${ses.titulo}: sessão vazia" }
            check(ses.blocos.none { it.itens.isEmpty() }) { "$nome S${s.numero} ${ses.titulo}: bloco vazio ${ses.blocos.filter { it.itens.isEmpty() }.map { it.nome }}" }
            check(ses.minutos in 5..260) { "$nome ${ses.titulo}: ${ses.minutos} min" }
            for (it in itens) {
                val e = cat[it.exId]
                check(e != null) { "$nome: exercício inexistente ${it.exId}" }
                if (e == null) continue
                check(it.series >= 1) { "$nome ${e.id}: séries ${it.series}" }
                check((it.reps != null) != (it.trabalhoSeg != null)) { "$nome ${e.id}: reps=${it.reps} tempo=${it.trabalhoSeg}" }
                val conflito = e.evitar.filter { x -> x in p.evitar }
                check(conflito.isEmpty()) { "$nome ${ses.titulo}: ${e.id} conflita com $conflito" }
            }
            if (p.modalidade == Modalidade.CASA_CORPO && p.equip == setOf("corpo", "rua")) {
                val proibidos = itens.mapNotNull { cat[it.exId] }.filter { it.equip.none { q -> q in p.equip } }
                check(proibidos.isEmpty()) { "$nome: equipamento indisponível ${proibidos.map { it.id }}" }
            }
            val ids = ses.blocos.filter { it.tipo == TipoBloco.PRINCIPAL }.flatMap { b -> b.itens.map { it.exId } }
            check(ids.size == ids.distinct().size || ses.tipo == "luta") { "$nome ${ses.titulo}: exercício repetido $ids" }
        }
    }
}

fun main(args: Array<String>) {
    val cat = Catalogo.deJson(File(args[0]).readText())
    val ger = Gerador(cat)
    check(cat.exercicios.size >= 150) { "catálogo pequeno: ${cat.exercicios.size}" }
    check(cat.exercicios.all { it.dicas.size >= 3 }) { "exercício sem dicas" }

    // ---- matriz de perfis
    var planos = 0
    val minutosForca = mutableListOf<Pair<Int, Int>>()
    for (mod in Modalidade.entries) for (exp in Nivel.entries) for (dias in 2..6) for (obj in Objetivo.entries) {
        if (mod in setOf(Modalidade.MOBILIDADE, Modalidade.LONGEVIDADE, Modalidade.CORRIDA, Modalidade.BIKE, Modalidade.LUTA, Modalidade.ATLETA) && obj != Objetivo.SAUDE && obj != Objetivo.MASSA) continue
        val r = respostas(mod.id, obj.id, exp.id, dias)
        check(Questionario.completo(r)) { "questionário incompleto: $mod ${Questionario.visiveis(r).filter { !it.respondida(r) }.map { it.id }}" }
        val p = Perfil.de(r)
        val plano = ger.gerar(p)
        planos++
        validarPlano("$mod/$exp/${dias}d/$obj", p, plano, cat)
        if (mod == Modalidade.ACADEMIA) plano.semanas[1].sessoes.filter { it.tipo == "forca" }.forEach { minutosForca += p.minutos to it.minutos }
        check(ger.gerar(p) == plano) { "não determinístico: $mod" }
    }
    // variações específicas
    val especiais = listOf(
        "casa sem nada + joelho" to respostas("casa_corpo", "emagrecer", "iniciante", 4, 30, mapOf("limitacoes" to listOf("joelho"))),
        "casa elástico + ombro" to respostas("casa_elastico", "massa", "intermediario", 4, 45, mapOf("limitacoes" to listOf("ombro", "punho"))),
        "academia lombar" to respostas("academia", "forca", "avancado", 5, 75, mapOf("limitacoes" to listOf("lombar"))),
        "corrida do zero" to respostas("corrida", "saude", "iniciante", 3, 30, mapOf("corrida_meta" to listOf("comecar"))),
        "corrida 5 dias zero" to respostas("corrida", "saude", "iniciante", 5, 30, mapOf("corrida_meta" to listOf("comecar"))),
        "maratona sem base" to respostas("corrida", "performance", "iniciante", 4, 60, mapOf("corrida_meta" to listOf("42k"), "corrida_continuo" to listOf("nao"))),
        "maratona com 5k" to respostas("corrida", "performance", "avancado", 6, 90, mapOf("corrida_meta" to listOf("42k"), "corrida_5k" to listOf("20"))),
        "meia" to respostas("corrida", "performance", "intermediario", 4, 60, mapOf("corrida_meta" to listOf("21k"), "corrida_5k" to listOf("27"))),
        "bike ftp" to respostas("bike", "performance", "avancado", 6, 90, mapOf("bike_ftp" to listOf("260"), "bike_tipo" to listOf("mtb"))),
        "bike iniciante" to respostas("bike", "emagrecer", "iniciante", 3, 45),
        "luta marcada bjj" to respostas("luta", "performance", "avancado", 5, 60, mapOf("luta_arte" to listOf("bjj"), "luta_marcada" to listOf("6"), "luta_tecnicos" to listOf("5"))),
        "luta boxe casa" to respostas("luta", "performance", "intermediario", 4, 45, mapOf("luta_arte" to listOf("boxe"), "local" to listOf("casa"), "equipamentos" to listOf("saco", "corda"))),
        "atleta em temporada" to respostas("atleta", "performance", "avancado", 5, 60, mapOf("atleta_fase" to listOf("em"), "atleta_esporte" to listOf("raquete"))),
        "atleta resistência" to respostas("atleta", "performance", "intermediario", 6, 60, mapOf("atleta_fase" to listOf("fora"), "atleta_esporte" to listOf("resistencia"))),
        "hiit casa kettlebell" to respostas("hiit", "emagrecer", "avancado", 5, 30, mapOf("local" to listOf("casa"), "equipamentos" to listOf("kettlebell"))),
        "híbrido bike" to respostas("hibrido", "resistencia", "intermediario", 6, 60, mapOf("hibrido_cardio" to listOf("bike"))),
        "50+ casa" to respostas("longevidade", "saude", "iniciante", 3, 45, mapOf("idade" to listOf("68"), "local" to listOf("casa"), "equipamentos" to listOf("elastico", "banco"))),
        "gestante" to respostas("casa_corpo", "saude", "iniciante", 3, 30, mapOf("sexo" to listOf("f"), "gestante" to listOf("sim"))),
        "parq" to respostas("academia", "saude", "iniciante", 2, 45, mapOf("parq" to listOf("coracao", "remedio"))),
    )
    for ((nome, r) in especiais) {
        check(Questionario.completo(r)) { "$nome: incompleto ${Questionario.visiveis(r).filter { !it.respondida(r) }.map { it.id }}" }
        val p = Perfil.de(r)
        val plano = ger.gerar(p)
        planos++
        validarPlano(nome, p, plano, cat)
    }
    run {
        val p = Perfil.de(especiais.first { it.first == "maratona sem base" }.second)
        val pl = ger.gerar(p)
        check(pl.semanas.size == 8 && pl.alertas.any { "base" in it }) { "maratona sem base deveria virar plano de base com alerta" }
        val m = ger.gerar(Perfil.de(especiais.first { it.first == "maratona com 5k" }.second))
        check(m.semanas.size == 16) { "maratona deveria ter 16 semanas" }
        check(m.semanas.last().sessoes.last().titulo.contains("prova")) { "última sessão da maratona deveria ser a prova: ${m.semanas.last().sessoes.last().titulo}" }
        val intens = m.semanas[1].sessoes.flatMap { s -> s.blocos.flatMap { b -> b.itens.mapNotNull { it.intensidade } } }
        check(intens.any { "/km" in it }) { "ritmos por km esperados com tempo de 5 km: $intens" }
        val longoes = m.semanas.map { s -> s.sessoes.last().blocos.flatMap { it.itens }.maxOf { it.trabalhoSeg ?: 0 } / 60 }
        check(longoes[3] < longoes[2] && longoes.max() <= 215) { "longões da maratona: $longoes" }
        val b = ger.gerar(Perfil.de(especiais.first { it.first == "bike ftp" }.second))
        check(b.semanas[0].sessoes.flatMap { s -> s.blocos.flatMap { bl -> bl.itens.mapNotNull { it.intensidade } } }.any { " W" in it }) { "bike com FTP deveria ter watts" }
        val luta = ger.gerar(Perfil.de(especiais.first { it.first == "luta marcada bjj" }.second))
        check(luta.semanas.size == 6 && luta.semanas.last().fase == "Semana da luta") { "camp de luta: ${luta.semanas.map { it.fase }}" }
        val g = ger.gerar(Perfil.de(especiais.first { it.first == "gestante" }.second))
        check(g.alertas.any { "Gestação" in it }) { "alerta de gestação ausente" }
        val pq = ger.gerar(Perfil.de(especiais.first { it.first == "parq" }.second))
        check(pq.alertas.any { "PAR-Q" in it }) { "alerta PAR-Q ausente" }
        val zero = ger.gerar(Perfil.de(especiais.first { it.first == "corrida 5 dias zero" }.second))
        check(zero.semanas[0].sessoes.count { it.titulo.startsWith("Caminhada +") } == 3) { "do zero com 5 dias deveria ter 3 sessões de corre/caminha: ${zero.semanas[0].sessoes.map { it.titulo }}" }
    }
    // tempo das sessões de força próximo do pedido
    val fora = minutosForca.filter { (pedido, real) -> real < pedido * 0.55 || real > pedido * 1.35 }
    check(fora.size <= minutosForca.size / 10) { "sessões de força fora do tempo pedido: ${fora.take(10)} de ${minutosForca.size}" }

    // ---- rotinas avulsas de mobilidade
    run {
        check(Rotinas.todas.size >= 20) { "poucas rotinas: ${Rotinas.todas.size}" }
        check(Rotinas.todas.map { it.id }.distinct().size == Rotinas.todas.size) { "ids de rotina repetidos" }
        for (c in Rotinas.CATEGORIAS) check(Rotinas.todas.count { it.categoria == c } >= 5) { "categoria $c com poucas rotinas" }
        for (r in Rotinas.todas) {
            r.sessao.blocos.flatMap { it.itens }.forEach { check(cat[it.exId] != null) { "rotina ${r.id}: exercício ${it.exId} inexistente" } }
            val m = Roteiro.minutos(r.sessao, cat)
            check(m in 4..20) { "rotina ${r.id}: $m min" }
        }
        for (m in Modalidade.entries) check(Rotinas.recomendadas(m).size >= 3) { "recomendadas $m" }
    }

    // ---- questionário
    run {
        val r = respostas("corrida", "saude", "iniciante", 3, 30, mapOf("corrida_meta" to listOf("comecar")))
        check("corrida_continuo" !in r && "corrida_5k" !in r) { "perguntas de ritmo deveriam sumir para 'começar'" }
        check(Questionario.visiveis(respostas("academia")).none { it.id == "equipamentos" }) { "academia não pergunta equipamento" }
        check(Questionario.visiveis(respostas("casa_corpo")).any { it.id == "equipamentos" }) { "casa pergunta equipamento" }
        val semDias = respostas("academia").toMutableMap().apply { put("dias_semana", listOf("1", "3")) }
        check(!Questionario.completo(semDias)) { "dias da semana devem bater com a quantidade" }
        check(Questionario.visiveis(respostas("academia", extra = mapOf("sexo" to listOf("f")))).any { it.id == "gestante" }) { "pergunta de gestação para sexo feminino" }
    }

    // ---- roteiro
    run {
        val p = Perfil.de(respostas("hiit", "emagrecer", "intermediario", 3, 45))
        val s = ger.gerar(p).semanas[0].sessoes[0]
        val passos = Roteiro.passos(s, cat)
        val esperado = s.blocos.sumOf { b -> if (b.tipo == TipoBloco.CIRCUITO) b.voltas * b.itens.size else b.itens.sumOf { it.series } }
        check(passos.size == esperado) { "roteiro: ${passos.size} passos, esperado $esperado" }
        check(passos.last().descansoDepois == 0) { "último passo sem descanso" }
        check(Roteiro.prescricao(Item("x", 4, reps = "8–12")) == "4 × 8–12") { "prescrição reps" }
        check(Roteiro.prescricao(Item("x", 6, trabalhoSeg = 60, descansoSeg = 120)) == "6 × 1 min / 2 min") { "prescrição intervalo: ${Roteiro.prescricao(Item("x", 6, trabalhoSeg = 60, descansoSeg = 120))}" }
        check(Roteiro.formatarTempo(5400) == "1h30") { "formatar 1h30" }
    }

    // ---- loja / persistência
    run {
        var dia = 20_380L // uma segunda? calculado abaixo
        val mem = Memoria()
        val loja = Loja(cat, mem) { dia }
        check(!loja.estado.value.temPlano) { "loja vazia não tem plano" }
        loja.salvarRespostas(respostas("academia", "massa", "intermediario", 4))
        val e = loja.estado.value
        check(e.temPlano && e.plano!!.semanas.size == 8) { "plano após respostas" }
        check(Datas.diaSemana(e.inicio) == 1) { "início deve ser segunda" }
        check(Datas.diaSemana(0) == 4) { "1970-01-01 foi quinta" }
        val idx = 0
        val ses = e.plano!!.semanas[0].sessoes[idx]
        val ex = ses.blocos[1].itens[0].exId
        val alt = cat.alternativas(cat.exigir(ex), e.perfil!!.equip, e.perfil!!.evitar)
        check(alt.isNotEmpty()) { "sem alternativas para $ex" }
        val semanasCom = e.plano!!.semanas.filter { w -> w.sessoes[idx].blocos.any { b -> b.itens.any { it.exId == ex } } }.map { it.numero }
        loja.trocar(idx, ex, alt[0].id)
        val depois = loja.estado.value.plano!!.semanas
        check(semanasCom.isNotEmpty() && semanasCom.all { n -> depois[n - 1].sessoes[idx].blocos.none { b -> b.itens.any { it.exId == ex } } }) { "troca aplicada nas semanas $semanasCom" }
        loja.registrar(Registro(dia, 1, 0, "A", "forca", 3000, listOf(SerieFeita(alt[0].id, 12, 40.0), SerieFeita(alt[0].id, 12, 40.0)), 7, ""))
        val loja2 = Loja(cat, mem) { dia }
        check(loja2.estado.value.registros.size == 1 && loja2.estado.value.trocas.size == 1) { "persistência de registros e trocas" }
        check(loja2.estado.value.plano == loja.estado.value.plano) { "plano recarregado igual" }
        val sug = Progresso.sugestao(loja2.estado.value.registros, Item(alt[0].id, 3, reps = "8–12"))
        check(sug != null && "42" in sug) { "sugestão de carga: $sug" }
        check(Progresso.recordes(loja2.estado.value.registros).first().kg == 40.0) { "recorde" }
        dia += 7
        check(loja2.semanaAtual() == 2) { "semana 2 após 7 dias: ${loja2.semanaAtual()}" }
        dia += 365
        check(loja2.semanaAtual() == 8) { "semana limitada ao fim do plano" }
        loja2.registrarPeso(78.5); loja2.registrarPeso(78.0)
        check(loja2.estado.value.pesos.size == 1 && loja2.estado.value.pesos[0].second == 78.0) { "peso do dia substituído" }
        loja2.trocar(idx, ex, null)
        check(loja2.estado.value.trocas.isEmpty()) { "desfazer troca" }
        loja2.apagarTudo()
        check(!loja2.estado.value.temPlano && loja2.estado.value.registros.isEmpty()) { "apagar tudo" }
        // sequência
        val regs = listOf(100L, 101L, 102L).map { Registro(it, 1, 0, "", "", 60, emptyList(), 5, "") }
        check(Progresso.sequenciaDias(regs, 102) == 3 && Progresso.sequenciaDias(regs, 103) == 3 && Progresso.sequenciaDias(regs, 104) == 0) { "sequência de dias" }
        // JSON corrompido não derruba
        mem.m["registros"] = "{lixo"
        check(Loja(cat, mem) { dia }.estado.value.registros.isEmpty()) { "json corrompido" }
    }

    if (args.size > 1) {
        // imprime um plano para revisão manual: run.sh <assets> <modalidade> [obj] [exp] [dias] [min]
        val p = Perfil.de(respostas(args[1], args.getOrElse(2) { "massa" }, args.getOrElse(3) { "intermediario" }, args.getOrElse(4) { "4" }.toInt(), args.getOrElse(5) { "60" }.toInt()))
        val pl = ger.gerar(p)
        println("== ${pl.nome} — ${pl.resumo} | ${pl.metaSemanal}")
        pl.alertas.forEach { println("! $it") }
        for (s in pl.semanas.filter { it.numero in setOf(1, 4, pl.semanas.size) }) {
            println("-- Semana ${s.numero} · ${s.fase}: ${s.nota}")
            for (ses in s.sessoes) {
                println("  [${Questionario.DIAS_NOMES[ses.diaSemana - 1]}] ${ses.titulo} (${ses.minutos} min)")
                for (b in ses.blocos) {
                    println("     ${b.nome}${if (b.voltas > 1) " ×${b.voltas}" else ""}")
                    b.itens.forEach { println("       - ${cat.exigir(it.exId).nome}: ${Roteiro.prescricao(it, b.tipo == TipoBloco.CIRCUITO, b.voltas)}  ${it.intensidade ?: ""} ${it.nota ?: ""}") }
                }
            }
        }
    }

    println("Planos gerados: $planos · verificações: ${ok + falhas.size} · OK: $ok · falhas: ${falhas.size}")
    falhas.distinct().take(40).forEach { println("FALHA: $it") }
    if (falhas.isNotEmpty()) kotlin.system.exitProcess(1)
}
