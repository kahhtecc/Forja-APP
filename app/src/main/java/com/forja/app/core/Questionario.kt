package com.forja.app.core

typealias Respostas = Map<String, List<String>>

fun Respostas.um(id: String): String? = this[id]?.firstOrNull()
fun Respostas.num(id: String): Int? = um(id)?.toIntOrNull()

enum class TipoPergunta { UNICA, MULTIPLA, NUMERO, DIAS, TEXTO }

data class Opcao(val valor: String, val titulo: String, val descricao: String? = null)

data class Pergunta(
    val id: String,
    val secao: String,
    val titulo: String,
    val subtitulo: String? = null,
    val tipo: TipoPergunta,
    val opcoes: List<Opcao> = emptyList(),
    val min: Int = 0,
    val max: Int = 0,
    val passo: Int = 1,
    val padrao: Int? = null,
    val unidade: String = "",
    val opcional: Boolean = false,
    /** Valor exclusivo numa múltipla escolha (ex.: "nenhuma" desmarca o resto). */
    val exclusiva: String? = null,
    val visivel: (Respostas) -> Boolean = { true },
) {
    fun respondida(r: Respostas): Boolean {
        val v = r[id].orEmpty()
        return when (tipo) {
            TipoPergunta.DIAS -> v.size == (r.num("dias") ?: 0)
            TipoPergunta.MULTIPLA -> opcional || v.isNotEmpty()
            TipoPergunta.TEXTO -> opcional || v.firstOrNull().orEmpty().isNotBlank()
            else -> opcional || v.isNotEmpty()
        }
    }
}

object Questionario {
    private fun mod(r: Respostas) = Modalidade.de(r.um("modalidade"))
    private fun emCasa(r: Respostas) = when (mod(r)) {
        Modalidade.CASA_CORPO, Modalidade.CASA_ELASTICO -> true
        Modalidade.LUTA, Modalidade.ATLETA, Modalidade.HIBRIDO, Modalidade.HIIT, Modalidade.LONGEVIDADE -> r.um("local") == "casa"
        else -> false
    }
    private fun corre(r: Respostas) = mod(r) == Modalidade.CORRIDA || (mod(r) == Modalidade.HIBRIDO && r.um("hibrido_cardio") != "bike")

    val DIAS_NOMES = listOf("Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom")

    val perguntas: List<Pergunta> = listOf(
        Pergunta("nome", "Você", "Como podemos te chamar?", "Opcional — só para personalizar o app.", TipoPergunta.TEXTO, opcional = true),
        Pergunta(
            "modalidade", "Treino", "Que tipo de treino você quer fazer?", "Você pode trocar quando quiser refazendo o questionário.",
            TipoPergunta.UNICA,
            listOf(
                Opcao("academia", "Academia · musculação", "Máquinas, barras e halteres"),
                Opcao("casa_corpo", "Em casa · peso do corpo", "Sem equipamento ou com o que tiver"),
                Opcao("casa_elastico", "Em casa · elásticos", "Faixas e tubos elásticos"),
                Opcao("corrida", "Corrida", "Do primeiro trote à maratona"),
                Opcao("bike", "Bike · ciclismo", "Rolo, estrada, MTB ou ergométrica"),
                Opcao("luta", "Lutadores", "Boxe, muay thai, MMA, jiu-jitsu, judô…"),
                Opcao("atleta", "Atletas · performance", "Força, potência, velocidade e prevenção"),
                Opcao("hiit", "HIIT & funcional", "Circuitos intensos e curtos"),
                Opcao("hibrido", "Híbrido", "Força + corrida ou bike na mesma semana"),
                Opcao("mobilidade", "Mobilidade & alongamento", "Postura, flexibilidade e recuperação"),
                Opcao("longevidade", "50+ · força e equilíbrio", "Autonomia, ossos e equilíbrio"),
            ),
        ),
        Pergunta(
            "objetivo", "Treino", "Qual é o seu objetivo principal?", null, TipoPergunta.UNICA,
            listOf(
                Opcao("massa", "Ganhar massa muscular", "Hipertrofia e definição"),
                Opcao("emagrecer", "Perder gordura", "Gasto calórico e manutenção da massa magra"),
                Opcao("saude", "Saúde e vida ativa", "Disposição, coração e articulações"),
                Opcao("forca", "Ficar mais forte", "Mais carga nos movimentos básicos"),
                Opcao("resistencia", "Resistência e fôlego", "Aguentar mais tempo com menos cansaço"),
                Opcao("performance", "Performance", "Render mais no seu esporte ou prova"),
            ),
            visivel = { mod(it) != Modalidade.MOBILIDADE },
        ),
        Pergunta(
            "experiencia", "Treino", "Há quanto tempo você treina?", "Seja sincero: isso define volume e intensidade.", TipoPergunta.UNICA,
            listOf(
                Opcao("iniciante", "Estou começando", "Nunca treinei ou estou parado há mais de 6 meses"),
                Opcao("intermediario", "Já treino", "Com regularidade, de 6 meses a 2 anos"),
                Opcao("avancado", "Treino há bastante tempo", "Mais de 2 anos e domino a técnica"),
            ),
        ),
        Pergunta("dias", "Agenda", "Quantos dias por semana você vai treinar?", "Consistência vale mais que volume.", TipoPergunta.NUMERO, min = 2, max = 6, padrao = 3, unidade = "dias"),
        Pergunta("dias_semana", "Agenda", "Em quais dias?", "Escolha exatamente a quantidade de dias que você marcou.", TipoPergunta.DIAS),
        Pergunta(
            "minutos", "Agenda", "Quanto tempo por sessão?", "Incluindo aquecimento e alongamento.", TipoPergunta.UNICA,
            listOf("20", "30", "45", "60", "75", "90").map { Opcao(it, "$it min") },
        ),
        Pergunta(
            "local", "Equipamento", "Onde você vai fazer a parte de força?", null, TipoPergunta.UNICA,
            listOf(Opcao("academia", "Academia", "Acesso a máquinas, barras e halteres"), Opcao("casa", "Em casa", "Com o que eu tiver disponível")),
            visivel = { mod(it) in setOf(Modalidade.LUTA, Modalidade.ATLETA, Modalidade.HIBRIDO, Modalidade.HIIT, Modalidade.LONGEVIDADE) },
        ),
        Pergunta(
            "equipamentos", "Equipamento", "O que você tem em casa?", "Marque tudo o que tiver. Nada? Tudo bem, o peso do corpo resolve.", TipoPergunta.MULTIPLA,
            listOf(
                Opcao("halter", "Halteres"), Opcao("kettlebell", "Kettlebell"), Opcao("elastico", "Elásticos / mini-band"),
                Opcao("barra_fixa", "Barra fixa"), Opcao("banco", "Banco ou cadeira firme"), Opcao("corda", "Corda de pular"),
                Opcao("bola", "Medicine ball"), Opcao("rolo", "Rolo de liberação"), Opcao("saco", "Saco de pancada"),
                Opcao("bike", "Bike ergométrica / rolo"), Opcao("esteira", "Esteira"),
            ),
            opcional = true,
            visivel = { emCasa(it) },
        ),
        Pergunta(
            "hibrido_cardio", "Específico", "Qual cardio entra no seu híbrido?", null, TipoPergunta.UNICA,
            listOf(Opcao("corrida", "Corrida"), Opcao("bike", "Bike")),
            visivel = { mod(it) == Modalidade.HIBRIDO },
        ),
        Pergunta(
            "corrida_meta", "Corrida", "Qual é a sua meta na corrida?", null, TipoPergunta.UNICA,
            listOf(
                Opcao("comecar", "Começar a correr", "Sair do zero até 30 minutos contínuos"),
                Opcao("5k", "5 km"), Opcao("10k", "10 km"), Opcao("21k", "Meia maratona · 21 km"), Opcao("42k", "Maratona · 42 km"),
                Opcao("ritmo", "Ficar mais rápido", "Sem prova específica"),
                Opcao("saude", "Correr por saúde", "Constância e prazer"),
            ),
            visivel = { corre(it) },
        ),
        Pergunta(
            "corrida_continuo", "Corrida", "Hoje você consegue correr 20 minutos sem parar?", null, TipoPergunta.UNICA,
            listOf(Opcao("sim", "Sim"), Opcao("nao", "Ainda não")),
            visivel = { corre(it) && it.um("corrida_meta") != "comecar" },
        ),
        Pergunta(
            "corrida_5k", "Corrida", "Seu tempo atual nos 5 km", "Opcional. Usamos para calcular seus ritmos de treino.", TipoPergunta.NUMERO,
            min = 15, max = 60, padrao = 32, unidade = "min", opcional = true,
            visivel = { corre(it) && it.um("corrida_meta") != "comecar" && it.um("corrida_continuo") == "sim" },
        ),
        Pergunta(
            "bike_tipo", "Bike", "Onde você pedala?", null, TipoPergunta.UNICA,
            listOf(Opcao("indoor", "Rolo / indoor"), Opcao("estrada", "Estrada · speed"), Opcao("mtb", "Mountain bike"), Opcao("ergometrica", "Ergométrica / spinning")),
            visivel = { mod(it) == Modalidade.BIKE || (mod(it) == Modalidade.HIBRIDO && it.um("hibrido_cardio") == "bike") },
        ),
        Pergunta(
            "bike_ftp", "Bike", "Você sabe o seu FTP?", "Potência que você sustenta por ~1 hora, em watts. Não sabe? Pule — usamos a percepção de esforço.",
            TipoPergunta.NUMERO, min = 80, max = 450, passo = 5, padrao = 200, unidade = "W", opcional = true,
            visivel = { mod(it) == Modalidade.BIKE },
        ),
        Pergunta(
            "luta_arte", "Luta", "Qual é a sua luta?", null, TipoPergunta.UNICA,
            listOf(
                Opcao("boxe", "Boxe"), Opcao("muay", "Muay thai · kickboxing"), Opcao("mma", "MMA"), Opcao("bjj", "Jiu-jitsu"),
                Opcao("judo", "Judô"), Opcao("wrestling", "Wrestling · luta olímpica"), Opcao("karate", "Karatê · taekwondo"),
            ),
            visivel = { mod(it) == Modalidade.LUTA },
        ),
        Pergunta(
            "luta_tecnicos", "Luta", "Quantos treinos técnicos de luta você faz por semana?", "Treinos no tatame/ringue. A preparação física se ajusta a eles.",
            TipoPergunta.NUMERO, min = 0, max = 7, padrao = 3, unidade = "treinos",
            visivel = { mod(it) == Modalidade.LUTA },
        ),
        Pergunta(
            "luta_marcada", "Luta", "Tem luta ou campeonato marcado?", null, TipoPergunta.UNICA,
            listOf(Opcao("nao", "Não"), Opcao("4", "Em ~4 semanas"), Opcao("6", "Em ~6 semanas"), Opcao("8", "Em ~8 semanas"), Opcao("12", "Em ~12 semanas")),
            visivel = { mod(it) == Modalidade.LUTA },
        ),
        Pergunta(
            "atleta_esporte", "Esporte", "Qual é o perfil do seu esporte?", null, TipoPergunta.UNICA,
            listOf(
                Opcao("coletivo", "Coletivo", "Futebol, basquete, vôlei, handebol"),
                Opcao("raquete", "Raquete", "Tênis, padel, beach tennis"),
                Opcao("velocidade", "Velocidade e saltos", "Atletismo, sprint, saltos"),
                Opcao("resistencia", "Resistência", "Triathlon, corrida longa, remo, natação"),
                Opcao("forca", "Força", "Levantamentos, crossfit, arremessos"),
            ),
            visivel = { mod(it) == Modalidade.ATLETA },
        ),
        Pergunta(
            "atleta_fase", "Esporte", "Em que fase da temporada você está?", null, TipoPergunta.UNICA,
            listOf(
                Opcao("fora", "Fora de temporada", "Tempo para construir força e massa"),
                Opcao("pre", "Pré-temporada", "Converter força em potência e velocidade"),
                Opcao("em", "Em temporada", "Manter, sem atrapalhar jogos e provas"),
            ),
            visivel = { mod(it) == Modalidade.ATLETA },
        ),
        Pergunta("idade", "Você", "Qual a sua idade?", null, TipoPergunta.NUMERO, min = 14, max = 90, padrao = 30, unidade = "anos"),
        Pergunta(
            "sexo", "Você", "Sexo", "Usado só para estimativas (ex.: gasto calórico).", TipoPergunta.UNICA,
            listOf(Opcao("f", "Feminino"), Opcao("m", "Masculino"), Opcao("x", "Prefiro não dizer")),
        ),
        Pergunta("altura", "Você", "Sua altura", null, TipoPergunta.NUMERO, min = 120, max = 220, padrao = 170, unidade = "cm"),
        Pergunta("peso", "Você", "Seu peso", null, TipoPergunta.NUMERO, min = 35, max = 220, padrao = 70, unidade = "kg"),
        Pergunta(
            "gestante", "Saúde", "Você está grávida ou teve bebê há menos de 6 meses?", null, TipoPergunta.UNICA,
            listOf(Opcao("nao", "Não"), Opcao("sim", "Sim")),
            visivel = { it.um("sexo") == "f" },
        ),
        Pergunta(
            "limitacoes", "Saúde", "Alguma dor ou limitação?", "Adaptamos os exercícios. Dor forte ou persistente pede avaliação profissional.", TipoPergunta.MULTIPLA,
            listOf(Opcao("joelho", "Joelho"), Opcao("lombar", "Lombar / coluna"), Opcao("ombro", "Ombro"), Opcao("punho", "Punho"), Opcao("nenhuma", "Nenhuma")),
            exclusiva = "nenhuma",
        ),
        Pergunta(
            "parq", "Saúde", "Triagem de segurança (PAR-Q+)", "Marque o que for verdade para você.", TipoPergunta.MULTIPLA,
            listOf(
                Opcao("coracao", "Um médico já disse que tenho problema no coração ou pressão alta"),
                Opcao("dor_peito", "Sinto dor no peito em repouso, no dia a dia ou ao me exercitar"),
                Opcao("tontura", "Perdi o equilíbrio por tontura ou desmaiei nos últimos 12 meses"),
                Opcao("cronica", "Tenho outra doença crônica diagnosticada (além de coração/pressão)"),
                Opcao("remedio", "Tomo remédio prescrito para doença crônica"),
                Opcao("osso", "Tenho problema ósseo, articular ou de tecido mole que piora com exercício"),
                Opcao("supervisao", "Um médico disse que só devo me exercitar com supervisão"),
                Opcao("nenhuma", "Nenhuma das anteriores"),
            ),
            exclusiva = "nenhuma",
        ),
    )

    fun visiveis(r: Respostas) = perguntas.filter { it.visivel(r) }

    /** Remove respostas de perguntas que ficaram ocultas (ex.: trocou de modalidade). */
    fun limpar(r: Respostas): Respostas {
        val ids = visiveis(r).map { it.id }.toSet()
        return r.filterKeys { it in ids }
    }

    fun completo(r: Respostas) = visiveis(r).all { it.respondida(r) }

    /** Dias sugeridos para a quantidade escolhida (1 = seg). */
    fun diasSugeridos(n: Int): List<Int> = when (n) {
        1 -> listOf(1)
        2 -> listOf(2, 5)
        3 -> listOf(1, 3, 5)
        4 -> listOf(1, 2, 4, 5)
        5 -> listOf(1, 2, 3, 5, 6)
        6 -> listOf(1, 2, 3, 4, 5, 6)
        else -> (1..7).toList()
    }
}

/** Respostas já interpretadas para o gerador. */
data class Perfil(
    val nome: String,
    val modalidade: Modalidade,
    val objetivo: Objetivo,
    val nivel: Nivel,
    val dias: List<Int>,
    val minutos: Int,
    val equip: Set<String>,
    val evitar: Set<String>,
    val idade: Int,
    val sexo: String,
    val alturaCm: Int,
    val pesoKg: Int,
    val gestante: Boolean,
    val parq: Set<String>,
    val emCasa: Boolean,
    val cardioHibrido: String,
    val corridaMeta: String,
    val correContinuo: Boolean,
    val tempo5kMin: Int?,
    val bikeTipo: String,
    val ftp: Int?,
    val lutaArte: String,
    val lutaTecnicos: Int,
    val lutaSemanas: Int?,
    val atletaEsporte: String,
    val atletaFase: String,
) {
    val imc: Double get() = pesoKg / ((alturaCm / 100.0) * (alturaCm / 100.0))

    companion object {
        private val ACADEMIA = setOf("corpo", "barra", "halter", "maquina", "polia", "banco", "kettlebell", "barra_fixa", "elastico", "bola", "corda", "rolo", "bike", "esteira", "outro", "rua", "pista")

        fun de(r: Respostas): Perfil {
            val m = Modalidade.de(r.um("modalidade")) ?: Modalidade.CASA_CORPO
            val emCasa = m == Modalidade.CASA_CORPO || m == Modalidade.CASA_ELASTICO || r.um("local") == "casa"
            val extras = r["equipamentos"].orEmpty().toSet()
            val equip = buildSet {
                if (emCasa) {
                    add("corpo"); add("rua"); addAll(extras)
                    if (m == Modalidade.CASA_ELASTICO) add("elastico")
                } else {
                    addAll(ACADEMIA)
                }
                if (m == Modalidade.LUTA) { add("saco"); add("corpo") }
                if (m == Modalidade.BIKE) add("bike")
                if (m == Modalidade.CORRIDA) { add("rua"); add("pista") }
                if (m == Modalidade.HIBRIDO && r.um("hibrido_cardio") == "bike") add("bike")
            }
            val lim = r["limitacoes"].orEmpty().filter { it != "nenhuma" }.toMutableSet()
            val nivel = Nivel.de(r.um("experiencia")) ?: Nivel.INICIANTE
            val idade = r.num("idade") ?: 30
            val altura = r.num("altura") ?: 170
            val peso = r.num("peso") ?: 70
            val imc = peso / ((altura / 100.0) * (altura / 100.0))
            if (idade >= 60 || (nivel == Nivel.INICIANTE && imc >= 32) || lim.contains("joelho") || r.um("gestante") == "sim") lim.add("impacto")
            val dias = r["dias_semana"].orEmpty().mapNotNull { it.toIntOrNull() }.sorted()
                .ifEmpty { Questionario.diasSugeridos(r.num("dias") ?: 3) }
            val objPadrao = when (m) {
                Modalidade.MOBILIDADE, Modalidade.LONGEVIDADE -> Objetivo.SAUDE
                Modalidade.ATLETA, Modalidade.LUTA -> Objetivo.PERFORMANCE
                Modalidade.CORRIDA, Modalidade.BIKE -> Objetivo.RESISTENCIA
                else -> Objetivo.MASSA
            }
            return Perfil(
                nome = r.um("nome").orEmpty().trim(),
                modalidade = m,
                objetivo = Objetivo.de(r.um("objetivo")) ?: objPadrao,
                nivel = nivel,
                dias = dias,
                minutos = r.num("minutos") ?: 45,
                equip = equip,
                evitar = lim,
                idade = idade,
                sexo = r.um("sexo") ?: "x",
                alturaCm = altura,
                pesoKg = peso,
                gestante = r.um("gestante") == "sim",
                parq = r["parq"].orEmpty().filter { it != "nenhuma" }.toSet(),
                emCasa = emCasa,
                cardioHibrido = r.um("hibrido_cardio") ?: "corrida",
                corridaMeta = r.um("corrida_meta") ?: "saude",
                correContinuo = r.um("corrida_continuo") != "nao" && r.um("corrida_meta") != "comecar",
                tempo5kMin = r.num("corrida_5k"),
                bikeTipo = r.um("bike_tipo") ?: "indoor",
                ftp = r.num("bike_ftp"),
                lutaArte = r.um("luta_arte") ?: "mma",
                lutaTecnicos = r.num("luta_tecnicos") ?: 3,
                lutaSemanas = r.um("luta_marcada")?.toIntOrNull(),
                atletaEsporte = r.um("atleta_esporte") ?: "coletivo",
                atletaFase = r.um("atleta_fase") ?: "fora",
            )
        }
    }
}
