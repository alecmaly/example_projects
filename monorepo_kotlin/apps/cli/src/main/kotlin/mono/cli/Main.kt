package mono.cli

import mono.shared.User
import mono.shared.Util

fun main() = println(Util.formatUser(User(99, "cli-user")))
