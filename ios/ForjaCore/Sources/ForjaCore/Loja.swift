import Foundation

public protocol Armazenamento: AnyObject {
    func ler(_ chave: String) -> String?
    func gravar(_ chave: String, _ valor: String?)
}

public final class MemoriaArmazenamento: Armazenamento {
    public var m: [String: String] = [:]
    public init() {}
    public func ler(_ chave: String) -> String? { m[chave] }
    public func gravar(_ chave: String, _ valor: String?) { m[chave] = valor }
}

public struct Ajustes: Codable, Equatable, Sendable {
    public var som = true, vibracao = true, telaLigada = true
    public init(som: Bool = true, vibracao: Bool = true, telaLigada: Bool = true) { self.som = som; self.vibracao = vibracao; self.telaLigada = telaLigada }
}

public struct PesoRegistro: Codable, Equatable, Sendable { public var dia: Int; public var kg: Double }

public struct Estado: Sendable {
    public var respostas: Respostas = [:]
    public var inicio: Int = 0
    public var trocas: [String: String] = [:]
    public var registros: [Registro] = []
    public var pesos: [PesoRegistro] = []
    public var ajustes = Ajustes()
    public var perfil: Perfil? = nil
    public var plano: Plano? = nil
    public var temPlano: Bool { plano != nil }
}

/// Estado do app + persistência (porte de Loja.kt). Sem dependência de UI.
public final class Loja {
    public let catalogo: Catalogo
    private let arm: Armazenamento
    private let relogio: () -> Int
    private let gerador: Gerador
    public private(set) var estado = Estado()
    public var aoMudar: ((Estado) -> Void)?

    public init(catalogo: Catalogo, armazenamento: Armazenamento, hoje: @escaping () -> Int = { Datas.hoje() }) {
        self.catalogo = catalogo; self.arm = armazenamento; self.relogio = hoje; self.gerador = Gerador(catalogo)
        estado = carregar()
    }

    public func hoje() -> Int { relogio() }

    static let K_RESP = "respostas", K_INICIO = "inicio", K_TROCAS = "trocas", K_REG = "registros", K_PESOS = "pesos", K_AJ = "ajustes"

    private func publicar() { estado = carregar(); aoMudar?(estado) }
    private func json<T: Encodable>(_ v: T) -> String? { (try? JSONEncoder().encode(v)).flatMap { String(data: $0, encoding: .utf8) } }
    private func de<T: Decodable>(_ s: String?, _ t: T.Type) -> T? { s.flatMap { $0.data(using: .utf8) }.flatMap { try? JSONDecoder().decode(t, from: $0) } }

    public func salvarRespostas(_ r: Respostas, manterHistorico: Bool = true) {
        arm.gravar(Loja.K_RESP, json(Questionario.limpar(r)))
        arm.gravar(Loja.K_INICIO, String(Datas.segunda(hoje())))
        arm.gravar(Loja.K_TROCAS, nil)
        if !manterHistorico { arm.gravar(Loja.K_REG, nil) }
        publicar()
    }
    public func recomecarPlano() { arm.gravar(Loja.K_INICIO, String(Datas.segunda(hoje()))); publicar() }
    public func definirInicio(_ dia: Int) { arm.gravar(Loja.K_INICIO, String(dia)); publicar() }
    public func registrar(_ r: Registro) { arm.gravar(Loja.K_REG, json(estado.registros + [r])); publicar() }
    public func apagarRegistro(_ r: Registro) {
        var l = estado.registros
        if let i = l.firstIndex(of: r) { l.remove(at: i) }
        arm.gravar(Loja.K_REG, json(l)); publicar()
    }
    public func trocar(_ sessaoIdx: Int, _ original: String, _ novo: String?) {
        var t = estado.trocas
        let chave = "\(sessaoIdx)|\(original)"
        if novo == nil || novo == original { t.removeValue(forKey: chave) } else { t[chave] = novo }
        arm.gravar(Loja.K_TROCAS, json(t)); publicar()
    }
    public func registrarPeso(_ kg: Double, dia: Int? = nil) {
        let d = dia ?? hoje()
        let l = (estado.pesos.filter { $0.dia != d } + [PesoRegistro(dia: d, kg: kg)]).sorted { $0.dia < $1.dia }
        arm.gravar(Loja.K_PESOS, json(l)); publicar()
    }
    public func salvarAjustes(_ a: Ajustes) { arm.gravar(Loja.K_AJ, json(a)); estado.ajustes = a; aoMudar?(estado) }
    public func apagarTudo() { for k in [Loja.K_RESP, Loja.K_INICIO, Loja.K_TROCAS, Loja.K_REG, Loja.K_PESOS, Loja.K_AJ] { arm.gravar(k, nil) }; publicar() }

    public func semanaAtual() -> Int { Progresso.semanaAtual(estado.inicio, hoje(), estado.plano?.semanas.count ?? 1) }

    public func sessaoDeHoje() -> (Int, Sessao)? {
        guard let p = estado.plano else { return nil }
        let dia = Datas.diaSemana(hoje())
        let s = p.semanas[semanaAtual() - 1].sessoes
        guard let i = s.firstIndex(where: { $0.diaSemana == dia }) else { return nil }
        return (i, s[i])
    }

    public func proximaSessao() -> (Int, Sessao)? {
        guard let p = estado.plano else { return nil }
        let w = semanaAtual()
        let feitas = Progresso.feitas(estado.registros, w)
        let dia = Datas.diaSemana(hoje())
        let s = p.semanas[w - 1].sessoes
        let pend = s.enumerated().filter { !feitas.contains($0.offset) }
        if let x = pend.first(where: { $0.element.diaSemana >= dia }) ?? pend.first { return (x.offset, x.element) }
        return nil
    }

    private func carregar() -> Estado {
        var e = Estado()
        e.respostas = de(arm.ler(Loja.K_RESP), Respostas.self) ?? [:]
        e.inicio = arm.ler(Loja.K_INICIO).flatMap { Int($0) } ?? Datas.segunda(hoje())
        e.trocas = de(arm.ler(Loja.K_TROCAS), [String: String].self) ?? [:]
        e.registros = de(arm.ler(Loja.K_REG), [Registro].self) ?? []
        e.pesos = de(arm.ler(Loja.K_PESOS), [PesoRegistro].self) ?? []
        e.ajustes = de(arm.ler(Loja.K_AJ), Ajustes.self) ?? Ajustes()
        if !e.respostas.isEmpty && Questionario.completo(e.respostas) {
            let perfil = Perfil.de(e.respostas)
            e.perfil = perfil
            e.plano = aplicarTrocas(gerador.gerar(perfil), e.trocas)
        }
        return e
    }

    private func aplicarTrocas(_ p: Plano, _ trocas: [String: String]) -> Plano {
        if trocas.isEmpty { return p }
        var p = p
        for w in p.semanas.indices {
            for (i, _) in p.semanas[w].sessoes.enumerated() {
                for b in p.semanas[w].sessoes[i].blocos.indices {
                    let tipo = p.semanas[w].sessoes[i].blocos[b].tipo
                    for k in p.semanas[w].sessoes[i].blocos[b].itens.indices {
                        var it = p.semanas[w].sessoes[i].blocos[b].itens[k]
                        guard let novo = trocas["\(i)|\(it.exId)"], let ex = catalogo[novo] else { continue }
                        if ex.porTempo && it.reps != nil { it.reps = nil; it.trabalhoSeg = 40 }
                        else if !ex.porTempo && it.reps == nil && tipo == .PRINCIPAL { it.reps = "10–12"; it.trabalhoSeg = nil }
                        it.exId = novo
                        p.semanas[w].sessoes[i].blocos[b].itens[k] = it
                    }
                }
            }
        }
        return p
    }
}
