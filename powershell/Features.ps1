# Enum
enum Priority {
    Low    = 1
    Medium = 5
    High   = 10
}

# Advanced function with CmdletBinding + parameter sets + ValidateSet.
function Invoke-Task {
    [CmdletBinding(DefaultParameterSetName = 'ByName')]
    param(
        [Parameter(Mandatory, ParameterSetName = 'ByName', Position = 0)]
        [ValidateNotNullOrEmpty()]
        [string] $Name,

        [Parameter(Mandatory, ParameterSetName = 'ById', Position = 0)]
        [int] $Id,

        [Parameter(Position = 1)]
        [Priority] $Priority = [Priority]::Medium,

        [ValidateSet('run', 'dry-run', 'explain')]
        [string] $Mode = 'run',

        [switch] $Force
    )

    process {
        switch ($PSCmdlet.ParameterSetName) {
            'ByName' { Write-Host "Invoke by name=$Name priority=$Priority mode=$Mode force=$Force" }
            'ById'   { Write-Host "Invoke by id=$Id priority=$Priority mode=$Mode force=$Force" }
        }
    }
}

# Pipeline-consuming function.
function Sum-Pipeline {
    [CmdletBinding()]
    param(
        [Parameter(ValueFromPipeline)]
        [int] $Number
    )
    begin { $acc = 0 }
    process { $acc += $Number }
    end { $acc }
}

function Invoke-FeatureDemo {
    Invoke-Task -Name "deploy" -Priority High -Mode dry-run -Force
    Invoke-Task -Id 42 -Priority Low
    Write-Host "pipe sum = $((1..5) | Sum-Pipeline)"

    # Hashtable + splatting
    $params = @{ Name = "hello"; Priority = [Priority]::Medium; Mode = 'explain' }
    Invoke-Task @params
}
