package com.forja.app.ui

import android.annotation.SuppressLint
import android.content.Intent
import android.net.Uri
import android.webkit.WebChromeClient
import android.webkit.WebView
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
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.GridItemSpan
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.automirrored.rounded.OpenInNew
import androidx.compose.material.icons.rounded.Check
import androidx.compose.material.icons.rounded.Close
import androidx.compose.material.icons.rounded.EmojiEvents
import androidx.compose.material.icons.rounded.PlayArrow
import androidx.compose.material.icons.rounded.Restore
import androidx.compose.material.icons.rounded.Search
import androidx.compose.material.icons.rounded.SwapHoriz
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import com.forja.app.AppViewModel
import com.forja.app.core.Estado
import com.forja.app.core.Exercicio
import com.forja.app.core.Progresso

private val EQUIP_NOMES = mapOf(
    "corpo" to "Peso do corpo", "elastico" to "Elástico", "halter" to "Halteres", "barra" to "Barra", "maquina" to "Máquina", "polia" to "Polia",
    "kettlebell" to "Kettlebell", "banco" to "Banco", "barra_fixa" to "Barra fixa", "bola" to "Medicine ball", "corda" to "Corda", "rolo" to "Rolo",
    "saco" to "Saco de pancada", "bike" to "Bike", "esteira" to "Esteira", "rua" to "Rua", "pista" to "Pista", "outro" to "Outros",
)
private val TIPO_NOMES = mapOf("forca" to "Força", "cardio" to "Cardio", "pliometria" to "Pliometria", "potencia" to "Potência", "mobilidade" to "Mobilidade", "tecnica" to "Técnica")

@Composable
fun TelaBiblioteca(vm: AppViewModel, estado: Estado, nav: Navegador) {
    var busca by rememberSaveable { mutableStateOf("") }
    var grupo by rememberSaveable { mutableStateOf("Todos") }
    var casa by rememberSaveable { mutableStateOf(false) }
    val grupos = listOf("Todos") + vm.catalogo.grupos()
    val termo = busca.trim().lowercase()
    val lista = vm.catalogo.exercicios.filter { e ->
        (grupo == "Todos" || e.grupo == grupo) &&
            (!casa || e.equip.any { it in setOf("corpo", "elastico") }) &&
            (termo.isEmpty() || e.nome.lowercase().contains(termo) || e.grupo.lowercase().contains(termo) || e.equip.any { (EQUIP_NOMES[it] ?: it).lowercase().contains(termo) })
    }
    LazyVerticalGrid(GridCells.Fixed(2), Modifier.fillMaxSize(), contentPadding = PaddingValues(start = 16.dp, end = 16.dp, bottom = ESPACO_BARRA),
        horizontalArrangement = Arrangement.spacedBy(12.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        item(span = { GridItemSpan(2) }) {
            Column(Modifier.padding(horizontal = 4.dp, vertical = 10.dp)) {
                Rotulo("${vm.catalogo.exercicios.size} exercícios com demonstração e vídeo", Cor.Brasa)
                Text("Biblioteca", style = Tipo.Titulo1, color = Cor.Texto)
                Spacer(Modifier.height(14.dp))
                val forma = RoundedCornerShape(18.dp)
                Row(Modifier.fillMaxWidth().clip(forma).background(Cor.Sup1).border(1.dp, Cor.Borda, forma).padding(horizontal = 16.dp, vertical = 14.dp), verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Rounded.Search, null, tint = Cor.Texto3, modifier = Modifier.size(20.dp))
                    Spacer(Modifier.width(10.dp))
                    BasicTextField(busca, { busca = it }, Modifier.weight(1f), textStyle = Tipo.Corpo.copy(color = Cor.Texto), singleLine = true, cursorBrush = SolidColor(Cor.Brasa),
                        decorationBox = { c -> if (busca.isEmpty()) Text("Buscar exercício, músculo ou equipamento", style = Tipo.Corpo, color = Cor.Texto3, maxLines = 1); c() })
                    if (busca.isNotEmpty()) Icon(Icons.Rounded.Close, "Limpar busca", tint = Cor.Texto3, modifier = Modifier.size(20.dp).toque("Limpar busca") { busca = "" })
                }
                Spacer(Modifier.height(12.dp))
                LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    item { Chip("Sem equipamento", casa) { casa = !casa } }
                    items(grupos) { g -> Chip(g, g == grupo) { grupo = g } }
                }
            }
        }
        if (lista.isEmpty()) item(span = { GridItemSpan(2) }) { Vazio("Nada encontrado", "Tente outro termo ou limpe os filtros.", Icons.Rounded.Search) }
        items(lista, key = { it.id }) { e ->
            val forma = RoundedCornerShape(20.dp)
            Column(Modifier.clip(forma).background(Cor.Sup1).border(1.dp, Cor.Borda, forma).toque(e.nome) { nav.ir(Rota.ExercicioDet(e.id)) }) {
                DemoExercicio(e, Modifier.fillMaxWidth().aspectRatio(1.25f), animar = false, cantos = 0.dp)
                Column(Modifier.padding(12.dp)) {
                    Text(e.nome, style = Tipo.PequenoForte, color = Cor.Texto, maxLines = 2, overflow = TextOverflow.Ellipsis, minLines = 2)
                    Spacer(Modifier.height(4.dp))
                    Text("${e.grupo} · ${EQUIP_NOMES[e.equip.first()] ?: e.equip.first()}", style = Tipo.Pequeno, color = Cor.Texto3, maxLines = 1, overflow = TextOverflow.Ellipsis)
                }
            }
        }
    }
}

@Composable
fun TelaExercicio(vm: AppViewModel, estado: Estado, id: String, troca: Troca?, nav: Navegador) {
    val e = vm.catalogo[id] ?: return
    val perfil = estado.perfil
    val origem = troca?.let { t -> estado.trocas.entries.firstOrNull { it.key.startsWith("${t.sessaoIdx}|") && it.value == id }?.key?.substringAfter("|") } ?: id
    val trocado = troca != null && origem != id
    val recorde = Progresso.recordes(estado.registros).firstOrNull { it.exId == id }
    val ultimas = Progresso.ultimas(estado.registros, id)
    val cor = Cor.Brasa

    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState())) {
        Box {
            DemoExercicio(e, Modifier.fillMaxWidth().aspectRatio(1.1f), cor = cor, cantos = 0.dp)
            BotaoIcone(Icons.AutoMirrored.Rounded.ArrowBack, "Voltar", Modifier.padding(16.dp), fundo = Cor.Fundo.copy(alpha = 0.6f)) { nav.voltar() }
        }
        Column(Modifier.padding(horizontal = 20.dp)) {
            Spacer(Modifier.height(16.dp))
            Rotulo(e.grupo, cor)
            Text(e.nome, style = Tipo.Titulo1, color = Cor.Texto)
            Spacer(Modifier.height(12.dp))
            LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                items(e.equip) { q -> Etiqueta(EQUIP_NOMES[q] ?: q, Cor.Texto2) }
                item { Etiqueta(TIPO_NOMES[e.tipo] ?: e.tipo, cor) }
                item { Etiqueta(listOf("", "Básico", "Intermediário", "Avançado")[e.nivel.coerceIn(1, 3)], Cor.Texto2) }
            }
            Spacer(Modifier.height(18.dp))
            BotaoPrimario(if (e.video != null) "Assistir vídeo demonstrativo" else "Buscar vídeo no YouTube", Modifier.fillMaxWidth(), icone = Icons.Rounded.PlayArrow) { nav.ir(Rota.Video(e.id)) }
            if (e.video != null) {
                Spacer(Modifier.height(6.dp))
                Text("${e.video.titulo}${if (e.video.canal.isNotBlank() && e.video.canal != "não identificado") " · ${e.video.canal}" else ""}${if (e.video.idioma == "en") " · em inglês" else ""}",
                    style = Tipo.Pequeno, color = Cor.Texto3, maxLines = 2, overflow = TextOverflow.Ellipsis)
            }
            Secao("Como executar")
            e.dicas.forEachIndexed { k, d ->
                Row(Modifier.padding(vertical = 6.dp)) {
                    Box(Modifier.size(28.dp).clip(RoundedCornerShape(9.dp)).background(cor.copy(alpha = 0.15f)), contentAlignment = Alignment.Center) {
                        Text("${k + 1}", style = Tipo.PequenoForte, color = cor)
                    }
                    Spacer(Modifier.width(12.dp))
                    Text(d, style = Tipo.Corpo, color = Cor.Texto, modifier = Modifier.padding(top = 3.dp))
                }
            }
            if (recorde != null || ultimas.isNotEmpty()) {
                Secao("Seu histórico")
                Cartao(Modifier.fillMaxWidth()) {
                    if (recorde != null) Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Rounded.EmojiEvents, null, tint = Cor.Alerta, modifier = Modifier.size(22.dp))
                        Spacer(Modifier.width(10.dp))
                        Text("Recorde: ${recorde.reps} × ${Progresso.fmtKg(recorde.kg)} kg · 1RM estimado ${Progresso.fmtKg(Math.round(recorde.rm1 * 2) / 2.0)} kg", style = Tipo.PequenoForte, color = Cor.Texto)
                    }
                    if (ultimas.isNotEmpty()) {
                        Spacer(Modifier.height(8.dp))
                        Text("Última vez: " + ultimas.joinToString(" · ") { if (it.kg > 0) "${it.reps}×${Progresso.fmtKg(it.kg)}" else if (it.seg > 0) "${it.seg}s" else "${it.reps}" }, style = Tipo.Pequeno, color = Cor.Texto2)
                    }
                }
            }
            if (troca != null && perfil != null) {
                val atual = vm.catalogo[origem] ?: e
                val alts = vm.catalogo.alternativas(atual, perfil.equip, perfil.evitar).filter { it.id != id }
                Secao("Trocar neste treino")
                Text("Não tem o aparelho ou não se adaptou? Escolha uma alternativa com o mesmo padrão de movimento. A troca vale para este treino em todas as semanas.", style = Tipo.Pequeno, color = Cor.Texto2)
                Spacer(Modifier.height(10.dp))
                if (trocado) {
                    BotaoSecundario("Voltar ao original: ${atual.nome}", Modifier.fillMaxWidth(), icone = Icons.Rounded.Restore) {
                        vm.loja.trocar(troca.sessaoIdx, origem, null); nav.voltar()
                    }
                    Spacer(Modifier.height(10.dp))
                }
                alts.take(12).forEach { a -> LinhaAlternativa(a) { vm.loja.trocar(troca.sessaoIdx, origem, a.id); nav.voltar() } }
                if (alts.isEmpty()) Text("Sem alternativas com o seu equipamento.", style = Tipo.Pequeno, color = Cor.Texto3)
            }
            Spacer(Modifier.height(40.dp))
        }
    }
}

@Composable
private fun LinhaAlternativa(a: Exercicio, onClick: () -> Unit) {
    Row(Modifier.fillMaxWidth().padding(vertical = 5.dp).clip(RoundedCornerShape(18.dp)).background(Cor.Sup1).border(1.dp, Cor.Borda, RoundedCornerShape(18.dp))
        .toque("Trocar por ${a.nome}", onClick).padding(10.dp), verticalAlignment = Alignment.CenterVertically) {
        DemoExercicio(a, Modifier.size(56.dp), animar = false, cantos = 12.dp)
        Spacer(Modifier.width(12.dp))
        Column(Modifier.weight(1f)) {
            Text(a.nome, style = Tipo.CorpoForte, color = Cor.Texto, maxLines = 2, overflow = TextOverflow.Ellipsis)
            Text(a.equip.joinToString(" · ") { EQUIP_NOMES[it] ?: it }, style = Tipo.Pequeno, color = Cor.Texto3, maxLines = 1)
        }
        Icon(Icons.Rounded.SwapHoriz, null, tint = Cor.Brasa)
    }
}

// ------------------------------------------------------------------ vídeo

@SuppressLint("SetJavaScriptEnabled")
@Composable
fun TelaVideo(vm: AppViewModel, exId: String, onVoltar: () -> Unit) {
    val e = vm.catalogo[exId] ?: return
    val ctx = LocalContext.current
    val v = e.video
    fun abrir(url: String) = runCatching { ctx.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url)).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)) }
    val busca = "https://www.youtube.com/results?search_query=" + Uri.encode(e.busca)
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).navigationBarsPadding()) {
        Topo(e.nome, "Vídeo demonstrativo", onVoltar = onVoltar)
        if (v != null) {
            val html = """
                <!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
                <style>html,body{margin:0;background:#0E0D0C;height:100%}.w{position:relative;width:100%;padding-top:56.25%}
                iframe{position:absolute;inset:0;width:100%;height:100%;border:0}</style></head><body>
                <div class="w"><iframe src="https://www.youtube-nocookie.com/embed/${v.id}?playsinline=1&rel=0&modestbranding=1"
                allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture; fullscreen" allowfullscreen
                referrerpolicy="strict-origin-when-cross-origin"></iframe></div></body></html>
            """.trimIndent()
            AndroidView(
                factory = { c ->
                    WebView(c).apply {
                        settings.javaScriptEnabled = true
                        settings.domStorageEnabled = true
                        settings.mediaPlaybackRequiresUserGesture = false
                        webChromeClient = WebChromeClient()
                        setBackgroundColor(android.graphics.Color.parseColor("#0E0D0C"))
                        loadDataWithBaseURL("https://forja.app/", html, "text/html", "utf-8", null)
                    }
                },
                onRelease = { it.destroy() },
                modifier = Modifier.fillMaxWidth().aspectRatio(16f / 9f),
            )
            Column(Modifier.padding(20.dp)) {
                Text(v.titulo, style = Tipo.CorpoForte, color = Cor.Texto)
                if (v.canal.isNotBlank() && v.canal != "não identificado") Text(v.canal, style = Tipo.Pequeno, color = Cor.Texto2)
                if (v.idioma == "en") Text("Vídeo em inglês — ative as legendas automáticas em português.", style = Tipo.Pequeno, color = Cor.Texto3)
                Spacer(Modifier.height(18.dp))
                BotaoSecundario("Abrir no YouTube", Modifier.fillMaxWidth(), icone = Icons.AutoMirrored.Rounded.OpenInNew) { abrir("https://www.youtube.com/watch?v=${v.id}") }
                Spacer(Modifier.height(10.dp))
                BotaoSecundario("Ver outros vídeos", Modifier.fillMaxWidth(), icone = Icons.Rounded.Search) { abrir(busca) }
                Spacer(Modifier.height(18.dp))
                Text("O vídeo não carregou? Alguns canais bloqueiam a reprodução fora do YouTube — use “Abrir no YouTube”.", style = Tipo.Pequeno, color = Cor.Texto3)
            }
        } else {
            Column(Modifier.padding(20.dp)) {
                DemoExercicio(e, Modifier.fillMaxWidth().aspectRatio(1.4f))
                Spacer(Modifier.height(18.dp))
                BotaoPrimario("Buscar no YouTube", Modifier.fillMaxWidth(), icone = Icons.Rounded.Search) { abrir(busca) }
            }
        }
        Spacer(Modifier.height(12.dp))
        Column(Modifier.padding(horizontal = 20.dp)) {
            Rotulo("Pontos-chave")
            e.dicas.forEach { d -> Row(Modifier.padding(vertical = 4.dp)) { Icon(Icons.Rounded.Check, null, tint = Cor.Brasa, modifier = Modifier.size(18.dp)); Spacer(Modifier.width(8.dp)); Text(d, style = Tipo.Pequeno, color = Cor.Texto2) } }
        }
    }
}
