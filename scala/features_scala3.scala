package scala3

// Scala 3 feature coverage: enum with parameters, opaque types, given/using,
// extension blocks, union types, inline defs. Parser-only fixture — no build
// required; imports may reference packages that aren't installed.

// --- Scala 3 enum with parameterized cases.
enum Shape3 {
  case Circle3(r: Double)
  case Square3(s: Double)

  def area: Double = this match {
    case Circle3(r) => math.Pi * r * r
    case Square3(s) => s * s
  }
}

// --- Opaque type with companion providing apply.
object UserIds {
  opaque type UserId = Int

  object UserId {
    def apply(raw: Int): UserId = raw
    extension (id: UserId) def value: Int = id
  }
}

// --- Given instance.
given intOrd: Ordering[Int] with {
  def compare(a: Int, b: Int): Int = a - b
}

// --- Function with a using clause (context parameter).
def maxOf[A](a: A, b: A)(using ord: Ordering[A]): A =
  if ord.gt(a, b) then a else b

// --- Extension block.
extension (s: String)
  def shout: String = s.toUpperCase + "!"

// --- Union type alias.
type IntOrString = Int | String

// --- Inline def with inline if.
inline def dbg[A](inline x: A): A =
  inline if true then x else x
