import Foundation

public typealias Respostas = [String: [String]]

public extension Dictionary where Key == String, Value == [String] {
    func um(_ id: String) -> String? { self[id]?.first }
    func num(_ id: String) -> Int? { um(id).flatMap { Int($0) } }
}

public enum TipoPergunta: String, Sendable { case UNICA, MULTIPLA, NUMERO, DIAS, TEXTO }

public struct Opcao: Sendable { public let valor: String, titulo: String, descricao: String? }

public struct Pergunta: Identifiable, @unchecked Sendable {
    public let id: String
    public let secao: String
    public let titulo: String
    public let subtitulo: String?
    public let tipo: TipoPergunta
    public var opcoes: [Opcao] = []
    public var min = 0, max = 0, passo = 1
    public var padrao: Int? = nil
    public var unidade = ""
    public var opcional = false
    public var exclusiva: String? = nil
    public var visivel: (Respostas) -> Bool = { _ in true }

    public func respondida(_ r: Respostas) -> Bool {
        let v = r[id] ?? []
        switch tipo {
        case .DIAS: return v.count == (r.num("dias") ?? 0)
        case .MULTIPLA: return opcional || !v.isEmpty
        case .TEXTO: return opcional || !(v.first ?? "").trimmingCharacters(in: .whitespaces).isEmpty
        default: return opcional || !v.isEmpty
        }
    }
}

private func o(_ v: String, _ t: String, _ d: String? = nil) -> Opcao { Opcao(valor: v, titulo: t, descricao: d) }

public enum Questionario {
    static func mod(_ r: Respostas) -> Modalidade? { Modalidade.de(r.um("modalidade")) }
    static func emCasa(_ r: Respostas) -> Bool {
        switch mod(r) {
        case .casaCorpo, .casaElastico: return true
        case .luta, .atleta, .hibrido, .hiit, .longevidade: return r.um("local") == "casa"
        default: return false
        }
    }
    static func corre(_ r: Respostas) -> Bool { mod(r) == .corrida || (mod(r) == .hibrido && r.um("hibrido_cardio") != "bike") }

    public static let DIAS_NOMES = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]

    public static let perguntas: [Pergunta] = {
        var l: [Pergunta] = []
        l.append(Pergunta(id: "nome", secao: "Você", titulo: "Como podemos te chamar?", subtitulo: "Opcional — só para personalizar o app.", tipo: .TEXTO, opcional: true))
        l.append(Pergunta(id: "modalidade", secao: "Treino", titulo: "Que tipo de treino você quer fazer?", subtitulo: "Você pode trocar quando quiser refazendo o questionário.", tipo: .UNICA, opcoes: [
            o("academia", "Academia · musculação", "Máquinas, barras e halteres"),
            o("casa_corpo", "Em casa · peso do corpo", "Sem equipamento ou com o que tiver"),
            o("casa_elastico", "Em casa · elásticos", "Faixas e tubos elásticos"),
            o("corrida", "Corrida", "Do primeiro trote à maratona"),
            o("bike", "Bike · ciclismo", "Rolo, estrada, MTB ou ergométrica"),
            o("luta", "Lutadores", "Boxe, muay thai, MMA, jiu-jitsu, judô…"),
            o("atleta", "Atletas · performance", "Força, potência, velocidade e prevenção"),
            o("hiit", "HIIT & funcional", "Circuitos intensos e curtos"),
            o("hibrido", "Híbrido", "Força + corrida ou bike na mesma semana"),
            o("mobilidade", "Mobilidade & alongamento", "Postura, flexibilidade e recuperação"),
            o("longevidade", "50+ · força e equilíbrio", "Autonomia, ossos e equilíbrio"),
        ]))
        l.append(Pergunta(id: "objetivo", secao: "Treino", titulo: "Qual é o seu objetivo principal?", subtitulo: nil, tipo: .UNICA, opcoes: [
            o("massa", "Ganhar massa muscular", "Hipertrofia e definição"),
            o("emagrecer", "Perder gordura", "Gasto calórico e manutenção da massa magra"),
            o("saude", "Saúde e vida ativa", "Disposição, coração e articulações"),
            o("forca", "Ficar mais forte", "Mais carga nos movimentos básicos"),
            o("resistencia", "Resistência e fôlego", "Aguentar mais tempo com menos cansaço"),
            o("performance", "Performance", "Render mais no seu esporte ou prova"),
        ], visivel: { mod($0) != .mobilidade }))
        l.append(Pergunta(id: "experiencia", secao: "Treino", titulo: "Há quanto tempo você treina?", subtitulo: "Seja sincero: isso define volume e intensidade.", tipo: .UNICA, opcoes: [
            o("iniciante", "Estou começando", "Nunca treinei ou estou parado há mais de 6 meses"),
            o("intermediario", "Já treino", "Com regularidade, de 6 meses a 2 anos"),
            o("avancado", "Treino há bastante tempo", "Mais de 2 anos e domino a técnica"),
        ]))
        l.append(Pergunta(id: "dias", secao: "Agenda", titulo: "Quantos dias por semana você vai treinar?", subtitulo: "Consistência vale mais que volume.", tipo: .NUMERO, min: 2, max: 6, padrao: 3, unidade: "dias"))
        l.append(Pergunta(id: "dias_semana", secao: "Agenda", titulo: "Em quais dias?", subtitulo: "Escolha exatamente a quantidade de dias que você marcou.", tipo: .DIAS))
        l.append(Pergunta(id: "minutos", secao: "Agenda", titulo: "Quanto tempo por sessão?", subtitulo: "Incluindo aquecimento e alongamento.", tipo: .UNICA,
                          opcoes: ["20", "30", "45", "60", "75", "90"].map { o($0, "\($0) min") }))
        l.append(Pergunta(id: "local", secao: "Equipamento", titulo: "Onde você vai fazer a parte de força?", subtitulo: nil, tipo: .UNICA,
                          opcoes: [o("academia", "Academia", "Acesso a máquinas, barras e halteres"), o("casa", "Em casa", "Com o que eu tiver disponível")],
                          visivel: { [.luta, .atleta, .hibrido, .hiit, .longevidade].contains(mod($0) ?? .academia) && mod($0) != nil }))
        l.append(Pergunta(id: "equipamentos", secao: "Equipamento", titulo: "O que você tem em casa?", subtitulo: "Marque tudo o que tiver. Nada? Tudo bem, o peso do corpo resolve.", tipo: .MULTIPLA, opcoes: [
            o("halter", "Halteres"), o("kettlebell", "Kettlebell"), o("elastico", "Elásticos / mini-band"),
            o("barra_fixa", "Barra fixa"), o("banco", "Banco ou cadeira firme"), o("corda", "Corda de pular"),
            o("bola", "Medicine ball"), o("rolo", "Rolo de liberação"), o("saco", "Saco de pancada"),
            o("bike", "Bike ergométrica / rolo"), o("esteira", "Esteira"),
        ], opcional: true, visivel: { emCasa($0) }))
        l.append(Pergunta(id: "hibrido_cardio", secao: "Específico", titulo: "Qual cardio entra no seu híbrido?", subtitulo: nil, tipo: .UNICA,
                          opcoes: [o("corrida", "Corrida"), o("bike", "Bike")], visivel: { mod($0) == .hibrido }))
        l.append(Pergunta(id: "corrida_meta", secao: "Corrida", titulo: "Qual é a sua meta na corrida?", subtitulo: nil, tipo: .UNICA, opcoes: [
            o("comecar", "Começar a correr", "Sair do zero até 30 minutos contínuos"),
            o("5k", "5 km"), o("10k", "10 km"), o("21k", "Meia maratona · 21 km"), o("42k", "Maratona · 42 km"),
            o("ritmo", "Ficar mais rápido", "Sem prova específica"),
            o("saude", "Correr por saúde", "Constância e prazer"),
        ], visivel: { corre($0) }))
        l.append(Pergunta(id: "corrida_continuo", secao: "Corrida", titulo: "Hoje você consegue correr 20 minutos sem parar?", subtitulo: nil, tipo: .UNICA,
                          opcoes: [o("sim", "Sim"), o("nao", "Ainda não")], visivel: { corre($0) && $0.um("corrida_meta") != "comecar" }))
        l.append(Pergunta(id: "corrida_5k", secao: "Corrida", titulo: "Seu tempo atual nos 5 km", subtitulo: "Opcional. Usamos para calcular seus ritmos de treino.", tipo: .NUMERO,
                          min: 15, max: 60, padrao: 32, unidade: "min", opcional: true,
                          visivel: { corre($0) && $0.um("corrida_meta") != "comecar" && $0.um("corrida_continuo") == "sim" }))
        l.append(Pergunta(id: "bike_tipo", secao: "Bike", titulo: "Onde você pedala?", subtitulo: nil, tipo: .UNICA,
                          opcoes: [o("indoor", "Rolo / indoor"), o("estrada", "Estrada · speed"), o("mtb", "Mountain bike"), o("ergometrica", "Ergométrica / spinning")],
                          visivel: { mod($0) == .bike || (mod($0) == .hibrido && $0.um("hibrido_cardio") == "bike") }))
        l.append(Pergunta(id: "bike_ftp", secao: "Bike", titulo: "Você sabe o seu FTP?", subtitulo: "Potência que você sustenta por ~1 hora, em watts. Não sabe? Pule — usamos a percepção de esforço.",
                          tipo: .NUMERO, min: 80, max: 450, passo: 5, padrao: 200, unidade: "W", opcional: true, visivel: { mod($0) == .bike }))
        l.append(Pergunta(id: "luta_arte", secao: "Luta", titulo: "Qual é a sua luta?", subtitulo: nil, tipo: .UNICA, opcoes: [
            o("boxe", "Boxe"), o("muay", "Muay thai · kickboxing"), o("mma", "MMA"), o("bjj", "Jiu-jitsu"),
            o("judo", "Judô"), o("wrestling", "Wrestling · luta olímpica"), o("karate", "Karatê · taekwondo"),
        ], visivel: { mod($0) == .luta }))
        l.append(Pergunta(id: "luta_tecnicos", secao: "Luta", titulo: "Quantos treinos técnicos de luta você faz por semana?", subtitulo: "Treinos no tatame/ringue. A preparação física se ajusta a eles.",
                          tipo: .NUMERO, min: 0, max: 7, padrao: 3, unidade: "treinos", visivel: { mod($0) == .luta }))
        l.append(Pergunta(id: "luta_marcada", secao: "Luta", titulo: "Tem luta ou campeonato marcado?", subtitulo: nil, tipo: .UNICA,
                          opcoes: [o("nao", "Não"), o("4", "Em ~4 semanas"), o("6", "Em ~6 semanas"), o("8", "Em ~8 semanas"), o("12", "Em ~12 semanas")],
                          visivel: { mod($0) == .luta }))
        l.append(Pergunta(id: "atleta_esporte", secao: "Esporte", titulo: "Qual é o perfil do seu esporte?", subtitulo: nil, tipo: .UNICA, opcoes: [
            o("coletivo", "Coletivo", "Futebol, basquete, vôlei, handebol"),
            o("raquete", "Raquete", "Tênis, padel, beach tennis"),
            o("velocidade", "Velocidade e saltos", "Atletismo, sprint, saltos"),
            o("resistencia", "Resistência", "Triathlon, corrida longa, remo, natação"),
            o("forca", "Força", "Levantamentos, crossfit, arremessos"),
        ], visivel: { mod($0) == .atleta }))
        l.append(Pergunta(id: "atleta_fase", secao: "Esporte", titulo: "Em que fase da temporada você está?", subtitulo: nil, tipo: .UNICA, opcoes: [
            o("fora", "Fora de temporada", "Tempo para construir força e massa"),
            o("pre", "Pré-temporada", "Converter força em potência e velocidade"),
            o("em", "Em temporada", "Manter, sem atrapalhar jogos e provas"),
        ], visivel: { mod($0) == .atleta }))
        l.append(Pergunta(id: "idade", secao: "Você", titulo: "Qual a sua idade?", subtitulo: nil, tipo: .NUMERO, min: 14, max: 90, padrao: 30, unidade: "anos"))
        l.append(Pergunta(id: "sexo", secao: "Você", titulo: "Sexo", subtitulo: "Usado só para estimativas (ex.: gasto calórico).", tipo: .UNICA,
                          opcoes: [o("f", "Feminino"), o("m", "Masculino"), o("x", "Prefiro não dizer")]))
        l.append(Pergunta(id: "altura", secao: "Você", titulo: "Sua altura", subtitulo: nil, tipo: .NUMERO, min: 120, max: 220, padrao: 170, unidade: "cm"))
        l.append(Pergunta(id: "peso", secao: "Você", titulo: "Seu peso", subtitulo: nil, tipo: .NUMERO, min: 35, max: 220, padrao: 70, unidade: "kg"))
        l.append(Pergunta(id: "gestante", secao: "Saúde", titulo: "Você está grávida ou teve bebê há menos de 6 meses?", subtitulo: nil, tipo: .UNICA,
                          opcoes: [o("nao", "Não"), o("sim", "Sim")], visivel: { $0.um("sexo") == "f" }))
        l.append(Pergunta(id: "limitacoes", secao: "Saúde", titulo: "Alguma dor ou limitação?", subtitulo: "Adaptamos os exercícios. Dor forte ou persistente pede avaliação profissional.", tipo: .MULTIPLA,
                          opcoes: [o("joelho", "Joelho"), o("lombar", "Lombar / coluna"), o("ombro", "Ombro"), o("punho", "Punho"), o("nenhuma", "Nenhuma")], exclusiva: "nenhuma"))
        l.append(Pergunta(id: "parq", secao: "Saúde", titulo: "Triagem de segurança (PAR-Q+)", subtitulo: "Marque o que for verdade para você.", tipo: .MULTIPLA, opcoes: [
            o("coracao", "Um médico já disse que tenho problema no coração ou pressão alta"),
            o("dor_peito", "Sinto dor no peito em repouso, no dia a dia ou ao me exercitar"),
            o("tontura", "Perdi o equilíbrio por tontura ou desmaiei nos últimos 12 meses"),
            o("cronica", "Tenho outra doença crônica diagnosticada (além de coração/pressão)"),
            o("remedio", "Tomo remédio prescrito para doença crônica"),
            o("osso", "Tenho problema ósseo, articular ou de tecido mole que piora com exercício"),
            o("supervisao", "Um médico disse que só devo me exercitar com supervisão"),
            o("nenhuma", "Nenhuma das anteriores"),
        ], exclusiva: "nenhuma"))
        return l
    }()

    public static func visiveis(_ r: Respostas) -> [Pergunta] { perguntas.filter { $0.visivel(r) } }
    public static func limpar(_ r: Respostas) -> Respostas {
        let ids = Set(visiveis(r).map(\.id))
        return r.filter { ids.contains($0.key) }
    }
    public static func completo(_ r: Respostas) -> Bool { visiveis(r).allSatisfy { $0.respondida(r) } }

    public static func diasSugeridos(_ n: Int) -> [Int] {
        switch n {
        case 1: return [1]
        case 2: return [2, 5]
        case 3: return [1, 3, 5]
        case 4: return [1, 2, 4, 5]
        case 5: return [1, 2, 3, 5, 6]
        case 6: return [1, 2, 3, 4, 5, 6]
        default: return Array(1...7)
        }
    }
}

public struct Perfil: Equatable, Sendable {
    public var nome: String
    public var modalidade: Modalidade
    public var objetivo: Objetivo
    public var nivel: Nivel
    public var dias: [Int]
    public var minutos: Int
    public var equip: Set<String>
    public var evitar: Set<String>
    public var idade: Int
    public var sexo: String
    public var alturaCm: Int
    public var pesoKg: Int
    public var gestante: Bool
    public var parq: Set<String>
    public var emCasa: Bool
    public var cardioHibrido: String
    public var corridaMeta: String
    public var correContinuo: Bool
    public var tempo5kMin: Int?
    public var bikeTipo: String
    public var ftp: Int?
    public var lutaArte: String
    public var lutaTecnicos: Int
    public var lutaSemanas: Int?
    public var atletaEsporte: String
    public var atletaFase: String
    /// Limitações na ordem em que foram respondidas (o Kotlin preserva essa ordem nos alertas).
    public var ordemLimitacoes: [String] = []

    public var imc: Double { Double(pesoKg) / ((Double(alturaCm) / 100.0) * (Double(alturaCm) / 100.0)) }

    static let ACADEMIA: Set<String> = ["corpo", "barra", "halter", "maquina", "polia", "banco", "kettlebell", "barra_fixa", "elastico", "bola", "corda", "rolo", "bike", "esteira", "outro", "rua", "pista"]

    public static func de(_ r: Respostas) -> Perfil {
        let m = Modalidade.de(r.um("modalidade")) ?? .casaCorpo
        let emCasa = m == .casaCorpo || m == .casaElastico || r.um("local") == "casa"
        let extras = Set(r["equipamentos"] ?? [])
        var equip = Set<String>()
        if emCasa {
            equip.insert("corpo"); equip.insert("rua"); equip.formUnion(extras)
            if m == .casaElastico { equip.insert("elastico") }
        } else { equip.formUnion(ACADEMIA) }
        if m == .luta { equip.insert("saco"); equip.insert("corpo") }
        if m == .bike { equip.insert("bike") }
        if m == .corrida { equip.insert("rua"); equip.insert("pista") }
        if m == .hibrido && r.um("hibrido_cardio") == "bike" { equip.insert("bike") }
        var lim = Set((r["limitacoes"] ?? []).filter { $0 != "nenhuma" })
        let nivel = Nivel.de(r.um("experiencia")) ?? .iniciante
        let idade = r.num("idade") ?? 30
        let altura = r.num("altura") ?? 170
        let peso = r.num("peso") ?? 70
        let imc = Double(peso) / ((Double(altura) / 100.0) * (Double(altura) / 100.0))
        if idade >= 60 || (nivel == .iniciante && imc >= 32) || lim.contains("joelho") || r.um("gestante") == "sim" { lim.insert("impacto") }
        var dias = (r["dias_semana"] ?? []).compactMap { Int($0) }.sorted()
        if dias.isEmpty { dias = Questionario.diasSugeridos(r.num("dias") ?? 3) }
        let objPadrao: Objetivo
        switch m {
        case .mobilidade, .longevidade: objPadrao = .saude
        case .atleta, .luta: objPadrao = .performance
        case .corrida, .bike: objPadrao = .resistencia
        default: objPadrao = .massa
        }
        return Perfil(
            nome: (r.um("nome") ?? "").trimmingCharacters(in: .whitespaces), modalidade: m, objetivo: Objetivo.de(r.um("objetivo")) ?? objPadrao,
            nivel: nivel, dias: dias, minutos: r.num("minutos") ?? 45, equip: equip, evitar: lim, idade: idade, sexo: r.um("sexo") ?? "x",
            alturaCm: altura, pesoKg: peso, gestante: r.um("gestante") == "sim", parq: Set((r["parq"] ?? []).filter { $0 != "nenhuma" }),
            emCasa: emCasa, cardioHibrido: r.um("hibrido_cardio") ?? "corrida", corridaMeta: r.um("corrida_meta") ?? "saude",
            correContinuo: r.um("corrida_continuo") != "nao" && r.um("corrida_meta") != "comecar", tempo5kMin: r.num("corrida_5k"),
            bikeTipo: r.um("bike_tipo") ?? "indoor", ftp: r.num("bike_ftp"), lutaArte: r.um("luta_arte") ?? "mma",
            lutaTecnicos: r.num("luta_tecnicos") ?? 3, lutaSemanas: r.um("luta_marcada").flatMap { Int($0) },
            atletaEsporte: r.um("atleta_esporte") ?? "coletivo", atletaFase: r.um("atleta_fase") ?? "fora",
            ordemLimitacoes: (r["limitacoes"] ?? []).filter { $0 != "nenhuma" })
    }
}
