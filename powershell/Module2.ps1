$script:MODULE2_CONSTANT = "I'm a constant in module2"
$script:MODULE2_GLOBAL = "I'm global in module2"

function Function2 {
    Write-Host "This is Function2 from Module2"
    Write-Host "Accessing module constant: $script:MODULE2_CONSTANT"
    InternalFunction
}

function InternalFunction {
    $internalVar = "I'm local to InternalFunction"
    Write-Host "This is an internal function in Module2"
    Write-Host "Internal var: $internalVar"
    Write-Host "Accessing global: $script:MODULE2_GLOBAL"
}