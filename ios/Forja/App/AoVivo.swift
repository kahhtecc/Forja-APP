import Foundation
import ActivityKit
import UserNotifications

/// Treino ao vivo fora do app: Live Activity (tela bloqueada, Dynamic Island e Smart Stack do Apple Watch
/// no watchOS 11+) e notificação no fim do descanso, que o iPhone espelha no relógio com vibração no pulso.
@MainActor
final class AoVivo {
    static let shared = AoVivo()
    static let chave = "aovivo.on"
    static var ligado: Bool { UserDefaults.standard.object(forKey: chave) as? Bool ?? true }

    private var atividade: Any?       // Activity<TreinoAtividade> (iOS 16.1+)
    private var ultimo: Any?          // último ContentState enviado
    private var ultimaAtualizacao = Date.distantPast
    private static let idNotificacao = "forja.fim-descanso"

    static func cor(_ tipo: String) -> UInt32 {
        switch tipo {
        case "corrida": return 0x34D399
        case "bike": return 0x38BDF8
        case "luta": return 0xF43F5E
        case "hiit": return 0xFACC15
        case "mobilidade": return 0x5EEAD4
        case "cardio": return 0x7DD3FC
        case "atleta": return 0xA78BFA
        default: return 0xFF5B22
        }
    }

    /// Fecha Live Activities que ficaram de um treino interrompido (app fechado à força).
    func limparPendentes() {
        guard #available(iOS 16.2, *) else { return }
        for a in Activity<TreinoAtividade>.activities where atividade == nil {
            Task { await a.end(nil, dismissalPolicy: .immediate) }
        }
    }

    func pedirPermissaoNotificacoes() {
        guard Self.ligado else { return }
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound]) { _, _ in }
    }

    @available(iOS 16.1, *)
    func iniciar(titulo: String, tipo: String, inicio: Date, estado: TreinoAtividade.ContentState) {
        guard Self.ligado, ActivityAuthorizationInfo().areActivitiesEnabled else { return }
        encerrar(concluido: false, imediato: true)
        let attrs = TreinoAtividade(titulo: titulo, tipo: tipo, inicio: inicio, cor: Self.cor(tipo))
        do {
            if #available(iOS 16.2, *) {
                atividade = try Activity.request(attributes: attrs, content: ActivityContent(state: estado, staleDate: nil), pushType: nil)
            } else {
                atividade = try Activity.request(attributes: attrs, contentState: estado, pushType: nil)
            }
            ultimo = estado
            ultimaAtualizacao = Date()
        } catch {}
    }

    /// Atualiza a Live Activity. Mudança só de FC é limitada a uma a cada 15 s.
    @available(iOS 16.1, *)
    func atualizar(_ estado: TreinoAtividade.ContentState) {
        guard let a = atividade as? Activity<TreinoAtividade> else { return }
        if let u = ultimo as? TreinoAtividade.ContentState {
            if u == estado { return }
            var semFC = u; semFC.bpm = estado.bpm
            if semFC == estado && Date().timeIntervalSince(ultimaAtualizacao) < 15 { return }
        }
        ultimo = estado
        ultimaAtualizacao = Date()
        Task {
            if #available(iOS 16.2, *) { await a.update(ActivityContent(state: estado, staleDate: nil)) }
            else { await a.update(using: estado) }
        }
    }

    func encerrar(concluido: Bool, imediato: Bool = false) {
        cancelarAviso()
        guard #available(iOS 16.1, *), let a = atividade as? Activity<TreinoAtividade> else { return }
        atividade = nil
        var final = (ultimo as? TreinoAtividade.ContentState)
        final?.concluido = concluido
        final?.descansando = false
        final?.fimEm = nil
        let politica: ActivityUIDismissalPolicy = imediato || !concluido ? .immediate : .after(Date().addingTimeInterval(120))
        Task {
            if #available(iOS 16.2, *) { await a.end(final.map { ActivityContent(state: $0, staleDate: nil) }, dismissalPolicy: politica) }
            else { await a.end(using: final, dismissalPolicy: politica) }
        }
    }

    /// Notificação no fim do descanso (ou do exercício por tempo). Com o app aberto o iOS não a mostra;
    /// com o iPhone bloqueado ela toca e aparece no Apple Watch, que vibra no pulso.
    func agendarAviso(em data: Date, descanso: Bool, proximo: String?) {
        cancelarAviso()
        guard Self.ligado, data.timeIntervalSinceNow > 1 else { return }
        let c = UNMutableNotificationContent()
        c.title = descanso ? "Fim do descanso" : "Tempo!"
        c.body = descanso ? (proximo.map { "Bora: \($0)" } ?? "Próxima série") : (proximo.map { "Próximo: \($0)" } ?? "Exercício concluído")
        c.sound = .default
        c.interruptionLevel = .timeSensitive
        c.threadIdentifier = "forja.treino"
        let gatilho = UNTimeIntervalNotificationTrigger(timeInterval: data.timeIntervalSinceNow, repeats: false)
        UNUserNotificationCenter.current().add(UNNotificationRequest(identifier: Self.idNotificacao, content: c, trigger: gatilho))
    }

    func cancelarAviso() {
        UNUserNotificationCenter.current().removePendingNotificationRequests(withIdentifiers: [Self.idNotificacao])
    }
}
