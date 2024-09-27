package com.example

open class BaseClass {
    protected val baseVar = "I'm a base class variable"

    open suspend fun baseMethod() {
        println("This is a method from BaseClass")
        println("Base var: $baseVar")
        kotlinx.coroutines.delay(100)
    }
}

class DerivedClass : BaseClass() {
    private val derivedVar = "I'm a derived class variable"

    suspend fun derivedMethod() {
        println("This is a method from DerivedClass")
        println("Derived var: $derivedVar")
        baseMethod()
    }

    override suspend fun baseMethod() {
        super.baseMethod()
        println("This is an overridden method in DerivedClass")
    }
}

class Class1 {
    private val privateVar = "I'm private"

    suspend fun method1() {
        println("This is method1 from Class1")
        privateMethod()
    }

    private suspend fun privateMethod() {
        println("This is a private method in Class1")
        println("Private var: $privateVar")
        kotlinx.coroutines.delay(100) // Simulate some async work
    }

    companion object {
        const val STATIC_VAR = "I'm a static variable in Class1"
    }
}