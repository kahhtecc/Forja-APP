package com.forja.app

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.io.InputStream
import java.net.HttpURLConnection
import java.net.URL

/**
 * Conteúdo atualizável sem reinstalar o app: exercícios, animações 3D e fontes.
 *
 * O app traz uma cópia do conteúdo em assets/ com um manifesto (versão + hash de cada arquivo).
 * Ao abrir, consulta o manifesto publicado no GitHub; se a versão for maior, baixa só os arquivos que mudaram
 * para filesDir/conteudo e passa a usá-los. Para trocar o endereço (ex.: repositório público só de conteúdo),
 * altere BASE.
 */
object Conteudo {
    const val BASE = "https://raw.githubusercontent.com/kaiqueguimacuper-bit/teste-3/claude/personalized-workout-app-ou3pc2/app/src/main/assets/"
    const val MANIFESTO = "conteudo2.json"
    private const val RELEASES = "https://api.github.com/repos/kaiqueguimacuper-bit/teste-3/releases?per_page=15"

    data class Manifesto(val versao: Int, val arquivos: Map<String, String>)

    private fun pasta(ctx: Context) = File(ctx.filesDir, "conteudo")

    private fun ler(json: String): Manifesto {
        val o = JSONObject(json)
        val a = o.optJSONObject("arquivos") ?: JSONObject()
        return Manifesto(o.optInt("versao", 0), a.keys().asSequence().associateWith { a.getString(it) })
    }

    @Volatile private var cacheEmb: Manifesto? = null
    @Volatile private var cacheLoc: Pair<Long, Manifesto?>? = null

    fun embutido(ctx: Context): Manifesto = cacheEmb ?: runCatching { ler(ctx.assets.open(MANIFESTO).bufferedReader().use { it.readText() }) }
        .getOrDefault(Manifesto(0, emptyMap())).also { cacheEmb = it }

    fun local(ctx: Context): Manifesto? {
        val f = File(pasta(ctx), MANIFESTO)
        val marca = if (f.exists()) f.lastModified() else -1L
        cacheLoc?.let { (m, v) -> if (m == marca) return v }
        val v = if (marca < 0) null else runCatching { ler(f.readText()) }.getOrNull()
        cacheLoc = marca to v
        return v
    }

    fun versaoAtual(ctx: Context): Int = maxOf(embutido(ctx).versao, local(ctx)?.versao ?: 0)

    /** Abre um arquivo de conteúdo: a versão baixada, se for a mais nova, senão a embutida no app. */
    fun abrir(ctx: Context, caminho: String): InputStream? {
        val loc = local(ctx)
        val emb = embutido(ctx)
        val f = File(pasta(ctx), caminho)
        if (loc != null && loc.versao > emb.versao && f.exists() && loc.arquivos.containsKey(caminho) && loc.arquivos[caminho] != emb.arquivos[caminho]) {
            return runCatching { f.inputStream() }.getOrNull()
        }
        return runCatching { ctx.assets.open(caminho) }.getOrNull()
            ?: if (f.exists()) runCatching { f.inputStream() }.getOrNull() else null
    }

    /** Endereço para tocadores de mídia: o arquivo baixado, se for o mais novo, senão o embutido (asset:///). */
    fun uri(ctx: Context, caminho: String): android.net.Uri {
        val loc = local(ctx)
        val emb = embutido(ctx)
        val f = File(pasta(ctx), caminho)
        val baixado = loc != null && loc.versao > emb.versao && f.exists() && loc.arquivos.containsKey(caminho) && loc.arquivos[caminho] != emb.arquivos[caminho]
        return if (baixado || (!emb.arquivos.containsKey(caminho) && f.exists())) android.net.Uri.fromFile(f) else android.net.Uri.parse("asset:///$caminho")
    }

    fun existe(ctx: Context, caminho: String): Boolean = abrir(ctx, caminho)?.use { true } ?: false

    private fun baixar(url: String, limite: Int = 8000): ByteArray? = runCatching {
        val c = URL(url).openConnection() as HttpURLConnection
        c.connectTimeout = limite; c.readTimeout = limite * 3
        c.setRequestProperty("Cache-Control", "no-cache")
        try {
            if (c.responseCode != 200) null else c.inputStream.use { it.readBytes() }
        } finally { c.disconnect() }
    }.getOrNull()

    private fun sha1(b: ByteArray): String = java.security.MessageDigest.getInstance("SHA-1").digest(b).joinToString("") { "%02x".format(it) }

    /**
     * Procura conteúdo novo. Retorna quantos arquivos foram atualizados (0 = nada novo).
     * Seguro para rodar em segundo plano; falhas de rede são ignoradas.
     */
    fun atualizar(ctx: Context): Int {
        val remotoBytes = baixar(BASE + MANIFESTO) ?: return 0
        val remoto = runCatching { ler(String(remotoBytes)) }.getOrNull() ?: return 0
        if (remoto.versao <= versaoAtual(ctx)) return 0
        val emb = embutido(ctx)
        val loc = local(ctx)
        val dir = pasta(ctx).apply { mkdirs() }
        var n = 0
        for ((caminho, hash) in remoto.arquivos) {
            if (emb.arquivos[caminho] == hash) continue // igual ao que veio no app
            val f = File(dir, caminho)
            if (loc?.arquivos?.get(caminho) == hash && f.exists()) continue
            val b = baixar(BASE + caminho, 15000) ?: return 0 // sem rede no meio: tenta de novo depois
            if (sha1(b) != hash) return 0
            f.parentFile?.mkdirs()
            val tmp = File(f.path + ".tmp")
            tmp.writeBytes(b)
            tmp.renameTo(f)
            n++
        }
        File(dir, MANIFESTO).writeBytes(remotoBytes)
        return maxOf(n, 1)
    }

    data class NovaVersao(val numero: Int, val pagina: String, val apk: String?)

    /** Verifica se há APK mais novo publicado (GitHub Releases). */
    fun novaVersaoDoApp(): NovaVersao? {
        if (BuildConfig.LOJA_PLAY) return null // na Play Store, as atualizações vêm da própria loja
        val b = baixar(RELEASES) ?: return null
        return runCatching {
            val lista = JSONArray(String(b))
            val r = (0 until lista.length()).map { lista.getJSONObject(it) }.first { it.getString("tag_name").startsWith("build-") }
            val n = r.getString("tag_name").substringAfter("build-").toInt()
            if (n <= BuildConfig.VERSION_CODE) return null
            val assets = r.getJSONArray("assets")
            val apk = (0 until assets.length()).map { assets.getJSONObject(it) }
                .firstOrNull { it.getString("name").endsWith(".apk") && !it.getString("name").contains("debug") }?.getString("browser_download_url")
            NovaVersao(n, r.getString("html_url"), apk)
        }.getOrNull()
    }
}
