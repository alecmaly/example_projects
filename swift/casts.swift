// Swift cast catalogue.

import Foundation

class AnimalC {}
class DogC: AnimalC { func bark() -> String { "woof" } }

// 1. `as!` — forced downcast (crash on failure).
func forceCast(_ a: AnimalC) -> DogC { return a as! DogC }

// 2. `as?` — optional downcast (nil on failure).
func safeCast(_ a: AnimalC) -> DogC? { return a as? DogC }

// 3. `is` — type-test.
func isDog(_ a: AnimalC) -> Bool { return a is DogC }

// 4. Pattern-match cast.
func describe(_ o: Any) -> String {
    switch o {
    case let s as String where s.count > 3: return "long str \(s)"
    case let s as String:                   return "short \(s)"
    case let i as Int:                       return "int \(i)"
    case is Double:                          return "double"
    case nil as Any?:                        return "nil"
    default:                                 return "other"
    }
}

// 5. Numeric conversion initializers.
func numericCasts() {
    let i: Int = 300
    let d: Double = Double(i)
    let s: String = String(i)
    if let n = Int("42") { print("parsed \(n)") }
    print(i, d, s)
}

// 6. Bridging (Swift String ↔ NSString).
func bridging() {
    let s: String = "hello"
    let ns: NSString = s as NSString
    let back: String = ns as String
    print(s, ns, back)
}

// 7. Enum raw-value conversion.
enum Role: Int { case admin = 1, user = 2, guest = 3 }
func roleFromInt(_ n: Int) -> Role? { return Role(rawValue: n) }

func runCastsDemoSwift() {
    let a: AnimalC = DogC()
    print(forceCast(a).bark())
    print(safeCast(a)?.bark() ?? "nil")
    print(isDog(a))
    print(describe("a long string"))
    numericCasts()
    bridging()
    print(roleFromInt(1) as Any)
}
