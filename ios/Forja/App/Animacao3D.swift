import SwiftUI
import AVFoundation

/// Vídeos 3D (humano com os músculos trabalhados em destaque): video3d/<id>.mp4 + pôster video3d/<id>.webp + meta.json.
final class Animacoes3D {
    static let shared = Animacoes3D()
    private var ids: Set<String>?
    private let posters = NSCache<NSString, UIImage>()
    private let trava = NSLock()

    init() { posters.countLimit = 80 }

    func limpar() { trava.lock(); ids = nil; trava.unlock(); posters.removeAllObjects() }

    func tem(_ id: String) -> Bool {
        trava.lock(); defer { trava.unlock() }
        if ids == nil {
            if let d = Conteudo.dados("video3d/meta.json"), let o = try? JSONSerialization.jsonObject(with: d) as? [String: Any] {
                ids = Set(o.keys)
            } else { ids = [] }
        }
        return ids!.contains(id)
    }

    func poster(_ id: String) -> UIImage? {
        if let i = posters.object(forKey: id as NSString) { return i }
        guard let d = Conteudo.dados("video3d/\(id).webp"), let i = UIImage(data: d) else { return nil }
        posters.setObject(i, forKey: id as NSString)
        return i
    }
}

/// Vídeo 3D em loop (ou só o pôster, se animar = false). O quadro ocupa a altura toda (corpo inteiro visível),
/// com as laterais esfumadas no fundo.
struct Animacao3DView: View {
    static let fundo = Color(red: 27 / 255, green: 23 / 255, blue: 19 / 255)
    let id: String
    var animar = true
    @State private var poster: UIImage?

    var body: some View {
        GeometryReader { g in
            let lado = g.size.height * 1.12
            ZStack {
                Animacao3DView.fundo
                ZStack {
                    if let p = poster { Image(uiImage: p).resizable() }
                    if animar, let u = Conteudo.url("video3d/\(id).mp4") { VideoLoop(url: u) }
                }
                .frame(width: lado, height: lado)
                .mask(LinearGradient(stops: [.init(color: .clear, location: 0), .init(color: .black, location: 0.1),
                                             .init(color: .black, location: 0.9), .init(color: .clear, location: 1)], startPoint: .leading, endPoint: .trailing))
                .position(x: g.size.width / 2, y: g.size.height / 2)
            }
        }
        .clipped()
        .task(id: id) {
            let alvo = id
            poster = await Task.detached(priority: .userInitiated) { Animacoes3D.shared.poster(alvo) }.value
        }
    }
}

/// AVQueuePlayer + AVPlayerLooper: loop sem emenda, sem som e sem interromper a música do usuário.
struct VideoLoop: UIViewRepresentable {
    let url: URL

    final class Vista: UIView {
        override class var layerClass: AnyClass { AVPlayerLayer.self }
        var camada: AVPlayerLayer { layer as! AVPlayerLayer }
        var looper: AVPlayerLooper?
        var observador: NSKeyValueObservation?
    }

    func makeUIView(context: Context) -> Vista {
        let v = Vista()
        v.backgroundColor = .clear
        v.camada.videoGravity = .resizeAspect
        v.alpha = 0
        let player = AVQueuePlayer()
        player.isMuted = true
        player.preventsDisplaySleepDuringVideoPlayback = false
        v.looper = AVPlayerLooper(player: player, templateItem: AVPlayerItem(url: url))
        v.camada.player = player
        v.observador = v.camada.observe(\.isReadyForDisplay, options: [.new]) { camada, _ in
            if camada.isReadyForDisplay { DispatchQueue.main.async { UIView.animate(withDuration: 0.15) { v.alpha = 1 } } }
        }
        player.play()
        return v
    }

    func updateUIView(_ v: Vista, context: Context) {}

    static func dismantleUIView(_ v: Vista, coordinator: ()) {
        v.camada.player?.pause()
        v.looper?.disableLooping()
        v.observador?.invalidate()
        v.camada.player = nil
    }
}
