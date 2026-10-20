import Foundation

// Porte fiel de app/src/main/java/com/forja/app/core/Modelo.kt — o teste de paridade garante o mesmo resultado.

public enum Modalidade: String, CaseIterable, Codable, Sendable {
    case casaCorpo = "casa_corpo", casaElastico = "casa_elastico", academia, corrida, bike, luta, atleta, hiit, hibrido, mobilidade, longevidade

    public var id: String { rawValue }
    public var nome: String {
        switch self {
        case .casaCorpo: return "Em casa · peso do corpo"
        case .casaElastico: return "Em casa · elásticos"
        case .academia: return "Academia · musculação"
        case .corrida: return "Corrida"
        case .bike: return "Bike · ciclismo"
        case .luta: return "Lutadores"
        case .atleta: return "Atletas · performance"
        case .hiit: return "HIIT & funcional"
        case .hibrido: return "Híbrido · força + corrida"
        case .mobilidade: return "Mobilidade & alongamento"
        case .longevidade: return "50+ · força e equilíbrio"
        }
    }
    public var curto: String {
        switch self {
        case .casaCorpo: return "Casa"
        case .casaElastico: return "Elásticos"
        case .academia: return "Musculação"
        case .corrida: return "Corrida"
        case .bike: return "Bike"
        case .luta: return "Luta"
        case .atleta: return "Atleta"
        case .hiit: return "HIIT"
        case .hibrido: return "Híbrido"
        case .mobilidade: return "Mobilidade"
        case .longevidade: return "50+"
        }
    }
    /// Mesma ordem de declaração do Kotlin (usada em cálculos que dependem do índice).
    public static let ordem: [Modalidade] = [.casaCorpo, .casaElastico, .academia, .corrida, .bike, .luta, .atleta, .hiit, .hibrido, .mobilidade, .longevidade]
    public static func de(_ id: String?) -> Modalidade? { id.flatMap { Modalidade(rawValue: $0) } }
}

public enum Objetivo: String, CaseIterable, Codable, Sendable {
    case massa, emagrecer, saude, forca, resistencia, performance
    public var id: String { rawValue }
    public var nome: String {
        switch self {
        case .massa: return "Ganhar massa muscular"
        case .emagrecer: return "Perder gordura"
        case .saude: return "Saúde e vida ativa"
        case .forca: return "Ficar mais forte"
        case .resistencia: return "Resistência e fôlego"
        case .performance: return "Performance no esporte"
        }
    }
    public static func de(_ id: String?) -> Objetivo? { id.flatMap { Objetivo(rawValue: $0) } }
}

public enum Nivel: String, CaseIterable, Codable, Sendable {
    case iniciante, intermediario, avancado
    public var id: String { rawValue }
    public var nome: String {
        switch self {
        case .iniciante: return "Iniciante"
        case .intermediario: return "Intermediário"
        case .avancado: return "Avançado"
        }
    }
    public static func de(_ id: String?) -> Nivel? { id.flatMap { Nivel(rawValue: $0) } }
}

public struct Video: Equatable, Sendable {
    public let id: String, titulo: String, canal: String, idioma: String
}

public struct Exercicio: Equatable, Identifiable, Sendable {
    public let id: String
    public let nome: String
    public let equip: [String]
    public let grupo: String
    public let tipo: String
    public let nivel: Int
    public let dicas: [String]
    public let busca: String
    public let padroes: [String]
    public let evitar: [String]
    public let temImagem: Bool
    public let video: Video?

    /// Exercícios medidos em tempo (e não repetições).
    public var porTempo: Bool {
        ["cardio", "mobilidade", "tecnica"].contains(tipo) ||
            ["prancha", "prancha-lateral", "isometria-pescoco", "farmer-walk", "equilibrio-unipodal", "monster-walk"].contains(id)
    }
}

public enum TipoBloco: String, Codable, Sendable { case AQUECIMENTO, PRINCIPAL, CIRCUITO, INTERVALADO, DESAQUECIMENTO }

public struct Item: Equatable, Sendable {
    public var exId: String
    public var series: Int
    public var reps: String? = nil
    public var trabalhoSeg: Int? = nil
    public var descansoSeg: Int = 60
    public var intensidade: String? = nil
    public var nota: String? = nil

    public init(_ exId: String, _ series: Int, reps: String? = nil, trabalhoSeg: Int? = nil, descansoSeg: Int = 60, intensidade: String? = nil, nota: String? = nil) {
        self.exId = exId; self.series = series; self.reps = reps; self.trabalhoSeg = trabalhoSeg
        self.descansoSeg = descansoSeg; self.intensidade = intensidade; self.nota = nota
    }
}

public struct Bloco: Equatable, Sendable {
    public var nome: String
    public var tipo: TipoBloco
    public var itens: [Item]
    public var voltas: Int = 1
    public var nota: String? = nil
    public init(_ nome: String, _ tipo: TipoBloco, _ itens: [Item], voltas: Int = 1, nota: String? = nil) {
        self.nome = nome; self.tipo = tipo; self.itens = itens; self.voltas = voltas; self.nota = nota
    }
}

public struct Sessao: Equatable, Sendable {
    public var titulo: String
    public var foco: String
    /// forca, corrida, bike, luta, hiit, mobilidade, cardio, atleta
    public var tipo: String
    public var minutos: Int
    public var blocos: [Bloco]
    /// 1 = segunda ... 7 = domingo
    public var diaSemana: Int
    public init(_ titulo: String, _ foco: String, _ tipo: String, _ minutos: Int, _ blocos: [Bloco], _ diaSemana: Int) {
        self.titulo = titulo; self.foco = foco; self.tipo = tipo; self.minutos = minutos; self.blocos = blocos; self.diaSemana = diaSemana
    }
}

public struct Semana: Equatable, Sendable {
    public var numero: Int, fase: String, nota: String, sessoes: [Sessao]
}

public struct Plano: Equatable, Sendable {
    public var nome: String
    public var resumo: String
    public var modalidade: Modalidade
    public var objetivo: Objetivo
    public var nivel: Nivel
    public var semanas: [Semana]
    public var dicas: [String]
    public var alertas: [String]
    public var metaSemanal: String
}

public struct SerieFeita: Equatable, Codable, Sendable {
    public var exId: String, reps: Int, kg: Double, seg: Int = 0
    public init(_ exId: String, _ reps: Int, _ kg: Double, seg: Int = 0) { self.exId = exId; self.reps = reps; self.kg = kg; self.seg = seg }
}

public struct Registro: Equatable, Codable, Identifiable, Sendable {
    public var id: String { "\(epochDay)-\(semana)-\(sessaoIdx)-\(titulo)-\(duracaoSeg)" }
    public var epochDay: Int
    public var semana: Int
    public var sessaoIdx: Int
    public var titulo: String
    public var tipo: String
    public var duracaoSeg: Int
    public var series: [SerieFeita]
    public var esforco: Int
    public var nota: String
    public init(epochDay: Int, semana: Int, sessaoIdx: Int, titulo: String, tipo: String, duracaoSeg: Int, series: [SerieFeita], esforco: Int, nota: String) {
        self.epochDay = epochDay; self.semana = semana; self.sessaoIdx = sessaoIdx; self.titulo = titulo; self.tipo = tipo
        self.duracaoSeg = duracaoSeg; self.series = series; self.esforco = esforco; self.nota = nota
    }
}

// Utilitários com a mesma semântica do Kotlin
@inline(__always) func mod(_ a: Int, _ n: Int) -> Int { ((a % n) + n) % n }
/// Kotlin roundToInt (Math.round: metade para cima).
@inline(__always) func arred(_ x: Double) -> Int { Int((x + 0.5).rounded(.down)) }
