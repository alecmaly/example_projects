$script:MODULE1_GLOBAL = "I'm global in module1"

# Phase 1: PS5+ class
class Shape {
    [double] $R
    Shape([double]$r) { $this.R = $r }
    [double] Area() { return [Math]::PI * $this.R * $this.R }
}

function Set-Module1Global {
    param([string]$Value)
    $script:MODULE1_GLOBAL = $Value # cross-script WRITE target
}

function Function1 {
    $localVar = "I'm local to Function1"
    Write-Host "This is Function1 from Module1"
    Write-Host "Local var in Function1: $localVar"
    Write-Host "Accessing global: $script:MODULE1_GLOBAL"
}

# Demonstrate nested functions
function OuterFunction {
    $outerVar = "I'm in the outer function"
    
    function InnerFunction {
        $innerVar = "I'm in the inner function"
        Write-Host "Inner accessing outer: $outerVar"
        Write-Host "Inner local: $innerVar"
    }
    
    InnerFunction
    Write-Host "Outer local: $outerVar"
}