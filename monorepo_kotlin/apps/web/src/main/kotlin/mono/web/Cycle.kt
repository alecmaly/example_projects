package mono.web

// Kotlin class-class cycle — same package, no special handling needed.

class CycleA(val name: String) {
    var child: CycleB? = null                 // C1.a.type_ref → CycleB

    fun spawnBravo(): CycleB = CycleB("$name/b")
    fun describe(): String    = "CycleA($name)"

    companion object {
        fun kickOff(): String {
            val a = CycleA("root")
            val b = a.spawnBravo()
            return b.bounceToAlpha()
        }
    }
}

class CycleB(val tag: String) {
    var owner: CycleA? = null                 // C1.b.type_ref → CycleA

    fun bounceToAlpha(): String = CycleA("bounce-from-$tag").describe()
}
