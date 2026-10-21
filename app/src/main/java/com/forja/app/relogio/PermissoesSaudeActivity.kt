package com.forja.app.relogio

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawingPadding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Text
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.forja.app.ui.BotaoPrimario
import com.forja.app.ui.BotaoSecundario
import com.forja.app.ui.Cor
import com.forja.app.ui.PRIVACIDADE
import com.forja.app.ui.Rotulo
import com.forja.app.ui.TemaForja
import com.forja.app.ui.Tipo

/**
 * Justificativa das permissões de saúde, aberta pelo Health Connect
 * (androidx.health.ACTION_SHOW_PERMISSIONS_RATIONALE e, no Android 14+, VIEW_PERMISSION_USAGE).
 */
class PermissoesSaudeActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            TemaForja {
                Column(Modifier.fillMaxSize().background(Cor.Fundo).safeDrawingPadding().verticalScroll(rememberScrollState()).padding(24.dp)) {
                    Rotulo("Forja · Health Connect", Cor.Brasa)
                    Spacer(Modifier.height(8.dp))
                    Text("Como o Forja usa seus dados de saúde", style = Tipo.Titulo2, color = Cor.Texto)
                    Spacer(Modifier.height(16.dp))
                    ITENS.forEach { (t, d) ->
                        Text(t, style = Tipo.CorpoForte, color = Cor.Texto)
                        Text(d, style = Tipo.Corpo, color = Cor.Texto2)
                        Spacer(Modifier.height(14.dp))
                    }
                    Spacer(Modifier.height(10.dp))
                    BotaoPrimario("Ler a política de privacidade", Modifier.fillMaxWidth()) {
                        runCatching { startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(PRIVACIDADE))) }
                    }
                    Spacer(Modifier.height(10.dp))
                    BotaoSecundario("Fechar", Modifier.fillMaxWidth()) { finish() }
                }
            }
        }
    }

    private companion object {
        val ITENS = listOf(
            "Gravar sessões de exercício" to "Quando você conclui um treino no Forja, ele é salvo no Health Connect com tipo (musculação, corrida, bike…), horário e duração, para aparecer nos seus outros apps de saúde.",
            "Ler frequência cardíaca" to "O Forja lê só a frequência cardíaca do intervalo do treino que você acabou de fazer (registrada pelo seu relógio) para mostrar a FC média e máxima na tela de treino concluído.",
            "Fica no seu aparelho" to "Nada é enviado para servidores do Forja ou de terceiros, nem usado para anúncios. Você pode revogar o acesso a qualquer momento nas configurações do Health Connect.",
        )
    }
}
