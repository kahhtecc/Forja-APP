import Foundation
import HealthKit

/// Sessão de treino do HealthKit no relógio: mantém o app ativo com a tela abaixada,
/// mede FC e calorias ao vivo e grava o treino no app Saúde ao terminar.
final class GerenteTreino: NSObject, ObservableObject, HKWorkoutSessionDelegate, HKLiveWorkoutBuilderDelegate {
    let loja = HKHealthStore()
    private var sessao: HKWorkoutSession?
    private var builder: HKLiveWorkoutBuilder?

    @Published var bpm: Int?
    @Published var kcal: Double = 0
    @Published var rodando = false
    /// Chamado a cada nova leitura de FC (para repassar ao iPhone).
    var aoLerFC: ((Int, Int) -> Void)?

    static let bpmUnidade = HKUnit.count().unitDivided(by: .minute())

    var disponivel: Bool { HKHealthStore.isHealthDataAvailable() }

    func autorizar() async -> Bool {
        guard disponivel else { return false }
        let gravar: Set<HKSampleType> = [HKObjectType.workoutType(), HKQuantityType(.activeEnergyBurned), HKQuantityType(.heartRate)]
        let ler: Set<HKObjectType> = [HKObjectType.workoutType(), HKQuantityType(.activeEnergyBurned), HKQuantityType(.heartRate)]
        do { try await loja.requestAuthorization(toShare: gravar, read: ler); return true } catch { return false }
    }

    func iniciar(tipoSessao: String) async {
        guard disponivel, sessao == nil else { return }
        _ = await autorizar()
        let config = AtividadeSaude.configuracao(tipoSessao)
        do {
            let s = try HKWorkoutSession(healthStore: loja, configuration: config)
            let b = s.associatedWorkoutBuilder()
            b.dataSource = HKLiveWorkoutDataSource(healthStore: loja, workoutConfiguration: config)
            s.delegate = self
            b.delegate = self
            sessao = s; builder = b
            let agora = Date()
            s.startActivity(with: agora)
            try await b.beginCollection(at: agora)
            await MainActor.run { self.rodando = true }
        } catch {
            sessao = nil; builder = nil
        }
    }

    struct Resumo { var fcMedia: Int?; var fcMax: Int?; var kcal: Int?; var salvo: Bool }

    /// Encerra a sessão e grava o treino no app Saúde.
    func encerrar(descartar: Bool = false) async -> Resumo {
        guard let s = sessao, let b = builder else { return Resumo(fcMedia: nil, fcMax: nil, kcal: kcal > 0 ? Int(kcal) : nil, salvo: false) }
        s.end()
        _ = try? await b.endCollection(at: Date())
        let fc = b.statistics(for: HKQuantityType(.heartRate))
        let media = fc?.averageQuantity()?.doubleValue(for: Self.bpmUnidade)
        let maximo = fc?.maximumQuantity()?.doubleValue(for: Self.bpmUnidade)
        let energia = b.statistics(for: HKQuantityType(.activeEnergyBurned))?.sumQuantity()?.doubleValue(for: .kilocalorie())
        var salvo = false
        if descartar { b.discardWorkout() } else { let w = try? await b.finishWorkout(); salvo = w != nil }
        sessao = nil; builder = nil
        await MainActor.run { self.rodando = false; self.bpm = nil }
        return Resumo(fcMedia: media.map { Int($0.rounded()) }, fcMax: maximo.map { Int($0.rounded()) }, kcal: energia.map { Int($0.rounded()) }, salvo: salvo)
    }

    // MARK: delegados (chegam fora da fila principal)

    func workoutSession(_ workoutSession: HKWorkoutSession, didChangeTo toState: HKWorkoutSessionState, from fromState: HKWorkoutSessionState, date: Date) {}
    func workoutSession(_ workoutSession: HKWorkoutSession, didFailWithError error: Error) {}
    func workoutBuilderDidCollectEvent(_ workoutBuilder: HKLiveWorkoutBuilder) {}

    func workoutBuilder(_ workoutBuilder: HKLiveWorkoutBuilder, didCollectDataOf collectedTypes: Set<HKSampleType>) {
        var novoBpm: Int?
        var novaKcal: Double?
        for tipo in collectedTypes {
            guard let q = tipo as? HKQuantityType, let st = workoutBuilder.statistics(for: q) else { continue }
            if q == HKQuantityType(.heartRate), let v = st.mostRecentQuantity()?.doubleValue(for: Self.bpmUnidade) { novoBpm = Int(v.rounded()) }
            if q == HKQuantityType(.activeEnergyBurned), let v = st.sumQuantity()?.doubleValue(for: .kilocalorie()) { novaKcal = v }
        }
        DispatchQueue.main.async {
            if let b = novoBpm { self.bpm = b }
            if let k = novaKcal { self.kcal = k }
            if novoBpm != nil || novaKcal != nil, let b = self.bpm { self.aoLerFC?(b, Int(self.kcal)) }
        }
    }
}
