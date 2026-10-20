package com.forja.app.ui

import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideInHorizontally
import androidx.compose.animation.slideOutHorizontally
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.automirrored.rounded.ArrowForward
import androidx.compose.material.icons.rounded.Add
import androidx.compose.material.icons.rounded.Check
import androidx.compose.material.icons.rounded.Remove
import androidx.compose.material.icons.rounded.WarningAmber
import androidx.compose.material3.Icon
import androidx.compose.material3.Slider
import androidx.compose.material3.SliderDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardCapitalization
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.forja.app.AppViewModel
import com.forja.app.core.Estado
import com.forja.app.core.Gerador
import com.forja.app.core.Modalidade
import com.forja.app.core.Perfil
import com.forja.app.core.Pergunta
import com.forja.app.core.Questionario
import com.forja.app.core.Respostas
import com.forja.app.core.TipoPergunta
import com.forja.app.core.num
import com.forja.app.core.um
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

@Composable
fun TelaQuestionario(vm: AppViewModel, estado: Estado, podeVoltar: Boolean, onVoltar: () -> Unit, onConcluir: () -> Unit) {
    var resp by remember { mutableStateOf(estado.respostas) }
    var etapa by remember { mutableIntStateOf(if (estado.respostas.isEmpty()) -1 else 0) }
    var gerando by remember { mutableStateOf(false) }

    if (gerando) {
        Gerando(vm, resp, onPronto = {
            vm.loja.salvarRespostas(resp)
            onConcluir()
        })
        return
    }
    if (etapa < 0) {
        BoasVindas(onComecar = { etapa = 0 }, onVoltar = if (podeVoltar) onVoltar else null)
        return
    }
    val visiveis = Questionario.visiveis(resp)
    val idx = etapa.coerceIn(0, visiveis.lastIndex)
    val p = visiveis[idx]

    // Valor padrão para perguntas numéricas obrigatórias (o usuário vê e ajusta).
    LaunchedEffect(p.id) {
        if (p.tipo == TipoPergunta.NUMERO && !p.opcional && resp[p.id].isNullOrEmpty()) resp = resp + (p.id to listOf("${p.padrao ?: p.min}"))
        if (p.tipo == TipoPergunta.DIAS) {
            val n = resp.num("dias") ?: 3
            if (resp[p.id].orEmpty().size != n) resp = resp + (p.id to Questionario.diasSugeridos(n).map { "$it" })
        }
    }
    val escopo = rememberCoroutineScope()
    fun avancar() {
        if (idx >= visiveis.lastIndex) gerando = true else etapa = idx + 1
    }
    fun voltar() {
        if (idx == 0) { if (podeVoltar) onVoltar() else etapa = -1 } else etapa = idx - 1
    }

    Column(Modifier.fillMaxSize().imePadding()) {
        // cabeçalho com progresso
        Row(Modifier.fillMaxWidth().padding(horizontal = 20.dp, vertical = 12.dp), verticalAlignment = Alignment.CenterVertically) {
            BotaoIcone(Icons.AutoMirrored.Rounded.ArrowBack, "Voltar", onClick = { voltar() })
            Spacer(Modifier.width(16.dp))
            Column(Modifier.weight(1f)) {
                Row {
                    Rotulo(p.secao, Cor.Brasa)
                    Spacer(Modifier.weight(1f))
                    Rotulo("${idx + 1} / ${visiveis.size}")
                }
                Spacer(Modifier.height(8.dp))
                val prog by animateFloatAsState((idx + 1f) / visiveis.size, tween(400), label = "prog")
                BarraProgresso(prog, Modifier.fillMaxWidth(), altura = 5.dp)
            }
        }
        AnimatedContent(p, transitionSpec = {
            (slideInHorizontally(tween(260)) { it / 6 } + fadeIn(tween(260))) togetherWith (slideOutHorizontally(tween(200)) { -it / 6 } + fadeOut(tween(160)))
        }, modifier = Modifier.weight(1f), label = "pergunta") { perg ->
            Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal = 22.dp)) {
                Spacer(Modifier.height(18.dp))
                Text(perg.titulo, style = Tipo.Titulo1, color = Cor.Texto)
                if (perg.subtitulo != null) {
                    Spacer(Modifier.height(10.dp))
                    Text(perg.subtitulo, style = Tipo.Corpo, color = Cor.Texto2)
                }
                Spacer(Modifier.height(24.dp))
                CorpoPergunta(perg, resp, onMudar = { resp = it }, onEscolhaUnica = {
                    escopo.launch { delay(260); avancar() }
                })
                Spacer(Modifier.height(24.dp))
            }
        }
        Column(Modifier.navigationBarsPadding().padding(horizontal = 22.dp, vertical = 12.dp)) {
            val respondida = p.respondida(resp)
            val pular = p.opcional && resp[p.id].isNullOrEmpty()
            BotaoPrimario(
                if (idx == visiveis.lastIndex) "Montar minha rotina" else if (pular) "Pular" else "Continuar",
                Modifier.fillMaxWidth(), icone = Icons.AutoMirrored.Rounded.ArrowForward, ativo = respondida,
            ) { avancar() }
        }
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun CorpoPergunta(p: Pergunta, resp: Respostas, onMudar: (Respostas) -> Unit, onEscolhaUnica: () -> Unit) {
    val atual = resp[p.id].orEmpty()
    when (p.tipo) {
        TipoPergunta.UNICA -> {
            if (p.id == "minutos") {
                FlowRow(horizontalArrangement = Arrangement.spacedBy(10.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    p.opcoes.forEach { o ->
                        Pilula(o.titulo, o.valor in atual, Modifier.width(100.dp)) { onMudar(resp + (p.id to listOf(o.valor))); onEscolhaUnica() }
                    }
                }
            } else Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                p.opcoes.forEach { o ->
                    val m = if (p.id == "modalidade") Modalidade.de(o.valor) else null
                    CartaoOpcao(o.titulo, o.descricao, o.valor in atual, multipla = false, cor = m?.let { Cor.modalidade(it) } ?: Cor.Brasa, icone = m?.let { iconeModalidade(it) }) {
                        onMudar(resp + (p.id to listOf(o.valor))); onEscolhaUnica()
                    }
                }
            }
        }
        TipoPergunta.MULTIPLA -> Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
            if (p.id == "parq") {
                Row(Modifier.fillMaxWidth().clip(RoundedCornerShape(16.dp)).background(Cor.Alerta.copy(alpha = 0.10f)).padding(14.dp)) {
                    Icon(Icons.Rounded.WarningAmber, null, tint = Cor.Alerta, modifier = Modifier.size(20.dp))
                    Spacer(Modifier.width(10.dp))
                    Text("Qualquer “sim” não impede o treino, mas pede conversa com um médico antes de aumentar a intensidade.", style = Tipo.Pequeno, color = Cor.Texto2)
                }
            }
            p.opcoes.forEach { o ->
                val marcado = o.valor in atual
                CartaoOpcao(o.titulo, o.descricao, marcado, multipla = true) {
                    val novo = when {
                        marcado -> atual - o.valor
                        o.valor == p.exclusiva -> listOf(o.valor)
                        else -> atual.filter { it != p.exclusiva } + o.valor
                    }
                    onMudar(resp + (p.id to novo))
                }
            }
        }
        TipoPergunta.NUMERO -> SeletorNumero(p, resp.num(p.id), onMudar = { v ->
            var r = resp + (p.id to listOfNotNull(v?.toString()))
            if (p.id == "dias" && v != null) r = r + ("dias_semana" to Questionario.diasSugeridos(v).map { "$it" })
            onMudar(r)
        })
        TipoPergunta.DIAS -> {
            val n = resp.num("dias") ?: 3
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Questionario.DIAS_NOMES.forEachIndexed { i, nome ->
                    val v = "${i + 1}"
                    val sel = v in atual
                    Box(
                        Modifier.size(44.dp).clip(CircleShape).background(if (sel) Cor.Brasa else Cor.Sup2).border(1.dp, if (sel) Cor.Brasa else Cor.Borda, CircleShape)
                            .toque("$nome${if (sel) ", selecionado" else ""}") {
                                val novo = if (sel) atual - v else if (atual.size < n) atual + v else atual.drop(1) + v
                                onMudar(resp + (p.id to novo.sortedBy { it.toInt() }))
                            },
                        contentAlignment = Alignment.Center,
                    ) { Text(nome.take(3), style = Tipo.PequenoForte, color = if (sel) Color.White else Cor.Texto2) }
                }
            }
            Spacer(Modifier.height(16.dp))
            Text("${atual.size} de $n dias escolhidos", style = Tipo.CorpoForte, color = if (atual.size == n) Cor.Ok else Cor.Texto2)
            Spacer(Modifier.height(8.dp))
            Text("Dica: deixe pelo menos um dia de descanso entre treinos pesados do mesmo grupo.", style = Tipo.Pequeno, color = Cor.Texto3)
        }
        TipoPergunta.TEXTO -> {
            val forma = RoundedCornerShape(18.dp)
            BasicTextField(
                value = resp.um(p.id).orEmpty(), onValueChange = { onMudar(resp + (p.id to listOf(it.take(24)))) },
                textStyle = Tipo.Titulo2.copy(color = Cor.Texto), cursorBrush = SolidColor(Cor.Brasa), singleLine = true,
                keyboardOptions = KeyboardOptions(capitalization = KeyboardCapitalization.Words, imeAction = ImeAction.Done),
                modifier = Modifier.fillMaxWidth().clip(forma).background(Cor.Sup1).border(1.dp, Cor.Borda, forma).padding(20.dp),
                decorationBox = { campo ->
                    if (resp.um(p.id).isNullOrEmpty()) Text("Seu nome", style = Tipo.Titulo2, color = Cor.Texto3)
                    campo()
                },
            )
        }
    }
}

@Composable
private fun Pilula(texto: String, sel: Boolean, modifier: Modifier = Modifier, onClick: () -> Unit) {
    val forma = RoundedCornerShape(16.dp)
    Box(
        modifier.height(56.dp).clip(forma).background(if (sel) Cor.Brasa.copy(alpha = 0.16f) else Cor.Sup1)
            .border(1.5.dp, if (sel) Cor.Brasa else Cor.Borda, forma).toque(texto, onClick),
        contentAlignment = Alignment.Center,
    ) { Text(texto, style = Tipo.Titulo3, color = if (sel) Cor.Texto else Cor.Texto2) }
}

@Composable
fun CartaoOpcao(
    titulo: String, descricao: String?, selecionado: Boolean, multipla: Boolean,
    cor: Color = Cor.Brasa, icone: androidx.compose.ui.graphics.vector.ImageVector? = null, onClick: () -> Unit,
) {
    val forma = RoundedCornerShape(18.dp)
    Row(
        Modifier.fillMaxWidth().clip(forma).background(if (selecionado) cor.copy(alpha = 0.12f) else Cor.Sup1)
            .border(1.5.dp, if (selecionado) cor else Cor.Borda, forma)
            .toque(titulo + if (selecionado) ", selecionado" else "", onClick).padding(horizontal = 16.dp, vertical = 14.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        if (icone != null) {
            IconeRedondo(icone, cor, 42.dp)
            Spacer(Modifier.width(14.dp))
        }
        Column(Modifier.weight(1f)) {
            Text(titulo, style = Tipo.CorpoForte, color = Cor.Texto)
            if (descricao != null) Text(descricao, style = Tipo.Pequeno, color = Cor.Texto2)
        }
        Spacer(Modifier.width(10.dp))
        val f = if (multipla) RoundedCornerShape(7.dp) else CircleShape
        Box(
            Modifier.size(24.dp).clip(f).background(if (selecionado) cor else Color.Transparent).border(1.5.dp, if (selecionado) cor else Cor.Texto3, f),
            contentAlignment = Alignment.Center,
        ) { if (selecionado) Icon(Icons.Rounded.Check, null, tint = Cor.Fundo, modifier = Modifier.size(16.dp)) }
    }
}

@Composable
private fun SeletorNumero(p: Pergunta, valor: Int?, onMudar: (Int?) -> Unit) {
    val v = valor ?: p.padrao ?: p.min
    Column(Modifier.fillMaxWidth(), horizontalAlignment = Alignment.CenterHorizontally) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            BotaoIcone(Icons.Rounded.Remove, "Diminuir", tamanho = 58.dp) { onMudar((v - p.passo).coerceAtLeast(p.min)) }
            Spacer(Modifier.width(22.dp))
            Column(horizontalAlignment = Alignment.CenterHorizontally, modifier = Modifier.width(150.dp)) {
                Text(if (valor == null && p.opcional) "—" else "$v", style = Tipo.Gigante.copy(fontSize = 88.sp, lineHeight = 84.sp), color = if (valor == null && p.opcional) Cor.Texto3 else Cor.Texto, textAlign = TextAlign.Center)
                Rotulo(p.unidade, Cor.Brasa)
            }
            Spacer(Modifier.width(22.dp))
            BotaoIcone(Icons.Rounded.Add, "Aumentar", tamanho = 58.dp) { onMudar((v + p.passo).coerceAtMost(p.max)) }
        }
        Spacer(Modifier.height(24.dp))
        Slider(
            value = v.toFloat(), onValueChange = { onMudar((Math.round(it / p.passo) * p.passo).coerceIn(p.min, p.max)) },
            valueRange = p.min.toFloat()..p.max.toFloat(),
            colors = SliderDefaults.colors(thumbColor = Cor.Brasa, activeTrackColor = Cor.Brasa, inactiveTrackColor = Cor.Sup3),
        )
        if (p.id == "dias") {
            Spacer(Modifier.height(12.dp))
            Text(
                when (v) { 2 -> "Ótimo para começar e manter."; 3 -> "O ponto ideal para a maioria."; 4 -> "Permite dividir em superiores e inferiores."; 5 -> "Volume alto — durma bem."; else -> "Para quem já tem rotina consolidada." },
                style = Tipo.Corpo, color = Cor.Texto2, textAlign = TextAlign.Center,
            )
        }
        if (p.opcional && valor != null) {
            Spacer(Modifier.height(12.dp))
            Text("Limpar", style = Tipo.PequenoForte, color = Cor.Texto2, modifier = Modifier.toque("Limpar valor") { onMudar(null) }.padding(8.dp))
        }
    }
}

@Composable
private fun BoasVindas(onComecar: () -> Unit, onVoltar: (() -> Unit)?) {
    Box(Modifier.fillMaxSize()) {
        // mosaico de fotos
        Column(Modifier.fillMaxWidth().padding(top = 8.dp)) {
            Row(Modifier.fillMaxWidth().padding(horizontal = 12.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                FotoMosaico("agachamento-barra", Modifier.weight(1.3f).aspectRatio(0.72f))
                Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    FotoMosaico("swing", Modifier.fillMaxWidth().aspectRatio(0.95f))
                    FotoMosaico("corrida-leve", Modifier.fillMaxWidth().aspectRatio(1.05f))
                }
            }
        }
        Box(Modifier.fillMaxSize().background(Brush.verticalGradient(0.25f to Color.Transparent, 0.58f to Cor.Fundo)))
        Column(Modifier.align(Alignment.BottomStart).navigationBarsPadding().padding(24.dp)) {
            LinhaBrasa(Modifier.width(56.dp))
            Spacer(Modifier.height(14.dp))
            Text("FORJA", style = Tipo.Gigante.copy(fontSize = 84.sp, lineHeight = 80.sp, letterSpacing = 2.sp), color = Cor.Texto)
            Text("Treino sob medida.", style = Tipo.Titulo2, color = Cor.Brasa)
            Spacer(Modifier.height(14.dp))
            Text("Responda algumas perguntas e receba uma rotina completa — musculação, casa, corrida, bike, lutas, atletas, mobilidade e mais — com vídeo de cada exercício.",
                style = Tipo.Corpo, color = Cor.Texto2)
            Spacer(Modifier.height(24.dp))
            BotaoPrimario("Montar minha rotina", Modifier.fillMaxWidth(), icone = Icons.AutoMirrored.Rounded.ArrowForward, onClick = onComecar)
            if (onVoltar != null) {
                Spacer(Modifier.height(10.dp))
                BotaoSecundario("Cancelar", Modifier.fillMaxWidth(), onClick = onVoltar)
            }
            Spacer(Modifier.height(8.dp))
            Text("Leva cerca de 2 minutos · baseado em diretrizes do ACSM, OMS e NSCA", style = Tipo.Pequeno, color = Cor.Texto3, modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Center)
        }
    }
}

@Composable
private fun FotoMosaico(id: String, modifier: Modifier) {
    val img = imagemAsset("img/${id}_1.webp")
    Box(modifier.clip(RoundedCornerShape(22.dp)).background(Cor.Sup2)) {
        if (img != null) Image(img, null, Modifier.fillMaxSize(), contentScale = ContentScale.Crop)
    }
}

@Composable
private fun Gerando(vm: AppViewModel, resp: Respostas, onPronto: () -> Unit) {
    val passos = listOf("Analisando seu perfil", "Aplicando a triagem de segurança", "Escolhendo os exercícios", "Ajustando volume e intensidade", "Organizando as semanas")
    var feito by remember { mutableIntStateOf(0) }
    val plano = remember(resp) { runCatching { Gerador(vm.catalogo).gerar(Perfil.de(resp)) }.getOrNull() }
    LaunchedEffect(Unit) {
        for (i in passos.indices) { delay(430); feito = i + 1 }
        delay(250)
    }
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).navigationBarsPadding().padding(24.dp)) {
        Spacer(Modifier.height(30.dp))
        val cor = Cor.modalidade(plano?.modalidade)
        Anel(feito / passos.size.toFloat(), Modifier.size(96.dp), cor = cor) {
            Icon(iconeModalidade(plano?.modalidade), null, tint = cor, modifier = Modifier.size(38.dp))
        }
        Spacer(Modifier.height(26.dp))
        Text(if (feito < passos.size) "Forjando sua rotina…" else "Sua rotina está pronta", style = Tipo.Titulo1, color = Cor.Texto)
        Spacer(Modifier.height(18.dp))
        passos.forEachIndexed { i, s ->
            Row(Modifier.padding(vertical = 6.dp), verticalAlignment = Alignment.CenterVertically) {
                Box(Modifier.size(22.dp).clip(CircleShape).background(if (i < feito) Cor.Ok else Cor.Sup3), contentAlignment = Alignment.Center) {
                    if (i < feito) Icon(Icons.Rounded.Check, null, tint = Cor.Fundo, modifier = Modifier.size(15.dp))
                }
                Spacer(Modifier.width(12.dp))
                Text(s, style = Tipo.Corpo, color = if (i < feito) Cor.Texto else Cor.Texto3)
            }
        }
        if (feito >= passos.size && plano != null) {
            Spacer(Modifier.height(22.dp))
            Cartao(Modifier.fillMaxWidth()) {
                Etiqueta(plano.modalidade.nome, cor, iconeModalidade(plano.modalidade))
                Spacer(Modifier.height(12.dp))
                Text(plano.nome, style = Tipo.Titulo2, color = Cor.Texto)
                Spacer(Modifier.height(6.dp))
                Text(plano.resumo, style = Tipo.Pequeno, color = Cor.Texto2)
                Spacer(Modifier.height(12.dp))
                Text(plano.metaSemanal, style = Tipo.PequenoForte, color = cor)
            }
            plano.alertas.forEach {
                Spacer(Modifier.height(10.dp))
                Row(Modifier.fillMaxWidth().clip(RoundedCornerShape(16.dp)).background(Cor.Alerta.copy(alpha = 0.10f)).padding(14.dp)) {
                    Icon(Icons.Rounded.WarningAmber, null, tint = Cor.Alerta, modifier = Modifier.size(20.dp))
                    Spacer(Modifier.width(10.dp))
                    Text(it, style = Tipo.Pequeno, color = Cor.Texto)
                }
            }
            Spacer(Modifier.height(24.dp))
            BotaoPrimario("Ver meu plano", Modifier.fillMaxWidth(), icone = Icons.AutoMirrored.Rounded.ArrowForward, onClick = onPronto)
        }
    }
}
