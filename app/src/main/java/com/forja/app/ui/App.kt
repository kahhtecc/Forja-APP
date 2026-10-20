package com.forja.app.ui

import androidx.activity.compose.BackHandler
import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.CalendarMonth
import androidx.compose.material.icons.rounded.FitnessCenter
import androidx.compose.material.icons.rounded.Insights
import androidx.compose.material.icons.rounded.LocalFireDepartment
import androidx.compose.material.icons.rounded.SelfImprovement
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.runtime.LaunchedEffect
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.forja.app.AppViewModel
import com.forja.app.core.Registro

sealed interface Rota {
    data object Abas : Rota
    data object Questionario : Rota
    data object Perfil : Rota
    data object Fontes : Rota
    data class SessaoDet(val semana: Int, val idx: Int) : Rota
    data class RotinaDet(val id: String) : Rota
    data class Treino(val semana: Int, val idx: Int) : Rota
    data class TreinoRotina(val id: String) : Rota
    data class ExercicioDet(val id: String, val troca: Troca? = null) : Rota
    data class Video(val exId: String) : Rota
    data class Concluido(val registro: Registro, val novo: Boolean) : Rota
}

data class Troca(val sessaoIdx: Int, val original: String)

enum class Aba(val nome: String, val icone: ImageVector) {
    HOJE("Hoje", Icons.Rounded.LocalFireDepartment),
    PLANO("Plano", Icons.Rounded.CalendarMonth),
    MOBILIDADE("Mobilidade", Icons.Rounded.SelfImprovement),
    EXERCICIOS("Exercícios", Icons.Rounded.FitnessCenter),
    PROGRESSO("Progresso", Icons.Rounded.Insights),
}

class Navegador(inicial: List<Rota>) {
    val pilha = mutableStateListOf<Rota>().apply { addAll(inicial) }
    val atual: Rota get() = pilha.last()
    fun ir(r: Rota) { pilha.add(r) }
    fun voltar(): Boolean = if (pilha.size > 1) { pilha.removeAt(pilha.lastIndex); true } else false
    fun substituir(r: Rota) { pilha.removeAt(pilha.lastIndex); pilha.add(r) }
    fun raiz(r: Rota) { pilha.clear(); pilha.add(r) }
}

@Composable
fun App(vm: AppViewModel, telaInicial: String?, manterTela: (Boolean) -> Unit) {
    val loja = vm.loja
    val estado by loja.estado.collectAsStateWithLifecycle()
    var aba by rememberSaveable { mutableStateOf(Aba.HOJE) }
    val nav = remember {
        val inicial = mutableListOf<Rota>(if (loja.estado.value.temPlano) Rota.Abas else Rota.Questionario)
        if (loja.estado.value.temPlano) when {
            telaInicial == null || telaInicial == "home" -> {}
            telaInicial == "quiz" -> inicial += Rota.Questionario
            telaInicial == "perfil" -> inicial += Rota.Perfil
            telaInicial == "fontes" -> inicial += Rota.Fontes
            telaInicial == "sessao" || telaInicial == "player" -> {
                val (i, _) = loja.proximaSessao() ?: (0 to null)
                inicial += if (telaInicial == "sessao") Rota.SessaoDet(loja.semanaAtual(), i) else Rota.Treino(loja.semanaAtual(), i)
            }
            telaInicial.startsWith("exercicio:") -> inicial += Rota.ExercicioDet(telaInicial.substringAfter(":"))
            telaInicial.startsWith("video:") -> inicial += Rota.Video(telaInicial.substringAfter(":"))
            telaInicial.startsWith("rotina:") -> inicial += Rota.RotinaDet(telaInicial.substringAfter(":"))
            telaInicial.startsWith("treinorotina:") -> inicial += Rota.TreinoRotina(telaInicial.substringAfter(":"))
            else -> Aba.entries.firstOrNull { it.name.equals(telaInicial, true) }?.let { aba = it }
        }
        Navegador(inicial)
    }
    BackHandler(enabled = nav.pilha.size > 1 || aba != Aba.HOJE) {
        if (!nav.voltar()) aba = Aba.HOJE
    }
    val emTreino = nav.atual is Rota.Treino || nav.atual is Rota.TreinoRotina
    DisposableEffect(emTreino, estado.ajustes.telaLigada) {
        manterTela(emTreino && estado.ajustes.telaLigada)
        onDispose { }
    }

    Box(Modifier.fillMaxSize().background(Cor.Fundo)) {
        AnimatedContent(nav.atual, transitionSpec = { fadeIn(tween(220)) togetherWith fadeOut(tween(160)) }, label = "rota") { rota ->
            Box(Modifier.fillMaxSize().statusBarsPadding()) {
                when (rota) {
                    Rota.Abas -> Abas(vm, estado, aba, onAba = { aba = it }, nav)
                    Rota.Questionario -> TelaQuestionario(vm, estado, podeVoltar = estado.temPlano, onVoltar = { nav.voltar() }, onConcluir = {
                        aba = Aba.HOJE; nav.raiz(Rota.Abas)
                    })
                    Rota.Perfil -> TelaPerfil(vm, estado, nav)
                    Rota.Fontes -> TelaFontes(vm, onVoltar = { nav.voltar() })
                    is Rota.SessaoDet -> TelaSessao(vm, estado, rota.semana, rota.idx, nav)
                    is Rota.RotinaDet -> TelaRotina(vm, rota.id, nav)
                    is Rota.Treino -> {
                        val ses = estado.plano?.semanas?.getOrNull(rota.semana - 1)?.sessoes?.getOrNull(rota.idx)
                        if (ses == null) LaunchedEffect(Unit) { nav.voltar() } else TelaTreino(vm, estado, ses, rota.semana, rota.idx, onSair = { nav.voltar() }, onFim = { reg -> nav.substituir(Rota.Concluido(reg, true)) }, nav)
                    }
                    is Rota.TreinoRotina -> {
                        val r = com.forja.app.core.Rotinas.porId(rota.id)
                        if (r == null) LaunchedEffect(Unit) { nav.voltar() } else TelaTreino(vm, estado, r.sessao, 0, -1, onSair = { nav.voltar() }, onFim = { reg -> nav.substituir(Rota.Concluido(reg, true)) }, nav)
                    }
                    is Rota.ExercicioDet -> TelaExercicio(vm, estado, rota.id, rota.troca, nav)
                    is Rota.Video -> TelaVideo(vm, rota.exId, onVoltar = { nav.voltar() })
                    is Rota.Concluido -> TelaConcluido(vm, estado, rota.registro, rota.novo, onFechar = { aba = Aba.HOJE; nav.raiz(Rota.Abas) })
                }
            }
        }
    }
}

@Composable
private fun Abas(vm: AppViewModel, estado: com.forja.app.core.Estado, aba: Aba, onAba: (Aba) -> Unit, nav: Navegador) {
    Box(Modifier.fillMaxSize()) {
        Box(Modifier.fillMaxSize()) {
            when (aba) {
                Aba.HOJE -> TelaHoje(vm, estado, nav, onAba)
                Aba.PLANO -> TelaPlano(vm, estado, nav)
                Aba.MOBILIDADE -> TelaMobilidade(vm, estado, nav)
                Aba.EXERCICIOS -> TelaBiblioteca(vm, estado, nav)
                Aba.PROGRESSO -> TelaProgresso(vm, estado, nav)
            }
        }
        BarraAbas(aba, onAba, Modifier.align(Alignment.BottomCenter))
    }
}

@Composable
private fun BarraAbas(aba: Aba, onAba: (Aba) -> Unit, modifier: Modifier) {
    val forma = RoundedCornerShape(28.dp)
    Row(
        modifier.navigationBarsPadding().padding(horizontal = 14.dp, vertical = 10.dp).fillMaxWidth()
            .shadow(24.dp, forma).clip(forma).background(Cor.Sup2.copy(alpha = 0.97f)).border(1.dp, Cor.Borda, forma)
            .padding(horizontal = 6.dp, vertical = 6.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
    ) {
        Aba.entries.forEach { a ->
            val sel = a == aba
            Column(
                Modifier.weight(1f).clip(RoundedCornerShape(22.dp)).background(if (sel) Cor.Brasa.copy(alpha = 0.14f) else Cor.Sup2.copy(alpha = 0f))
                    .toque(a.nome) { onAba(a) }.padding(vertical = 8.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
            ) {
                Icon(a.icone, null, tint = if (sel) Cor.Brasa else Cor.Texto3, modifier = Modifier.size(22.dp))
                Spacer(Modifier.height(3.dp))
                Text(a.nome, style = Tipo.Rotulo.copy(letterSpacing = 0.2.sp), color = if (sel) Cor.Texto else Cor.Texto3, maxLines = 1)
            }
        }
    }
}

/** Espaço no fim das listas para não ficar atrás da barra flutuante. */
val ESPACO_BARRA = 120.dp
