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
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.rounded.CheckCircle
import androidx.compose.material.icons.rounded.ChevronRight
import androidx.compose.material.icons.rounded.PlayArrow
import androidx.compose.material.icons.rounded.Repeat
import androidx.compose.material.icons.rounded.Schedule
import androidx.compose.material.icons.rounded.SwapHoriz
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.forja.app.AppViewModel
import com.forja.app.core.Estado
import com.forja.app.core.Progresso
import com.forja.app.core.Questionario
import com.forja.app.core.Roteiro
import com.forja.app.core.Rotinas
import com.forja.app.core.Sessao
import com.forja.app.core.TipoBloco

@Composable
fun TelaPlano(vm: AppViewModel, estado: Estado, nav: Navegador) {
    val plano = estado.plano ?: return
    val atual = vm.loja.semanaAtual()
    var sel by remember { mutableIntStateOf(atual) }
    val semana = plano.semanas[sel - 1]
    val feitas = Progresso.feitas(estado.registros, sel)
    val corM = Cor.modalidade(plano.modalidade)
    val estadoLista = rememberLazyListState()
    LaunchedEffect(Unit) { estadoLista.scrollToItem((atual - 2).coerceAtLeast(0)) }

    LazyColumn(Modifier.fillMaxSize(), contentPadding = PaddingValues(bottom = ESPACO_BARRA)) {
        item {
            Column(Modifier.padding(horizontal = 20.dp, vertical = 10.dp)) {
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Etiqueta(plano.modalidade.curto, corM, iconeModalidade(plano.modalidade))
                    Etiqueta(plano.nivel.nome, Cor.Texto2)
                }
                Spacer(Modifier.height(12.dp))
                Text(plano.nome, style = Tipo.Titulo1, color = Cor.Texto)
                Spacer(Modifier.height(8.dp))
                Text(plano.resumo, style = Tipo.Corpo, color = Cor.Texto2)
                Spacer(Modifier.height(6.dp))
                Text(plano.metaSemanal, style = Tipo.PequenoForte, color = corM)
            }
            Spacer(Modifier.height(14.dp))
            LazyRow(state = estadoLista, contentPadding = PaddingValues(horizontal = 20.dp), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                itemsIndexed(plano.semanas) { i, s ->
                    val n = i + 1
                    val completa = Progresso.feitas(estado.registros, n).size >= s.sessoes.size
                    val ativo = n == sel
                    val forma = RoundedCornerShape(18.dp)
                    Column(
                        Modifier.width(78.dp).clip(forma).background(if (ativo) corM else Cor.Sup1)
                            .border(1.dp, if (n == atual && !ativo) corM else Cor.Borda, forma)
                            .toque("Semana $n") { sel = n }.padding(vertical = 12.dp),
                        horizontalAlignment = Alignment.CenterHorizontally,
                    ) {
                        Text("S%02d".format(n), style = Tipo.Numero.copy(fontSize = 24.sp), color = if (ativo) Cor.Fundo else Cor.Texto)
                        Spacer(Modifier.height(2.dp))
                        if (completa) Icon(Icons.Rounded.CheckCircle, null, tint = if (ativo) Cor.Fundo else Cor.Ok, modifier = Modifier.size(16.dp))
                        else Text(if (n == atual) "atual" else s.fase.take(10), style = Tipo.Rotulo.copy(letterSpacing = 0.sp), color = if (ativo) Cor.Fundo.copy(alpha = 0.8f) else Cor.Texto3, maxLines = 1)
                    }
                }
            }
            Spacer(Modifier.height(16.dp))
            Cartao(Modifier.fillMaxWidth().padding(horizontal = 20.dp), cor = corM.copy(alpha = 0.07f), borda = corM.copy(alpha = 0.3f)) {
                Rotulo("Semana $sel · ${semana.fase}", corM)
                Spacer(Modifier.height(6.dp))
                Text(semana.nota, style = Tipo.Corpo, color = Cor.Texto)
            }
            Spacer(Modifier.height(8.dp))
        }
        itemsIndexed(semana.sessoes) { i, s ->
            CartaoSessao(vm, s, i in feitas, corM, Modifier.padding(horizontal = 20.dp, vertical = 6.dp)) { nav.ir(Rota.SessaoDet(sel, i)) }
        }
        item {
            Column(Modifier.padding(horizontal = 20.dp)) {
                Secao("Como progredir")
                plano.dicas.forEach { d ->
                    Row(Modifier.padding(vertical = 6.dp)) {
                        Box(Modifier.padding(top = 8.dp).size(6.dp).clip(CircleShape).background(corM))
                        Spacer(Modifier.width(12.dp))
                        Text(d, style = Tipo.Corpo, color = Cor.Texto2)
                    }
                }
            }
        }
    }
}

@Composable
private fun CartaoSessao(vm: AppViewModel, s: Sessao, feita: Boolean, corM: Color, modifier: Modifier, onClick: () -> Unit) {
    val cor = Cor.tipoSessao(s.tipo, corM)
    Cartao(modifier.fillMaxWidth(), padding = PaddingValues(14.dp), onClick = onClick, descricao = "${s.titulo}, ${Questionario.DIAS_NOMES[s.diaSemana - 1]}") {
        Row(verticalAlignment = Alignment.CenterVertically) {
            val capa = capaSessao(s)?.let { vm.catalogo[it] }
            Box(Modifier.size(72.dp)) {
                if (capa != null) DemoExercicio(capa, Modifier.fillMaxSize(), cor = cor, animar = false, cantos = 16.dp)
                if (feita) Box(Modifier.fillMaxSize().clip(RoundedCornerShape(16.dp)).background(Cor.Ok.copy(alpha = 0.55f)), contentAlignment = Alignment.Center) {
                    Icon(Icons.Rounded.CheckCircle, null, tint = Color.White, modifier = Modifier.size(30.dp))
                }
            }
            Spacer(Modifier.width(14.dp))
            Column(Modifier.weight(1f)) {
                Rotulo(Questionario.DIAS_NOMES[s.diaSemana - 1] + " · " + s.foco, cor)
                Spacer(Modifier.height(2.dp))
                Text(s.titulo, style = Tipo.Titulo3, color = Cor.Texto, maxLines = 2, overflow = TextOverflow.Ellipsis)
                Spacer(Modifier.height(4.dp))
                val n = s.blocos.filter { it.tipo != TipoBloco.AQUECIMENTO && it.tipo != TipoBloco.DESAQUECIMENTO }.sumOf { it.itens.size }
                Text("${s.minutos} min · $n ${if (n == 1) "exercício" else "exercícios"}", style = Tipo.Pequeno, color = Cor.Texto2)
            }
            Icon(Icons.Rounded.ChevronRight, null, tint = Cor.Texto3)
        }
    }
}

// ------------------------------------------------------------------ detalhe da sessão

@Composable
fun TelaSessao(vm: AppViewModel, estado: Estado, semana: Int, idx: Int, nav: Navegador) {
    val plano = estado.plano ?: return
    val s = plano.semanas.getOrNull(semana - 1)?.sessoes?.getOrNull(idx) ?: return
    val corM = Cor.modalidade(plano.modalidade)
    val cor = Cor.tipoSessao(s.tipo, corM)
    val feito = estado.registros.lastOrNull { it.semana == semana && it.sessaoIdx == idx }
    DetalheSessao(vm, s, cor, cabecalho = "Semana $semana · ${Questionario.DIAS_NOMES[s.diaSemana - 1]}", nav = nav,
        aviso = feito?.let { "Concluído · ${it.duracaoSeg / 60} min · esforço ${it.esforco}/10" },
        troca = { blocoTipo, exId -> if (blocoTipo == TipoBloco.PRINCIPAL || blocoTipo == TipoBloco.CIRCUITO) Troca(idx, exId) else null },
        rotulo = if (feito != null) "Treinar de novo" else "Começar treino",
        onComecar = { nav.ir(Rota.Treino(semana, idx)) },
        extra = {
            val recs = Rotinas.recomendadas(plano.modalidade, estado.perfil).take(2)
            if (recs.isNotEmpty()) {
                Secao("Preparo e volta à calma")
                recs.forEach { r ->
                    Cartao(Modifier.fillMaxWidth().padding(bottom = 10.dp), padding = PaddingValues(14.dp), onClick = { nav.ir(Rota.RotinaDet(r.id)) }, descricao = r.titulo) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            IconeRedondo(iconeModalidade(com.forja.app.core.Modalidade.MOBILIDADE), Cor.tema(r.tema), 40.dp)
                            Spacer(Modifier.width(12.dp))
                            Column(Modifier.weight(1f)) {
                                Text(r.titulo, style = Tipo.CorpoForte, color = Cor.Texto)
                                Text("${Roteiro.minutos(r.sessao, vm.catalogo)} min · ${r.categoria}", style = Tipo.Pequeno, color = Cor.Texto2)
                            }
                            Icon(Icons.Rounded.ChevronRight, null, tint = Cor.Texto3)
                        }
                    }
                }
            }
        })
}

@Composable
fun TelaRotina(vm: AppViewModel, id: String, nav: Navegador) {
    val r = Rotinas.porId(id) ?: return
    DetalheSessao(vm, r.sessao, Cor.tema(r.tema), cabecalho = r.categoria, nav = nav, aviso = null, troca = { _, _ -> null },
        rotulo = "Começar rotina", onComecar = { nav.ir(Rota.TreinoRotina(r.id)) }, subtituloOverride = r.subtitulo)
}

@Composable
fun DetalheSessao(
    vm: AppViewModel, s: Sessao, cor: Color, cabecalho: String, nav: Navegador, aviso: String?,
    troca: (TipoBloco, String) -> Troca?, rotulo: String, onComecar: () -> Unit,
    subtituloOverride: String? = null, extra: @Composable () -> Unit = {},
) {
    val capa = capaSessao(s)?.let { vm.catalogo[it] }
    val img = imagemAsset(capa?.takeIf { it.temImagem }?.let { "img/${it.id}_0.webp" })
    Box(Modifier.fillMaxSize()) {
        LazyColumn(Modifier.fillMaxSize(), contentPadding = PaddingValues(bottom = 120.dp)) {
            item {
                Box(Modifier.fillMaxWidth().height(300.dp)) {
                    if (img != null) Image(img, null, Modifier.fillMaxSize(), contentScale = ContentScale.Crop)
                    Box(Modifier.fillMaxSize().background(Brush.verticalGradient(0f to Color.Black.copy(alpha = 0.35f), 0.4f to Color.Transparent, 1f to Cor.Fundo)))
                    BotaoIcone(Icons.AutoMirrored.Rounded.ArrowBack, "Voltar", Modifier.padding(16.dp), fundo = Cor.Fundo.copy(alpha = 0.6f)) { nav.voltar() }
                    Column(Modifier.align(Alignment.BottomStart).padding(horizontal = 20.dp, vertical = 8.dp)) {
                        Rotulo(cabecalho, cor)
                        Spacer(Modifier.height(4.dp))
                        Text(s.titulo, style = Tipo.Titulo1, color = Cor.Texto)
                        Spacer(Modifier.height(6.dp))
                        Text(subtituloOverride ?: s.foco, style = Tipo.Corpo, color = Cor.Texto2)
                    }
                }
                Row(Modifier.padding(horizontal = 20.dp, vertical = 8.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Etiqueta("${Roteiro.minutos(s, vm.catalogo)} min", cor, Icons.Rounded.Schedule)
                    Etiqueta("${Roteiro.exerciciosDaSessao(s).size} exercícios", cor)
                }
                if (aviso != null) Row(Modifier.padding(horizontal = 20.dp, vertical = 4.dp).clip(RoundedCornerShape(14.dp)).background(Cor.Ok.copy(alpha = 0.1f)).padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Rounded.CheckCircle, null, tint = Cor.Ok, modifier = Modifier.size(18.dp))
                    Spacer(Modifier.width(8.dp))
                    Text(aviso, style = Tipo.PequenoForte, color = Cor.Ok)
                }
            }
            s.blocos.forEach { b ->
                item {
                    Column(Modifier.padding(horizontal = 20.dp)) {
                        Row(Modifier.padding(top = 22.dp, bottom = 4.dp), verticalAlignment = Alignment.CenterVertically) {
                            LinhaBrasa(cor = cor)
                            Spacer(Modifier.width(10.dp))
                            Text(b.nome, style = Tipo.Titulo3, color = Cor.Texto, modifier = Modifier.weight(1f))
                            if (b.voltas > 1) Etiqueta("${b.voltas} voltas", cor, Icons.Rounded.Repeat)
                        }
                        if (b.nota != null) Text(b.nota, style = Tipo.Pequeno, color = Cor.Texto2, modifier = Modifier.padding(bottom = 6.dp))
                    }
                }
                itemsIndexed(b.itens) { _, it ->
                    val ex = vm.catalogo[it.exId] ?: return@itemsIndexed
                    val t = troca(b.tipo, it.exId)
                    Row(
                        Modifier.fillMaxWidth().toque("${ex.nome}, ${Roteiro.prescricao(it, b.tipo == TipoBloco.CIRCUITO, b.voltas)}") { nav.ir(Rota.ExercicioDet(ex.id, t)) }
                            .padding(horizontal = 20.dp, vertical = 8.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        DemoExercicio(ex, Modifier.size(64.dp), cor = cor, animar = false, cantos = 14.dp)
                        Spacer(Modifier.width(14.dp))
                        Column(Modifier.weight(1f)) {
                            Text(ex.nome, style = Tipo.CorpoForte, color = Cor.Texto, maxLines = 2, overflow = TextOverflow.Ellipsis)
                            Spacer(Modifier.height(2.dp))
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Text(Roteiro.prescricao(it, b.tipo == TipoBloco.CIRCUITO, b.voltas), style = Tipo.PequenoForte, color = cor)
                                if (it.intensidade != null) Text("  ·  ${it.intensidade}", style = Tipo.Pequeno, color = Cor.Texto2, maxLines = 1, overflow = TextOverflow.Ellipsis)
                            }
                            if (it.nota != null) Text(it.nota, style = Tipo.Pequeno, color = Cor.Texto3, maxLines = 2, overflow = TextOverflow.Ellipsis)
                        }
                        if (t != null) Icon(Icons.Rounded.SwapHoriz, "Pode trocar", tint = Cor.Texto3, modifier = Modifier.size(20.dp))
                        else Icon(Icons.Rounded.ChevronRight, null, tint = Cor.Texto3)
                    }
                }
            }
            item { Column(Modifier.padding(horizontal = 20.dp)) { extra() } }
        }
        Box(Modifier.align(Alignment.BottomCenter).fillMaxWidth().background(Brush.verticalGradient(listOf(Color.Transparent, Cor.Fundo, Cor.Fundo))).navigationBarsPadding().padding(start = 20.dp, end = 20.dp, top = 24.dp, bottom = 12.dp)) {
            BotaoPrimario(rotulo, Modifier.fillMaxWidth(), icone = Icons.Rounded.PlayArrow, cor = if (cor == Cor.Brasa) null else cor, onClick = onComecar)
        }
    }
}
