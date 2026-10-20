package com.forja.app

import android.annotation.SuppressLint
import android.app.AlarmManager
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import androidx.core.content.ContextCompat
import com.forja.app.core.Catalogo
import com.forja.app.core.Loja
import com.forja.app.core.Progresso
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.ZoneId

/** Lembrete diário nos dias de treino (alarme inexato, sem dependências extras). */
object Lembretes {
    private const val CANAL = "treinos"
    private const val PREFS = "forja_lembrete"

    fun ativo(ctx: Context) = ctx.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getBoolean("on", false)
    fun hora(ctx: Context) = ctx.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getInt("hora", 18)

    fun configurar(ctx: Context, ligado: Boolean, hora: Int) {
        ctx.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit().putBoolean("on", ligado).putInt("hora", hora).apply()
        agendar(ctx)
    }

    private fun pendente(ctx: Context) = PendingIntent.getBroadcast(
        ctx, 1, Intent(ctx, LembreteReceiver::class.java), PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
    )

    fun agendar(ctx: Context) {
        val am = ctx.getSystemService(AlarmManager::class.java) ?: return
        am.cancel(pendente(ctx))
        if (!ativo(ctx)) return
        var alvo = LocalDate.now().atTime(hora(ctx), 0)
        if (alvo.isBefore(LocalDateTime.now())) alvo = alvo.plusDays(1)
        val ms = alvo.atZone(ZoneId.systemDefault()).toInstant().toEpochMilli()
        am.setInexactRepeating(AlarmManager.RTC_WAKEUP, ms, AlarmManager.INTERVAL_DAY, pendente(ctx))
    }

    @SuppressLint("MissingPermission")
    fun notificar(ctx: Context) {
        if (!ativo(ctx)) return
        if (Build.VERSION.SDK_INT >= 33 && ContextCompat.checkSelfPermission(ctx, android.Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) return
        val cat = Catalogo.deJson(ctx.assets.open("exercises.json").bufferedReader().use { it.readText() })
        val loja = Loja(cat, Preferencias(ctx, "forja")) { LocalDate.now().toEpochDay() }
        val (idx, ses) = loja.sessaoDeHoje() ?: return
        if (idx in Progresso.feitas(loja.estado.value.registros, loja.semanaAtual())) return
        val nm = ctx.getSystemService(NotificationManager::class.java)
        nm?.createNotificationChannel(NotificationChannel(CANAL, "Lembretes de treino", NotificationManager.IMPORTANCE_DEFAULT))
        val abrir = PendingIntent.getActivity(ctx, 2, Intent(ctx, MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK), PendingIntent.FLAG_IMMUTABLE)
        val n = NotificationCompat.Builder(ctx, CANAL)
            .setSmallIcon(R.drawable.ic_notificacao)
            .setContentTitle("Hoje: ${ses.titulo}")
            .setContentText("${ses.minutos} min · ${ses.foco}. Bora forjar!")
            .setContentIntent(abrir).setAutoCancel(true)
            .build()
        runCatching { NotificationManagerCompat.from(ctx).notify(10, n) }
    }
}

class LembreteReceiver : BroadcastReceiver() {
    override fun onReceive(ctx: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED) Lembretes.agendar(ctx) else Lembretes.notificar(ctx)
    }
}
