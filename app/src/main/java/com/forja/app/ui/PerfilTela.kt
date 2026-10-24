package com.forja.app.ui

import android.annotation.SuppressLint
import android.bluetooth.BluetoothAdapter
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.rounded.OpenInNew
import androidx.compose.material.icons.rounded.Bluetooth
import androidx.compose.material.icons.rounded.ChevronRight
import androidx.compose.material.icons.rounded.Favorite
import androidx.compose.material.icons.rounded.MonitorHeart
import androidx.compose.material.icons.rounded.DeleteForever
import androidx.compose.material.icons.rounded.Edit
import androidx.compose.material.icons.rounded.Notifications
import androidx.compose.material.icons.rounded.RestartAlt
import androidx.compose.material.icons.rounded.Science
import androidx.compose.material.icons.rounded.Shield
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Icon
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.forja.app.AppViewModel
import com.forja.app.BuildConfig
import com.forja.app.Lembretes
import com.forja.app.core.Estado
import com.forja.app.core.Questionario
import com.forja.app.relogio.FcAoVivo
import com.forja.app.relogio.MonitorBle
import com.forja.app.relogio.PrefsRelogio
import com.forja.app.relogio.Saude
import androidx.core.content.ContextCompat
import androidx.health.connect.client.PermissionController
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

@OptIn(ExperimentalLayoutApi::class)
@Composable
fun TelaPerfil(vm: AppViewModel, estado: Estado, nav: Navegador) {
    val ctx = LocalContext.current
    val p = estado.perfil
    val plano = estado.plano
    val aj = estado.ajustes
    var confirmarApagar by remember { mutableStateOf(false) }
    var confirmarRecomecar by remember { mutableStateOf(false) }
    var lembrete by remember { mutableStateOf(Lembretes.ativo(ctx)) }
    var hora by remember { mutableIntStateOf(Lembretes.hora(ctx)) }
    val permissao = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { ok ->
        lembrete = ok; Lembretes.configurar(ctx, ok, hora)
    }
    val cor = Cor.modalidade(plano?.modalidade)

    // Relógio e saúde
    var mostrarRelogio by remember { mutableStateOf(PrefsRelogio.mostrar(ctx)) }
    val permNotif = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { ok ->
        if (!ok) vm.aviso = "Sem permissão de notificação o treino não aparece no relógio."
    }
    var hcConectado by remember { mutableStateOf(false) }
    var hcVersao by remember { mutableIntStateOf(0) }
    LaunchedEffect(hcVersao) { hcConectado = !vm.demo && withContext(Dispatchers.IO) { runCatching { Saude.conectado(ctx) }.getOrDefault(false) } }
    val hcPedir = rememberLauncherForActivityResult(PermissionController.createRequestPermissionResultContract()) { g ->
        hcVersao++
        if (g.isNotEmpty()) vm.aviso = "Health Connect conectado: seus treinos e a FC do relógio passam a ser sincronizados."
    }
    var bleLembrado by remember { mutableStateOf(PrefsRelogio.ble(ctx)) }
    var dialogoBle by remember { mutableStateOf(false) }
    val blePedir = rememberLauncherForActivityResult(ActivityResultContracts.RequestMultiplePermissions()) { r ->
        if (r.values.all { it }) dialogoBle = true else vm.aviso = "Sem a permissão de Bluetooth não dá para procurar o monitor cardíaco."
    }

    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).navigationBarsPadding()) {
        Topo("Perfil", "Você e seus ajustes", onVoltar = { nav.voltar() })
        Column(Modifier.padding(horizontal = 20.dp)) {
            Cartao(Modifier.fillMaxWidth()) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(Modifier.size(58.dp).clip(CircleShape).background(Cor.gradBrasa), contentAlignment = Alignment.Center) {
                        Text(p?.nome?.take(1)?.uppercase()?.ifBlank { "F" } ?: "F", style = Tipo.Titulo2, color = Color.White)
                    }
                    Spacer(Modifier.width(14.dp))
                    Column {
                        Text(p?.nome?.ifBlank { "Atleta Forja" } ?: "Atleta Forja", style = Tipo.Titulo2, color = Cor.Texto)
                        if (p != null) Text("${p.idade} anos · ${p.alturaCm} cm · ${p.pesoKg} kg · IMC ${"%.1f".format(p.imc).replace('.', ',')}", style = Tipo.Pequeno, color = Cor.Texto2)
                    }
                }
                if (p != null && plano != null) {
                    Spacer(Modifier.height(14.dp))
                    FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Etiqueta(p.modalidade.curto, cor, iconeModalidade(p.modalidade))
                        Etiqueta(p.objetivo.nome, Cor.Texto2)
                        Etiqueta(p.nivel.nome, Cor.Texto2)
                        Etiqueta("${p.dias.size}x · ${p.dias.joinToString(" ") { Questionario.DIAS_NOMES[it - 1] }}", Cor.Texto2)
                        Etiqueta("${p.minutos} min", Cor.Texto2)
                    }
                }
            }
            Secao("Plano")
            LinhaAcao(Icons.Rounded.Edit, "Refazer questionário", "Mude modalidade, objetivo, dias ou limitações") { nav.ir(Rota.Questionario) }
            LinhaAcao(Icons.Rounded.RestartAlt, "Recomeçar da semana 1", "Mantém o histórico de treinos") { confirmarRecomecar = true }

            Secao("Treino ao vivo")
            Cartao(Modifier.fillMaxWidth(), padding = PaddingValues(horizontal = 16.dp, vertical = 6.dp)) {
                Alternar("Sons do cronômetro", aj.som) { vm.loja.salvarAjustes(aj.copy(som = it)) }
                Alternar("Vibração", aj.vibracao) { vm.loja.salvarAjustes(aj.copy(vibracao = it)) }
                Alternar("Manter a tela ligada", aj.telaLigada) { vm.loja.salvarAjustes(aj.copy(telaLigada = it)) }
            }

            Secao("Relógio e saúde")
            Cartao(Modifier.fillMaxWidth(), padding = PaddingValues(horizontal = 16.dp, vertical = 6.dp)) {
                Alternar("Mostrar treino no relógio (notificação)", mostrarRelogio) { on ->
                    mostrarRelogio = on; PrefsRelogio.setMostrar(ctx, on)
                    if (on && Build.VERSION.SDK_INT >= 33 && ContextCompat.checkSelfPermission(ctx, android.Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED)
                        permNotif.launch(android.Manifest.permission.POST_NOTIFICATIONS)
                }
                Text("Exercício, série, descanso com vibração no fim e botões “Concluir série” e “Pular descanso” na tela bloqueada e no relógio pareado (Wear OS, Galaxy Watch, Garmin, Amazfit, Xiaomi…).",
                    style = Tipo.Pequeno, color = Cor.Texto2, modifier = Modifier.padding(bottom = 10.dp))
            }
            LinhaAcao(Icons.Rounded.MonitorHeart, "Conectar ao Health Connect",
                when {
                    hcConectado -> "Conectado ✓ · treinos salvos e FC do relógio no fim do treino"
                    Saude.disponivel(ctx) -> "Salva seus treinos e lê a FC de relógios Samsung, Garmin, Fitbit, Xiaomi…"
                    Saude.precisaInstalar(ctx) -> "Instale o Health Connect para sincronizar com seu relógio"
                    else -> "Health Connect não disponível neste aparelho"
                }) {
                when {
                    Saude.disponivel(ctx) -> hcPedir.launch(Saude.PERMISSOES)
                    Saude.precisaInstalar(ctx) -> Saude.instalar(ctx)
                    else -> vm.aviso = "O Health Connect não está disponível neste aparelho."
                }
            }
            LinhaAcao(Icons.Rounded.Bluetooth, "Conectar cinta/relógio por Bluetooth",
                bleLembrado?.let { "Lembrado: ${it.second} · conecta sozinho no treino" } ?: "Cintas e relógios com “transmitir FC” (Polar, Garmin, Coros, Amazfit…)") {
                when {
                    !MonitorBle.disponivel(ctx) -> vm.aviso = "Este aparelho não tem Bluetooth LE."
                    MonitorBle.temPermissao(ctx) -> dialogoBle = true
                    else -> blePedir.launch(MonitorBle.permissoes())
                }
            }

            Secao("Lembretes")
            Cartao(Modifier.fillMaxWidth(), padding = PaddingValues(16.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Rounded.Notifications, null, tint = Cor.Brasa)
                    Spacer(Modifier.width(12.dp))
                    Column(Modifier.weight(1f)) {
                        Text("Avisar nos dias de treino", style = Tipo.CorpoForte, color = Cor.Texto)
                        Text("Só quando o treino do dia ainda não foi feito", style = Tipo.Pequeno, color = Cor.Texto2)
                    }
                    Switch(lembrete, onCheckedChange = { on ->
                        if (on && Build.VERSION.SDK_INT >= 33) permissao.launch(android.Manifest.permission.POST_NOTIFICATIONS)
                        else { lembrete = on; Lembretes.configurar(ctx, on, hora) }
                    }, colors = SwitchDefaults.colors(checkedTrackColor = Cor.Brasa, checkedThumbColor = Color.White, uncheckedTrackColor = Cor.Sup3, uncheckedBorderColor = Cor.Borda))
                }
                if (lembrete) {
                    Spacer(Modifier.height(12.dp))
                    FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        listOf(6, 7, 8, 12, 17, 18, 19, 20).forEach { h -> Chip("${h}h", h == hora) { hora = h; Lembretes.configurar(ctx, true, h) } }
                    }
                }
            }

            Secao("Sobre")
            LinhaAcao(Icons.Rounded.Science, "Base científica", "Diretrizes e ${vm.fontes.size} referências usadas para montar as rotinas") { nav.ir(Rota.Fontes) }
            LinhaAcao(Icons.Rounded.Shield, "Política de privacidade", "Nada sai do seu aparelho: sem cadastro, anúncios ou rastreamento") {
                runCatching { ctx.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(PRIVACIDADE))) }
            }
            Cartao(Modifier.fillMaxWidth().padding(top = 4.dp)) {
                Text("Forja ${BuildConfig.VERSION_NAME}", style = Tipo.CorpoForte, color = Cor.Texto)
                Spacer(Modifier.height(6.dp))
                Text("Animações 3D feitas com o MakeHuman (CC0) e o Blender. Fotos: free-exercise-db (domínio público). Fontes Big Shoulders e Manrope (SIL OFL). Vídeos dos respectivos canais no YouTube.",
                    style = Tipo.Pequeno, color = Cor.Texto2)
                Spacer(Modifier.height(8.dp))
                Text("O Forja orienta com base em diretrizes reconhecidas, mas não substitui avaliação médica nem acompanhamento de um profissional de educação física.",
                    style = Tipo.Pequeno, color = Cor.Texto3)
                if (vm.demo) { Spacer(Modifier.height(8.dp)); Etiqueta("Modo demonstração", Cor.Alerta) }
            }
            Spacer(Modifier.height(14.dp))
            LinhaAcao(Icons.Rounded.DeleteForever, "Apagar todos os dados", "Respostas, plano e histórico", cor = Cor.Perigo) { confirmarApagar = true }
            Spacer(Modifier.height(30.dp))
        }
    }
    if (dialogoBle) DialogoBle(onFechar = { dialogoBle = false; bleLembrado = PrefsRelogio.ble(ctx) })
    if (confirmarApagar) AlertDialog(onDismissRequest = { confirmarApagar = false }, containerColor = Cor.Sup2,
        title = { Text("Apagar tudo?", style = Tipo.Titulo3, color = Cor.Texto) },
        text = { Text("Isso remove suas respostas, o plano e todo o histórico deste aparelho. Não dá para desfazer.", style = Tipo.Corpo, color = Cor.Texto2) },
        confirmButton = { TextButton(onClick = { confirmarApagar = false; vm.treino = null; vm.loja.apagarTudo(); nav.raiz(Rota.Questionario) }) { Text("Apagar", style = Tipo.Botao, color = Cor.Perigo) } },
        dismissButton = { TextButton(onClick = { confirmarApagar = false }) { Text("Cancelar", style = Tipo.Botao, color = Cor.Texto2) } })
    if (confirmarRecomecar) AlertDialog(onDismissRequest = { confirmarRecomecar = false }, containerColor = Cor.Sup2,
        title = { Text("Recomeçar o plano?", style = Tipo.Titulo3, color = Cor.Texto) },
        text = { Text("A semana atual passa a ser a semana 1. Seus treinos registrados continuam no histórico.", style = Tipo.Corpo, color = Cor.Texto2) },
        confirmButton = { TextButton(onClick = { confirmarRecomecar = false; vm.loja.recomecarPlano() }) { Text("Recomeçar", style = Tipo.Botao, color = Cor.Brasa) } },
        dismissButton = { TextButton(onClick = { confirmarRecomecar = false }) { Text("Cancelar", style = Tipo.Botao, color = Cor.Texto2) } })
}

@SuppressLint("MissingPermission")
@Composable
private fun DialogoBle(onFechar: () -> Unit) {
    val ctx = LocalContext.current
    val lista by MonitorBle.encontrados.collectAsState()
    val buscando by MonitorBle.escaneando.collectAsState()
    val conectado by MonitorBle.conectado.collectAsState()
    val conectando by MonitorBle.conectando.collectAsState()
    val bpm by FcAoVivo.bpm.collectAsState()
    var ligado by remember { mutableStateOf(MonitorBle.ligado(ctx)) }
    var lembrado by remember { mutableStateOf(PrefsRelogio.ble(ctx)) }
    val ligar = rememberLauncherForActivityResult(ActivityResultContracts.StartActivityForResult()) { ligado = MonitorBle.ligado(ctx) }
    LaunchedEffect(ligado) { if (ligado) MonitorBle.escanear(ctx) }
    DisposableEffect(Unit) { onDispose { MonitorBle.pararBusca(ctx); MonitorBle.desconectar() } }
    AlertDialog(
        onDismissRequest = onFechar, containerColor = Cor.Sup2,
        title = { Text("Monitor cardíaco", style = Tipo.Titulo3, color = Cor.Texto) },
        text = {
            Column(Modifier.verticalScroll(rememberScrollState())) {
                if (!ligado) {
                    Text("O Bluetooth está desligado.", style = Tipo.Corpo, color = Cor.Texto2)
                    Spacer(Modifier.height(10.dp))
                    BotaoSecundario("Ligar Bluetooth") { runCatching { ligar.launch(Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE)) } }
                    return@Column
                }
                Text("No relógio, ative “transmitir frequência cardíaca” (Garmin: Transmitir FC; Polar: Compartilhar FC; Coros/Amazfit: Heart rate broadcast). Cintas ligam ao umedecer os eletrodos.",
                    style = Tipo.Pequeno, color = Cor.Texto2)
                Spacer(Modifier.height(12.dp))
                if (conectado != null) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Rounded.Favorite, null, tint = Cor.Perigo, modifier = Modifier.size(20.dp))
                        Spacer(Modifier.width(8.dp))
                        Text("$conectado · ${FcAoVivo.atual()?.let { "$it bpm" } ?: bpm?.let { "$it bpm" } ?: "aguardando FC…"}", style = Tipo.CorpoForte, color = Cor.Texto)
                    }
                    Spacer(Modifier.height(10.dp))
                } else if (conectando) {
                    Text("Conectando…", style = Tipo.CorpoForte, color = Cor.Brasa)
                    Spacer(Modifier.height(10.dp))
                }
                lista.forEach { d ->
                    Row(Modifier.fillMaxWidth().clip(RoundedCornerShape(14.dp)).background(Cor.Sup3)
                        .toque("Conectar ${d.nome}") { MonitorBle.pararBusca(ctx); MonitorBle.conectar(ctx, d.endereco, d.nome); lembrado = PrefsRelogio.ble(ctx) }
                        .padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Rounded.Bluetooth, null, tint = Cor.Brasa, modifier = Modifier.size(20.dp))
                        Spacer(Modifier.width(10.dp))
                        Text(d.nome, style = Tipo.CorpoForte, color = Cor.Texto, modifier = Modifier.weight(1f))
                        if (lembrado?.first == d.endereco) Text("lembrado", style = Tipo.Pequeno, color = Cor.Texto3)
                    }
                    Spacer(Modifier.height(6.dp))
                }
                if (buscando) Text("Procurando monitores por perto…", style = Tipo.Pequeno, color = Cor.Texto3)
                else {
                    if (lista.isEmpty()) Text("Nenhum monitor encontrado.", style = Tipo.Pequeno, color = Cor.Texto3)
                    Spacer(Modifier.height(8.dp))
                    BotaoSecundario("Procurar de novo") { MonitorBle.escanear(ctx) }
                }
                lembrado?.let { l ->
                    Spacer(Modifier.height(8.dp))
                    TextButton(onClick = { MonitorBle.esquecer(ctx); lembrado = null }) { Text("Esquecer ${l.second}", style = Tipo.Botao, color = Cor.Perigo) }
                }
            }
        },
        confirmButton = { TextButton(onClick = onFechar) { Text("Pronto", style = Tipo.Botao, color = Cor.Brasa) } },
    )
}

@Composable
private fun LinhaAcao(icone: ImageVector, titulo: String, sub: String, cor: Color = Cor.Brasa, onClick: () -> Unit) {
    Cartao(Modifier.fillMaxWidth().padding(vertical = 5.dp), padding = PaddingValues(14.dp), onClick = onClick, descricao = titulo) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            IconeRedondo(icone, cor, 40.dp)
            Spacer(Modifier.width(12.dp))
            Column(Modifier.weight(1f)) {
                Text(titulo, style = Tipo.CorpoForte, color = if (cor == Cor.Perigo) Cor.Perigo else Cor.Texto)
                Text(sub, style = Tipo.Pequeno, color = Cor.Texto2)
            }
            Icon(Icons.Rounded.ChevronRight, null, tint = Cor.Texto3)
        }
    }
}

@Composable
private fun Alternar(texto: String, valor: Boolean, onMudar: (Boolean) -> Unit) {
    Row(Modifier.fillMaxWidth().padding(vertical = 6.dp), verticalAlignment = Alignment.CenterVertically) {
        Text(texto, style = Tipo.Corpo, color = Cor.Texto, modifier = Modifier.weight(1f))
        Switch(valor, onCheckedChange = onMudar, colors = SwitchDefaults.colors(checkedTrackColor = Cor.Brasa, checkedThumbColor = Color.White, uncheckedTrackColor = Cor.Sup3, uncheckedBorderColor = Cor.Borda))
    }
}

// ------------------------------------------------------------------ base científica

private val PRINCIPIOS = listOf(
    "Musculação" to "Hipertrofia: ~6–12 repetições (faixas mais amplas também funcionam) perto da falha (RIR 0–3), 10+ séries semanais por grupo muscular e cada grupo 2x por semana. Força: cargas altas, 3–6 repetições e descansos de 2–5 min. Progressão por dupla progressão e semana leve a cada 4–6 semanas.",
    "Saúde e emagrecimento" to "OMS 2020: 150–300 min de atividade moderada (ou 75–150 vigorosa) por semana e força pelo menos 2 dias. No déficit calórico, a musculação preserva a massa magra.",
    "Corrida" to "Cerca de 80% do volume em intensidade leve (Seiler). Longão progressivo, semanas de recuperação a cada 3–4 e polimento antes da prova. Iniciantes alternam caminhada e corrida.",
    "Ciclismo" to "Zonas por % do FTP (Coggan): Z2 56–75%, sweet spot 88–94%, limiar 91–105%, VO2máx 106–120%. FTP ≈ 95% da potência média de 20 min.",
    "Lutas e atletas" to "Força máxima e potência longe dos treinos técnicos pesados, condicionamento no formato dos rounds, pliometria com volume controlado e prevenção (ex.: flexão nórdica, FIFA 11+).",
    "Mobilidade" to "Antes do treino, mobilidade dinâmica (estático curto, até ~60 s por grupo). Depois, alongamento estático de 10–30 s, 2–4 vezes, pelo menos 2–3 dias por semana.",
    "Segurança" to "Triagem PAR-Q+, adaptação conservadora para joelho, lombar e ombro, e liberação médica na gestação. Pare se sentir dor no peito, tontura ou falta de ar desproporcional.",
)

@Composable
fun TelaFontes(vm: AppViewModel, onVoltar: () -> Unit) {
    val ctx = LocalContext.current
    LazyColumn(Modifier.fillMaxSize().navigationBarsPadding(), contentPadding = PaddingValues(bottom = 30.dp)) {
        item { Topo("Base científica", "Como o Forja monta sua rotina", onVoltar = onVoltar) }
        items(PRINCIPIOS) { (t, d) ->
            Cartao(Modifier.fillMaxWidth().padding(horizontal = 20.dp, vertical = 5.dp)) {
                Rotulo(t, Cor.Brasa)
                Spacer(Modifier.height(6.dp))
                Text(d, style = Tipo.Corpo, color = Cor.Texto)
            }
        }
        item { Box(Modifier.padding(horizontal = 20.dp)) { Secao("Referências (${vm.fontes.size})") } }
        items(vm.fontes) { f ->
            Row(Modifier.fillMaxWidth().toque(f.titulo) {
                com.forja.app.Seguranca.abrirLink(ctx, f.url)
            }.padding(horizontal = 20.dp, vertical = 10.dp), verticalAlignment = Alignment.CenterVertically) {
                Text("${f.ano}", style = Tipo.PequenoForte, color = Cor.Brasa, modifier = Modifier.width(44.dp))
                Text(f.titulo, style = Tipo.Pequeno, color = Cor.Texto2, modifier = Modifier.weight(1f))
                Spacer(Modifier.width(8.dp))
                Icon(Icons.AutoMirrored.Rounded.OpenInNew, null, tint = Cor.Texto3, modifier = Modifier.size(16.dp))
            }
        }
    }
}

const val PRIVACIDADE = "https://kaiqueguimacuper-bit.github.io/teste-3/privacidade.html"
