// Root build file — applies conventions to every subproject.
plugins {
    id("java") apply false
}

subprojects {
    plugins.apply("java")

    repositories {
        mavenCentral()
    }

    extensions.configure<JavaPluginExtension> {
        toolchain {
            languageVersion.set(JavaLanguageVersion.of(21))
        }
    }
}
