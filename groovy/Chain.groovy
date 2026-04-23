package com.example

// Transitive chain via 3 static classes.

class ChainOrigin  { static String ORIGIN_VALUE  = "T1.origin" }         // T1.origin.def
class ChainMiddle  { static String MIDDLE_VALUE  = ChainOrigin.ORIGIN_VALUE }  // T1.middle.reexport
class ChainDeep    { static String VALUE_ALIAS   = ChainMiddle.MIDDLE_VALUE } // T1.deep.reexport
