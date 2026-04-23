package mono.web

// 1. `as` — throws ClassCastException on failure.
fun unsafeCast(x: Any): String = x as String

// 2. `as?` — safe cast, returns null on failure.
fun safeCast(x: Any): String? = x as? String

// 3. `is` / `!is` with smart cast.
fun describe(x: Any): String = when (x) {
    is String -> "str len=${x.length}"          // smart-cast to String
    is Int    -> "int=${x}"
    !is Number -> "not a number"
    else       -> "number ${x}"
}

// 4. Nullable-unwrap via `!!`.
fun forceUnwrap(s: String?): String = s!!

// 5. Numeric conversions (no implicit promotion in Kotlin).
fun numericCasts() {
    val l: Long = 42L
    val i: Int = l.toInt()
    val d: Double = i.toDouble()
    val s: String = d.toString()
    println("$l $i $d $s")
}

// 6. Generic reified cast via `inline fun <reified T>`.
inline fun <reified T> tryCast(x: Any): T? = x as? T

// 7. Data-class copy — not a cast, but a related value-transformation.
data class Point(val x: Int, val y: Int)
fun copyShift(p: Point, dx: Int): Point = p.copy(x = p.x + dx)

// 8. Sealed-class exhaustive when.
sealed class Event {
    data class Click(val x: Int) : Event()
    object   Close : Event()
}
fun handle(e: Event): String = when (e) {
    is Event.Click -> "click ${e.x}"
    Event.Close    -> "close"
}

fun runCastsDemo() {
    println(unsafeCast("hi"))
    println(safeCast(42))
    println(describe("long string"))
    println(forceUnwrap("x"))
    numericCasts()
    println(tryCast<String>("s") ?: "null")
    println(copyShift(Point(1, 2), 5))
    println(handle(Event.Click(3)))
}
