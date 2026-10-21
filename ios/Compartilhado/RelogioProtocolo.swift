import Foundation
import HealthKit

// Compilado nos dois alvos (iPhone e Apple Watch): o formato do que viaja pelo WatchConnectivity.
// O relógio não carrega o catálogo nem o gerador: recebe a sessão já "achatada" em passos.

/// Um passo do treino (uma série ou rodada), igual ao `Passo` do núcleo, só com o que o relógio mostra.
struct PassoRelogio: Codable, Equatable {
    var exId: String
    var nome: String
    var rotulo: String          // "Série 2 de 4", "Volta 1 de 3"
    var bloco: String           // "Aquecimento", "Principal"…
    var serie: Int
    var totalSeries: Int
    var reps: String?           // "8–10"
    var trabalhoSeg: Int?       // por tempo
    var descanso: Int           // descanso depois do passo (s)
    var temCarga: Bool
    var kg: Double              // carga sugerida (última usada)
    var repsAlvo: Int

    var porTempo: Bool { trabalhoSeg != nil }
    var prescricao: String {
        if let t = trabalhoSeg { return RelogioFormato.tempo(t) }
        return "\(reps ?? "\(repsAlvo)") reps"
    }
}

/// Sessão de treino enviada pelo iPhone (fica em cache no relógio para treinar sem o iPhone).
struct SessaoRelogio: Codable, Equatable {
    var titulo: String
    var foco: String
    var tipo: String            // forca, corrida, bike, luta, hiit, mobilidade, cardio, atleta
    var minutos: Int
    var semana: Int
    var idx: Int                // índice da sessão na semana (-1 = rotina avulsa)
    var epochDay: Int           // dia a que a sessão se refere
    var ehHoje: Bool
    var concluida: Bool
    var passos: [PassoRelogio]
}

/// Estado do treino ao vivo, espelhado entre os dois aparelhos.
struct EstadoAoVivo: Codable, Equatable {
    var titulo: String
    var i: Int
    var descansando: Bool
    var fimEm: Date?            // fim do descanso ou do exercício por tempo
    var inicio: Date
    var ativo: Bool
}

struct SerieRelogio: Codable, Equatable {
    var exId: String
    var reps: Int
    var kg: Double
    var seg: Int
}

/// Treino feito no relógio (com ou sem o iPhone por perto).
struct RegistroRelogio: Codable, Equatable {
    var id: String
    var titulo: String
    var tipo: String
    var semana: Int
    var idx: Int
    var epochDay: Int
    var inicio: Date
    var fim: Date
    var series: [SerieRelogio]
    var fcMedia: Int?
    var fcMax: Int?
    var kcal: Int?
    var salvoNoSaude: Bool

    var duracaoSeg: Int { max(0, Int(fim.timeIntervalSince(inicio))) }
}

/// Chaves das mensagens.
enum RelogioMsg {
    static let sessao = "sessao"        // applicationContext: SessaoRelogio (JSON)
    static let estado = "estado"        // sendMessage: EstadoAoVivo (JSON)
    static let acao = "acao"            // sendMessage: String (concluir-serie, pular-descanso, iniciar, encerrar)
    static let indice = "i"
    static let reps = "reps"
    static let kg = "kg"
    static let fc = "fc"                // sendMessage: Int (bpm ao vivo do relógio)
    static let kcal = "kcal"
    static let registro = "registro"    // transferUserInfo / sendMessage: RegistroRelogio (JSON)
    static let pedirSessao = "pedir-sessao"

    static let concluirSerie = "concluir-serie"
    static let pularDescanso = "pular-descanso"
    static let iniciar = "iniciar"
    static let encerrar = "encerrar"

    static func codificar<T: Encodable>(_ v: T) -> Data? {
        let e = JSONEncoder(); e.dateEncodingStrategy = .secondsSince1970
        return try? e.encode(v)
    }
    static func decodificar<T: Decodable>(_ t: T.Type, _ d: Any?) -> T? {
        guard let d = d as? Data else { return nil }
        let j = JSONDecoder(); j.dateDecodingStrategy = .secondsSince1970
        return try? j.decode(t, from: d)
    }
}

enum RelogioFormato {
    static func tempo(_ seg: Int) -> String {
        if seg >= 3600 { return String(format: "%dh%02d", seg / 3600, (seg % 3600) / 60) }
        if seg >= 60 && seg % 60 == 0 { return "\(seg / 60) min" }
        if seg >= 60 { return String(format: "%d:%02d", seg / 60, seg % 60) }
        return "\(seg) s"
    }
    static func relogio(_ s: Int) -> String { s >= 60 ? String(format: "%d:%02d", s / 60, s % 60) : "\(s)" }
    static func duracao(_ d: Int) -> String { d >= 3600 ? String(format: "%d:%02d:%02d", d / 3600, d % 3600 / 60, d % 60) : String(format: "%d:%02d", d / 60, d % 60) }
    static func kg(_ v: Double) -> String { v == v.rounded() ? String(Int(v)) : String(format: "%.1f", v).replacingOccurrences(of: ".", with: ",") }
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
    /// O caminho inverso, para o relógio aberto pelo iPhone (startWatchApp).
    static func tipoSessao(_ a: HKWorkoutActivityType) -> String {
        switch a {
        case .running: return "corrida"
        case .cycling: return "bike"
        case .martialArts: return "luta"
        case .highIntensityIntervalTraining: return "hiit"
        case .flexibility: return "mobilidade"
        case .mixedCardio: return "cardio"
        case .functionalStrengthTraining: return "atleta"
        default: return "forca"
        }
    }
}
