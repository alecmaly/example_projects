# _ilspy_dump

Synthetic ILSpy-style decompilation fixture. No `*.csproj` / `*.sln` on purpose.
Exercises the patterns the extractor is likely to stumble on when handed raw
decompiler output:

- `extern alias`
- `[module: ...]` and `[assembly: ...]` attribute lines
- `[CompilerGenerated]` closure types: `<>c`, `<>c__DisplayClass0_0`
- `<Main>b__0_0` lambda names
- `<PrivateImplementationDetails>` with `$$method` helpers
- Nested DLL references — `CoreLib.dll` folder references `Shared.dll` folder

Directory layout intentionally mirrors "dump each DLL to its own folder":
```
CoreLib.dll/ — decompiled core library
Shared.dll/  — decompiled shared library referenced by CoreLib
```
