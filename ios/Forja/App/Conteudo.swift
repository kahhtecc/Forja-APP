import Foundation
import CryptoKit

/// Conteúdo atualizável sem reinstalar (mesmo esquema do Android, ver Conteudo.kt):
/// o app traz exercises.json, fontes.json e anim3d/ com um manifesto (versão + SHA-1).
/// Ao abrir, baixa o manifesto publicado; se a versão for maior, baixa só os arquivos que mudaram.
enum Conteudo {
    static let base = URL(string: "https://raw.githubusercontent.com/kaiqueguimacuper-bit/teste-3/claude/personalized-workout-app-ou3pc2/app/src/main/assets/")!
    static let manifesto = "conteudo2.json"

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

    /// Caminhos fora do padrão (ex.: "../") são descartados: nunca gravamos fora de Application Support/conteudo.
    private static func ler(_ d: Data?) -> Manifesto? {
        guard let m = d.flatMap({ try? JSONDecoder().decode(Manifesto.self, from: $0) }) else { return nil }
        return Manifesto(versao: m.versao, arquivos: m.arquivos.filter { Seguranca.caminhoValido($0.key) })
    }
    static var embutido: Manifesto { ler(embutidoURL(manifesto).flatMap { try? Data(contentsOf: $0) }) ?? Manifesto(versao: 0, arquivos: [:]) }
    static var local: Manifesto? { ler(try? Data(contentsOf: pasta.appendingPathComponent(manifesto))) }

    /// Dados do arquivo: a cópia baixada, se for mais nova, senão a embutida no app.
    static func dados(_ caminho: String) -> Data? {
        guard Seguranca.caminhoValido(caminho) else { return nil }
        let f = pasta.appendingPathComponent(caminho)
        let emb = embutido
        if let loc = local, loc.versao > emb.versao, let h = loc.arquivos[caminho], h != emb.arquivos[caminho],
           let d = try? Data(contentsOf: f) { return d }
        if let u = embutidoURL(caminho), let d = try? Data(contentsOf: u) { return d }
        return try? Data(contentsOf: f)
    }

    /// Endereço do arquivo para tocadores de mídia: a cópia baixada, se for a mais nova, senão a embutida.
    static func url(_ caminho: String) -> URL? {
        guard Seguranca.caminhoValido(caminho) else { return nil }
        let f = pasta.appendingPathComponent(caminho)
        let emb = embutido
        if let loc = local, loc.versao > emb.versao, let h = loc.arquivos[caminho], h != emb.arquivos[caminho],
           FileManager.default.fileExists(atPath: f.path) { return f }
        if let u = embutidoURL(caminho) { return u }
        return FileManager.default.fileExists(atPath: f.path) ? f : nil
    }

    private static func sha1(_ d: Data) -> String { Insecure.SHA1.hash(data: d).map { String(format: "%02x", $0) }.joined() }

    /// Baixa por HTTPS com teto de tamanho (um arquivo de conteúdo não passa de alguns MB).
    private static func baixar(_ url: URL, maxBytes: Int = 25 << 20) async -> Data? {
        guard url.scheme == "https" else { return nil }
        var req = URLRequest(url: url, cachePolicy: .reloadIgnoringLocalCacheData, timeoutInterval: 20)
        req.setValue("no-cache", forHTTPHeaderField: "Cache-Control")
        guard let (d, r) = try? await URLSession.shared.data(for: req), (r as? HTTPURLResponse)?.statusCode == 200,
              r.url?.scheme == "https", d.count <= maxBytes else { return nil }
        return d
    }

    /// Procura conteúdo novo. Retorna quantos arquivos mudaram (0 = nada novo). Falhas de rede são ignoradas.
    static func atualizar() async -> Int {
        guard let bruto = await baixar(base.appendingPathComponent(manifesto), maxBytes: 1 << 20), let remoto = ler(bruto) else { return 0 }
        let emb = embutido, loc = local
        guard remoto.versao > max(emb.versao, loc?.versao ?? 0) else { return 0 }
        try? FileManager.default.createDirectory(at: pasta, withIntermediateDirectories: true)
        // conteúdo que dá para baixar de novo não vai para o backup do iCloud (regra da App Store)
        var p = pasta
        var rv = URLResourceValues(); rv.isExcludedFromBackup = true
        try? p.setResourceValues(rv)
        var n = 0
        for (caminho, hash) in remoto.arquivos {
            if emb.arquivos[caminho] == hash { continue }
            let f = pasta.appendingPathComponent(caminho)
            guard Seguranca.dentroDe(pasta, f) else { continue }
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
