import Foundation
import CryptoKit

/// Conteúdo atualizável sem reinstalar (mesmo esquema do Android, ver Conteudo.kt):
/// o app traz exercises.json, fontes.json e anim3d/ com um manifesto (versão + SHA-1).
/// Ao abrir, baixa o manifesto publicado; se a versão for maior, baixa só os arquivos que mudaram.
enum Conteudo {
    static let base = URL(string: "https://raw.githubusercontent.com/kaiqueguimacuper-bit/teste-3/claude/personalized-workout-app-ou3pc2/app/src/main/assets/")!
    static let manifesto = "conteudo_manifesto.json"

    struct Manifesto: Decodable { let versao: Int; let arquivos: [String: String] }

    static var pasta: URL {
        FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0].appendingPathComponent("conteudo", isDirectory: true)
    }

    private static func embutidoURL(_ caminho: String) -> URL? {
        let partes = caminho.split(separator: "/").map(String.init)
        let nome = (partes.last! as NSString).deletingPathExtension
        let ext = (partes.last! as NSString).pathExtension
        let sub = partes.count > 1 ? partes.dropLast().joined(separator: "/") : nil
        return Bundle.main.url(forResource: nome, withExtension: ext, subdirectory: sub)
    }

    private static func ler(_ d: Data?) -> Manifesto? { d.flatMap { try? JSONDecoder().decode(Manifesto.self, from: $0) } }
    static var embutido: Manifesto { ler(embutidoURL(manifesto).flatMap { try? Data(contentsOf: $0) }) ?? Manifesto(versao: 0, arquivos: [:]) }
    static var local: Manifesto? { ler(try? Data(contentsOf: pasta.appendingPathComponent(manifesto))) }

    /// Dados do arquivo: a cópia baixada, se for mais nova, senão a embutida no app.
    static func dados(_ caminho: String) -> Data? {
        let f = pasta.appendingPathComponent(caminho)
        let emb = embutido
        if let loc = local, loc.versao > emb.versao, let h = loc.arquivos[caminho], h != emb.arquivos[caminho],
           let d = try? Data(contentsOf: f) { return d }
        if let u = embutidoURL(caminho), let d = try? Data(contentsOf: u) { return d }
        return try? Data(contentsOf: f)
    }

    private static func sha1(_ d: Data) -> String { Insecure.SHA1.hash(data: d).map { String(format: "%02x", $0) }.joined() }

    private static func baixar(_ url: URL) async -> Data? {
        var req = URLRequest(url: url, cachePolicy: .reloadIgnoringLocalCacheData, timeoutInterval: 20)
        req.setValue("no-cache", forHTTPHeaderField: "Cache-Control")
        guard let (d, r) = try? await URLSession.shared.data(for: req), (r as? HTTPURLResponse)?.statusCode == 200 else { return nil }
        return d
    }

    /// Procura conteúdo novo. Retorna quantos arquivos mudaram (0 = nada novo). Falhas de rede são ignoradas.
    static func atualizar() async -> Int {
        guard let bruto = await baixar(base.appendingPathComponent(manifesto)), let remoto = ler(bruto) else { return 0 }
        let emb = embutido, loc = local
        guard remoto.versao > max(emb.versao, loc?.versao ?? 0) else { return 0 }
        try? FileManager.default.createDirectory(at: pasta, withIntermediateDirectories: true)
        var n = 0
        for (caminho, hash) in remoto.arquivos {
            if emb.arquivos[caminho] == hash { continue }
            let f = pasta.appendingPathComponent(caminho)
            if loc?.arquivos[caminho] == hash, FileManager.default.fileExists(atPath: f.path) { continue }
            guard let d = await baixar(base.appendingPathComponent(caminho)), sha1(d) == hash else { return 0 }
            try? FileManager.default.createDirectory(at: f.deletingLastPathComponent(), withIntermediateDirectories: true)
            guard (try? d.write(to: f, options: .atomic)) != nil else { return 0 }
            n += 1
        }
        try? bruto.write(to: pasta.appendingPathComponent(manifesto), options: .atomic)
        return max(n, 1)
    }
}
