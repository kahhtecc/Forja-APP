import SwiftUI
import ForjaCore

// MARK: - Imagens

final class CacheImagens {
    static let shared = CacheImagens()
    private let cache = NSCache<NSString, UIImage>()
    func imagem(_ nome: String) -> UIImage? {
        if let i = cache.object(forKey: nome as NSString) { return i }
        guard let url = Bundle.main.url(forResource: nome, withExtension: "webp", subdirectory: "img"),
              let d = try? Data(contentsOf: url), let i = UIImage(data: d) else { return nil }
        cache.setObject(i, forKey: nome as NSString)
        return i
    }
}

/// Demonstração animada: alterna as fotos de início e fim do movimento em loop.
struct DemoExercicio: View {
    let ex: Exercicio
    var cor: Color = Cor.brasa
    var animar = true
    var cantos: CGFloat = 20

    var body: some View {
        ZStack {
            Cor.sup2
            if Animacoes3D.shared.tem(ex.id) {
                Animacao3DView(id: ex.id, animar: animar)
            } else if ex.temImagem, let a = CacheImagens.shared.imagem("\(ex.id)_0"), let b = CacheImagens.shared.imagem("\(ex.id)_1") {
                if animar {
                    TimelineView(.animation(minimumInterval: 1 / 30, paused: false)) { ctx in
                        let t = ctx.date.timeIntervalSinceReferenceDate.truncatingRemainder(dividingBy: 2.6) / 2.6
                        let mix: Double = t < 0.4 ? 0 : t < 0.5 ? (t - 0.4) / 0.1 : t < 0.9 ? 1 : 1 - (t - 0.9) / 0.1
                        let zoom = 1.04 + 0.03 * sin(t * 2 * .pi)
                        ZStack {
                            Image(uiImage: a).resizable().scaledToFill()
                            Image(uiImage: b).resizable().scaledToFill().opacity(mix)
                        }.scaleEffect(zoom)
                    }
                } else {
                    Image(uiImage: b).resizable().scaledToFill().scaleEffect(1.04)
                }
                LinearGradient(stops: [.init(color: .clear, location: 0.55), .init(color: .black.opacity(0.55), location: 1)], startPoint: .top, endPoint: .bottom)
                cor.opacity(0.10)
            } else {
                RadialGradient(colors: [cor.opacity(0.35), Cor.sup2], center: .center, startRadius: 0, endRadius: 160)
                Image(systemName: simbolo).font(.system(size: 44, weight: .bold)).foregroundStyle(cor)
            }
        }
        .clipShape(RoundedRectangle(cornerRadius: cantos, style: .continuous))
        .accessibilityLabel("Demonstração de \(ex.nome)")
    }

    var simbolo: String {
        if ex.padroes.contains(where: { $0.hasPrefix("luta") }) { return "figure.boxing" }
        if ex.padroes.contains("corrida") { return "figure.run" }
        if ex.padroes.contains("bike") { return "figure.outdoor.cycle" }
        if ex.tipo == "mobilidade" { return "figure.mind.and.body" }
        if ex.tipo == "cardio" { return "flame.fill" }
        return "dumbbell.fill"
    }
}

struct FotoAsset: View {
    let nome: String
    var body: some View {
        if let i = CacheImagens.shared.imagem(nome) { Image(uiImage: i).resizable().scaledToFill() } else { Cor.sup2 }
    }
}

// MARK: - Blocos visuais

struct Cartao<C: View>: View {
    var cor: Color = Cor.sup1
    var borda: Color = Cor.borda
    var cantos: CGFloat = 22
    var padding: CGFloat = 18
    @ViewBuilder var conteudo: () -> C
    var body: some View {
        VStack(alignment: .leading, spacing: 0) { conteudo() }
            .padding(padding)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(cor, in: RoundedRectangle(cornerRadius: cantos, style: .continuous))
            .overlay(RoundedRectangle(cornerRadius: cantos, style: .continuous).stroke(borda, lineWidth: 1))
    }
}

struct Rotulo: View {
    let texto: String
    var cor: Color = Cor.texto3
    init(_ texto: String, _ cor: Color = Cor.texto3) { self.texto = texto; self.cor = cor }
    var body: some View { Text(texto.uppercased()).font(Tipo.rotulo).tracking(1.4).foregroundStyle(cor).lineLimit(1) }
}

struct Etiqueta: View {
    let texto: String
    var cor: Color = Cor.brasa
    var icone: String? = nil
    var cheia = false
    var sobreFoto = false
    var body: some View {
        HStack(spacing: 5) {
            if let i = icone { Image(systemName: i).font(.system(size: 11, weight: .bold)) }
            Text(texto).font(Tipo.pequenoForte).lineLimit(1)
        }
        .foregroundStyle(cheia ? Cor.sobre(cor) : cor)
        .padding(.horizontal, 10).padding(.vertical, 5)
        .background(cheia ? cor : (sobreFoto ? Cor.fundo.opacity(0.78) : cor.opacity(0.14)), in: Capsule())
    }
}

struct BotaoPrimario: View {
    let texto: String
    var icone: String? = nil
    var cor: Color? = nil
    var ativo = true
    let acao: () -> Void
    var body: some View {
        Button { Haptico.toque(); acao() } label: {
            HStack(spacing: 10) {
                if let i = icone { Image(systemName: i).font(.system(size: 17, weight: .bold)) }
                Text(texto).font(Tipo.botao)
            }
            .foregroundStyle(!ativo ? Cor.texto3 : (cor.map { Cor.sobre($0) } ?? .white))
            .frame(maxWidth: .infinity, minHeight: 58)
            .background {
                RoundedRectangle(cornerRadius: 18, style: .continuous).fill(!ativo ? AnyShapeStyle(Cor.sup3) : (cor.map { AnyShapeStyle($0) } ?? AnyShapeStyle(Cor.gradBrasa)))
            }
        }
        .disabled(!ativo)
        .buttonStyle(Pressionavel())
    }
}

struct BotaoSecundario: View {
    let texto: String
    var icone: String? = nil
    var cor: Color = Cor.texto
    let acao: () -> Void
    var body: some View {
        Button { Haptico.toque(); acao() } label: {
            HStack(spacing: 8) {
                if let i = icone { Image(systemName: i).font(.system(size: 15, weight: .bold)) }
                Text(texto).font(Tipo.botao).lineLimit(1)
            }
            .foregroundStyle(cor)
            .padding(.horizontal, 16)
            .frame(maxWidth: .infinity, minHeight: 50)
            .background(Cor.sup2, in: RoundedRectangle(cornerRadius: 16, style: .continuous))
            .overlay(RoundedRectangle(cornerRadius: 16, style: .continuous).stroke(Cor.borda, lineWidth: 1))
        }
        .buttonStyle(Pressionavel())
    }
}

struct BotaoIcone: View {
    let icone: String
    let descricao: String
    var cor: Color = Cor.texto
    var fundo: Color = Cor.sup2
    var tamanho: CGFloat = 46
    let acao: () -> Void
    var body: some View {
        Button { Haptico.toque(); acao() } label: {
            Image(systemName: icone).font(.system(size: tamanho * 0.38, weight: .bold)).foregroundStyle(cor)
                .frame(width: tamanho, height: tamanho)
                .background(fundo, in: Circle())
                .overlay(Circle().stroke(Cor.borda, lineWidth: 1))
        }
        .buttonStyle(Pressionavel())
        .accessibilityLabel(descricao)
    }
}

struct Pressionavel: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label.scaleEffect(configuration.isPressed ? 0.97 : 1).animation(.spring(response: 0.25, dampingFraction: 0.7), value: configuration.isPressed)
    }
}

struct Secao: View {
    let titulo: String
    var acao: String? = nil
    var onAcao: (() -> Void)? = nil
    var body: some View {
        HStack(alignment: .firstTextBaseline) {
            Text(titulo).font(Tipo.titulo3).foregroundStyle(Cor.texto)
            Spacer()
            if let a = acao, let f = onAcao { Button(a) { Haptico.toque(); f() }.font(Tipo.pequenoForte).foregroundStyle(Cor.brasa) }
        }
        .padding(.top, 26).padding(.bottom, 12)
    }
}

struct Anel<C: View>: View {
    let progresso: Double
    var cor: Color = Cor.brasa
    var espessura: CGFloat = 10
    @ViewBuilder var centro: () -> C
    var body: some View {
        ZStack {
            Circle().stroke(Cor.sup3, lineWidth: espessura)
            Circle().trim(from: 0, to: max(0, min(1, progresso)))
                .stroke(AngularGradient(colors: [cor.opacity(0.6), cor], center: .center), style: StrokeStyle(lineWidth: espessura, lineCap: .round))
                .rotationEffect(.degrees(-90))
                .animation(.linear(duration: 0.25), value: progresso)
            centro()
        }
        .padding(espessura / 2)
    }
}

struct BarraProgresso: View {
    let progresso: Double
    var cor: Color = Cor.brasa
    var altura: CGFloat = 6
    var body: some View {
        GeometryReader { g in
            ZStack(alignment: .leading) {
                Capsule().fill(Cor.sup3)
                Capsule().fill(cor).frame(width: g.size.width * max(0, min(1, progresso)))
            }
        }.frame(height: altura)
    }
}

struct Estatistica: View {
    let valor: String
    let rotulo: String
    var cor: Color = Cor.texto
    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(valor).font(Tipo.numero).foregroundStyle(cor).lineLimit(1).minimumScaleFactor(0.6)
            Text(rotulo).font(Tipo.pequeno).foregroundStyle(Cor.texto2).lineLimit(2)
        }
    }
}

struct IconeRedondo: View {
    let icone: String
    let cor: Color
    var tamanho: CGFloat = 44
    var body: some View {
        Image(systemName: icone).font(.system(size: tamanho * 0.42, weight: .bold)).foregroundStyle(cor)
            .frame(width: tamanho, height: tamanho)
            .background(cor.opacity(0.16), in: RoundedRectangle(cornerRadius: 14, style: .continuous))
    }
}

struct LinhaBrasa: View {
    var cor: Color = Cor.brasa
    var largura: CGFloat = 36
    var body: some View { Capsule().fill(LinearGradient(colors: [cor, cor.opacity(0)], startPoint: .leading, endPoint: .trailing)).frame(width: largura, height: 3) }
}

struct Chip: View {
    let texto: String
    let sel: Bool
    var cor: Color = Cor.brasa
    let acao: () -> Void
    var body: some View {
        Button { Haptico.toque(); acao() } label: {
            Text(texto).font(Tipo.pequenoForte).lineLimit(1)
                .foregroundStyle(sel ? Cor.sobre(cor) : Cor.texto2)
                .padding(.horizontal, 16).padding(.vertical, 9)
                .background(sel ? cor : Cor.sup1, in: Capsule())
                .overlay(Capsule().stroke(sel ? cor : Cor.borda, lineWidth: 1))
        }.buttonStyle(.plain)
    }
}

struct Aviso: View {
    let texto: String
    var body: some View {
        HStack(alignment: .top, spacing: 10) {
            Image(systemName: "exclamationmark.triangle.fill").foregroundStyle(Cor.alerta)
            Text(texto).font(Tipo.pequeno).foregroundStyle(Cor.texto)
        }
        .padding(14).frame(maxWidth: .infinity, alignment: .leading)
        .background(Cor.alerta.opacity(0.10), in: RoundedRectangle(cornerRadius: 16, style: .continuous))
    }
}

extension View {
    /// Fundo padrão das telas.
    func telaForja() -> some View { self.background(Cor.fundo.ignoresSafeArea()).foregroundStyle(Cor.texto) }
}

func capaSessao(_ s: Sessao) -> String? {
    (s.blocos.first { $0.tipo != .AQUECIMENTO } ?? s.blocos.first)?.itens.first?.exId
}

func nExercicios(_ s: Sessao) -> Int { s.blocos.filter { $0.tipo != .AQUECIMENTO && $0.tipo != .DESAQUECIMENTO }.reduce(0) { $0 + $1.itens.count } }

let DIAS = Questionario.DIAS_NOMES
