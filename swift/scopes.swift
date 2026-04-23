// Labeled scope test cases for Swift. See SCOPE_TEST_SPEC.md.

import Foundation

var moduleVar: String = "mod-initial"               // S04.def

func s01Local() {
    let localA = "S01.local"                        // S01.def
    print(localA)                                   // S01.read
}

func s02ClosureRead() {
    let outerA = "S02.outer"                        // S02.outer.def
    let inner = { print(outerA) }                   // S02.inner.read
    inner()
}

func s03ClosureWrite() -> Int {
    var counter = 0                                 // S03.outer.def
    let bump = { counter += 1 }                     // S03.inner.write
    bump(); bump()
    return counter                                  // S03.outer.read
}

func s05SameModuleWrite() {
    moduleVar = "rotated"                           // S05.write
    print(moduleVar)                                // S05.read
}

func s08Shadowing() {
    let moduleVar = "shadowed"                      // S08.shadow.def
    print(moduleVar)                                // S08.shadow.read
}

class ScopeBase {
    static var staticX: Int = 1                     // S12.static.def / S13.base.def
    var x: Int                                      // S11.instance.def
    init(_ x: Int) { self.x = x }
    func readInstance(_ x: Int) -> Int {
        return x + self.x                           // S11.param.read + S11.instance.read
    }
}

class ScopeDerived: ScopeBase {
    init() { super.init(5) }
    func readInherited() -> Int { ScopeBase.staticX }  // S13.derived.read
}

struct Widget {                                     // S14.Widget.def
    let label: String
}

func s14Qualified() -> String { Widget(label: "hi").label } // S14.read

func runScopeDemoSwift() {
    s01Local()
    s02ClosureRead()
    print(s03ClosureWrite())
    s05SameModuleWrite()
    s08Shadowing()
    print(ScopeBase(42).readInstance(100))
    print(ScopeDerived().readInherited())
    print(s14Qualified())
}
