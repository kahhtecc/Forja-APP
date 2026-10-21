package com.forja.app.relogio

import android.Manifest
import android.annotation.SuppressLint
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothGatt
import android.bluetooth.BluetoothGattCallback
import android.bluetooth.BluetoothGattCharacteristic
import android.bluetooth.BluetoothGattDescriptor
import android.bluetooth.BluetoothManager
import android.bluetooth.BluetoothProfile
import android.bluetooth.le.ScanCallback
import android.bluetooth.le.ScanFilter
import android.bluetooth.le.ScanResult
import android.bluetooth.le.ScanSettings
import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import android.os.Handler
import android.os.Looper
import android.os.ParcelUuid
import androidx.core.content.ContextCompat
import kotlinx.coroutines.flow.MutableStateFlow
import java.util.UUID

/**
 * Monitor cardíaco por Bluetooth LE no perfil padrão (serviço 0x180D, característica 0x2A37):
 * cintas Polar/Garmin/Wahoo e relógios com "transmitir frequência cardíaca" (Garmin, Polar, Coros, Amazfit, Suunto…).
 */
@SuppressLint("MissingPermission")
object MonitorBle {
    private val SERVICO_FC: UUID = UUID.fromString("0000180d-0000-1000-8000-00805f9b34fb")
    private val MEDIDA_FC: UUID = UUID.fromString("00002a37-0000-1000-8000-00805f9b34fb")
    private val CCCD: UUID = UUID.fromString("00002902-0000-1000-8000-00805f9b34fb")

    data class Dispositivo(val endereco: String, val nome: String, val rssi: Int)

    val encontrados = MutableStateFlow<List<Dispositivo>>(emptyList())
    val escaneando = MutableStateFlow(false)
    /** Nome do dispositivo conectado (null = desconectado). */
    val conectado = MutableStateFlow<String?>(null)
    val conectando = MutableStateFlow(false)

    private val h = Handler(Looper.getMainLooper())
    private var gatt: BluetoothGatt? = null
    private var nomeAtual: String? = null
    private var querConectado = false
    private var tentativas = 0
    private var app: Context? = null

    fun permissoes(): Array<String> =
        if (Build.VERSION.SDK_INT >= 31) arrayOf(Manifest.permission.BLUETOOTH_SCAN, Manifest.permission.BLUETOOTH_CONNECT)
        else arrayOf(Manifest.permission.ACCESS_FINE_LOCATION)

    fun temPermissao(ctx: Context) = permissoes().all { ContextCompat.checkSelfPermission(ctx, it) == PackageManager.PERMISSION_GRANTED }

    fun adaptador(ctx: Context): BluetoothAdapter? = runCatching { ctx.getSystemService(BluetoothManager::class.java)?.adapter }.getOrNull()

    fun disponivel(ctx: Context) = ctx.packageManager.hasSystemFeature(PackageManager.FEATURE_BLUETOOTH_LE) && adaptador(ctx) != null

    fun ligado(ctx: Context) = runCatching { adaptador(ctx)?.isEnabled == true }.getOrDefault(false)

    // ------------------------------------------------------------- busca

    private val busca = object : ScanCallback() {
        override fun onScanResult(callbackType: Int, result: ScanResult) {
            val d = result.device ?: return
            val nome = runCatching { result.scanRecord?.deviceName ?: d.name }.getOrNull()?.takeIf { it.isNotBlank() } ?: "Monitor ${d.address.takeLast(5)}"
            val novo = Dispositivo(d.address, nome, result.rssi)
            encontrados.value = (encontrados.value.filter { it.endereco != d.address } + novo).sortedByDescending { it.rssi }
        }

        override fun onScanFailed(errorCode: Int) { escaneando.value = false }
    }

    fun escanear(ctx: Context) {
        if (!temPermissao(ctx) || escaneando.value) return
        val sc = runCatching { adaptador(ctx)?.bluetoothLeScanner }.getOrNull() ?: return
        encontrados.value = emptyList()
        val filtros = listOf(ScanFilter.Builder().setServiceUuid(ParcelUuid(SERVICO_FC)).build())
        val ajustes = ScanSettings.Builder().setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY).build()
        runCatching { sc.startScan(filtros, ajustes, busca); escaneando.value = true }
        h.postDelayed({ pararBusca(ctx) }, 20_000)
    }

    fun pararBusca(ctx: Context) {
        if (!escaneando.value) return
        escaneando.value = false
        runCatching { adaptador(ctx)?.bluetoothLeScanner?.stopScan(busca) }
    }

    // ------------------------------------------------------------- conexão

    fun conectar(ctx: Context, endereco: String, nome: String) {
        if (!temPermissao(ctx)) return
        PrefsRelogio.setBle(ctx, endereco, nome)
        app = ctx.applicationContext
        querConectado = true
        tentativas = 0
        abrir(endereco, nome)
    }

    /** Conecta ao dispositivo lembrado (início do treino), se houver permissão e Bluetooth ligado. */
    fun conectarLembrado(ctx: Context) {
        val (end, nome) = PrefsRelogio.ble(ctx) ?: return
        if (!temPermissao(ctx) || !ligado(ctx) || gatt != null) return
        app = ctx.applicationContext
        querConectado = true
        tentativas = 0
        abrir(end, nome)
    }

    private fun abrir(endereco: String, nome: String) {
        val c = app ?: return
        val ad = adaptador(c) ?: return
        runCatching { gatt?.close() }
        gatt = null
        nomeAtual = nome
        conectando.value = true
        gatt = runCatching {
            val d = ad.getRemoteDevice(endereco)
            d.connectGatt(c, false, retorno, BluetoothDevice.TRANSPORT_LE)
        }.getOrNull()
        if (gatt == null) conectando.value = false
    }

    fun desconectar() {
        querConectado = false
        h.removeCallbacksAndMessages(null)
        runCatching { gatt?.disconnect(); gatt?.close() }
        gatt = null
        conectado.value = null
        conectando.value = false
    }

    fun esquecer(ctx: Context) {
        desconectar()
        PrefsRelogio.setBle(ctx, null, null)
    }

    private val retorno = object : BluetoothGattCallback() {
        override fun onConnectionStateChange(g: BluetoothGatt, status: Int, newState: Int) {
            if (newState == BluetoothProfile.STATE_CONNECTED) {
                tentativas = 0
                h.post { runCatching { g.discoverServices() } }
            } else if (newState == BluetoothProfile.STATE_DISCONNECTED) {
                conectado.value = null
                conectando.value = false
                runCatching { g.close() }
                if (gatt === g) gatt = null
                // reconecta sozinho algumas vezes (cinta saiu do alcance por um instante)
                val lembrado = app?.let { PrefsRelogio.ble(it) }
                if (querConectado && lembrado != null && tentativas < 5) {
                    tentativas++
                    h.postDelayed({ if (querConectado && gatt == null) abrir(lembrado.first, lembrado.second) }, 3000L * tentativas)
                }
            }
        }

        override fun onServicesDiscovered(g: BluetoothGatt, status: Int) {
            val ch = g.getService(SERVICO_FC)?.getCharacteristic(MEDIDA_FC)
            if (ch == null) { conectando.value = false; return }
            runCatching {
                g.setCharacteristicNotification(ch, true)
                val d = ch.getDescriptor(CCCD)
                if (d != null) {
                    if (Build.VERSION.SDK_INT >= 33) g.writeDescriptor(d, BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE)
                    else {
                        @Suppress("DEPRECATION")
                        d.value = BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE
                        @Suppress("DEPRECATION")
                        g.writeDescriptor(d)
                    }
                }
            }
            conectando.value = false
            conectado.value = nomeAtual ?: "Monitor cardíaco"
        }

        override fun onCharacteristicChanged(g: BluetoothGatt, ch: BluetoothGattCharacteristic, value: ByteArray) {
            if (ch.uuid == MEDIDA_FC) ler(value)?.let { FcAoVivo.receber(it, nomeAtual ?: "Bluetooth") }
        }

        @Deprecated("API < 33")
        override fun onCharacteristicChanged(g: BluetoothGatt, ch: BluetoothGattCharacteristic) {
            @Suppress("DEPRECATION")
            if (ch.uuid == MEDIDA_FC) ch.value?.let { v -> ler(v)?.let { FcAoVivo.receber(it, nomeAtual ?: "Bluetooth") } }
        }
    }

    /** Heart Rate Measurement: bit 0 das flags = valor em 16 bits; senão 8 bits. */
    fun ler(v: ByteArray): Int? {
        if (v.size < 2) return null
        val flags = v[0].toInt()
        return if (flags and 1 == 0) v[1].toInt() and 0xFF
        else if (v.size >= 3) (v[1].toInt() and 0xFF) or ((v[2].toInt() and 0xFF) shl 8) else null
    }
}
