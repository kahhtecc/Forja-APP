import SwiftUI
import ForjaCore

struct PerfilView: View {
    @EnvironmentObject var app: AppEstado
    @Environment(\.dismiss) private var dismiss
    let refazer: () -> Void
    let abrir: (Rota) -> Void
    @State private var confirmarApagar = false
    @State private var confirmarRecomecar = false
    @State private var lembrete = UserDefaults.standard.bool(forKey: "lembrete.on")
    @State private var hora = UserDefaults.standard.object(forKey: "lembrete.hora") as? Int ?? 18
    @AppStorage(AoVivo.chave) private var aoVivo = true
    @ObservedObject private var saude = Saude.shared
    @ObservedObject private var monitor = MonitorCardiaco.shared

    var body: some View {
        let p = app.e.perfil
        let cor = app.corModalidade
        ScrollView {
            VStack(alignment: .leading, spacing: 0) {
                Cartao {
                    HStack(spacing: 14) {
                        Text(String((p?.nome.isEmpty == false ? p!.nome : "F").prefix(1)).uppercased()).font(Tipo.titulo2).foregroundStyle(.white)
                            .frame(width: 58, height: 58).background(Cor.gradBrasa, in: Circle())
                        VStack(alignment: .leading) {
                            Text(p?.nome.isEmpty == false ? p!.nome : "Atleta Forja").font(Tipo.titulo2)
                            if let p { Text("\(p.idade) anos · \(p.alturaCm) cm · \(p.pesoKg) kg · IMC \(String(format: "%.1f", p.imc).replacingOccurrences(of: ".", with: ","))").font(Tipo.pequeno).foregroundStyle(Cor.texto2) }
                        }
                    }
                    if let p {
                        ScrollView(.horizontal, showsIndicators: false) {
                            HStack(spacing: 8) {
                                Etiqueta(texto: p.modalidade.curto, cor: cor, icone: p.modalidade.simbolo)
                                Etiqueta(texto: p.objetivo.nome, cor: Cor.texto2)
                                Etiqueta(texto: p.nivel.nome, cor: Cor.texto2)
                                Etiqueta(texto: "\(p.dias.count)x · \(p.dias.map { DIAS[$0 - 1] }.joined(separator: " "))", cor: Cor.texto2)
                                Etiqueta(texto: "\(p.minutos) min", cor: Cor.texto2)
                            }
                        }.padding(.top, 14)
                    }
                }
                Secao(titulo: "Plano")
                linha("square.and.pencil", "Refazer questionário", "Mude modalidade, objetivo, dias ou limitações") { refazer() }
                linha("arrow.counterclockwise", "Recomeçar da semana 1", "Mantém o histórico de treinos") { confirmarRecomecar = true }

                Secao(titulo: "Treino ao vivo")
                Cartao(padding: 16) {
                    Toggle("Sons do cronômetro", isOn: Binding(get: { app.e.ajustes.som }, set: { var a = app.e.ajustes; a.som = $0; app.loja.salvarAjustes(a) }))
                    Toggle("Vibração", isOn: Binding(get: { app.e.ajustes.vibracao }, set: { var a = app.e.ajustes; a.vibracao = $0; app.loja.salvarAjustes(a) })).padding(.top, 8)
                    Toggle("Manter a tela ligada", isOn: Binding(get: { app.e.ajustes.telaLigada }, set: { var a = app.e.ajustes; a.telaLigada = $0; app.loja.salvarAjustes(a) })).padding(.top, 8)
                }
                .font(Tipo.corpo).tint(Cor.brasa)

                Secao(titulo: "Relógio e saúde")
                Cartao(padding: 16) {
                    Toggle(isOn: $aoVivo) {
                        VStack(alignment: .leading) {
                            Text("Mostrar treino no relógio e na tela bloqueada").font(Tipo.corpoForte)
                            Text("Exercício, série e descanso na tela bloqueada, na Dynamic Island e no Apple Watch (watchOS 11+), com os botões Concluir série e Pular descanso. O relógio vibra no fim do descanso.").font(Tipo.pequeno).foregroundStyle(Cor.texto2)
                        }
                    }.tint(Cor.brasa)
                }
                linha("heart.text.square.fill", saude.conectado ? "Conectado ao app Saúde" : "Conectar ao app Saúde",
                      saude.conectado ? "Treinos gravados no Saúde e FC média/máxima do seu relógio no resumo" : "Grava os treinos e lê a FC do Apple Watch, Garmin, Polar, Withings, Oura e outros que sincronizam com o Saúde",
                      cor: saude.conectado ? Cor.ok : Cor.perigo) {
                    if saude.conectado { UIApplication.shared.open(URL(string: "x-apple-health://")!) } else { Task { await saude.conectar() } }
                }
                linha("dot.radiowaves.left.and.right", monitor.lembrado.map { "Monitor: \($0)" } ?? "Conectar cinta ou relógio por Bluetooth",
                      monitor.lembrado == nil ? "Cinta cardíaca ou relógio em modo transmitir FC: batimentos ao vivo no treino" : (monitor.bpm.map { "\($0) bpm agora · toque para gerenciar" } ?? "Reconecta sozinho quando estiver por perto")) {
                    abrir(.cardiaco)
                }

                Secao(titulo: "Lembretes")
                Cartao(padding: 16) {
                    Toggle(isOn: Binding(get: { lembrete }, set: { lembrete = $0; app.configurarLembretes(ligado: $0, hora: hora) })) {
                        VStack(alignment: .leading) {
                            Text("Avisar nos dias de treino").font(Tipo.corpoForte)
                            Text("Notificação no horário escolhido").font(Tipo.pequeno).foregroundStyle(Cor.texto2)
                        }
                    }.tint(Cor.brasa)
                    if lembrete {
                        ScrollView(.horizontal, showsIndicators: false) {
                            HStack(spacing: 8) { ForEach([6, 7, 8, 12, 17, 18, 19, 20], id: \.self) { h in Chip(texto: "\(h)h", sel: h == hora) { hora = h; app.configurarLembretes(ligado: true, hora: h) } } }
                        }.padding(.top, 12)
                    }
                }

                Secao(titulo: "Sobre")
                linha("flask.fill", "Base científica", "Diretrizes e \(app.fontes.count) referências usadas nas rotinas") { abrir(.fontes) }
                linha("lock.shield.fill", "Política de privacidade", "Nada sai do seu aparelho: sem cadastro, anúncios ou rastreamento") {
                    UIApplication.shared.open(URL(string: "https://kaiqueguimacuper-bit.github.io/teste-3/privacidade.html")!)
                }
                Cartao {
                    Text("Forja 1.0 para iOS").font(Tipo.corpoForte)
                    Text("Animações 3D feitas com o MakeHuman (CC0) e o Blender. Fotos: free-exercise-db (domínio público). Fontes Big Shoulders e Manrope (SIL OFL). Vídeos dos respectivos canais no YouTube.").font(Tipo.pequeno).foregroundStyle(Cor.texto2).padding(.top, 6)
                    Text("O Forja orienta com base em diretrizes reconhecidas, mas não substitui avaliação médica nem acompanhamento de um profissional de educação física.").font(Tipo.pequeno).foregroundStyle(Cor.texto3).padding(.top, 8)
                    if app.demo { Etiqueta(texto: "Modo demonstração", cor: Cor.alerta).padding(.top, 8) }
                }.padding(.top, 4)
                linha("trash.fill", "Apagar todos os dados", "Respostas, plano e histórico", cor: Cor.perigo) { confirmarApagar = true }.padding(.top, 14)
            }
            .padding(.horizontal, 20).padding(.vertical, 10)
        }
        .telaForja()
        .navigationTitle("Perfil")
        .navigationBarTitleDisplayMode(.large)
        .confirmationDialog("Apagar tudo?", isPresented: $confirmarApagar, titleVisibility: .visible) {
            Button("Apagar", role: .destructive) { app.loja.apagarTudo(); app.configurarLembretes(ligado: false, hora: hora) }
        } message: { Text("Remove suas respostas, o plano e todo o histórico deste aparelho. Não dá para desfazer.") }
        .confirmationDialog("Recomeçar o plano?", isPresented: $confirmarRecomecar, titleVisibility: .visible) {
            Button("Recomeçar") { app.loja.recomecarPlano() }
        } message: { Text("A semana atual passa a ser a semana 1. Seus treinos continuam no histórico.") }
    }

    func linha(_ icone: String, _ titulo: String, _ sub: String, cor: Color = Cor.brasa, acao: @escaping () -> Void) -> some View {
        Button { Haptico.toque(); acao() } label: {
            HStack(spacing: 12) {
                IconeRedondo(icone: icone, cor: cor, tamanho: 40)
                VStack(alignment: .leading) {
                    Text(titulo).font(Tipo.corpoForte).foregroundStyle(cor == Cor.perigo ? Cor.perigo : Cor.texto)
                    Text(sub).font(Tipo.pequeno).foregroundStyle(Cor.texto2)
                }
                Spacer()
                Image(systemName: "chevron.right").foregroundStyle(Cor.texto3)
            }
            .padding(14).background(Cor.sup1, in: RoundedRectangle(cornerRadius: 22, style: .continuous))
            .overlay(RoundedRectangle(cornerRadius: 22, style: .continuous).stroke(Cor.borda, lineWidth: 1))
        }.buttonStyle(Pressionavel()).padding(.vertical, 5)
    }
}

struct FontesView: View {
    @EnvironmentObject var app: AppEstado
    static let principios: [(String, String)] = [
        ("Musculação", "Hipertrofia: ~6–12 repetições (faixas mais amplas também funcionam) perto da falha (RIR 0–3), 10+ séries semanais por grupo muscular e cada grupo 2x por semana. Força: cargas altas, 3–6 repetições e descansos de 2–5 min. Progressão por dupla progressão e semana leve a cada 4–6 semanas."),
        ("Saúde e emagrecimento", "OMS 2020: 150–300 min de atividade moderada (ou 75–150 vigorosa) por semana e força pelo menos 2 dias. No déficit calórico, a musculação preserva a massa magra."),
        ("Corrida", "Cerca de 80% do volume em intensidade leve (Seiler). Longão progressivo, semanas de recuperação a cada 3–4 e polimento antes da prova. Iniciantes alternam caminhada e corrida."),
        ("Ciclismo", "Zonas por % do FTP (Coggan): Z2 56–75%, sweet spot 88–94%, limiar 91–105%, VO2máx 106–120%. FTP ≈ 95% da potência média de 20 min."),
        ("Lutas e atletas", "Força máxima e potência longe dos treinos técnicos pesados, condicionamento no formato dos rounds, pliometria com volume controlado e prevenção (ex.: flexão nórdica, FIFA 11+)."),
        ("Mobilidade", "Antes do treino, mobilidade dinâmica (estático curto, até ~60 s por grupo). Depois, alongamento estático de 10–30 s, 2–4 vezes, pelo menos 2–3 dias por semana."),
        ("Segurança", "Triagem PAR-Q+, adaptação conservadora para joelho, lombar e ombro, e liberação médica na gestação. Pare se sentir dor no peito, tontura ou falta de ar desproporcional."),
    ]
    var body: some View {
        List {
            Section {
                ForEach(Self.principios, id: \.0) { t, d in
                    VStack(alignment: .leading, spacing: 6) { Rotulo(t, Cor.brasa); Text(d).font(Tipo.corpo) }.padding(.vertical, 6)
                }
            }
            Section("Referências (\(app.fontes.count))") {
                ForEach(app.fontes) { f in
                    if let u = URL(string: f.url) {
                        Link(destination: u) {
                            HStack(alignment: .top) {
                                Text("\(f.ano)").font(Tipo.pequenoForte).foregroundStyle(Cor.brasa).frame(width: 44, alignment: .leading)
                                Text(f.titulo).font(Tipo.pequeno).foregroundStyle(Cor.texto2).multilineTextAlignment(.leading)
                            }
                        }
                    }
                }
            }
        }
        .scrollContentBackground(.hidden)
        .background(Cor.fundo.ignoresSafeArea())
        .navigationTitle("Base científica")
    }
}
