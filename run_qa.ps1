<#
Run the QA engine from the repository root or any working directory.
Usage examples:
  PowerShell (from any folder):
    & "E:/My Program/GovSync/run_qa.ps1" -Offscreen
  Or from the repo root:
    cd "E:\My Program\GovSync"; & .\run_qa.ps1
#>
param(
    [switch]$Offscreen
)

# Allow running in environments with restricted execution policy if already set by the user
if ($PSVersionTable -and $PSVersionTable.PSEdition) {
    # Best-effort activate virtualenv if present
    $activate = Join-Path $PSScriptRoot ".venv/Scripts/Activate.ps1"
    if (Test-Path $activate) {
        try { & $activate } catch { }
    }
}

if ($Offscreen) { $env:QT_QPA_PLATFORM = 'offscreen' }

$python = Join-Path $PSScriptRoot ".venv/Scripts/python.exe"
$runner = Join-Path $PSScriptRoot "tools/qa_engine/run.py"
$logdir = Join-Path $PSScriptRoot "qa_output/logs"
if (-not (Test-Path $logdir)) { New-Item -ItemType Directory -Path $logdir | Out-Null }
$timestamp = (Get-Date).ToString('yyyyMMdd_HHmmss')
$log = Join-Path $logdir "qa_run_$timestamp.log"

if (-not (Test-Path $python)) {
    Write-Error "Python executable not found at $python. Activate your venv or adjust the script."; exit 2
}
if (-not (Test-Path $runner)) {
    Write-Error "Runner not found at $runner"; exit 2
}

Write-Output "Running QA engine (offscreen=$Offscreen)"
& $python $runner 2>&1 | Tee-Object -FilePath $log

if ($LASTEXITCODE -ne 0) { Write-Error "QA runner exited with code $LASTEXITCODE"; exit $LASTEXITCODE }
Write-Output "QA run completed. Logs: $log"