package com.forja.app.relogio

import android.Manifest
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.content.pm.ServiceInfo
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import androidx.core.app.ServiceCompat
import androidx.core.content.ContextCompat
import androidx.wear.ongoing.OngoingActivity
import androidx.wear.ongoing.Status
import com.forja.app.MainActivity
import com.forja.app.R
import com.forja.app.core.Progresso
import com.forja.app.core.Roteiro
import com.forja.app.ui.EstadoTreino
import com.forja.app.ui.relogio
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.launch

/**
 * Treino ao vivo fora da tela: notificação contínua (serviço em primeiro plano) com exercício, série, cronômetro
 * do descanso, FC e botões "Concluir série" / "Pular descanso" / "Encerrar". Ela aparece como atividade em
 * andamento no Wear OS (Ongoing Activity) e uma cópia "espelho" vai para o relógio pareado (Wear OS, Galaxy Watch e
 * relógios que espelham notificações: Garmin, Amazfit, Xiaomi…). No fim do descanso, alerta com vibração forte.
 */
object TreinoAoVivo {
    const val ACAO_CONCLUIR = "concluir-serie"
    const val ACAO_PULAR = "pular-descanso"
    const val ACAO_ENCERRAR = "encerrar"
    const val ACAO_FIM = "fim-cronometro"

    const val CANAL_AO_VIVO = "treino_ao_vivo"
    const val CANAL_RELOGIO = "treino_relogio"
    const val CANAL_ALERTA = "treino_alerta"
    const val ID_AO_VIVO = 4101
    private const val ID_RELOGIO = 4102
    private const val ID_ALERTA = 4103
    private const val GRUPO = "forja_treino"
    val VIBRACAO = longArrayOf(0, 450, 160, 450, 160, 900)

    /** Ações vindas da notificação/relógio, consumidas pela tela do treino. */
    val acoes = MutableSharedFlow<String>(extraBufferCapacity = 16)
    @Volatile var appVisivel = false

    private val h = Handler(Looper.getMainLooper())
    private val escopo = CoroutineScope(SupervisorJob() + Dispatchers.Main)
    private var fcJob: Job? = null
    private var app: Context? = null
    private var t: EstadoTreino? = null
    private var titulo = "Treino"
    private var ultimoRender = 0L
    var ligado = false
        private set

    /** Permissões pedidas no início do treino (notificações e atividade física, exigida pelo serviço "health"). */
    fun permissoesFaltando(ctx: Context): Array<String> = buildList {
        if (Build.VERSION.SDK_INT >= 33) add(Manifest.permission.POST_NOTIFICATIONS)
        if (Build.VERSION.SDK_INT >= 29) add(Manifest.permission.ACTIVITY_RECOGNITION)
    }.filter { ContextCompat.checkSelfPermission(ctx, it) != PackageManager.PERMISSION_GRANTED }.toTypedArray()

    /** O serviço "health" do Android 14+ exige atividade física (ou sensores corporais) concedida. */
    fun podeServicoSaude(ctx: Context) = Build.VERSION.SDK_INT < 34 ||
        ContextCompat.checkSelfPermission(ctx, Manifest.permission.ACTIVITY_RECOGNITION) == PackageManager.PERMISSION_GRANTED ||
        ContextCompat.checkSelfPermission(ctx, Manifest.permission.BODY_SENSORS) == PackageManager.PERMISSION_GRANTED

    fun iniciar(ctx: Context, e: EstadoTreino, tituloSessao: String) {
        val c = ctx.applicationContext
        app = c; t = e; titulo = tituloSessao; ligado = true
        criarCanais(c)
        fcJob?.cancel()
        fcJob = escopo.launch {
            FcAoVivo.bpm.collect { if (System.currentTimeMillis() - ultimoRender > 5000) renderizar() }
        }
        if (podeServicoSaude(c)) runCatching { ContextCompat.startForegroundService(c, Intent(c, ServicoTreino::class.java)) }
        atualizar()
    }

    fun atualizar() {
        if (!ligado) return
        renderizar()
        agendar()
    }

    fun parar(ctx: Context) {
        if (!ligado && t == null) return
        ligado = false; t = null
        fcJob?.cancel(); fcJob = null
        h.removeCallbacksAndMessages(null)
        val nm = NotificationManagerCompat.from(ctx)
        nm.cancel(ID_RELOGIO); nm.cancel(ID_AO_VIVO)
        runCatching { ctx.stopService(Intent(ctx, ServicoTreino::class.java)) }
    }

    // ------------------------------------------------------------- conteúdo

    private class Painel(val exercicio: String, val linha: String, val descansando: Boolean, val fimMs: Long?, val pausado: Boolean, val porTempo: Boolean, val ultimo: Boolean)

    private fun painel(e: EstadoTreino): Painel {
        val p = e.passo
        val prox = e.passos.getOrNull(e.i + 1)
        val carga = if (!p.porTempo && e.kg > 0) " · ${Progresso.fmtKg(e.kg)} kg" else ""
        val alvo = if (p.porTempo) Roteiro.formatarTempo(p.item.trabalhoSeg ?: 0) else "${p.item.reps ?: e.reps} reps$carga"
        return if (e.descansando) Painel(
            "Descanso", prox?.let { "A seguir: ${it.ex.nome} · ${it.rotulo}" } ?: "Última série feita", true, e.fimMs, e.pausadoRestante != null, false, false,
        ) else Painel(p.ex.nome, "${p.rotulo} · $alvo", false, e.fimMs, e.pausadoRestante != null, p.porTempo, e.i == e.passos.lastIndex)
    }

    private fun intent(c: Context, acao: String, req: Int) = PendingIntent.getBroadcast(
        c, req, Intent(c, AcaoTreinoReceiver::class.java).setAction(acao), PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
    )

    private fun abrirApp(c: Context) = PendingIntent.getActivity(
        c, 40, Intent(c, MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_REORDER_TO_FRONT),
        PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
    )

    private fun base(c: Context, canal: String, pn: Painel): NotificationCompat.Builder {
        val bpm = FcAoVivo.atual()
        val b = NotificationCompat.Builder(c, canal)
            .setSmallIcon(R.drawable.ic_notificacao)
            .setColor(0xFFFF5B22.toInt())
            .setContentTitle(pn.exercicio)
            .setContentText(pn.linha)
            .setSubText(listOfNotNull(titulo, bpm?.let { "♥ $it bpm" }).joinToString(" · "))
            .setCategory("workout")
            .setVisibility(NotificationCompat.VISIBILITY_PUBLIC)
            .setOnlyAlertOnce(true)
            .setSilent(true)
            .setContentIntent(abrirApp(c))
            .setGroup(GRUPO)
        val f = pn.fimMs
        if (f != null && !pn.pausado && f > System.currentTimeMillis()) {
            b.setUsesChronometer(true).setChronometerCountDown(true).setWhen(f).setShowWhen(true)
        } else b.setShowWhen(false)
        if (pn.descansando) b.addAction(R.drawable.ic_notificacao, "Pular descanso", intent(c, ACAO_PULAR, 41))
        else b.addAction(R.drawable.ic_notificacao, if (pn.porTempo && f == null) "Iniciar" else if (pn.ultimo) "Finalizar" else "Concluir série", intent(c, ACAO_CONCLUIR, 42))
        b.addAction(R.drawable.ic_notificacao, "Encerrar", intent(c, ACAO_ENCERRAR, 43))
        return b
    }

    /** Notificação do serviço em primeiro plano (também usada como Ongoing Activity no Wear OS). */
    fun notificacao(ctx: Context): Notification? {
        val c = ctx.applicationContext
        val e = t ?: return null
        criarCanais(c)
        val pn = painel(e)
        val espelho = PrefsRelogio.mostrar(c)
        val b = base(c, CANAL_AO_VIVO, pn).setOngoing(true).setGroupSummary(espelho).setLocalOnly(espelho)
            .setForegroundServiceBehavior(NotificationCompat.FOREGROUND_SERVICE_IMMEDIATE)
        runCatching {
            val f = pn.fimMs
            val status = if (f != null && !pn.pausado && f > System.currentTimeMillis())
                Status.Builder().addTemplate("#ex# · #t#").addPart("ex", Status.TextPart(pn.exercicio)).addPart("t", Status.TimerPart(f)).build()
            else Status.Builder().addTemplate("#ex#").addPart("ex", Status.TextPart(pn.exercicio)).build()
            OngoingActivity.Builder(c, ID_AO_VIVO, b)
                .setStaticIcon(R.drawable.ic_notificacao)
                .setTouchIntent(abrirApp(c))
                .setTitle(titulo)
                .setCategory("workout")
                .setStatus(status)
                .build().apply(c)
        }
        return b.build()
    }

    private fun renderizar() {
        val c = app ?: return
        val e = t ?: return
        ultimoRender = System.currentTimeMillis()
        val nm = NotificationManagerCompat.from(c)
        if (!nm.areNotificationsEnabled()) return
        runCatching {
            notificacao(c)?.let { nm.notify(ID_AO_VIVO, it) }
            // Notificações contínuas não são enviadas ao relógio: esta cópia (não contínua, silenciosa) é a que aparece no pulso.
            if (PrefsRelogio.mostrar(c)) nm.notify(ID_RELOGIO, base(c, CANAL_RELOGIO, painel(e)).setLocalOnly(false).setTimeoutAfter(3 * 3600_000L).build())
            else nm.cancel(ID_RELOGIO)
        }
    }

    private val fimCronometro = Runnable {
        val e = t
        if (e != null && ligado) {
            alertar(e)
            acoes.tryEmit(ACAO_FIM)
            h.postDelayed({ atualizar() }, 400)
        }
    }

    private fun agendar() {
        h.removeCallbacks(fimCronometro)
        val e = t ?: return
        val f = e.fimMs ?: return
        if (e.pausadoRestante != null) return
        h.postDelayed(fimCronometro, (f - System.currentTimeMillis()).coerceAtLeast(0))
    }

    /** Alerta de alta prioridade com vibração forte (chega também ao relógio). */
    private fun alertar(e: EstadoTreino) {
        val c = app ?: return
        if (appVisivel && !PrefsRelogio.mostrar(c)) return
        val nm = NotificationManagerCompat.from(c)
        if (!nm.areNotificationsEnabled()) return
        val prox = if (e.descansando) e.passos.getOrNull(e.i + 1) else null
        val (tt, tx) = if (e.descansando) "Descanso acabou! 🔥" to (prox?.let { "${it.ex.nome} · ${it.rotulo}" } ?: "Bora!")
        else "Tempo! ${relogio(e.passo.item.trabalhoSeg ?: 0)} concluídos" to e.passo.ex.nome
        val n = NotificationCompat.Builder(c, CANAL_ALERTA)
            .setSmallIcon(R.drawable.ic_notificacao)
            .setColor(0xFFFF5B22.toInt())
            .setContentTitle(tt).setContentText(tx)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setCategory(NotificationCompat.CATEGORY_REMINDER)
            .setVibrate(VIBRACAO)
            .setDefaults(NotificationCompat.DEFAULT_SOUND)
            .setAutoCancel(true)
            .setTimeoutAfter(25_000)
            .setContentIntent(abrirApp(c))
            .build()
        runCatching { nm.notify(ID_ALERTA, n) }
    }

    fun criarCanais(c: Context) {
        if (Build.VERSION.SDK_INT < 26) return
        val nm = c.getSystemService(NotificationManager::class.java) ?: return
        if (nm.getNotificationChannel(CANAL_ALERTA) != null) return
        nm.createNotificationChannel(NotificationChannel(CANAL_AO_VIVO, "Treino ao vivo", NotificationManager.IMPORTANCE_LOW).apply {
            description = "Exercício atual, série, descanso e botões durante o treino"
            setShowBadge(false)
        })
        nm.createNotificationChannel(NotificationChannel(CANAL_RELOGIO, "Treino no relógio", NotificationManager.IMPORTANCE_LOW).apply {
            description = "Cópia do treino ao vivo para o relógio pareado"
            setShowBadge(false)
        })
        nm.createNotificationChannel(NotificationChannel(CANAL_ALERTA, "Fim do descanso", NotificationManager.IMPORTANCE_HIGH).apply {
            description = "Aviso com vibração forte quando o descanso ou o tempo acaba"
            enableVibration(true)
            vibrationPattern = VIBRACAO
        })
    }
}

/** Serviço em primeiro plano que mantém o treino vivo com a tela apagada (tipo "health" no Android 14+). */
class ServicoTreino : Service() {
    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val n = TreinoAoVivo.notificacao(this) ?: NotificationCompat.Builder(this, TreinoAoVivo.CANAL_AO_VIVO)
            .setSmallIcon(R.drawable.ic_notificacao).setContentTitle("Treino em andamento").build()
        val tipo = if (Build.VERSION.SDK_INT >= 34) ServiceInfo.FOREGROUND_SERVICE_TYPE_HEALTH else 0
        try {
            ServiceCompat.startForeground(this, TreinoAoVivo.ID_AO_VIVO, n, tipo)
        } catch (_: Exception) {
            // sem permissão para o tipo "health": a notificação segue como comum enquanto o app estiver aberto
        }
        if (!TreinoAoVivo.ligado) stopSelf()
        return START_NOT_STICKY
    }
}

/** Botões da notificação (no celular ou no relógio). */
class AcaoTreinoReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val a = intent.action ?: return
        if (!TreinoAoVivo.ligado) {
            TreinoAoVivo.parar(context)
            return
        }
        TreinoAoVivo.acoes.tryEmit(a)
    }
}
