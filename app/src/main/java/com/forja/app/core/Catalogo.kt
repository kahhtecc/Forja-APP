package com.forja.app.core

import org.json.JSONArray

class Catalogo(val exercicios: List<Exercicio>) {
    private val porId = exercicios.associateBy { it.id }

    operator fun get(id: String): Exercicio? = porId[id]
    fun exigir(id: String): Exercicio = porId[id] ?: error("Exercício desconhecido: $id")

    /** Alternativas com o mesmo padrão de movimento (para "trocar exercício"). */
    fun alternativas(ex: Exercicio, equip: Set<String>, evitar: Set<String>): List<Exercicio> =
        exercicios.filter { o ->
            o.id != ex.id && o.padroes.any { it in ex.padroes } &&
                o.equip.any { it in equip } && o.evitar.none { it in evitar }
        }

    fun grupos(): List<String> = exercicios.map { it.grupo }.distinct()

    companion object {
        fun deJson(texto: String): Catalogo {
            val arr = JSONArray(texto)
            val lista = (0 until arr.length()).map { i ->
                val o = arr.getJSONObject(i)
                fun strs(nome: String): List<String> {
                    val a = o.optJSONArray(nome) ?: return emptyList()
                    return (0 until a.length()).map { a.getString(it) }
                }
                val v = o.optJSONObject("video")
                Exercicio(
                    id = o.getString("id"),
                    nome = o.getString("nome"),
                    equip = strs("equip"),
                    grupo = o.getString("grupo"),
                    tipo = o.getString("tipo"),
                    nivel = o.optInt("nivel", 1),
                    dicas = strs("dicas"),
                    busca = o.optString("busca", o.getString("nome")),
                    padroes = strs("padroes"),
                    evitar = strs("evitar"),
                    temImagem = o.optBoolean("img", false),
                    video = v?.let { Video(it.getString("id"), it.optString("titulo"), it.optString("canal"), it.optString("idioma")) },
                )
            }
            return Catalogo(lista)
        }
    }
}
