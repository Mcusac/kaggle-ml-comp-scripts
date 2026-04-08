$ErrorActionPreference = "Stop"

function Assert-LastExitCode {
  param([string]$stepName)
  if ($LASTEXITCODE -ne 0) {
    throw "Step failed ($stepName). Exit code: $LASTEXITCODE"
  }
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$packageRoot = Resolve-Path (Join-Path $scriptDir "..\..\..")

$venvDir = Join-Path $packageRoot ".venv"
$activate = Join-Path $venvDir "Scripts\Activate.ps1"

Write-Host "Package root: $packageRoot"
Write-Host "Venv path:    $venvDir"

if (-not (Test-Path $activate)) {
  Write-Host "Creating venv..."
  try {
    py -3 -m venv $venvDir
    Assert-LastExitCode "py -3 -m venv"
  } catch {
    python -m venv $venvDir
    Assert-LastExitCode "python -m venv"
  }
}

Write-Host "Activating venv..."
. $activate

Write-Host "Upgrading pip..."
python -m pip install --upgrade pip
Assert-LastExitCode "pip upgrade"

Write-Host "Installing requirements-dev.txt..."
$reqDev = Join-Path $packageRoot "requirements-dev.txt"
python -m pip install -r $reqDev
Assert-LastExitCode "pip install requirements-dev.txt"

Write-Host "Done."

