import Foundation
import CoreBluetooth

/// Monitor cardíaco Bluetooth padrão (Heart Rate Service 0x180D, medição 0x2A37):
/// cintas Polar/Garmin/Wahoo/Coospo, braçadeiras e relógios em modo "transmitir FC" (Garmin, Polar, Coros, Suunto, Amazfit…).
final class MonitorCardiaco: NSObject, ObservableObject, CBCentralManagerDelegate, CBPeripheralDelegate {
    static let shared = MonitorCardiaco()
    static let servico = CBUUID(string: "180D")
    static let medicao = CBUUID(string: "2A37")
    private static let chave = "ble.fc.uuid"
    private static let chaveNome = "ble.fc.nome"

    struct Encontrado: Identifiable, Equatable { let id: UUID; let nome: String; var rssi: Int }

    @Published var encontrados: [Encontrado] = []
    @Published var escaneando = false
    @Published var bpm: Int?
    @Published var conectadoA: String?
    @Published var estado = "Desligado"
    @Published var bluetoothLigado = false

    private var central: CBCentralManager?
    private var perifericos: [UUID: CBPeripheral] = [:]
    private var atual: CBPeripheral?
    private var querEscanear = false

    var lembrado: String? { UserDefaults.standard.string(forKey: Self.chaveNome) }
    private var lembradoId: UUID? { UserDefaults.standard.string(forKey: Self.chave).flatMap(UUID.init) }

    /// Só cria o gerenciador (e o pedido de permissão do Bluetooth) quando o usuário usa a função.
    func ligar() {
        if central == nil { central = CBCentralManager(delegate: self, queue: nil) }
    }

    /// Ao abrir o app: reconecta sozinho ao aparelho lembrado.
    func reconectarSeLembrado() {
        if lembradoId != nil { ligar() }
    }

    func escanear() {
        querEscanear = true
        ligar()
        guard let c = central, c.state == .poweredOn else { return }
        encontrados = []
        escaneando = true
        c.scanForPeripherals(withServices: [Self.servico], options: [CBCentralManagerScanOptionAllowDuplicatesKey: false])
        // Também lista os que já estão conectados ao iPhone por outro app.
        for p in c.retrieveConnectedPeripherals(withServices: [Self.servico]) { adicionar(p, rssi: -50) }
        DispatchQueue.main.asyncAfter(deadline: .now() + 20) { [weak self] in self?.pararEscaneamento() }
    }

    func pararEscaneamento() {
        querEscanear = false
        central?.stopScan()
        escaneando = false
    }

    func conectar(_ id: UUID) {
        guard let c = central, let p = perifericos[id] else { return }
        pararEscaneamento()
        if let a = atual, a.identifier != id { c.cancelPeripheralConnection(a) }
        atual = p
        p.delegate = self
        estado = "Conectando…"
        UserDefaults.standard.set(id.uuidString, forKey: Self.chave)
        UserDefaults.standard.set(p.name ?? "Monitor cardíaco", forKey: Self.chaveNome)
        c.connect(p, options: nil)
    }

    func esquecer() {
        if let a = atual { central?.cancelPeripheralConnection(a) }
        atual = nil; bpm = nil; conectadoA = nil
        UserDefaults.standard.removeObject(forKey: Self.chave)
        UserDefaults.standard.removeObject(forKey: Self.chaveNome)
        estado = bluetoothLigado ? "Pronto" : estado
        objectWillChange.send()
    }

    private func adicionar(_ p: CBPeripheral, rssi: Int) {
        perifericos[p.identifier] = p
        let nome = p.name ?? "Monitor cardíaco"
        if let k = encontrados.firstIndex(where: { $0.id == p.identifier }) { encontrados[k].rssi = rssi }
        else { encontrados.append(Encontrado(id: p.identifier, nome: nome, rssi: rssi)) }
        encontrados.sort { $0.rssi > $1.rssi }
    }

    /// Só para as capturas de tela do modo demonstração.
    func preencherDemo() {
        encontrados = [Encontrado(id: UUID(), nome: "Polar H10 8A3F21", rssi: -48), Encontrado(id: UUID(), nome: "Forerunner 265", rssi: -71)]
        conectadoA = "Polar H10 8A3F21"; bpm = 72; estado = "Conectado"
    }

    // MARK: CBCentralManagerDelegate

    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        bluetoothLigado = central.state == .poweredOn
        switch central.state {
        case .poweredOn:
            estado = "Pronto"
            if querEscanear { escanear() }
            if atual == nil, let id = lembradoId, let p = central.retrievePeripherals(withIdentifiers: [id]).first {
                perifericos[id] = p; atual = p; p.delegate = self
                estado = "Procurando \(p.name ?? lembrado ?? "monitor")…"
                central.connect(p, options: nil)   // sem prazo: conecta quando o aparelho aparecer
            }
        case .poweredOff: estado = "Bluetooth desligado"
        case .unauthorized: estado = "Sem permissão do Bluetooth (Ajustes > Forja)"
        case .unsupported: estado = "Bluetooth indisponível neste aparelho"
        default: estado = "Aguardando o Bluetooth"
        }
    }

    func centralManager(_ central: CBCentralManager, didDiscover peripheral: CBPeripheral, advertisementData: [String: Any], rssi RSSI: NSNumber) {
        adicionar(peripheral, rssi: RSSI.intValue)
    }

    func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
        conectadoA = peripheral.name ?? lembrado ?? "Monitor cardíaco"
        estado = "Conectado"
        peripheral.discoverServices([Self.servico])
    }

    func centralManager(_ central: CBCentralManager, didFailToConnect peripheral: CBPeripheral, error: Error?) {
        estado = "Não conectou. Tente de novo."
    }

    func centralManager(_ central: CBCentralManager, didDisconnectPeripheral peripheral: CBPeripheral, error: Error?) {
        bpm = nil; conectadoA = nil
        guard peripheral.identifier == lembradoId else { estado = "Pronto"; return }
        // Saiu do alcance: tenta de novo sozinho.
        estado = "Desconectado; reconectando…"
        central.connect(peripheral, options: nil)
    }

    // MARK: CBPeripheralDelegate

    func peripheral(_ peripheral: CBPeripheral, didDiscoverServices error: Error?) {
        for s in peripheral.services ?? [] where s.uuid == Self.servico { peripheral.discoverCharacteristics([Self.medicao], for: s) }
    }

    func peripheral(_ peripheral: CBPeripheral, didDiscoverCharacteristicsFor service: CBService, error: Error?) {
        for c in service.characteristics ?? [] where c.uuid == Self.medicao { peripheral.setNotifyValue(true, for: c) }
    }

    func peripheral(_ peripheral: CBPeripheral, didUpdateValueFor characteristic: CBCharacteristic, error: Error?) {
        guard characteristic.uuid == Self.medicao, let d = characteristic.value, let v = Self.lerBpm(d) else { return }
        bpm = v
        Sensores.shared.registrar(bpm: v, fonte: conectadoA ?? "Bluetooth")
    }

    /// Formato da medição (Bluetooth SIG): bit 0 das flags = FC em 16 bits.
    static func lerBpm(_ d: Data) -> Int? {
        let b = [UInt8](d)
        guard b.count >= 2 else { return nil }
        if b[0] & 0x01 == 0 { return Int(b[1]) }
        guard b.count >= 3 else { return nil }
        return Int(UInt16(b[1]) | UInt16(b[2]) << 8)
    }
}

/// Junta as leituras de FC ao vivo (cinta/relógio Bluetooth) e guarda as amostras do treino atual.
@MainActor
final class Sensores: ObservableObject {
    static let shared = Sensores()
    @Published private(set) var bpm: Int?
    @Published private(set) var fonte: String?
    private(set) var amostras: [(Date, Int)] = []
    private var ultimaLeitura = Date.distantPast
    var gravando = false

    nonisolated func registrar(bpm: Int, fonte: String) {
        Task { @MainActor in
            self.bpm = bpm; self.fonte = fonte; self.ultimaLeitura = Date()
            if self.gravando { self.amostras.append((Date(), bpm)) }
        }
    }

    /// FC atual, se a última leitura é recente.
    var bpmAtual: Int? { Date().timeIntervalSince(ultimaLeitura) < 10 ? bpm : nil }

    private(set) var inicioTreino: Date?
    private(set) var fimTreino: Date?
    private(set) var tipoTreino = "forca"

    func comecarTreino() { amostras = []; gravando = true; inicioTreino = Date(); fimTreino = nil }
    func marcarIntervalo(inicio: Date, fim: Date, tipo: String) { inicioTreino = inicio; fimTreino = fim; tipoTreino = tipo }
    func terminarTreino() { gravando = false }

    var resumo: Saude.FCResumo? {
        guard !amostras.isEmpty else { return nil }
        let v = amostras.map(\.1)
        return Saude.FCResumo(media: v.reduce(0, +) / v.count, max: v.max() ?? 0, fonte: fonte ?? "Bluetooth")
    }

    /// Só para as capturas de tela do modo demonstração.
    func simular(_ bpm: Int, _ fonte: String) { self.bpm = bpm; self.fonte = fonte; ultimaLeitura = Date.distantFuture }
}
