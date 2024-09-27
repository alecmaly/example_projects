import com.example.BaseClass
import com.example.DerivedClass
import com.example.function1
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

val globalVar = "I'm global"

fun main() = runBlocking {
    val localVar = "I'm local to main"
    println(globalVar)
    println(localVar)

    val baseObj = BaseClass()
    val derivedObj = DerivedClass()

    baseObj.baseMethod()
    derivedObj.baseMethod()
    derivedObj.derivedMethod()

    function1()
    recursiveFunction(5)

    // Using coroutines
    launch {
        delay(100)
        println("This is executed asynchronously")
    }

    // Using higher-order functions
    val numbers = listOf(1, 2, 3, 4, 5)
    val evenSquares = numbers.filter { it % 2 == 0 }.map { it * it }
    println("Even squares: $evenSquares")

    // Demonstrate function overloading
    println(add(5, 3))
    println(add("Hello", "World"))

    // Demonstrate higher-order function
    val result = operateOnNumbers(5, 3) { a, b -> a * b }
    println("Result of operation: $result")

    // Demonstrate coroutine flow
    createFlow().collect { value ->
        println("Flow emitted: $value")
    }
}

suspend fun recursiveFunction(n: Int) {
    if (n <= 0) return
    println("Recursion level: $n")
    delay(100) // Simulate some async work
    recursiveFunction(n - 1)
}

// Function overloading
fun add(a: Int, b: Int) = a + b
fun add(a: String, b: String) = a + b

// Higher-order function
fun operateOnNumbers(a: Int, b: Int, operation: (Int, Int) -> Int): Int {
    return operation(a, b)
}

// Coroutine flow
fun createFlow(): Flow<Int> = flow {
    for (i in 1..5) {
        delay(100)
        emit(i)
    }
}