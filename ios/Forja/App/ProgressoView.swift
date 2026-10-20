import SwiftUI
import Charts
import ForjaCore

struct ProgressoView: View {
    @EnvironmentObject var app: AppEstado
    @State private var apagar: Registro?
    @State private var novoPeso: Double?

    var body: some View {
        let regs = app.e.registros
        let corM = app.corModalidade
        let semanas = Progresso.minutosPorSemana(regs, app.loja.hoje())
        let total = regs.reduce(0.0) { $0 + Progresso.volumeKg($1) }
        ScrollView {
            VStack(alignment: .leading, spacing: 0) {
                Rotulo("Sua evolução", corM)
                Text("Progresso").font(Tipo.titulo1)
                HStack(spacing: 10) {
                    Cartao(padding: 14) { Estatistica(valor: "\(regs.count)", rotulo: "treinos") }
                    Cartao(padding: 14) { Estatistica(valor: "\(regs.reduce(0) { $0 + $1.duracaoSeg } / 3600)h", rotulo: "treinando") }
                    Cartao(padding: 14) { Estatistica(valor: total >= 1000 ? String(format: "%.1ft", total / 1000).replacingOccurrences(of: ".", with: ",") : Progresso.fmtKg(total), rotulo: "volume total") }
                }.padding(.top, 12)

                Secao(titulo: "Minutos por semana")
                Cartao {
                    Chart {
                        ForEach(Array(semanas.enumerated()), id: \.offset) { k, s in
                            BarMark(x: .value("Semana", Self.curta.string(from: Datas.data(s.0))), y: .value("Minutos", s.1))
                                .foregroundStyle(k == semanas.count - 1 ? Cor.gradBrasa : LinearGradient(colors: [corM.opacity(0.55), corM.opacity(0.3)], startPoint: .top, endPoint: .bottom))
                                .cornerRadius(8)
                                .annotation(position: .top) { Text("\(s.1)").font(Tipo.texto(11, "Bold")).foregroundStyle(Cor.texto2) }
                        }
                        RuleMark(y: .value("Meta OMS", 150)).lineStyle(StrokeStyle(lineWidth: 1, dash: [6, 6])).foregroundStyle(Cor.texto3)
                    }
                    .chartYAxis(.hidden)
                    .chartXAxis { AxisMarks { _ in AxisValueLabel().font(Tipo.texto(11)).foregroundStyle(Cor.texto3) } }
                    .frame(height: 170)
                    Text("Linha tracejada: 150 min/semana, mínimo recomendado pela OMS.").font(Tipo.pequeno).foregroundStyle(Cor.texto3).padding(.top, 8)
                }

                if let plano = app.plano {
                    Secao(titulo: "Consistência no plano")
                    Cartao {
                        HStack(alignment: .bottom, spacing: 6) {
                            ForEach(plano.semanas, id: \.numero) { s in
                                let f = Progresso.feitas(regs, s.numero).count
                                VStack(spacing: 4) {
                                    VStack(spacing: 3) {
                                        ForEach(0..<s.sessoes.count, id: \.self) { k in
                                            RoundedRectangle(cornerRadius: 4).fill(s.sessoes.count - 1 - k < f ? corM : Cor.sup3)
                                        }
                                    }.frame(height: 70)
                                    Text("S\(s.numero)").font(Tipo.pequeno).foregroundStyle(Cor.texto3)
                                }.frame(maxWidth: .infinity)
                            }
                        }
                    }
                }

                pesoCorporal(corM)

                let rec = Array(Progresso.recordes(regs).prefix(8))
                if !rec.isEmpty {
                    Secao(titulo: "Recordes")
                    Cartao(padding: 16) {
                        ForEach(rec, id: \.exId) { r in
                            HStack {
                                Image(systemName: "trophy.fill").foregroundStyle(Cor.alerta)
                                Text(app.catalogo[r.exId]?.nome ?? r.exId).font(Tipo.pequenoForte).lineLimit(1)
                                Spacer()
                                Text("\(r.reps)×\(Progresso.fmtKg(r.kg)) kg").font(Tipo.pequenoForte).foregroundStyle(corM)
                            }.padding(.vertical, 8)
                        }
                    }
                }

                Secao(titulo: "Histórico")
                if regs.isEmpty {
                    VStack(spacing: 8) {
                        Image(systemName: "chart.bar.xaxis").font(.largeTitle).foregroundStyle(Cor.texto3)
                        Text("Nenhum treino ainda").font(Tipo.titulo3)
                        Text("Conclua seu primeiro treino para ver sua evolução aqui.").font(Tipo.pequeno).foregroundStyle(Cor.texto2).multilineTextAlignment(.center)
                    }.frame(maxWidth: .infinity).padding(.vertical, 30)
                }
                ForEach(regs.sorted { $0.epochDay > $1.epochDay }.prefix(60)) { r in
                    HStack(spacing: 12) {
                        Circle().fill(Cor.tipoSessao(r.tipo, corM)).frame(width: 10, height: 10)
                        VStack(alignment: .leading, spacing: 2) {
                            Text(r.titulo).font(Tipo.corpoForte).lineLimit(1)
                            Text("\(Self.media.string(from: Datas.data(r.epochDay))) · \(r.duracaoSeg / 60) min · esforço \(r.esforco)/10\(r.series.isEmpty ? "" : " · \(r.series.count) séries")").font(Tipo.pequeno).foregroundStyle(Cor.texto2).lineLimit(1)
                            if !r.nota.isEmpty { Text("“\(r.nota)”").font(Tipo.pequeno).foregroundStyle(Cor.texto3).lineLimit(2) }
                        }
                        Spacer()
                        Button { apagar = r } label: { Image(systemName: "trash").foregroundStyle(Cor.texto3) }.accessibilityLabel("Apagar registro")
                    }
                    .padding(14).background(Cor.sup1, in: RoundedRectangle(cornerRadius: 18, style: .continuous)).padding(.vertical, 5)
                }
            }
            .padding(.horizontal, 20).padding(.top, 10).padding(.bottom, ESPACO_BARRA)
        }
        .telaForja()
        .confirmationDialog("Apagar este treino?", isPresented: Binding(get: { apagar != nil }, set: { if !$0 { apagar = nil } }), titleVisibility: .visible) {
            Button("Apagar", role: .destructive) { if let r = apagar { app.loja.apagarRegistro(r) }; apagar = nil }
        } message: { Text(apagar?.titulo ?? "") }
    }

    @ViewBuilder func pesoCorporal(_ cor: Color) -> some View {
        let pesos = app.e.pesos
        let atual = pesos.last?.kg ?? Double(app.e.perfil?.pesoKg ?? 70)
        let valor = novoPeso ?? atual
        Secao(titulo: "Peso corporal")
        Cartao {
            HStack(spacing: 12) {
                IconeRedondo(icone: "scalemass.fill", cor: cor)
                VStack(alignment: .leading) {
                    Text("\(Progresso.fmtKg(atual)) kg").font(Tipo.titulo2)
                    if pesos.count >= 2 {
                        let dif = ((pesos.last!.kg - pesos.first!.kg) * 10).rounded() / 10
                        Text("\(dif > 0 ? "+" : "")\(Progresso.fmtKg(dif)) kg desde o primeiro registro").font(Tipo.pequeno).foregroundStyle(Cor.texto2)
                    } else { Text("Registre seu peso uma vez por semana, no mesmo horário.").font(Tipo.pequeno).foregroundStyle(Cor.texto2) }
                }
            }
            if pesos.count >= 2 {
                Chart(pesos, id: \.dia) { p in
                    LineMark(x: .value("Dia", Datas.data(p.dia)), y: .value("kg", p.kg)).foregroundStyle(cor).interpolationMethod(.catmullRom)
                    PointMark(x: .value("Dia", Datas.data(p.dia)), y: .value("kg", p.kg)).foregroundStyle(cor)
                }
                .chartYScale(domain: (pesos.map(\.kg).min()! - 0.5)...(pesos.map(\.kg).max()! + 0.5))
                .chartXAxis(.hidden)
                .chartYAxis { AxisMarks { _ in AxisValueLabel().foregroundStyle(Cor.texto3) } }
                .frame(height: 100).padding(.top, 12)
            }
            HStack {
                BotaoIcone(icone: "minus", descricao: "Diminuir peso", tamanho: 42) { novoPeso = ((valor - 0.1) * 10).rounded() / 10 }
                Text("\(Progresso.fmtKg(valor)) kg").font(Tipo.titulo3).frame(maxWidth: .infinity)
                BotaoIcone(icone: "plus", descricao: "Aumentar peso", tamanho: 42) { novoPeso = ((valor + 0.1) * 10).rounded() / 10 }
                BotaoSecundario(texto: "Registrar", cor: Cor.brasa) { app.loja.registrarPeso(valor); novoPeso = nil; Haptico.sucesso() }.frame(width: 120)
            }.padding(.top, 14)
        }
    }

    static let curta: DateFormatter = { let f = DateFormatter(); f.dateFormat = "d/M"; return f }()
    static let media: DateFormatter = { let f = DateFormatter(); f.locale = Locale(identifier: "pt_BR"); f.dateFormat = "EEE, d MMM"; return f }()
}
