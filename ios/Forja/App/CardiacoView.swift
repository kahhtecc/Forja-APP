import SwiftUI

/// Conectar cinta cardíaca ou relógio que transmite FC por Bluetooth.
struct CardiacoView: View {
    @EnvironmentObject var app: AppEstado
    @ObservedObject private var monitor = MonitorCardiaco.shared

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 0) {
                Cartao {
                    HStack(spacing: 14) {
                        IconeRedondo(icone: "heart.fill", cor: Cor.perigo, tamanho: 52)
                        VStack(alignment: .leading, spacing: 2) {
                            Rotulo(monitor.conectadoA ?? monitor.lembrado ?? "Nenhum monitor", monitor.conectadoA != nil ? Cor.ok : Cor.texto3)
                            HStack(alignment: .firstTextBaseline, spacing: 6) {
                                Text(monitor.bpm.map(String.init) ?? "--").font(Tipo.gigante).monospacedDigit()
                                Text("bpm").font(Tipo.corpoForte).foregroundStyle(Cor.texto2)
                            }
                            Text(monitor.estado).font(Tipo.pequeno).foregroundStyle(Cor.texto2)
                        }
                    }
                }
                BotaoPrimario(texto: monitor.escaneando ? "Procurando…" : "Procurar aparelhos", icone: "dot.radiowaves.left.and.right", ativo: !monitor.escaneando) {
                    monitor.escanear()
                }.padding(.top, 14)

                if !monitor.encontrados.isEmpty {
                    Secao(titulo: "Encontrados")
                    ForEach(monitor.encontrados) { d in
                        Button { Haptico.toque(); monitor.conectar(d.id) } label: {
                            HStack(spacing: 12) {
                                IconeRedondo(icone: "heart.circle.fill", cor: Cor.brasa, tamanho: 40)
                                VStack(alignment: .leading) {
                                    Text(d.nome).font(Tipo.corpoForte).foregroundStyle(Cor.texto)
                                    Text(sinal(d.rssi)).font(Tipo.pequeno).foregroundStyle(Cor.texto2)
                                }
                                Spacer()
                                Text(monitor.conectadoA == d.nome ? "Conectado" : "Conectar").font(Tipo.pequenoForte).foregroundStyle(monitor.conectadoA == d.nome ? Cor.ok : Cor.brasa)
                            }
                            .padding(14).background(Cor.sup1, in: RoundedRectangle(cornerRadius: 22, style: .continuous))
                            .overlay(RoundedRectangle(cornerRadius: 22, style: .continuous).stroke(Cor.borda, lineWidth: 1))
                        }.buttonStyle(Pressionavel()).padding(.vertical, 5)
                    }
                }

                if monitor.lembrado != nil {
                    BotaoSecundario(texto: "Esquecer este aparelho") { monitor.esquecer() }.padding(.top, 14)
                }

                Secao(titulo: "Como deixar o seu aparelho visível")
                Cartao(padding: 16) {
                    dica("Cintas (Polar H9/H10, Garmin HRM, Wahoo TICKR, Coospo…)", "Molhe os eletrodos e vista: ela liga sozinha.")
                    dica("Garmin", "No relógio: Configurações › Sensores e acessórios › Transmitir frequência cardíaca (ou segure o botão do meio › Transmitir FC).")
                    dica("Polar, Coros, Suunto, Amazfit", "Ative \"Compartilhar FC\" / \"Transmitir FC\" / \"HR Broadcast\" no relógio.")
                    dica("Apple Watch", "Não transmite FC por Bluetooth: use o app Saúde (Perfil › Conectar ao app Saúde) para ver a FC média e máxima no fim do treino, e a Live Activity para acompanhar o treino no pulso.")
                }
                Text("O Forja lembra o aparelho e reconecta sozinho quando ele estiver por perto. A FC aparece ao vivo no treino e no resumo ao concluir.")
                    .font(Tipo.pequeno).foregroundStyle(Cor.texto3).padding(.top, 12)
            }
            .padding(.horizontal, 20).padding(.vertical, 10)
        }
        .telaForja()
        .navigationTitle("Monitor cardíaco")
        .navigationBarTitleDisplayMode(.large)
        .onAppear { if app.demo { monitor.preencherDemo() } else { monitor.ligar() } }
        .onDisappear { monitor.pararEscaneamento() }
    }

    func sinal(_ rssi: Int) -> String { rssi > -60 ? "Sinal forte · bem perto" : (rssi > -80 ? "Sinal bom" : "Sinal fraco · aproxime o aparelho") }

    func dica(_ t: String, _ d: String) -> some View {
        VStack(alignment: .leading, spacing: 3) {
            Text(t).font(Tipo.pequenoForte)
            Text(d).font(Tipo.pequeno).foregroundStyle(Cor.texto2)
        }.padding(.vertical, 5)
    }
}
