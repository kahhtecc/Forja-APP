package com.forja.app.ui

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.CheckCircle
import androidx.compose.material.icons.rounded.FitnessCenter
import androidx.compose.material.icons.rounded.Lightbulb
import androidx.compose.material.icons.rounded.NightsStay
import androidx.compose.material.icons.rounded.PlayArrow
import androidx.compose.material.icons.rounded.Schedule
import androidx.compose.material.icons.rounded.WarningAmber
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.forja.app.AppViewModel
import com.forja.app.core.Datas
import com.forja.app.core.Estado
import com.forja.app.core.Progresso
import com.forja.app.core.Questionario
import com.forja.app.core.Rotina
import com.forja.app.core.Rotinas
import com.forja.app.core.Sessao
import com.forja.app.core.TipoBloco
import java.time.LocalDate
import java.time.LocalTime
import java.time.format.DateTimeFormatter
import java.util.Locale

private val PT = Locale("pt", "BR")

@Composable
fun TelaHoje(vm: AppViewModel, estado: Estado, nav: Navegador, onAba: (Aba) -> Unit) {
    val plano = estado.plano ?: return
    val loja = vm.loja
    val hoje = loja.hoje()
    val w = loja.semanaAtual()
    val semana = plano.semanas[w - 1]
    val feitas = Progresso.feitas(estado.registros, w)
    val deHoje = loja.sessaoDeHoje()
    val proxima = loja.proximaSessao()
    val corM = Cor.modalidade(plano.modalidade)
    val nome = estado.perfil?.nome.orEmpty()
    val minutosSemana = estado.registros.filter { it.epochDay >= Datas.segunda(hoje) }.sumOf { it.duracaoSeg } / 60

    LazyColumn(Modifier.fillMaxSize(), contentPadding = PaddingValues(start = 20.dp, end = 20.dp, top = 8.dp, bottom = ESPACO_BARRA)) {
        item {
            Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.padding(vertical = 8.dp)) {
                Column(Modifier.weight(1f)) {
                    Rotulo(LocalDate.ofEpochDay(hoje).format(DateTimeFormatter.ofPattern("EEEE, d 'de' MMMM", PT)))
                    val h = LocalTime.now().hour
                    val saud = if (h < 12) "Bom dia" else if (h < 18) "Boa tarde" else "Boa noite"
                    Text(if (nome.isNotBlank()) "$saud, $nome" else saud, style = Tipo.Titulo1, color = Cor.Texto, maxLines = 1, overflow = TextOverflow.Ellipsis)
                }
                Box(
                    Modifier.size(48.dp).clip(CircleShape).background(Cor.gradBrasa).toque("Perfil e ajustes") { nav.ir(Rota.Perfil) },
                    contentAlignment = Alignment.Center,
                ) { Text(nome.take(1).uppercase().ifBlank { "F" }, style = Tipo.Titulo3, color = Color.White) }
            }
            Spacer(Modifier.height(14.dp))
        }
        item {
            val (idx, ses) = when {
                deHoje != null -> deHoje
                proxima != null -> proxima
                else -> null to null
            }
            when {
                ses != null && idx != null && idx !in feitas -> Hero(vm, ses, w, semana.fase, corM, deHoje?.first == idx,
                    onComecar = { nav.ir(Rota.Treino(w, idx)) }, onDetalhes = { nav.ir(Rota.SessaoDet(w, idx)) })
                deHoje != null && deHoje.first in feitas -> Concluido(deHoje.second, corM, proxima, onProxima = { proxima?.let { nav.ir(Rota.SessaoDet(w, it.first)) } })
                else -> SemanaCompleta(corM, w, plano.semanas.size, onPlano = { onAba(Aba.PLANO) })
            }
        }
        item {
            Secao("Esta semana", "Ver plano") { onAba(Aba.PLANO) }
            Faixa7Dias(semana.sessoes, feitas, Datas.diaSemana(hoje), corM) { i -> nav.ir(Rota.SessaoDet(w, i)) }
            Spacer(Modifier.height(14.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                Cartao(Modifier.weight(1f), padding = PaddingValues(16.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Anel(feitas.size.toFloat() / semana.sessoes.size, Modifier.size(54.dp), cor = corM, espessura = 7.dp) {
                            Text("${feitas.size}/${semana.sessoes.size}", style = Tipo.PequenoForte, color = Cor.Texto)
                        }
                        Spacer(Modifier.width(12.dp))
                        Column {
                            Text("Treinos", style = Tipo.CorpoForte, color = Cor.Texto)
                            Text("semana $w de ${plano.semanas.size}", style = Tipo.Pequeno, color = Cor.Texto2)
                        }
                    }
                }
                Cartao(Modifier.weight(1f), padding = PaddingValues(16.dp)) {
                    Estatistica("$minutosSemana", "minutos ativos nesta semana", cor = Cor.Texto)
                }
            }
            Spacer(Modifier.height(12.dp))
            val seq = Progresso.sequenciaSemanas(estado.registros, plano, w)
            val total = estado.registros.size
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                Cartao(Modifier.weight(1f), padding = PaddingValues(16.dp)) { Estatistica("$seq", if (seq == 1) "semana completa seguida" else "semanas completas seguidas", cor = corM) }
                Cartao(Modifier.weight(1f), padding = PaddingValues(16.dp)) { Estatistica("$total", "treinos concluídos no total") }
            }
        }
        item {
            Secao("Mobilidade para você", "Ver todas") { onAba(Aba.MOBILIDADE) }
        }
        item {
            LazyRow(horizontalArrangement = Arrangement.spacedBy(12.dp), contentPadding = PaddingValues(end = 20.dp)) {
                items(Rotinas.recomendadas(plano.modalidade, estado.perfil)) { r -> CartaoRotinaPequeno(vm, r) { nav.ir(Rota.RotinaDet(r.id)) } }
            }
        }
        if (plano.alertas.isNotEmpty()) item {
            Spacer(Modifier.height(18.dp))
            plano.alertas.forEach { a ->
                Row(Modifier.fillMaxWidth().padding(bottom = 8.dp).clip(RoundedCornerShape(18.dp)).background(Cor.Alerta.copy(alpha = 0.09f)).padding(14.dp)) {
                    Icon(Icons.Rounded.WarningAmber, null, tint = Cor.Alerta, modifier = Modifier.size(20.dp))
                    Spacer(Modifier.width(10.dp))
                    Text(a, style = Tipo.Pequeno, color = Cor.Texto)
                }
            }
        }
        item {
            val dicas = plano.dicas
            if (dicas.isNotEmpty()) {
                Secao("Dica do dia")
                Cartao(Modifier.fillMaxWidth()) {
                    Row {
                        IconeRedondo(Icons.Rounded.Lightbulb, Cor.Alerta, 40.dp)
                        Spacer(Modifier.width(14.dp))
                        Text(dicas[(hoje % dicas.size).toInt()], style = Tipo.Corpo, color = Cor.Texto)
                    }
                }
            }
        }
    }
}

/** Exercício que representa a sessão (primeiro do bloco principal). */
fun capaSessao(s: Sessao): String? =
    (s.blocos.firstOrNull { it.tipo != TipoBloco.AQUECIMENTO } ?: s.blocos.firstOrNull())?.itens?.firstOrNull()?.exId

@Composable
private fun Hero(vm: AppViewModel, s: Sessao, w: Int, fase: String, corM: Color, ehHoje: Boolean, onComecar: () -> Unit, onDetalhes: () -> Unit) {
    val cor = Cor.tipoSessao(s.tipo, corM)
    val capa = capaSessao(s)?.let { vm.catalogo[it] }
    val img = imagemAsset(capa?.takeIf { it.temImagem }?.let { "img/${it.id}_1.webp" })
    val forma = RoundedCornerShape(28.dp)
    Box(Modifier.fillMaxWidth().height(380.dp).clip(forma).background(Cor.Sup2).border(1.dp, Cor.Borda, forma).toque("Detalhes do treino ${s.titulo}", onDetalhes)) {
        if (img != null) Image(img, null, Modifier.fillMaxSize(), contentScale = ContentScale.Crop)
        Box(Modifier.fillMaxSize().background(Brush.verticalGradient(0f to Color.Black.copy(alpha = 0.15f), 0.45f to Color.Transparent, 1f to Cor.Fundo.copy(alpha = 0.97f))))
        Box(Modifier.fillMaxSize().background(Brush.radialGradient(listOf(cor.copy(alpha = 0.22f), Color.Transparent))))
        Row(Modifier.padding(18.dp)) {
            Etiqueta(if (ehHoje) "HOJE" else "PRÓXIMO", cor, cheia = true)
            Spacer(Modifier.width(8.dp))
            Etiqueta("Semana $w · $fase", Cor.Texto)
        }
        Column(Modifier.align(Alignment.BottomStart).padding(20.dp)) {
            Text(s.titulo, style = Tipo.Titulo1, color = Cor.Texto, maxLines = 2, overflow = TextOverflow.Ellipsis)
            Spacer(Modifier.height(6.dp))
            Text(s.foco, style = Tipo.Corpo, color = Cor.Texto2)
            Spacer(Modifier.height(14.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Etiqueta("${s.minutos} min", cor, Icons.Rounded.Schedule)
                val n = s.blocos.filter { it.tipo != TipoBloco.AQUECIMENTO && it.tipo != TipoBloco.DESAQUECIMENTO }.sumOf { it.itens.size }
                Etiqueta("$n ${if (n == 1) "exercício" else "exercícios"}", cor, Icons.Rounded.FitnessCenter)
            }
            Spacer(Modifier.height(18.dp))
            BotaoPrimario("Começar treino", Modifier.fillMaxWidth(), icone = Icons.Rounded.PlayArrow, cor = if (cor == Cor.Brasa) null else cor, onClick = onComecar)
        }
    }
}

@Composable
private fun Concluido(s: Sessao, cor: Color, proxima: Pair<Int, Sessao>?, onProxima: () -> Unit) {
    Cartao(Modifier.fillMaxWidth(), cor = Cor.Ok.copy(alpha = 0.08f), borda = Cor.Ok.copy(alpha = 0.4f)) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Rounded.CheckCircle, null, tint = Cor.Ok, modifier = Modifier.size(36.dp))
            Spacer(Modifier.width(14.dp))
            Column {
                Rotulo("Treino de hoje concluído", Cor.Ok)
                Text(s.titulo, style = Tipo.Titulo2, color = Cor.Texto)
            }
        }
        Spacer(Modifier.height(10.dp))
        Text("Recupere bem: hidratação, proteína e sono. ${if (proxima != null) "O próximo é ${proxima.second.titulo} (${Questionario.DIAS_NOMES[proxima.second.diaSemana - 1]})." else ""}", style = Tipo.Pequeno, color = Cor.Texto2)
        if (proxima != null) {
            Spacer(Modifier.height(14.dp))
            BotaoSecundario("Ver próximo treino", Modifier.fillMaxWidth(), onClick = onProxima)
        }
    }
}

@Composable
private fun SemanaCompleta(cor: Color, w: Int, total: Int, onPlano: () -> Unit) {
    Cartao(Modifier.fillMaxWidth()) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            IconeRedondo(Icons.Rounded.NightsStay, cor, 48.dp)
            Spacer(Modifier.width(14.dp))
            Column {
                Rotulo(if (w >= total) "Plano concluído" else "Semana completa", cor)
                Text(if (w >= total) "Você fechou o ciclo!" else "Tudo feito por aqui", style = Tipo.Titulo2, color = Cor.Texto)
            }
        }
        Spacer(Modifier.height(10.dp))
        Text(if (w >= total) "Refaça o questionário no perfil para gerar o próximo bloco com novos estímulos." else "Aproveite para descansar ou faça uma rotina de mobilidade.", style = Tipo.Pequeno, color = Cor.Texto2)
        Spacer(Modifier.height(14.dp))
        BotaoSecundario("Ver plano", Modifier.fillMaxWidth(), onClick = onPlano)
    }
}

@Composable
fun Faixa7Dias(sessoes: List<Sessao>, feitas: Set<Int>, hojeDia: Int?, cor: Color, onSessao: (Int) -> Unit) {
    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
        for (d in 1..7) {
            val i = sessoes.indexOfFirst { it.diaSemana == d }
            val feita = i in feitas
            val ehHoje = d == hojeDia
            val corS = if (i >= 0) Cor.tipoSessao(sessoes[i].tipo, cor) else Cor.Texto3
            Column(horizontalAlignment = Alignment.CenterHorizontally, modifier = Modifier.width(42.dp)
                .then(if (i >= 0) Modifier.toque("${Questionario.DIAS_NOMES[d - 1]}: ${sessoes[i].titulo}") { onSessao(i) } else Modifier)) {
                Text(Questionario.DIAS_NOMES[d - 1].take(3), style = Tipo.PequenoForte, color = if (ehHoje) Cor.Texto else Cor.Texto3)
                Spacer(Modifier.height(6.dp))
                Box(
                    Modifier.size(40.dp).clip(CircleShape)
                        .background(if (feita) corS else if (ehHoje) Cor.Sup3 else Cor.Sup1)
                        .border(if (ehHoje) 2.dp else 1.dp, if (i >= 0 && !feita) corS.copy(alpha = if (ehHoje) 1f else 0.6f) else if (ehHoje) Cor.Texto else Cor.Borda, CircleShape),
                    contentAlignment = Alignment.Center,
                ) {
                    when {
                        feita -> Icon(Icons.Rounded.CheckCircle, null, tint = Cor.Fundo, modifier = Modifier.size(20.dp))
                        i >= 0 -> Box(Modifier.size(8.dp).clip(CircleShape).background(corS))
                        else -> Text("·", style = Tipo.CorpoForte, color = Cor.Texto3)
                    }
                }
            }
        }
    }
}

@Composable
fun CartaoRotinaPequeno(vm: AppViewModel, r: Rotina, onClick: () -> Unit) {
    val cor = Cor.tema(r.tema)
    val ex = r.sessao.blocos.first().itens.getOrNull(1)?.let { vm.catalogo[it.exId] } ?: r.sessao.blocos.first().itens.first().let { vm.catalogo[it.exId] }
    val forma = RoundedCornerShape(22.dp)
    Column(Modifier.width(220.dp).clip(forma).background(Cor.Sup1).border(1.dp, Cor.Borda, forma).toque(r.titulo, onClick)) {
        Box(Modifier.fillMaxWidth().height(110.dp)) {
            if (ex != null) DemoExercicio(ex, Modifier.fillMaxSize(), cor = cor, animar = false, cantos = 0.dp)
            Box(Modifier.padding(10.dp)) { Etiqueta(r.categoria, cor, cheia = true) }
        }
        Column(Modifier.padding(14.dp)) {
            Text(r.titulo, style = Tipo.CorpoForte, color = Cor.Texto, maxLines = 1, overflow = TextOverflow.Ellipsis)
            Text("${com.forja.app.core.Roteiro.minutos(r.sessao, vm.catalogo)} min · ${r.subtitulo}", style = Tipo.Pequeno, color = Cor.Texto2, maxLines = 2, overflow = TextOverflow.Ellipsis)
        }
    }
}
