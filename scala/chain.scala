package com.example.chain

// T1 transitive chain (flat scala — 3 package-level objects).
object Origin { val ORIGIN_VALUE: String = "T1.origin" }        // T1.origin.def

object Middle { val MIDDLE_VALUE: String = Origin.ORIGIN_VALUE } // T1.middle.reexport

object Deep   { val VALUE_ALIAS: String = Middle.MIDDLE_VALUE }  // T1.deep.reexport
