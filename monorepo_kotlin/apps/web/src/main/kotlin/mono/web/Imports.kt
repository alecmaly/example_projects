package mono.web

// 1. Single-class import.
import kotlin.math.PI
// 2. Wildcard.
import kotlin.collections.*
// 3. Aliased import.
import kotlin.math.sqrt as kSqrt
// 4. Top-level function import.
import kotlin.math.max
// 5. Re-imported with alias.
import kotlin.math.PI as MATH_PI
// 6. Cross-workspace-package imports.
import mono.shared.User
import mono.shared.Util
import mono.utils.TAG
import mono.utils.clamp as kclamp

fun importsDemo() {
    val xs = arrayListOf(1, 2, 3)
    val v = PI + kSqrt(2.0) + max(1, 2) + MATH_PI
    val u = User(1, "imports")
    println("$xs sum=${xs.sum()} v=$v")
    println("shared=${Util.formatUser(u)} tag=$TAG clamp=${kclamp(42, 0, 10)}")
}
