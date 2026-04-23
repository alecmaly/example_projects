// Swift class cycle — use `weak` on one side to avoid a retain cycle
// at runtime (ARC would otherwise leak). The LSP must still resolve
// both directions symbolically.

class AlphaS {
    let name: String
    var child: BravoS?              // strong → BravoS
    init(name: String) { self.name = name }
    func describe() -> String { return "AlphaS(\(name))" }
    func spawnBravo() -> BravoS {
        let b = BravoS(tag: "\(name)/b")
        b.owner = self              // weak back-ref
        child = b
        return b
    }
}

class BravoS {
    let tag: String
    weak var owner: AlphaS?         // weak → breaks cycle at runtime
    init(tag: String) { self.tag = tag }
    func bounceToAlpha() -> String {
        return AlphaS(name: "bounce-from-\(tag)").describe()
    }
}

func runCycleDemoSwift() {
    let a = AlphaS(name: "root")
    let b = a.spawnBravo()
    print("cycle:", b.bounceToAlpha())
}
