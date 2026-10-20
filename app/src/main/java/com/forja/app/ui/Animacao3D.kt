package com.forja.app.ui

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideInVertically
import androidx.compose.animation.slideOutVertically
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.requiredSize
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.AutoAwesome
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.produceState
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clipToBounds
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.forja.app.Conteudo
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext
import org.json.JSONObject

/** Vídeos 3D (humano com os músculos trabalhados em destaque): video3d/<id>.mp4 + pôster video3d/<id>.webp + meta.json. */
object Animacoes3D {
    private var ids: Set<String>? = null
    private val posters = android.util.LruCache<String, ImageBitmap>(80)

    fun limpar() { ids = null; posters.evictAll() }

    fun tem(ctx: Context, id: String): Boolean {
        val conhecidos = ids ?: runCatching {
            JSONObject(Conteudo.abrir(ctx, "video3d/meta.json")!!.bufferedReader().use { it.readText() }).keys().asSequence().toSet()
        }.getOrDefault(emptySet()).also { ids = it }
        return id in conhecidos
    }

    fun posterEmCache(id: String): ImageBitmap? = posters.get(id)

    fun poster(ctx: Context, id: String): ImageBitmap? {
        posters.get(id)?.let { return it }
        val op = BitmapFactory.Options().apply { inPreferredConfig = Bitmap.Config.RGB_565 }
        return runCatching { Conteudo.abrir(ctx, "video3d/$id.webp")!!.use { BitmapFactory.decodeStream(it, null, op) }!!.asImageBitmap() }
            .getOrNull()?.also { posters.put(id, it) }
    }
}

private val FundoAnim = androidx.compose.ui.graphics.Color(0xFF1B1713)

/** Toca o vídeo 3D em loop (ou só o pôster, se animar = false). Retorna false se não houver vídeo para o exercício. */
@Composable
fun Animacao3D(id: String, modifier: Modifier = Modifier, animar: Boolean = true): Boolean {
    val ctx = LocalContext.current
    if (!remember(id) { Animacoes3D.tem(ctx, id) }) return false
    val poster by produceState(Animacoes3D.posterEmCache(id), id) {
        value = withContext(Dispatchers.IO) { Animacoes3D.poster(ctx, id) }
    }
    BoxWithConstraints(modifier.clipToBounds().background(FundoAnim), contentAlignment = Alignment.Center) {
        // quadrado na altura do espaço (corpo inteiro visível), levemente ampliado
        val lado = maxHeight * 1.12f
        Box(Modifier.requiredSize(lado)) {
            poster?.let { androidx.compose.foundation.Image(it, null, Modifier.fillMaxSize(), contentScale = ContentScale.Fit) }
            if (animar) VideoLoop(id, Modifier.fillMaxSize())
        }
        // laterais esfumadas no fundo
        val faixa = lado * 0.12f
        Box(Modifier.align(Alignment.Center).requiredSize(lado, maxHeight)) {
            Box(Modifier.align(Alignment.CenterStart).fillMaxHeight().width(faixa)
                .background(androidx.compose.ui.graphics.Brush.horizontalGradient(listOf(FundoAnim, FundoAnim.copy(alpha = 0f)))))
            Box(Modifier.align(Alignment.CenterEnd).fillMaxHeight().width(faixa)
                .background(androidx.compose.ui.graphics.Brush.horizontalGradient(listOf(FundoAnim.copy(alpha = 0f), FundoAnim))))
        }
    }
    return true
}

@androidx.annotation.OptIn(androidx.media3.common.util.UnstableApi::class)
@Composable
private fun VideoLoop(id: String, modifier: Modifier) {
    val ctx = LocalContext.current
    val player = remember(id) {
        androidx.media3.exoplayer.ExoPlayer.Builder(ctx).build().apply {
            volume = 0f
            repeatMode = androidx.media3.common.Player.REPEAT_MODE_ALL
            setMediaItem(androidx.media3.common.MediaItem.fromUri(Conteudo.uri(ctx, "video3d/$id.mp4")))
            prepare()
            playWhenReady = true
        }
    }
    var pronto by remember(id) { mutableStateOf(false) }
    DisposableEffect(player) {
        val ouvinte = object : androidx.media3.common.Player.Listener {
            override fun onRenderedFirstFrame() { pronto = true }
        }
        player.addListener(ouvinte)
        onDispose { player.removeListener(ouvinte); player.release() }
    }
    // pausa quando o app vai para segundo plano
    val ciclo = androidx.lifecycle.compose.LocalLifecycleOwner.current
    DisposableEffect(ciclo, player) {
        val obs = androidx.lifecycle.LifecycleEventObserver { _, e ->
            when (e) {
                androidx.lifecycle.Lifecycle.Event.ON_PAUSE -> player.pause()
                androidx.lifecycle.Lifecycle.Event.ON_RESUME -> player.play()
                else -> {}
            }
        }
        ciclo.lifecycle.addObserver(obs)
        onDispose { ciclo.lifecycle.removeObserver(obs) }
    }
    androidx.compose.ui.viewinterop.AndroidView(
        factory = { c -> android.view.TextureView(c).apply { isOpaque = false; player.setVideoTextureView(this) } },
        modifier = modifier.alpha(if (pronto) 1f else 0f),
    )
}

/** Aviso que aparece por alguns segundos no topo (ex.: conteúdo atualizado). */
@Composable
fun AvisoFlutuante(texto: String?, onFim: () -> Unit) {
    LaunchedEffect(texto) { if (texto != null) { delay(4500); onFim() } }
    Box(Modifier.fillMaxSize(), contentAlignment = Alignment.TopCenter) {
        AnimatedVisibility(texto != null, enter = slideInVertically { -it } + fadeIn(), exit = slideOutVertically { -it } + fadeOut()) {
            Row(
                Modifier.padding(top = 48.dp, start = 20.dp, end = 20.dp).fillMaxWidth().clip(RoundedCornerShape(18.dp)).background(Cor.Sup3)
                    .border(1.dp, Cor.Brasa.copy(alpha = 0.5f), RoundedCornerShape(18.dp)).padding(16.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Icon(Icons.Rounded.AutoAwesome, null, tint = Cor.Brasa, modifier = Modifier.size(22.dp))
                Spacer(Modifier.width(12.dp))
                Text(texto.orEmpty(), style = Tipo.PequenoForte, color = Cor.Texto)
            }
        }
    }
}
