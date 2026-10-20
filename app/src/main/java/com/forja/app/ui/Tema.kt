package com.forja.app.ui

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.Typography
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.Font
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp
import com.forja.app.R
import com.forja.app.core.Modalidade

object Cor {
    val Fundo = Color(0xFF0E0D0C)
    val Sup1 = Color(0xFF161412)
    val Sup2 = Color(0xFF1E1B18)
    val Sup3 = Color(0xFF28241F)
    val Borda = Color(0xFF35302A)
    val Texto = Color(0xFFF2EBE0)
    val Texto2 = Color(0xFFA89E90)
    val Texto3 = Color(0xFF6E665C)
    val Brasa = Color(0xFFFF5B22)
    val BrasaClara = Color(0xFFFF8A50)
    val BrasaEscura = Color(0xFFC2410C)
    val Ok = Color(0xFF34D399)
    val Alerta = Color(0xFFFBBF24)
    val Perigo = Color(0xFFF43F5E)

    val gradBrasa = Brush.linearGradient(listOf(Color(0xFFFF8A50), Color(0xFFFF5B22), Color(0xFFD9381E)))

    fun modalidade(m: Modalidade?): Color = when (m) {
        Modalidade.ACADEMIA -> Brasa
        Modalidade.CASA_CORPO -> Color(0xFFF2B24C)
        Modalidade.CASA_ELASTICO -> Color(0xFFE879A6)
        Modalidade.CORRIDA -> Color(0xFF34D399)
        Modalidade.BIKE -> Color(0xFF38BDF8)
        Modalidade.LUTA -> Color(0xFFF43F5E)
        Modalidade.ATLETA -> Color(0xFFA78BFA)
        Modalidade.HIIT -> Color(0xFFFACC15)
        Modalidade.HIBRIDO -> Color(0xFFFB923C)
        Modalidade.MOBILIDADE -> Color(0xFF5EEAD4)
        Modalidade.LONGEVIDADE -> Color(0xFFA3E635)
        null -> Brasa
    }

    /** Cor por tipo de sessão (dentro de um plano). */
    fun tipoSessao(tipo: String, padrao: Color): Color = when (tipo) {
        "corrida" -> modalidade(Modalidade.CORRIDA)
        "bike" -> modalidade(Modalidade.BIKE)
        "luta" -> modalidade(Modalidade.LUTA)
        "hiit" -> modalidade(Modalidade.HIIT)
        "mobilidade" -> modalidade(Modalidade.MOBILIDADE)
        "cardio" -> Color(0xFF7DD3FC)
        "atleta" -> modalidade(Modalidade.ATLETA)
        else -> padrao
    }

    fun tema(id: String): Color = Modalidade.de(id)?.let { modalidade(it) } ?: modalidade(Modalidade.MOBILIDADE)
}

val Display = FontFamily(
    Font(R.font.bigshoulders_bold, FontWeight.Bold),
    Font(R.font.bigshoulders_extrabold, FontWeight.ExtraBold),
    Font(R.font.bigshoulders_black, FontWeight.Black),
)

val Texto = FontFamily(
    Font(R.font.manrope_regular, FontWeight.Normal),
    Font(R.font.manrope_medium, FontWeight.Medium),
    Font(R.font.manrope_semibold, FontWeight.SemiBold),
    Font(R.font.manrope_bold, FontWeight.Bold),
    Font(R.font.manrope_extrabold, FontWeight.ExtraBold),
)

object Tipo {
    val Gigante = TextStyle(fontFamily = Display, fontWeight = FontWeight.Black, fontSize = 64.sp, lineHeight = 60.sp, letterSpacing = (-0.5).sp)
    val Titulo1 = TextStyle(fontFamily = Display, fontWeight = FontWeight.Black, fontSize = 40.sp, lineHeight = 40.sp)
    val Titulo2 = TextStyle(fontFamily = Display, fontWeight = FontWeight.ExtraBold, fontSize = 30.sp, lineHeight = 31.sp)
    val Titulo3 = TextStyle(fontFamily = Display, fontWeight = FontWeight.ExtraBold, fontSize = 22.sp, lineHeight = 24.sp)
    val Numero = TextStyle(fontFamily = Display, fontWeight = FontWeight.Black, fontSize = 28.sp, lineHeight = 28.sp)
    val Rotulo = TextStyle(fontFamily = Texto, fontWeight = FontWeight.ExtraBold, fontSize = 11.sp, letterSpacing = 1.4.sp)
    val Corpo = TextStyle(fontFamily = Texto, fontWeight = FontWeight.Medium, fontSize = 15.sp, lineHeight = 22.sp)
    val CorpoForte = TextStyle(fontFamily = Texto, fontWeight = FontWeight.Bold, fontSize = 15.sp, lineHeight = 21.sp)
    val Pequeno = TextStyle(fontFamily = Texto, fontWeight = FontWeight.Medium, fontSize = 13.sp, lineHeight = 18.sp)
    val PequenoForte = TextStyle(fontFamily = Texto, fontWeight = FontWeight.Bold, fontSize = 13.sp, lineHeight = 18.sp)
    val Botao = TextStyle(fontFamily = Texto, fontWeight = FontWeight.ExtraBold, fontSize = 15.sp, letterSpacing = 0.3.sp)
}

@Composable
fun TemaForja(content: @Composable () -> Unit) {
    @Suppress("UNUSED_VARIABLE") val escuro = isSystemInDarkTheme()
    MaterialTheme(
        colorScheme = darkColorScheme(
            primary = Cor.Brasa, onPrimary = Color.White, background = Cor.Fundo, onBackground = Cor.Texto,
            surface = Cor.Sup1, onSurface = Cor.Texto, surfaceVariant = Cor.Sup2, onSurfaceVariant = Cor.Texto2, outline = Cor.Borda,
        ),
        typography = Typography(bodyLarge = Tipo.Corpo, bodyMedium = Tipo.Corpo, labelLarge = Tipo.Botao),
        content = content,
    )
}
