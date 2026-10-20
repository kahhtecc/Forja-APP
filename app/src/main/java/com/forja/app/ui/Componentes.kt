package com.forja.app.ui

import android.content.Context
import android.graphics.BitmapFactory
import android.view.HapticFeedbackConstants
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxScope
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.RowScope
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.ArrowBack
import androidx.compose.material.icons.automirrored.rounded.DirectionsBike
import androidx.compose.material.icons.automirrored.rounded.DirectionsRun
import androidx.compose.material.icons.rounded.Bolt
import androidx.compose.material.icons.rounded.Elderly
import androidx.compose.material.icons.rounded.EmojiEvents
import androidx.compose.material.icons.rounded.FitnessCenter
import androidx.compose.material.icons.rounded.Home
import androidx.compose.material.icons.rounded.LocalFireDepartment
import androidx.compose.material.icons.rounded.SelfImprovement
import androidx.compose.material.icons.rounded.SportsMma
import androidx.compose.material.icons.rounded.Spa
import androidx.compose.material.icons.rounded.SyncAlt
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.produceState
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.luminance
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import com.forja.app.core.Exercicio
import com.forja.app.core.Modalidade
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

// ------------------------------------------------------------------ imagens

object Imagens {
    private val cache = android.util.LruCache<String, ImageBitmap>(80)

    fun carregar(ctx: Context, caminho: String): ImageBitmap? {
        cache.get(caminho)?.let { return it }
        return runCatching {
            ctx.assets.open(caminho).use { BitmapFactory.decodeStream(it) }?.asImageBitmap()
        }.getOrNull()?.also { cache.put(caminho, it) }
    }
}

@Composable
fun imagemAsset(caminho: String?): ImageBitmap? {
    val ctx = LocalContext.current
    val img by produceState<ImageBitmap?>(null, caminho) {
        value = caminho?.let { withContext(Dispatchers.IO) { Imagens.carregar(ctx, it) } }
    }
    return img
}

/** Demonstração animada: alterna as fotos de início e fim do movimento em loop. */
@Composable
fun DemoExercicio(ex: Exercicio, modifier: Modifier = Modifier, cor: Color = Cor.Brasa, animar: Boolean = true, cantos: Dp = 20.dp) {
    val a = imagemAsset(if (ex.temImagem) "img/${ex.id}_0.webp" else null)
    val b = imagemAsset(if (ex.temImagem) "img/${ex.id}_1.webp" else null)
    val trans = rememberInfiniteTransition(label = "demo")
    val fase by trans.animateFloat(0f, 1f, infiniteRepeatable(tween(2600, easing = FastOutSlowInEasing), RepeatMode.Restart), label = "fase")
    // 0–0.4 mostra A, 0.4–0.5 transição, 0.5–0.9 mostra B, 0.9–1 volta
    val mixB = if (!animar) 0f else when {
        fase < 0.4f -> 0f
        fase < 0.5f -> (fase - 0.4f) / 0.1f
        fase < 0.9f -> 1f
        else -> 1f - (fase - 0.9f) / 0.1f
    }
    val zoom = if (animar) 1.04f + 0.03f * kotlin.math.sin(fase * 6.283f) else 1.04f
    Box(
        modifier.clip(RoundedCornerShape(cantos)).background(Cor.Sup2)
            .semantics { contentDescription = "Demonstração de ${ex.nome}" },
    ) {
        if (a != null) {
            Image(a, null, Modifier.fillMaxSize().scale(zoom), contentScale = ContentScale.Crop)
            if (b != null) Image(b, null, Modifier.fillMaxSize().scale(zoom).alpha(mixB), contentScale = ContentScale.Crop)
            Box(Modifier.fillMaxSize().background(Brush.verticalGradient(0.55f to Color.Transparent, 1f to Color.Black.copy(alpha = 0.55f))))
            Box(Modifier.fillMaxSize().background(cor.copy(alpha = 0.10f)))
        } else {
            SemImagem(ex, cor)
        }
    }
}

@Composable
private fun BoxScope.SemImagem(ex: Exercicio, cor: Color) {
    val trans = rememberInfiniteTransition(label = "pulso")
    val p by trans.animateFloat(0.85f, 1.1f, infiniteRepeatable(tween(900), RepeatMode.Reverse), label = "p")
    Box(Modifier.fillMaxSize().background(Brush.radialGradient(listOf(cor.copy(alpha = 0.35f), Cor.Sup2))))
    Icon(iconeGrupo(ex), null, tint = cor, modifier = Modifier.align(Alignment.Center).size(64.dp).scale(p))
}

fun iconeGrupo(ex: Exercicio): ImageVector = when {
    ex.padroes.any { it.startsWith("luta") } -> Icons.Rounded.SportsMma
    ex.padroes.contains("corrida") -> Icons.AutoMirrored.Rounded.DirectionsRun
    ex.padroes.contains("bike") -> Icons.AutoMirrored.Rounded.DirectionsBike
    ex.tipo == "mobilidade" -> Icons.Rounded.SelfImprovement
    ex.tipo == "cardio" -> Icons.Rounded.LocalFireDepartment
    else -> Icons.Rounded.FitnessCenter
}

fun iconeModalidade(m: Modalidade?): ImageVector = when (m) {
    Modalidade.ACADEMIA -> Icons.Rounded.FitnessCenter
    Modalidade.CASA_CORPO -> Icons.Rounded.Home
    Modalidade.CASA_ELASTICO -> Icons.Rounded.SyncAlt
    Modalidade.CORRIDA -> Icons.AutoMirrored.Rounded.DirectionsRun
    Modalidade.BIKE -> Icons.AutoMirrored.Rounded.DirectionsBike
    Modalidade.LUTA -> Icons.Rounded.SportsMma
    Modalidade.ATLETA -> Icons.Rounded.EmojiEvents
    Modalidade.HIIT -> Icons.Rounded.Bolt
    Modalidade.HIBRIDO -> Icons.Rounded.LocalFireDepartment
    Modalidade.MOBILIDADE -> Icons.Rounded.Spa
    Modalidade.LONGEVIDADE -> Icons.Rounded.Elderly
    null -> Icons.Rounded.FitnessCenter
}

// ------------------------------------------------------------------ toque com vibração

@Composable
fun Modifier.toque(descricao: String? = null, onClick: () -> Unit): Modifier {
    val view = LocalView.current
    return this
        .then(if (descricao != null) Modifier.semantics { contentDescription = descricao } else Modifier)
        .clickable {
            view.performHapticFeedback(HapticFeedbackConstants.KEYBOARD_TAP)
            onClick()
        }
}

// ------------------------------------------------------------------ blocos visuais

@Composable
fun Cartao(
    modifier: Modifier = Modifier,
    cor: Color = Cor.Sup1,
    borda: Color = Cor.Borda,
    cantos: Dp = 22.dp,
    padding: PaddingValues = PaddingValues(18.dp),
    onClick: (() -> Unit)? = null,
    descricao: String? = null,
    content: @Composable ColumnScope.() -> Unit,
) {
    val forma = RoundedCornerShape(cantos)
    Column(
        modifier.clip(forma).background(cor).border(BorderStroke(1.dp, borda), forma)
            .then(if (onClick != null) Modifier.toque(descricao, onClick) else Modifier)
            .padding(padding),
        content = content,
    )
}

@Composable
fun Rotulo(texto: String, cor: Color = Cor.Texto3, modifier: Modifier = Modifier) {
    Text(texto.uppercase(), style = Tipo.Rotulo, color = cor, modifier = modifier)
}

@Composable
fun Etiqueta(texto: String, cor: Color = Cor.Brasa, icone: ImageVector? = null, cheia: Boolean = false, sobreFoto: Boolean = false) {
    Row(
        Modifier.clip(RoundedCornerShape(50)).background(if (cheia) cor else if (sobreFoto) Cor.Fundo.copy(alpha = 0.78f) else cor.copy(alpha = 0.14f))
            .padding(horizontal = 10.dp, vertical = 5.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        if (icone != null) {
            Icon(icone, null, tint = if (cheia) Cor.Fundo else cor, modifier = Modifier.size(14.dp))
            Spacer(Modifier.width(5.dp))
        }
        Text(texto, style = Tipo.PequenoForte, color = if (cheia) Cor.Fundo else cor, maxLines = 1, overflow = TextOverflow.Ellipsis)
    }
}

@Composable
fun BotaoPrimario(texto: String, modifier: Modifier = Modifier, icone: ImageVector? = null, ativo: Boolean = true, cor: Color? = null, onClick: () -> Unit) {
    val forma = RoundedCornerShape(18.dp)
    Row(
        modifier.heightIn(min = 58.dp).clip(forma)
            .then(if (!ativo) Modifier.background(Cor.Sup3) else if (cor != null) Modifier.background(cor) else Modifier.background(Cor.gradBrasa))
            .then(if (ativo) Modifier.toque(texto, onClick) else Modifier.semantics { contentDescription = texto })
            .padding(horizontal = 22.dp, vertical = 14.dp),
        horizontalArrangement = Arrangement.Center,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        val tinta = if (!ativo) Cor.Texto3 else if (cor != null && cor.luminance() > 0.45f) Cor.Fundo else Color.White
        if (icone != null) {
            Icon(icone, null, tint = tinta, modifier = Modifier.size(22.dp))
            Spacer(Modifier.width(10.dp))
        }
        Text(texto, style = Tipo.Botao, color = tinta)
    }
}

@Composable
fun BotaoSecundario(texto: String, modifier: Modifier = Modifier, icone: ImageVector? = null, cor: Color = Cor.Texto, onClick: () -> Unit) {
    val forma = RoundedCornerShape(16.dp)
    Row(
        modifier.heightIn(min = 50.dp).clip(forma).background(Cor.Sup2).border(1.dp, Cor.Borda, forma)
            .toque(texto, onClick).padding(horizontal = 16.dp, vertical = 12.dp),
        horizontalArrangement = Arrangement.Center,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        if (icone != null) {
            Icon(icone, null, tint = cor, modifier = Modifier.size(20.dp))
            Spacer(Modifier.width(8.dp))
        }
        Text(texto, style = Tipo.Botao, color = cor, maxLines = 1, overflow = TextOverflow.Ellipsis)
    }
}

@Composable
fun BotaoIcone(icone: ImageVector, descricao: String, modifier: Modifier = Modifier, cor: Color = Cor.Texto, fundo: Color = Cor.Sup2, tamanho: Dp = 46.dp, onClick: () -> Unit) {
    Box(
        modifier.size(tamanho).clip(CircleShape).background(fundo).border(1.dp, Cor.Borda, CircleShape).toque(descricao, onClick),
        contentAlignment = Alignment.Center,
    ) { Icon(icone, null, tint = cor, modifier = Modifier.size(tamanho * 0.48f)) }
}

@Composable
fun Topo(titulo: String, subtitulo: String? = null, onVoltar: (() -> Unit)? = null, acoes: @Composable RowScope.() -> Unit = {}) {
    Row(Modifier.fillMaxWidth().padding(horizontal = 20.dp, vertical = 12.dp), verticalAlignment = Alignment.CenterVertically) {
        if (onVoltar != null) {
            BotaoIcone(Icons.AutoMirrored.Rounded.ArrowBack, "Voltar", onClick = onVoltar)
            Spacer(Modifier.width(14.dp))
        }
        Column(Modifier.weight(1f)) {
            if (subtitulo != null) Rotulo(subtitulo)
            Text(titulo, style = Tipo.Titulo2, color = Cor.Texto, maxLines = 2, overflow = TextOverflow.Ellipsis)
        }
        acoes()
    }
}

@Composable
fun Secao(titulo: String, acao: String? = null, onAcao: (() -> Unit)? = null) {
    Row(Modifier.fillMaxWidth().padding(top = 26.dp, bottom = 12.dp), verticalAlignment = Alignment.CenterVertically) {
        Text(titulo, style = Tipo.Titulo3, color = Cor.Texto, modifier = Modifier.weight(1f))
        if (acao != null && onAcao != null) Text(acao, style = Tipo.PequenoForte, color = Cor.Brasa, modifier = Modifier.toque(acao, onAcao).padding(6.dp))
    }
}

/** Anel de progresso com texto central. */
@Composable
fun Anel(progresso: Float, modifier: Modifier = Modifier, cor: Color = Cor.Brasa, espessura: Dp = 10.dp, content: @Composable BoxScope.() -> Unit = {}) {
    Box(modifier, contentAlignment = Alignment.Center) {
        Canvas(Modifier.fillMaxSize()) {
            val s = espessura.toPx()
            val r = Size(size.width - s, size.height - s)
            drawArc(Cor.Sup3, -90f, 360f, false, Offset(s / 2, s / 2), r, style = Stroke(s, cap = StrokeCap.Round))
            if (progresso > 0f) drawArc(
                Brush.sweepGradient(listOf(cor.copy(alpha = 0.6f), cor, cor)), -90f, 360f * progresso.coerceIn(0f, 1f), false,
                Offset(s / 2, s / 2), r, style = Stroke(s, cap = StrokeCap.Round),
            )
        }
        content()
    }
}

@Composable
fun BarraProgresso(progresso: Float, modifier: Modifier = Modifier, cor: Color = Cor.Brasa, altura: Dp = 6.dp) {
    Box(modifier.height(altura).clip(RoundedCornerShape(50)).background(Cor.Sup3)) {
        Box(Modifier.fillMaxWidth(progresso.coerceIn(0f, 1f)).height(altura).clip(RoundedCornerShape(50)).background(cor))
    }
}

@Composable
fun Estatistica(valor: String, rotulo: String, modifier: Modifier = Modifier, cor: Color = Cor.Texto) {
    Column(modifier) {
        Text(valor, style = Tipo.Numero, color = cor, maxLines = 1)
        Spacer(Modifier.height(2.dp))
        Text(rotulo, style = Tipo.Pequeno, color = Cor.Texto2, maxLines = 2)
    }
}

@Composable
fun IconeRedondo(icone: ImageVector, cor: Color, tamanho: Dp = 44.dp) {
    Box(Modifier.size(tamanho).clip(RoundedCornerShape(14.dp)).background(cor.copy(alpha = 0.16f)), contentAlignment = Alignment.Center) {
        Icon(icone, null, tint = cor, modifier = Modifier.size(tamanho * 0.52f))
    }
}

@Composable
fun Vazio(titulo: String, texto: String, icone: ImageVector) {
    Column(Modifier.fillMaxWidth().padding(vertical = 40.dp, horizontal = 24.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        IconeRedondo(icone, Cor.Texto3, 64.dp)
        Spacer(Modifier.height(16.dp))
        Text(titulo, style = Tipo.Titulo3, color = Cor.Texto, textAlign = TextAlign.Center)
        Spacer(Modifier.height(6.dp))
        Text(texto, style = Tipo.Pequeno, color = Cor.Texto2, textAlign = TextAlign.Center)
    }
}

/** Linha fina com gradiente brasa — assinatura visual do app. */
@Composable
fun LinhaBrasa(modifier: Modifier = Modifier, cor: Color = Cor.Brasa) {
    Box(modifier.height(3.dp).width(36.dp).clip(RoundedCornerShape(50)).background(Brush.horizontalGradient(listOf(cor, cor.copy(alpha = 0f)))))
}

@Composable
fun rememberHaptico(): (Int) -> Unit {
    val view = LocalView.current
    return remember(view) { { tipo: Int -> view.performHapticFeedback(tipo) } }
}
