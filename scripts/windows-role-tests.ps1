# Tests for role separation and the Flask CRUD module (isolated SQLite test DB).
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root
if (-not (Test-Path '.env')) { throw 'Run windows-setup.ps1 first.' }
Get-Content '.env' | ForEach-Object {
  $line = $_.Trim()
  if ($line -and -not $line.StartsWith('#') -and $line -match '^([^=]+)=(.*)$') {
    [Environment]::SetEnvironmentVariable($Matches[1].Trim(), $Matches[2], 'Process')
  }
}
Push-Location backend
try {
  & .\.venv\Scripts\python.exe -m pytest -q tests/test_flask_final.py tests/test_demo_accounts.py
  if ($LASTEXITCODE -ne 0) { throw 'Role/CRUD tests failed. Inspect the traceback.' }
} finally { Pop-Location }
