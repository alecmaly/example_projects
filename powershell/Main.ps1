. .\Module1.ps1
. .\Module2.ps1

$global:GlobalVar = "I'm global in main"

function Main {
    $localVar = "I'm local to Main"
    Write-Host $global:GlobalVar
    Write-Host $localVar
    Write-Host "Imported constant: $script:MODULE2_CONSTANT"
    
    Function1
    Function2
    RecursiveFunction 5
    
    # Accessing module-level variables
    Write-Host "Module1 global: $script:MODULE1_GLOBAL"
    Write-Host "Module2 global: $script:MODULE2_GLOBAL"
    
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