package mono.web

// Ktor framework idioms: Application.module DSL, routing { get/post },
// call.respond, receive<>, ContentNegotiation, status pages, coroutines
// inside handlers, Serialization @Serializable data classes.

import io.ktor.http.*
import io.ktor.serialization.kotlinx.json.*
import io.ktor.server.application.*
import io.ktor.server.engine.*
import io.ktor.server.netty.*
import io.ktor.server.plugins.contentnegotiation.*
import io.ktor.server.plugins.statuspages.*
import io.ktor.server.request.*
import io.ktor.server.response.*
import io.ktor.server.routing.*
import kotlinx.coroutines.delay
import kotlinx.serialization.Serializable

@Serializable
data class KtorUser(val id: Int, val email: String, val name: String? = null)

@Serializable
data class KtorCreateUserReq(val email: String, val name: String? = null)

class UserRepositoryKtor {
    private val users = mutableMapOf(
        1 to KtorUser(1, "alice@example.com", "Alice"),
        2 to KtorUser(2, "bob@example.com", "Bob"),
    )
    private var nextId = 3

    suspend fun findById(id: Int): KtorUser? {
        delay(1) // simulate IO
        return users[id]
    }

    suspend fun create(req: KtorCreateUserReq): KtorUser {
        delay(1)
        val u = KtorUser(nextId++, req.email, req.name)
        users[u.id] = u
        return u
    }

    suspend fun all(limit: Int): List<KtorUser> {
        delay(1)
        return users.values.take(limit)
    }
}

class NotFoundException(msg: String) : RuntimeException(msg)

fun Application.userModule(repo: UserRepositoryKtor) {
    install(ContentNegotiation) {
        json()
    }
    install(StatusPages) {
        exception<NotFoundException> { call, cause ->
            call.respond(HttpStatusCode.NotFound, mapOf("error" to cause.message))
        }
        exception<Throwable> { call, cause ->
            call.respond(HttpStatusCode.InternalServerError, mapOf("error" to cause.message))
        }
    }

    routing {
        route("/api/users") {
            get {
                val limit = call.request.queryParameters["limit"]?.toIntOrNull() ?: 10
                call.respond(repo.all(limit))
            }

            get("/{id}") {
                val id = call.parameters["id"]?.toIntOrNull()
                    ?: return@get call.respond(HttpStatusCode.BadRequest, "bad id")
                val user = repo.findById(id) ?: throw NotFoundException("user $id")
                call.respond(user)
            }

            post {
                val req = call.receive<KtorCreateUserReq>()
                val user = repo.create(req)
                call.respond(HttpStatusCode.Created, user)
            }
        }

        get("/health") {
            call.respondText("ok")
        }
    }
}

fun runKtorServer() {
    val repo = UserRepositoryKtor()
    embeddedServer(Netty, port = 8080) {
        userModule(repo)
    }.start(wait = true)
}
