# csharp_multi_dll

Simulates 3 DLLs delivered to separate directories with **no shared `.sln` / `.csproj`**.
Each subfolder is a standalone "artifact" that references symbols in the others by
namespace name. The extractor must resolve `A.Types.Widget` from `C/Consumer.cs` even
though the LSP cannot boot a single project rooted here.

Layout:
- `A/A.cs`         — namespace `A.Types`, defines `Widget`, static `Registry.Count`
- `B/B.cs`         — namespace `B.Logic`, references `A.Types.Widget`, writes `A.Types.Registry.Count`
- `C/Consumer.cs`  — namespace `C.App`, references both `A.Types.Widget` and `B.Logic.Processor`

State-var R+W is deliberately **cross-directory**: `A.Types.Registry.Count` is
read in `A/`, written in `B/`, read again in `C/`.
