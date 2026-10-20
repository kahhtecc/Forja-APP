package com.forja.app.core

enum class Modalidade(val id: String, val nome: String, val curto: String) {
    CASA_CORPO("casa_corpo", "Em casa · peso do corpo", "Casa"),
    CASA_ELASTICO("casa_elastico", "Em casa · elásticos", "Elásticos"),
    ACADEMIA("academia", "Academia · musculação", "Musculação"),
    CORRIDA("corrida", "Corrida", "Corrida"),
    BIKE("bike", "Bike · ciclismo", "Bike"),
    LUTA("luta", "Lutadores", "Luta"),
    ATLETA("atleta", "Atletas · performance", "Atleta"),
    HIIT("hiit", "HIIT & funcional", "HIIT"),
    HIBRIDO("hibrido", "Híbrido · força + corrida", "Híbrido"),
    MOBILIDADE("mobilidade", "Mobilidade & alongamento", "Mobilidade"),
    LONGEVIDADE("longevidade", "50+ · força e equilíbrio", "50+");

    companion object {
        fun de(id: String?) = entries.firstOrNull { it.id == id }
    }
}

enum class Objetivo(val id: String, val nome: String) {
    MASSA("massa", "Ganhar massa muscular"),
    EMAGRECER("emagrecer", "Perder gordura"),
    SAUDE("saude", "Saúde e vida ativa"),
    FORCA("forca", "Ficar mais forte"),
    RESISTENCIA("resistencia", "Resistência e fôlego"),
    PERFORMANCE("performance", "Performance no esporte");

    companion object {
        fun de(id: String?) = entries.firstOrNull { it.id == id }
    }
}

enum class Nivel(val id: String, val nome: String) {
    INICIANTE("iniciante", "Iniciante"),
    INTERMEDIARIO("intermediario", "Intermediário"),
    AVANCADO("avancado", "Avançado");

    companion object {
        fun de(id: String?) = entries.firstOrNull { it.id == id }
    }
}

data class Video(val id: String, val titulo: String, val canal: String, val idioma: String)

data class Exercicio(
    val id: String,
    val nome: String,
    val equip: List<String>,
    val grupo: String,
    val tipo: String,
    val nivel: Int,
    val dicas: List<String>,
    val busca: String,
    val padroes: List<String>,
    val evitar: List<String>,
    val temImagem: Boolean,
    val video: Video?,
) {
    /** Exercícios medidos em tempo (e não repetições). */
    val porTempo: Boolean
        get() = tipo in setOf("cardio", "mobilidade", "tecnica") ||
            id in setOf("prancha", "prancha-lateral", "isometria-pescoco", "farmer-walk", "equilibrio-unipodal", "monster-walk")
}

enum class TipoBloco { AQUECIMENTO, PRINCIPAL, CIRCUITO, INTERVALADO, DESAQUECIMENTO }

data class Item(
    val exId: String,
    val series: Int,
    /** Repetições alvo ("8–12"). Nulo quando é por tempo. */
    val reps: String? = null,
    /** Tempo de trabalho por série/rodada, em segundos. */
    val trabalhoSeg: Int? = null,
    val descansoSeg: Int = 60,
    val intensidade: String? = null,
    val nota: String? = null,
)

data class Bloco(
    val nome: String,
    val tipo: TipoBloco,
    val itens: List<Item>,
    /** Voltas (para circuitos). Nos demais blocos é 1 e as séries ficam em cada item. */
    val voltas: Int = 1,
    val nota: String? = null,
)

data class Sessao(
    val titulo: String,
    val foco: String,
    /** forca, corrida, bike, luta, hiit, mobilidade, cardio */
    val tipo: String,
    val minutos: Int,
    val blocos: List<Bloco>,
    /** 1 = segunda ... 7 = domingo */
    val diaSemana: Int,
)

data class Semana(val numero: Int, val fase: String, val nota: String, val sessoes: List<Sessao>)

data class Plano(
    val nome: String,
    val resumo: String,
    val modalidade: Modalidade,
    val objetivo: Objetivo,
    val nivel: Nivel,
    val semanas: List<Semana>,
    val dicas: List<String>,
    val alertas: List<String>,
    val metaSemanal: String,
)

data class SerieFeita(val exId: String, val reps: Int, val kg: Double, val seg: Int = 0)

data class Registro(
    val epochDay: Long,
    val semana: Int,
    val sessaoIdx: Int,
    val titulo: String,
    val tipo: String,
    val duracaoSeg: Int,
    val series: List<SerieFeita>,
    val esforco: Int,
    val nota: String,
)
