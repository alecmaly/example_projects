package mono.web

// Kotlin feature coverage — ported from kotlin/Features.kt. Self-contained.

object Config {
    var logLevel: String = "info"
    fun isDebug() = logLevel == "debug"
}

enum class Priority(val weight: Int) {
    LOW(1), MEDIUM(5), HIGH(10);
    fun describe(): String = when (this) {
        LOW    -> "take your time"
        MEDIUM -> "soon please"
        HIGH   -> "drop everything"
    }
}

sealed class Event {
    data class Click(val x: Int, val y: Int) : Event()
    data class Key(val code: Int) : Event()
    object Close : Event()
}

inline fun <reified T> isOfType(x: Any): Boolean = x is T

val String.quoted: String get() = "\"$this\""

fun runFeatureDemo() {
    println("debug? ${Config.isDebug()}")
    Config.logLevel = "debug"
    println("after set: ${Config.isDebug()}")

    val pri = Priority.HIGH
    println("${pri.name} → ${pri.describe()}")

    val events: List<Event> = listOf(Event.Click(1, 2), Event.Key(42), Event.Close)
    for (e in events) {
        val msg = when (e) {
            is Event.Click -> "click@(${e.x},${e.y})"
            is Event.Key   -> "key=${e.code}"
            Event.Close    -> "close"
        }
        println(msg)
    }

    println("isOfType<String>(\"x\") = ${isOfType<String>("x")}")
    println("isOfType<Int>(\"x\") = ${isOfType<Int>("x")}")
    println("quoted = ${"hello".quoted}")

    val out = "abc".let { it.uppercase() }
        .also { println("also saw: $it") }
        .run { length }
    println("len = $out")

    val list = mutableListOf<Int>().apply { add(1); add(2); add(3) }
    println("apply built: $list")

    val summary = with(list) { "size=$size first=${first()}" }
    println(summary)
}
