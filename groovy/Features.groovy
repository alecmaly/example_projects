package com.example

// Groovy features: closures, GString, meta-programming, traits,
// operator overloading, @CompileStatic, null-safe ops.

import groovy.transform.CompileStatic
import groovy.transform.ToString

// Trait = reusable method bundle (mixed into classes).
trait Greetable {
    String greeting() { "hello" }
    String greetTo(String name) { "${greeting()}, $name" }
}

// Operator overloading via `plus`, `multiply`.
@ToString(includeNames = true)
class Vec2 implements Greetable {
    double x; double y
    Vec2 plus(Vec2 other)      { new Vec2(x: x + other.x, y: y + other.y) }
    Vec2 multiply(double k)    { new Vec2(x: x * k, y: y * k) }
    double dot(Vec2 other)     { x * other.x + y * other.y }
}

// Closure with free-var capture.
def makeCounter() {
    int count = 0
    return { -> count++ }
}

// Meta-programming: dynamic method addition on an instance.
def demoMetaProgramming() {
    def obj = new Object()
    obj.metaClass.greet = { String n -> "meta, $n" }
    obj.greet("world")
}

// @CompileStatic — switches Groovy to static compilation for this block.
@CompileStatic
int clamp(int n, int lo, int hi) { Math.max(lo, Math.min(hi, n)) }

// Spread / null-safe / Elvis.
String firstName(Map? m) {
    return m?.name?.split(" ")?.first() ?: "unknown"
}

class Features {
    static void run() {
        def counter = makeCounter()
        println counter()
        println counter()

        def v = new Vec2(x: 1, y: 2) + new Vec2(x: 3, y: 4)
        println v

        def meta = demoMetaProgramming()
        println meta

        println clamp(42, 0, 10)
        println firstName(name: "Alice Bobsson")

        // Trait usage.
        def g = new Vec2(x: 1, y: 1)
        println g.greetTo("v")

        // Ranges + collection methods.
        def evenSquares = (1..5).findAll { it % 2 == 0 }.collect { it * it }
        println evenSquares
    }
}
