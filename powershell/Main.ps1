. .\Module1.ps1
. .\Module2.ps1
. .\Features.ps1
. .\Scopes.ps1

$global:GlobalVar = "I'm global in main"

function Main {
    $localVar = "I'm local to Main"
    Write-Host $global:GlobalVar
    Write-Host $localVar
    Write-Host "Imported constant: $script:MODULE2_CONSTANT"
    
    Function1
    Function2
    RecursiveFunction 5
    
    # Accessing module-level variables (reads)
    Write-Host "Module1 global: $script:MODULE1_GLOBAL"
    Write-Host "Module2 global: $script:MODULE2_GLOBAL"

    # Cross-script WRITE
    Set-Module1Global -Value "rotated-from-main"
    $script:MODULE2_GLOBAL = "rotated-directly"
    Write-Host "Module1 global after: $script:MODULE1_GLOBAL"
    Write-Host "Module2 global after: $script:MODULE2_GLOBAL"

    # Class usage
    $shape = [Shape]::new(2.5)
    Write-Host "Circle area: $($shape.Area())"

    # Error handling
    try { throw "boom" }
    catch { Write-Host "caught: $_" }
    finally { Write-Host "finally block" }

    # CmdletBinding, parameter sets, enum, ValidateSet, pipeline
    Invoke-FeatureDemo

    # Labeled scope test cases
    Invoke-ScopeDemo
    
    # Using a standard cmdlet
    $computerInfo = Get-ComputerInfo
    Write-Host "Operating System: $($computerInfo.OsName)"
}

function RecursiveFunction($n) {
    if ($n -le 0) {
        return
    }
    Write-Host "Recursion level: $n"
    RecursiveFunction ($n - 1)
}

Main