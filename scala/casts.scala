package com.example

import scala.util.Try

object Casts {
    class Base
    class Derived extends Base { def extra = "derived" }

    // 1. asInstanceOf — unchecked downcast.
    def unsafeDown(o: AnyRef): String = o.asInstanceOf[String]

    // 2. isInstanceOf — runtime type check.
    def isString(o: AnyRef): Boolean = o.isInstanceOf[String]

    // 3. Pattern match with type ascription.
    def describe(o: Any): String = o match {
        case s: String if s.length > 3 => s"long str $s"
        case s: String                 => s"short $s"
        case i: Int                    => s"int $i"
        case null                      => "null"
        case _                         => "other"
    }

    // 4. Numeric conversions.
    def numeric(): Unit = {
        val l: Long = 42L
        val i: Int = l.toInt
        val d: Double = i.toDouble
        println(s"$l $i $d")
    }

    // 5. Try-based parsing (safe cast from String).
    def parse(s: String): Option[Int] = Try(s.toInt).toOption

    // 6. Implicit conversion (deprecated but still recognised).
    implicit def intToString(n: Int): String = n.toString
    val s: String = 42   // uses implicit conversion

    def run(): Unit = {
        println(unsafeDown("hi"))
        println(isString("x"))
        println(describe(42))
        println(describe("a long one"))
        numeric()
        println(parse("123"))
        println(s)
    }
}
