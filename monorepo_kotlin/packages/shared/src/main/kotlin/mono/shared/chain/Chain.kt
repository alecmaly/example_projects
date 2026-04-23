package mono.shared.chain

// T1.origin — defined here.
object Origin {
    const val ORIGIN_VALUE: String = "T1.origin"                 // T1.origin.def
}

// T1.middle — re-exposes Origin via its own constant.
object Middle {
    const val MIDDLE_VALUE: String = Origin.ORIGIN_VALUE         // T1.middle.reexport
}

// T1.deep — renamed alias at the third level.
object Deep {
    const val VALUE_ALIAS: String = Middle.MIDDLE_VALUE          // T1.deep.reexport
}

// Extra: `typealias` as another re-export shape.
typealias AliasedOrigin = Origin
