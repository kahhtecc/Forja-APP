package com.forja.app

import android.content.Context
import android.content.Intent
import android.net.Uri
import java.io.File

/** Regras de segurança compartilhadas: o que o app aceita de fora (conteúdo baixado e links). */
object Seguranca {
    /** Caminhos de conteúdo: só letras, números, _ - . e subpastas; sem "..", sem caminho absoluto. */
    private val CAMINHO = Regex("^([A-Za-z0-9_-]+/)*[A-Za-z0-9_-][A-Za-z0-9_.-]*$")
    private val EXTENSOES = setOf("json", "mp4", "webp", "png", "jpg")

    fun caminhoValido(caminho: String): Boolean =
        caminho.length <= 160 && CAMINHO.matches(caminho) && ".." !in caminho &&
            caminho.substringAfterLast('.', "").lowercase() in EXTENSOES

    /** Garante que [f] fica dentro de [pasta] mesmo depois de resolver links e "..". */
    fun dentroDe(pasta: File, f: File): Boolean =
        f.canonicalPath.startsWith(pasta.canonicalPath + File.separator)

    /** ID de vídeo do YouTube (11 caracteres). */
    fun idYoutubeValido(id: String) = Regex("^[A-Za-z0-9_-]{11}$").matches(id)

    /** Só abre links https (nada de intent:, file:, content: ou javascript: vindos do conteúdo). */
    fun linkSeguro(url: String?): Uri? {
        val u = url?.let { runCatching { Uri.parse(it.trim()) }.getOrNull() } ?: return null
        return u.takeIf { it.scheme.equals("https", ignoreCase = true) && !it.host.isNullOrBlank() }
    }

    /** Links de atualização do APK: só do próprio repositório no GitHub. */
    fun linkDoRepositorio(url: String?): Boolean {
        val u = linkSeguro(url) ?: return false
        val p = u.path.orEmpty()
        return (u.host == "github.com" && p.startsWith("/kaiqueguimacuper-bit/teste-3/")) ||
            (u.host == "objects.githubusercontent.com")
    }

    fun abrirLink(ctx: Context, url: String?) {
        val u = linkSeguro(url) ?: return
        runCatching {
            ctx.startActivity(Intent(Intent.ACTION_VIEW, u).addCategory(Intent.CATEGORY_BROWSABLE).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
        }
    }
}
