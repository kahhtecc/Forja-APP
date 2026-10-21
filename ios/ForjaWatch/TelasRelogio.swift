import SwiftUI
import WatchKit

// MARK: - Hoje

struct HojeRelogioView: View {
    @EnvironmentObject var m: ModeloRelogio

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 8) {
                    if let s = m.sessao {
                        let cor = CorW.tipo(s.tipo)
                        HStack(spacing: 6) {
                            Image(systemName: CorW.simbolo(s.tipo)).font(.system(size: 13, weight: .bold)).foregroundStyle(cor)
                            RotuloW(s.concluida ? "Concluído hoje" : (s.ehHoje ? "Treino de hoje" : "Próximo treino"), s.concluida ? CorW.ok : cor)
                        }
                        Text(s.titulo).font(TipoW.titulo(24)).foregroundStyle(CorW.texto).lineLimit(3).minimumScaleFactor(0.7)
                        Text(resumo(s)).font(.system(size: 13, weight: .medium, design: .rounded)).foregroundStyle(CorW.texto2)
                        Button {
                            m.iniciar()
                        } label: {
                            Label(s.concluida ? "Treinar de novo" : "Iniciar", systemImage: "play.fill")
                                .font(.system(size: 16, weight: .heavy, design: .rounded))
                                .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.borderedProminent).tint(cor)
                        .foregroundStyle(CorW.fundo)
                        .padding(.top, 4)
                        .disabled(s.passos.isEmpty)
                        HStack(spacing: 5) {
                            Image(systemName: m.iphoneAlcancavel ? "iphone" : "iphone.slash").font(.system(size: 11))
                            Text(m.iphoneAlcancavel ? "iPhone conectado" : "Treina sem o iPhone; salva depois").font(.system(size: 11, design: .rounded))
                        }
                        .foregroundStyle(CorW.texto2).padding(.top, 2)
                    } else {
                        Image(systemName: "applewatch.radiowaves.left.and.right").font(.system(size: 30)).foregroundStyle(CorW.brasa)
                        Text("Abra o Forja no iPhone").font(TipoW.titulo(22)).foregroundStyle(CorW.texto)
                        Text("O treino do dia chega aqui e fica guardado para treinar mesmo sem o iPhone por perto.")
                            .font(.system(size: 13, design: .rounded)).foregroundStyle(CorW.texto2)
                        Button("Sincronizar") { m.pedirSessao() }.padding(.top, 4)
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)
            }
            .navigationTitle("Forja")
            .containerBackground(CorW.brasa.opacity(0.22).gradient, for: .navigation)
        }
    }

    func resumo(_ s: SessaoRelogio) -> String {
        let ex = Set(s.passos.filter { $0.bloco != "Aquecimento" && $0.bloco != "Desaquecimento" }.map(\.exId)).count
        return "\(s.minutos > 0 ? "\(s.minutos) min · " : "")\(ex) exercícios · \(s.passos.count) séries"
    }
}

// MARK: - Treino ao vivo

struct TreinoRelogioView: View {
    @EnvironmentObject var m: ModeloRelogio
    @State private var pagina = 0

    var cor: Color { CorW.tipo(m.sessao?.tipo ?? "forca") }

    var body: some View {
        ZStack {
            TabView(selection: $pagina) {
                exercicio.tag(0)
                metricas.tag(1)
            }
            .tabViewStyle(.verticalPage)
            if m.descansando { descanso.transition(.opacity) }
        }
        .animation(.easeOut(duration: 0.2), value: m.descansando)
        .background(CorW.fundo.ignoresSafeArea())
    }

    var cabecalho: some View {
        HStack {
            Text(RelogioFormato.duracao(Int(Date().timeIntervalSince(m.inicio)))).font(TipoW.numero(18)).monospacedDigit().foregroundStyle(CorW.texto)
            Spacer()
            FCView(bpm: m.bpm, tamanho: 18)
        }
    }

    @ViewBuilder var exercicio: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 6) {
                cabecalho
                if let p = m.passo {
                    HStack {
                        RotuloW(p.rotulo, cor)
                        Spacer()
                        Text("\(m.i + 1)/\(m.passos.count)").font(.system(size: 11, weight: .bold, design: .rounded)).foregroundStyle(CorW.texto2)
                    }
                    Text(p.nome).font(TipoW.titulo(21)).foregroundStyle(CorW.texto).lineLimit(2).minimumScaleFactor(0.7)
                    if p.porTempo {
                        let seg = m.restanteSeg ?? p.trabalhoSeg ?? 0
                        Text(RelogioFormato.relogio(seg)).font(TipoW.numero(46)).monospacedDigit().foregroundStyle(cor).frame(maxWidth: .infinity)
                        Button {
                            if m.fimEm == nil { m.iniciarTempo() } else { m.concluirSerie() }
                        } label: {
                            Label(m.fimEm == nil ? "Iniciar" : "Concluir", systemImage: m.fimEm == nil ? "play.fill" : "checkmark")
                                .font(.system(size: 16, weight: .heavy, design: .rounded)).frame(maxWidth: .infinity, minHeight: 34)
                        }
                        .buttonStyle(.borderedProminent).tint(cor).foregroundStyle(CorW.fundo)
                    } else {
                        HStack(spacing: 4) {
                            botaoMenor("minus") { m.reps = max(0, m.reps - 1) }
                            VStack(spacing: -2) {
                                Text("\(m.reps)").font(TipoW.numero(36)).monospacedDigit().foregroundStyle(CorW.texto)
                                Text(p.temCarga ? "reps · \(RelogioFormato.kg(m.kg)) kg" : "reps (\(p.reps ?? "\(p.repsAlvo)"))")
                                    .font(.system(size: 11, weight: .semibold, design: .rounded)).foregroundStyle(CorW.texto2).lineLimit(1).minimumScaleFactor(0.7)
                            }.frame(maxWidth: .infinity)
                            botaoMenor("plus") { m.reps += 1 }
                        }
                        Button { m.concluirSerie() } label: {
                            Label(m.i == m.passos.count - 1 ? "Finalizar" : "Concluir série", systemImage: "checkmark")
                                .font(.system(size: 16, weight: .heavy, design: .rounded)).frame(maxWidth: .infinity, minHeight: 34)
                        }
                        .buttonStyle(.borderedProminent).tint(cor).foregroundStyle(CorW.fundo)
                        if p.temCarga {
                            HStack {
                                Button("−2,5 kg") { m.kg = max(0, m.kg - 2.5) }
                                Button("+2,5 kg") { m.kg += 2.5 }
                            }.font(.system(size: 12, weight: .bold, design: .rounded))
                        }
                    }
                } else {
                    Text("Medindo seu treino").font(TipoW.titulo(20)).foregroundStyle(CorW.texto)
                    Text("Siga pelo iPhone. FC e calorias vão para o app Saúde.").font(.system(size: 12, design: .rounded)).foregroundStyle(CorW.texto2)
                }
            }
        }
    }

    func botaoMenor(_ icone: String, acao: @escaping () -> Void) -> some View {
        Button(action: acao) { Image(systemName: icone).font(.system(size: 14, weight: .heavy)) }
            .buttonStyle(.bordered).frame(width: 40).clipShape(Circle())
    }

    var metricas: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(RelogioFormato.duracao(Int(Date().timeIntervalSince(m.inicio)))).font(TipoW.numero(34)).monospacedDigit().foregroundStyle(CorW.brasa)
            FCView(bpm: m.bpm, tamanho: 30)
            HStack(spacing: 4) {
                Text("\(Int(m.treino.kcal))").font(TipoW.numero(28)).foregroundStyle(CorW.texto)
                Text("kcal ativas").font(.system(size: 12, weight: .semibold, design: .rounded)).foregroundStyle(CorW.texto2)
            }
            Text("\(m.feitas.count) de \(m.passos.count) séries").font(.system(size: 12, design: .rounded)).foregroundStyle(CorW.texto2)
            Spacer(minLength: 2)
            Button(role: .destructive) { m.encerrar() } label: {
                Label(m.encerrando ? "Salvando…" : "Encerrar", systemImage: "xmark").font(.system(size: 15, weight: .heavy, design: .rounded)).frame(maxWidth: .infinity)
            }.disabled(m.encerrando)
            if m.espelhado { Text("Espelhado com o iPhone").font(.system(size: 10, design: .rounded)).foregroundStyle(CorW.texto2).frame(maxWidth: .infinity) }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
    }

    var descanso: some View {
        let seg = m.restanteSeg ?? 0
        let total = Double(max(1, m.passo?.descanso ?? 1))
        let prox = m.passos.indices.contains(m.i + 1) ? m.passos[m.i + 1] : nil
        return VStack(spacing: 4) {
            HStack { RotuloW("Descanso", cor); Spacer(); FCView(bpm: m.bpm, tamanho: 14) }
            ZStack {
                Circle().stroke(CorW.sup2, lineWidth: 8)
                Circle().trim(from: 0, to: Double(seg) / total).stroke(cor, style: StrokeStyle(lineWidth: 8, lineCap: .round)).rotationEffect(.degrees(-90))
                Text(RelogioFormato.relogio(seg)).font(TipoW.numero(seg >= 60 ? 40 : 50)).monospacedDigit().foregroundStyle(CorW.texto)
            }
            .frame(width: 104, height: 104)
            if let prox { Text("A seguir: \(prox.nome)").font(.system(size: 11, weight: .semibold, design: .rounded)).foregroundStyle(CorW.texto2).lineLimit(1) }
            HStack(spacing: 6) {
                Button("+15") { m.ajustarDescanso(15) }.font(.system(size: 14, weight: .heavy, design: .rounded)).frame(width: 56)
                Button { m.pularDescanso() } label: {
                    Label("Pular", systemImage: "forward.end.fill").font(.system(size: 14, weight: .heavy, design: .rounded)).frame(maxWidth: .infinity)
                }.buttonStyle(.borderedProminent).tint(cor).foregroundStyle(CorW.fundo)
            }
        }
        .padding(.horizontal, 6)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(CorW.fundo.opacity(0.97).ignoresSafeArea())
    }
}

struct FCView: View {
    let bpm: Int?
    var tamanho: CGFloat = 18
    var body: some View {
        HStack(spacing: 3) {
            Image(systemName: "heart.fill").font(.system(size: tamanho * 0.6)).foregroundStyle(CorW.fc)
                .symbolEffect(.pulse, isActive: bpm != nil)
            Text(bpm.map(String.init) ?? "--").font(TipoW.numero(tamanho)).monospacedDigit().foregroundStyle(CorW.texto)
            if tamanho >= 24 { Text("bpm").font(.system(size: 12, weight: .semibold, design: .rounded)).foregroundStyle(CorW.texto2) }
        }
        .accessibilityLabel(bpm.map { "Frequência cardíaca \($0) batimentos por minuto" } ?? "Frequência cardíaca indisponível")
    }
}

// MARK: - Concluído

struct ConcluidoRelogioView: View {
    @EnvironmentObject var m: ModeloRelogio
    var body: some View {
        ScrollView {
            VStack(spacing: 6) {
                Image(systemName: "checkmark.circle.fill").font(.system(size: 34)).foregroundStyle(CorW.ok)
                RotuloW("Treino concluído", CorW.ok)
                if let r = m.registro {
                    Text(r.titulo).font(TipoW.titulo(18)).foregroundStyle(CorW.texto).multilineTextAlignment(.center).lineLimit(2)
                    Grid(horizontalSpacing: 8, verticalSpacing: 6) {
                        GridRow {
                            numero(RelogioFormato.duracao(r.duracaoSeg), "duração")
                            numero(r.kcal.map(String.init) ?? "—", "kcal")
                        }
                        GridRow {
                            numero(r.fcMedia.map(String.init) ?? "—", "FC média")
                            numero(r.fcMax.map(String.init) ?? "—", "FC máx")
                        }
                    }
                    .padding(.top, 4)
                    Text(r.salvoNoSaude ? "Salvo no app Saúde" : (r.series.isEmpty ? "Nenhuma série registrada" : "Enviado ao iPhone"))
                        .font(.system(size: 11, design: .rounded)).foregroundStyle(CorW.texto2)
                }
                Button("OK") { m.voltarAoInicio() }.padding(.top, 4)
            }
        }
        .background(CorW.fundo.ignoresSafeArea())
    }

    func numero(_ v: String, _ rotulo: String) -> some View {
        VStack(spacing: 0) {
            Text(v).font(TipoW.numero(24)).monospacedDigit().foregroundStyle(CorW.texto).lineLimit(1).minimumScaleFactor(0.6)
            Text(rotulo).font(.system(size: 10, weight: .semibold, design: .rounded)).foregroundStyle(CorW.texto2)
        }
        .frame(maxWidth: .infinity).padding(.vertical, 6)
        .background(CorW.sup1, in: RoundedRectangle(cornerRadius: 12))
    }
}
