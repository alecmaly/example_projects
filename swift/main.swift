import Foundation
let GREETING = "hi"
class Greeter {
    var prefix: String = GREETING
    func greet(_ name: String) -> String { return "\(prefix) \(name)" }
}
func main() { let g = Greeter(); print(g.greet("world")) }
main()
