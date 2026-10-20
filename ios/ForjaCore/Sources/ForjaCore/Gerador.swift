import Foundation

/// Porte fiel de Gerador.kt. Determinístico: o mesmo perfil gera sempre o mesmo plano.
public final class Gerador {
    private let cat: Catalogo
    public init(_ cat: Catalogo) { self.cat = cat }

    public func gerar(_ p: Perfil) -> Plano {
        var plano: Plano
        switch p.modalidade {
        case .academia, .casaCorpo, .casaElastico: plano = planoForca(p)
        case .corrida: plano = planoCorrida(p)
        case .bike: plano = planoBike(p)
        case .luta: plano = planoLuta(p)
        case .atleta: plano = planoAtleta(p)
        case .hiit: plano = planoHiit(p)
        case .hibrido: plano = planoHibrido(p)
        case .mobilidade: plano = planoMobilidade(p)
        case .longevidade: plano = planoLongevidade(p)
        }
        let semanas = plano.semanas.map { s -> Semana in
            var s = s; s.sessoes = s.sessoes.map { var x = $0; x.minutos = Roteiro.minutos(x, cat); return x }; return s
        }
        let sem1 = semanas[0].sessoes
        plano.semanas = semanas
        plano.alertas = alertas(p) + plano.alertas
        plano.dicas = plano.dicas + Gerador.DICAS_GERAIS
        plano.metaSemanal = "\(sem1.count) treinos · ~\(sem1.reduce(0) { $0 + $1.minutos }) min por semana"
        return plano
    }

    // ------------------------------------------------------------------ seleção

    final class Seletor {
        let p: Perfil, equip: Set<String>, nivelMax: Int, cat: Catalogo
        init(_ g: Gerador, _ p: Perfil, equip: Set<String>? = nil, nivelMax: Int? = nil) {
            self.p = p; self.equip = equip ?? p.equip; self.nivelMax = nivelMax ?? g.nivelMaximo(p); self.cat = g.cat
        }
        func disponivel(_ e: Exercicio) -> Bool {
            if e.evitar.contains(where: { p.evitar.contains($0) }) { return false }
            if e.nivel > nivelMax { return false }
            if e.equip.contains("barra_fixa") && !e.equip.contains("corpo") { return equip.contains("barra_fixa") }
            return e.equip.contains(where: { equip.contains($0) })
        }
        func pontos(_ e: Exercicio) -> Int {
            var s = 0
            let academia = !p.emCasa && p.modalidade != .casaCorpo && p.modalidade != .casaElastico
            for q in e.equip {
                let v: Int
                switch q {
                case "barra": v = academia ? 4 : 0
                case "maquina", "polia": v = academia ? 3 : 0
                case "halter": v = 3
                case "kettlebell": v = 2
                case "elastico": v = p.modalidade == .casaElastico ? 5 : (academia ? -2 : 1)
                case "barra_fixa": v = 3
                case "corpo": v = academia ? 0 : 2
                default: v = 0
                }
                s = Swift.max(s, v)
            }
            if Gerador.CLASSICOS.contains(e.id) { s += 2 }
            if p.nivel == .iniciante && e.nivel == 1 { s += 2 }
            if p.nivel == .avancado && e.nivel >= 2 { s += 1 }
            return s
        }
        func pool(_ padrao: String) -> [Exercicio] {
            cat.exercicios.filter { $0.padroes.contains(padrao) && disponivel($0) }
                .map { ($0, pontos($0)) }
                .sorted { a, b in
                    if a.1 != b.1 { return a.1 > b.1 }
                    if a.0.nivel != b.0.nivel { return a.0.nivel < b.0.nivel }
                    return a.0.id < b.0.id
                }.map { $0.0 }
        }
        func escolher(_ padrao: String, _ variante: Int, _ usados: inout Set<String>) -> Exercicio? {
            for pd in [padrao] + (Gerador.FALLBACK[padrao] ?? []) {
                let pl = pool(pd).filter { !usados.contains($0.id) }
                if !pl.isEmpty {
                    let e = pl[mod(variante, pl.count)]
                    usados.insert(e.id)
                    return e
                }
            }
            return nil
        }
        func primeiro(_ ids: String..., usados: inout Set<String>) -> Exercicio? {
            for id in ids { if let e = cat[id], disponivel(e), !usados.contains(e.id) { usados.insert(e.id); return e } }
            return nil
        }
        func primeiro(_ ids: String...) -> Exercicio? {
            for id in ids { if let e = cat[id], disponivel(e) { return e } }
            return nil
        }
    }

    func nivelMaximo(_ p: Perfil) -> Int {
        if p.modalidade == .longevidade && p.nivel == .iniciante { return 1 }
        if p.nivel == .iniciante || p.gestante || p.idade >= 65 { return 2 }
        return 3
    }

    // ------------------------------------------------------------------ doses

    struct Dose { let series: Int, rMin: Int, rMax: Int, descanso: Int, rir: String }

    func dose(_ obj: Objetivo, _ n: Nivel, _ principal: Bool) -> Dose {
        switch obj {
        case .massa:
            switch n {
            case .iniciante: return Dose(series: 3, rMin: 10, rMax: 12, descanso: 75, rir: "RIR 2–3")
            case .intermediario: return principal ? Dose(series: 4, rMin: 6, rMax: 10, descanso: 120, rir: "RIR 1–2") : Dose(series: 3, rMin: 10, rMax: 12, descanso: 75, rir: "RIR 1–2")
            case .avancado: return principal ? Dose(series: 4, rMin: 6, rMax: 8, descanso: 150, rir: "RIR 0–2") : Dose(series: 3, rMin: 10, rMax: 15, descanso: 75, rir: "RIR 0–1")
            }
        case .forca, .performance:
            switch n {
            case .iniciante: return principal ? Dose(series: 3, rMin: 6, rMax: 8, descanso: 120, rir: "RIR 2–3") : Dose(series: 2, rMin: 10, rMax: 12, descanso: 75, rir: "RIR 2")
            case .intermediario: return principal ? Dose(series: 4, rMin: 4, rMax: 6, descanso: 180, rir: "RIR 1–2") : Dose(series: 3, rMin: 8, rMax: 10, descanso: 90, rir: "RIR 2")
            case .avancado: return principal ? Dose(series: 5, rMin: 3, rMax: 5, descanso: 210, rir: "RIR 1–2") : Dose(series: 3, rMin: 6, rMax: 10, descanso: 120, rir: "RIR 1–2")
            }
        case .emagrecer:
            switch n {
            case .iniciante: return Dose(series: 2, rMin: 12, rMax: 15, descanso: 45, rir: "RIR 2–3")
            case .intermediario: return Dose(series: 3, rMin: 10, rMax: 15, descanso: 45, rir: "RIR 1–2")
            case .avancado: return Dose(series: principal ? 4 : 3, rMin: 8, rMax: 12, descanso: 60, rir: "RIR 1–2")
            }
        case .saude:
            switch n {
            case .iniciante: return Dose(series: 2, rMin: 10, rMax: 15, descanso: 60, rir: "RIR 3")
            case .intermediario: return Dose(series: 3, rMin: 10, rMax: 12, descanso: 60, rir: "RIR 2")
            case .avancado: return Dose(series: 3, rMin: 8, rMax: 12, descanso: 75, rir: "RIR 1–2")
            }
        case .resistencia: return Dose(series: n == .iniciante ? 2 : 3, rMin: 15, rMax: 20, descanso: 40, rir: "RIR 2")
        }
    }

    struct FaseSemana { var nome: String, nota: String, extraSerie: Bool, deload: Bool, variante: Int, volume: Double }

    func faseForca(_ semana: Int, _ n: Nivel) -> FaseSemana {
        switch semana {
        case 1: return FaseSemana(nome: "Adaptação", nota: "Cargas confortáveis: foque na técnica e no ritmo (2 s descendo).", extraSerie: false, deload: false, variante: 0, volume: 1.0)
        case 2: return FaseSemana(nome: "Construção", nota: "Dupla progressão: bateu o topo das repetições em todas as séries? Suba 2–5% a carga.", extraSerie: false, deload: false, variante: 0, volume: 1.0)
        case 3: return FaseSemana(nome: "Construção", nota: "+1 série nos exercícios principais. Mantenha a margem de repetições (RIR).", extraSerie: n != .iniciante, deload: false, variante: 0, volume: 1.0)
        case 4: return FaseSemana(nome: "Semana leve", nota: "Deload: ~40% menos séries e carga um pouco menor. Recuperar também é treino.", extraSerie: false, deload: true, variante: 0, volume: 0.6)
        case 5: return FaseSemana(nome: "Intensificação", nota: "Novas variações de exercícios. Recomece com cargas que deixem 2–3 repetições de reserva.", extraSerie: false, deload: false, variante: 1, volume: 1.0)
        case 6: return FaseSemana(nome: "Intensificação", nota: "Progrida a carga sempre que completar o topo da faixa.", extraSerie: false, deload: false, variante: 1, volume: 1.0)
        case 7: return FaseSemana(nome: "Pico", nota: "+1 série nos principais. Semana mais exigente do bloco.", extraSerie: true, deload: false, variante: 1, volume: 1.0)
        default: return FaseSemana(nome: "Semana leve & reteste", nota: "Volume reduzido. No último treino, teste suas cargas para o próximo bloco.", extraSerie: false, deload: true, variante: 1, volume: 0.6)
        }
    }

    func repsTexto(_ d: Dose) -> String { d.rMin == d.rMax ? "\(d.rMin)" : "\(d.rMin)–\(d.rMax)" }

    // ------------------------------------------------------------------ blocos padrão

    func aquecimento(_ p: Perfil, _ foco: String, _ usados: inout Set<String>) -> Bloco {
        let sel = Seletor(self, p, nivelMax: 3)
        let cardio: Exercicio
        if p.equip.contains("bike") && (p.evitar.contains("impacto") || !p.emCasa) { cardio = cat["bike-leve"]! }
        else if !p.emCasa && !p.evitar.contains("impacto") { cardio = cat["eliptico"]! }
        else if !p.evitar.contains("impacto") && p.equip.contains("corda") { cardio = cat["corda"]! }
        else if !p.evitar.contains("impacto") { cardio = cat["polichinelo"]! }
        else { cardio = cat["caminhada"]! }
        var itens = [Item(cardio.id, 1, trabalhoSeg: 180, descansoSeg: 0, intensidade: "Leve · 3/10", nota: cardio.id == "caminhada" ? "Pode ser marcha no lugar" : nil)]
        let mob: [String]
        switch foco {
        case "superior": mob = ["circulos-braco", "rotacao-toracica", "band-pull-apart"]
        case "inferior": mob = ["circulos-quadril", "maior-alongamento", "ponte-gluteo"]
        case "corrida": mob = ["circulos-quadril", "maior-alongamento", "educativos-corrida"]
        default: mob = ["circulos-quadril", "maior-alongamento", "circulos-braco"]
        }
        for id in mob {
            guard let e = sel.primeiro(id, usados: &usados) else { continue }
            itens.append(e.porTempo ? Item(e.id, 1, trabalhoSeg: 45, descansoSeg: 0) : Item(e.id, 1, reps: "12", descansoSeg: 15, intensidade: "Ativação"))
        }
        return Bloco("Aquecimento", .AQUECIMENTO, itens, nota: "Eleve a temperatura e prepare as articulações.")
    }

    func desaquecimento(_ foco: String) -> Bloco {
        let ids: [String]
        switch foco {
        case "superior": ids = ["alongamento-peito", "postura-crianca"]
        case "inferior", "corrida": ids = ["alongamento-panturrilha", "flexor-quadril", "alongamento-posterior"]
        case "bike": ids = ["flexor-quadril", "alongamento-quadriceps", "alongamento-posterior"]
        default: ids = ["postura-crianca", "flexor-quadril", "alongamento-posterior"]
        }
        return Bloco("Volta à calma", .DESAQUECIMENTO, ids.map { Item($0, 1, trabalhoSeg: Gerador.BILATERAL.contains($0) ? 60 : 40, descansoSeg: 0, nota: Gerador.BILATERAL.contains($0) ? "30 s cada lado" : nil) })
    }

    func blocoForca(_ p: Perfil, _ slots: [String], _ fase: FaseSemana, _ minutosPrincipal: Int, _ usados: inout Set<String>,
                    sel selIn: Seletor? = nil, obj objIn: Objetivo? = nil, principais: Int = 2, nome: String = "Treino principal") -> Bloco {
        let sel = selIn ?? Seletor(self, p)
        let obj = objIn ?? p.objetivo
        var itens: [Item] = []
        var tempo = 0
        for (i, slot) in slots.enumerated() {
            let partes = slot.split(separator: ":").map(String.init)
            let padrao = partes[0]; let v = partes.count > 1 ? (Int(partes[1]) ?? 0) : 0
            guard let e = sel.escolher(padrao, v + fase.variante, &usados) else { continue }
            let principal = i < principais
            let d = dose(obj, p.nivel, principal)
            var series = d.series + ((fase.extraSerie && principal) ? 1 : 0)
            if fase.deload { series = Swift.max(1, Int(ceil(Double(series) * fase.volume))) }
            series = Swift.min(series, 5)
            let item: Item
            if e.porTempo {
                let seg: Int
                if e.id == "farmer-walk" { seg = 40 } else if p.nivel == .iniciante { seg = 25 } else if p.nivel == .intermediario { seg = 40 } else { seg = 50 }
                item = Item(e.id, series, trabalhoSeg: seg, descansoSeg: Swift.min(d.descanso, 60), intensidade: fase.deload ? "Leve" : "Firme, sem perder a postura")
            } else {
                let semCarga = e.equip.allSatisfy { ["corpo", "banco", "barra_fixa"].contains($0) }
                item = Item(e.id, series, reps: repsTexto(d), descansoSeg: d.descanso, intensidade: fase.deload ? (semCarga ? "Mais leve · RIR 4" : "RIR 4 · carga −10%") : d.rir)
            }
            let custo = Roteiro.segundosItem(item) + 60
            if itens.count >= 3 && tempo + custo > minutosPrincipal * 60 { break }
            tempo += custo
            itens.append(item)
        }
        return Bloco(nome, .PRINCIPAL, itens, nota: "Descanse o tempo indicado entre as séries.")
    }

    func finalizador(_ p: Perfil, _ usados: inout Set<String>, _ voltas: Int, trabalho: Int = 30, descanso: Int = 30) -> Bloco? {
        let sel = Seletor(self, p)
        let ids = [sel.escolher("condicionamento", 0, &usados), sel.escolher("core", 1, &usados), sel.escolher("condicionamento", 1, &usados)].compactMap { $0 }
        if ids.count < 2 { return nil }
        return Bloco("Finalizador metabólico", .CIRCUITO, ids.map { Item($0.id, 1, trabalhoSeg: trabalho, descansoSeg: descanso, intensidade: "Forte · 8/10") }, voltas: voltas,
                     nota: "\(trabalho) s de esforço, \(descanso) s de pausa. Mantenha a técnica.")
    }

    func sessaoCardioLeve(_ p: Perfil, _ dia: Int, _ minutos: Int, titulo: String = "Cardio Z2", nota: String = "Ritmo em que você consegue conversar.") -> Sessao {
        let ex: String
        if !p.emCasa && p.evitar.contains("impacto") { ex = "bike-leve" }
        else if !p.emCasa { ex = p.nivel == .iniciante ? "eliptico" : "corrida-leve" }
        else if p.equip.contains("bike") { ex = "bike-leve" }
        else if p.equip.contains("esteira") && !p.evitar.contains("impacto") && p.nivel != .iniciante { ex = "corrida-leve" }
        else { ex = "caminhada" }
        let corpo = Swift.max(15, minutos - 5)
        return Sessao(titulo, "Base aeróbica", "cardio", minutos, [
            Bloco("Cardio contínuo", .PRINCIPAL, [Item(ex, 1, trabalhoSeg: corpo * 60, descansoSeg: 0, intensidade: "Zona 2 · 3–4/10", nota: nota)]),
            desaquecimento("inferior"),
        ], dia)
    }

    func sessaoMobilidade(_ p: Perfil, _ dia: Int, _ foco: Int, _ hold: Int, titulo: String? = nil) -> Sessao {
        let fluxos: [(String, [String])] = [
            ("Coluna & quadril", ["gato-camelo", "maior-alongamento", "flexor-quadril", "rotacao-toracica", "postura-crianca", "alongamento-adutores"]),
            ("Ombros & torácica", ["circulos-braco", "rotacao-toracica", "alongamento-peito", "band-pull-apart", "gato-camelo", "postura-crianca"]),
            ("Pernas & posterior", ["circulos-quadril", "alongamento-posterior", "alongamento-quadriceps", "alongamento-panturrilha", "alongamento-adutores", "flexor-quadril"]),
            ("Fluxo completo", ["inchworm", "maior-alongamento", "gato-camelo", "rotacao-toracica", "flexor-quadril", "alongamento-posterior", "postura-crianca"]),
            ("Liberação & equilíbrio", ["rolo-quadriceps", "rolo-panturrilha", "rolo-it", "equilibrio-unipodal", "alongamento-adutores", "postura-crianca"]),
        ]
        let (nome, ids) = fluxos[mod(foco, fluxos.count)]
        let sel = Seletor(self, p, nivelMax: 3)
        var usados = Set<String>()
        let escolhidos = ids.compactMap { sel.primeiro($0, usados: &usados) }
        let porVolta = escolhidos.reduce(0) { $0 + ((!$1.porTempo ? 40 : (Gerador.BILATERAL.contains($1.id) ? hold * 2 : hold)) + 15) }
        let series = Swift.min(4, Swift.max(2, arred(Double(p.minutos) * 60.0 / Double(Swift.max(1, porVolta)))))
        let itens = escolhidos.map { e -> Item in
            if e.porTempo { return Item(e.id, series, trabalhoSeg: Gerador.BILATERAL.contains(e.id) ? hold * 2 : hold, descansoSeg: 10, intensidade: "Alongamento confortável", nota: Gerador.BILATERAL.contains(e.id) ? "\(hold) s cada lado" : nil) }
            return Item(e.id, series, reps: "10–12", descansoSeg: 20, intensidade: "Controle")
        }
        return Sessao(titulo ?? "Mobilidade · \(nome)", nome, "mobilidade", 0, [
            Bloco("Fluxo de mobilidade", .PRINCIPAL, itens, nota: "Respire fundo e solte o ar devagar em cada posição. Sem dor."),
        ], dia)
    }

    // ------------------------------------------------------------------ musculação

    let FULL_A = ["agachar", "empurrar_h", "puxar_h", "gluteo", "empurrar_v", "ombro_post", "core"]
    let FULL_B = ["dobradica", "puxar_v", "empurrar_v:1", "unilateral", "biceps", "triceps", "core:1"]
    let FULL_C = ["unilateral:1", "empurrar_h:1", "puxar_h:1", "gluteo:1", "ombro_lat", "panturrilha", "core:2"]
    let UPPER_A = ["empurrar_h", "puxar_h", "empurrar_v", "puxar_v", "ombro_lat", "biceps", "triceps"]
    let LOWER_A = ["agachar", "dobradica", "unilateral", "posterior", "panturrilha", "core"]
    let UPPER_B = ["puxar_v:1", "empurrar_h:1", "puxar_h:1", "empurrar_v:1", "ombro_post", "triceps:1", "biceps:1"]
    let LOWER_B = ["dobradica:1", "agachar:1", "gluteo", "quadriceps", "panturrilha:1", "core:1"]
    let PUSH = ["empurrar_h", "empurrar_v", "empurrar_h:1", "peito_iso", "ombro_lat", "triceps", "triceps:1"]
    let PULL = ["puxar_v", "puxar_h", "puxar_h:1", "ombro_post", "trapezio", "biceps", "biceps:1"]
    let LEGS = ["agachar", "dobradica", "unilateral", "quadriceps", "posterior", "gluteo", "panturrilha"]

    struct Modelo { let titulo: String, foco: String, aq: String, slots: [String]; var variante = 0 }

    func divisao(_ dias: Int) -> (String, [Modelo]) {
        switch dias {
        case 1, 2: return ("Full body A/B", [Modelo(titulo: "Corpo inteiro A", foco: "Corpo inteiro", aq: "total", slots: FULL_A), Modelo(titulo: "Corpo inteiro B", foco: "Corpo inteiro", aq: "total", slots: FULL_B)])
        case 3: return ("Full body A/B/C", [Modelo(titulo: "Corpo inteiro A", foco: "Corpo inteiro", aq: "total", slots: FULL_A), Modelo(titulo: "Corpo inteiro B", foco: "Corpo inteiro", aq: "total", slots: FULL_B), Modelo(titulo: "Corpo inteiro C", foco: "Corpo inteiro", aq: "total", slots: FULL_C)])
        case 4: return ("Superior/Inferior", [Modelo(titulo: "Superiores A", foco: "Peito, costas e ombros", aq: "superior", slots: UPPER_A), Modelo(titulo: "Inferiores A", foco: "Pernas e glúteos", aq: "inferior", slots: LOWER_A),
                                            Modelo(titulo: "Superiores B", foco: "Costas, peito e braços", aq: "superior", slots: UPPER_B), Modelo(titulo: "Inferiores B", foco: "Posterior e glúteos", aq: "inferior", slots: LOWER_B)])
        case 5: return ("Superior/Inferior + Push/Pull/Legs", [Modelo(titulo: "Superiores", foco: "Peito, costas e ombros", aq: "superior", slots: UPPER_A), Modelo(titulo: "Inferiores", foco: "Pernas e glúteos", aq: "inferior", slots: LOWER_A),
                                                             Modelo(titulo: "Empurrar", foco: "Peito, ombros e tríceps", aq: "superior", slots: PUSH, variante: 1), Modelo(titulo: "Puxar", foco: "Costas e bíceps", aq: "superior", slots: PULL, variante: 1), Modelo(titulo: "Pernas", foco: "Quadríceps, posterior e glúteos", aq: "inferior", slots: LEGS, variante: 1)])
        default: return ("Push/Pull/Legs 2x", [Modelo(titulo: "Empurrar A", foco: "Peito, ombros e tríceps", aq: "superior", slots: PUSH), Modelo(titulo: "Puxar A", foco: "Costas e bíceps", aq: "superior", slots: PULL), Modelo(titulo: "Pernas A", foco: "Quadríceps, posterior e glúteos", aq: "inferior", slots: LEGS),
                                               Modelo(titulo: "Empurrar B", foco: "Peito, ombros e tríceps", aq: "superior", slots: PUSH, variante: 1), Modelo(titulo: "Puxar B", foco: "Costas e bíceps", aq: "superior", slots: PULL, variante: 1), Modelo(titulo: "Pernas B", foco: "Posterior, glúteos e quadríceps", aq: "inferior", slots: LEGS, variante: 1)])
        }
    }

    func sessaoForca(_ p: Perfil, _ m: Modelo, _ dia: Int, _ fase: FaseSemana, minutos minIn: Int? = nil, finalizar: Bool = false, obj: Objetivo? = nil) -> Sessao {
        let minutos = minIn ?? p.minutos
        var usados = Set<String>()
        let aq = aquecimento(p, m.aq, &usados)
        let fin = (finalizar && minutos >= 40 && !fase.deload) ? 8 : 0
        let disponivel = Swift.max(10, minutos - 7 - 4 - fin)
        let slots = m.slots.map { s -> String in
            if m.variante == 0 { return s }
            let pt = s.split(separator: ":").map(String.init)
            return "\(pt[0]):\((pt.count > 1 ? (Int(pt[1]) ?? 0) : 0) + m.variante)"
        }
        let principal = blocoForca(p, slots, fase, disponivel, &usados, obj: obj)
        var blocos = [aq, principal]
        if fin > 0, let f = finalizador(p, &usados, p.nivel == .iniciante ? 3 : 4) { blocos.append(f) }
        blocos.append(desaquecimento(m.aq))
        return Sessao(m.titulo, m.foco, "forca", minutos, blocos, dia)
    }

    func planoForca(_ p: Perfil) -> Plano {
        let n = p.dias.count
        var diasForca: Int
        switch p.objetivo {
        case .saude: diasForca = Swift.min(n, 3)
        case .emagrecer, .resistencia: diasForca = Swift.min(n, n >= 5 ? 3 : Swift.max(2, n - 1))
        default: diasForca = p.nivel == .iniciante ? Swift.min(n, 4) : n
        }
        diasForca = Swift.max(diasForca, Swift.min(n, 2))
        let (nomeDiv, modelos) = divisao(diasForca)
        let indicesForca = Set((0..<diasForca).map { k in Swift.min(arred(Double(k) * Double(n) / Double(diasForca)), n - 1) })
        let semanas = (1...8).map { w -> Semana in
            let fase = faseForca(w, p.nivel)
            var f = 0, c = 0
            let sessoes = p.dias.enumerated().map { (i, dia) -> Sessao in
                if indicesForca.contains(i) && f < diasForca {
                    let m = modelos[f % modelos.count]; f += 1
                    return sessaoForca(p, m, dia, fase, finalizar: p.objetivo == .emagrecer)
                }
                c += 1
                let hiit = p.objetivo == .emagrecer && c % 2 == 0 && p.nivel != .iniciante && !p.evitar.contains("impacto")
                return hiit ? sessaoHiitCurta(p, dia, fase, w) : sessaoCardioLeve(p, dia, Swift.min(p.minutos, fase.deload ? 30 : 45))
            }
            return Semana(numero: w, fase: fase.nome, nota: fase.nota, sessoes: sessoes)
        }
        let local: String
        switch p.modalidade { case .casaCorpo: local = "em casa"; case .casaElastico: local = "com elásticos"; default: local = "na academia" }
        var dicas = [
            "RIR = repetições em reserva. RIR 2 significa terminar a série sentindo que faria mais 2.",
            "Progrida sempre que completar o topo da faixa de repetições em todas as séries.",
        ]
        if p.modalidade != .academia { dicas.append("Ficou fácil? Desça mais devagar (3–4 s), pause no fundo ou use a variação mais difícil.") }
        if p.objetivo == .massa { dicas.append("Para hipertrofia: proteína ~1,6 g/kg/dia e sono de 7–9 h fazem diferença.") }
        if p.objetivo == .emagrecer { dicas.append("O treino de força preserva a massa magra no déficit calórico; some passos no dia a dia (7–10 mil).") }
        if p.objetivo == .saude { dicas.append("Meta da OMS: 150–300 min de atividade moderada por semana + força 2x.") }
        return Plano(nome: "\(p.objetivo.nome) \(local)",
                     resumo: "\(nomeDiv) · \(diasForca)x força\(n > diasForca ? " + \(n - diasForca)x cardio" : "") · 8 semanas com semana leve na 4 e na 8.",
                     modalidade: p.modalidade, objetivo: p.objetivo, nivel: p.nivel, semanas: semanas, dicas: dicas, alertas: [], metaSemanal: "")
    }

    func sessaoHiitCurta(_ p: Perfil, _ dia: Int, _ fase: FaseSemana, _ w: Int) -> Sessao {
        var usados = Set<String>()
        let sel = Seletor(self, p)
        let ids = [sel.escolher("condicionamento", w, &usados), sel.escolher("agachar", w, &usados), sel.escolher("condicionamento", w + 1, &usados), sel.escolher("core", w, &usados)].compactMap { $0 }
        let voltas = fase.deload ? 3 : 4 + (p.nivel == .avancado ? 1 : 0)
        let aq = aquecimento(p, "total", &usados)
        return Sessao("HIIT curto", "Condicionamento", "hiit", 0, [
            aq,
            Bloco("Circuito 40/20", .CIRCUITO, ids.map { Item($0.id, 1, trabalhoSeg: 40, descansoSeg: 20, intensidade: "Forte · 8/10") }, voltas: voltas, nota: "40 s de esforço, 20 s de pausa. 1 min entre voltas se precisar."),
            desaquecimento("total"),
        ], dia)
    }

    // ------------------------------------------------------------------ corrida

    func pace(_ seg: Int) -> String { String(format: "%d:%02d", seg / 60, seg % 60) }
    func faixaPace(_ p: Perfil, _ de: Int, _ ate: Int) -> String? {
        guard let t = p.tempo5kMin else { return nil }
        let base = t * 60 / 5
        return "\(pace(base + de))–\(pace(base + ate)) /km"
    }
    func intensidade(_ zona: String, _ pace: String?) -> String { pace != nil ? "\(zona) · \(pace!)" : zona }
    func semanasCorrida(_ meta: String) -> Int { switch meta { case "10k": return 10; case "21k": return 12; case "42k": return 16; default: return 8 } }

    func longaoMin(_ meta: String, _ n: Nivel) -> (Int, Int) {
        switch meta {
        case "5k": switch n { case .iniciante: return (30, 45); case .intermediario: return (40, 55); case .avancado: return (45, 65) }
        case "10k": switch n { case .iniciante: return (40, 70); case .intermediario: return (50, 80); case .avancado: return (60, 90) }
        case "21k": switch n { case .iniciante: return (60, 120); case .intermediario: return (70, 130); case .avancado: return (80, 140) }
        case "42k": switch n { case .iniciante: return (75, 190); case .intermediario: return (90, 200); case .avancado: return (100, 210) }
        default: switch n { case .iniciante: return (30, 50); case .intermediario: return (40, 65); case .avancado: return (50, 80) }
        }
    }
    func taper(_ meta: String) -> Int { switch meta { case "42k": return 3; case "21k": return 2; default: return 1 } }

    func fatorCorrida(_ w: Int, _ total: Int, _ meta: String) -> (Double, String) {
        let tp = taper(meta)
        let pico = total - tp
        if w > pico {
            let k = w - pico
            let fs: [Double] = tp == 3 ? [0.75, 0.6, 0.4] : (tp == 2 ? [0.7, 0.45] : [0.55])
            return (fs[k - 1], w == total ? "Semana de prova" : "Polimento")
        }
        if w % 4 == 0 { return (-1.0, "Recuperação") }
        return (Double(w - 1) / Double(Swift.max(1, pico - 1)), w <= pico / 2 ? "Base" : "Construção")
    }

    struct Tiro { let reps: Int, trabalho: Int, pausa: Int, nome: String }
    func tiros(_ n: Nivel, _ w: Int) -> Tiro {
        let l: [Tiro]
        switch n {
        case .iniciante: l = [Tiro(reps: 6, trabalho: 60, pausa: 120, nome: "6 × 1 min"), Tiro(reps: 8, trabalho: 60, pausa: 90, nome: "8 × 1 min"), Tiro(reps: 6, trabalho: 120, pausa: 120, nome: "6 × 2 min"), Tiro(reps: 5, trabalho: 180, pausa: 120, nome: "5 × 3 min")]
        case .intermediario: l = [Tiro(reps: 8, trabalho: 90, pausa: 90, nome: "8 × 400 m (~90 s)"), Tiro(reps: 6, trabalho: 180, pausa: 120, nome: "6 × 800 m (~3 min)"), Tiro(reps: 5, trabalho: 240, pausa: 120, nome: "5 × 1 km (~4 min)"), Tiro(reps: 10, trabalho: 60, pausa: 60, nome: "10 × 1 min")]
        case .avancado: l = [Tiro(reps: 10, trabalho: 90, pausa: 60, nome: "10 × 400 m"), Tiro(reps: 6, trabalho: 240, pausa: 90, nome: "6 × 1 km"), Tiro(reps: 5, trabalho: 300, pausa: 120, nome: "5 × 1200 m (~5 min)"), Tiro(reps: 12, trabalho: 60, pausa: 60, nome: "12 × 1 min"), Tiro(reps: 4, trabalho: 480, pausa: 120, nome: "4 × 2 km (~8 min)")]
        }
        return l[mod(w - 1, l.count)]
    }

    func sessaoCorrida(_ p: Perfil, _ dia: Int, _ tipo: String, _ w: Int, _ total: Int, _ meta: String, forcaExtra: Bool = false) -> Sessao {
        let (lo, hi) = longaoMin(meta, p.nivel)
        let (fator, _) = fatorCorrida(w, total, meta)
        var longao: Int
        if fator < 0 { longao = arred((Double(lo) + Double(hi - lo) * Double(w - 2) / Double(Swift.max(1, total - taper(meta) - 1))) * 0.75) }
        else if w > total - taper(meta) { longao = arred(Double(hi) * fator) }
        else { longao = arred(Double(lo) + Double(hi - lo) * fator) }
        longao = Swift.max(longao, 20)
        let leve = Swift.min(Swift.max(arred(Double(longao) * 0.6), 20), Swift.max(20, p.minutos - 10))
        let recup = fator < 0 || w > total - taper(meta)
        let aqCorrida = Bloco("Aquecimento", .AQUECIMENTO, [
            Item("corrida-leve", 1, trabalhoSeg: 600, descansoSeg: 0, intensidade: "Bem leve · 2–3/10", nota: "Comece caminhando se precisar"),
            Item("educativos-corrida", 1, trabalhoSeg: 180, descansoSeg: 0, nota: "Skipping, anfersen e dribling"),
        ])
        let ultima = w == total && tipo == "L" && ["5k", "10k", "21k", "42k"].contains(meta)
        var blocos: [Bloco] = []
        let titulo: String, foco: String
        if ultima {
            let km = String(meta.dropLast())
            titulo = "Dia da prova · \(km) km"; foco = "Prova"
            blocos.append(Bloco("Aquecimento", .AQUECIMENTO, [Item("corrida-leve", 1, trabalhoSeg: 600, descansoSeg: 0, intensidade: "Leve")]))
            blocos.append(Bloco("Prova", .PRINCIPAL, [Item("prova", 1, trabalhoSeg: longaoMin(meta, p.nivel).1 * 60, descansoSeg: 0, intensidade: "Ritmo de prova", nota: "Largue controlado; acelere na segunda metade.")]))
        } else if tipo == "L" {
            titulo = "Longão"; foco = "Resistência aeróbica"
            blocos.append(Bloco("Corrida longa", .PRINCIPAL, [Item("longao", 1, trabalhoSeg: longao * 60, descansoSeg: 0, intensidade: intensidade("Zona 2 · conversa", faixaPace(p, 70, 105)),
                                                                     nota: longao >= 75 ? "Leve água e carboidrato a partir de 60 min." : nil)]))
        } else if tipo == "Q" && !recup {
            let corridaLonga = meta == "21k" || meta == "42k"
            if corridaLonga && w % 2 == 0 {
                let blocosMin = Swift.min(20, 8 + w)
                let reps = meta == "42k" ? 3 : 2
                titulo = "Ritmo de prova"; foco = "Ritmo específico"
                blocos.append(aqCorrida)
                blocos.append(Bloco("Blocos no ritmo de prova", .INTERVALADO, [Item("tempo-run", reps, trabalhoSeg: blocosMin * 60, descansoSeg: 120,
                    intensidade: intensidade("Ritmo de prova · 6–7/10", faixaPace(p, meta == "42k" ? 40 : 25, meta == "42k" ? 55 : 40)), nota: "Recupere trotando 2 min")]))
            } else {
                let t = tiros(p.nivel, (w + 1) / 2)
                titulo = "Intervalado · \(t.nome)"; foco = "Velocidade e VO2"
                blocos.append(aqCorrida)
                blocos.append(Bloco("Tiros", .INTERVALADO, [Item("tiros", t.reps, trabalhoSeg: t.trabalho, descansoSeg: t.pausa,
                    intensidade: intensidade("Forte · 8/10", faixaPace(p, -10, 0)), nota: "Recuperação trotando ou caminhando")]))
            }
        } else if tipo == "T" && !recup {
            let base: Int
            switch p.nivel { case .iniciante: base = 10 + w; case .intermediario: base = 15 + w * 2; case .avancado: base = 20 + w * 2 }
            let dur = Swift.min(base, 40)
            titulo = "Corrida de limiar"; foco = "Limiar"
            blocos.append(aqCorrida)
            blocos.append(Bloco("Limiar contínuo", .PRINCIPAL, [Item("tempo-run", 1, trabalhoSeg: dur * 60, descansoSeg: 0, intensidade: intensidade("Confortavelmente difícil · 7/10", faixaPace(p, 15, 25)))]))
        } else if tipo == "R" {
            titulo = "Regenerativo"; foco = "Recuperação"
            blocos.append(Bloco("Corrida leve", .PRINCIPAL, [Item("corrida-leve", 1, trabalhoSeg: Swift.min(30, leve) * 60, descansoSeg: 0, intensidade: intensidade("Muito leve · 2/10", faixaPace(p, 90, 120)))]))
        } else {
            titulo = forcaExtra ? "Leve + força" : "Corrida leve"; foco = "Base aeróbica"
            let strides = (p.nivel != .iniciante && !recup) ? [Item("tiros", 4, trabalhoSeg: 20, descansoSeg: 60, intensidade: "Acelerações · 85%", nota: "Strides: soltas, sem forçar")] : []
            blocos.append(Bloco("Corrida leve", .PRINCIPAL, [Item("corrida-leve", 1, trabalhoSeg: leve * 60, descansoSeg: 0, intensidade: intensidade("Zona 2 · conversa", faixaPace(p, 60, 90)))] + strides))
        }
        if forcaExtra { blocos.append(forcaCorredor(p, w)) }
        blocos.append(desaquecimento("corrida"))
        return Sessao(titulo, foco, "corrida", 0, blocos, dia)
    }

    func forcaCorredor(_ p: Perfil, _ w: Int, nome: String = "Força para corredores") -> Bloco {
        let pesos: Set<String> = (p.modalidade == .corrida || p.modalidade == .bike) ? [] : p.equip.intersection(["elastico", "halter", "kettlebell"])
        let sel = Seletor(self, p, equip: Set(["corpo"]).union(pesos))
        var usados = Set<String>()
        let ids = [sel.escolher("unilateral", w, &usados), sel.escolher("gluteo", w, &usados), sel.escolher("panturrilha", 0, &usados), sel.escolher("core", w, &usados)].compactMap { $0 }
        return Bloco(nome, .CIRCUITO, ids.map { e in
            e.porTempo ? Item(e.id, 1, trabalhoSeg: 40, descansoSeg: 20) : Item(e.id, 1, reps: "10–12", descansoSeg: 20, intensidade: "RIR 2")
        }, voltas: p.nivel == .iniciante ? 2 : 3, nota: "Previne lesões e melhora a economia de corrida.")
    }

    func sessaoCaminhaCorre(_ p: Perfil, _ dia: Int, _ w: Int, _ k: Int) -> Sessao {
        let tabela = [(60, 90, 8), (90, 90, 7), (120, 90, 6), (180, 90, 5), (300, 120, 4), (480, 120, 3), (720, 120, 2)]
        let principal: Item
        if w >= 8 {
            let m = [25, 28, 30][Swift.min(Swift.max(k, 0), 2)]
            principal = Item("corrida-leve", 1, trabalhoSeg: m * 60, descansoSeg: 0, intensidade: "Zona 2 · conversa", nota: "Corrida contínua! Devagar está ótimo.")
        } else {
            let (corre, caminha, reps) = tabela[w - 1]
            principal = Item("caminhada-corrida", reps, trabalhoSeg: corre, descansoSeg: caminha, intensidade: "Trote leve · 4–5/10", nota: "No descanso, caminhe rápido")
        }
        return Sessao(w >= 8 ? "Corrida contínua" : "Caminhada + corrida", "Construção de base", "corrida", 0, [
            Bloco("Aquecimento", .AQUECIMENTO, [Item("caminhada", 1, trabalhoSeg: 300, descansoSeg: 0, intensidade: "Caminhada rápida")]),
            Bloco("Corre & caminha", .INTERVALADO, [principal]),
            Bloco("Volta à calma", .DESAQUECIMENTO, [Item("caminhada", 1, trabalhoSeg: 300, descansoSeg: 0)] + desaquecimento("corrida").itens),
        ], dia)
    }

    func planoCorrida(_ p: Perfil) -> Plano {
        var meta = p.corridaMeta
        var alertas: [String] = []
        if !p.correContinuo {
            if ["10k", "21k", "42k"].contains(meta) { alertas.append("Antes de buscar os \(meta.dropLast()) km, este plano constrói sua base até 30 minutos contínuos. Depois, refaça o questionário.") }
            meta = "comecar"
        }
        let n = p.dias.count
        if meta == "comecar" {
            let semanas = (1...8).map { w -> Semana in
                var k = 0
                let sessoes = p.dias.enumerated().map { (i, dia) -> Sessao in
                    let corrida = n <= 3 || i % 2 == 0 || (k < 3 && n - i <= 3 - k)
                    if corrida && k < 3 { let s = sessaoCaminhaCorre(p, dia, w, k); k += 1; return s }
                    if i % 2 == 1 && n >= 4 {
                        var u = Set<String>()
                        return Sessao("Força para corredores", "Prevenção", "forca", 0, [aquecimento(p, "inferior", &u), forcaCorredor(p, w, nome: "Circuito de força"), desaquecimento("inferior")], dia)
                    }
                    var pc = p; pc.emCasa = true
                    return sessaoCardioLeve(pc, dia, 30, titulo: "Caminhada rápida", nota: "Passo firme: respiração acelerada, mas dá para conversar.")
                }
                return Semana(numero: w, fase: w < 4 ? "Base" : (w < 8 ? "Construção" : "30 minutos!"), nota: "Corrida e caminhada intercaladas. Repita a semana se sentir que precisa — tudo bem.", sessoes: sessoes)
            }
            return Plano(nome: "Do zero aos 30 minutos", resumo: "8 semanas de corrida e caminhada intercaladas até 30 min contínuos (≈ 5 km).", modalidade: p.modalidade, objetivo: p.objetivo, nivel: p.nivel, semanas: semanas,
                         dicas: ["Ritmo certo é o que deixa você conversar. Correr devagar é correr certo.", "Tênis confortável e superfície regular nas primeiras semanas.", "Dor articular que piora ao correr = pare e descanse; dor muscular leve no dia seguinte é normal."],
                         alertas: alertas, metaSemanal: "")
        }
        let total = semanasCorrida(meta)
        var modelo: [String]
        switch n {
        case 2: modelo = ["Q", "L"]
        case 3: modelo = ["Q", "E", "L"]
        case 4: modelo = ["Q", "E", p.nivel == .iniciante ? "E" : "T", "L"]
        case 5: modelo = ["Q", "E", "T", "E", "L"]
        default: modelo = ["Q", "E", "T", "E", "R", "L"]
        }
        modelo = modelo.map { (meta == "saude" && p.nivel == .iniciante && $0 == "Q") ? "E" : $0 }
        let semanas = (1...total).map { w -> Semana in
            let (_, fase) = fatorCorrida(w, total, meta)
            var forcas = 0
            let sessoes = p.dias.enumerated().map { (i, dia) -> Sessao in
                let t = modelo[Swift.min(i, modelo.count - 1)]
                let forca = t == "E" && forcas < (n >= 5 ? 2 : 1) && n >= 3
                if forca { forcas += 1 }
                return sessaoCorrida(p, dia, t, w, total, meta, forcaExtra: forca)
            }
            let nota: String
            switch fase {
            case "Recuperação": nota = "Semana mais leve para absorver o treino. Volume ~25% menor."
            case "Polimento": nota = "Menos volume, mantendo um pouco de intensidade: chegue descansado."
            case "Semana de prova": nota = "Durma bem, nada de novidade em tênis ou comida. Confie no treino!"
            case "Base": nota = "80% dos treinos em ritmo leve (Seiler). A intensidade fica nos dias de qualidade."
            default: nota = "Volume subindo aos poucos. Respeite os ritmos — leve é leve."
            }
            return Semana(numero: w, fase: fase, nota: nota, sessoes: sessoes)
        }
        let nome: String
        switch meta { case "5k": nome = "5 km"; case "10k": nome = "10 km"; case "21k": nome = "Meia maratona"; case "42k": nome = "Maratona"; case "ritmo": nome = "Mais velocidade"; default: nome = "Correr por saúde" }
        var dicas = [p.tempo5kMin == nil ? "Sem tempo de 5 km informado, os ritmos estão por percepção de esforço (escala 0–10)." : "Ritmos calculados a partir dos seus \(p.tempo5kMin!) min nos 5 km. Refaça um teste a cada 6–8 semanas.",
                     "Cadência alta (passos curtos) reduz o impacto. Mire em ~170–180 passos por minuto."]
        if meta == "21k" || meta == "42k" { dicas.append("Treine a hidratação e os géis nos longões, nunca teste novidade no dia da prova.") }
        return Plano(nome: "\(nome) em \(total) semanas", resumo: "\(n)x por semana · distribuição 80/20 · longão progressivo com semanas de recuperação.", modalidade: p.modalidade, objetivo: p.objetivo, nivel: p.nivel, semanas: semanas,
                     dicas: dicas, alertas: alertas, metaSemanal: "")
    }

    // ------------------------------------------------------------------ bike

    struct ZonaBike { let nome: String, de: Int, ate: Int, rpe: String }
    let Z1 = ZonaBike(nome: "Z1 Recuperação", de: 0, ate: 55, rpe: "2/10")
    let Z2 = ZonaBike(nome: "Z2 Endurance", de: 56, ate: 75, rpe: "3–4/10")
    let Z3 = ZonaBike(nome: "Z3 Tempo", de: 76, ate: 90, rpe: "5–6/10")
    let SS = ZonaBike(nome: "Sweet spot", de: 88, ate: 94, rpe: "6–7/10")
    let Z4 = ZonaBike(nome: "Z4 Limiar", de: 91, ate: 105, rpe: "7–8/10")
    let Z5 = ZonaBike(nome: "Z5 VO2máx", de: 106, ate: 120, rpe: "9/10")

    func zona(_ p: Perfil, _ z: ZonaBike) -> String {
        if let ftp = p.ftp { return "\(z.nome) · \(arred(Double(ftp * z.de) / 100.0))–\(arred(Double(ftp * z.ate) / 100.0)) W" }
        return "\(z.nome) · \(z.rpe)"
    }

    func sessaoBike(_ p: Perfil, _ dia: Int, _ tipo: String, _ w: Int, _ fase: FaseSemana) -> Sessao {
        let leve = fase.deload
        let ini = p.nivel == .iniciante
        let aq = Bloco("Aquecimento", .AQUECIMENTO, [Item("bike-leve", 1, trabalhoSeg: 600, descansoSeg: 0, intensidade: zona(p, Z2), nota: "Suba a intensidade aos poucos")])
        let volta = Bloco("Volta à calma", .DESAQUECIMENTO, [Item("bike-leve", 1, trabalhoSeg: 300, descansoSeg: 0, intensidade: zona(p, Z1))] + desaquecimento("bike").itens)
        let k = w <= 4 ? w : w - 4
        func intervalo(_ titulo: String, _ foco: String, _ ex: String, _ reps: Int, _ trab: Int, _ pausa: Int, _ z: ZonaBike, _ nota: String? = nil) -> Sessao {
            Sessao(titulo, foco, "bike", 0, [aq, Bloco("Série principal", .INTERVALADO, [Item(ex, reps, trabalhoSeg: trab, descansoSeg: pausa, intensidade: zona(p, z), nota: nota ?? "Pausa pedalando leve")]), volta], dia)
        }
        switch tipo {
        case "SS":
            if leve { return intervalo("Sweet spot leve", "Limiar", "bike-intervalado", 2, 480, 240, ini ? Z3 : SS) }
            if ini { return intervalo("Tempo", "Resistência", "bike-intervalado", 3, (5 + k) * 60, 240, Z3) }
            return intervalo("Sweet spot", "Limiar", "bike-intervalado", k >= 3 ? 2 : 3, [8, 10, 15, 20][Swift.min(k, 3)] * 60, 300, SS)
        case "LIM":
            if leve || ini { return sessaoBike(p, dia, "SS", w, fase) }
            return intervalo("Limiar", "FTP", "bike-intervalado", k >= 3 ? 3 : 4, [6, 8, 10, 12][Swift.min(k, 3)] * 60, 240, Z4)
        case "VO2":
            if leve { return intervalo("Ativação curta", "Manutenção", "bike-intervalado", 4, 60, 120, Z4) }
            if ini { return intervalo("Intervalado curto", "Potência aeróbica", "bike-intervalado", 6 + k, 60, 120, Z4) }
            return intervalo("VO2máx", "Potência aeróbica", "bike-intervalado", [5, 6, 5, 4][Swift.min(k, 3)], [180, 180, 240, 300][Swift.min(k, 3)], 180, Z5, "Recupere o mesmo tempo pedalando leve")
        case "CAD":
            return Sessao("Endurance + cadência", "Técnica", "bike", 0, [aq,
                Bloco("Drills de cadência", .INTERVALADO, [Item("bike-cadencia", 6, trabalhoSeg: 30, descansoSeg: 90, intensidade: "Leve · 110+ rpm", nota: "Quadril parado no selim")]),
                Bloco("Endurance", .PRINCIPAL, [Item("bike-leve", 1, trabalhoSeg: Swift.max(15, p.minutos - 30) * 60, descansoSeg: 0, intensidade: zona(p, Z2))]), volta], dia)
        case "SUB": return intervalo("Subida · força no pedal", "Força específica", "bike-subida", leve ? 3 : 4 + k / 2, 360, 180, Z3, "60–70 rpm, marcha pesada")
        case "REC": return Sessao("Recuperação ativa", "Recuperação", "bike", 0, [Bloco("Giro leve", .PRINCIPAL, [Item("bike-leve", 1, trabalhoSeg: 35 * 60, descansoSeg: 0, intensidade: zona(p, Z1))]), desaquecimento("bike")], dia)
        case "Z2": return Sessao("Endurance", "Base aeróbica", "bike", 0, [Bloco("Endurance", .PRINCIPAL, [Item("bike-leve", 1, trabalhoSeg: Swift.max(30, p.minutos - 5) * 60, descansoSeg: 0, intensidade: zona(p, Z2))]), desaquecimento("bike")], dia)
        case "F":
            var u = Set<String>()
            return Sessao("Força para ciclistas", "Prevenção e potência", "forca", 0, [aquecimento(p, "inferior", &u), forcaCorredor(p, w, nome: "Circuito de força"), desaquecimento("inferior")], dia)
        default:
            let (lo, hi): (Int, Int)
            switch p.nivel { case .iniciante: (lo, hi) = (60, 105); case .intermediario: (lo, hi) = (90, 150); case .avancado: (lo, hi) = (120, 210) }
            let prog = w <= 3 ? w - 1 : ((5...7).contains(w) ? w - 2 : 0)
            let m = leve ? lo : arred(Double(lo) + Double(hi - lo) * Double(prog) / 5.0)
            return Sessao("Longo de fim de semana", "Resistência", "bike", 0, [Bloco("Pedal longo", .PRINCIPAL, [Item("bike-leve", 1, trabalhoSeg: m * 60, descansoSeg: 0, intensidade: zona(p, Z2), nota: "Coma e beba a cada 20–30 min acima de 90 min")]), desaquecimento("bike")], dia)
        }
    }

    func planoBike(_ p: Perfil) -> Plano {
        let n = p.dias.count
        let modelo: [String]
        switch n {
        case 2: modelo = ["SS", "LONGO"]
        case 3: modelo = ["SS", "CAD", "LONGO"]
        case 4: modelo = ["VO2", "CAD", "SS", "LONGO"]
        case 5: modelo = ["VO2", "F", "LIM", "REC", "LONGO"]
        default: modelo = ["VO2", "F", "SS", (p.bikeTipo == "mtb" || p.bikeTipo == "estrada") ? "SUB" : "CAD", "REC", "LONGO"]
        }
        let semanas = (1...8).map { w -> Semana in
            var fase = faseForca(w, p.nivel)
            if fase.deload { fase.nome = "Recuperação"; fase.nota = "Semana leve: volume menor e só uma sessão intensa curta." }
            else { fase.nota = "Progressão de tempo em zona. \(p.ftp == nil ? "Sem FTP: guie-se pela percepção de esforço." : "Zonas calculadas a partir do FTP de \(p.ftp!) W.")" }
            return Semana(numero: w, fase: fase.deload ? fase.nome : (w < 4 ? "Base" : "Construção"), nota: fase.nota,
                          sessoes: p.dias.enumerated().map { (i, dia) in sessaoBike(p, dia, modelo[Swift.min(i, modelo.count - 1)], w, fase) })
        }
        var dicas: [String] = []
        if p.ftp == nil { dicas.append("Para descobrir o FTP: após aquecer, pedale 20 min no máximo sustentável; FTP ≈ 95% da potência média.") }
        dicas.append("Ajuste da bike: joelho levemente flexionado no ponto mais baixo do pedal.")
        dicas.append("Acima de 90 min, consuma 30–60 g de carboidrato por hora.")
        return Plano(nome: "Ciclismo · \(p.objetivo.nome.lowercased())", resumo: "\(n)x por semana · zonas de Coggan · sweet spot, VO2 e longo progressivo.", modalidade: p.modalidade, objetivo: p.objetivo, nivel: p.nivel, semanas: semanas,
                     dicas: dicas, alertas: [], metaSemanal: "")
    }

    // ------------------------------------------------------------------ lutas

    struct Round { let trabalho: Int, pausa: Int, rounds: Int, grappling: Bool }
    func round(_ arte: String) -> Round {
        switch arte {
        case "boxe": return Round(trabalho: 180, pausa: 60, rounds: 3, grappling: false)
        case "muay": return Round(trabalho: 180, pausa: 120, rounds: 5, grappling: false)
        case "mma": return Round(trabalho: 300, pausa: 60, rounds: 3, grappling: false)
        case "bjj": return Round(trabalho: 360, pausa: 60, rounds: 4, grappling: true)
        case "judo": return Round(trabalho: 240, pausa: 60, rounds: 4, grappling: true)
        case "wrestling": return Round(trabalho: 180, pausa: 30, rounds: 2, grappling: true)
        default: return Round(trabalho: 120, pausa: 60, rounds: 3, grappling: false)
        }
    }

    func faseLuta(_ w: Int, _ total: Int, _ marcada: Bool) -> FaseSemana {
        if !marcada { var f = faseForca(w, .intermediario); f.nome = f.deload ? "Semana leve" : (w <= 4 ? "Preparação geral" : "Preparação específica"); return f }
        let polimento = total >= 6 ? 2 : 1
        if w == total { return FaseSemana(nome: "Semana da luta", nota: "Volume mínimo, só manter a velocidade. Durma e se hidrate bem.", extraSerie: false, deload: true, variante: 1, volume: 0.4) }
        if w > total - polimento { return FaseSemana(nome: "Polimento", nota: "Volume cai, intensidade fica: chegue rápido e descansado.", extraSerie: false, deload: true, variante: 1, volume: 0.6) }
        if w <= (total - polimento) / 2 { return FaseSemana(nome: "Preparação geral", nota: "Base de força e condicionamento.", extraSerie: false, deload: false, variante: 0, volume: 1.0) }
        return FaseSemana(nome: "Preparação específica", nota: "Força vira potência; rounds no ritmo da luta.", extraSerie: true, deload: false, variante: 1, volume: 1.0)
    }

    func sessaoRounds(_ p: Perfil, _ dia: Int, _ fase: FaseSemana, _ w: Int, _ variante: Int) -> Sessao {
        let r = round(p.lutaArte)
        let sel = Seletor(self, p, nivelMax: 3)
        let drills = r.grappling ? ["sprawl", "fuga-quadril", "ponte-pescoco", "bear-crawl", "burpee", "farmer-walk"] : ["sombra", "saco-combinacoes", "sprawl", "burpee", "battle-rope", "corda"]
        var disponiveis = drills.compactMap { sel.primeiro($0) }
        if disponiveis.isEmpty { disponiveis = [cat["sombra"]].compactMap { $0 } }
        var rounds: Int
        if fase.deload { rounds = Swift.max(2, arred(Double(r.rounds) * fase.volume)) } else if fase.extraSerie { rounds = r.rounds + 1 } else { rounds = r.rounds }
        rounds += (p.nivel == .avancado && !fase.deload) ? 1 : 0
        let itens = (0..<rounds).map { i -> Item in
            let e = disponiveis[mod(i + variante + w, disponiveis.count)]
            return Item(e.id, 1, trabalhoSeg: r.trabalho, descansoSeg: r.pausa, intensidade: "Ritmo de luta · 8/10",
                        nota: r.grappling ? "Alterne 30 s explosivos e 30 s de controle" : "Picos de 10 s em máxima velocidade a cada 30 s")
        }
        let pausaMin = Double(r.pausa) / 60.0
        var usados = Set(disponiveis.map(\.id))
        var core: [Exercicio] = []
        if p.minutos >= 45 && !fase.deload {
            core = [sel.escolher("core", w, &usados), sel.escolher("core", w + 1, &usados), p.lutaArte != "karate" ? sel.primeiro("isometria-pescoco", usados: &usados) : nil].compactMap { $0 }
        }
        var u2 = Set<String>()
        var blocos = [aquecimento(p, "total", &u2),
                      Bloco("Rounds", .INTERVALADO, itens, nota: "\(rounds) rounds de \(r.trabalho / 60) min com \(pausaMin < 1 ? "\(r.pausa) s" : "\(arred(pausaMin)) min") de pausa — o formato da sua luta.")]
        if !core.isEmpty { blocos.append(Bloco("Core & pescoço", .CIRCUITO, core.map { $0.porTempo ? Item($0.id, 1, trabalhoSeg: 30, descansoSeg: 15) : Item($0.id, 1, reps: "12", descansoSeg: 15) }, voltas: 3)) }
        blocos.append(desaquecimento("total"))
        return Sessao("Condicionamento em rounds", "Específico de luta", "luta", 0, blocos, dia)
    }

    func sessaoPotencia(_ p: Perfil, _ dia: Int, _ fase: FaseSemana, titulo: String = "Potência & velocidade", comPrevencao: Bool = false) -> Sessao {
        let sel = Seletor(self, p, nivelMax: 3)
        var usados = Set<String>()
        let aq = aquecimento(p, "total", &usados)
        let ex = [sel.escolher("pliometria", fase.variante, &usados), sel.escolher("potencia", fase.variante, &usados),
                  sel.escolher("potencia_sup", 0, &usados), sel.escolher("potencia_rot", 0, &usados)].compactMap { $0 }
        let series = fase.deload ? 2 : (p.nivel == .iniciante ? 3 : 4)
        let itens = ex.map { Item($0.id, series, reps: $0.padroes.contains("pliometria") ? "4–6" : "3–5", descansoSeg: 90, intensidade: "Máxima velocidade", nota: "Pare antes de perder qualidade") }
        var blocos = [aq, Bloco("Potência", .PRINCIPAL, itens, nota: "Cada repetição o mais rápida possível. Qualidade > cansaço.")]
        if comPrevencao { blocos.append(blocoPrevencao(p, fase)) }
        else {
            let core = [sel.escolher("core", 0, &usados), sel.escolher("core", 2, &usados), p.modalidade == .luta ? sel.primeiro("isometria-pescoco", usados: &usados) : nil].compactMap { $0 }
            blocos.append(Bloco("Core", .PRINCIPAL, core.map { $0.porTempo ? Item($0.id, 3, trabalhoSeg: 30, descansoSeg: 30) : Item($0.id, 3, reps: "10–12", descansoSeg: 45) }))
        }
        blocos.append(desaquecimento("total"))
        return Sessao(titulo, "Explosão", "forca", 0, blocos, dia)
    }

    func blocoPrevencao(_ p: Perfil, _ fase: FaseSemana) -> Bloco {
        let sel = Seletor(self, p, nivelMax: 3)
        var u = Set<String>()
        let ex = [sel.primeiro("nordico", "mesa-flexora", "stiff-halteres", usados: &u), sel.primeiro("monster-walk", "ponte-unilateral", usados: &u),
                  sel.primeiro("rotacao-externa", "face-pull", "band-pull-apart", usados: &u), sel.primeiro("panturrilha-pe", "panturrilha-elastico", usados: &u),
                  sel.primeiro("prancha-lateral", usados: &u), sel.primeiro("equilibrio-unipodal", usados: &u)].compactMap { $0 }
        let s = fase.deload ? 1 : 2
        return Bloco("Prevenção de lesões", .PRINCIPAL, ex.map { $0.porTempo ? Item($0.id, s, trabalhoSeg: 30, descansoSeg: 20) : Item($0.id, s, reps: $0.id == "nordico" ? "4–6" : "10–12", descansoSeg: 45, intensidade: "Controle") },
                     nota: "Posterior, quadril, ombro e tornozelo: onde mais acontecem lesões no esporte.")
    }

    func planoLuta(_ p: Perfil) -> Plano {
        let marcada = p.lutaSemanas != nil
        let total = p.lutaSemanas ?? 8
        let n = p.dias.count
        let muitosTecnicos = p.lutaTecnicos >= 5
        var modelo: [String]
        switch n {
        case 2: modelo = ["FP", "R"]
        case 3: modelo = ["F", "R", "P"]
        case 4: modelo = ["F", "R", "P", "A"]
        case 5: modelo = ["F", "R", "P", "A", "M"]
        default: modelo = ["F", "R", "P", "A", "R2", "M"]
        }
        modelo = modelo.map { (muitosTecnicos && $0 == "R2") ? "M" : $0 }
        let forcaSlots = ["agachar", "dobradica", "empurrar_h", "puxar_v", "puxar_h", "carregar", "core"]
        let semanas = (1...total).map { w -> Semana in
            let fase = faseLuta(w, total, marcada)
            let sessoes = p.dias.enumerated().map { (i, dia) -> Sessao in
                let t = modelo[Swift.min(i, modelo.count - 1)]
                switch t {
                case "F", "FP":
                    var usados = Set<String>()
                    let aq = aquecimento(p, "total", &usados)
                    let pre: [Item] = t == "FP" ? [Seletor(self, p).escolher("pliometria", 0, &usados)].compactMap { $0 }.map { Item($0.id, 3, reps: "4–5", descansoSeg: 90, intensidade: "Máxima velocidade") } : []
                    let principal = blocoForca(p, forcaSlots, fase, Swift.max(15, p.minutos - 15), &usados, obj: .forca)
                    let pescoco = (p.lutaArte != "karate" && !p.evitar.contains("impacto")) ? cat["isometria-pescoco"] : nil
                    var blocos = [aq]
                    if !pre.isEmpty { blocos.append(Bloco("Potência", .PRINCIPAL, pre)) }
                    blocos.append(principal)
                    if let pe = pescoco { blocos.append(Bloco("Pescoço", .PRINCIPAL, [Item(pe.id, 2, trabalhoSeg: 60, descansoSeg: 30, intensidade: "Progressivo, sem dor", nota: "15 s em cada direção")])) }
                    blocos.append(desaquecimento("total"))
                    return Sessao(t == "FP" ? "Força & potência" : "Força máxima", "Força", "forca", 0, blocos, dia)
                case "R": return sessaoRounds(p, dia, fase, w, 0)
                case "R2": return sessaoRounds(p, dia, fase, w, 2)
                case "P": return sessaoPotencia(p, dia, fase)
                case "A": return sessaoCardioLeve(p, dia, Swift.min(45, p.minutos), titulo: "Base aeróbica", nota: "Melhora a recuperação entre os rounds. Ritmo de conversa.")
                default: return sessaoMobilidade(p, dia, w, 40, titulo: "Mobilidade & recuperação")
                }
            }
            return Semana(numero: w, fase: fase.nome, nota: fase.nota, sessoes: sessoes)
        }
        let arte = Questionario.perguntas.first { $0.id == "luta_arte" }!.opcoes.first { $0.valor == p.lutaArte }?.titulo ?? p.lutaArte
        var dicas = ["Os treinos técnicos de luta continuam sendo a prioridade: encaixe a força longe dos sparrings mais duros."]
        if muitosTecnicos { dicas.append("Com \(p.lutaTecnicos) treinos técnicos por semana, reduzimos o condicionamento extra para não acumular fadiga.") }
        dicas.append("Corte de peso agressivo prejudica o desempenho: planeje com nutricionista.")
        return Plano(nome: "Preparação física · \(arte)", resumo: (marcada ? "Camp de \(total) semanas até a luta" : "Bloco de 8 semanas") + " · força, potência e rounds no formato da sua luta.",
                     modalidade: p.modalidade, objetivo: p.objetivo, nivel: p.nivel, semanas: semanas, dicas: dicas, alertas: [], metaSemanal: "")
    }

    // ------------------------------------------------------------------ atletas

    func planoAtleta(_ p: Perfil) -> Plano {
        let n = p.dias.count
        let emTemporada = p.atletaFase == "em"
        let objF: Objetivo = p.atletaFase == "fora" ? .massa : .forca
        let forcaA = ["agachar", "dobradica", "empurrar_h", "puxar_h", "unilateral", "core"]
        let forcaB = ["dobradica:1", "unilateral:1", "empurrar_v", "puxar_v", "posterior", "core:1"]
        var modelo: [String]
        switch n {
        case 2: modelo = ["A+P", "B+PREV"]
        case 3: modelo = ["A", "V+P", "B+PREV"]
        case 4: modelo = ["A", "V", "B", "P+PREV"]
        case 5: modelo = ["A", "V", "B", "P+PREV", "C"]
        default: modelo = ["A", "V", "B", "P+PREV", "C", "M"]
        }
        modelo = modelo.map { (emTemporada && ["C", "V"].contains($0) && n >= 4) ? "M" : $0 }
        let semanas = (1...8).map { w -> Semana in
            let base = faseForca(w, p.nivel)
            var fase = base
            if base.deload { fase.nome = "Semana leve" }
            else if p.atletaFase == "em" { fase.nome = "Manutenção" }
            else if w <= 3 { fase.nome = p.atletaFase == "fora" ? "Hipertrofia funcional" : "Força" }
            else { fase.nome = p.atletaFase == "fora" ? "Força" : "Potência" }
            fase.nota = emTemporada ? "Em temporada: pouco volume, alta qualidade. Nunca treine pesado na véspera de jogo." : base.nota
            let obj: Objetivo = (w > 4 && p.atletaFase == "fora") ? .forca : objF
            let sessoes = p.dias.enumerated().map { (i, dia) -> Sessao in
                let m = modelo[Swift.min(i, modelo.count - 1)]
                switch m {
                case "A", "A+P", "B", "B+PREV":
                    var usados = Set<String>()
                    let aq = aquecimento(p, "total", &usados)
                    let pot: [Item] = m == "A+P" ? [Seletor(self, p).escolher("pliometria", 0, &usados)].compactMap { $0 }.map { Item($0.id, 3, reps: "4–5", descansoSeg: 90, intensidade: "Máxima velocidade") } : []
                    let minutos = emTemporada ? Swift.min(p.minutos, 45) : p.minutos
                    var faseF = fase
                    if emTemporada { faseF.deload = true; faseF.volume = 0.6 }
                    let principal = blocoForca(p, m.hasPrefix("A") ? forcaA : forcaB, faseF, Swift.max(15, minutos - 15 - (m == "B+PREV" ? 8 : 0)), &usados, obj: obj, nome: "Força")
                    var blocos = [aq]
                    if !pot.isEmpty { blocos.append(Bloco("Potência", .PRINCIPAL, pot)) }
                    blocos.append(principal)
                    if m == "B+PREV" { blocos.append(blocoPrevencao(p, fase)) }
                    blocos.append(desaquecimento("total"))
                    return Sessao(m.hasPrefix("A") ? "Força A" : "Força B", "Força", "forca", 0, blocos, dia)
                case "V", "V+P": return sessaoVelocidade(p, dia, fase, m == "V+P")
                case "P+PREV": return sessaoPotencia(p, dia, fase, titulo: "Potência & prevenção", comPrevencao: true)
                case "C": return sessaoCondicionamentoEsporte(p, dia, fase)
                default: return sessaoMobilidade(p, dia, w, 40, titulo: "Mobilidade & recuperação")
                }
            }
            return Semana(numero: w, fase: fase.nome, nota: fase.nota, sessoes: sessoes)
        }
        let esporte = Questionario.perguntas.first { $0.id == "atleta_esporte" }!.opcoes.first { $0.valor == p.atletaEsporte }?.titulo ?? p.atletaEsporte
        let faseNome = Questionario.perguntas.first { $0.id == "atleta_fase" }!.opcoes.first { $0.valor == p.atletaFase }?.titulo ?? p.atletaFase
        return Plano(nome: "Performance · \(esporte)", resumo: "\(faseNome) · força, potência, velocidade e prevenção em 8 semanas.", modalidade: p.modalidade, objetivo: p.objetivo, nivel: p.nivel, semanas: semanas,
                     dicas: ["Treine força/potência longe (24–48 h) dos jogos e treinos táticos mais intensos.", "Pliometria: qualidade de aterrissagem antes de altura ou volume.", "Durma 8–10 h: é quando a adaptação acontece."],
                     alertas: [], metaSemanal: "")
    }

    func sessaoVelocidade(_ p: Perfil, _ dia: Int, _ fase: FaseSemana, _ comPotencia: Bool) -> Sessao {
        let sel = Seletor(self, p, nivelMax: 3)
        var usados = Set<String>()
        var itens = [
            Item("educativos-corrida", 1, trabalhoSeg: 240, descansoSeg: 30, nota: "Skipping, anfersen, dribling"),
            Item("tiros", fase.deload ? 4 : 6 + fase.variante * 2, trabalhoSeg: 6, descansoSeg: 90, intensidade: "Máxima velocidade", nota: "Sprints de 20–30 m. Recuperação completa"),
        ]
        for e in [sel.primeiro("bound-lateral", usados: &usados), sel.primeiro("salto-distancia", usados: &usados)].compactMap({ $0 }) {
            itens.append(Item(e.id, 3, reps: "4–6", descansoSeg: 75, intensidade: "Explosivo"))
        }
        let aq = aquecimento(p, "corrida", &usados)
        var blocos = [aq, Bloco("Velocidade & agilidade", .PRINCIPAL, itens, nota: "Velocidade se treina descansado: pausa longa é parte do treino.")]
        if comPotencia, let e = sel.escolher("potencia_sup", 0, &usados) { blocos.append(Bloco("Potência de tronco", .PRINCIPAL, [Item(e.id, 3, reps: "5", descansoSeg: 75)])) }
        blocos.append(desaquecimento("corrida"))
        return Sessao("Velocidade & agilidade", "Velocidade", "atleta", 0, blocos, dia)
    }

    func sessaoCondicionamentoEsporte(_ p: Perfil, _ dia: Int, _ fase: FaseSemana) -> Sessao {
        switch p.atletaEsporte {
        case "resistencia": return sessaoCardioLeve(p, dia, p.minutos, titulo: "Endurance Z2", nota: "Volume aeróbico de base.")
        case "forca": var s = sessaoHiitCurta(p, dia, fase, 1); s.titulo = "Condicionamento metabólico"; return s
        default:
            var u = Set<String>()
            return Sessao("Condicionamento intermitente", "Repetição de sprints", "atleta", 0, [
                aquecimento(p, "corrida", &u),
                Bloco("Intermitente 15/15", .INTERVALADO, [Item("tiros", fase.deload ? 8 : 12, trabalhoSeg: 15, descansoSeg: 15, intensidade: "Forte · 85–90%", nota: "Simula as ações repetidas do jogo")],
                      nota: "Faça 2 séries com 3 min de pausa se estiver em boa forma."),
                desaquecimento("corrida"),
            ], dia)
        }
    }

    // ------------------------------------------------------------------ HIIT

    func planoHiit(_ p: Perfil) -> Plano {
        let (trab, pausa, voltasBase): (Int, Int, Int)
        switch p.nivel { case .iniciante: (trab, pausa, voltasBase) = (30, 30, 3); case .intermediario: (trab, pausa, voltasBase) = (40, 20, 4); case .avancado: (trab, pausa, voltasBase) = (45, 15, 5) }
        let semanas = (1...8).map { w -> Semana in
            let fase = faseForca(w, p.nivel)
            let voltas = fase.deload ? Swift.max(2, voltasBase - 1) : ([3, 7].contains(w) ? voltasBase + 1 : voltasBase)
            let sessoes = p.dias.enumerated().map { (i, dia) -> Sessao in
                let tipo = (p.dias.count >= 5 && i == p.dias.count - 1) ? 3 : i % 3
                var usados = Set<String>()
                let sel = Seletor(self, p)
                switch tipo {
                case 0:
                    let ex = [sel.escolher("agachar", w, &usados), sel.escolher("empurrar_h", w, &usados), sel.escolher("dobradica", w, &usados),
                              sel.escolher("puxar_h", w, &usados), sel.escolher("core", w, &usados), sel.escolher("condicionamento", w, &usados)].compactMap { $0 }
                    let aq = aquecimento(p, "total", &usados)
                    return Sessao("Circuito de força", "Força + fôlego", "hiit", 0, [aq,
                        Bloco("Circuito \(trab)/\(pausa)", .CIRCUITO, ex.map { Item($0.id, 1, trabalhoSeg: trab, descansoSeg: pausa, intensidade: "Forte · 7–8/10") }, voltas: voltas, nota: "Descanse 1 min entre as voltas."),
                        desaquecimento("total")], dia)
                case 1:
                    let pares = [sel.escolher("condicionamento", w, &usados), sel.escolher("agachar", w + 1, &usados), sel.escolher("condicionamento", w + 1, &usados), sel.escolher("core", w + 1, &usados)].compactMap { $0 }
                    let tabatas = fase.deload ? 2 : (p.nivel == .iniciante ? 2 : Swift.min(4, pares.count))
                    let aq = aquecimento(p, "total", &usados)
                    let tb = pares.prefix(tabatas).enumerated().map { (k, e) in Bloco("Tabata \(k + 1)", .INTERVALADO, [Item(e.id, 8, trabalhoSeg: 20, descansoSeg: 10, intensidade: "Máximo · 9/10")], nota: "8 × 20 s / 10 s. 1 min de pausa entre os tabatas.") }
                    return Sessao("Tabata", "Intervalado máximo", "hiit", 0, [aq] + tb + [desaquecimento("total")], dia)
                case 2:
                    let ex = [sel.escolher("potencia", w, &usados), sel.escolher("unilateral", w, &usados), sel.escolher("empurrar_v", w, &usados),
                              sel.escolher("condicionamento", w + 2, &usados), sel.escolher("core", w + 2, &usados)].compactMap { $0 }
                    let aq = aquecimento(p, "total", &usados)
                    return Sessao("EMOM funcional", "Potência e ritmo", "hiit", 0, [aq,
                        Bloco("A cada minuto", .CIRCUITO, ex.map { Item($0.id, 1, trabalhoSeg: 40, descansoSeg: 20, intensidade: "Ritmo constante") }, voltas: voltas, nota: "Um exercício por minuto: trabalhe 40 s e use o resto do minuto para respirar."),
                        desaquecimento("total")], dia)
                default: return sessaoMobilidade(p, dia, w, 40, titulo: "Mobilidade ativa")
                }
            }
            return Semana(numero: w, fase: fase.nome, nota: fase.deload ? "Semana leve: menos voltas, mesma qualidade." : "Mais voltas nas semanas 3 e 7. Respeite as pausas.", sessoes: sessoes)
        }
        return Plano(nome: "HIIT & funcional", resumo: "Circuitos \(trab)/\(pausa), Tabata e EMOM · \(p.dias.count)x por semana.", modalidade: p.modalidade, objetivo: p.objetivo, nivel: p.nivel, semanas: semanas,
                     dicas: ["HIIT é intenso: 2–4 sessões por semana costumam bastar; nos outros dias, prefira atividades leves.", "Técnica primeiro. Se perder a forma, reduza o ritmo, não a amplitude."],
                     alertas: [], metaSemanal: "")
    }

    // ------------------------------------------------------------------ híbrido

    func planoHibrido(_ p: Perfil) -> Plano {
        let n = p.dias.count
        let bike = p.cardioHibrido == "bike"
        let modelo: [String]
        switch n {
        case 2: modelo = ["FA", "CL"]
        case 3: modelo = ["FA", "CQ", "FB"]
        case 4: modelo = ["U", "CQ", "L", "CL"]
        case 5: modelo = ["U", "CQ", "L", "CE", "FC"]
        default: modelo = ["U", "CQ", "L", "CE", "FC", "CL"]
        }
        let meta = ["5k", "10k"].contains(p.corridaMeta) ? p.corridaMeta : "ritmo"
        let semanas = (1...8).map { w -> Semana in
            let fase = faseForca(w, p.nivel)
            let sessoes = p.dias.enumerated().map { (i, dia) -> Sessao in
                switch modelo[Swift.min(i, modelo.count - 1)] {
                case "FA": return sessaoForca(p, Modelo(titulo: "Força · corpo inteiro A", foco: "Corpo inteiro", aq: "total", slots: FULL_A), dia, fase)
                case "FB": return sessaoForca(p, Modelo(titulo: "Força · corpo inteiro B", foco: "Corpo inteiro", aq: "total", slots: FULL_B), dia, fase)
                case "FC": return sessaoForca(p, Modelo(titulo: "Força · corpo inteiro C", foco: "Corpo inteiro", aq: "total", slots: FULL_C), dia, fase)
                case "U": return sessaoForca(p, Modelo(titulo: "Força · superiores", foco: "Peito, costas e ombros", aq: "superior", slots: UPPER_A), dia, fase)
                case "L": return sessaoForca(p, Modelo(titulo: "Força · inferiores", foco: "Pernas e glúteos", aq: "inferior", slots: LOWER_A), dia, fase)
                case "CQ": return bike ? sessaoBike(p, dia, w % 2 == 0 ? "VO2" : "SS", w, fase) : (p.correContinuo ? sessaoCorrida(p, dia, w % 2 == 0 ? "T" : "Q", w, 8, meta) : sessaoCaminhaCorre(p, dia, w, 0))
                case "CE": return bike ? sessaoBike(p, dia, "Z2", w, fase) : (p.correContinuo ? sessaoCorrida(p, dia, "E", w, 8, meta) : sessaoCaminhaCorre(p, dia, w, 1))
                default: return bike ? sessaoBike(p, dia, "LONGO", w, fase) : (p.correContinuo ? sessaoCorrida(p, dia, "L", w, 8, meta) : sessaoCaminhaCorre(p, dia, w, 2))
                }
            }
            return Semana(numero: w, fase: fase.nome, nota: "Separe força de pernas e treinos intensos de \(bike ? "bike" : "corrida") por pelo menos 24 h quando possível.", sessoes: sessoes)
        }
        return Plano(nome: "Híbrido · força + \(bike ? "bike" : "corrida")", resumo: "\(n)x por semana · força 2–3x e cardio estruturado · 8 semanas.", modalidade: p.modalidade, objetivo: p.objetivo, nivel: p.nivel, semanas: semanas,
                     dicas: ["Treino concorrente funciona: só evite colocar o cardio intenso logo antes do treino de pernas.", "Mantenha a maior parte do cardio em intensidade leve (zona 2)."],
                     alertas: [], metaSemanal: "")
    }

    // ------------------------------------------------------------------ mobilidade e 50+

    func planoMobilidade(_ p: Perfil) -> Plano {
        let inicial: Int
        switch p.nivel { case .iniciante: inicial = 30; case .intermediario: inicial = 40; case .avancado: inicial = 50 }
        let semanas = (1...8).map { w -> Semana in
            let hold = Swift.min(inicial + (w >= 3 ? 10 : 0) + (w >= 6 ? 10 : 0), 75)
            return Semana(numero: w, fase: w <= 2 ? "Consciência" : (w <= 5 ? "Amplitude" : "Controle"), nota: "Segure cada posição por ~\(hold) s, respirando devagar. Nunca force até doer.",
                          sessoes: p.dias.enumerated().map { (i, dia) in sessaoMobilidade(p, dia, i + w, hold) })
        }
        return Plano(nome: "Mobilidade & alongamento", resumo: "\(p.dias.count) sessões por semana de coluna, quadril, ombros e pernas · 8 semanas.", modalidade: p.modalidade, objetivo: p.objetivo, nivel: p.nivel, semanas: semanas,
                     dicas: ["Alongamento estático rende mais depois do treino ou em sessão separada (ACSM: 10–30 s, 2–4 repetições).", "Antes de treinar, prefira mobilidade dinâmica."],
                     alertas: [], metaSemanal: "")
    }

    func planoLongevidade(_ p: Perfil) -> Plano {
        let n = p.dias.count
        let a = ["agachar", "empurrar_h", "puxar_h", "gluteo", "panturrilha", "carregar"]
        let b = ["unilateral", "empurrar_v", "puxar_v", "dobradica", "core", "ombro_post"]
        let modelo: [String]
        switch n {
        case 2: modelo = ["A", "B"]
        case 3: modelo = ["A", "CAM", "B"]
        case 4: modelo = ["A", "CAM", "B", "MOB"]
        case 5: modelo = ["A", "CAM", "B", "CAM", "MOB"]
        default: modelo = ["A", "CAM", "B", "CAM", "A2", "MOB"]
        }
        let semanas = (1...8).map { w -> Semana in
            let fase = faseForca(w, .iniciante)
            let sessoes = p.dias.enumerated().map { (i, dia) -> Sessao in
                let t = modelo[Swift.min(i, modelo.count - 1)]
                switch t {
                case "A", "A2", "B":
                    var usados = Set<String>()
                    let aq = aquecimento(p, "total", &usados)
                    var f2 = fase; f2.variante = fase.variante + (t == "A2" ? 1 : 0)
                    let principal = blocoForca(p, t == "B" ? b : a, f2, Swift.max(15, p.minutos - 15), &usados, obj: .saude, principais: 3)
                    let eq = cat["equilibrio-unipodal"]!
                    return Sessao(t == "B" ? "Força funcional B" : "Força funcional A", "Força e equilíbrio", "forca", 0, [aq, principal,
                        Bloco("Equilíbrio", .PRINCIPAL, [Item(eq.id, 2, trabalhoSeg: 60, descansoSeg: 20, nota: "30 s cada perna, perto de um apoio")]),
                        desaquecimento("total")], dia)
                case "CAM":
                    var pc = p; pc.emCasa = true; pc.equip.remove("esteira")
                    return sessaoCardioLeve(pc, dia, Swift.min(p.minutos, 20 + w * 3), titulo: "Caminhada", nota: "Passo firme: dá para conversar, mas não para cantar.")
                default: return sessaoMobilidade(p, dia, w, 30, titulo: "Mobilidade & equilíbrio")
                }
            }
            return Semana(numero: w, fase: fase.nome, nota: "Força 2x por semana preserva músculos, ossos e autonomia (OMS 2020).", sessoes: sessoes)
        }
        return Plano(nome: "Força, equilíbrio e longevidade", resumo: "\(n)x por semana · força funcional, equilíbrio e caminhada.", modalidade: p.modalidade, objetivo: p.objetivo, nivel: p.nivel, semanas: semanas,
                     dicas: ["Levante-se devagar após exercícios no chão para evitar tontura.", "Prefira calçado firme e um apoio por perto nos exercícios de equilíbrio."],
                     alertas: [], metaSemanal: "")
    }

    // ------------------------------------------------------------------ alertas

    func alertas(_ p: Perfil) -> [String] {
        var l: [String] = []
        if !p.parq.isEmpty { l.append("Você marcou itens da triagem PAR-Q+. Procure liberação médica antes de começar e comece com intensidade leve.") }
        if p.gestante { l.append("Gestação ou pós-parto: treine somente com liberação médica. Evite impacto, esforço máximo e longos períodos deitada de barriga para cima após o 1º trimestre. Removemos exercícios de impacto.") }
        let lim = p.evitar.subtracting(["impacto"])
        if !lim.isEmpty {
            // Mesma ordem do LinkedHashSet do Kotlin: ordem em que as limitações aparecem nas respostas
            let ordem = ["joelho", "lombar", "ombro", "punho"]
            let lista = (p.ordemLimitacoes.isEmpty ? ordem : p.ordemLimitacoes).filter { lim.contains($0) }
            l.append("Adaptamos os exercícios para: \(lista.joined(separator: ", ")). Se a dor aumentar durante ou após o treino, pare e procure um fisioterapeuta.")
        }
        if p.idade < 18 { l.append("Menor de 18 anos: treine com supervisão de um profissional, priorizando técnica antes da carga.") }
        if p.nivel == .iniciante && p.imc >= 32 && p.modalidade != .mobilidade && p.modalidade != .bike { l.append("Priorizamos exercícios de baixo impacto para proteger as articulações no começo.") }
        return l
    }

    // ------------------------------------------------------------------ tabelas

    static let BILATERAL: Set<String> = ["flexor-quadril", "alongamento-quadriceps", "alongamento-panturrilha", "alongamento-posterior", "maior-alongamento", "alongamento-peito", "rotacao-toracica", "rolo-it", "rolo-panturrilha"]

    static let CLASSICOS: Set<String> = [
        "supino-reto", "supino-halteres", "agachamento-barra", "leg-press", "stiff", "remada-curvada", "remada-baixa", "remada-unilateral",
        "puxada-frente", "barra-fixa", "desenvolvimento-halteres", "elevacao-lateral", "rosca-direta", "triceps-polia", "flexao",
        "agachamento-livre", "agachamento-goblet", "ponte-gluteo", "elevacao-quadril", "afundo", "prancha", "crucifixo", "mesa-flexora",
        "panturrilha-pe", "face-pull", "remada-elastico", "supino-elastico", "agachamento-elastico", "desenvolvimento-elastico",
    ]

    static let FALLBACK: [String: [String]] = [
        "puxar_v": ["puxar_h", "ombro_post"], "puxar_h": ["puxar_v", "ombro_post"],
        "empurrar_v": ["empurrar_h", "ombro_lat"], "empurrar_h": ["empurrar_v"],
        "dobradica": ["gluteo", "posterior"], "posterior": ["dobradica", "gluteo"],
        "quadriceps": ["agachar", "unilateral"], "unilateral": ["agachar", "gluteo"], "agachar": ["unilateral", "gluteo"],
        "peito_iso": ["empurrar_h"], "ombro_lat": ["ombro_post", "empurrar_v"], "ombro_post": ["puxar_h"],
        "trapezio": ["ombro_post"], "biceps": ["puxar_h"], "triceps": ["empurrar_h"], "gluteo": ["dobradica", "unilateral"],
        "pliometria": ["condicionamento"], "potencia": ["pliometria", "condicionamento"], "potencia_sup": ["empurrar_h"],
        "potencia_rot": ["core"], "carregar": ["core"], "condicionamento": ["core"],
    ]

    public static let DICAS_GERAIS = [
        "Pare imediatamente se sentir dor no peito, falta de ar desproporcional, tontura ou palpitações.",
        "Durma bem e beba água: recuperação é parte do treino.",
    ]
}
