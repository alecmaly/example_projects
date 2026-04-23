package com.example
class Greeter(val prefix: String) {
  def greet(name: String): String = s"$prefix $name"
}
object App extends Greeter("hi") {
  def main(args: Array[String]): Unit = println(greet("world"))
}
