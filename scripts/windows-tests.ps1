# Run isolated Flask + SQLite tests. Does not modify persistent MySQL.
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root
Get-Content '.env' | ForEach-Object {
  $line = $_.Trim()
  if ($line -and -not $line.StartsWith('#') -and $line -match '^([^=]+)=(.*)$') {
    [Environment]::SetEnvironmentVariable($Matches[1].Trim(), $Matches[2], 'Process')
  }
}
Push-Location backend
try {
  & .\.venv\Scripts\python.exe -m pytest -q tests/test_flask_final.py tests/test_demo_accounts.py tests/test_health.py
  if ($LASTEXITCODE -ne 0) { throw 'Tests failed. Review output.' }
} finally { Pop-Location }
