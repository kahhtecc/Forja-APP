package com.forja.app.relogio

import android.content.Context
import android.content.Intent
import android.net.Uri
import androidx.health.connect.client.HealthConnectClient
import androidx.health.connect.client.permission.HealthPermission
import androidx.health.connect.client.records.ExerciseSessionRecord
import androidx.health.connect.client.records.HeartRateRecord
import androidx.health.connect.client.records.metadata.Metadata
import androidx.health.connect.client.request.AggregateRequest
import androidx.health.connect.client.time.TimeRangeFilter
import com.forja.app.core.Registro
import java.time.Instant
import java.time.ZoneId

/**
 * Health Connect: grava cada treino concluído como sessão de exercício e lê a frequência cardíaca
 * registrada por qualquer relógio que sincronize com ele (Wear OS, Galaxy Watch, Fitbit, Garmin, Xiaomi, Amazfit…).
 */
object Saude {
    const val PACOTE = "com.google.android.apps.healthdata"
    val ESCRITA = HealthPermission.getWritePermission(ExerciseSessionRecord::class)
    val LEITURA_FC = HealthPermission.getReadPermission(HeartRateRecord::class)
    val PERMISSOES = setOf(ESCRITA, LEITURA_FC)

    fun status(ctx: Context): Int = runCatching { HealthConnectClient.getSdkStatus(ctx, PACOTE) }.getOrDefault(HealthConnectClient.SDK_UNAVAILABLE)
    fun disponivel(ctx: Context) = status(ctx) == HealthConnectClient.SDK_AVAILABLE
    fun precisaInstalar(ctx: Context) = status(ctx) == HealthConnectClient.SDK_UNAVAILABLE_PROVIDER_UPDATE_REQUIRED

    private fun cliente(ctx: Context): HealthConnectClient? =
        if (disponivel(ctx)) runCatching { HealthConnectClient.getOrCreate(ctx, PACOTE) }.getOrNull() else null

    suspend fun concedidas(ctx: Context): Set<String> =
        cliente(ctx)?.let { c -> runCatching { c.permissionController.getGrantedPermissions() }.getOrNull() } ?: emptySet()

    suspend fun conectado(ctx: Context) = concedidas(ctx).isNotEmpty()

    /** Abre a Play Store no Health Connect (Android 13 ou anterior, ou versão desatualizada). */
    fun instalar(ctx: Context) {
        val uri = Uri.parse("market://details?id=$PACOTE&url=healthconnect%3A%2F%2Fonboarding")
        runCatching { ctx.startActivity(Intent(Intent.ACTION_VIEW, uri).setPackage("com.android.vending").addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)) }
            .onFailure { runCatching { ctx.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse("https://play.google.com/store/apps/details?id=$PACOTE")).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)) } }
    }

    fun tipoExercicio(tipo: String): Int = when (tipo) {
        "corrida" -> ExerciseSessionRecord.EXERCISE_TYPE_RUNNING
        "bike" -> ExerciseSessionRecord.EXERCISE_TYPE_BIKING
        "hiit" -> ExerciseSessionRecord.EXERCISE_TYPE_HIGH_INTENSITY_INTERVAL_TRAINING
        "luta" -> ExerciseSessionRecord.EXERCISE_TYPE_MARTIAL_ARTS
        "mobilidade" -> ExerciseSessionRecord.EXERCISE_TYPE_STRETCHING
        "cardio", "atleta" -> ExerciseSessionRecord.EXERCISE_TYPE_OTHER_WORKOUT
        else -> ExerciseSessionRecord.EXERCISE_TYPE_STRENGTH_TRAINING
    }

    fun intervalo(reg: Registro): Pair<Instant, Instant> {
        val fim = Instant.ofEpochMilli(if (reg.fimMs > 0) reg.fimMs else System.currentTimeMillis())
        return fim.minusSeconds(reg.duracaoSeg.coerceAtLeast(60).toLong()) to fim
    }

    /** Grava o treino como ExerciseSessionRecord. Retorna true se gravou. */
    suspend fun gravarTreino(ctx: Context, reg: Registro): Boolean {
        val c = cliente(ctx) ?: return false
        if (ESCRITA !in concedidas(ctx)) return false
        val (ini, fim) = intervalo(reg)
        val zona = ZoneId.systemDefault().rules
        return runCatching {
            c.insertRecords(listOf(ExerciseSessionRecord(
                startTime = ini, startZoneOffset = zona.getOffset(ini),
                endTime = fim, endZoneOffset = zona.getOffset(fim),
                metadata = Metadata.manualEntry(),
                exerciseType = tipoExercicio(reg.tipo),
                title = reg.titulo.ifBlank { "Treino Forja" },
                notes = reg.nota.ifBlank { null },
            )))
            true
        }.getOrDefault(false)
    }

    /** FC média e máxima registradas no Health Connect no intervalo (null se não houver). */
    suspend fun fc(ctx: Context, ini: Instant, fim: Instant): Pair<Int, Int>? {
        val c = cliente(ctx) ?: return null
        if (LEITURA_FC !in concedidas(ctx)) return null
        return runCatching {
            val r = c.aggregate(AggregateRequest(setOf(HeartRateRecord.BPM_AVG, HeartRateRecord.BPM_MAX), TimeRangeFilter.between(ini, fim)))
            val med = r[HeartRateRecord.BPM_AVG] ?: return@runCatching null
            med.toInt() to (r[HeartRateRecord.BPM_MAX] ?: med).toInt()
        }.getOrNull()
    }
}
