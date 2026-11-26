# Run from any PowerShell directory after the original PREVIA setup.
# Creates two test identities with role separation; no fixed passwords.
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root
if (-not (Test-Path '.env')) { throw 'Missing .env. First run .\scripts\windows-setup.ps1.' }
Get-Content '.env' | ForEach-Object {
  $line = $_.Trim()
  if ($line -and -not $line.StartsWith('#') -and $line -match '^([^=]+)=(.*)$') {
    [Environment]::SetEnvironmentVariable($Matches[1].Trim(), $Matches[2], 'Process')
  }
}
& docker compose up -d --wait mysql mailpit
if ($LASTEXITCODE -ne 0) { throw 'MySQL or Mailpit could not start.' }
Push-Location backend
try {
  & .\.venv\Scripts\python.exe -m app.db.demo_accounts --confirm-local-test
  if ($LASTEXITCODE -ne 0) { throw 'Could not provision demo accounts; do not proceed.' }
} finally { Pop-Location }
