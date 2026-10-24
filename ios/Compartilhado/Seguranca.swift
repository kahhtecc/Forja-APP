import Foundation

/// Regras de segurança compartilhadas (mesmas do Android, ver Seguranca.kt): o que o app aceita de fora.
enum Seguranca {
    private static let extensoes: Set<String> = ["json", "mp4", "webp", "png", "jpg"]

    /// Caminhos de conteúdo: só letras, números, _ - . e subpastas; sem "..", sem caminho absoluto.
    static func caminhoValido(_ c: String) -> Bool {
        guard c.count <= 160, !c.contains(".."),
              c.range(of: "^([A-Za-z0-9_-]+/)*[A-Za-z0-9_-][A-Za-z0-9_.-]*$", options: .regularExpression) != nil else { return false }
        return extensoes.contains((c as NSString).pathExtension.lowercased())
    }

    /// Garante que `f` fica dentro de `pasta` depois de resolver links e "..".
    static func dentroDe(_ pasta: URL, _ f: URL) -> Bool {
        f.standardizedFileURL.resolvingSymlinksInPath().path.hasPrefix(pasta.standardizedFileURL.resolvingSymlinksInPath().path + "/")
    }

    static func idYoutubeValido(_ id: String) -> Bool {
        id.range(of: "^[A-Za-z0-9_-]{11}$", options: .regularExpression) != nil
    }

    /// Só links https com host (nada de file:, javascript: ou esquemas de outros apps vindos do conteúdo).
    static func linkSeguro(_ s: String?) -> URL? {
        guard let s, let u = URL(string: s.trimmingCharacters(in: .whitespaces)),
              u.scheme?.lowercased() == "https", let h = u.host, !h.isEmpty else { return nil }
        return u
    }
}
