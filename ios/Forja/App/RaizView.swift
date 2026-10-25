import SwiftUI
import ForjaCore

enum Rota: Hashable {
    case sessao(semana: Int, idx: Int)
    case rotina(String)
    case exercicio(String, trocaSessao: Int?)
    case video(String)
    case perfil
    case fontes
    case cardiaco
}

enum Aba: String, CaseIterable {
    case hoje = "Hoje", plano = "Plano", mobilidade = "Mobilidade", exercicios = "Exercícios", progresso = "Progresso"
    var icone: String {
        switch self {
        case .hoje: return "flame.fill"
        case .plano: return "calendar"
        case .mobilidade: return "figure.mind.and.body"
        case .exercicios: return "dumbbell.fill"
        case .progresso: return "chart.bar.xaxis"
        }
    }
}

struct RaizView: View {
    @EnvironmentObject var app: AppEstado
    @State private var aba: Aba = .hoje
    @State private var caminho = NavigationPath()
    @State private var questionario = false
    @State private var concluido: Registro?
    @State private var iniciou = false

    var body: some View {
        NavigationStack(path: $caminho) {
            ZStack(alignment: .bottom) {
                Cor.fundo.ignoresSafeArea()
                Group {
                    switch aba {
                    case .hoje: HojeView(irAba: { aba = $0 }, abrir: abrir, refazer: { questionario = true })
                    case .plano: PlanoView(abrir: abrir)
                    case .mobilidade: MobilidadeView(abrir: abrir)
                    case .exercicios: BibliotecaView(abrir: abrir)
                    case .progresso: ProgressoView()
                    }
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                BarraAbas(aba: $aba)
            }
            .toolbar(.hidden, for: .navigationBar)
            .navigationDestination(for: Rota.self) { r in
                Group {
                    switch r {
                    case .sessao(let w, let i): SessaoView(semana: w, idx: i, abrir: abrir)
                    case .rotina(let id): RotinaView(id: id, abrir: abrir)
                    case .exercicio(let id, let t): ExercicioView(id: id, trocaSessao: t, abrir: abrir, voltar: { if !caminho.isEmpty { caminho.removeLast() } })
                    case .video(let id): VideoView(id: id)
                    case .perfil: PerfilView(refazer: { questionario = true }, abrir: abrir)
                    case .fontes: FontesView()
                    case .cardiaco: CardiacoView()
                    }
                }
                .toolbarBackground(Cor.fundo, for: .navigationBar)
                .toolbarColorScheme(.dark, for: .navigationBar)
            }
        }
        .fullScreenCover(isPresented: Binding(get: { !app.e.temPlano || questionario }, set: { if !$0 { questionario = false } })) {
            QuestionarioView(podeFechar: app.e.temPlano, fechar: { questionario = false; aba = .hoje; caminho = NavigationPath() })
                .environmentObject(app)
        }
        .fullScreenCover(item: $app.treinoAtivo) { alvo in
            TreinoView(alvo: alvo) { reg in
                app.treinoAtivo = nil
                if let r = reg { DispatchQueue.main.asyncAfter(deadline: .now() + 0.4) { concluido = r } }
            }
            .environmentObject(app)
        }
        .sheet(item: $concluido) { r in
            ConcluidoView(registro: r) { concluido = nil }
                .environmentObject(app)
                .presentationDetents([.large])
        }
        .overlay(alignment: .top) {
            if let t = app.aviso {
                HStack(spacing: 12) {
                    Image(systemName: "sparkles").foregroundStyle(Cor.brasa)
                    Text(t).font(Tipo.pequenoForte).foregroundStyle(Cor.texto)
                }
                .padding(16).frame(maxWidth: .infinity, alignment: .leading)
                .background(Cor.sup3, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
                .overlay(RoundedRectangle(cornerRadius: 18, style: .continuous).stroke(Cor.brasa.opacity(0.5), lineWidth: 1))
                .padding(.horizontal, 20).padding(.top, 8)
                .transition(.move(edge: .top).combined(with: .opacity))
                .task { try? await Task.sleep(nanoseconds: 4_500_000_000); withAnimation { app.aviso = nil } }
            }
        }
        .animation(.spring(response: 0.4), value: app.aviso)
        .onAppear(perform: telaDeCaptura)
    }

    func abrir(_ r: Rota) { caminho.append(r) }

    /// Abre uma tela direto pelos argumentos (-tela X), usado nas capturas automáticas.
    func telaDeCaptura() {
        guard !iniciou, let t = app.telaInicial, app.e.temPlano else { return }
        iniciou = true
        switch t {
        case "plano": aba = .plano
        case "mobilidade": aba = .mobilidade
        case "exercicios": aba = .exercicios
        case "progresso": aba = .progresso
        case "perfil": abrir(.perfil)
        case "fontes": abrir(.fontes)
        case "cardiaco": abrir(.cardiaco)
        case "concluido":
            if let r = app.e.registros.last { concluido = r }
        case "quiz": questionario = true
        case "sessao", "treino":
            let (i, s) = app.loja.proximaSessao() ?? (0, app.plano!.semanas[app.semanaAtual - 1].sessoes[0])
            if t == "sessao" { abrir(.sessao(semana: app.semanaAtual, idx: i)) } else { app.treinoAtivo = TreinoAlvo(sessao: s, semana: app.semanaAtual, idx: i) }
        default:
            if t.hasPrefix("exercicio:") { abrir(.exercicio(String(t.dropFirst(10)), trocaSessao: nil)) }
            else if t.hasPrefix("rotina:") { abrir(.rotina(String(t.dropFirst(7)))) }
            else if t.hasPrefix("video:") { abrir(.video(String(t.dropFirst(6)))) }
            else if t.hasPrefix("treinorotina:"), let r = Rotinas.porId(String(t.dropFirst(13))) { app.treinoAtivo = TreinoAlvo(sessao: r.sessao, semana: 0, idx: -1) }
        }
    }
}

struct BarraAbas: View {
    @Binding var aba: Aba
    var body: some View {
        HStack(spacing: 4) {
            ForEach(Aba.allCases, id: \.self) { a in
                let sel = a == aba
                Button { Haptico.toque(); withAnimation(.easeOut(duration: 0.2)) { aba = a } } label: {
                    VStack(spacing: 3) {
                        Image(systemName: a.icone).font(.system(size: 18, weight: .semibold))
                        Text(a.rawValue).font(Tipo.texto(10, "ExtraBold")).lineLimit(1).minimumScaleFactor(0.8)
                    }
                    .foregroundStyle(sel ? Cor.texto : Cor.texto3)
                    .frame(maxWidth: .infinity).padding(.vertical, 8)
                    .background(sel ? Cor.brasa.opacity(0.14) : .clear, in: RoundedRectangle(cornerRadius: 22, style: .continuous))
                    .overlay(alignment: .top) { if sel { Capsule().fill(Cor.brasa).frame(width: 18, height: 3).offset(y: -2) } }
                }
                .buttonStyle(.plain)
                .accessibilityLabel(a.rawValue)
                .accessibilityAddTraits(sel ? .isSelected : [])
            }
        }
        .padding(6)
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 28, style: .continuous))
        .background(Cor.sup2.opacity(0.85), in: RoundedRectangle(cornerRadius: 28, style: .continuous))
        .overlay(RoundedRectangle(cornerRadius: 28, style: .continuous).stroke(Cor.borda, lineWidth: 1))
        .shadow(color: .black.opacity(0.45), radius: 24, y: 10)
        .padding(.horizontal, 14).padding(.bottom, 4)
    }
}

let ESPACO_BARRA: CGFloat = 110
