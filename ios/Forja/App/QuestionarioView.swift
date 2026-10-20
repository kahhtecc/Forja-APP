import SwiftUI
import ForjaCore

func iconeModalidade(_ m: Modalidade?) -> String {
    switch m {
    case .academia: return "dumbbell.fill"
    case .casaCorpo: return "figure.strengthtraining.functional"
    case .casaElastico: return "figure.flexibility"
    case .corrida: return "figure.run"
    case .bike: return "figure.outdoor.cycle"
    case .luta: return "figure.boxing"
    case .atleta: return "figure.track.and.field"
    case .hiit: return "flame.fill"
    case .hibrido: return "figure.cross.training"
    case .mobilidade: return "figure.mind.and.body"
    case .longevidade: return "figure.walk"
    case nil: return "bolt.fill"
    }
}

/// Questionário em etapas: uma pergunta por tela, mesma lógica do Android (Questionario do núcleo).
struct QuestionarioView: View {
    let podeFechar: Bool
    let fechar: () -> Void
    @EnvironmentObject var app: AppEstado
    @State private var resp: Respostas = [:]
    @State private var etapa = -1
    @State private var gerando = false
    @State private var iniciou = false

    var body: some View {
        ZStack {
            Cor.fundo.ignoresSafeArea()
            if gerando {
                GerandoView(resp: resp) {
                    app.loja.salvarRespostas(resp)
                    fechar()
                }
            } else if etapa < 0 {
                BoasVindasView(comecar: { withAnimation { etapa = 0 } }, cancelar: podeFechar ? fechar : nil)
            } else {
                perguntas
            }
        }
        .foregroundStyle(Cor.texto)
        .onAppear {
            guard !iniciou else { return }
            iniciou = true
            resp = app.e.respostas
            etapa = resp.isEmpty ? -1 : 0
        }
    }

    private var visiveis: [Pergunta] { Questionario.visiveis(resp) }
    private var idx: Int { max(0, min(etapa, visiveis.count - 1)) }

    private func avancar() {
        if idx >= visiveis.count - 1 { withAnimation { gerando = true } } else { withAnimation(.easeOut(duration: 0.25)) { etapa = idx + 1 } }
    }
    private func voltar() {
        if idx == 0 { if podeFechar { fechar() } else { withAnimation { etapa = -1 } } } else { withAnimation(.easeOut(duration: 0.25)) { etapa = idx - 1 } }
    }

    /// Valor padrão para perguntas numéricas obrigatórias e dias sugeridos (o usuário vê e ajusta).
    private func preparar(_ p: Pergunta) {
        if p.tipo == .NUMERO && !p.opcional && (resp[p.id] ?? []).isEmpty { resp[p.id] = ["\(p.padrao ?? p.min)"] }
        if p.tipo == .DIAS {
            let n = resp.num("dias") ?? 3
            if (resp[p.id] ?? []).count != n { resp[p.id] = Questionario.diasSugeridos(n).map { "\($0)" } }
        }
    }

    private var perguntas: some View {
        let lista = visiveis
        let p = lista[idx]
        return VStack(spacing: 0) {
            HStack(spacing: 16) {
                BotaoIcone(icone: "chevron.left", descricao: "Voltar") { voltar() }
                VStack(alignment: .leading, spacing: 8) {
                    HStack {
                        Rotulo(p.secao, Cor.brasa)
                        Spacer()
                        Rotulo("\(idx + 1) / \(lista.count)")
                    }
                    BarraProgresso(progresso: Double(idx + 1) / Double(lista.count), altura: 5)
                        .animation(.easeOut(duration: 0.4), value: idx)
                }
            }
            .padding(.horizontal, 20).padding(.vertical, 12)

            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    Text(p.titulo).font(Tipo.titulo1).foregroundStyle(Cor.texto).fixedSize(horizontal: false, vertical: true)
                    if let s = p.subtitulo {
                        Text(s).font(Tipo.corpo).foregroundStyle(Cor.texto2).padding(.top, 10)
                    }
                    CorpoPergunta(p: p, resp: $resp, escolhaUnica: {
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.26) { avancar() }
                    })
                    .padding(.top, 24)
                }
                .padding(.horizontal, 22).padding(.vertical, 18)
                .frame(maxWidth: .infinity, alignment: .leading)
            }
            .id(p.id)
            .transition(.asymmetric(insertion: .move(edge: .trailing).combined(with: .opacity), removal: .opacity))
            .scrollDismissesKeyboard(.interactively)

            let pular = p.opcional && (resp[p.id] ?? []).isEmpty
            BotaoPrimario(texto: idx == lista.count - 1 ? "Montar minha rotina" : (pular ? "Pular" : "Continuar"),
                          icone: "arrow.right", ativo: p.respondida(resp)) { avancar() }
                .padding(.horizontal, 22).padding(.vertical, 12)
        }
        .onAppear { preparar(p) }
        .onChange(of: p.id) { _ in preparar(visiveis[idx]) }
    }
}

private struct CorpoPergunta: View {
    let p: Pergunta
    @Binding var resp: Respostas
    let escolhaUnica: () -> Void

    private var atual: [String] { resp[p.id] ?? [] }

    var body: some View {
        switch p.tipo {
        case .UNICA:
            if p.id == "minutos" {
                LazyVGrid(columns: [GridItem(.adaptive(minimum: 96), spacing: 10)], spacing: 10) {
                    ForEach(p.opcoes, id: \.valor) { o in
                        Pilula(texto: o.titulo, sel: atual.contains(o.valor)) { resp[p.id] = [o.valor]; escolhaUnica() }
                    }
                }
            } else {
                VStack(spacing: 10) {
                    ForEach(p.opcoes, id: \.valor) { o in
                        let m = p.id == "modalidade" ? Modalidade.de(o.valor) : nil
                        CartaoOpcao(titulo: o.titulo, descricao: o.descricao, selecionado: atual.contains(o.valor), multipla: false,
                                    cor: m.map { Cor.modalidade($0) } ?? Cor.brasa, icone: m.map { iconeModalidade($0) }) {
                            resp[p.id] = [o.valor]; escolhaUnica()
                        }
                    }
                }
            }
        case .MULTIPLA:
            VStack(spacing: 10) {
                if p.id == "parq" {
                    Aviso(texto: "Qualquer “sim” não impede o treino, mas pede conversa com um médico antes de aumentar a intensidade.")
                }
                ForEach(p.opcoes, id: \.valor) { o in
                    let marcado = atual.contains(o.valor)
                    CartaoOpcao(titulo: o.titulo, descricao: o.descricao, selecionado: marcado, multipla: true) {
                        if marcado { resp[p.id] = atual.filter { $0 != o.valor } }
                        else if o.valor == p.exclusiva { resp[p.id] = [o.valor] }
                        else { resp[p.id] = atual.filter { $0 != p.exclusiva } + [o.valor] }
                    }
                }
            }
        case .NUMERO:
            SeletorNumero(p: p, valor: resp.num(p.id)) { v in
                resp[p.id] = v.map { ["\($0)"] } ?? []
                if p.id == "dias", let v { resp["dias_semana"] = Questionario.diasSugeridos(v).map { "\($0)" } }
            }
        case .DIAS:
            let n = resp.num("dias") ?? 3
            VStack(alignment: .leading, spacing: 0) {
                HStack {
                    ForEach(Array(Questionario.DIAS_NOMES.enumerated()), id: \.offset) { i, nome in
                        let v = "\(i + 1)"
                        let sel = atual.contains(v)
                        Button {
                            Haptico.toque()
                            var novo = atual
                            if sel { novo.removeAll { $0 == v } } else if novo.count < n { novo.append(v) } else { novo = Array(novo.dropFirst()) + [v] }
                            resp[p.id] = novo.sorted { Int($0)! < Int($1)! }
                        } label: {
                            Text(String(nome.prefix(3))).font(Tipo.pequenoForte)
                                .foregroundStyle(sel ? .white : Cor.texto2)
                                .frame(width: 44, height: 44)
                                .background(sel ? Cor.brasa : Cor.sup2, in: Circle())
                                .overlay(Circle().stroke(sel ? Cor.brasa : Cor.borda, lineWidth: 1))
                        }
                        .buttonStyle(.plain)
                        .accessibilityLabel(nome + (sel ? ", selecionado" : ""))
                        if i < 6 { Spacer(minLength: 0) }
                    }
                }
                Text("\(atual.count) de \(n) dias escolhidos").font(Tipo.corpoForte)
                    .foregroundStyle(atual.count == n ? Cor.ok : Cor.texto2).padding(.top, 16)
                Text("Dica: deixe pelo menos um dia de descanso entre treinos pesados do mesmo grupo.")
                    .font(Tipo.pequeno).foregroundStyle(Cor.texto3).padding(.top, 8)
            }
        case .TEXTO:
            TextField("", text: Binding(get: { resp.um(p.id) ?? "" }, set: { resp[p.id] = [String($0.prefix(24))] }),
                      prompt: Text("Seu nome").foregroundColor(Cor.texto3))
                .font(Tipo.titulo2).foregroundStyle(Cor.texto).tint(Cor.brasa)
                .textInputAutocapitalization(.words).submitLabel(.done)
                .padding(20)
                .background(Cor.sup1, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
                .overlay(RoundedRectangle(cornerRadius: 18, style: .continuous).stroke(Cor.borda, lineWidth: 1))
        }
    }
}

private struct Pilula: View {
    let texto: String
    let sel: Bool
    let acao: () -> Void
    var body: some View {
        Button { Haptico.toque(); acao() } label: {
            Text(texto).font(Tipo.titulo3).foregroundStyle(sel ? Cor.texto : Cor.texto2)
                .frame(maxWidth: .infinity, minHeight: 56)
                .background(sel ? Cor.brasa.opacity(0.16) : Cor.sup1, in: RoundedRectangle(cornerRadius: 16, style: .continuous))
                .overlay(RoundedRectangle(cornerRadius: 16, style: .continuous).stroke(sel ? Cor.brasa : Cor.borda, lineWidth: 1.5))
        }.buttonStyle(Pressionavel())
    }
}

struct CartaoOpcao: View {
    let titulo: String
    let descricao: String?
    let selecionado: Bool
    let multipla: Bool
    var cor: Color = Cor.brasa
    var icone: String? = nil
    let acao: () -> Void
    var body: some View {
        Button { Haptico.toque(); acao() } label: {
            HStack(spacing: 14) {
                if let i = icone { IconeRedondo(icone: i, cor: cor, tamanho: 42) }
                VStack(alignment: .leading, spacing: 2) {
                    Text(titulo).font(Tipo.corpoForte).foregroundStyle(Cor.texto)
                    if let d = descricao { Text(d).font(Tipo.pequeno).foregroundStyle(Cor.texto2) }
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .multilineTextAlignment(.leading)
                ZStack {
                    if multipla {
                        RoundedRectangle(cornerRadius: 7).fill(selecionado ? cor : .clear)
                        RoundedRectangle(cornerRadius: 7).stroke(selecionado ? cor : Cor.texto3, lineWidth: 1.5)
                    } else {
                        Circle().fill(selecionado ? cor : .clear)
                        Circle().stroke(selecionado ? cor : Cor.texto3, lineWidth: 1.5)
                    }
                    if selecionado { Image(systemName: "checkmark").font(.system(size: 12, weight: .heavy)).foregroundStyle(Cor.fundo) }
                }
                .frame(width: 24, height: 24)
            }
            .padding(.horizontal, 16).padding(.vertical, 14)
            .background(selecionado ? cor.opacity(0.12) : Cor.sup1, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
            .overlay(RoundedRectangle(cornerRadius: 18, style: .continuous).stroke(selecionado ? cor : Cor.borda, lineWidth: 1.5))
        }
        .buttonStyle(Pressionavel())
        .accessibilityLabel(titulo + (selecionado ? ", selecionado" : ""))
    }
}

private struct SeletorNumero: View {
    let p: Pergunta
    let valor: Int?
    let mudar: (Int?) -> Void
    var body: some View {
        let v = valor ?? p.padrao ?? p.min
        let vazio = valor == nil && p.opcional
        VStack(spacing: 0) {
            HStack(spacing: 22) {
                BotaoIcone(icone: "minus", descricao: "Diminuir", tamanho: 58) { mudar(max(p.min, v - p.passo)) }
                VStack(spacing: 0) {
                    Text(vazio ? "—" : "\(v)").font(Tipo.display(88)).foregroundStyle(vazio ? Cor.texto3 : Cor.texto)
                        .monospacedDigit().contentTransition(.numericText())
                    Rotulo(p.unidade, Cor.brasa)
                }
                .frame(width: 150)
                BotaoIcone(icone: "plus", descricao: "Aumentar", tamanho: 58) { mudar(min(p.max, v + p.passo)) }
            }
            Slider(value: Binding(get: { Double(v) }, set: { mudar(min(p.max, max(p.min, Int(($0 / Double(p.passo)).rounded()) * p.passo))) }),
                   in: Double(p.min)...Double(p.max))
                .tint(Cor.brasa).padding(.top, 24)
            if p.id == "dias" {
                Text(dica(v)).font(Tipo.corpo).foregroundStyle(Cor.texto2).multilineTextAlignment(.center).padding(.top, 12)
            }
            if p.opcional && valor != nil {
                Button("Limpar") { mudar(nil) }.font(Tipo.pequenoForte).foregroundStyle(Cor.texto2).padding(.top, 12)
            }
        }
        .frame(maxWidth: .infinity)
        .animation(.easeOut(duration: 0.2), value: v)
    }

    private func dica(_ v: Int) -> String {
        switch v {
        case 2: return "Ótimo para começar e manter."
        case 3: return "O ponto ideal para a maioria."
        case 4: return "Permite dividir em superiores e inferiores."
        case 5: return "Volume alto — durma bem."
        default: return "Para quem já tem rotina consolidada."
        }
    }
}

private struct BoasVindasView: View {
    let comecar: () -> Void
    let cancelar: (() -> Void)?
    var body: some View {
        ZStack(alignment: .bottomLeading) {
            VStack {
                HStack(spacing: 8) {
                    FotoAsset(nome: "agachamento-barra_1").frame(maxWidth: .infinity).aspectRatio(0.72, contentMode: .fit)
                        .clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))
                    VStack(spacing: 8) {
                        FotoAsset(nome: "swing_1").aspectRatio(0.95, contentMode: .fit).clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))
                        FotoAsset(nome: "corrida-leve_1").aspectRatio(1.05, contentMode: .fit).clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))
                    }
                    .frame(maxWidth: .infinity)
                }
                .padding(.horizontal, 12).padding(.top, 8)
                Spacer()
            }
            LinearGradient(stops: [.init(color: .clear, location: 0.25), .init(color: Cor.fundo, location: 0.58)], startPoint: .top, endPoint: .bottom)
                .ignoresSafeArea()
            VStack(alignment: .leading, spacing: 0) {
                LinhaBrasa(largura: 56)
                Text("FORJA").font(Tipo.display(84)).tracking(2).padding(.top, 14)
                Text("Treino sob medida.").font(Tipo.titulo2).foregroundStyle(Cor.brasa)
                Text("Responda algumas perguntas e receba uma rotina completa — musculação, casa, corrida, bike, lutas, atletas, mobilidade e mais — com demonstração de cada exercício.")
                    .font(Tipo.corpo).foregroundStyle(Cor.texto2).padding(.top, 14)
                BotaoPrimario(texto: "Montar minha rotina", icone: "arrow.right", acao: comecar).padding(.top, 24)
                if let c = cancelar { BotaoSecundario(texto: "Cancelar", acao: c).padding(.top, 10) }
                Text("Leva cerca de 2 minutos · baseado em diretrizes do ACSM, OMS e NSCA")
                    .font(Tipo.pequeno).foregroundStyle(Cor.texto3).frame(maxWidth: .infinity).multilineTextAlignment(.center).padding(.top, 8)
            }
            .padding(24)
        }
    }
}

private struct GerandoView: View {
    let resp: Respostas
    let pronto: () -> Void
    @EnvironmentObject var app: AppEstado
    @State private var feito = 0
    @State private var plano: Plano?
    private let passos = ["Analisando seu perfil", "Aplicando a triagem de segurança", "Escolhendo os exercícios", "Ajustando volume e intensidade", "Organizando as semanas"]

    var body: some View {
        let cor = Cor.modalidade(plano?.modalidade)
        ScrollView {
            VStack(alignment: .leading, spacing: 0) {
                Anel(progresso: Double(feito) / Double(passos.count), cor: cor) {
                    Image(systemName: iconeModalidade(plano?.modalidade)).font(.system(size: 36, weight: .bold)).foregroundStyle(cor)
                }
                .frame(width: 96, height: 96).padding(.top, 30)
                Text(feito < passos.count ? "Forjando sua rotina…" : "Sua rotina está pronta").font(Tipo.titulo1).padding(.top, 26)
                VStack(alignment: .leading, spacing: 12) {
                    ForEach(Array(passos.enumerated()), id: \.offset) { i, s in
                        HStack(spacing: 12) {
                            ZStack {
                                Circle().fill(i < feito ? Cor.ok : Cor.sup3)
                                if i < feito { Image(systemName: "checkmark").font(.system(size: 11, weight: .heavy)).foregroundStyle(Cor.fundo) }
                            }.frame(width: 22, height: 22)
                            Text(s).font(Tipo.corpo).foregroundStyle(i < feito ? Cor.texto : Cor.texto3)
                        }
                    }
                }
                .padding(.top, 18)
                if feito >= passos.count, let plano {
                    Cartao {
                        Etiqueta(texto: plano.modalidade.nome, cor: cor, icone: iconeModalidade(plano.modalidade))
                        Text(plano.nome).font(Tipo.titulo2).padding(.top, 12)
                        Text(plano.resumo).font(Tipo.pequeno).foregroundStyle(Cor.texto2).padding(.top, 6)
                        Text(plano.metaSemanal).font(Tipo.pequenoForte).foregroundStyle(cor).padding(.top, 12)
                    }
                    .padding(.top, 22)
                    ForEach(plano.alertas, id: \.self) { Aviso(texto: $0).padding(.top, 10) }
                    BotaoPrimario(texto: "Ver meu plano", icone: "arrow.right", acao: pronto).padding(.top, 24)
                }
            }
            .padding(24)
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .task {
            plano = Gerador(app.catalogo).gerar(Perfil.de(resp))
            for i in passos.indices {
                try? await Task.sleep(nanoseconds: 430_000_000)
                withAnimation { feito = i + 1 }
            }
            Haptico.sucesso()
        }
    }
}
