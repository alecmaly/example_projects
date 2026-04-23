package mono.shared

// Cross-package mutable state exercised from app/web.
var SharedStatus: String = "initial"

interface ShapeShared {
    val name: String
    fun area(): Double
}

data class CircleShape(val r: Double) : ShapeShared {
    override val name = "Circle"
    override fun area() = Math.PI * r * r
}

fun describeClass(obj: Any): String = obj::class.simpleName ?: "?"
