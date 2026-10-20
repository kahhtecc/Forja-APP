package com.forja.app.ui

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
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.Check
import androidx.compose.material.icons.rounded.EmojiEvents
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.forja.app.AppViewModel
import com.forja.app.core.Estado
import com.forja.app.core.Progresso
import com.forja.app.core.Registro

private val ESCALA = listOf("Muito leve", "Muito leve", "Leve", "Leve", "Moderado", "Moderado", "Difícil", "Difícil", "Muito difícil", "Quase máximo", "Máximo")

@Composable
fun TelaConcluido(vm: AppViewModel, estado: Estado, reg: Registro, novo: Boolean, onFechar: () -> Unit) {
    var esforco by remember { mutableIntStateOf(reg.esforco) }
    var nota by remember { mutableStateOf("") }
    val cor = Cor.tipoSessao(reg.tipo, Cor.modalidade(estado.plano?.modalidade))
    val volume = Progresso.volumeKg(reg)
    val recordesAntes = remember { Progresso.recordes(estado.registros).associateBy { it.exId } }
    val novosRecordes = remember(reg) {
        Progresso.recordes(listOf(reg)).filter { r -> recordesAntes[r.exId]?.let { r.rm1 > it.rm1 + 0.01 } ?: false }
    }

    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).navigationBarsPadding().padding(24.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Spacer(Modifier.height(30.dp))
        Box(Modifier.size(110.dp).clip(CircleShape).background(cor.copy(alpha = 0.15f)), contentAlignment = Alignment.Center) {
            Box(Modifier.size(78.dp).clip(CircleShape).background(cor), contentAlignment = Alignment.Center) {
                Icon(Icons.Rounded.Check, null, tint = Cor.Fundo, modifier = Modifier.size(44.dp))
            }
        }
        Spacer(Modifier.height(20.dp))
        Rotulo("Treino concluído", cor)
        Text(reg.titulo, style = Tipo.Titulo1, color = Cor.Texto, textAlign = TextAlign.Center)
        Spacer(Modifier.height(22.dp))
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            Cartao(Modifier.weight(1f), padding = PaddingValues(14.dp)) { Estatistica("${reg.duracaoSeg / 60}", "minutos") }
            Cartao(Modifier.weight(1f), padding = PaddingValues(14.dp)) { Estatistica("${reg.series.size}", "séries feitas") }
            Cartao(Modifier.weight(1f), padding = PaddingValues(14.dp)) { Estatistica(if (volume > 0) Progresso.fmtKg(volume) else "—", "kg de volume") }
        }
        if (novosRecordes.isNotEmpty()) {
            Spacer(Modifier.height(12.dp))
            Cartao(Modifier.fillMaxWidth(), cor = Cor.Alerta.copy(alpha = 0.08f), borda = Cor.Alerta.copy(alpha = 0.4f)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Rounded.EmojiEvents, null, tint = Cor.Alerta, modifier = Modifier.size(28.dp))
                    Spacer(Modifier.size(12.dp))
                    Column {
                        Text("Novo recorde!", style = Tipo.CorpoForte, color = Cor.Texto)
                        novosRecordes.forEach { r -> Text("${vm.catalogo[r.exId]?.nome}: ${r.reps} × ${Progresso.fmtKg(r.kg)} kg", style = Tipo.Pequeno, color = Cor.Texto2) }
                    }
                }
            }
        }
        Spacer(Modifier.height(26.dp))
        Text("Como foi o esforço?", style = Tipo.Titulo3, color = Cor.Texto)
        Spacer(Modifier.height(4.dp))
        Text("$esforco/10 · ${ESCALA[esforco]}", style = Tipo.CorpoForte, color = cor)
        Spacer(Modifier.height(12.dp))
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            (1..10).forEach { n ->
                val sel = n == esforco
                Box(
                    Modifier.size(30.dp).clip(RoundedCornerShape(9.dp)).background(if (n <= esforco) cor.copy(alpha = 0.25f + n * 0.07f) else Cor.Sup2)
                        .border(if (sel) 2.dp else 0.dp, if (sel) Cor.Texto else Color.Transparent, RoundedCornerShape(9.dp))
                        .toque("Esforço $n") { esforco = n },
                    contentAlignment = Alignment.Center,
                ) { Text("$n", style = Tipo.PequenoForte, color = if (n <= esforco) Cor.Texto else Cor.Texto3) }
            }
        }
        Spacer(Modifier.height(20.dp))
        val forma = RoundedCornerShape(16.dp)
        BasicTextField(
            value = nota, onValueChange = { nota = it.take(200) }, textStyle = Tipo.Corpo.copy(color = Cor.Texto), cursorBrush = SolidColor(Cor.Brasa),
            modifier = Modifier.fillMaxWidth().clip(forma).background(Cor.Sup1).border(1.dp, Cor.Borda, forma).padding(16.dp),
            decorationBox = { c -> if (nota.isEmpty()) Text("Anotação (opcional): como se sentiu, dores, ajustes…", style = Tipo.Corpo, color = Cor.Texto3); c() },
        )
        Spacer(Modifier.height(26.dp))
        BotaoPrimario("Salvar treino", Modifier.fillMaxWidth(), icone = Icons.Rounded.Check, cor = if (cor == Cor.Brasa) null else cor) {
            if (novo) vm.loja.registrar(reg.copy(esforco = esforco, nota = nota.trim()))
            onFechar()
        }
        Spacer(Modifier.height(10.dp))
        Text("Descartar", style = Tipo.PequenoForte, color = Cor.Texto3, modifier = Modifier.toque("Descartar treino", onFechar).padding(10.dp))
    }
}
