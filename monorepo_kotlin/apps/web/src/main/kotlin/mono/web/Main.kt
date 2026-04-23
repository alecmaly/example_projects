package mono.web

// Class import.
import mono.shared.User
import mono.shared.Role
import mono.shared.DEFAULT_ROLE
// Object-member import (accesses the `Util` object directly).
import mono.shared.Util.formatUser
import mono.shared.Util.hello
// Wildcard import.
import mono.utils.*
// Aliased import.
import mono.shared.quoted as quote
// Aliased class import.
import mono.shared.User as SharedUser

fun main() {
    val u: SharedUser = User(1, "alice")
    val role: Role = DEFAULT_ROLE
    println("${formatUser(u)} $role")
    println(hello("world"))
    println("tag=$TAG clamped=${clamp(42, 0, 10)}")
    println("hello".quote())

    // Ported coverage from the flat kotlin/ fixture.
    runFeatureDemo()
    runScopeDemo()
    importsDemo()
    runAdvancedDemo()
    runCastsDemo()

    // T1 transitive chain — LSP must follow Deep.VALUE_ALIAS back through
    // Middle.MIDDLE_VALUE to Origin.ORIGIN_VALUE.
    println("transitive: ${mono.shared.chain.Deep.VALUE_ALIAS}")

    // Cycle: CycleA ↔ CycleB.
    println("cycle: ${CycleA.kickOff()}")
}
