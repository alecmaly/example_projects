package com.example

// Labeled scope test cases for Scala. See SCOPE_TEST_SPEC.md.

import scala.collection.mutable

// Import with alias — used for S09.
import com.example.scopes_ns.{Widget => NsWidget}    // S09.def

object Scopes {
  var moduleVar: String = "mod-initial"              // S04.def

  def s01Local(): Unit = {
    val localA = "S01.local"                         // S01.def
    println(localA)                                  // S01.read
  }

  def s02ClosureRead(): Unit = {
    val outerA = "S02.outer"                         // S02.outer.def
    val inner = () => println(outerA)                // S02.inner.read
    inner()
  }

  def s03ClosureWrite(): Int = {
    var counter = 0                                  // S03.outer.def
    val bump = () => counter += 1                    // S03.inner.write
    bump(); bump()
    counter                                          // S03.outer.read
  }

  def s05SameModuleWrite(): Unit = {
    moduleVar = "rotated"                            // S05.write
    println(moduleVar)                               // S05.read
  }

  def s08Shadowing(): Unit = {
    val moduleVar = "shadowed"                       // S08.shadow.def
    println(moduleVar)                               // S08.shadow.read
  }

  def s09AliasedImport(): Unit = {
    val w = new NsWidget("via-alias")                // S09.read
    println(w.label)
  }

  class Base(val x: Int) {                           // S11.instance.def
    def readInstance(x: Int): Int = x + this.x       // S11.param.read + S11.instance.read
  }

  object Base {                                      // S12.static.def (companion)
    var staticX: Int = 1
  }

  class Derived extends Base(5) {
    def readInherited: Int = Base.staticX            // S13.derived.read
  }

  def s14Qualified(): String = new NsWidget("hi").label   // S14.read

  def run(): Unit = {
    s01Local()
    s02ClosureRead()
    println(s03ClosureWrite())
    s05SameModuleWrite()
    s08Shadowing()
    s09AliasedImport()
    println(new Base(42).readInstance(100))
    println((new Derived).readInherited)
    println(s14Qualified())
  }
}
