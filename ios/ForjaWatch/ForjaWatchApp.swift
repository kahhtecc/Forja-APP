import SwiftUI
import WatchKit
import HealthKit

/// Recebe o pedido do iPhone (HKHealthStore.startWatchApp) para abrir o treino no relógio.
final class DelegadoRelogio: NSObject, WKApplicationDelegate {
    func handle(_ workoutConfiguration: HKWorkoutConfiguration) {
        DispatchQueue.main.async { ModeloRelogio.shared.iniciarPeloIPhone(workoutConfiguration) }
    }
}

@main
struct ForjaWatchApp: App {
    @WKApplicationDelegateAdaptor(DelegadoRelogio.self) var delegado
    @ObservedObject private var modelo = ModeloRelogio.shared

    var body: some Scene {
        WindowGroup {
            Group {
                switch modelo.tela {
                case .hoje: HojeRelogioView()
                case .treino: TreinoRelogioView()
                case .concluido: ConcluidoRelogioView()
                }
            }
            .environmentObject(modelo)
            .tint(CorW.brasa)
        }
    }
}

enum CorW {
    static let fundo = Color(red: 0x0E / 255, green: 0x0D / 255, blue: 0x0C / 255)
    static let sup1 = Color(red: 0x1E / 255, green: 0x1B / 255, blue: 0x18 / 255)
    static let sup2 = Color(red: 0x28 / 255, green: 0x24 / 255, blue: 0x1F / 255)
    static let texto = Color(red: 0xF2 / 255, green: 0xEB / 255, blue: 0xE0 / 255)
    static let texto2 = Color(red: 0xA8 / 255, green: 0x9E / 255, blue: 0x90 / 255)
    static let brasa = Color(red: 1, green: 0x5B / 255, blue: 0x22 / 255)
    static let ok = Color(red: 0x34 / 255, green: 0xD3 / 255, blue: 0x99 / 255)
    static let fc = Color(red: 0xF4 / 255, green: 0x3F / 255, blue: 0x5E / 255)

    static func tipo(_ t: String) -> Color {
        switch t {
        case "corrida": return Color(red: 0x34 / 255, green: 0xD3 / 255, blue: 0x99 / 255)
        case "bike": return Color(red: 0x38 / 255, green: 0xBD / 255, blue: 0xF8 / 255)
        case "luta": return fc
        case "hiit": return Color(red: 0xFA / 255, green: 0xCC / 255, blue: 0x15 / 255)
        case "mobilidade": return Color(red: 0x5E / 255, green: 0xEA / 255, blue: 0xD4 / 255)
        case "cardio": return Color(red: 0x7D / 255, green: 0xD3 / 255, blue: 0xFC / 255)
        case "atleta": return Color(red: 0xA7 / 255, green: 0x8B / 255, blue: 0xFA / 255)
        default: return brasa
        }
    }
    static func simbolo(_ t: String) -> String {
        switch t {
        case "corrida": return "figure.run"
        case "bike": return "figure.outdoor.cycle"
        case "luta": return "figure.boxing"
        case "hiit": return "bolt.fill"
        case "mobilidade": return "figure.mind.and.body"
        case "cardio": return "heart.fill"
        case "atleta": return "trophy.fill"
        default: return "dumbbell.fill"
        }
    }
}

enum TipoW {
    static func numero(_ t: CGFloat) -> Font { .custom("BigShouldersDisplay-Black", size: t) }
    static func titulo(_ t: CGFloat) -> Font { .custom("BigShouldersDisplay-ExtraBold", size: t) }
    static let rotulo = Font.system(size: 11, weight: .heavy, design: .rounded)
}

struct RotuloW: View {
    let texto: String
    var cor: Color = CorW.texto2
    init(_ texto: String, _ cor: Color = CorW.texto2) { self.texto = texto; self.cor = cor }
    var body: some View { Text(texto.uppercased()).font(TipoW.rotulo).tracking(1.1).foregroundStyle(cor).lineLimit(1) }
}
