import XCTest
@testable import ForjaCore

/// Garante que o núcleo Swift gera exatamente os mesmos planos que o núcleo Kotlin do Android.
final class ParidadeTests: XCTestCase {
    static func recurso(_ nome: String) -> Data {
        let url = Bundle.module.url(forResource: nome, withExtension: "json", subdirectory: "Resources")!
        return try! Data(contentsOf: url)
    }
    lazy var cat: Catalogo = try! Catalogo.deJson(Self.recurso("exercises"))
    lazy var ouro: [String: Any] = try! JSONSerialization.jsonObject(with: Self.recurso("ouro")) as! [String: Any]

    func itemJson(_ it: Item) -> [String: Any] {
        var o: [String: Any] = ["e": it.exId, "s": it.series, "d": it.descansoSeg]
        if let r = it.reps { o["r"] = r }
        if let t = it.trabalhoSeg { o["t"] = t }
        if let i = it.intensidade { o["i"] = i }
        if let n = it.nota { o["n"] = n }
        return o
    }
    func sessaoJson(_ s: Sessao) -> [String: Any] {
        ["titulo": s.titulo, "foco": s.foco, "tipo": s.tipo, "min": s.minutos, "dia": s.diaSemana,
         "blocos": s.blocos.map { b in ["nome": b.nome, "tipo": b.tipo.rawValue, "voltas": b.voltas, "nota": b.nota ?? "", "itens": b.itens.map(itemJson)] as [String: Any] }]
    }
    func planoJson(_ p: Plano) -> [String: Any] {
        ["nome": p.nome, "resumo": p.resumo, "modalidade": p.modalidade.id, "objetivo": p.objetivo.id, "nivel": p.nivel.id, "meta": p.metaSemanal,
         "dicas": p.dicas, "alertas": p.alertas,
         "semanas": p.semanas.map { w in ["n": w.numero, "fase": w.fase, "nota": w.nota, "sessoes": w.sessoes.map(sessaoJson)] as [String: Any] }]
    }

    /// Primeira diferença entre dois valores JSON (caminho legível).
    func diferenca(_ a: Any, _ b: Any, _ caminho: String = "") -> String? {
        if let da = a as? [String: Any], let db = b as? [String: Any] {
            for k in Set(da.keys).union(db.keys).sorted() {
                guard let va = da[k] else { return "\(caminho).\(k): ausente no Swift" }
                guard let vb = db[k] else { return "\(caminho).\(k): sobra no Swift = \(va)" }
                if let d = diferenca(va, vb, "\(caminho).\(k)") { return d }
            }
            return nil
        }
        if let la = a as? [Any], let lb = b as? [Any] {
            if la.count != lb.count { return "\(caminho): tamanho \(la.count) (Swift) vs \(lb.count) (Kotlin)" }
            for i in la.indices { if let d = diferenca(la[i], lb[i], "\(caminho)[\(i)]") { return d } }
            return nil
        }
        return (a as AnyObject).isEqual(b) ? nil : "\(caminho): Swift=\(a) Kotlin=\(b)"
    }

    func testPlanosIguaisAoKotlin() {
        let casos = ouro["casos"] as! [[String: Any]]
        XCTAssertGreaterThan(casos.count, 100)
        let ger = Gerador(cat)
        var falhas = 0
        for (i, c) in casos.enumerated() {
            let resp = (c["respostas"] as! [String: [String]])
            let plano = ger.gerar(Perfil.de(resp))
            if let d = diferenca(planoJson(plano), c["plano"]!) {
                falhas += 1
                if falhas <= 15 { XCTFail("caso \(i) \(resp["modalidade"] ?? []) \(resp["experiencia"] ?? []) \(resp["dias"] ?? []): \(d)") }
            }
        }
        XCTAssertEqual(falhas, 0, "\(falhas) de \(casos.count) planos diferentes do Kotlin")
    }

    func testRotinasIguaisAoKotlin() {
        let rot = ouro["rotinas"] as! [[String: Any]]
        XCTAssertEqual(rot.count, Rotinas.todas.count)
        for (k, r) in Rotinas.todas.enumerated() {
            let o = rot[k]
            XCTAssertEqual(o["id"] as? String, r.id)
            XCTAssertEqual(o["min"] as? Int, Roteiro.minutos(r.sessao, cat), r.id)
            if let d = diferenca(sessaoJson(r.sessao), o["sessao"]!) { XCTFail("rotina \(r.id): \(d)") }
        }
    }

    func testQuestionario() {
        var r: Respostas = ["modalidade": ["corrida"], "corrida_meta": ["comecar"]]
        XCTAssertFalse(Questionario.visiveis(r).contains { $0.id == "corrida_continuo" })
        r["modalidade"] = ["academia"]
        XCTAssertFalse(Questionario.visiveis(r).contains { $0.id == "equipamentos" })
        r["modalidade"] = ["casa_corpo"]
        XCTAssertTrue(Questionario.visiveis(r).contains { $0.id == "equipamentos" })
        XCTAssertEqual(Datas.diaSemana(0), 4)
    }

    func testLojaPersisteETroca() {
        var dia = 20_382
        let mem = MemoriaArmazenamento()
        let loja = Loja(catalogo: cat, armazenamento: mem) { dia }
        XCTAssertFalse(loja.estado.temPlano)
        let resp: Respostas = ["modalidade": ["academia"], "objetivo": ["massa"], "experiencia": ["intermediario"], "dias": ["4"], "dias_semana": ["1", "2", "4", "5"],
                               "minutos": ["60"], "idade": ["30"], "sexo": ["m"], "altura": ["175"], "peso": ["78"], "limitacoes": ["nenhuma"], "parq": ["nenhuma"]]
        loja.salvarRespostas(resp)
        XCTAssertEqual(loja.estado.plano?.semanas.count, 8)
        XCTAssertEqual(Datas.diaSemana(loja.estado.inicio), 1)
        let ex = loja.estado.plano!.semanas[0].sessoes[0].blocos[1].itens[0].exId
        let alt = cat.alternativas(cat.exigir(ex), equip: loja.estado.perfil!.equip, evitar: loja.estado.perfil!.evitar)
        XCTAssertFalse(alt.isEmpty)
        loja.trocar(0, ex, alt[0].id)
        XCTAssertEqual(loja.estado.plano!.semanas[0].sessoes[0].blocos[1].itens[0].exId, alt[0].id)
        loja.registrar(Registro(epochDay: dia, semana: 1, sessaoIdx: 0, titulo: "A", tipo: "forca", duracaoSeg: 3000, series: [SerieFeita(alt[0].id, 12, 40), SerieFeita(alt[0].id, 12, 40)], esforco: 7, nota: ""))
        let loja2 = Loja(catalogo: cat, armazenamento: mem) { dia }
        XCTAssertEqual(loja2.estado.registros.count, 1)
        XCTAssertEqual(loja2.estado.trocas.count, 1)
        XCTAssertTrue(Progresso.sugestao(loja2.estado.registros, Item(alt[0].id, 3, reps: "8–12"))?.contains("42") ?? false)
        dia += 7
        XCTAssertEqual(loja2.semanaAtual(), 2)
        loja2.apagarTudo()
        XCTAssertFalse(loja2.estado.temPlano)
    }
}
