# Labeled scope test cases for PowerShell. See SCOPE_TEST_SPEC.md at repo root.
# N/A for PowerShell: S09 (no aliased import for variables; Import-Module -Prefix
# is a command-rename mechanism), S10 (no re-export).

# ---------------------------------------------------- S04 def / S05 write target
$script:MODULE_VAR = "mod-initial"           # S04.def

function S01-Local {
    $localA = "S01.local"                        # S01.def
    Write-Host $localA                           # S01.read
}

function S02-ClosureRead {
    $outerA = "S02.outer"                        # S02.outer.def
    $inner = { Write-Host $outerA }.GetNewClosure()  # S02.inner.read
    & $inner
}

function S03-ClosureWrite {
    $counter = [ref] 0                           # S03.outer.def — [ref] gives scriptblock mutation
    $bump = { param($c) $c.Value++ }
    & $bump $counter; & $bump $counter           # S03.inner.write (via [ref])
    return $counter.Value                        # S03.outer.read
}

function S05-SameModuleWrite {
    $script:MODULE_VAR = "rotated"               # S05.write
    Write-Host $script:MODULE_VAR                # S05.read
}

function S06-CrossRead {
    return $script:MODULE1_GLOBAL                # S06.read — defined in Module1.ps1
}

function S07-CrossWrite {
    Set-Module1Global -Value "S07"               # S07.write (indirect via helper)
}

function S08-Shadowing {
    $MODULE_VAR = "shadowed"                     # S08.shadow.def — local shadows $script:
    Write-Host $MODULE_VAR                       # S08.shadow.read
}

# S11 / S12 / S13 — class (PS5+).
class ScopeBase {
    static [int] $StaticX = 1                    # S12.static.def / S13.base.def
    [int] $X                                     # S11.instance.def

    ScopeBase([int]$x) { $this.X = $x }

    [int] ReadInstance([int] $x) {
        return $x + $this.X                      # S11.param.read + S11.instance.read
    }
}

class ScopeDerived : ScopeBase {
    ScopeDerived() : base(5) {}
    [int] ReadInherited() {
        return [ScopeBase]::StaticX              # S13.derived.read
    }
    # Method override — same signature as ScopeBase.ReadInstance.
    # PowerShell has no `override` keyword; subclass signature match
    # replaces the base method.
    [int] ReadInstance([int] $x) {
        return ([ScopeBase]$this).ReadInstance($x) * 10   # call base + augment
    }
}

function Invoke-ScopeDemo {
    S01-Local
    S02-ClosureRead
    Write-Host "counter=$(S03-ClosureWrite)"
    S05-SameModuleWrite
    Write-Host "S06: $(S06-CrossRead)"
    S07-CrossWrite
    S08-Shadowing
    Write-Host "S11: $([ScopeBase]::new(42).ReadInstance(100))"
    Write-Host "S13: $([ScopeDerived]::new().ReadInherited())"
}
