import SwiftUI
import ForjaCore
import WebKit

let EQUIP_NOMES: [String: String] = [
    "corpo": "Peso do corpo", "elastico": "Elástico", "halter": "Halteres", "barra": "Barra", "maquina": "Máquina", "polia": "Polia",
    "kettlebell": "Kettlebell", "banco": "Banco", "barra_fixa": "Barra fixa", "bola": "Medicine ball", "corda": "Corda", "rolo": "Rolo",
    "saco": "Saco de pancada", "bike": "Bike", "esteira": "Esteira", "rua": "Rua", "pista": "Pista", "outro": "Outros",
]

// MARK: - Mobilidade

struct MobilidadeView: View {
    @EnvironmentObject var app: AppEstado
    let abrir: (Rota) -> Void
    @State private var filtro = "Todas"

    var body: some View {
        let lista = Rotinas.todas.filter { filtro == "Todas" || $0.categoria == filtro }
        ScrollView {
            VStack(alignment: .leading, spacing: 0) {
                Rotulo("Alongamento & mobilidade", Cor.modalidade(.mobilidade))
                Text("Prepare o corpo,\nrecupere melhor.").font(Tipo.titulo1)
                Text("Antes do esporte, movimento dinâmico. Depois do treino, alongamento estático de 20–30 s. E mobilidade para o dia a dia.").font(Tipo.corpo).foregroundStyle(Cor.texto2).padding(.top, 8)
                Secao(titulo: "Para o seu treino")
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 12) { ForEach(Rotinas.recomendadas(app.plano?.modalidade, app.e.perfil)) { r in CartaoRotinaPequeno(rotina: r) { abrir(.rotina(r.id)) } } }
                }
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) { ForEach(["Todas"] + Rotinas.CATEGORIAS, id: \.self) { c in Chip(texto: c, sel: c == filtro) { filtro = c } } }
                }.padding(.top, 22)
                ForEach(Rotinas.CATEGORIAS.filter { c in lista.contains { $0.categoria == c } }, id: \.self) { cat in
                    Secao(titulo: cat)
                    VStack(spacing: 10) {
                        ForEach(lista.filter { $0.categoria == cat }) { r in LinhaRotina(rotina: r) { abrir(.rotina(r.id)) } }
                    }
                }
            }
            .padding(.horizontal, 20).padding(.top, 10).padding(.bottom, ESPACO_BARRA)
        }
        .telaForja()
    }
}

struct LinhaRotina: View {
    @EnvironmentObject var app: AppEstado
    let rotina: Rotina
    let acao: () -> Void
    var body: some View {
        let cor = Cor.tema(rotina.tema)
        let itens = rotina.sessao.blocos[0].itens
        Button { Haptico.toque(); acao() } label: {
            HStack(spacing: 14) {
                if let ex = app.catalogo[(itens.count > 1 ? itens[1] : itens[0]).exId] { DemoExercicio(ex: ex, cor: cor, animar: false, cantos: 16).frame(width: 76, height: 76) }
                VStack(alignment: .leading, spacing: 3) {
                    HStack(spacing: 6) { Circle().fill(cor).frame(width: 8, height: 8); Rotulo("\(Roteiro.minutos(rotina.sessao, app.catalogo)) min · \(itens.count) movimentos", cor) }
                    Text(rotina.titulo).font(Tipo.corpoForte).lineLimit(1)
                    Text(rotina.subtitulo).font(Tipo.pequeno).foregroundStyle(Cor.texto2).lineLimit(2).multilineTextAlignment(.leading)
                }
                Spacer(minLength: 0)
                Image(systemName: "chevron.right").foregroundStyle(Cor.texto3)
            }
            .padding(12)
            .background(Cor.sup1, in: RoundedRectangle(cornerRadius: 22, style: .continuous))
            .overlay(RoundedRectangle(cornerRadius: 22, style: .continuous).stroke(Cor.borda, lineWidth: 1))
        }.buttonStyle(Pressionavel()).foregroundStyle(Cor.texto)
    }
}

// MARK: - Biblioteca

struct BibliotecaView: View {
    @EnvironmentObject var app: AppEstado
    let abrir: (Rota) -> Void
    @State private var busca = ""
    @State private var grupo = "Todos"
    @State private var semEquip = false

    var body: some View {
        let termo = busca.trimmingCharacters(in: .whitespaces).lowercased()
        let lista = app.catalogo.exercicios.filter { e in
            (grupo == "Todos" || e.grupo == grupo) && (!semEquip || e.equip.contains { $0 == "corpo" || $0 == "elastico" }) &&
                (termo.isEmpty || e.nome.lowercased().contains(termo) || e.grupo.lowercased().contains(termo) || e.equip.contains { (EQUIP_NOMES[$0] ?? $0).lowercased().contains(termo) })
        }
        ScrollView {
            VStack(alignment: .leading, spacing: 12) {
                Rotulo("\(app.catalogo.exercicios.count) exercícios com demonstração e vídeo", Cor.brasa)
                Text("Biblioteca").font(Tipo.titulo1)
                HStack {
                    Image(systemName: "magnifyingglass").foregroundStyle(Cor.texto3)
                    TextField("Buscar exercício, músculo ou equipamento", text: $busca).font(Tipo.corpo).textInputAutocapitalization(.never).autocorrectionDisabled()
                    if !busca.isEmpty { Button { busca = "" } label: { Image(systemName: "xmark.circle.fill").foregroundStyle(Cor.texto3) }.accessibilityLabel("Limpar busca") }
                }
                .padding(.horizontal, 16).padding(.vertical, 14)
                .background(Cor.sup1, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
                .overlay(RoundedRectangle(cornerRadius: 18, style: .continuous).stroke(Cor.borda, lineWidth: 1))
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        Chip(texto: "Sem equipamento", sel: semEquip) { semEquip.toggle() }
                        ForEach(["Todos"] + app.catalogo.grupos(), id: \.self) { g in Chip(texto: g, sel: g == grupo) { grupo = g } }
                    }
                }
                if lista.isEmpty {
                    VStack(spacing: 8) { Image(systemName: "magnifyingglass").font(.largeTitle).foregroundStyle(Cor.texto3); Text("Nada encontrado").font(Tipo.titulo3) }.frame(maxWidth: .infinity).padding(.vertical, 40)
                }
                LazyVGrid(columns: [GridItem(.flexible(), spacing: 12), GridItem(.flexible(), spacing: 12)], spacing: 12) {
                    ForEach(lista) { e in
                        Button { Haptico.toque(); abrir(.exercicio(e.id, trocaSessao: nil)) } label: {
                            VStack(alignment: .leading, spacing: 0) {
                                DemoExercicio(ex: e, animar: false, cantos: 0).aspectRatio(1.25, contentMode: .fit)
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(e.nome).font(Tipo.pequenoForte).lineLimit(2, reservesSpace: true).multilineTextAlignment(.leading)
                                    Text("\(e.grupo) · \(EQUIP_NOMES[e.equip.first ?? ""] ?? "")").font(Tipo.pequeno).foregroundStyle(Cor.texto3).lineLimit(1)
                                }.padding(12)
                            }
                            .background(Cor.sup1)
                            .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
                            .overlay(RoundedRectangle(cornerRadius: 20, style: .continuous).stroke(Cor.borda, lineWidth: 1))
                        }.buttonStyle(Pressionavel()).foregroundStyle(Cor.texto)
                    }
                }
            }
            .padding(.horizontal, 16).padding(.top, 10).padding(.bottom, ESPACO_BARRA)
        }
        .scrollDismissesKeyboard(.immediately)
        .telaForja()
    }
}

// MARK: - Exercício

struct ExercicioView: View {
    @EnvironmentObject var app: AppEstado
    let id: String
    let trocaSessao: Int?
    let abrir: (Rota) -> Void
    let voltar: () -> Void

    var body: some View {
        if let e = app.catalogo[id] {
            let origem = trocaSessao.flatMap { t in app.e.trocas.first { $0.key.hasPrefix("\(t)|") && $0.value == id }?.key.components(separatedBy: "|").last } ?? id
            let recorde = Progresso.recordes(app.e.registros).first { $0.exId == id }
            let ultimas = Progresso.ultimas(app.e.registros, id)
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    DemoExercicio(ex: e, cantos: 0).aspectRatio(1.1, contentMode: .fit)
                    VStack(alignment: .leading, spacing: 0) {
                        Rotulo(e.grupo, Cor.brasa).padding(.top, 16)
                        Text(e.nome).font(Tipo.titulo1)
                        ScrollView(.horizontal, showsIndicators: false) {
                            HStack(spacing: 8) {
                                ForEach(e.equip, id: \.self) { Etiqueta(texto: EQUIP_NOMES[$0] ?? $0, cor: Cor.texto2) }
                                Etiqueta(texto: ["", "Básico", "Intermediário", "Avançado"][min(max(e.nivel, 1), 3)], cor: Cor.texto2)
                            }
                        }.padding(.top, 12)
                        BotaoPrimario(texto: e.video != nil ? "Assistir vídeo demonstrativo" : "Buscar vídeo no YouTube", icone: "play.fill") { abrir(.video(e.id)) }.padding(.top, 18)
                        if let v = e.video {
                            Text(v.titulo + (v.canal.isEmpty || v.canal == "não identificado" ? "" : " · \(v.canal)") + (v.idioma == "en" ? " · em inglês" : ""))
                                .font(Tipo.pequeno).foregroundStyle(Cor.texto3).lineLimit(2).padding(.top, 6)
                        }
                        Secao(titulo: "Como executar")
                        ForEach(Array(e.dicas.enumerated()), id: \.offset) { k, d in
                            HStack(alignment: .top, spacing: 12) {
                                Text("\(k + 1)").font(Tipo.pequenoForte).foregroundStyle(Cor.brasa).frame(width: 28, height: 28).background(Cor.brasa.opacity(0.15), in: RoundedRectangle(cornerRadius: 9))
                                Text(d).font(Tipo.corpo).padding(.top, 3)
                            }.padding(.vertical, 6)
                        }
                        if recorde != nil || !ultimas.isEmpty {
                            Secao(titulo: "Seu histórico")
                            Cartao {
                                if let r = recorde {
                                    Label("Recorde: \(r.reps) × \(Progresso.fmtKg(r.kg)) kg · 1RM estimado \(Progresso.fmtKg((r.rm1 * 2).rounded() / 2)) kg", systemImage: "trophy.fill").font(Tipo.pequenoForte)
                                }
                                if !ultimas.isEmpty {
                                    Text("Última vez: " + ultimas.map { $0.kg > 0 ? "\($0.reps)×\(Progresso.fmtKg($0.kg))" : ($0.seg > 0 ? "\($0.seg)s" : "\($0.reps)") }.joined(separator: " · "))
                                        .font(Tipo.pequeno).foregroundStyle(Cor.texto2).padding(.top, 8)
                                }
                            }
                        }
                        if let t = trocaSessao, let perfil = app.e.perfil {
                            let atual = app.catalogo[origem] ?? e
                            let alts = app.catalogo.alternativas(atual, equip: perfil.equip, evitar: perfil.evitar).filter { $0.id != id }
                            Secao(titulo: "Trocar neste treino")
                            Text("Não tem o aparelho ou não se adaptou? Escolha uma alternativa com o mesmo padrão de movimento. A troca vale para este treino em todas as semanas.").font(Tipo.pequeno).foregroundStyle(Cor.texto2)
                            if origem != id {
                                BotaoSecundario(texto: "Voltar ao original: \(atual.nome)", icone: "arrow.uturn.backward") { app.loja.trocar(t, origem, nil); voltar() }.padding(.top, 10)
                            }
                            ForEach(alts.prefix(12)) { a in
                                Button { Haptico.toque(); app.loja.trocar(t, origem, a.id); voltar() } label: {
                                    HStack(spacing: 12) {
                                        DemoExercicio(ex: a, animar: false, cantos: 12).frame(width: 56, height: 56)
                                        VStack(alignment: .leading) {
                                            Text(a.nome).font(Tipo.corpoForte).lineLimit(2).multilineTextAlignment(.leading)
                                            Text(a.equip.map { EQUIP_NOMES[$0] ?? $0 }.joined(separator: " · ")).font(Tipo.pequeno).foregroundStyle(Cor.texto3).lineLimit(1)
                                        }
                                        Spacer()
                                        Image(systemName: "arrow.left.arrow.right").foregroundStyle(Cor.brasa)
                                    }
                                    .padding(10).background(Cor.sup1, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
                                }.buttonStyle(Pressionavel()).foregroundStyle(Cor.texto).padding(.top, 10)
                            }
                        }
                    }
                    .padding(.horizontal, 20).padding(.bottom, 40)
                }
            }
            .telaForja()
            .navigationBarTitleDisplayMode(.inline)
            .ignoresSafeArea(edges: .top)
        }
    }
}

// MARK: - Vídeo

struct VideoView: View {
    @EnvironmentObject var app: AppEstado
    @Environment(\.openURL) private var openURL
    let id: String
    var body: some View {
        if let e = app.catalogo[id] {
            let busca = URL(string: "https://www.youtube.com/results?search_query=" + (e.busca.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? ""))!
            ScrollView {
                VStack(alignment: .leading, spacing: 0) {
                    if let v = e.video {
                        YouTubeEmbed(videoId: v.id).aspectRatio(16 / 9, contentMode: .fit).clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
                        Text(v.titulo).font(Tipo.corpoForte).padding(.top, 14)
                        if !v.canal.isEmpty && v.canal != "não identificado" { Text(v.canal).font(Tipo.pequeno).foregroundStyle(Cor.texto2) }
                        if v.idioma == "en" { Text("Vídeo em inglês — ative as legendas automáticas em português.").font(Tipo.pequeno).foregroundStyle(Cor.texto3) }
                        BotaoSecundario(texto: "Abrir no YouTube", icone: "arrow.up.right.square") { openURL(URL(string: "https://www.youtube.com/watch?v=\(v.id)")!) }.padding(.top, 18)
                        BotaoSecundario(texto: "Ver outros vídeos", icone: "magnifyingglass") { openURL(busca) }.padding(.top, 10)
                        Text("O vídeo não carregou? Alguns canais bloqueiam a reprodução fora do YouTube — use “Abrir no YouTube”.").font(Tipo.pequeno).foregroundStyle(Cor.texto3).padding(.top, 14)
                    } else {
                        DemoExercicio(ex: e).aspectRatio(1.4, contentMode: .fit)
                        BotaoPrimario(texto: "Buscar no YouTube", icone: "magnifyingglass") { openURL(busca) }.padding(.top, 18)
                    }
                    Rotulo("Pontos-chave").padding(.top, 22)
                    ForEach(e.dicas, id: \.self) { d in
                        Label { Text(d).font(Tipo.pequeno).foregroundStyle(Cor.texto2) } icon: { Image(systemName: "checkmark").foregroundStyle(Cor.brasa) }.padding(.top, 6)
                    }
                }.padding(20)
            }
            .telaForja()
            .navigationTitle(e.nome)
            .navigationBarTitleDisplayMode(.inline)
        }
    }
}

struct YouTubeEmbed: UIViewRepresentable {
    let videoId: String
    func makeUIView(context: Context) -> WKWebView {
        let c = WKWebViewConfiguration()
        c.allowsInlineMediaPlayback = true
        c.mediaTypesRequiringUserActionForPlayback = []
        let w = WKWebView(frame: .zero, configuration: c)
        w.isOpaque = false; w.backgroundColor = UIColor(Cor.fundo); w.scrollView.isScrollEnabled = false
        let html = """
        <!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
        <style>html,body{margin:0;background:#0E0D0C;height:100%}iframe{position:absolute;inset:0;width:100%;height:100%;border:0}</style></head>
        <body><iframe src="https://www.youtube-nocookie.com/embed/\(videoId)?playsinline=1&rel=0&modestbranding=1" allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen referrerpolicy="strict-origin-when-cross-origin"></iframe></body></html>
        """
        w.loadHTMLString(html, baseURL: URL(string: "https://forja.app/"))
        return w
    }
    func updateUIView(_ uiView: WKWebView, context: Context) {}
}
