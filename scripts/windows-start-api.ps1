$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root
if (-not (Test-Path '.env')) { throw 'Run .\scripts\windows-setup.ps1 first.' }
Get-Content '.env' | ForEach-Object {
  $line = $_.Trim()
  if ($line -and -not $line.StartsWith('#') -and $line -match '^([^=]+)=(.*)$') {
    [Environment]::SetEnvironmentVariable($Matches[1].Trim(), $Matches[2], 'Process')
  }
}
& docker compose up -d mysql mailpit
if ($LASTEXITCODE -ne 0) { throw 'Docker failed.' }
Set-Location backend
& .\.venv\Scripts\python.exe -m flask --app app.flask_api:app run --host 127.0.0.1 --port 8000
