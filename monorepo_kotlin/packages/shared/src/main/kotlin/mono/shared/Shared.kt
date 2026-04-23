package mono.shared

data class User(val id: Int, val name: String)

enum class Role { Admin, User, Guest }

val DEFAULT_ROLE = Role.User

object Util {
    fun formatUser(u: User): String = "${u.id}:${u.name}"
    fun hello(msg: String): String = "hello, $msg"
}

// Top-level extension function — Kotlin-specific shape.
fun String.quoted(): String = "\"$this\""
