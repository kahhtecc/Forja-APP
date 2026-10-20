import SwiftUI
import ForjaCore
import AudioToolbox

/// Treino ao vivo: séries, cronômetro por tempo, descanso com contagem regressiva, sons e vibração.
struct TreinoView: View {
    @EnvironmentObject var app: AppEstado
    let alvo: TreinoAlvo
    let fim: (Registro?) -> Void

    @State private var passos: [Passo] = []
    @State private var i = 0
    @State private var descansando = false
    @State private var fimEm: Date?
    @State private var pausado: TimeInterval?
    @State private var reps = 10
    @State private var kg = 0.0
    @State private var feitas: [Int: SerieFeita] = [:]
    @State private var inicio = Date()
    @State private var agora = Date()
    @State private var ultimoBip = -1
    @State private var confirmarSaida = false
    @State private var video: String?

    let tique = Timer.publish(every: 0.2, on: .main, in: .common).autoconnect()

    var cor: Color { Cor.tipoSessao(alvo.sessao.tipo, app.corModalidade) }
    var p: Passo? { passos.indices.contains(i) ? passos[i] : nil }
    var restante: TimeInterval? { pausado ?? fimEm.map { max(0, $0.timeIntervalSince(agora)) } }
    var restanteSeg: Int? { restante.map { Int(ceil($0)) } }

    var body: some View {
        ZStack {
            Cor.fundo.ignoresSafeArea()
            if let p {
                VStack(spacing: 0) {
                    topo(p)
                    ScrollView {
                        VStack(alignment: .leading, spacing: 0) {
                            DemoExercicio(ex: p.ex, cor: cor, cantos: 26).aspectRatio(1.45, contentMode: .fit).frame(maxWidth: .infinity).padding(.top, 14)
                            HStack { Rotulo(p.rotulo, cor); Spacer(); Text("\(i + 1) / \(passos.count)").font(Tipo.pequeno).foregroundStyle(Cor.texto3) }.padding(.top, 16)
                            Text(p.ex.nome).font(Tipo.titulo1).padding(.top, 4)
                            HStack(spacing: 8) {
                                Etiqueta(texto: p.porTempo ? Roteiro.formatarTempo(p.item.trabalhoSeg ?? 0) : "\(p.item.reps ?? "") reps", cor: cor, cheia: true)
                                if let x = p.item.intensidade { Etiqueta(texto: x, cor: cor) }
                            }.padding(.top, 10)
                            if let n = p.item.nota { Text(n).font(Tipo.pequeno).foregroundStyle(Cor.texto2).padding(.top, 8) }
                            Group {
                                if p.porTempo { cronometro(p) } else { contadores(p) }
                            }.padding(.top, 18)
                            Cartao(padding: 16) {
                                Rotulo("Execução", cor)
                                ForEach(Array(p.ex.dicas.enumerated()), id: \.offset) { k, d in
                                    HStack(alignment: .top) { Text("\(k + 1)").font(Tipo.pequenoForte).foregroundStyle(cor).frame(width: 18, alignment: .leading); Text(d).font(Tipo.pequeno) }.padding(.top, 6)
                                }
                            }.padding(.top, 18).padding(.bottom, 16)
                        }.padding(.horizontal, 20)
                    }
                    controles(p)
                }
                if descansando { descanso(p).transition(.opacity) }
            }
        }
        .foregroundStyle(Cor.texto)
        .onAppear {
            passos = Roteiro.passos(alvo.sessao, app.catalogo)
            inicio = Date()
            UIApplication.shared.isIdleTimerDisabled = app.e.ajustes.telaLigada
            preparar()
        }
        .onDisappear { UIApplication.shared.isIdleTimerDisabled = false }
        .onReceive(tique) { _ in agora = Date(); verificarCronometro() }
        .confirmationDialog("Sair do treino?", isPresented: $confirmarSaida, titleVisibility: .visible) {
            if !feitas.isEmpty { Button("Salvar e sair") { finalizar() } }
            Button(feitas.isEmpty ? "Sair" : "Descartar", role: .destructive) { fim(nil) }
            Button("Continuar treinando", role: .cancel) {}
        } message: { Text(feitas.isEmpty ? "Nada foi registrado ainda." : "Você já fez \(feitas.count) séries.") }
        .sheet(item: Binding(get: { video.map { IdTexto(id: $0) } }, set: { video = $0?.id })) { v in
            NavigationStack { VideoView(id: v.id) }.environmentObject(app).preferredColorScheme(.dark)
        }
    }

    // MARK: partes

    func topo(_ p: Passo) -> some View {
        let d = Int(agora.timeIntervalSince(inicio))
        return VStack(spacing: 8) {
            HStack {
                BotaoIcone(icone: "xmark", descricao: "Sair do treino") { confirmarSaida = true }
                Spacer()
                VStack(spacing: 0) {
                    Text(d >= 3600 ? String(format: "%d:%02d:%02d", d / 3600, d % 3600 / 60, d % 60) : String(format: "%d:%02d", d / 60, d % 60)).font(Tipo.display(24)).monospacedDigit()
                    Rotulo(p.blocoNome, cor)
                }
                Spacer()
                BotaoIcone(icone: "play.rectangle.fill", descricao: "Ver vídeo de \(p.ex.nome)", cor: cor) { video = p.ex.id }
            }
            HStack(spacing: 3) {
                let grupos = gruposProgresso()
                ForEach(Array(grupos.enumerated()), id: \.offset) { _, g in
                    BarraProgresso(progresso: Double(g.filter { $0 < i || feitas[$0] != nil }.count) / Double(g.count), cor: cor, altura: 4)
                        .frame(maxWidth: .infinity)
                        .layoutPriority(Double(min(g.count, 4)))
                }
            }
        }
        .padding(.horizontal, 16).padding(.top, 8)
    }

    func gruposProgresso() -> [[Int]] {
        var ordem: [String] = []; var m: [String: [Int]] = [:]
        for (k, x) in passos.enumerated() { let c = "\(x.blocoIdx)-\(x.itemIdx)"; if m[c] == nil { ordem.append(c) }; m[c, default: []].append(k) }
        if ordem.count > 24 {
            var o2: [Int] = []; var m2: [Int: [Int]] = [:]
            for (k, x) in passos.enumerated() { if m2[x.blocoIdx] == nil { o2.append(x.blocoIdx) }; m2[x.blocoIdx, default: []].append(k) }
            return o2.map { m2[$0]! }
        }
        return ordem.map { m[$0]! }
    }

    func cronometro(_ p: Passo) -> some View {
        let total = Double(p.item.trabalhoSeg ?? 1)
        let prog = (restante == nil || descansando) ? 0 : 1 - (restante! / total)
        let seg = (descansando || restanteSeg == nil) ? (p.item.trabalhoSeg ?? 0) : restanteSeg!
        return Anel(progresso: prog, cor: cor, espessura: 12) {
            VStack {
                Text(relogio(seg)).font(Tipo.gigante).monospacedDigit()
                Text(fimEm == nil && pausado == nil ? "toque em iniciar" : (pausado != nil ? "pausado" : "em andamento")).font(Tipo.pequeno).foregroundStyle(Cor.texto2)
            }
        }
        .frame(width: 200, height: 200).frame(maxWidth: .infinity)
    }

    func contadores(_ p: Passo) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(spacing: 12) {
                contador("Repetições", "\(reps)", menos: { reps = max(0, reps - 1) }, mais: { reps += 1 })
                if temCarga(p) { contador("Carga (kg)", Progresso.fmtKg(kg), menos: { kg = max(0, kg - 2.5) }, mais: { kg += 2.5 }) }
            }
            if let s = Progresso.sugestao(app.e.registros, p.item) { Text(s).font(Tipo.pequeno).foregroundStyle(Cor.texto2) }
        }
    }

    func contador(_ rotulo: String, _ valor: String, menos: @escaping () -> Void, mais: @escaping () -> Void) -> some View {
        Cartao(padding: 12) {
            Rotulo(rotulo)
            HStack {
                BotaoIcone(icone: "minus", descricao: "Menos \(rotulo)", tamanho: 40, acao: menos)
                Text(valor).font(Tipo.titulo1).monospacedDigit().frame(maxWidth: .infinity).lineLimit(1).minimumScaleFactor(0.6)
                BotaoIcone(icone: "plus", descricao: "Mais \(rotulo)", tamanho: 40, acao: mais)
            }.padding(.top, 6)
        }
    }

    func controles(_ p: Passo) -> some View {
        HStack(spacing: 10) {
            BotaoIcone(icone: "backward.end.fill", descricao: "Anterior", tamanho: 54) { irPara(i - 1) }
            if p.porTempo {
                let rodando = fimEm != nil && pausado == nil
                BotaoPrimario(texto: rodando ? "Pausar" : (pausado != nil ? "Continuar" : "Iniciar"), icone: rodando ? "pause.fill" : "play.fill", cor: cor == Cor.brasa ? nil : cor) {
                    if rodando { pausado = max(0, fimEm!.timeIntervalSinceNow) }
                    else if let r = pausado { fimEm = Date().addingTimeInterval(r); pausado = nil }
                    else { fimEm = Date().addingTimeInterval(Double(p.item.trabalhoSeg ?? 0)); ultimoBip = -1 }
                }
            } else {
                BotaoPrimario(texto: i == passos.count - 1 ? "Finalizar treino" : "Concluir série", icone: "checkmark", cor: cor == Cor.brasa ? nil : cor) { concluirSerie() }
            }
            BotaoIcone(icone: "forward.end.fill", descricao: p.porTempo ? "Concluir agora" : "Pular", tamanho: 54) { if p.porTempo { concluirSerie() } else { irPara(i + 1) } }
        }
        .padding(.horizontal, 16).padding(.vertical, 10)
    }

    func descanso(_ p: Passo) -> some View {
        let prox = passos.indices.contains(i + 1) ? passos[i + 1] : nil
        let total = max(1, p.descansoDepois)
        return VStack(spacing: 0) {
            Rotulo(prox != nil && prox!.tipoBloco == .INTERVALADO && prox!.ex.id == p.ex.id ? "Recuperação" : "Descanso", cor).padding(.top, 40)
            Anel(progresso: Double(restanteSeg ?? 0) / Double(total), cor: cor, espessura: 14) {
                Text(relogio(restanteSeg ?? 0)).font(Tipo.display(92)).monospacedDigit()
            }.frame(width: 250, height: 250).padding(.top, 20)
            HStack(spacing: 12) {
                BotaoSecundario(texto: "−15 s") { fimEm = max(Date().addingTimeInterval(1), (fimEm ?? Date()).addingTimeInterval(-15)) }
                BotaoSecundario(texto: "+15 s") { fimEm = (fimEm ?? Date()).addingTimeInterval(15) }
            }.frame(width: 240).padding(.top, 24)
            Spacer()
            if let prox {
                VStack(alignment: .leading, spacing: 10) {
                    Rotulo("A seguir")
                    HStack(spacing: 14) {
                        DemoExercicio(ex: prox.ex, cor: cor, animar: false, cantos: 14).frame(width: 70, height: 70)
                        VStack(alignment: .leading) {
                            Text(prox.ex.nome).font(Tipo.corpoForte).lineLimit(2)
                            Text("\(prox.rotulo) · \(Roteiro.prescricao(prox.item).components(separatedBy: "× ").last ?? "")").font(Tipo.pequeno).foregroundStyle(Cor.texto2)
                        }
                        Spacer()
                    }
                    .padding(12).background(Cor.sup1, in: RoundedRectangle(cornerRadius: 20, style: .continuous))
                }.padding(.bottom, 16)
            }
            BotaoPrimario(texto: "Pular descanso", icone: "forward.end.fill", cor: cor == Cor.brasa ? nil : cor) { irPara(i + 1, auto: true) }
        }
        .padding(24)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Cor.fundo.opacity(0.98).ignoresSafeArea())
    }

    // MARK: lógica (igual ao Android)

    func temCarga(_ p: Passo) -> Bool { p.ex.equip.contains { ["barra", "halter", "kettlebell", "maquina", "polia", "bola"].contains($0) } }

    func repsAlvo(_ p: Passo) -> Int {
        let r = p.item.reps ?? ""
        return Int(r.components(separatedBy: CharacterSet(charactersIn: "–- ")).first ?? "") ?? 10
    }

    func preparar() {
        guard let p else { return }
        let anterior = feitas.sorted { $0.key < $1.key }.last { passos[$0.key].ex.id == p.ex.id }?.value
        reps = anterior?.reps ?? repsAlvo(p)
        kg = anterior?.kg ?? Progresso.ultimas(app.e.registros, p.ex.id).map(\.kg).max() ?? 0
    }

    func irPara(_ n: Int, auto: Bool = false) {
        descansando = false; fimEm = nil; pausado = nil
        if n > passos.count - 1 { finalizar(); return }
        let anterior = p
        withAnimation(.easeOut(duration: 0.2)) { i = max(0, n) }
        preparar()
        if let novo = p, auto, novo.porTempo, let a = anterior, a.porTempo, a.blocoIdx == novo.blocoIdx {
            fimEm = Date().addingTimeInterval(Double(novo.item.trabalhoSeg ?? 0)); ultimoBip = -1
        }
    }

    func concluirSerie() {
        guard let p else { return }
        if app.e.ajustes.vibracao { Haptico.sucesso() }
        feitas[i] = p.porTempo ? SerieFeita(p.ex.id, 0, 0, seg: p.item.trabalhoSeg ?? 0) : SerieFeita(p.ex.id, reps, temCarga(p) ? kg : 0)
        if i == passos.count - 1 { finalizar(); return }
        if p.descansoDepois > 0 {
            withAnimation { descansando = true }
            fimEm = Date().addingTimeInterval(Double(p.descansoDepois)); pausado = nil; ultimoBip = -1
        } else { irPara(i + 1) }
    }

    func verificarCronometro() {
        guard let r = restanteSeg, pausado == nil else { return }
        if r > 3 { ultimoBip = -1 }
        if (1...3).contains(r) && ultimoBip != r {
            ultimoBip = r
            if app.e.ajustes.som { AudioServicesPlaySystemSound(1103) }
            if app.e.ajustes.vibracao { Haptico.toque() }
        }
        if r == 0 && ultimoBip != 0 {
            ultimoBip = 0
            if app.e.ajustes.som { AudioServicesPlaySystemSound(1025) }
            if app.e.ajustes.vibracao { Haptico.forte() }
            if descansando { irPara(i + 1, auto: true) } else { concluirSerie() }
        }
    }

    func finalizar() {
        let series = feitas.sorted { $0.key < $1.key }.map(\.value)
        let dur = Int(Date().timeIntervalSince(inicio))
        fim(Registro(epochDay: app.loja.hoje(), semana: alvo.semana, sessaoIdx: alvo.idx, titulo: alvo.sessao.titulo, tipo: alvo.sessao.tipo, duracaoSeg: dur, series: series, esforco: 7, nota: ""))
    }
}

struct IdTexto: Identifiable { let id: String }

func relogio(_ s: Int) -> String { s >= 60 ? String(format: "%d:%02d", s / 60, s % 60) : "\(s)" }

// MARK: - Concluído

struct ConcluidoView: View {
    @EnvironmentObject var app: AppEstado
    let registro: Registro
    let fechar: () -> Void
    @State private var esforco = 7
    @State private var nota = ""
    static let escala = ["Muito leve", "Muito leve", "Leve", "Leve", "Moderado", "Moderado", "Difícil", "Difícil", "Muito difícil", "Quase máximo", "Máximo"]

    var body: some View {
        let cor = Cor.tipoSessao(registro.tipo, app.corModalidade)
        let volume = Progresso.volumeKg(registro)
        ScrollView {
            VStack(spacing: 0) {
                ZStack {
                    Circle().fill(cor.opacity(0.15)).frame(width: 110, height: 110)
                    Circle().fill(cor).frame(width: 78, height: 78)
                    Image(systemName: "checkmark").font(.system(size: 38, weight: .heavy)).foregroundStyle(Cor.fundo)
                }.padding(.top, 30)
                Rotulo("Treino concluído", cor).padding(.top, 20)
                Text(registro.titulo).font(Tipo.titulo1).multilineTextAlignment(.center)
                HStack(spacing: 10) {
                    Cartao(padding: 14) { Estatistica(valor: "\(registro.duracaoSeg / 60)", rotulo: "minutos") }
                    Cartao(padding: 14) { Estatistica(valor: "\(registro.series.count)", rotulo: "séries feitas") }
                    Cartao(padding: 14) { Estatistica(valor: volume > 0 ? Progresso.fmtKg(volume) : "—", rotulo: "kg de volume") }
                }.padding(.top, 22)
                Text("Como foi o esforço?").font(Tipo.titulo3).padding(.top, 26)
                Text("\(esforco)/10 · \(Self.escala[esforco])").font(Tipo.corpoForte).foregroundStyle(cor).padding(.top, 4)
                HStack {
                    ForEach(1...10, id: \.self) { n in
                        Button { Haptico.toque(); esforco = n } label: {
                            Text("\(n)").font(Tipo.pequenoForte).foregroundStyle(n <= esforco ? Cor.texto : Cor.texto3)
                                .frame(width: 30, height: 30)
                                .background(n <= esforco ? cor.opacity(0.25 + Double(n) * 0.07) : Cor.sup2, in: RoundedRectangle(cornerRadius: 9))
                                .overlay(RoundedRectangle(cornerRadius: 9).stroke(n == esforco ? Cor.texto : .clear, lineWidth: 2))
                        }.buttonStyle(.plain).frame(maxWidth: .infinity)
                    }
                }.padding(.top, 12)
                TextField("Anotação (opcional): como se sentiu, ajustes…", text: $nota, axis: .vertical)
                    .font(Tipo.corpo).lineLimit(2...4)
                    .padding(16).background(Cor.sup1, in: RoundedRectangle(cornerRadius: 16)).padding(.top, 20)
                BotaoPrimario(texto: "Salvar treino", icone: "checkmark", cor: cor == Cor.brasa ? nil : cor) {
                    var r = registro; r.esforco = esforco; r.nota = nota.trimmingCharacters(in: .whitespaces)
                    app.loja.registrar(r); Haptico.sucesso(); fechar()
                }.padding(.top, 26)
                Button("Descartar") { fechar() }.font(Tipo.pequenoForte).foregroundStyle(Cor.texto3).padding(10)
            }.padding(24)
        }
        .telaForja()
    }
}
