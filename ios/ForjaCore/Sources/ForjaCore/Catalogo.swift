import Foundation

public final class Catalogo: @unchecked Sendable {
    public let exercicios: [Exercicio]
    private let porId: [String: Exercicio]

    public init(_ exercicios: [Exercicio]) {
        self.exercicios = exercicios
        var m: [String: Exercicio] = [:]
        for e in exercicios { m[e.id] = e }
        porId = m
    }

    public subscript(_ id: String) -> Exercicio? { porId[id] }
    public func exigir(_ id: String) -> Exercicio { guard let e = porId[id] else { fatalError("Exercício desconhecido: \(id)") }; return e }

    /// Alternativas com o mesmo padrão de movimento (para "trocar exercício").
    public func alternativas(_ ex: Exercicio, equip: Set<String>, evitar: Set<String>) -> [Exercicio] {
        exercicios.filter { o in
            o.id != ex.id && o.padroes.contains(where: { ex.padroes.contains($0) }) &&
                o.equip.contains(where: { equip.contains($0) }) && !o.evitar.contains(where: { evitar.contains($0) })
        }
    }

    public func grupos() -> [String] {
        var vistos = Set<String>(); var out: [String] = []
        for e in exercicios where !vistos.contains(e.grupo) { vistos.insert(e.grupo); out.append(e.grupo) }
        return out
    }

    public static func deJson(_ dados: Data) throws -> Catalogo {
        guard let arr = try JSONSerialization.jsonObject(with: dados) as? [[String: Any]] else { throw NSError(domain: "Forja", code: 1) }
        let lista = arr.map { o -> Exercicio in
            func strs(_ k: String) -> [String] { (o[k] as? [String]) ?? [] }
            let v = o["video"] as? [String: Any]
            return Exercicio(
                id: o["id"] as? String ?? "", nome: o["nome"] as? String ?? "", equip: strs("equip"), grupo: o["grupo"] as? String ?? "",
                tipo: o["tipo"] as? String ?? "", nivel: o["nivel"] as? Int ?? 1, dicas: strs("dicas"),
                busca: o["busca"] as? String ?? (o["nome"] as? String ?? ""), padroes: strs("padroes"), evitar: strs("evitar"),
                temImagem: o["img"] as? Bool ?? false,
                video: v.map { Video(id: $0["id"] as? String ?? "", titulo: $0["titulo"] as? String ?? "", canal: $0["canal"] as? String ?? "", idioma: $0["idioma"] as? String ?? "") })
        }
        return Catalogo(lista)
    }
}
