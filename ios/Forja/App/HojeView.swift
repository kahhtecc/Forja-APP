import SwiftUI
import ForjaCore

struct HojeView: View {
    @EnvironmentObject var app: AppEstado
    let irAba: (Aba) -> Void
    let abrir: (Rota) -> Void
    let refazer: () -> Void

    var body: some View {
        if let plano = app.plano {
            let w = app.semanaAtual
            let semana = plano.semanas[w - 1]
            let feitas = Progresso.feitas(app.e.registros, w)
            let deHoje = app.loja.sessaoDeHoje()
            let proxima = app.loja.proximaSessao()
            let corM = app.corModalidade
            let hoje = app.loja.hoje()
            let nome = app.e.perfil?.nome ?? ""
            let minutosSemana = app.e.registros.filter { $0.epochDay >= Datas.segunda(hoje) }.reduce(0) { $0 + $1.duracaoSeg } / 60

            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    HStack(alignment: .center) {
                        VStack(alignment: .leading, spacing: 2) {
                            Rotulo(Self.dataLonga.string(from: Datas.data(hoje)))
                            Text(nome.isEmpty ? saudacao : "\(saudacao), \(nome)").font(Tipo.titulo1).lineLimit(1).minimumScaleFactor(0.7)
                        }
                        Spacer()
                        Button { Haptico.toque(); abrir(.perfil) } label: {
                            Text(String((nome.isEmpty ? "F" : nome).prefix(1)).uppercased()).font(Tipo.titulo3).foregroundStyle(.white)
                                .frame(width: 48, height: 48).background(Cor.gradBrasa, in: Circle())
                        }.accessibilityLabel("Perfil e ajustes")
                    }
                    .padding(.vertical, 8)

                    Group {
                        if let alvo = deHoje ?? proxima, !feitas.contains(alvo.0) {
                            Heroi(sessao: alvo.1, semana: w, fase: semana.fase, corM: corM, ehHoje: deHoje?.0 == alvo.0,
                                  comecar: { app.treinoAtivo = TreinoAlvo(sessao: alvo.1, semana: w, idx: alvo.0) },
                                  detalhes: { abrir(.sessao(semana: w, idx: alvo.0)) })
                        } else if let h = deHoje, feitas.contains(h.0) {
                            Cartao(cor: Cor.ok.opacity(0.08), borda: Cor.ok.opacity(0.4)) {
                                HStack(spacing: 14) {
                                    Image(systemName: "checkmark.circle.fill").font(.system(size: 34)).foregroundStyle(Cor.ok)
                                    VStack(alignment: .leading) { Rotulo("Treino de hoje concluído", Cor.ok); Text(h.1.titulo).font(Tipo.titulo2) }
                                }
                                Text("Recupere bem: hidratação, proteína e sono.").font(Tipo.pequeno).foregroundStyle(Cor.texto2).padding(.top, 10)
                            }
                        } else {
                            Cartao {
                                HStack(spacing: 14) {
                                    IconeRedondo(icone: "moon.stars.fill", cor: corM, tamanho: 48)
                                    VStack(alignment: .leading) { Rotulo(w >= plano.semanas.count ? "Plano concluído" : "Semana completa", corM); Text("Tudo feito por aqui").font(Tipo.titulo2) }
                                }
                                Text(w >= plano.semanas.count ? "Refaça o questionário no perfil para gerar o próximo bloco." : "Aproveite para descansar ou faça uma rotina de mobilidade.").font(Tipo.pequeno).foregroundStyle(Cor.texto2).padding(.top, 10)
                            }
                        }
                    }
                    .padding(.top, 6)

                    Secao(titulo: "Esta semana", acao: "Ver plano") { irAba(.plano) }
                    Faixa7Dias(sessoes: semana.sessoes, feitas: feitas, hojeDia: Datas.diaSemana(hoje), cor: corM) { abrir(.sessao(semana: w, idx: $0)) }

                    HStack(spacing: 12) {
                        Cartao(padding: 16) {
                            HStack(spacing: 12) {
                                Anel(progresso: Double(feitas.count) / Double(max(1, semana.sessoes.count)), cor: corM, espessura: 7) {
                                    Text("\(feitas.count)/\(semana.sessoes.count)").font(Tipo.pequenoForte)
                                }.frame(width: 56, height: 56)
                                VStack(alignment: .leading) {
                                    Text("Treinos").font(Tipo.corpoForte)
                                    Text("semana \(w) de \(plano.semanas.count)").font(Tipo.pequeno).foregroundStyle(Cor.texto2)
                                }
                            }
                        }
                        Cartao(padding: 16) { Estatistica(valor: "\(minutosSemana)", rotulo: "minutos ativos nesta semana") }
                    }
                    .padding(.top, 14)
                    HStack(spacing: 12) {
                        let seq = Progresso.sequenciaSemanas(app.e.registros, plano, w)
                        Cartao(padding: 16) { Estatistica(valor: "\(seq)", rotulo: seq == 1 ? "semana completa seguida" : "semanas completas seguidas", cor: corM) }
                        Cartao(padding: 16) { Estatistica(valor: "\(app.e.registros.count)", rotulo: "treinos concluídos no total") }
                    }
                    .padding(.top, 12)

                    Secao(titulo: "Mobilidade para você", acao: "Ver todas") { irAba(.mobilidade) }
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 12) {
                            ForEach(Rotinas.recomendadas(plano.modalidade, app.e.perfil)) { r in
                                CartaoRotinaPequeno(rotina: r) { abrir(.rotina(r.id)) }
                            }
                        }
                    }

                    if !plano.alertas.isEmpty {
                        VStack(spacing: 8) { ForEach(plano.alertas, id: \.self) { Aviso(texto: $0) } }.padding(.top, 18)
                    }

                    if !plano.dicas.isEmpty {
                        Secao(titulo: "Dica do dia")
                        Cartao {
                            HStack(alignment: .top, spacing: 14) {
                                IconeRedondo(icone: "lightbulb.fill", cor: Cor.alerta, tamanho: 40)
                                Text(plano.dicas[hoje % plano.dicas.count]).font(Tipo.corpo)
                            }
                        }
                    }
                }
                .padding(.horizontal, 20)
                .padding(.bottom, ESPACO_BARRA)
            }
            .telaForja()
        }
    }

    var saudacao: String {
        let h = Calendar.current.component(.hour, from: Date())
        return h < 12 ? "Bom dia" : (h < 18 ? "Boa tarde" : "Boa noite")
    }
    static let dataLonga: DateFormatter = { let f = DateFormatter(); f.locale = Locale(identifier: "pt_BR"); f.dateFormat = "EEEE, d 'de' MMMM"; return f }()
}

struct Heroi: View {
    @EnvironmentObject var app: AppEstado
    let sessao: Sessao
    let semana: Int
    let fase: String
    let corM: Color
    let ehHoje: Bool
    let comecar: () -> Void
    let detalhes: () -> Void

    var body: some View {
        let cor = Cor.tipoSessao(sessao.tipo, corM)
        let capa = capaSessao(sessao).flatMap { app.catalogo[$0] }
        ZStack(alignment: .bottomLeading) {
            if let c = capa, Animacoes3D.shared.tem(c.id) {
                VStack(spacing: 0) { Animacao3DView(id: c.id).frame(height: 290); Animacao3DView.fundo }
            } else if let c = capa, c.temImagem { FotoAsset(nome: "\(c.id)_1") } else { Cor.sup2 }
            LinearGradient(stops: [.init(color: .black.opacity(0.45), location: 0), .init(color: .black.opacity(0.2), location: 0.38),
                                   .init(color: Cor.fundo.opacity(0.85), location: 0.7), .init(color: Cor.fundo, location: 1)], startPoint: .top, endPoint: .bottom)
            VStack(alignment: .leading, spacing: 0) {
                HStack(spacing: 8) {
                    Etiqueta(texto: ehHoje ? "HOJE" : "PRÓXIMO", cor: cor, cheia: true)
                    Etiqueta(texto: "Semana \(semana) · \(fase)", cor: Cor.texto, sobreFoto: true)
                }
                Spacer()
                Text(sessao.titulo).font(Tipo.titulo1).lineLimit(2).minimumScaleFactor(0.7)
                Text(sessao.foco).font(Tipo.corpo).foregroundStyle(Cor.texto2).padding(.top, 6)
                HStack(spacing: 8) {
                    Etiqueta(texto: "\(sessao.minutos) min", cor: cor, icone: "clock", sobreFoto: true)
                    let n = nExercicios(sessao)
                    Etiqueta(texto: "\(n) \(n == 1 ? "exercício" : "exercícios")", cor: cor, icone: "dumbbell", sobreFoto: true)
                }.padding(.top, 14)
                BotaoPrimario(texto: "Começar treino", icone: "play.fill", cor: cor == Cor.brasa ? nil : cor, acao: comecar).padding(.top, 18)
            }
            .padding(20)
        }
        .frame(height: 390)
        .clipShape(RoundedRectangle(cornerRadius: 28, style: .continuous))
        .overlay(RoundedRectangle(cornerRadius: 28, style: .continuous).stroke(Cor.borda, lineWidth: 1))
        .contentShape(Rectangle())
        .onTapGesture { Haptico.toque(); detalhes() }
        .accessibilityElement(children: .contain)
    }
}

struct Faixa7Dias: View {
    let sessoes: [Sessao]
    let feitas: Set<Int>
    let hojeDia: Int?
    let cor: Color
    let abrir: (Int) -> Void
    var body: some View {
        HStack {
            ForEach(1...7, id: \.self) { d in
                let i = sessoes.firstIndex { $0.diaSemana == d }
                let feita = i.map { feitas.contains($0) } ?? false
                let ehHoje = d == hojeDia
                let corS = i.map { Cor.tipoSessao(sessoes[$0].tipo, cor) } ?? Cor.texto3
                Button { if let i { Haptico.toque(); abrir(i) } } label: {
                    VStack(spacing: 6) {
                        Text(DIAS[d - 1]).font(Tipo.pequenoForte).foregroundStyle(ehHoje ? Cor.texto : Cor.texto3)
                        ZStack {
                            Circle().fill(feita ? corS : (ehHoje ? Cor.sup3 : Cor.sup1))
                            Circle().stroke(i != nil && !feita ? corS.opacity(ehHoje ? 1 : 0.6) : (ehHoje ? Cor.texto : Cor.borda), lineWidth: ehHoje ? 2 : 1)
                            if feita { Image(systemName: "checkmark").font(.system(size: 14, weight: .heavy)).foregroundStyle(Cor.fundo) }
                            else if i != nil { Circle().fill(corS).frame(width: 8, height: 8) }
                        }.frame(width: 40, height: 40)
                    }
                }
                .buttonStyle(.plain)
                .disabled(i == nil)
                .frame(maxWidth: .infinity)
                .accessibilityLabel(i.map { "\(DIAS[d - 1]): \(sessoes[$0].titulo)" } ?? DIAS[d - 1])
            }
        }
    }
}

struct CartaoRotinaPequeno: View {
    @EnvironmentObject var app: AppEstado
    let rotina: Rotina
    let acao: () -> Void
    var body: some View {
        let cor = Cor.tema(rotina.tema)
        let itens = rotina.sessao.blocos[0].itens
        let ex = app.catalogo[(itens.count > 1 ? itens[1] : itens[0]).exId]
        Button { Haptico.toque(); acao() } label: {
            VStack(alignment: .leading, spacing: 0) {
                ZStack(alignment: .topLeading) {
                    if let ex { DemoExercicio(ex: ex, cor: cor, animar: false, cantos: 0) }
                    Etiqueta(texto: rotina.categoria, cor: cor, cheia: true).padding(10)
                }.frame(height: 110).clipped()
                VStack(alignment: .leading, spacing: 2) {
                    Text(rotina.titulo).font(Tipo.corpoForte).lineLimit(1)
                    Text("\(Roteiro.minutos(rotina.sessao, app.catalogo)) min · \(rotina.subtitulo)").font(Tipo.pequeno).foregroundStyle(Cor.texto2).lineLimit(2, reservesSpace: true)
                }.padding(14)
            }
            .frame(width: 220)
            .background(Cor.sup1, in: RoundedRectangle(cornerRadius: 22, style: .continuous))
            .clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))
            .overlay(RoundedRectangle(cornerRadius: 22, style: .continuous).stroke(Cor.borda, lineWidth: 1))
        }
        .buttonStyle(Pressionavel())
        .foregroundStyle(Cor.texto)
    }
}
