# 1. Dot-source — executes the file in current scope, sharing variables/fns.
. .\Module1.ps1

# 2. Import-Module — loads a module, respects ExportedFunctions.
# Import-Module -Name .\MyModule.psd1          # shape-only

# 3. Import-Module -Prefix — prepends noun prefix to every cmdlet
#    (PowerShell's closest analogue to a per-import alias).
# Import-Module AzureRM -Prefix Az             # shape-only

# 4. using module — declarative module import, enables class/enum usage
#    from the imported module (PS5+).
# using module .\MyModule.psd1                 # shape-only

# 5. using namespace — imports a .NET namespace for type shorthand.
using namespace System.Collections.Generic

# 6. $env: — "import" an environment variable into the session.
$env:APP_ENV = "dev"

# 7. $Global: — explicit cross-session global. Exercises
#    PowerShellExtractor.normalize_identifier's scope-prefix stripping.
$Global:GLOBAL_IMPORT_VALUE = "G.imports"

# 8. ${Global:...} brace form — same semantics as $Global:X, different
#    surface syntax. Both should normalize to the same canonical name
#    after the extractor strips ``$``, braces, and scope prefix.
${Global:BRACED_IMPORT_VALUE} = "G.braced.imports"

function Invoke-ImportsDemo {
    $list = [List[int]]::new()         # via `using namespace`
    $list.Add(1); $list.Add(2)
    Write-Host "list=$($list -join ',')"
    Write-Host "env=$env:APP_ENV"
    Write-Host "global=$Global:GLOBAL_IMPORT_VALUE"
    Write-Host "braced=${Global:BRACED_IMPORT_VALUE}"
    Function1                          # via dot-source of Module1.ps1
}
