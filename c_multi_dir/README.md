# c_multi_dir

C fixture whose headers and sources are in **different directories** and there is
no Makefile / CMakeLists / compile_commands.json. Forces the extractor's C
indexer to reconcile cross-directory includes and cross-TU externs by path
heuristics rather than build-system intel.

Layout:
```
lib/include/libfoo.h   — public API + function-like macros
lib/src/libfoo.c       — defines globals, writes them
app/main.c             — includes via relative `../lib/include`, reads+writes globals
```
