param(
    [ValidateSet(
        "idle",
        "running",
        "waiting",
        "review",
        "failed",
        "waving",
        "jumping",
        "running-left",
        "running-right",
        "start",
        "health"
    )]
    [string]$Action = "failed",

    [int]$Duration = 1800,

    [string]$Python = $env:WANGZAI_PYTHON
)

if (-not $Python) {
    $Python = "python"
}

$Root = $PSScriptRoot
$Controller = Join-Path $Root "wangzai_pet_controller.py"
$Trigger = Join-Path $Root "pet_action.py"
$HealthUrl = "http://127.0.0.1:7777/health"

if ($Action -eq "start") {
    Start-Process -FilePath $Python -ArgumentList @($Controller) -WindowStyle Hidden
    Start-Sleep -Milliseconds 700
    Invoke-RestMethod -Uri $HealthUrl -Method Get
    exit
}

if ($Action -eq "health") {
    Invoke-RestMethod -Uri $HealthUrl -Method Get
    exit
}

& $Python $Trigger $Action $Duration
