package com.example

import scala.concurrent.{Future, ExecutionContext, Await}
import scala.concurrent.duration._

// Scala feature coverage: case classes, sealed traits + pattern match,
// traits with default methods, implicits, for-comprehensions, Option,
// Either, Future.

// --- sealed trait hierarchy = ADT.
sealed trait Shape
case class Circle(r: Double)                       extends Shape
case class Square(side: Double)                    extends Shape
case class Rectangle(w: Double, h: Double)         extends Shape

object Shape {
  def area(s: Shape): Double = s match {
    case Circle(r)         => math.Pi * r * r
    case Square(s)         => s * s
    case Rectangle(w, h)   => w * h
  }
}

// --- trait with default method.
trait Greeter[A] {
  def greet(a: A): String
  def shout(a: A): String = greet(a).toUpperCase
}

object Greeter {
  implicit val stringGreeter: Greeter[String] = new Greeter[String] {
    def greet(s: String) = s"hello, $s"
  }
  implicit val intGreeter: Greeter[Int] = new Greeter[Int] {
    def greet(n: Int) = s"number $n"
  }
  def greet[A](a: A)(implicit g: Greeter[A]): String = g.greet(a)
}

// --- concrete class overriding a trait's default method.
abstract class BaseGreeter[A] extends Greeter[A] {
  override def shout(a: A): String = "[!] " + greet(a).toUpperCase
}

class LoudStringGreeter extends BaseGreeter[String] {
  override def greet(a: String): String = s"hello, $a"
}

// --- implicit class / extension method.
object Implicits {
  implicit class StringOps(val s: String) extends AnyVal {
    def quoted: String = "\"" + s + "\""
  }
}

// --- Option + Either + for-comprehension.
object Optionals {
  def parsePort(s: String): Option[Int] =
    try Some(s.toInt) catch { case _: Throwable => None }

  def parsePair(a: String, b: String): Either[String, (Int, Int)] =
    for {
      x <- parsePort(a).toRight(s"bad: $a")
      y <- parsePort(b).toRight(s"bad: $b")
    } yield (x, y)
}

// --- Future + ExecutionContext.
object Async {
  def compute(x: Int)(implicit ec: ExecutionContext): Future[Int] =
    Future { Thread.sleep(5); x * x }
}

object Features {
  import Implicits.StringOps
  def run(): Unit = {
    println(s"area circle=${Shape.area(Circle(2))}")
    println(Greeter.greet("world"))
    println(Greeter.greet(42))
    println("hello".quoted)
    println(Optionals.parsePort("8080"))
    println(Optionals.parsePair("1", "2"))

    implicit val ec: ExecutionContext = ExecutionContext.global
    val f = for {
      a <- Async.compute(3)
      b <- Async.compute(4)
    } yield a + b
    println(s"async sum = ${Await.result(f, 1.second)}")
  }
}
