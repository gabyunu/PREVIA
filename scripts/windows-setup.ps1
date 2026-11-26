# PREVIA Windows 11 - First-time local setup. Run from ANY PowerShell location:
#   Set-ExecutionPolicy -Scope Process Bypass
#   .\scripts\windows-setup.ps1
# Requires: Git, Docker Desktop (Linux containers), uv, Node 22.22.3+/24.15+/26+.
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root

function Require-Program([string]$name) {
  if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
    throw "Missing required program: $name. See docs/WINDOWS_11.md"
  }
}
foreach ($name in @('git', 'docker', 'uv', 'node', 'npm.cmd')) { Require-Program $name }

$nodeVersion = (& node --version).TrimStart('v').Split('.')
$major = [int]$nodeVersion[0]; $minor = [int]$nodeVersion[1]; $patch = [int]$nodeVersion[2]
$nodeOk = ($major -eq 22 -and ($minor -gt 22 -or ($minor -eq 22 -and $patch -ge 3))) -or
          ($major -eq 24 -and $minor -ge 15) -or $major -eq 26
if (-not $nodeOk) { throw "Your Node.js version is not supported by this Angular project. Install Node 26 LTS." }

& docker info --format '{{.ServerVersion}}' | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Docker Desktop is not running. Start Docker Desktop first.' }

$envfile = Join-Path $root '.env'
if (-not (Test-Path $envfile)) {
  $template = Get-Content (Join-Path $root '.env.example') -Raw
  foreach ($name in @('MYSQL_PASSWORD', 'MYSQL_ROOT_PASSWORD', 'AUTH_HMAC_KEY')) {
    $bytes = New-Object byte[] 32
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try { $rng.GetBytes($bytes) } finally { $rng.Dispose() }
    $secret = [BitConverter]::ToString($bytes).Replace('-', '').ToLowerInvariant()
    $template = [regex]::Replace($template, "(?m)^$name=.*$", "${name}=$secret")
  }
  [System.IO.File]::WriteAllText($envfile, $template, (New-Object System.Text.UTF8Encoding($false)))
  Write-Host 'Created local .env with random credentials. Do not commit this file.'
}

Get-Content $envfile | ForEach-Object {
  $line = $_.Trim()
  if ($line -and -not $line.StartsWith('#') -and $line -match '^([^=]+)=(.*)$') {
    [Environment]::SetEnvironmentVariable($Matches[1].Trim(), $Matches[2], 'Process')
  }
}

Write-Host 'Starting MySQL and Mailpit...'
& docker compose up -d --wait mysql mailpit
if ($LASTEXITCODE -ne 0) { throw 'Could not start Docker services.' }

& uv python install 3.14
if ($LASTEXITCODE -ne 0) { throw 'Could not install Python 3.14.' }
& uv venv --python 3.14 backend/.venv
if ($LASTEXITCODE -ne 0) { throw 'Could not create the Python environment.' }
$python = Join-Path $root 'backend\.venv\Scripts\python.exe'
& uv pip install --python $python -r backend/requirements-flask.txt
if ($LASTEXITCODE -ne 0) { throw 'Python dependencies could not be installed.' }
& uv pip install --python $python --no-deps -e backend
if ($LASTEXITCODE -ne 0) { throw 'PREVIA backend could not be installed.' }

Push-Location backend
try {
  & $python -m alembic upgrade head
  if ($LASTEXITCODE -ne 0) { throw 'Database migration failed.' }
  & $python -m app.db.seed
  if ($LASTEXITCODE -ne 0) { throw 'Initial curriculum seed failed.' }
  & $python -m app.db.demo_period
  if ($LASTEXITCODE -ne 0) { throw 'Demo period setup failed.' }
  & $python -m app.db.demo_accounts --confirm-local-test
  if ($LASTEXITCODE -ne 0) { throw 'Demo account provisioning failed.' }
} finally { Pop-Location }

Push-Location frontend
try {
  & npm.cmd ci
  if ($LASTEXITCODE -ne 0) { throw 'Angular dependency installation failed.' }
  & npm.cmd run build
  if ($LASTEXITCODE -ne 0) { throw 'Angular build failed.' }
} finally { Pop-Location }

Write-Host ''
Write-Host 'Setup finished. Open TWO PowerShell terminals:' -ForegroundColor Green
Write-Host '  .\scripts\windows-start-api.ps1'
Write-Host '  .\scripts\windows-start-frontend.ps1'
Write-Host '  PREVIA: http://127.0.0.1:4200'
Write-Host '  Flask API docs: http://127.0.0.1:8000/docs'
Write-Host '  Mailpit: http://127.0.0.1:8025'
