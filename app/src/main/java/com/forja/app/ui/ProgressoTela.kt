package com.forja.app.ui

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
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
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.Add
import androidx.compose.material.icons.rounded.DeleteOutline
import androidx.compose.material.icons.rounded.EmojiEvents
import androidx.compose.material.icons.rounded.Insights
import androidx.compose.material.icons.rounded.MonitorWeight
import androidx.compose.material.icons.rounded.Remove
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableDoubleStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.forja.app.AppViewModel
import com.forja.app.core.Estado
import com.forja.app.core.Progresso
import com.forja.app.core.Registro
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import java.util.Locale

@Composable
fun TelaProgresso(vm: AppViewModel, estado: Estado, nav: Navegador) {
    val regs = estado.registros
    val hoje = vm.loja.hoje()
    val corM = Cor.modalidade(estado.plano?.modalidade)
    val semanas = Progresso.minutosPorSemana(regs, hoje)
    var apagar by remember { mutableStateOf<Registro?>(null) }
    val fmt = DateTimeFormatter.ofPattern("EEE, d MMM", Locale("pt", "BR"))

    LazyColumn(Modifier.fillMaxSize(), contentPadding = PaddingValues(start = 20.dp, end = 20.dp, bottom = ESPACO_BARRA)) {
        item {
            Column(Modifier.padding(vertical = 10.dp)) {
                Rotulo("Sua evolução", corM)
                Text("Progresso", style = Tipo.Titulo1, color = Cor.Texto)
            }
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                Cartao(Modifier.weight(1f), padding = PaddingValues(14.dp)) { Estatistica("${regs.size}", "treinos") }
                Cartao(Modifier.weight(1f), padding = PaddingValues(14.dp)) { Estatistica("${regs.sumOf { it.duracaoSeg } / 3600}h", "treinando") }
                Cartao(Modifier.weight(1f), padding = PaddingValues(14.dp)) {
                    val t = regs.sumOf { Progresso.volumeKg(it) }
                    Estatistica(if (t >= 1000) "%.1ft".format(t / 1000).replace('.', ',') else Progresso.fmtKg(t), "volume total")
                }
            }
            Secao("Minutos por semana")
            Cartao(Modifier.fillMaxWidth()) {
                val max = (semanas.maxOfOrNull { it.second } ?: 0).coerceAtLeast(60)
                Canvas(Modifier.fillMaxWidth().height(150.dp)) {
                    val n = semanas.size
                    val gap = 10.dp.toPx()
                    val bw = (size.width - gap * (n - 1)) / n
                    // linha da meta de 150 min (OMS)
                    val yMeta = size.height * (1 - 150f / max)
                    if (150 <= max) drawLine(Cor.Texto3, Offset(0f, yMeta), Offset(size.width, yMeta), strokeWidth = 1.dp.toPx(), pathEffect = androidx.compose.ui.graphics.PathEffect.dashPathEffect(floatArrayOf(8f, 8f)))
                    semanas.forEachIndexed { i, (_, m) ->
                        val h = (size.height * m / max).coerceAtLeast(4.dp.toPx())
                        drawRoundRect(
                            if (i == n - 1) Brush.verticalGradient(listOf(Cor.BrasaClara, Cor.Brasa)) else Brush.verticalGradient(listOf(corM.copy(alpha = 0.55f), corM.copy(alpha = 0.3f))),
                            Offset(i * (bw + gap), size.height - h), Size(bw, h), CornerRadius(8.dp.toPx()),
                        )
                    }
                }
                Spacer(Modifier.height(8.dp))
                Row(Modifier.fillMaxWidth()) {
                    semanas.forEachIndexed { i, (ini, m) ->
                        Column(Modifier.weight(1f), horizontalAlignment = Alignment.CenterHorizontally) {
                            Text("$m", style = Tipo.PequenoForte, color = if (i == semanas.lastIndex) Cor.Texto else Cor.Texto2)
                            Text(LocalDate.ofEpochDay(ini).format(DateTimeFormatter.ofPattern("d/M")), style = Tipo.Pequeno, color = Cor.Texto3)
                        }
                    }
                }
                Spacer(Modifier.height(8.dp))
                Text("Linha tracejada: 150 min/semana, mínimo recomendado pela OMS.", style = Tipo.Pequeno, color = Cor.Texto3)
            }
            estado.plano?.let { plano ->
                Secao("Consistência no plano")
                Cartao(Modifier.fillMaxWidth()) {
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(6.dp), verticalAlignment = Alignment.Bottom) {
                        plano.semanas.forEach { s ->
                            val f = Progresso.feitas(regs, s.numero).size
                            Column(Modifier.weight(1f), horizontalAlignment = Alignment.CenterHorizontally) {
                                Column(Modifier.fillMaxWidth().height(70.dp), verticalArrangement = Arrangement.spacedBy(3.dp, Alignment.Bottom)) {
                                    repeat(s.sessoes.size) { k ->
                                        Box(Modifier.fillMaxWidth().weight(1f).clip(RoundedCornerShape(4.dp)).background(if (s.sessoes.size - 1 - k < f) corM else Cor.Sup3))
                                    }
                                }
                                Spacer(Modifier.height(4.dp))
                                Text("S${s.numero}", style = Tipo.Pequeno, color = Cor.Texto3)
                            }
                        }
                    }
                }
            }
            PesoCorporal(vm, estado)
            val rec = Progresso.recordes(regs).take(8)
            if (rec.isNotEmpty()) {
                Secao("Recordes")
                Cartao(Modifier.fillMaxWidth(), padding = PaddingValues(vertical = 6.dp, horizontal = 16.dp)) {
                    rec.forEach { r ->
                        Row(Modifier.padding(vertical = 10.dp), verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Rounded.EmojiEvents, null, tint = Cor.Alerta, modifier = Modifier.size(20.dp))
                            Spacer(Modifier.width(10.dp))
                            Text(vm.catalogo[r.exId]?.nome ?: r.exId, style = Tipo.PequenoForte, color = Cor.Texto, modifier = Modifier.weight(1f), maxLines = 1, overflow = TextOverflow.Ellipsis)
                            Text("${r.reps}×${Progresso.fmtKg(r.kg)} kg", style = Tipo.PequenoForte, color = corM)
                        }
                    }
                }
            }
            Secao("Histórico")
            if (regs.isEmpty()) Vazio("Nenhum treino ainda", "Conclua seu primeiro treino para começar a ver sua evolução aqui.", Icons.Rounded.Insights)
        }
        items(regs.sortedByDescending { it.epochDay }.take(60)) { r ->
            val cor = Cor.tipoSessao(r.tipo, corM)
            Row(Modifier.fillMaxWidth().padding(vertical = 5.dp).clip(RoundedCornerShape(18.dp)).background(Cor.Sup1).padding(14.dp), verticalAlignment = Alignment.CenterVertically) {
                Box(Modifier.size(10.dp).clip(RoundedCornerShape(50)).background(cor))
                Spacer(Modifier.width(12.dp))
                Column(Modifier.weight(1f)) {
                    Text(r.titulo, style = Tipo.CorpoForte, color = Cor.Texto, maxLines = 1, overflow = TextOverflow.Ellipsis)
                    Text("${LocalDate.ofEpochDay(r.epochDay).format(fmt)} · ${r.duracaoSeg / 60} min · esforço ${r.esforco}/10" + if (r.series.isNotEmpty()) " · ${r.series.size} séries" else "",
                        style = Tipo.Pequeno, color = Cor.Texto2, maxLines = 1, overflow = TextOverflow.Ellipsis)
                    if (r.nota.isNotBlank()) Text("“${r.nota}”", style = Tipo.Pequeno, color = Cor.Texto3, maxLines = 2, overflow = TextOverflow.Ellipsis)
                }
                Icon(Icons.Rounded.DeleteOutline, "Apagar registro", tint = Cor.Texto3, modifier = Modifier.size(22.dp).toque("Apagar registro") { apagar = r })
            }
        }
    }
    apagar?.let { r ->
        AlertDialog(onDismissRequest = { apagar = null }, containerColor = Cor.Sup2,
            title = { Text("Apagar este treino?", style = Tipo.Titulo3, color = Cor.Texto) },
            text = { Text(r.titulo, style = Tipo.Corpo, color = Cor.Texto2) },
            confirmButton = { TextButton(onClick = { vm.loja.apagarRegistro(r); apagar = null }) { Text("Apagar", style = Tipo.Botao, color = Cor.Perigo) } },
            dismissButton = { TextButton(onClick = { apagar = null }) { Text("Cancelar", style = Tipo.Botao, color = Cor.Texto2) } })
    }
}

@Composable
private fun PesoCorporal(vm: AppViewModel, estado: Estado) {
    val pesos = estado.pesos
    val atual = pesos.lastOrNull()?.second ?: estado.perfil?.pesoKg?.toDouble() ?: 70.0
    var novo by remember(atual) { mutableDoubleStateOf(atual) }
    Secao("Peso corporal")
    Cartao(Modifier.fillMaxWidth()) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            IconeRedondo(Icons.Rounded.MonitorWeight, Cor.modalidade(estado.plano?.modalidade), 44.dp)
            Spacer(Modifier.width(12.dp))
            Column(Modifier.weight(1f)) {
                Text("${Progresso.fmtKg(atual)} kg", style = Tipo.Titulo2, color = Cor.Texto)
                if (pesos.size >= 2) {
                    val dif = pesos.last().second - pesos.first().second
                    Text("${if (dif > 0) "+" else ""}${Progresso.fmtKg(Math.round(dif * 10) / 10.0)} kg desde o primeiro registro", style = Tipo.Pequeno, color = Cor.Texto2)
                } else Text("Registre seu peso uma vez por semana, no mesmo horário.", style = Tipo.Pequeno, color = Cor.Texto2)
            }
        }
        if (pesos.size >= 2) {
            Spacer(Modifier.height(12.dp))
            val cor = Cor.modalidade(estado.plano?.modalidade)
            Canvas(Modifier.fillMaxWidth().height(90.dp)) {
                val mn = pesos.minOf { it.second } - 0.5
                val mx = pesos.maxOf { it.second } + 0.5
                val path = Path()
                pesos.forEachIndexed { i, (_, kg) ->
                    val x = size.width * i / (pesos.size - 1)
                    val y = (size.height * (1 - (kg - mn) / (mx - mn))).toFloat()
                    if (i == 0) path.moveTo(x, y) else path.lineTo(x, y)
                    drawCircle(cor, 4.dp.toPx(), Offset(x, y))
                }
                drawPath(path, cor, style = Stroke(2.5.dp.toPx(), cap = StrokeCap.Round))
            }
        }
        Spacer(Modifier.height(14.dp))
        Row(verticalAlignment = Alignment.CenterVertically) {
            BotaoIcone(Icons.Rounded.Remove, "Diminuir peso", tamanho = 42.dp) { novo = Math.round((novo - 0.1) * 10) / 10.0 }
            Text("${Progresso.fmtKg(novo)} kg", style = Tipo.Titulo3, color = Cor.Texto, textAlign = TextAlign.Center, modifier = Modifier.weight(1f))
            BotaoIcone(Icons.Rounded.Add, "Aumentar peso", tamanho = 42.dp) { novo = Math.round((novo + 0.1) * 10) / 10.0 }
            Spacer(Modifier.width(10.dp))
            BotaoSecundario("Registrar", cor = Cor.Brasa) { vm.loja.registrarPeso(novo) }
        }
    }
}

@Suppress("unused")
private val semUso = Color.Unspecified
