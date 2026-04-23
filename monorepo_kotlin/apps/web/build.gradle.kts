plugins { application }

dependencies {
    implementation(project(":packages:shared"))
    implementation(project(":packages:utils"))
}

application { mainClass.set("mono.web.MainKt") }
