package com.forja.app.ui

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.BitmapRegionDecoder
import android.graphics.Rect
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideInVertically
import androidx.compose.animation.slideOutVertically
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Box
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
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.produceState
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.runtime.withFrameMillis
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.IntSize
import androidx.compose.ui.unit.dp
import com.forja.app.Conteudo
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext
import org.json.JSONObject

/** Animações 3D pré-renderizadas: uma folha de quadros (grade) por exercício em anim3d/<id>.webp + meta.json. */
object Animacoes3D {
    data class Meta(val quadros: Int, val colunas: Int, val lado: Int, val fps: Double)

    private var meta: Map<String, Meta>? = null
    private val folhas = android.util.LruCache<String, ImageBitmap>(3)
    private val capas = android.util.LruCache<String, ImageBitmap>(60)

    fun limpar() { meta = null; folhas.evictAll(); capas.evictAll() }

    fun meta(ctx: Context): Map<String, Meta> {
        meta?.let { return it }
        val m = runCatching {
            val o = JSONObject(Conteudo.abrir(ctx, "anim3d/meta.json")!!.bufferedReader().use { it.readText() })
            o.keys().asSequence().associateWith { k ->
                val x = o.getJSONObject(k)
                Meta(x.getInt("f"), x.getInt("c"), x.getInt("s"), x.optDouble("fps", 6.0))
            }
        }.getOrDefault(emptyMap())
        meta = m
        return m
    }

    fun tem(ctx: Context, id: String) = meta(ctx).containsKey(id)

    fun folha(ctx: Context, id: String): ImageBitmap? {
        folhas.get(id)?.let { return it }
        val op = BitmapFactory.Options().apply { inPreferredConfig = Bitmap.Config.RGB_565 }
        return runCatching { Conteudo.abrir(ctx, "anim3d/$id.webp")!!.use { BitmapFactory.decodeStream(it, null, op) }!!.asImageBitmap() }
            .getOrNull()?.also { folhas.put(id, it) }
    }

    /** Primeiro quadro, sem decodificar a folha inteira (para listas). */
    @Suppress("DEPRECATION")
    fun capa(ctx: Context, id: String, quadro: Int = 0): ImageBitmap? {
        val chave = "$id#$quadro"
        capas.get(chave)?.let { return it }
        val m = meta(ctx)[id] ?: return null
        return runCatching {
            Conteudo.abrir(ctx, "anim3d/$id.webp")!!.use { ins ->
                val dec = BitmapRegionDecoder.newInstance(ins, false)!!
                val x = (quadro % m.colunas) * m.lado
                val y = (quadro / m.colunas) * m.lado
                val op = BitmapFactory.Options().apply { inPreferredConfig = Bitmap.Config.RGB_565; inSampleSize = 2 }
                dec.decodeRegion(Rect(x, y, x + m.lado, y + m.lado), op).also { dec.recycle() }.asImageBitmap()
            }
        }.getOrNull()?.also { capas.put(chave, it) }
    }
}

/** Toca a animação 3D em loop (ou mostra um quadro fixo). Retorna false se não houver animação para o exercício. */
@Composable
fun Animacao3D(id: String, modifier: Modifier = Modifier, animar: Boolean = true, quadroFixo: Int? = null): Boolean {
    val ctx = LocalContext.current
    val m = remember(id) { Animacoes3D.meta(ctx)[id] } ?: return false
    if (!animar) {
        val capa by produceState<ImageBitmap?>(null, id) {
            value = withContext(Dispatchers.IO) { Animacoes3D.capa(ctx, id, quadroFixo ?: (m.quadros / 2)) }
        }
        Box(modifier.background(Cor.Sup2)) {
            capa?.let { androidx.compose.foundation.Image(it, null, Modifier.fillMaxSize(), contentScale = ContentScale.Crop) }
        }
        return true
    }
    val folha by produceState<ImageBitmap?>(null, id) { value = withContext(Dispatchers.IO) { Animacoes3D.folha(ctx, id) } }
    var quadro by remember(id) { mutableIntStateOf(0) }
    LaunchedEffect(id, folha) {
        if (folha == null) return@LaunchedEffect
        val passo = (1000.0 / m.fps).toLong()
        var ultimo = 0L
        while (true) {
            withFrameMillis { t ->
                if (t - ultimo >= passo) { ultimo = t; quadro = (quadro + 1) % m.quadros }
            }
        }
    }
    Box(modifier.background(Cor.Sup2)) {
        val f = folha
        if (f != null) {
            Canvas(Modifier.fillMaxSize()) { desenharQuadro(f, m, quadro) }
        } else {
            val capa by produceState<ImageBitmap?>(null, id) { value = withContext(Dispatchers.IO) { Animacoes3D.capa(ctx, id, 0) } }
            capa?.let { androidx.compose.foundation.Image(it, null, Modifier.fillMaxSize(), contentScale = ContentScale.Crop) }
        }
    }
    return true
}

private fun DrawScope.desenharQuadro(f: ImageBitmap, m: Animacoes3D.Meta, q: Int) {
    val x = (q % m.colunas) * m.lado
    val y = (q / m.colunas) * m.lado
    // recorte central (preenche o espaço, mantendo proporção)
    val alvoW = size.width; val alvoH = size.height
    val escala = maxOf(alvoW / m.lado, alvoH / m.lado)
    val srcW = (alvoW / escala).toInt().coerceAtMost(m.lado)
    val srcH = (alvoH / escala).toInt().coerceAtMost(m.lado)
    val sx = x + (m.lado - srcW) / 2
    val sy = y + (m.lado - srcH) / 2
    drawImage(f, srcOffset = IntOffset(sx, sy), srcSize = IntSize(srcW, srcH), dstSize = IntSize(alvoW.toInt(), alvoH.toInt()))
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
