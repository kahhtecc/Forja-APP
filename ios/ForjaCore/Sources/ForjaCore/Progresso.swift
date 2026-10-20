import Foundation

public enum Datas {
    /// 1 = segunda ... 7 = domingo (1970-01-01 foi quinta).
    public static func diaSemana(_ epochDay: Int) -> Int { mod(epochDay + 3, 7) + 1 }
    public static func segunda(_ epochDay: Int) -> Int { epochDay - (diaSemana(epochDay) - 1) }
    /// Dia atual (fuso local) contado desde 1970-01-01.
    public static func hoje(_ data: Date = Date()) -> Int {
        let c = Calendar(identifier: .gregorian).dateComponents(in: .current, from: data)
        var g = Calendar(identifier: .gregorian); g.timeZone = TimeZone(identifier: "UTC")!
        let d = g.date(from: DateComponents(year: c.year, month: c.month, day: c.day))!
        return Int(floor(d.timeIntervalSince1970 / 86400))
    }
    public static func data(_ epochDay: Int) -> Date {
        var g = Calendar(identifier: .gregorian); g.timeZone = TimeZone(identifier: "UTC")!
        let utc = Date(timeIntervalSince1970: Double(epochDay) * 86400)
        let c = g.dateComponents([.year, .month, .day], from: utc)
        return Calendar.current.date(from: c) ?? utc
    }
}

public struct Recorde: Equatable, Sendable { public let exId: String, kg: Double, reps: Int, rm1: Double, epochDay: Int }

public enum Progresso {
    public static func semanaAtual(_ inicio: Int, _ hoje: Int, _ total: Int) -> Int {
        let w = Swift.max(hoje - inicio, 0) / 7 + 1
        return Swift.min(Swift.max(w, 1), Swift.max(total, 1))
    }
    public static func feitas(_ r: [Registro], _ semana: Int) -> Set<Int> { Set(r.filter { $0.semana == semana }.map(\.sessaoIdx)) }

    public static func sequenciaSemanas(_ r: [Registro], _ plano: Plano, _ atual: Int) -> Int {
        func completa(_ w: Int) -> Bool { w >= 1 && w <= plano.semanas.count && feitas(r, w).count >= plano.semanas[w - 1].sessoes.count }
        var w = completa(atual) ? atual : atual - 1
        var n = 0
        while w >= 1 && completa(w) { n += 1; w -= 1 }
        return n
    }

    public static func minutosPorSemana(_ r: [Registro], _ hoje: Int, semanas: Int = 8) -> [(Int, Int)] {
        let seg = Datas.segunda(hoje)
        return (0..<semanas).reversed().map { k in
            let ini = seg - 7 * k
            return (ini, r.filter { $0.epochDay >= ini && $0.epochDay < ini + 7 }.reduce(0) { $0 + $1.duracaoSeg } / 60)
        }
    }

    public static func volumeKg(_ r: Registro) -> Double { r.series.reduce(0) { $0 + $1.kg * Double($1.reps) } }
    public static func epley(_ kg: Double, _ reps: Int) -> Double { reps <= 1 ? kg : kg * (1 + Double(reps) / 30.0) }

    public static func recordes(_ regs: [Registro]) -> [Recorde] {
        var melhor: [String: Recorde] = [:]
        for r in regs { for s in r.series where s.kg > 0 && s.reps > 0 {
            let rm = epley(s.kg, s.reps)
            if (melhor[s.exId]?.rm1 ?? -1) < rm { melhor[s.exId] = Recorde(exId: s.exId, kg: s.kg, reps: s.reps, rm1: rm, epochDay: r.epochDay) }
        } }
        return melhor.values.sorted { $0.epochDay > $1.epochDay }
    }

    public static func ultimas(_ regs: [Registro], _ exId: String) -> [SerieFeita] {
        regs.sorted { $0.epochDay > $1.epochDay }.first { $0.series.contains { $0.exId == exId } }?.series.filter { $0.exId == exId } ?? []
    }

    public static func sugestao(_ regs: [Registro], _ item: Item) -> String? {
        let ult = ultimas(regs, item.exId).filter { $0.kg > 0 }
        guard !ult.isEmpty, let reps = item.reps else { return nil }
        guard let topo = Int(reps.components(separatedBy: CharacterSet(charactersIn: "–-")).last?.trimmingCharacters(in: .whitespaces) ?? "") else { return nil }
        let kg = ult.map(\.kg).max()!
        if ult.allSatisfy({ $0.reps >= topo }) {
            let novo = (kg * 1.05 / 0.5).rounded() * 0.5
            return "Você bateu o topo da faixa com \(fmtKg(kg)) kg. Tente \(fmtKg(Swift.max(novo, kg + 1.0))) kg."
        }
        return "Última vez: \(ult.map { "\($0.reps)×\(fmtKg($0.kg))" }.joined(separator: " · ")) kg. Busque mais repetições."
    }

    public static func fmtKg(_ kg: Double) -> String {
        kg.truncatingRemainder(dividingBy: 1) == 0 ? "\(Int(kg))" : String(format: "%.1f", kg).replacingOccurrences(of: ".", with: ",")
    }
}
