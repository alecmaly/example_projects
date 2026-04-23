plugins {
    kotlin("jvm") version "1.9.23" apply false
}

subprojects {
    plugins.apply("org.jetbrains.kotlin.jvm")
    repositories { mavenCentral() }
}
