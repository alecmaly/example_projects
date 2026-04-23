// Labeled scope test cases for Kotlin — monorepo edition.
// Cross-package refs target mono.shared.SharedStatus + mono.shared.scopes.ns.Widget.

package mono.web

import mono.shared.SharedStatus as CrossStatus      // S09.def
import mono.shared.SharedStatus
import mono.shared.scopes.ns.Widget                  // S14.import

var moduleVar: String = "mod-initial"                // S04.def

fun s01Local() {
    val localA = "S01.local"                         // S01.def
    println(localA)                                  // S01.read
}

fun s02ClosureRead() {
    val outerA = "S02.outer"                         // S02.outer.def
    val inner = { println(outerA) }                  // S02.inner.read
    inner()
}

fun s03ClosureWrite(): Int {
    var counter = 0                                  // S03.outer.def
    val bump = { counter += 1 }                      // S03.inner.write
    bump(); bump()
    return counter                                   // S03.outer.read
}

fun s05SameModuleWrite() {
    moduleVar = "rotated"                            // S05.write
    println(moduleVar)                               // S05.read
}

fun s06CrossRead(): String = SharedStatus            // S06.read

fun s07CrossWrite() {
    SharedStatus = "S07"                             // S07.write
}

fun s08Shadowing() {
    val moduleVar = "shadowed"                       // S08.shadow.def
    println(moduleVar)                               // S08.shadow.read
}

fun s09AliasedImport() {
    println(CrossStatus)                             // S09.read
}

open class ScopeBase(val x: Int) {                   // S11.instance.def (x)
    companion object { var staticX: Int = 1 }        // S12.static.def / S13.base.def

    fun readInstance(x: Int): Int =
        x + this.x                                   // S11.param.read + S11.instance.read
}

class ScopeDerived : ScopeBase(5) {
    fun readInherited(): Int = staticX               // S13.derived.read
}

fun s14Qualified(): String = Widget("hi").label      // S14.read

fun runScopeDemo() {
    s01Local()
    s02ClosureRead()
    println(s03ClosureWrite())
    s05SameModuleWrite()
    println(s06CrossRead())
    s07CrossWrite()
    s08Shadowing()
    s09AliasedImport()
    println(ScopeBase(42).readInstance(100))
    println(ScopeDerived().readInherited())
    println(s14Qualified())
}
