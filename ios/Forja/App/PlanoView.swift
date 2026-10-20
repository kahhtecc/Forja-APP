import SwiftUI
import ForjaCore

struct PlanoView: View {
    @EnvironmentObject var app: AppEstado
    let abrir: (Rota) -> Void
    @State private var sel: Int?

    var body: some View {
        if let plano = app.plano {
            let atual = app.semanaAtual
            let s = sel ?? atual
            let semana = plano.semanas[s - 1]
            let feitas = Progresso.feitas(app.e.registros, s)
            let corM = app.corModalidade
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    HStack(spacing: 8) {
                        Etiqueta(texto: plano.modalidade.curto, cor: corM, icone: plano.modalidade.simbolo)
                        Etiqueta(texto: plano.nivel.nome, cor: Cor.texto2)
                    }
                    Text(plano.nome).font(Tipo.titulo1).padding(.top, 12)
                    Text(plano.resumo).font(Tipo.corpo).foregroundStyle(Cor.texto2).padding(.top, 8)
                    Text(plano.metaSemanal).font(Tipo.pequenoForte).foregroundStyle(corM).padding(.top, 6)
                }
                .padding(.horizontal, 20).padding(.top, 10)

                ScrollViewReader { proxy in
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 10) {
                            ForEach(plano.semanas, id: \.numero) { w in
                                let n = w.numero
                                let completa = Progresso.feitas(app.e.registros, n).count >= w.sessoes.count
                                let ativo = n == s
                                Button { Haptico.toque(); sel = n } label: {
                                    VStack(spacing: 2) {
                                        Text(String(format: "S%02d", n)).font(Tipo.display(24))
                                        if completa { Image(systemName: "checkmark.circle.fill").font(.system(size: 14)).foregroundStyle(ativo ? Cor.fundo : Cor.ok) }
                                        else { Text(n == atual ? "atual" : String(w.fase.prefix(10))).font(Tipo.texto(10, "ExtraBold")).textCase(.uppercase).lineLimit(1).opacity(0.8) }
                                    }
                                    .foregroundStyle(ativo ? Cor.fundo : Cor.texto)
                                    .frame(width: 78).padding(.vertical, 12)
                                    .background(ativo ? corM : Cor.sup1, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
                                    .overlay(RoundedRectangle(cornerRadius: 18, style: .continuous).stroke(n == atual && !ativo ? corM : Cor.borda, lineWidth: 1))
                                }
                                .buttonStyle(.plain).id(n)
                                .accessibilityLabel("Semana \(n)")
                            }
                        }.padding(.horizontal, 20)
                    }
                    .onAppear { proxy.scrollTo(max(1, atual - 1), anchor: .leading) }
                }
                .padding(.top, 14)

                VStack(alignment: .leading, spacing: 10) {
                    Cartao(cor: corM.opacity(0.07), borda: corM.opacity(0.3)) {
                        Rotulo("Semana \(s) · \(semana.fase)", corM)
                        Text(semana.nota).font(Tipo.corpo).padding(.top, 6)
                    }
                    ForEach(Array(semana.sessoes.enumerated()), id: \.offset) { i, ses in
                        CartaoSessao(sessao: ses, feita: feitas.contains(i), corM: corM) { abrir(.sessao(semana: s, idx: i)) }
                    }
                    Secao(titulo: "Como progredir")
                    ForEach(plano.dicas, id: \.self) { d in
                        HStack(alignment: .top, spacing: 12) {
                            Circle().fill(corM).frame(width: 6, height: 6).padding(.top, 8)
                            Text(d).font(Tipo.corpo).foregroundStyle(Cor.texto2)
                        }
                    }
                }
                .padding(.horizontal, 20).padding(.top, 16).padding(.bottom, ESPACO_BARRA)
            }
            .telaForja()
        }
    }
}

struct CartaoSessao: View {
    @EnvironmentObject var app: AppEstado
    let sessao: Sessao
    let feita: Bool
    let corM: Color
    let acao: () -> Void
    var body: some View {
        let cor = Cor.tipoSessao(sessao.tipo, corM)
        Button { Haptico.toque(); acao() } label: {
            HStack(spacing: 14) {
                ZStack {
                    if let c = capaSessao(sessao).flatMap({ app.catalogo[$0] }) { DemoExercicio(ex: c, cor: cor, animar: false, cantos: 16) }
                    if feita {
                        RoundedRectangle(cornerRadius: 16, style: .continuous).fill(Cor.ok.opacity(0.55))
                        Image(systemName: "checkmark").font(.system(size: 24, weight: .heavy)).foregroundStyle(.white)
                    }
                }.frame(width: 72, height: 72)
                VStack(alignment: .leading, spacing: 3) {
                    Rotulo("\(DIAS[sessao.diaSemana - 1]) · \(sessao.foco)", cor)
                    Text(sessao.titulo).font(Tipo.titulo3).lineLimit(2).multilineTextAlignment(.leading)
                    let n = nExercicios(sessao)
                    Text("\(sessao.minutos) min · \(n) \(n == 1 ? "exercício" : "exercícios")").font(Tipo.pequeno).foregroundStyle(Cor.texto2)
                }
                Spacer(minLength: 0)
                Image(systemName: "chevron.right").foregroundStyle(Cor.texto3)
            }
            .padding(14)
            .background(Cor.sup1, in: RoundedRectangle(cornerRadius: 22, style: .continuous))
            .overlay(RoundedRectangle(cornerRadius: 22, style: .continuous).stroke(Cor.borda, lineWidth: 1))
        }
        .buttonStyle(Pressionavel())
        .foregroundStyle(Cor.texto)
    }
}

// MARK: - Detalhe

struct SessaoView: View {
    @EnvironmentObject var app: AppEstado
    let semana: Int
    let idx: Int
    let abrir: (Rota) -> Void
    var body: some View {
        if let plano = app.plano, semana - 1 < plano.semanas.count, idx < plano.semanas[semana - 1].sessoes.count {
            let s = plano.semanas[semana - 1].sessoes[idx]
            let cor = Cor.tipoSessao(s.tipo, app.corModalidade)
            let feito = app.e.registros.last { $0.semana == semana && $0.sessaoIdx == idx }
            DetalheSessao(sessao: s, cor: cor, cabecalho: "Semana \(semana) · \(DIAS[s.diaSemana - 1])", subtitulo: s.foco,
                          aviso: feito.map { "Concluído · \($0.duracaoSeg / 60) min · esforço \($0.esforco)/10" },
                          rotuloBotao: feito != nil ? "Treinar de novo" : "Começar treino",
                          trocaSessao: idx, abrir: abrir,
                          comecar: { app.treinoAtivo = TreinoAlvo(sessao: s, semana: semana, idx: idx) }) {
                let recs = Array(Rotinas.recomendadas(plano.modalidade, app.e.perfil).prefix(2))
                if !recs.isEmpty {
                    Secao(titulo: "Preparo e volta à calma")
                    ForEach(recs) { r in
                        Button { abrir(.rotina(r.id)) } label: {
                            HStack(spacing: 12) {
                                IconeRedondo(icone: "figure.mind.and.body", cor: Cor.tema(r.tema), tamanho: 40)
                                VStack(alignment: .leading) {
                                    Text(r.titulo).font(Tipo.corpoForte)
                                    Text("\(Roteiro.minutos(r.sessao, app.catalogo)) min · \(r.categoria)").font(Tipo.pequeno).foregroundStyle(Cor.texto2)
                                }
                                Spacer()
                                Image(systemName: "chevron.right").foregroundStyle(Cor.texto3)
                            }
                            .padding(14).background(Cor.sup1, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
                        }.buttonStyle(Pressionavel()).foregroundStyle(Cor.texto)
                    }
                }
            }
        }
    }
}

struct RotinaView: View {
    @EnvironmentObject var app: AppEstado
    let id: String
    let abrir: (Rota) -> Void
    var body: some View {
        if let r = Rotinas.porId(id) {
            DetalheSessao(sessao: r.sessao, cor: Cor.tema(r.tema), cabecalho: r.categoria, subtitulo: r.subtitulo, aviso: nil, rotuloBotao: "Começar rotina",
                          trocaSessao: nil, abrir: abrir, comecar: { app.treinoAtivo = TreinoAlvo(sessao: r.sessao, semana: 0, idx: -1) }) { EmptyView() }
        }
    }
}

struct DetalheSessao<Extra: View>: View {
    @EnvironmentObject var app: AppEstado
    let sessao: Sessao
    let cor: Color
    let cabecalho: String
    let subtitulo: String
    let aviso: String?
    let rotuloBotao: String
    let trocaSessao: Int?
    let abrir: (Rota) -> Void
    let comecar: () -> Void
    @ViewBuilder var extra: () -> Extra

    var body: some View {
        ZStack(alignment: .bottom) {
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    ZStack(alignment: .bottomLeading) {
                        if let c = capaSessao(sessao).flatMap({ app.catalogo[$0] }), c.temImagem { FotoAsset(nome: "\(c.id)_0") } else { Cor.sup2 }
                        LinearGradient(stops: [.init(color: .black.opacity(0.35), location: 0), .init(color: .clear, location: 0.4), .init(color: Cor.fundo, location: 1)], startPoint: .top, endPoint: .bottom)
                        VStack(alignment: .leading, spacing: 4) {
                            Rotulo(cabecalho, cor)
                            Text(sessao.titulo).font(Tipo.titulo1).lineLimit(3).minimumScaleFactor(0.7)
                            Text(subtitulo).font(Tipo.corpo).foregroundStyle(Cor.texto2)
                        }.padding(.horizontal, 20).padding(.bottom, 8)
                    }
                    .frame(height: 300).clipped()

                    HStack(spacing: 8) {
                        Etiqueta(texto: "\(Roteiro.minutos(sessao, app.catalogo)) min", cor: cor, icone: "clock")
                        Etiqueta(texto: "\(Roteiro.exerciciosDaSessao(sessao).count) exercícios", cor: cor)
                    }.padding(.horizontal, 20).padding(.vertical, 8)
                    if let a = aviso {
                        Label(a, systemImage: "checkmark.circle.fill").font(Tipo.pequenoForte).foregroundStyle(Cor.ok)
                            .padding(12).background(Cor.ok.opacity(0.1), in: RoundedRectangle(cornerRadius: 14)).padding(.horizontal, 20)
                    }
                    ForEach(Array(sessao.blocos.enumerated()), id: \.offset) { _, b in
                        HStack(spacing: 10) {
                            LinhaBrasa(cor: cor)
                            Text(b.nome).font(Tipo.titulo3)
                            Spacer()
                            if b.voltas > 1 { Etiqueta(texto: "\(b.voltas) voltas", cor: cor, icone: "repeat") }
                        }.padding(.horizontal, 20).padding(.top, 22).padding(.bottom, 4)
                        if let n = b.nota { Text(n).font(Tipo.pequeno).foregroundStyle(Cor.texto2).padding(.horizontal, 20).padding(.bottom, 6) }
                        ForEach(Array(b.itens.enumerated()), id: \.offset) { _, it in
                            if let ex = app.catalogo[it.exId] {
                                let podeTrocar = trocaSessao != nil && (b.tipo == .PRINCIPAL || b.tipo == .CIRCUITO)
                                Button { Haptico.toque(); abrir(.exercicio(ex.id, trocaSessao: podeTrocar ? trocaSessao : nil)) } label: {
                                    HStack(spacing: 14) {
                                        DemoExercicio(ex: ex, cor: cor, animar: false, cantos: 14).frame(width: 64, height: 64)
                                        VStack(alignment: .leading, spacing: 2) {
                                            Text(ex.nome).font(Tipo.corpoForte).lineLimit(2).multilineTextAlignment(.leading)
                                            (Text(Roteiro.prescricao(it, circuito: b.tipo == .CIRCUITO, voltas: b.voltas)).foregroundColor(cor).font(Tipo.pequenoForte)
                                             + Text(it.intensidade.map { "  ·  \($0)" } ?? "").foregroundColor(Cor.texto2).font(Tipo.pequeno)).lineLimit(1)
                                            if let n = it.nota { Text(n).font(Tipo.pequeno).foregroundStyle(Cor.texto3).lineLimit(2) }
                                        }
                                        Spacer(minLength: 0)
                                        Image(systemName: podeTrocar ? "arrow.left.arrow.right" : "chevron.right").foregroundStyle(Cor.texto3)
                                    }
                                    .padding(.horizontal, 20).padding(.vertical, 8).contentShape(Rectangle())
                                }.buttonStyle(.plain).foregroundStyle(Cor.texto)
                            }
                        }
                    }
                    VStack(alignment: .leading, spacing: 10) { extra() }.padding(.horizontal, 20)
                }
                .padding(.bottom, 130)
            }
            VStack {
                BotaoPrimario(texto: rotuloBotao, icone: "play.fill", cor: cor == Cor.brasa ? nil : cor, acao: comecar)
            }
            .padding(.horizontal, 20).padding(.top, 24).padding(.bottom, 8)
            .background(LinearGradient(colors: [.clear, Cor.fundo, Cor.fundo], startPoint: .top, endPoint: .bottom).ignoresSafeArea())
        }
        .telaForja()
        .navigationBarTitleDisplayMode(.inline)
        .ignoresSafeArea(edges: .top)
    }
}
