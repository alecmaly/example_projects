plugins { application }
dependencies { implementation(project(":packages:shared")) }
application { mainClass.set("mono.cli.MainKt") }
