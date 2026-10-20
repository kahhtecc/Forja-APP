import SwiftUI
import ForjaCore

enum Cor {
    static let fundo = Color(hex: 0x0E0D0C)
    static let sup1 = Color(hex: 0x161412)
    static let sup2 = Color(hex: 0x1E1B18)
    static let sup3 = Color(hex: 0x28241F)
    static let borda = Color(hex: 0x35302A)
    static let texto = Color(hex: 0xF2EBE0)
    static let texto2 = Color(hex: 0xA89E90)
    static let texto3 = Color(hex: 0x6E665C)
    static let brasa = Color(hex: 0xFF5B22)
    static let brasaClara = Color(hex: 0xFF8A50)
    static let ok = Color(hex: 0x34D399)
    static let alerta = Color(hex: 0xFBBF24)
    static let perigo = Color(hex: 0xF43F5E)
    static let gradBrasa = LinearGradient(colors: [Color(hex: 0xFF8A50), brasa, Color(hex: 0xD9381E)], startPoint: .topLeading, endPoint: .bottomTrailing)

    static func modalidade(_ m: Modalidade?) -> Color {
        switch m {
        case .academia, .none: return brasa
        case .casaCorpo: return Color(hex: 0xF2B24C)
        case .casaElastico: return Color(hex: 0xE879A6)
        case .corrida: return Color(hex: 0x34D399)
        case .bike: return Color(hex: 0x38BDF8)
        case .luta: return Color(hex: 0xF43F5E)
        case .atleta: return Color(hex: 0xA78BFA)
        case .hiit: return Color(hex: 0xFACC15)
        case .hibrido: return Color(hex: 0xFB923C)
        case .mobilidade: return Color(hex: 0x5EEAD4)
        case .longevidade: return Color(hex: 0xA3E635)
        }
    }
    static func tipoSessao(_ tipo: String, _ padrao: Color) -> Color {
        switch tipo {
        case "corrida": return modalidade(.corrida)
        case "bike": return modalidade(.bike)
        case "luta": return modalidade(.luta)
        case "hiit": return modalidade(.hiit)
        case "mobilidade": return modalidade(.mobilidade)
        case "cardio": return Color(hex: 0x7DD3FC)
        case "atleta": return modalidade(.atleta)
        default: return padrao
        }
    }
    static func tema(_ id: String) -> Color { Modalidade.de(id).map { modalidade($0) } ?? modalidade(.mobilidade) }
    /// Texto legível sobre uma cor de destaque.
    static func sobre(_ c: Color) -> Color { c.luminancia > 0.45 ? fundo : .white }
}

extension Color {
    init(hex: UInt32) {
        self.init(.sRGB, red: Double((hex >> 16) & 0xFF) / 255, green: Double((hex >> 8) & 0xFF) / 255, blue: Double(hex & 0xFF) / 255, opacity: 1)
    }
    var luminancia: Double {
        var r: CGFloat = 0, g: CGFloat = 0, b: CGFloat = 0, a: CGFloat = 0
        UIColor(self).getRed(&r, green: &g, blue: &b, alpha: &a)
        func lin(_ c: CGFloat) -> Double { let c = Double(c); return c <= 0.03928 ? c / 12.92 : pow((c + 0.055) / 1.055, 2.4) }
        return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)
    }
}

enum Tipo {
    static func display(_ tam: CGFloat, _ peso: String = "Black") -> Font { .custom("BigShouldersDisplay-\(peso)", size: tam, relativeTo: .largeTitle) }
    static func texto(_ tam: CGFloat, _ peso: String = "Medium") -> Font { .custom("Manrope-\(peso)", size: tam, relativeTo: .body) }
    static let gigante = display(64)
    static let titulo1 = display(40)
    static let titulo2 = display(30, "ExtraBold")
    static let titulo3 = display(22, "ExtraBold")
    static let numero = display(28)
    static let rotulo = texto(11, "ExtraBold")
    static let corpo = texto(15)
    static let corpoForte = texto(15, "Bold")
    static let pequeno = texto(13)
    static let pequenoForte = texto(13, "Bold")
    static let botao = texto(15, "ExtraBold")
}

enum Haptico {
    static func toque() { UIImpactFeedbackGenerator(style: .light).impactOccurred() }
    static func forte() { UIImpactFeedbackGenerator(style: .heavy).impactOccurred() }
    static func sucesso() { UINotificationFeedbackGenerator().notificationOccurred(.success) }
}

extension Modalidade {
    var simbolo: String {
        switch self {
        case .academia: return "dumbbell.fill"
        case .casaCorpo: return "house.fill"
        case .casaElastico: return "arrow.left.and.right"
        case .corrida: return "figure.run"
        case .bike: return "figure.outdoor.cycle"
        case .luta: return "figure.boxing"
        case .atleta: return "trophy.fill"
        case .hiit: return "bolt.fill"
        case .hibrido: return "flame.fill"
        case .mobilidade: return "figure.mind.and.body"
        case .longevidade: return "figure.walk"
        }
    }
}
