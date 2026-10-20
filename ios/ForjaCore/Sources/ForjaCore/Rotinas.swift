import Foundation

/// Rotinas avulsas de alongamento e mobilidade (porte de Rotinas.kt).
public struct Rotina: Identifiable, Sendable {
    public let id: String
    public let categoria: String
    public let titulo: String
    public let subtitulo: String
    public let tema: String
    public let sessao: Sessao
}

public enum Rotinas {
    public static let ANTES = "Antes do esporte"
    public static let DEPOIS = "Depois do treino"
    public static let MOBILIDADE = "Mobilidade & bem-estar"
    public static let CATEGORIAS = [ANTES, DEPOIS, MOBILIDADE]

    static func t(_ id: String, _ seg: Int, _ nota: String? = nil) -> Item { Item(id, 1, trabalhoSeg: seg, descansoSeg: 5, nota: nota) }
    static func r(_ id: String, _ reps: String, _ nota: String? = nil) -> Item { Item(id, 1, reps: reps, descansoSeg: 10, nota: nota) }
    static func e(_ id: String, _ seg: Int = 30, _ lados: Bool = true) -> Item {
        Item(id, 2, trabalhoSeg: lados ? seg * 2 : seg, descansoSeg: 10, intensidade: "Alongamento confortável", nota: lados ? "\(seg) s cada lado" : nil)
    }
    static func rotina(_ id: String, _ cat: String, _ titulo: String, _ sub: String, _ tema: String, _ nota: String, _ itens: [Item]) -> Rotina {
        Rotina(id: id, categoria: cat, titulo: titulo, subtitulo: sub, tema: tema, sessao: Sessao(titulo, sub, "mobilidade", 0,
            [Bloco(cat == DEPOIS ? "Alongamento estático" : (cat == ANTES ? "Preparo dinâmico" : "Mobilidade"), .PRINCIPAL, itens, nota: nota)], 0))
    }
    static let DIN = "Movimentos controlados, amplitude crescendo a cada repetição. Nada de forçar."
    static let EST = "Segure sem balançar, respirando devagar. Desconforto leve, nunca dor."

    public static let todas: [Rotina] = [
        // ------------------------------------------------ ANTES
        rotina("pre-corrida", ANTES, "Antes de correr", "Tornozelos, quadril e posterior acordados", "corrida", DIN, [
            t("circulos-tornozelo", 40, "20 s cada pé"),
            r("balanco-pernas", "10 cada perna", "Frente-trás e lado a lado"),
            t("circulos-quadril", 40),
            r("maior-alongamento", "5 cada lado"),
            t("chute-gluteo", 30),
            t("educativos-corrida", 120, "Skipping, anfersen e dribling"),
            t("carioca", 40, "20 s para cada lado")]),
        rotina("pre-bike", ANTES, "Antes de pedalar", "Quadril, coluna e joelhos prontos para o selim", "bike", DIN, [
            t("circulos-quadril", 40),
            r("gato-camelo", "8"),
            r("balanco-pernas", "10 cada perna"),
            t("circulos-joelho", 30),
            t("circulos-tornozelo", 30),
            r("rotacao-toracica", "6 cada lado"),
            t("flexor-quadril", 40, "20 s cada lado — curto antes do treino")]),
        rotina("pre-inferiores", ANTES, "Antes de treinar pernas", "Quadril e joelhos para agachar e levantar", "academia", DIN, [
            t("circulos-quadril", 40),
            r("balanco-pernas", "10 cada perna"),
            r("maior-alongamento", "5 cada lado"),
            r("agachamento-livre", "10", "Lento, descendo fundo"),
            r("ponte-gluteo", "12", "Aperte o glúteo no topo"),
            t("monster-walk", 40)]),
        rotina("pre-superiores", ANTES, "Antes de treinar superiores", "Ombros e escápulas para empurrar e puxar", "academia", DIN, [
            t("circulos-ombro", 30),
            t("circulos-braco", 40),
            r("abertura-peito-dinamica", "12"),
            r("band-pull-apart", "15"),
            r("rotacao-externa", "12 cada lado"),
            r("rotacao-toracica", "6 cada lado"),
            r("flexao-inclinada", "8", "Série leve de ativação")]),
        rotina("pre-luta-pe", ANTES, "Antes de lutar em pé", "Boxe, muay thai, MMA, karatê", "luta", DIN, [
            t("corda", 120, "Ou polichinelo"),
            t("circulos-ombro", 30),
            t("circulos-punho", 30),
            t("alongamento-pescoco", 30, "15 s cada lado, sem forçar"),
            r("balanco-pernas", "10 cada perna", "Frontal e lateral para os chutes"),
            t("circulos-quadril", 30),
            t("sombra", 120, "Comece solto, acelere no fim")]),
        rotina("pre-luta-solo", ANTES, "Antes de lutar no chão", "Jiu-jitsu, judô e wrestling", "luta", DIN, [
            r("gato-camelo", "8"),
            t("fuga-quadril", 60, "Pelo tatame"),
            r("ponte-pescoco", "6 cada lado"),
            t("circulos-quadril", 30),
            r("spider", "5 cada lado"),
            t("isometria-pescoco", 40, "Leve: 10 s em cada direção"),
            r("inchworm", "5")]),
        rotina("pre-coletivos", ANTES, "Antes do futebol e coletivos", "Inspirado na parte 1 do FIFA 11+", "atleta", DIN, [
            t("corrida-leve", 120, "Trote leve"),
            t("carioca", 40, "20 s para cada lado"),
            r("balanco-pernas", "10 cada perna"),
            t("chute-gluteo", 30),
            t("circulos-quadril", 30, "Abrindo e fechando o portão"),
            r("maior-alongamento", "4 cada lado"),
            r("tiros", "4", "Acelerações progressivas de 15 m")]),
        rotina("pre-raquete", ANTES, "Antes do tênis e padel", "Ombro, punho e rotação de tronco", "atleta", DIN, [
            t("circulos-ombro", 30),
            t("circulos-punho", 30),
            r("rotacao-externa", "12 cada lado"),
            r("moinho", "10"),
            r("rotacao-toracica", "6 cada lado"),
            t("carioca", 40),
            r("bound-lateral", "6", "Saltos laterais leves")]),
        rotina("pre-natacao", ANTES, "Antes de nadar", "Ombros soltos e caixa torácica aberta", "atleta", DIN, [
            t("circulos-braco", 40, "Para frente e para trás"),
            t("circulos-ombro", 30),
            r("abertura-peito-dinamica", "12"),
            r("band-pull-apart", "15"),
            r("rotacao-externa", "12 cada lado"),
            r("rotacao-toracica", "6 cada lado"),
            t("circulos-tornozelo", 30)]),
        rotina("pre-hiit", ANTES, "Antes do HIIT e funcional", "Corpo todo pronto para intensidade", "hiit", DIN, [
            t("polichinelo", 60),
            r("inchworm", "5"),
            r("maior-alongamento", "4 cada lado"),
            r("agachamento-livre", "10"),
            t("circulos-punho", 30),
            t("circulos-ombro", 30),
            r("spider", "4 cada lado")]),
        rotina("pre-caminhada", ANTES, "Antes da caminhada ou trilha", "Rápida e suave para qualquer idade", "longevidade", DIN, [
            t("circulos-tornozelo", 40),
            t("circulos-joelho", 30),
            t("circulos-quadril", 40),
            r("balanco-pernas", "8 cada perna", "Com apoio"),
            t("circulos-braco", 30)]),

        // ------------------------------------------------ DEPOIS
        rotina("pos-corrida", DEPOIS, "Depois de correr", "Panturrilha, posterior, quadríceps e quadril", "corrida", EST, [
            e("alongamento-panturrilha"),
            e("alongamento-posterior"),
            e("alongamento-quadriceps"),
            e("flexor-quadril"),
            e("alongamento-gluteo"),
            e("alongamento-adutores", 40, false)]),
        rotina("pos-bike", DEPOIS, "Depois de pedalar", "Abre o quadril e devolve a postura", "bike", EST, [
            e("flexor-quadril"),
            e("alongamento-quadriceps"),
            e("alongamento-gluteo"),
            e("alongamento-posterior"),
            e("alongamento-peito"),
            e("torcao-coluna")]),
        rotina("pos-superiores", DEPOIS, "Depois de treinar superiores", "Peito, costas, braços e pescoço", "academia", EST, [
            e("alongamento-peito"),
            e("alongamento-triceps"),
            e("alongamento-dorsal", 30, false),
            e("alongamento-pescoco", 20),
            e("alongamento-antebraco", 30, false)]),
        rotina("pos-inferiores", DEPOIS, "Depois de treinar pernas", "Quadríceps, posterior, glúteo e adutores", "academia", EST, [
            e("alongamento-quadriceps"),
            e("alongamento-posterior"),
            e("alongamento-gluteo"),
            e("alongamento-adutores", 40, false),
            e("alongamento-panturrilha"),
            e("postura-crianca", 45, false)]),
        rotina("pos-luta", DEPOIS, "Depois da luta", "Pescoço, quadril, lombar e antebraços", "luta", EST, [
            e("alongamento-pescoco", 20),
            e("alongamento-peito"),
            e("alongamento-adutores", 40, false),
            e("alongamento-gluteo"),
            e("abraco-joelhos", 40, false),
            e("alongamento-antebraco", 30, false)]),
        rotina("pos-geral", DEPOIS, "Volta à calma completa", "Depois de qualquer treino", "mobilidade", EST, [
            e("postura-crianca", 40, false),
            e("flexor-quadril"),
            e("alongamento-posterior"),
            e("alongamento-peito"),
            e("torcao-coluna"),
            e("abraco-joelhos", 40, false)]),

        // ------------------------------------------------ MOBILIDADE
        rotina("mob-diaria", MOBILIDADE, "Mobilidade diária · 10 min", "O básico para o corpo todo", "mobilidade", DIN, [
            r("gato-camelo", "10"),
            r("maior-alongamento", "5 cada lado"),
            r("rotacao-toracica", "8 cada lado"),
            t("circulos-quadril", 40),
            r("inchworm", "5"),
            e("postura-crianca", 45, false)]),
        rotina("mob-escritorio", MOBILIDADE, "Postura & escritório", "Pescoço, ombros e quadril depois de horas sentado", "mobilidade", DIN, [
            e("alongamento-pescoco", 20),
            t("circulos-ombro", 30),
            r("abertura-peito-dinamica", "12"),
            e("alongamento-peito"),
            e("alongamento-lateral", 20),
            e("torcao-coluna", 20),
            e("flexor-quadril")]),
        rotina("mob-quadril", MOBILIDADE, "Quadril destravado", "Para agachar melhor e aliviar a lombar", "mobilidade", DIN, [
            t("circulos-quadril", 40),
            r("spider", "5 cada lado"),
            r("maior-alongamento", "5 cada lado"),
            e("flexor-quadril", 40),
            e("alongamento-gluteo", 40),
            e("alongamento-adutores", 45, false),
            r("ponte-gluteo", "12")]),
        rotina("mob-ombros", MOBILIDADE, "Ombros saudáveis", "Amplitude e estabilidade das escápulas", "mobilidade", DIN, [
            t("circulos-ombro", 30),
            r("band-pull-apart", "15"),
            r("rotacao-externa", "12 cada lado"),
            r("rotacao-toracica", "8 cada lado"),
            e("alongamento-peito"),
            e("alongamento-dorsal", 30, false)]),
        rotina("mob-coluna", MOBILIDADE, "Coluna & lombar", "Movimento suave para costas tensas", "mobilidade", DIN, [
            r("gato-camelo", "10"),
            e("abraco-joelhos", 40, false),
            r("dead-bug", "8 cada lado"),
            e("torcao-coluna"),
            r("rotacao-toracica", "8 cada lado"),
            e("postura-crianca", 60, false)]),
        rotina("mob-dormir", MOBILIDADE, "Antes de dormir", "Relaxe o corpo e desacelere a respiração", "mobilidade", "Inspire em 4 s, solte o ar em 6 s. Luz baixa, sem pressa.", [
            e("postura-crianca", 60, false),
            e("abraco-joelhos", 45, false),
            e("alongamento-gluteo", 40),
            e("torcao-coluna", 40),
            e("alongamento-adutores", 60, false)]),
        rotina("mob-acordar", MOBILIDADE, "Ao acordar", "5 minutos para tirar a rigidez da manhã", "mobilidade", DIN, [
            e("alongamento-lateral", 20),
            r("gato-camelo", "8"),
            r("moinho", "10"),
            t("circulos-quadril", 30),
            t("circulos-ombro", 30)]),
        rotina("mob-tornozelos", MOBILIDADE, "Tornozelos & pés", "Base firme para correr, saltar e se equilibrar", "mobilidade", DIN, [
            t("circulos-tornozelo", 40, "20 s cada pé"),
            e("alongamento-panturrilha", 30),
            r("panturrilha-pe", "15", "Lento, 2 s em cima"),
            t("equilibrio-unipodal", 60, "30 s cada perna")]),
    ]

    public static func porId(_ id: String) -> Rotina? { todas.first { $0.id == id } }

    public static func recomendadas(_ m: Modalidade?, _ p: Perfil? = nil) -> [Rotina] {
        let ids: [String]
        switch m {
        case .corrida: ids = ["pre-corrida", "pos-corrida", "mob-tornozelos"]
        case .bike: ids = ["pre-bike", "pos-bike", "mob-quadril"]
        case .academia, .casaCorpo, .casaElastico: ids = ["pre-inferiores", "pre-superiores", "pos-inferiores", "pos-superiores"]
        case .luta: ids = ["bjj", "judo", "wrestling"].contains(p?.lutaArte ?? "") ? ["pre-luta-solo", "pos-luta", "mob-quadril"] : ["pre-luta-pe", "pos-luta", "mob-ombros"]
        case .atleta:
            switch p?.atletaEsporte {
            case "raquete": ids = ["pre-raquete", "pos-geral", "mob-ombros"]
            case "resistencia": ids = ["pre-natacao", "pre-corrida", "pos-corrida"]
            default: ids = ["pre-coletivos", "pos-inferiores", "mob-quadril"]
            }
        case .hiit: ids = ["pre-hiit", "pos-geral", "mob-diaria"]
        case .hibrido: ids = [p?.cardioHibrido == "bike" ? "pre-bike" : "pre-corrida", "pre-inferiores", "pos-geral"]
        case .longevidade: ids = ["pre-caminhada", "mob-acordar", "mob-tornozelos"]
        default: ids = ["mob-diaria", "mob-escritorio", "mob-dormir"]
        }
        return ids.compactMap { porId($0) }
    }
}
