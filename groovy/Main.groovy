package com.example
class Greeter {
    String prefix = "hi"
    String greet(String name) { return prefix + " " + name }
}
class App {
    static void run() {
        new Greeter().greet("world")
    }
}
