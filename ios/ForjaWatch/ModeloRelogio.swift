import Foundation
import SwiftUI
import WatchKit
import WatchConnectivity
import HealthKit

/// Estado do app do relógio: sessão em cache, treino ao vivo (sozinho ou espelhado com o iPhone) e conexão.
final class ModeloRelogio: NSObject, ObservableObject, WCSessionDelegate {
    static let shared = ModeloRelogio()

    enum Tela: Equatable { case hoje, treino, concluido }

    @Published var sessao: SessaoRelogio?
    @Published var tela: Tela = .hoje
    @Published var i = 0
    @Published var descansando = false
    @Published var fimEm: Date?
    @Published var inicio = Date()
    @Published var reps = 10
    @Published var kg = 0.0
    @Published var feitas: [Int: SerieRelogio] = [:]
    @Published var espelhado = false        // o iPhone está com o treino aberto
    @Published var iphoneAlcancavel = false
    @Published var registro: RegistroRelogio?
    @Published var encerrando = false

    let treino = GerenteTreino()
    let demo: Bool
    private var tique: Timer?
    private var ultimoBip = -1
    private var bpmDemo: Int?

    var passos: [PassoRelogio] { sessao?.passos ?? [] }
    var passo: PassoRelogio? { passos.indices.contains(i) ? passos[i] : nil }
    var bpm: Int? { treino.bpm ?? bpmDemo }
    var restanteSeg: Int? { fimEm.map { max(0, Int(ceil($0.timeIntervalSinceNow))) } }

    private static let chaveCache = "sessao.cache"
    private static let chaveProcessados = "registros.enviados"

    override init() {
        let args = ProcessInfo.processInfo.arguments
        func arg(_ n: String) -> String? { args.firstIndex(of: "-" + n).flatMap { $0 + 1 < args.count ? args[$0 + 1] : nil } }
        demo = arg("demo") == "1"
        super.init()
        if demo {
            prepararDemo(arg("tela") ?? "hoje")
        } else {
            sessao = RelogioMsg.decodificar(SessaoRelogio.self, UserDefaults.standard.data(forKey: Self.chaveCache))
            if WCSession.isSupported() {
                WCSession.default.delegate = self
                WCSession.default.activate()
            }
        }
        treino.aoLerFC = { [weak self] bpm, kcal in self?.enviar([RelogioMsg.fc: bpm, RelogioMsg.kcal: kcal]) }
    }

    // MARK: ciclo do treino

    /// Começa no relógio (botão Iniciar). Se o iPhone estiver por perto, ele abre o treino e passa a espelhar.
    func iniciar(avisarIPhone: Bool = true) {
        guard let s = sessao, !s.passos.isEmpty else { return }
        i = 0; descansando = false; fimEm = nil; feitas = [:]; inicio = Date(); registro = nil
        preparar()
        tela = .treino
        ligarTique()
        if !demo { Task { await treino.iniciar(tipoSessao: s.tipo) } }
        if avisarIPhone { enviar([RelogioMsg.acao: RelogioMsg.iniciar, "semana": s.semana, "idx": s.idx, "titulo": s.titulo]) }
        WKInterfaceDevice.current().play(.start)
    }

    /// O iPhone abriu o app do relógio pelo app Saúde (startWatchApp) ao iniciar um treino lá.
    func iniciarPeloIPhone(_ config: HKWorkoutConfiguration) {
        if tela == .treino { return }
        if sessao == nil {
            sessao = SessaoRelogio(titulo: "Treino", foco: "", tipo: AtividadeSaude.tipoSessao(config.activityType), minutos: 0, semana: 0, idx: -1, epochDay: 0, ehHoje: true, concluida: false, passos: [])
        }
        if passos.isEmpty {
            // Sem passos (cache vazio): ainda assim mede FC/calorias e grava no Saúde.
            inicio = Date(); tela = .treino; ligarTique()
            Task { await treino.iniciar(tipoSessao: sessao?.tipo ?? "forca") }
        } else {
            iniciar(avisarIPhone: false)
        }
        espelhado = true
    }

    func preparar() {
        guard let p = passo else { return }
        let anterior = feitas.sorted { $0.key < $1.key }.last { passos[$0.key].exId == p.exId }?.value
        reps = anterior?.reps ?? p.repsAlvo
        kg = anterior?.kg ?? p.kg
    }

    func concluirSerie(local: Bool = true) {
        guard let p = passo else { return }
        feitas[i] = SerieRelogio(exId: p.exId, reps: p.porTempo ? 0 : reps, kg: p.temCarga ? kg : 0, seg: p.trabalhoSeg ?? 0)
        if local {
            WKInterfaceDevice.current().play(.success)
            enviar([RelogioMsg.acao: RelogioMsg.concluirSerie, RelogioMsg.indice: i, RelogioMsg.reps: reps, RelogioMsg.kg: kg])
        }
        if i >= passos.count - 1 { if local { encerrar() }; return }
        if p.descanso > 0 {
            descansando = true
            fimEm = Date().addingTimeInterval(Double(p.descanso))
            ultimoBip = -1
        } else { avancar() }
    }

    /// Começa o cronômetro de um exercício por tempo.
    func iniciarTempo() {
        guard let p = passo, let t = p.trabalhoSeg else { return }
        fimEm = Date().addingTimeInterval(Double(t)); ultimoBip = -1
        WKInterfaceDevice.current().play(.start)
    }

    func pularDescanso(local: Bool = true) {
        if local { enviar([RelogioMsg.acao: RelogioMsg.pularDescanso, RelogioMsg.indice: i]) }
        avancar()
    }

    func ajustarDescanso(_ seg: Double) {
        guard descansando, let f = fimEm else { return }
        fimEm = max(Date().addingTimeInterval(1), f.addingTimeInterval(seg))
    }

    private func avancar() {
        descansando = false; fimEm = nil
        guard i < passos.count - 1 else { return }
        i += 1
        preparar()
    }

    private func ligarTique() {
        tique?.invalidate()
        tique = Timer.scheduledTimer(withTimeInterval: 0.25, repeats: true) { [weak self] _ in self?.verificarCronometro() }
    }

    private func verificarCronometro() {
        objectWillChange.send()   // atualiza relógios na tela
        guard tela == .treino, let r = restanteSeg else { return }
        if r > 3 { ultimoBip = -1 }
        if (1...3).contains(r) && ultimoBip != r { ultimoBip = r; WKInterfaceDevice.current().play(.click) }
        if r == 0 && ultimoBip != 0 {
            ultimoBip = 0
            // háptico forte no fim do descanso/tempo (sente no pulso com o braço abaixado)
            WKInterfaceDevice.current().play(.notification)
            if descansando { avancar() } else if passo?.porTempo == true { concluirSerie(local: !espelhado) }
        }
    }

    /// Termina o treino no relógio: fecha a sessão do Saúde e manda o registro ao iPhone.
    func encerrar() {
        guard tela == .treino, !encerrando else { return }
        encerrando = true
        tique?.invalidate()
        let s = sessao
        let series = feitas.sorted { $0.key < $1.key }.map(\.value)
        let ini = inicio
        let estavaEspelhado = espelhado && iphoneAlcancavel
        enviar([RelogioMsg.acao: RelogioMsg.encerrar])
        Task {
            let r = demo ? GerenteTreino.Resumo(fcMedia: 128, fcMax: 161, kcal: 312, salvo: true) : await treino.encerrar(descartar: series.isEmpty)
            let reg = RegistroRelogio(id: UUID().uuidString, titulo: s?.titulo ?? "Treino", tipo: s?.tipo ?? "forca", semana: s?.semana ?? 0, idx: s?.idx ?? -1,
                                      epochDay: s?.epochDay ?? 0, inicio: ini, fim: Date(), series: series,
                                      fcMedia: r.fcMedia, fcMax: r.fcMax, kcal: r.kcal, salvoNoSaude: r.salvo)
            await MainActor.run {
                self.registro = reg
                self.encerrando = false
                self.espelhado = false
                self.tela = .concluido
                if !series.isEmpty, !self.demo { self.entregar(reg, espelhado: estavaEspelhado) }
                if var c = self.sessao, !series.isEmpty, c.ehHoje { c.concluida = true; self.sessao = c; self.guardar(c) }
            }
        }
    }

    func voltarAoInicio() { tela = .hoje; registro = nil }

    /// Com o iPhone com o treino aberto, manda o resumo na hora (ele grava o próprio registro);
    /// sozinho, manda o registro por transferUserInfo, que chega mesmo depois, quando o iPhone voltar.
    private func entregar(_ r: RegistroRelogio, espelhado: Bool) {
        guard WCSession.isSupported(), WCSession.default.activationState == .activated, let d = RelogioMsg.codificar(r) else { return }
        if espelhado && WCSession.default.isReachable {
            WCSession.default.sendMessage([RelogioMsg.registro: d, "espelhado": true], replyHandler: nil) { _ in
                WCSession.default.transferUserInfo([RelogioMsg.registro: d, "espelhado": true])
            }
        } else {
            WCSession.default.transferUserInfo([RelogioMsg.registro: d, "espelhado": false])
        }
    }

    // MARK: WatchConnectivity

    private func enviar(_ msg: [String: Any]) {
        guard !demo, WCSession.isSupported(), WCSession.default.activationState == .activated, WCSession.default.isReachable else { return }
        WCSession.default.sendMessage(msg, replyHandler: nil, errorHandler: nil)
    }

    func pedirSessao() {
        enviar([RelogioMsg.pedirSessao: true])
    }

    private func guardar(_ s: SessaoRelogio) {
        UserDefaults.standard.set(RelogioMsg.codificar(s), forKey: Self.chaveCache)
    }

    func session(_ session: WCSession, activationDidCompleteWith activationState: WCSessionActivationState, error: Error?) {
        let ctx = session.receivedApplicationContext
        let alcance = session.isReachable
        DispatchQueue.main.async {
            self.iphoneAlcancavel = alcance
            self.receberContexto(ctx)
            if alcance { self.pedirSessao() }
        }
    }

    func sessionReachabilityDidChange(_ session: WCSession) {
        let alcance = session.isReachable
        DispatchQueue.main.async {
            self.iphoneAlcancavel = alcance
            if !alcance { self.espelhado = false }
        }
    }

    func session(_ session: WCSession, didReceiveApplicationContext applicationContext: [String: Any]) {
        DispatchQueue.main.async { self.receberContexto(applicationContext) }
    }

    func session(_ session: WCSession, didReceiveMessage message: [String: Any]) {
        DispatchQueue.main.async { self.receberMensagem(message) }
    }

    func session(_ session: WCSession, didReceiveMessage message: [String: Any], replyHandler: @escaping ([String: Any]) -> Void) {
        replyHandler([:])
        DispatchQueue.main.async { self.receberMensagem(message) }
    }

    private func receberContexto(_ ctx: [String: Any]) {
        guard let s = RelogioMsg.decodificar(SessaoRelogio.self, ctx[RelogioMsg.sessao]) else { return }
        // Durante um treino, não troca os passos debaixo do usuário.
        if tela == .treino && sessao?.titulo != s.titulo { return }
        sessao = s
        guardar(s)
    }

    private func receberMensagem(_ m: [String: Any]) {
        if m[RelogioMsg.sessao] != nil { receberContexto(m) }
        guard let e = RelogioMsg.decodificar(EstadoAoVivo.self, m[RelogioMsg.estado]) else { return }
        if !e.ativo {
            // O iPhone terminou (ou descartou) o treino: fecha aqui também.
            if tela == .treino && espelhado { encerrar() }
            return
        }
        if tela != .treino {
            guard let s = sessao, s.titulo == e.titulo, !s.passos.isEmpty else { pedirSessao(); return }
            iniciar(avisarIPhone: false)
        }
        espelhado = true
        inicio = e.inicio
        let mudouPasso = e.i != i
        // Séries concluídas no iPhone entram no registro do relógio também.
        if e.i > i, let p = passo, feitas[i] == nil { feitas[i] = SerieRelogio(exId: p.exId, reps: p.porTempo ? 0 : reps, kg: p.temCarga ? kg : 0, seg: p.trabalhoSeg ?? 0) }
        i = min(max(0, e.i), max(0, passos.count - 1))
        if !descansando && e.descansando { WKInterfaceDevice.current().play(.click) }
        descansando = e.descansando
        fimEm = e.fimEm
        if mudouPasso { preparar() }
    }

    // MARK: demonstração (capturas no simulador)

    private func prepararDemo(_ t: String) {
        func p(_ id: String, _ nome: String, _ s: Int, _ tot: Int, reps: String? = "8–10", seg: Int? = nil, desc: Int = 90, kg: Double = 0, bloco: String = "Principal") -> PassoRelogio {
            PassoRelogio(exId: id, nome: nome, rotulo: tot > 1 ? "Série \(s) de \(tot)" : "Série única", bloco: bloco, serie: s, totalSeries: tot,
                         reps: seg == nil ? reps : nil, trabalhoSeg: seg, descanso: desc, temCarga: kg > 0, kg: kg, repsAlvo: 8)
        }
        var passos: [PassoRelogio] = [p("polichinelo", "Polichinelo", 1, 1, seg: 60, desc: 15, bloco: "Aquecimento")]
        for s in 1...4 { passos.append(p("supino-reto-barra", "Supino reto com barra", s, 4, kg: 42.5)) }
        for s in 1...3 { passos.append(p("crucifixo-halteres", "Crucifixo com halteres", s, 3, reps: "10–12", desc: 60, kg: 14)) }
        for s in 1...3 { passos.append(p("triceps-polia", "Tríceps na polia", s, 3, reps: "12–15", desc: 60, kg: 25)) }
        sessao = SessaoRelogio(titulo: "Treino A · Peito e tríceps", foco: "Empurrar", tipo: "forca", minutos: 55, semana: 3, idx: 0,
                               epochDay: 0, ehHoje: true, concluida: false, passos: passos)
        iphoneAlcancavel = true
        switch t {
        case "treino", "descanso":
            iniciar(avisarIPhone: false)
            i = 2; preparar(); reps = 9
            feitas = [0: SerieRelogio(exId: "polichinelo", reps: 0, kg: 0, seg: 60), 1: SerieRelogio(exId: "supino-reto-barra", reps: 10, kg: 42.5, seg: 0)]
            inicio = Date().addingTimeInterval(-754)
            bpmDemo = 134
            treino.kcal = 96
            espelhado = true
            if t == "descanso" { descansando = true; fimEm = Date().addingTimeInterval(75) }
        case "concluido":
            tela = .concluido
            registro = RegistroRelogio(id: "demo", titulo: sessao!.titulo, tipo: "forca", semana: 3, idx: 0, epochDay: 0,
                                       inicio: Date().addingTimeInterval(-3260), fim: Date(), series: [], fcMedia: 128, fcMax: 161, kcal: 312, salvoNoSaude: true)
        default: break
        }
    }
}
