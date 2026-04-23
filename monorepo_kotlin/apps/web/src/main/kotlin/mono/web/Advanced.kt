package mono.web

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.collect
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withContext
import kotlin.properties.Delegates

// Kotlin advanced-feature coverage ported from the flat kotlin/. Covers:
// runBlocking, suspend fn, launch, delay, Flow + emit + collect, open
// class + override + super, companion object usage, higher-order
// functions, function overloading.

// --- open class + override + super + companion object.
open class AnimalK(val name: String) {
    open fun speak(): String = "$name makes a sound"

    companion object {
        const val KINGDOM: String = "Animalia"
    }
}

class DogK(name: String, val breed: String) : AnimalK(name) {
    override fun speak(): String = "${super.speak()} (woof, $breed)"
}

// --- function overloading.
fun addK(a: Int, b: Int) = a + b
fun addK(a: String, b: String) = a + b

// --- higher-order function + lambda.
fun operateOnNumbers(a: Int, b: Int, operation: (Int, Int) -> Int): Int = operation(a, b)

// --- suspend fn.
suspend fun nap(ms: Long): Long {
    delay(ms)
    return ms
}

// --- Flow builder + map + collect.
fun numberFlow(): Flow<Int> = flow {
    for (i in 1..5) {
        delay(2)
        emit(i)
    }
}

// --- top-level coroutine entry point.
fun runAdvancedDemo() = runBlocking {
    // Inheritance + companion.
    val d: AnimalK = DogK("Rex", "collie")
    println(d.speak())
    println("kingdom=${AnimalK.KINGDOM}")

    // Function overloading.
    println(addK(5, 3))
    println(addK("hello ", "world"))

    // Higher-order function.
    println("op=${operateOnNumbers(2, 3) { a, b -> a * b }}")

    // Coroutines: launch + delay.
    val job = launch {
        delay(2)
        println("launched")
    }
    job.join()

    // suspend + withContext.
    val napped = withContext(Dispatchers.Default) { nap(1) }
    println("napped=$napped")

    // Parallel fan-out with async/awaitAll.
    val results = listOf(1, 2, 3).map { n -> async { nap(1); n * n } }.awaitAll()
    println("parallel=$results")

    // Flow emit + map + collect.
    numberFlow()
        .map { it * it }
        .collect { v -> println("flow=$v") }
}

// --- Delegated property via lazy.
val cachedGreeting by lazy { "hi".also { println("computed") } }

// --- Delegated property via Delegates.observable.
var observedNameK: String by Delegates.observable("initial") { _, old, new ->
    println("observedNameK changed: $old -> $new")
}

// --- Extension function on String.
fun String.truncateK(n: Int): String = if (length > n) substring(0, n) + "..." else this

// --- Extension property on String.
val String.firstCharOrQ: Char get() = firstOrNull() ?: '?'

// --- Inline function with reified generic.
inline fun <reified T> typeNameK(): String = T::class.qualifiedName ?: "?"

// --- Typealias.
typealias StringMapK = Map<String, String>

// --- Object declaration (singleton).
object SingletonKt { fun ping() = "pong" }
