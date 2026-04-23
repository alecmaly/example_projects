# PowerShell cast catalogue.

# 1. Type-accelerator prefix cast.
function Cast-TypeAccelerator {
    [int]$i = [int]"42"                    # string → int
    [double]$d = [double]"3.14"
    [datetime]$t = [datetime]"2024-01-01"
    Write-Host "$i $d $t"
}

# 2. -as operator (returns $null on failure).
function Cast-AsOperator {
    $n = "42" -as [int]
    $fail = "hi" -as [int]                 # $null
    Write-Host "n=$n fail=$($fail -eq $null)"
}

# 3. ::Parse / ::TryParse — .NET-style parsing.
function Cast-Parse {
    $n = [int]::Parse("123")
    [int]$out = 0
    $ok = [int]::TryParse("456", [ref]$out)
    Write-Host "parsed=$n tryparse=$out ok=$ok"
}

# 4. [type]::new() — constructor-style cast.
function Cast-CtorStyle {
    $sb = [System.Text.StringBuilder]::new("hello")
    $null = $sb.Append(" world")
    Write-Host $sb.ToString()
}

# 5. Format operator -f.
function Cast-Format {
    $s = "{0:N2}" -f 3.14159
    Write-Host "formatted=$s"
}

# 6. Enum cast.
enum Color { Red; Green; Blue }
function Cast-Enum {
    $c = [Color]"Red"
    Write-Host "enum=$c int=$([int]$c)"
}

# 7. PSCustomObject / pstypenames — tagging a hashtable with a class-like type.
function Cast-PSCustom {
    $obj = [PSCustomObject]@{ Name = "alice"; Age = 30 }
    $obj.PSTypeNames.Insert(0, 'My.User')
    Write-Host $obj.Name
}

function Invoke-CastsDemo {
    Cast-TypeAccelerator
    Cast-AsOperator
    Cast-Parse
    Cast-CtorStyle
    Cast-Format
    Cast-Enum
    Cast-PSCustom
}
