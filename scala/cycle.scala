package com.example

// Scala — traits can mutually reference each other via self-types.

trait AlphaT {
    def name: String
    def describe: String = s"AlphaT($name)"
    def spawnBravo(): BravoT = new BravoC(s"$name/b")
}

trait BravoT {
    def tag: String
    def bounceToAlpha(): String = new AlphaC(s"bounce-from-$tag").describe
}

class AlphaC(val name: String) extends AlphaT
class BravoC(val tag:  String) extends BravoT

object CycleDemo {
    def run(): Unit = {
        val a = new AlphaC("root")
        val b = a.spawnBravo()
        println("cycle: " + b.bounceToAlpha())
    }
}
