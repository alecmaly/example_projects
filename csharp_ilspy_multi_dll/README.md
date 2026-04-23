# csharp_ilspy_multi_dll

Simulates an **ILSpy decompile of a multi-DLL product** (the shape of the
SharePoint SE / Exchange SE `decompiled/` dumps):

- Each DLL lives in its own folder named after the assembly.
- Each folder has its own SDK-style `.csproj` (plus an `AssemblyInfo.cs`).
- A top-level `CsharpIlspyMultiDll.sln` ties the 6 projects together.
- A top-level `Directory.Build.props` holds shared language settings.
- Cross-DLL references use the two shapes ILSpy actually emits:
  - Bare `<Reference Include="Microsoft.Demo.Data.Common" />` (name-only,
    no `HintPath`, no `ProjectReference`) — the tool must resolve this to
    the sibling project via the `.sln`.
  - One `<ProjectReference Include="..\...\X.csproj" />` in the Handler
    project to exercise the easier resolution path.

## Layout

```
CsharpIlspyMultiDll.sln
Directory.Build.props
Microsoft.Demo.Data.Common/           # leaf — no deps
Microsoft.Demo.Data.Storage/          # -> Data.Common
Microsoft.Demo.HttpProxy.Routing/     # -> Data.Storage, Data.Common
Microsoft.Demo.HttpProxy.Handler/     # -> Routing (ProjectReference), Data.Common   [legacy ILSpy style]
Microsoft.Demo.HttpProxy.ModernHandler/ # -> Routing, Data.Common                     [modern ILSpy style]
Microsoft.Demo.FrontEnd/              # -> Handler, ModernHandler, Data.Common  (Exe)
```

## What the fixture exercises

### 1. Two cross-DLL call chains (both 5 hops across 5 assemblies)

Legacy-style stack (via `Handler`):
```
FrontEnd.Program.Main
  -> HttpProxy.Handler.Handler.HandleRequest
       -> HttpProxy.Routing.Router.Route
            -> Data.Storage.Repository.Load
                 -> Data.Common.Utilities.Normalize
```

Modern-style stack (via `ModernHandler`):
```
FrontEnd.Program.Main
  -> HttpProxy.ModernHandler.ModernHandler.HandleRequest
       -> HttpProxy.Routing.Router.Route
            -> Data.Storage.Repository.Load
                 -> Data.Common.Utilities.Normalize
```

Both converge at `Router.Route`. The scanner, when pointed at the repo root,
should stitch both stacks end-to-end across all assemblies, and resolve the
fan-in at `Router.Route` from the two independent Handler DLLs.

### 2. Cross-DLL state-variable R/W on `Microsoft.Demo.Data.Common.Globals`

- `RequestCount` — written in `Utilities.Normalize` (Common), read in
  `Repository.Load` (Storage), reset in `Repository.Reset` (Storage), read
  again in `Program.Main` (FrontEnd).
- `LastError` — written in `Utilities.Normalize` (Common) and
  `Repository.Load` (Storage), read in `Router.Route` (Routing),
  `Handler.HandleRequest` (Handler), and `ModernHandler.HandleRequest`
  (ModernHandler).

### 3. Reference-resolution shapes (both should resolve to the same sibling)

- Name-only `<Reference Include="Microsoft.Demo.Data.Common" />`
- Relative `<ProjectReference Include="..\...\...csproj" />`

### 4. Both ILSpy output flavors, side by side

Checked against the actual SharePoint SE / Exchange SE dumps: **modern
ILSpy rewrites lambdas and closures back into source form by default**, so
the angle-bracket names are mostly absent from those dumps. But older
output, or output with transformations disabled / unable-to-match, still
emits the raw compiler-generated names. Both flavors are represented here:

| Project | Style | Notes |
|---|---|---|
| `Microsoft.Demo.HttpProxy.Handler` | **Raw / legacy ILSpy** | `<>c__DisplayClass0_0` compiler-generated class, `<HandleRequest>b__0` lambda method name, `CS$<>8__locals0` temp. **Not legal C#** — parse-only. |
| `Microsoft.Demo.HttpProxy.ModernHandler` | **Modern ILSpy (clean)** | Matches what SharePoint SE / Exchange SE decompile output actually looks like: `=>` lambda, `.Where(...).Select(...).ToArray()`, file-scoped namespace. Legal C#. |

Plus the lighter ILSpy-isms shared across both:

- `[assembly: ...]` / `[module: ...]` attribute lines
- `GenerateAssemblyInfo=False` + explicit `AssemblyInfo.cs`
- `RootNamespace` left empty
- `// ILSpy-generated` header banner

(The heavier raw-ILSpy edge cases — `extern alias`, `<>c`, `<PrivateImplementationDetails>`, `AsyncStateMachine` — live in the sibling fixture `_ilspy_dump/`, which deliberately has no `.csproj`/`.sln`.)

## How to use

Point the scanner at this directory as the project root and verify:

- All **6** projects are discovered.
- Both call stacks join end-to-end (5 hops each, across 5 DLLs) with no
  broken edges at assembly boundaries.
- Fan-in at `Router.Route` is detected from both `Handler` and
  `ModernHandler`.
- R/W on `Globals.RequestCount` and `Globals.LastError` is reported across
  every DLL that touches them.
- Both `<Reference>` (name-only) and `<ProjectReference>` (path) resolve
  to the same sibling project, not to an unresolved external dep.
- Parser doesn't choke on the raw ILSpy angle-bracket identifiers in
  `Handler.cs` — and extracts the same semantic edges as it does from the
  clean lambda form in `ModernHandler.cs`.

> Note: `Handler.cs` contains `<>c__DisplayClass0_0` / `<HandleRequest>b__0`
> identifiers that are raw ILSpy output and **not legal C#**. This fixture
> is intended for static analysis, not `dotnet build` — same contract as
> `_ilspy_dump/`.
