import Foundation
import ActivityKit
import AppIntents

// Compilado no app e na extensão de widgets: o formato da Live Activity do treino ao vivo
// e as ações dos botões dela (rodam no processo do app).

@available(iOS 16.1, *)
struct TreinoAtividade: ActivityAttributes {
    public struct ContentState: Codable, Hashable {
        var exercicio: String
        var rotulo: String          // "Série 2 de 4"
        var prescricao: String      // "10 reps · 40 kg", "45 s"
        var indice: Int
        var total: Int
        var descansando: Bool
        var fimEm: Date?            // fim do descanso (ou do exercício por tempo)
        var porTempo: Bool
        var proximo: String?
        var bpm: Int?
        var concluido: Bool
    }
    var titulo: String
    var tipo: String
    var inicio: Date
    var cor: UInt32
}

extension Notification.Name {
    /// Ação vinda da Live Activity (object = "concluir" | "pular").
    static let forjaAcaoTreino = Notification.Name("forja.acaoTreino")
}

enum AcaoTreino {
    static let concluir = "concluir"
    static let pular = "pular"
}

@available(iOS 17.0, *)
struct ConcluirSerieIntent: LiveActivityIntent {
    static var title: LocalizedStringResource = "Concluir série"
    static var description = IntentDescription("Marca a série atual do treino como feita.")
    init() {}
    func perform() async throws -> some IntentResult {
        await MainActor.run { NotificationCenter.default.post(name: .forjaAcaoTreino, object: AcaoTreino.concluir) }
        return .result()
    }
}

@available(iOS 17.0, *)
struct PularDescansoIntent: LiveActivityIntent {
    static var title: LocalizedStringResource = "Pular descanso"
    static var description = IntentDescription("Encerra o descanso e vai para a próxima série.")
    init() {}
    func perform() async throws -> some IntentResult {
        await MainActor.run { NotificationCenter.default.post(name: .forjaAcaoTreino, object: AcaoTreino.pular) }
        return .result()
    }
}
