import Foundation
import HealthKit

/// Integração com o app Saúde: grava os treinos e lê a frequência cardíaca do intervalo do treino.
/// Assim aparecem os dados do Apple Watch e de qualquer relógio/anel que sincroniza com o Saúde
/// (Garmin, Polar, Withings, Oura, Amazfit, Fitbit via apps de terceiros…).
@MainActor
final class Saude: ObservableObject {
    static let shared = Saude()
    private let loja = HKHealthStore()
    @Published private(set) var conectado = false

    init() {
        // O status de gravação diz se o usuário liberou o acesso (o de leitura o iOS não revela).
        conectado = HKHealthStore.isHealthDataAvailable() && loja.authorizationStatus(for: HKObjectType.workoutType()) == .sharingAuthorized
    }

    var disponivel: Bool { HKHealthStore.isHealthDataAvailable() }
    static let bpm = HKUnit.count().unitDivided(by: .minute())

    private var gravar: Set<HKSampleType> { [HKObjectType.workoutType(), HKQuantityType(.activeEnergyBurned)] }
    private var ler: Set<HKObjectType> { [HKObjectType.workoutType(), HKQuantityType(.heartRate), HKQuantityType(.activeEnergyBurned)] }

    /// Pede acesso (o iOS só mostra a folha de permissões uma vez; depois, muda-se em Ajustes > Saúde).
    @discardableResult
    func conectar() async -> Bool {
        guard disponivel else { return false }
        do {
            try await loja.requestAuthorization(toShare: gravar, read: ler)
            // A leitura nunca revela se foi negada; a gravação sim.
            let ok = loja.authorizationStatus(for: HKObjectType.workoutType()) == .sharingAuthorized
            conectado = ok
            UserDefaults.standard.set(ok, forKey: "saude.on")
            return ok
        } catch { return false }
    }

    func desconectar() { conectado = false; UserDefaults.standard.set(false, forKey: "saude.on") }

    struct FCResumo: Equatable { var media: Int; var max: Int; var fonte: String }

    /// FC média e máxima no intervalo (de qualquer fonte que gravou no Saúde).
    func frequencia(de inicio: Date, ate fim: Date) async -> FCResumo? {
        guard disponivel, conectado else { return nil }
        let tipo = HKQuantityType(.heartRate)
        let pred = HKQuery.predicateForSamples(withStart: inicio, end: fim, options: [])
        let estat: HKStatistics? = await withCheckedContinuation { c in
            let q = HKStatisticsQuery(quantityType: tipo, quantitySamplePredicate: pred, options: [.discreteAverage, .discreteMax]) { _, s, _ in c.resume(returning: s) }
            loja.execute(q)
        }
        guard let st = estat, let m = st.averageQuantity()?.doubleValue(for: Self.bpm), let x = st.maximumQuantity()?.doubleValue(for: Self.bpm) else { return nil }
        let fontes = await nomesDasFontes(tipo, pred)
        return FCResumo(media: Int(m.rounded()), max: Int(x.rounded()), fonte: fontes)
    }

    private func nomesDasFontes(_ tipo: HKSampleType, _ pred: NSPredicate) async -> String {
        await withCheckedContinuation { c in
            let q = HKSampleQuery(sampleType: tipo, predicate: pred, limit: 50, sortDescriptors: nil) { _, amostras, _ in
                let nomes = Set((amostras ?? []).map { $0.sourceRevision.source.name })
                c.resume(returning: nomes.sorted().joined(separator: ", "))
            }
            loja.execute(q)
        }
    }

    /// Já existe um treino no Saúde cobrindo esse intervalo (gravado pelo Apple Watch, Garmin…)?
    func existeTreino(de inicio: Date, ate fim: Date) async -> Bool {
        let pred = HKQuery.predicateForSamples(withStart: inicio.addingTimeInterval(-300), end: fim.addingTimeInterval(300), options: [])
        return await withCheckedContinuation { c in
            let q = HKSampleQuery(sampleType: HKObjectType.workoutType(), predicate: pred, limit: 1, sortDescriptors: nil) { _, a, _ in c.resume(returning: !(a ?? []).isEmpty) }
            loja.execute(q)
        }
    }

    /// Grava o treino no Saúde (se nenhum relógio já gravou um treino no mesmo horário).
    func salvarTreino(tipoSessao: String, titulo: String, inicio: Date, fim: Date, kcal: Double?) async {
        guard disponivel, conectado, fim > inicio else { return }
        if await existeTreino(de: inicio, ate: fim) { return }
        let builder = HKWorkoutBuilder(healthStore: loja, configuration: AtividadeSaude.configuracao(tipoSessao), device: .local())
        do {
            try await builder.beginCollection(at: inicio)
            if let k = kcal, k > 0 {
                let a = HKQuantitySample(type: HKQuantityType(.activeEnergyBurned), quantity: HKQuantity(unit: .kilocalorie(), doubleValue: k), start: inicio, end: fim)
                try await builder.addSamples([a])
            }
            try await builder.addMetadata([HKMetadataKeyWorkoutBrandName: "Forja", "ForjaTitulo": titulo])
            try await builder.endCollection(at: fim)
            _ = try await builder.finishWorkout()
        } catch {}
    }
}

/// Tipo de atividade do app Saúde conforme o tipo da sessão.
enum AtividadeSaude {
    static func tipo(_ tipoSessao: String) -> HKWorkoutActivityType {
        switch tipoSessao {
        case "corrida": return .running
        case "bike": return .cycling
        case "luta": return .martialArts
        case "hiit": return .highIntensityIntervalTraining
        case "mobilidade": return .flexibility
        case "cardio": return .mixedCardio
        case "atleta": return .functionalStrengthTraining
        default: return .traditionalStrengthTraining
        }
    }
    static func configuracao(_ tipoSessao: String) -> HKWorkoutConfiguration {
        let c = HKWorkoutConfiguration()
        c.activityType = tipo(tipoSessao)
        c.locationType = ["corrida", "bike"].contains(tipoSessao) ? .outdoor : .indoor
        return c
    }
    /// Estimativa simples de kcal ativas (MET × peso × horas) quando nenhum sensor mediu.
    static func kcalEstimada(_ tipoSessao: String, pesoKg: Double, segundos: Int, fcMedia: Int?) -> Double {
        let met: Double
        switch tipoSessao {
        case "corrida": met = 9.0
        case "bike": met = 7.5
        case "luta", "hiit": met = 8.0
        case "mobilidade": met = 2.5
        case "cardio": met = 7.0
        default: met = 5.0
        }
        return max(0, (met - 1) * pesoKg * Double(segundos) / 3600)
    }
}
