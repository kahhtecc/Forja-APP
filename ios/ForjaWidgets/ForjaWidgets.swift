import SwiftUI
import WidgetKit
import ActivityKit
import AppIntents

// Live Activity do treino ao vivo: tela bloqueada, Dynamic Island e (watchOS 11+) Smart Stack do Apple Watch.

@main
struct ForjaWidgets: WidgetBundle {
    var body: some Widget {
        TreinoAoVivo()
    }
}

/// Tela bloqueada e Dynamic Island; no watchOS 11+ o Apple Watch mostra o layout compacto no Smart Stack.
struct TreinoAoVivo: Widget {
    var body: some WidgetConfiguration { LiveActivityTreino.configuracao() }
}

enum LiveActivityTreino {
    static func configuracao() -> ActivityConfiguration<TreinoAtividade> {
        ActivityConfiguration(for: TreinoAtividade.self) { ctx in
            ConteudoTreino(ctx: ctx)
                .activityBackgroundTint(Paleta.fundo)
                .activitySystemActionForegroundColor(Paleta.texto)
        } dynamicIsland: { ctx in
            let cor = Paleta.cor(ctx.attributes.cor)
            let s = ctx.state
            return DynamicIsland {
                DynamicIslandExpandedRegion(.leading) {
                    VStack(alignment: .leading, spacing: 2) {
                        Text(s.descansando ? "DESCANSO" : s.rotulo.uppercased()).font(.system(size: 11, weight: .heavy, design: .rounded)).foregroundStyle(cor)
                        Text(s.descansando ? (s.proximo.map { "A seguir: \($0)" } ?? "Última série") : s.exercicio)
                            .font(.system(size: 15, weight: .bold, design: .rounded)).lineLimit(2)
                    }
                }
                DynamicIslandExpandedRegion(.trailing) {
                    VStack(alignment: .trailing, spacing: 2) {
                        Cronometro(s: s, tamanho: 30)
                        FC(bpm: s.bpm, tamanho: 13)
                    }
                }
                DynamicIslandExpandedRegion(.bottom) {
                    Botoes(s: s, hex: ctx.attributes.cor)
                }
            } compactLeading: {
                Image(systemName: Paleta.simbolo(ctx.attributes.tipo)).foregroundStyle(cor)
            } compactTrailing: {
                if s.descansando || s.fimEm != nil { Cronometro(s: s, tamanho: 14).frame(maxWidth: 46) }
                else { Text("\(s.indice + 1)/\(s.total)").font(.system(size: 14, weight: .heavy, design: .rounded)).foregroundStyle(cor) }
            } minimal: {
                if s.descansando, s.fimEm != nil { Cronometro(s: s, tamanho: 12).foregroundStyle(cor) }
                else { Image(systemName: Paleta.simbolo(ctx.attributes.tipo)).foregroundStyle(cor) }
            }
            .keylineTint(cor)
        }
    }
}

/// Escolhe o layout: relógio (.small) ou tela bloqueada.
struct ConteudoTreino: View {
    let ctx: ActivityViewContext<TreinoAtividade>
    var body: some View {
        if #available(iOSApplicationExtension 18.0, *) { ConteudoPorFamilia(ctx: ctx) } else { TelaBloqueada(ctx: ctx) }
    }
}

@available(iOSApplicationExtension 18.0, *)
struct ConteudoPorFamilia: View {
    let ctx: ActivityViewContext<TreinoAtividade>
    @Environment(\.activityFamily) private var familia
    var body: some View {
        switch familia {
        case .small: NoRelogio(ctx: ctx)
        default: TelaBloqueada(ctx: ctx)
        }
    }
}

struct TelaBloqueada: View {
    let ctx: ActivityViewContext<TreinoAtividade>
    var body: some View {
        let s = ctx.state
        let cor = Paleta.cor(ctx.attributes.cor)
        VStack(alignment: .leading, spacing: 8) {
            HStack(spacing: 6) {
                Image(systemName: Paleta.simbolo(ctx.attributes.tipo)).font(.system(size: 12, weight: .bold)).foregroundStyle(cor)
                Text(ctx.attributes.titulo.uppercased()).font(.system(size: 11, weight: .heavy, design: .rounded)).foregroundStyle(Paleta.texto2).lineLimit(1)
                Spacer()
                FC(bpm: s.bpm, tamanho: 14)
                Text(timerInterval: ctx.attributes.inicio...Date.distantFuture, countsDown: false)
                    .font(.system(size: 13, weight: .bold, design: .rounded)).monospacedDigit().foregroundStyle(Paleta.texto2)
                    .frame(maxWidth: 56, alignment: .trailing)
            }
            if s.concluido {
                Text("Treino concluído").font(.system(size: 20, weight: .heavy, design: .rounded)).foregroundStyle(Paleta.texto)
            } else {
                HStack(alignment: .center) {
                    VStack(alignment: .leading, spacing: 2) {
                        Text(s.descansando ? "DESCANSO" : s.rotulo.uppercased()).font(.system(size: 11, weight: .heavy, design: .rounded)).foregroundStyle(cor)
                        Text(s.descansando ? (s.proximo ?? "Última série") : s.exercicio).font(.system(size: 19, weight: .heavy, design: .rounded)).foregroundStyle(Paleta.texto).lineLimit(2)
                        Text(s.descansando ? "a seguir" : s.prescricao).font(.system(size: 13, weight: .semibold, design: .rounded)).foregroundStyle(Paleta.texto2)
                    }
                    Spacer()
                    if s.descansando || s.fimEm != nil {
                        Cronometro(s: s, tamanho: 40).foregroundStyle(Paleta.texto)
                    } else {
                        Text("\(s.indice + 1)/\(s.total)").font(.system(size: 30, weight: .heavy, design: .rounded)).foregroundStyle(cor)
                    }
                }
                Botoes(s: s, hex: ctx.attributes.cor)
            }
        }
        .padding(16)
    }
}

/// Layout do Apple Watch (Smart Stack, watchOS 11+).
struct NoRelogio: View {
    let ctx: ActivityViewContext<TreinoAtividade>
    var body: some View {
        let s = ctx.state
        let cor = Paleta.cor(ctx.attributes.cor)
        VStack(alignment: .leading, spacing: 2) {
            HStack {
                Text(s.descansando ? "DESCANSO" : s.rotulo.uppercased()).font(.system(size: 11, weight: .heavy, design: .rounded)).foregroundStyle(cor).lineLimit(1)
                Spacer()
                FC(bpm: s.bpm, tamanho: 12)
            }
            if s.descansando || s.fimEm != nil {
                Cronometro(s: s, tamanho: 30).foregroundStyle(Paleta.texto)
            } else {
                Text(s.exercicio).font(.system(size: 15, weight: .heavy, design: .rounded)).foregroundStyle(Paleta.texto).lineLimit(2)
            }
            Botoes(s: s, hex: ctx.attributes.cor, compacto: true)
        }
        .padding(8)
    }
}

struct Cronometro: View {
    let s: TreinoAtividade.ContentState
    var tamanho: CGFloat
    var body: some View {
        if let f = s.fimEm, f > Date() {
            Text(timerInterval: Date()...f, countsDown: true)
                .font(.system(size: tamanho, weight: .heavy, design: .rounded)).monospacedDigit().multilineTextAlignment(.trailing)
        } else {
            Text("0:00").font(.system(size: tamanho, weight: .heavy, design: .rounded)).monospacedDigit()
        }
    }
}

struct FC: View {
    let bpm: Int?
    var tamanho: CGFloat
    var body: some View {
        if let b = bpm {
            HStack(spacing: 2) {
                Image(systemName: "heart.fill").font(.system(size: tamanho * 0.8)).foregroundStyle(Paleta.fc)
                Text("\(b)").font(.system(size: tamanho, weight: .heavy, design: .rounded)).monospacedDigit().foregroundStyle(Paleta.texto)
            }
        }
    }
}

/// Botões interativos (iOS 17+); no iOS 16 a Live Activity só mostra.
struct Botoes: View {
    let s: TreinoAtividade.ContentState
    let hex: UInt32
    var compacto = false
    var cor: Color { Paleta.cor(hex) }
    var body: some View {
        if #available(iOSApplicationExtension 17.0, *) {
            if s.concluido {
                EmptyView()
            } else if s.descansando {
                Button(intent: PularDescansoIntent()) { rotulo("Pular descanso", "forward.end.fill") }
                    .buttonStyle(.plain)
            } else if !s.porTempo {
                Button(intent: ConcluirSerieIntent()) { rotulo(compacto ? "Concluir" : "Concluir série", "checkmark") }
                    .buttonStyle(.plain)
            }
        }
    }
    func rotulo(_ t: String, _ icone: String) -> some View {
        Label(t, systemImage: icone)
            .font(.system(size: compacto ? 13 : 15, weight: .heavy, design: .rounded))
            .foregroundStyle(Paleta.sobre(hex))
            .frame(maxWidth: .infinity, minHeight: compacto ? 28 : 38)
            .background(cor, in: RoundedRectangle(cornerRadius: compacto ? 10 : 14, style: .continuous))
    }
}

enum Paleta {
    static let fundo = Color(red: 0x0E / 255, green: 0x0D / 255, blue: 0x0C / 255)
    static let texto = Color(red: 0xF2 / 255, green: 0xEB / 255, blue: 0xE0 / 255)
    static let texto2 = Color(red: 0xA8 / 255, green: 0x9E / 255, blue: 0x90 / 255)
    static let fc = Color(red: 0xF4 / 255, green: 0x3F / 255, blue: 0x5E / 255)
    static func cor(_ hex: UInt32) -> Color {
        Color(red: Double((hex >> 16) & 0xFF) / 255, green: Double((hex >> 8) & 0xFF) / 255, blue: Double(hex & 0xFF) / 255)
    }
    /// Texto escuro sobre cores claras (amarelo, verde), branco sobre a brasa.
    static func sobre(_ hex: UInt32) -> Color {
        let r = Double((hex >> 16) & 0xFF), g = Double((hex >> 8) & 0xFF), b = Double(hex & 0xFF)
        return (0.299 * r + 0.587 * g + 0.114 * b) / 255 > 0.62 ? fundo : .white
    }
    static func simbolo(_ t: String) -> String {
        switch t {
        case "corrida": return "figure.run"
        case "bike": return "figure.outdoor.cycle"
        case "luta": return "figure.boxing"
        case "hiit": return "bolt.fill"
        case "mobilidade": return "figure.mind.and.body"
        case "cardio": return "heart.fill"
        case "atleta": return "trophy.fill"
        default: return "dumbbell.fill"
        }
    }
}
