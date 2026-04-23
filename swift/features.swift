import Foundation

// Swift feature coverage: optionals, protocols, extensions, generics,
// enum with associated values, property observers, closures, structs
// (value type), classes (ref type), async/await, guard/if-let.

// --- Protocol + extension default impl.
protocol Greeter {
    func greet() -> String
}

extension Greeter {
    func shout() -> String { greet().uppercased() }
}

// --- Struct (value type).
struct UserV: Greeter {
    let name: String
    var age: Int
    func greet() -> String { "hello, \(name)" }
}

// --- Class (ref type) + inheritance + override.
class AnimalS {
    var name: String
    init(name: String) { self.name = name }
    func speak() -> String { "\(name) makes a sound" }
}

class DogS: AnimalS {
    let breed: String
    init(name: String, breed: String) {
        self.breed = breed
        super.init(name: name)
    }
    override func speak() -> String { "\(super.speak()) (woof, \(breed))" }
}

// --- Enum with associated values = ADT.
enum Shape {
    case circle(Double)
    case rectangle(w: Double, h: Double)
}

func area(_ s: Shape) -> Double {
    switch s {
    case .circle(let r): return .pi * r * r
    case .rectangle(let w, let h): return w * h
    }
}

// --- Generic function with constraints.
func clamp<T: Comparable>(_ n: T, _ lo: T, _ hi: T) -> T {
    max(lo, min(hi, n))
}

// --- Optional chaining + guard/if-let.
func firstLetter(of s: String?) -> Character? {
    guard let s = s, !s.isEmpty else { return nil }
    return s.first
}

// --- Property observers.
class Counter {
    var count: Int = 0 {
        willSet { print("willSet \(newValue)") }
        didSet  { print("didSet from \(oldValue) to \(count)") }
    }
}

// --- Closure capture.
func makeCounter() -> () -> Int {
    var n = 0
    return { n += 1; return n }
}

// --- async/await.
func asyncGreet(_ name: String) async -> String {
    try? await Task.sleep(nanoseconds: 1_000_000)
    return "async hi, \(name)"
}

func runFeatureDemo() {
    let u = UserV(name: "alice", age: 30)
    print(u.greet(), u.shout())

    let d: AnimalS = DogS(name: "Rex", breed: "collie")
    print(d.speak())

    print("area circle = \(area(.circle(2)))")
    print("area rect = \(area(.rectangle(w: 2, h: 3)))")

    print("clamp: \(clamp(42, 0, 10))")
    print("firstLetter: \(String(describing: firstLetter(of: "hello")))")

    let c = Counter()
    c.count = 5

    let next = makeCounter()
    print("counter: \(next()) \(next()) \(next())")
}

// --- Actor (structured concurrency isolation).
actor BankAccount {
    private var balance: Double = 0
    func deposit(_ amount: Double) { balance += amount }
    func getBalance() async -> Double { balance }
    nonisolated func id() -> String { "acct-1" }
}

// --- Custom result builder.
@resultBuilder
struct StringBuilderSwift {
    static func buildBlock(_ parts: String...) -> String {
        parts.joined(separator: "\n")
    }
}

@StringBuilderSwift
func makeDoc() -> String {
    "line1"
    "line2"
    "line3"
}

// --- async let — structured concurrency.
func computeA() async -> Int { 1 }
func computeB() async -> Int { 2 }

func fetchBoth() async -> (Int, Int) {
    async let a = computeA()
    async let b = computeB()
    return await (a, b)
}

// --- Opaque return type (some P).
protocol ShapeProtocol {
    var area: Double { get }
}

struct CircleShape: ShapeProtocol {
    let r: Double
    var area: Double { .pi * r * r }
}

func makeShape(r: Double) -> some ShapeProtocol {
    CircleShape(r: r)
}

// --- inout parameter.
func bumpInout(_ x: inout Int) { x += 1 }
