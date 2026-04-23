package com.example

// 1. Single-name import.
import scala.collection.mutable.ArrayBuffer

// 2. Wildcard.
import scala.collection.mutable._

// 3. Grouped (braced) import.
import scala.util.{Try, Success, Failure}

// 4. Renamed (aliased).
import scala.math.{BigDecimal => BD}

// 5. Hiding.
import scala.collection.immutable.{List => _, _}

// 6. Package-relative import inside an object scope.
object Imports {
  import scala.concurrent.duration._

  def run(): Unit = {
    val buf: ArrayBuffer[Int] = ArrayBuffer(1, 2, 3)
    val m: HashMap[Int, String] = HashMap(1 -> "a")   // from wildcard
    val t: Try[Int] = Try(42)
    val bd: BD = BD(3.14)                              // via alias
    val d: FiniteDuration = 5.seconds                  // from inner import
    println(s"$buf $m $t $bd $d")

    t match {
      case Success(v) => println(s"ok $v")
      case Failure(e) => println(s"err ${e.getMessage}")
    }
  }
}
