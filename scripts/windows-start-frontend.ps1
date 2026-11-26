$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
Set-Location (Join-Path $root 'frontend')
& npm.cmd start
