package com.example

suspend fun function1() {
    println("This is function1 from Class2")
    internalFunction()
}

private suspend fun internalFunction() {
    println("This is an internal function in Class2")
    kotlinx.coroutines.delay(100) // Simulate some async work
}

// Extension function example
fun String.addExclamation() = "$this!"

// Sealed class example
sealed class Result {
    data class Success(val data: String) : Result()
    data class Error(val message: String) : Result()
}