import Foundation

/// Um passo do player: uma série (ou rodada) de um exercício, seguida de descanso.
public struct Passo: Equatable, Sendable {
    public let blocoIdx: Int
    public let itemIdx: Int
    public let blocoNome: String
    public let tipoBloco: TipoBloco
    public let ex: Exercicio
    public let item: Item
    public let serie: Int
    public let totalSeries: Int
    public let circuito: Bool
    public var descansoDepois: Int

    public var porTempo: Bool { item.trabalhoSeg != nil }
    public var rotulo: String { circuito ? "Volta \(serie) de \(totalSeries)" : (totalSeries > 1 ? "Série \(serie) de \(totalSeries)" : "Série única") }
}

public enum Roteiro {
    public static let SEG_SERIE_REPS = 40

    public static func passos(_ s: Sessao, _ cat: Catalogo) -> [Passo] {
        var out: [Passo] = []
        for (bi, b) in s.blocos.enumerated() {
            if b.tipo == .CIRCUITO {
                if b.voltas >= 1 {
                    for v in 1...b.voltas {
                        for (ii, it) in b.itens.enumerated() {
                            guard let ex = cat[it.exId] else { continue }
                            let ultimo = ii == b.itens.count - 1
                            let desc = (ultimo && v < b.voltas) ? Swift.max(it.descansoSeg, 60) : it.descansoSeg
                            out.append(Passo(blocoIdx: bi, itemIdx: ii, blocoNome: b.nome, tipoBloco: b.tipo, ex: ex, item: it, serie: v, totalSeries: b.voltas, circuito: true, descansoDepois: desc))
                        }
                    }
                }
            } else {
                for (ii, it) in b.itens.enumerated() {
                    guard let ex = cat[it.exId], it.series >= 1 else { continue }
                    for sr in 1...it.series {
                        out.append(Passo(blocoIdx: bi, itemIdx: ii, blocoNome: b.nome, tipoBloco: b.tipo, ex: ex, item: it, serie: sr, totalSeries: it.series, circuito: false, descansoDepois: it.descansoSeg))
                    }
                }
            }
        }
        if !out.isEmpty { out[out.count - 1].descansoDepois = 0 }
        return out
    }

    public static func segundosItem(_ it: Item) -> Int {
        let trabalho = it.trabalhoSeg ?? SEG_SERIE_REPS
        return it.series * trabalho + Swift.max(it.series - 1, 0) * it.descansoSeg
    }

    public static func segundos(_ passos: [Passo]) -> Int { passos.reduce(0) { $0 + ($1.item.trabalhoSeg ?? SEG_SERIE_REPS) + $1.descansoDepois } }

    public static func minutos(_ s: Sessao, _ cat: Catalogo) -> Int {
        let p = passos(s, cat)
        var vistos = Set<String>()
        for x in p { vistos.insert("\(x.blocoIdx)-\(x.itemIdx)") }
        let trocas = vistos.count * 15
        return Swift.max(Int(ceil(Double(segundos(p) + trocas) / 60.0)), 5)
    }

    public static func exerciciosDaSessao(_ s: Sessao) -> [String] {
        var vistos = Set<String>(); var out: [String] = []
        for b in s.blocos { for it in b.itens where !vistos.contains(it.exId) { vistos.insert(it.exId); out.append(it.exId) } }
        return out
    }

    public static func formatarTempo(_ seg: Int) -> String {
        if seg >= 3600 { return String(format: "%dh%02d", seg / 3600, (seg % 3600) / 60) }
        if seg >= 60 && seg % 60 == 0 { return "\(seg / 60) min" }
        if seg >= 60 { return String(format: "%d:%02d", seg / 60, seg % 60) }
        return "\(seg) s"
    }

    public static func prescricao(_ it: Item, circuito: Bool = false, voltas: Int = 1) -> String {
        let n = circuito ? voltas : it.series
        if circuito { return it.reps ?? it.trabalhoSeg.map { formatarTempo($0) } ?? "" }
        if let r = it.reps { return "\(n) × \(r)" }
        if let t = it.trabalhoSeg, n == 1 { return formatarTempo(t) }
        if let t = it.trabalhoSeg, it.descansoSeg > 0 { return "\(n) × \(formatarTempo(t)) / \(formatarTempo(it.descansoSeg))" }
        if let t = it.trabalhoSeg { return "\(n) × \(formatarTempo(t))" }
        return "\(n) séries"
    }
}
