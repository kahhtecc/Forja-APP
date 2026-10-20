import SwiftUI

/// Animações 3D pré-renderizadas: folha de quadros (grade) por exercício em anim3d/<id>.webp + meta.json.
final class Animacoes3D {
    struct Meta { let quadros: Int, colunas: Int, lado: Int, fps: Double }
    static let shared = Animacoes3D()
    private var meta: [String: Meta]?
    private let quadros = NSCache<NSString, NSArray>()
    private let trava = NSLock()

    init() { quadros.countLimit = 4 }

    func limpar() { trava.lock(); meta = nil; trava.unlock(); quadros.removeAllObjects() }

    func metaDe(_ id: String) -> Meta? {
        trava.lock(); defer { trava.unlock() }
        if meta == nil {
            var m: [String: Meta] = [:]
            if let d = Conteudo.dados("anim3d/meta.json"), let o = try? JSONSerialization.jsonObject(with: d) as? [String: [String: Any]] {
                for (k, x) in o {
                    guard let f = x["f"] as? Int, let c = x["c"] as? Int, let s = x["s"] as? Int else { continue }
                    m[k] = Meta(quadros: f, colunas: c, lado: s, fps: (x["fps"] as? NSNumber)?.doubleValue ?? 6)
                }
            }
            meta = m
        }
        return meta?[id]
    }

    func tem(_ id: String) -> Bool { metaDe(id) != nil }

    /// Recorta a folha em quadros (feito uma vez por exercício, fora da thread principal).
    func quadrosDe(_ id: String) -> [UIImage]? {
        if let a = quadros.object(forKey: id as NSString) as? [UIImage] { return a }
        guard let m = metaDe(id), let d = Conteudo.dados("anim3d/\(id).webp"), let folha = UIImage(data: d)?.cgImage else { return nil }
        var lista: [UIImage] = []
        for q in 0..<m.quadros {
            let r = CGRect(x: (q % m.colunas) * m.lado, y: (q / m.colunas) * m.lado, width: m.lado, height: m.lado)
            if let c = folha.cropping(to: r) { lista.append(UIImage(cgImage: c)) }
        }
        quadros.setObject(lista as NSArray, forKey: id as NSString)
        return lista
    }
}

/// Toca a animação 3D em loop (ou mostra o quadro do meio, se animar = false).
struct Animacao3DView: View {
    let id: String
    var animar = true
    @State private var lista: [UIImage]?

    var body: some View {
        let m = Animacoes3D.shared.metaDe(id)
        ZStack {
            Cor.sup2
            if let lista, !lista.isEmpty, let m {
                if animar {
                    TimelineView(.animation(minimumInterval: 1 / m.fps, paused: false)) { ctx in
                        let i = Int(ctx.date.timeIntervalSinceReferenceDate * m.fps) % lista.count
                        Image(uiImage: lista[i]).resizable().scaledToFill()
                    }
                } else {
                    Image(uiImage: lista[lista.count / 2]).resizable().scaledToFill()
                }
            }
        }
        .task(id: id) {
            let alvo = id
            lista = await Task.detached(priority: .userInitiated) { Animacoes3D.shared.quadrosDe(alvo) }.value
        }
    }
}
