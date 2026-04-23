# _jadx_dump

Synthetic JADX output fixture. Mirrors what you get when decompiling an APK
without its Gradle project:

- No `build.gradle` / `settings.gradle` / `AndroidManifest.xml`
- Directory layout matches the decompiled package path
  (`com/example/app/...`, `com/example/lib/...`)
- Synthetic inner classes (`$1`, `$Lambda$0`, `R$layout`)
- Obfuscated single-letter names (`a.java`, `b.java`) that reference each other
- Cross-package references across the two artifact directories
