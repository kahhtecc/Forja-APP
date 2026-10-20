import SwiftUI
import ForjaCore
import UserNotifications

final class Preferencias: Armazenamento {
    private let d: UserDefaults
    private let prefixo: String
    init(prefixo: String) { d = .standard; self.prefixo = prefixo }
    func ler(_ chave: String) -> String? { d.string(forKey: prefixo + chave) }
    func gravar(_ chave: String, _ valor: String?) { if let v = valor { d.set(v, forKey: prefixo + chave) } else { d.removeObject(forKey: prefixo + chave) } }
}

struct Fonte: Identifiable { let id: String, titulo: String, ano: Int, url: String }

/// Estado observável do app: embrulha a Loja do núcleo (mesma lógica do Android).
@MainActor
final class AppEstado: ObservableObject {
    let catalogo: Catalogo
    let fontes: [Fonte]
    let loja: Loja
    let demo: Bool
    let telaInicial: String?
    @Published private(set) var e: Estado
    @Published var treinoAtivo: TreinoAlvo?

    init() {
        let args = ProcessInfo.processInfo.arguments
        func arg(_ nome: String) -> String? { args.firstIndex(of: "-" + nome).flatMap { $0 + 1 < args.count ? args[$0 + 1] : nil } }
        demo = arg("demo") == "1"
        telaInicial = arg("tela")
        let dados = try! Data(contentsOf: Bundle.main.url(forResource: "exercises", withExtension: "json")!)
        catalogo = try! Catalogo.deJson(dados)
        if let u = Bundle.main.url(forResource: "fontes", withExtension: "json"), let d = try? Data(contentsOf: u),
           let a = try? JSONSerialization.jsonObject(with: d) as? [[String: Any]] {
            fontes = a.map { Fonte(id: $0["id"] as? String ?? UUID().uuidString, titulo: $0["titulo"] as? String ?? "", ano: $0["ano"] as? Int ?? 0, url: $0["url"] as? String ?? "") }
        } else { fontes = [] }
        loja = Loja(catalogo: catalogo, armazenamento: Preferencias(prefixo: demo ? "demo." : "forja."))
        e = loja.estado
        loja.aoMudar = { [weak self] novo in self?.e = novo }
        if demo { semearDemo() }
    }

    // Atalhos
    var plano: Plano? { e.plano }
    var semanaAtual: Int { loja.semanaAtual() }
    var corModalidade: Color { Cor.modalidade(e.plano?.modalidade) }

    private func semearDemo() {
        guard !e.temPlano else { return }
        let r: Respostas = ["nome": ["Kaique"], "modalidade": ["academia"], "objetivo": ["massa"], "experiencia": ["intermediario"],
                            "dias": ["4"], "dias_semana": ["1", "2", "4", "5"], "minutos": ["60"], "idade": ["29"], "sexo": ["m"],
                            "altura": ["178"], "peso": ["80"], "limitacoes": ["nenhuma"], "parq": ["nenhuma"]]
        loja.salvarRespostas(r)
        let hoje = loja.hoje()
        let inicio = Datas.segunda(hoje) - 14
        loja.definirInicio(inicio)
        guard let plano = loja.estado.plano else { return }
        for w in 1...3 {
            for (i, s) in plano.semanas[w - 1].sessoes.enumerated() {
                let dia = inicio + (w - 1) * 7 + (s.diaSemana - 1)
                if dia >= hoje { continue }
                let series = Roteiro.passos(s, catalogo).filter { $0.item.reps != nil && $0.blocoNome != "Aquecimento" }.map {
                    SerieFeita($0.ex.id, 10 + (w % 2), kgExemplo($0.ex.id) + Double(w - 1) * 2.5)
                }
                loja.registrar(Registro(epochDay: dia, semana: w, sessaoIdx: i, titulo: s.titulo, tipo: s.tipo, duracaoSeg: s.minutos * 60, series: series, esforco: 7 + i % 2, nota: ""))
            }
        }
        for (k, kg) in [81.2, 80.8, 80.5, 80.1].enumerated() { loja.registrarPeso(kg, dia: hoje - (3 - k) * 7) }
    }

    private func kgExemplo(_ id: String) -> Double {
        if ["agachamento", "leg", "terra", "stiff"].contains(where: { id.contains($0) }) { return 60 }
        if ["supino", "remada", "puxada"].contains(where: { id.contains($0) }) { return 40 }
        if id.contains("desenvolvimento") { return 20 }
        return 12
    }

    // Lembretes nos dias de treino (notificação local semanal por dia).
    func configurarLembretes(ligado: Bool, hora: Int) {
        UserDefaults.standard.set(ligado, forKey: "lembrete.on")
        UserDefaults.standard.set(hora, forKey: "lembrete.hora")
        let c = UNUserNotificationCenter.current()
        c.removeAllPendingNotificationRequests()
        guard ligado, let p = e.perfil else { return }
        c.requestAuthorization(options: [.alert, .sound, .badge]) { ok, _ in
            guard ok else { return }
            for dia in p.dias {
                let conteudo = UNMutableNotificationContent()
                conteudo.title = "Hoje tem treino"
                conteudo.body = "Seu treino de hoje está pronto no Forja. Bora forjar!"
                conteudo.sound = .default
                var dc = DateComponents(); dc.hour = hora; dc.minute = 0
                dc.weekday = dia == 7 ? 1 : dia + 1 // Calendar: 1 = domingo
                let req = UNNotificationRequest(identifier: "treino-\(dia)", content: conteudo, trigger: UNCalendarNotificationTrigger(dateMatching: dc, repeats: true))
                c.add(req)
            }
        }
    }
}

struct TreinoAlvo: Identifiable, Equatable {
    let id = UUID()
    let sessao: Sessao
    let semana: Int
    let idx: Int
}

@main
struct ForjaApp: App {
    @StateObject private var app = AppEstado()
    init() {
        UINavigationBar.appearance().largeTitleTextAttributes = [.foregroundColor: UIColor(Cor.texto)]
        UINavigationBar.appearance().titleTextAttributes = [.foregroundColor: UIColor(Cor.texto), .font: UIFont(name: "Manrope-ExtraBold", size: 16) ?? .boldSystemFont(ofSize: 16)]
    }
    var body: some Scene {
        WindowGroup {
            RaizView()
                .environmentObject(app)
                .preferredColorScheme(.dark)
                .tint(Cor.brasa)
        }
    }
}
