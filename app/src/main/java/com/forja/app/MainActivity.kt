package com.forja.app

import android.os.Bundle
import android.view.WindowManager
import androidx.activity.ComponentActivity
import androidx.activity.SystemBarStyle
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.viewModels
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.key
import com.forja.app.ui.AvisoFlutuante
import androidx.compose.material3.LocalContentColor
import androidx.compose.ui.graphics.toArgb
import com.forja.app.ui.App
import com.forja.app.ui.Cor
import com.forja.app.ui.TemaForja

class MainActivity : ComponentActivity() {
    private val vm: AppViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge(
            statusBarStyle = SystemBarStyle.dark(Cor.Fundo.toArgb()),
            navigationBarStyle = SystemBarStyle.dark(Cor.Fundo.toArgb()),
        )
        // Extras para abrir telas direto (capturas automáticas): demo=true, screen=home|plano|mobilidade|exercicios|progresso|perfil|quiz|sessao|player|exercicio:<id>|rotina:<id>
        // Só valem pela entrada .Captura (protegida por DUMP, ou seja, só o adb); vindos de outro app são ignorados.
        val captura = intent.component?.className == "com.forja.app.Captura"
        val demo = captura && intent.getBooleanExtra("demo", false)
        val tela = if (captura) intent.getStringExtra("screen")?.takeIf { it.length <= 80 } else null
        vm.iniciar(demo)
        setContent {
            TemaForja {
                CompositionLocalProvider(LocalContentColor provides Cor.Texto) {
                    key(vm.versaoConteudo) {
                        App(vm, telaInicial = tela, manterTela = { ligar ->
                            if (ligar) window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
                            else window.clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
                        })
                    }
                    AvisoFlutuante(vm.aviso) { vm.aviso = null }
                }
            }
        }
    }

    override fun onStart() { super.onStart(); com.forja.app.relogio.TreinoAoVivo.appVisivel = true }
    override fun onStop() { com.forja.app.relogio.TreinoAoVivo.appVisivel = false; super.onStop() }
}
