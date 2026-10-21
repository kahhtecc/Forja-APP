package com.forja.app.ui

import android.media.AudioManager
import android.media.ToneGenerator
import android.view.HapticFeedbackConstants
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.Add
import androidx.compose.material.icons.rounded.Check
import androidx.compose.material.icons.rounded.Close
import androidx.compose.material.icons.rounded.Favorite
import androidx.compose.material.icons.rounded.Pause
import androidx.compose.material.icons.rounded.PlayArrow
import androidx.compose.material.icons.rounded.PlayCircle
import androidx.compose.material.icons.rounded.Remove
import androidx.compose.material.icons.rounded.SkipNext
import androidx.compose.material.icons.rounded.SkipPrevious
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableDoubleStateOf
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableLongStateOf
import androidx.compose.runtime.mutableStateMapOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import com.forja.app.relogio.FcAoVivo
import com.forja.app.relogio.MonitorBle
import com.forja.app.relogio.PrefsRelogio
import com.forja.app.relogio.TreinoAoVivo
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.forja.app.AppViewModel
import com.forja.app.core.Estado
import com.forja.app.core.Passo
import com.forja.app.core.Progresso
import com.forja.app.core.Registro
import com.forja.app.core.Roteiro
import com.forja.app.core.SerieFeita
import com.forja.app.core.Sessao
import com.forja.app.core.TipoBloco
import kotlinx.coroutines.delay

/** Estado do treino em andamento — fica no ViewModel para sobreviver a abrir o vídeo ou girar a tela.
 *  A lógica (concluir série, descanso, avançar) fica aqui, fora da tela, para os botões da notificação e do
 *  relógio funcionarem mesmo com o celular bloqueado (sem recomposição). */
class EstadoTreino(val chave: String, val passos: List<Passo>) {
    val inicioMs = System.currentTimeMillis()
    var i by mutableIntStateOf(0)
    var descansando by mutableStateOf(false)
    /** Fim do cronômetro atual (trabalho por tempo ou descanso), em ms. */
    var fimMs by mutableStateOf<Long?>(null)
    var pausadoRestante by mutableStateOf<Long?>(null)
    var reps by mutableIntStateOf(0)
    var kg by mutableDoubleStateOf(0.0)
    var preparadoPara by mutableIntStateOf(-1)
    var ultimoBip by mutableIntStateOf(-1)
    val feitas = mutableStateMapOf<Int, SerieFeita>()
    val passo: Passo get() = passos[i.coerceIn(0, passos.lastIndex)]

    /** Histórico (para sugerir a carga) e ganchos definidos pela tela. */
    var registros: List<Registro> = emptyList()
    var aoFinalizar: () -> Unit = {}
    var aoMudar: () -> Unit = {}

    /** Valores padrão de reps/kg quando muda de passo. */
    fun preparar() {
        if (preparadoPara == i) return
        preparadoPara = i
        val p = passo
        val anterior = feitas.entries.lastOrNull { passos[it.key].ex.id == p.ex.id }?.value
        reps = anterior?.reps ?: repsAlvo(p)
        kg = anterior?.kg ?: Progresso.ultimas(registros, p.ex.id).maxOfOrNull { it.kg } ?: 0.0
    }

    fun irPara(n: Int, auto: Boolean = false) {
        descansando = false; fimMs = null; pausadoRestante = null
        if (n > passos.lastIndex) { aoFinalizar(); return }
        val anterior = passos.getOrNull(i)
        i = n.coerceAtLeast(0)
        val novo = passos[i]
        // Em intervalados e circuitos por tempo, o próximo esforço começa sozinho depois da pausa.
        if (auto && novo.porTempo && anterior != null && anterior.porTempo && anterior.blocoIdx == novo.blocoIdx) {
            fimMs = System.currentTimeMillis() + (novo.item.trabalhoSeg ?: 0) * 1000L
            ultimoBip = -1
        }
        preparar()
        aoMudar()
    }

    fun concluirSerie() {
        val p = passo
        feitas[i] = if (p.porTempo) SerieFeita(p.ex.id, 0, 0.0, p.item.trabalhoSeg ?: 0)
        else SerieFeita(p.ex.id, reps, if (temCarga(p)) kg else 0.0)
        if (i == passos.lastIndex) { aoFinalizar(); return }
        if (p.descansoDepois > 0) {
            descansando = true
            fimMs = System.currentTimeMillis() + p.descansoDepois * 1000L
            pausadoRestante = null
            aoMudar()
        } else irPara(i + 1)
    }

    fun iniciarTempo() {
        fimMs = System.currentTimeMillis() + (passo.item.trabalhoSeg ?: 0) * 1000L
        pausadoRestante = null; ultimoBip = -1
        aoMudar()
    }

    fun pausar() { fimMs?.let { pausadoRestante = (it - System.currentTimeMillis()).coerceAtLeast(0) }; aoMudar() }

    fun continuar() { pausadoRestante?.let { fimMs = System.currentTimeMillis() + it }; pausadoRestante = null; aoMudar() }

    fun ajustarDescanso(deltaMs: Long) {
        val agora = System.currentTimeMillis()
        fimMs = ((fimMs ?: agora) + deltaMs).coerceAtLeast(agora + 1000)
        aoMudar()
    }

    /** Ações vindas da notificação ou do relógio. Retorna true se for para encerrar o treino. */
    fun acao(a: String): Boolean {
        val agora = System.currentTimeMillis()
        when (a) {
            TreinoAoVivo.ACAO_CONCLUIR -> when {
                descansando -> irPara(i + 1)
                passo.porTempo && fimMs == null && pausadoRestante == null -> iniciarTempo()
                else -> concluirSerie()
            }
            TreinoAoVivo.ACAO_PULAR -> if (descansando) irPara(i + 1)
            TreinoAoVivo.ACAO_FIM -> {
                val f = fimMs
                if (f != null && pausadoRestante == null && f <= agora + 600) {
                    ultimoBip = 0
                    if (descansando) irPara(i + 1, auto = true) else concluirSerie()
                }
            }
            TreinoAoVivo.ACAO_ENCERRAR -> return true
        }
        return false
    }
}

private fun temCarga(p: Passo) = p.ex.equip.any { it in setOf("barra", "halter", "kettlebell", "maquina", "polia", "bola") }

private fun repsAlvo(p: Passo): Int = p.item.reps?.substringBefore("–")?.substringBefore("-")?.trim()?.substringBefore(" ")?.toIntOrNull() ?: 10

@Composable
fun TelaTreino(vm: AppViewModel, estado: Estado, sessao: Sessao, semana: Int, idx: Int, onSair: () -> Unit, onFim: (Registro) -> Unit, nav: Navegador) {
    val chave = "$semana|$idx|${sessao.titulo}"
    val t = remember(chave) {
        (vm.treino as? EstadoTreino)?.takeIf { it.chave == chave } ?: EstadoTreino(chave, Roteiro.passos(sessao, vm.catalogo)).also {
            vm.treino = it
            FcAoVivo.comecarTreino()
        }
    }
    if (t.passos.isEmpty()) { LaunchedEffect(Unit) { onSair() }; return }
    val view = LocalView.current
    val ctx = LocalContext.current
    val tom = remember { runCatching { ToneGenerator(AudioManager.STREAM_MUSIC, 70) }.getOrNull() }
    DisposableEffect(Unit) { onDispose { tom?.release() } }
    var agora by remember { mutableLongStateOf(System.currentTimeMillis()) }
    var confirmarSaida by remember { mutableStateOf(false) }
    val aj = estado.ajustes
    val corBase = Cor.tipoSessao(sessao.tipo, Cor.modalidade(estado.plano?.modalidade))
    val bpm by FcAoVivo.bpm.collectAsState()

    LaunchedEffect(Unit) { while (true) { agora = System.currentTimeMillis(); delay(200) } }

    val p = t.passo
    t.registros = estado.registros
    LaunchedEffect(t.i) { t.preparar() }

    fun finalizar() {
        val series = t.feitas.toSortedMap().values.toList()
        val fim = System.currentTimeMillis()
        val dur = ((fim - t.inicioMs) / 1000).toInt()
        val (fcMed, fcMax) = FcAoVivo.resumo()
        FcAoVivo.pararTreino()
        vm.treino = null
        TreinoAoVivo.parar(ctx)
        onFim(Registro(vm.loja.hoje(), semana, idx, sessao.titulo, sessao.tipo, dur, series, 7, "", fcMed, fcMax, fim))
    }
    fun sair() { vm.treino = null; FcAoVivo.pararTreino(); TreinoAoVivo.parar(ctx); onSair() }
    t.aoFinalizar = { finalizar() }

    // Notificação do treino ao vivo (e relógio) + monitor cardíaco Bluetooth lembrado
    val mostrarRelogio = !vm.demo && PrefsRelogio.mostrar(ctx)
    t.aoMudar = { TreinoAoVivo.atualizar() }
    val pedir = rememberLauncherForActivityResult(ActivityResultContracts.RequestMultiplePermissions()) {
        if (vm.treino === t) TreinoAoVivo.iniciar(ctx, t, sessao.titulo)
    }
    LaunchedEffect(Unit) {
        if (!vm.demo) MonitorBle.conectarLembrado(ctx)
        if (mostrarRelogio) {
            val faltam = TreinoAoVivo.permissoesFaltando(ctx)
            if (faltam.isNotEmpty() && !PrefsRelogio.pediuPermissoes(ctx)) { PrefsRelogio.marcarPediu(ctx); pedir.launch(faltam) }
            else TreinoAoVivo.iniciar(ctx, t, sessao.titulo)
        }
    }
    DisposableEffect(Unit) {
        onDispose {
            // abrir o vídeo do exercício não encerra o treino; sair dele, sim
            if (vm.treino !== t || nav.atual !is Rota.Video) { TreinoAoVivo.parar(ctx); MonitorBle.desconectar() }
        }
    }
    val tratar by rememberUpdatedState<(String) -> Unit> { a ->
        if (t.acao(a)) { if (t.feitas.isEmpty()) sair() else finalizar() }
    }
    LaunchedEffect(Unit) { TreinoAoVivo.acoes.collect { tratar(it) } }

    fun irPara(n: Int, auto: Boolean = false) = t.irPara(n, auto)

    fun concluirSerie() {
        if (aj.vibracao) view.performHapticFeedback(HapticFeedbackConstants.LONG_PRESS)
        t.concluirSerie()
    }

    // cronômetro (trabalho por tempo ou descanso)
    val restanteMs = t.pausadoRestante ?: t.fimMs?.let { (it - agora).coerceAtLeast(0) }
    val restanteSeg = restanteMs?.let { ((it + 999) / 1000).toInt() }
    LaunchedEffect(restanteSeg, t.pausadoRestante) {
        val r = restanteSeg ?: return@LaunchedEffect
        if (t.pausadoRestante != null) return@LaunchedEffect
        if (r in 1..3 && t.ultimoBip != r) {
            t.ultimoBip = r
            if (aj.som) tom?.startTone(ToneGenerator.TONE_PROP_BEEP, 120)
            if (aj.vibracao) view.performHapticFeedback(HapticFeedbackConstants.KEYBOARD_TAP)
        }
        if (r == 0 && t.ultimoBip != 0) {
            t.ultimoBip = 0
            if (aj.som) tom?.startTone(ToneGenerator.TONE_PROP_ACK, 350)
            if (aj.vibracao) view.performHapticFeedback(HapticFeedbackConstants.LONG_PRESS)
            if (t.descansando) irPara(t.i + 1, auto = true) else concluirSerie()
        }
        if (r > 3) t.ultimoBip = -1
    }

    val decorrido = ((agora - t.inicioMs) / 1000).toInt()
    val cor = corBase

    Box(Modifier.fillMaxSize().background(Cor.Fundo)) {
        Column(Modifier.fillMaxSize()) {
            // topo
            Row(Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 10.dp), verticalAlignment = Alignment.CenterVertically) {
                BotaoIcone(Icons.Rounded.Close, "Sair do treino") { confirmarSaida = true }
                Column(Modifier.weight(1f), horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(if (decorrido >= 3600) "%d:%02d:%02d".format(decorrido / 3600, decorrido % 3600 / 60, decorrido % 60) else "%d:%02d".format(decorrido / 60, decorrido % 60),
                        style = Tipo.Numero.copy(fontSize = 24.sp), color = Cor.Texto)
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Rotulo(p.blocoNome, cor)
                        val fc = bpm?.takeIf { agora - FcAoVivo.ultimoMs < 10_000 }
                        if (fc != null) {
                            Spacer(Modifier.width(8.dp))
                            Icon(Icons.Rounded.Favorite, "Frequência cardíaca", tint = Cor.Perigo, modifier = Modifier.size(13.dp))
                            Spacer(Modifier.width(3.dp))
                            Text("$fc bpm", style = Tipo.PequenoForte, color = Cor.Texto)
                        }
                    }
                }
                BotaoIcone(Icons.Rounded.PlayCircle, "Ver vídeo de ${p.ex.nome}", cor = cor) { nav.ir(Rota.Video(p.ex.id)) }
            }
            // progresso segmentado por exercício
            Row(Modifier.fillMaxWidth().padding(horizontal = 16.dp), horizontalArrangement = Arrangement.spacedBy(3.dp)) {
                val grupos = t.passos.indices.groupBy { t.passos[it].blocoIdx to t.passos[it].itemIdx }.values.toList().let { g ->
                    if (g.size > 24) t.passos.indices.groupBy { t.passos[it].blocoIdx }.values.toList() else g
                }
                grupos.forEach { g ->
                    val prog = g.count { it < t.i || t.feitas.containsKey(it) } / g.size.toFloat()
                    BarraProgresso(prog, Modifier.weight(g.size.toFloat().coerceAtMost(4f)), cor = cor, altura = 4.dp)
                }
            }
            Column(Modifier.weight(1f).verticalScroll(rememberScrollState()).padding(horizontal = 20.dp)) {
                Spacer(Modifier.height(14.dp))
                DemoExercicio(p.ex, Modifier.fillMaxWidth().aspectRatio(1.45f), cor = cor, cantos = 26.dp)
                Spacer(Modifier.height(16.dp))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Rotulo(p.rotulo, cor)
                    Spacer(Modifier.weight(1f))
                    Text("${t.i + 1} / ${t.passos.size}", style = Tipo.Pequeno, color = Cor.Texto3)
                }
                Spacer(Modifier.height(4.dp))
                Text(p.ex.nome, style = Tipo.Titulo1, color = Cor.Texto)
                Spacer(Modifier.height(10.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Etiqueta(if (p.porTempo) Roteiro.formatarTempo(p.item.trabalhoSeg ?: 0) else "${p.item.reps} reps", cor, cheia = true)
                    if (p.item.intensidade != null) Etiqueta(p.item.intensidade, cor)
                }
                if (p.item.nota != null) {
                    Spacer(Modifier.height(8.dp))
                    Text(p.item.nota, style = Tipo.Pequeno, color = Cor.Texto2)
                }
                Spacer(Modifier.height(18.dp))
                if (p.porTempo) {
                    Box(Modifier.fillMaxWidth(), contentAlignment = Alignment.Center) {
                        val total = (p.item.trabalhoSeg ?: 1) * 1000f
                        val prog = if (restanteMs == null || t.descansando) 0f else 1f - restanteMs / total
                        Anel(prog, Modifier.size(190.dp), cor = cor, espessura = 12.dp) {
                            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                val seg = if (t.descansando || restanteSeg == null) (p.item.trabalhoSeg ?: 0) else restanteSeg
                                Text(relogio(seg), style = Tipo.Gigante, color = Cor.Texto)
                                Text(if (t.fimMs == null && t.pausadoRestante == null) "toque em iniciar" else if (t.pausadoRestante != null) "pausado" else "em andamento", style = Tipo.Pequeno, color = Cor.Texto2)
                            }
                        }
                    }
                } else {
                    Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                        Contador("Repetições", "${t.reps}", Modifier.weight(1f), onMenos = { t.reps = (t.reps - 1).coerceAtLeast(0) }, onMais = { t.reps += 1 })
                        if (temCarga(p)) Contador("Carga (kg)", Progresso.fmtKg(t.kg), Modifier.weight(1f), onMenos = { t.kg = (t.kg - 2.5).coerceAtLeast(0.0) }, onMais = { t.kg += 2.5 })
                    }
                    Progresso.sugestao(estado.registros, p.item)?.let {
                        Spacer(Modifier.height(10.dp))
                        Text(it, style = Tipo.Pequeno, color = Cor.Texto2)
                    }
                }
                Spacer(Modifier.height(18.dp))
                Cartao(Modifier.fillMaxWidth(), padding = PaddingValues(16.dp)) {
                    Rotulo("Execução", cor)
                    Spacer(Modifier.height(8.dp))
                    p.ex.dicas.forEachIndexed { k, d ->
                        Row(Modifier.padding(vertical = 3.dp)) {
                            Text("${k + 1}", style = Tipo.PequenoForte, color = cor, modifier = Modifier.width(18.dp))
                            Text(d, style = Tipo.Pequeno, color = Cor.Texto)
                        }
                    }
                }
                Spacer(Modifier.height(16.dp))
            }
            // controles
            Row(Modifier.navigationBarsPadding().padding(horizontal = 16.dp, vertical = 12.dp), verticalAlignment = Alignment.CenterVertically) {
                BotaoIcone(Icons.Rounded.SkipPrevious, "Anterior", tamanho = 54.dp) { irPara(t.i - 1) }
                Spacer(Modifier.width(10.dp))
                if (p.porTempo) {
                    val rodando = t.fimMs != null && t.pausadoRestante == null
                    BotaoPrimario(if (rodando) "Pausar" else if (t.pausadoRestante != null) "Continuar" else "Iniciar", Modifier.weight(1f),
                        icone = if (rodando) Icons.Rounded.Pause else Icons.Rounded.PlayArrow, cor = if (cor == Cor.Brasa) null else cor) {
                        when {
                            rodando -> t.pausar()
                            t.pausadoRestante != null -> t.continuar()
                            else -> t.iniciarTempo()
                        }
                    }
                } else {
                    BotaoPrimario(if (t.i == t.passos.lastIndex) "Finalizar treino" else "Concluir série", Modifier.weight(1f), icone = Icons.Rounded.Check, cor = if (cor == Cor.Brasa) null else cor) { concluirSerie() }
                }
                Spacer(Modifier.width(10.dp))
                BotaoIcone(Icons.Rounded.SkipNext, if (p.porTempo) "Concluir agora" else "Pular", tamanho = 54.dp) { if (p.porTempo) concluirSerie() else irPara(t.i + 1) }
            }
        }

        AnimatedVisibility(t.descansando, enter = fadeIn(), exit = fadeOut()) {
            Descanso(vm, t, restanteSeg ?: 0, p.descansoDepois, cor,
                onMais = { t.ajustarDescanso(15_000) },
                onMenos = { t.ajustarDescanso(-15_000) },
                onPular = { irPara(t.i + 1) })
        }
    }

    if (confirmarSaida) AlertDialog(
        onDismissRequest = { confirmarSaida = false },
        containerColor = Cor.Sup2,
        title = { Text("Sair do treino?", style = Tipo.Titulo3, color = Cor.Texto) },
        text = { Text(if (t.feitas.isEmpty()) "Nada foi registrado ainda." else "Você pode salvar o que já fez (${t.feitas.size} séries) ou descartar.", style = Tipo.Corpo, color = Cor.Texto2) },
        confirmButton = {
            TextButton(onClick = { confirmarSaida = false; if (t.feitas.isEmpty()) sair() else finalizar() }) {
                Text(if (t.feitas.isEmpty()) "Sair" else "Salvar e sair", style = Tipo.Botao, color = Cor.Brasa)
            }
        },
        dismissButton = {
            TextButton(onClick = { confirmarSaida = false; if (t.feitas.isNotEmpty()) sair() }) { Text(if (t.feitas.isEmpty()) "Continuar treinando" else "Descartar", style = Tipo.Botao, color = Cor.Texto2) }
        },
    )
}

fun relogio(seg: Int): String = if (seg >= 60) "%d:%02d".format(seg / 60, seg % 60) else "$seg"

@Composable
private fun Contador(rotulo: String, valor: String, modifier: Modifier, onMenos: () -> Unit, onMais: () -> Unit) {
    Cartao(modifier, padding = PaddingValues(12.dp)) {
        Rotulo(rotulo)
        Spacer(Modifier.height(6.dp))
        Row(verticalAlignment = Alignment.CenterVertically) {
            BotaoIcone(Icons.Rounded.Remove, "Menos $rotulo", tamanho = 40.dp, onClick = onMenos)
            Text(valor, style = Tipo.Titulo1, color = Cor.Texto, textAlign = TextAlign.Center, modifier = Modifier.weight(1f), maxLines = 1)
            BotaoIcone(Icons.Rounded.Add, "Mais $rotulo", tamanho = 40.dp, onClick = onMais)
        }
    }
}

@Composable
private fun Descanso(vm: AppViewModel, t: EstadoTreino, restante: Int, total: Int, cor: Color, onMais: () -> Unit, onMenos: () -> Unit, onPular: () -> Unit) {
    val prox = t.passos.getOrNull(t.i + 1)
    Column(
        Modifier.fillMaxSize().background(Cor.Fundo.copy(alpha = 0.98f)).navigationBarsPadding().padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Spacer(Modifier.height(30.dp))
        Rotulo(if (prox != null && prox.tipoBloco == TipoBloco.INTERVALADO && prox.ex.id == t.passo.ex.id) "Recuperação" else "Descanso", cor)
        Spacer(Modifier.height(20.dp))
        Anel(if (total > 0) restante / total.toFloat() else 0f, Modifier.size(250.dp), cor = cor, espessura = 14.dp) {
            Text(relogio(restante), style = Tipo.Gigante.copy(fontSize = 92.sp, lineHeight = 88.sp), color = Cor.Texto)
        }
        Spacer(Modifier.height(24.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            BotaoSecundario("−15 s", onClick = onMenos)
            BotaoSecundario("+15 s", onClick = onMais)
        }
        Spacer(Modifier.weight(1f))
        if (prox != null) {
            Rotulo("A seguir")
            Spacer(Modifier.height(10.dp))
            Row(Modifier.fillMaxWidth().clip(RoundedCornerShape(20.dp)).background(Cor.Sup1).border(1.dp, Cor.Borda, RoundedCornerShape(20.dp)).padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
                DemoExercicio(prox.ex, Modifier.size(70.dp), cor = cor, animar = false, cantos = 14.dp)
                Spacer(Modifier.width(14.dp))
                Column(Modifier.weight(1f)) {
                    Text(prox.ex.nome, style = Tipo.CorpoForte, color = Cor.Texto, maxLines = 2, overflow = TextOverflow.Ellipsis)
                    Text("${prox.rotulo} · ${Roteiro.prescricao(prox.item).substringAfter("× ")}", style = Tipo.Pequeno, color = Cor.Texto2)
                }
            }
            Spacer(Modifier.height(16.dp))
        }
        BotaoPrimario("Pular descanso", Modifier.fillMaxWidth(), icone = Icons.Rounded.SkipNext, cor = if (cor == Cor.Brasa) null else cor, onClick = onPular)
    }
}
