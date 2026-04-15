$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$pidsFile = Join-Path $repoRoot '.dev-pids.json'

if (Test-Path $pidsFile) {
  $data = Get-Content $pidsFile | ConvertFrom-Json
  foreach ($name in @('backend', 'frontend')) {
    $pid = [int]$data.$name
    if ($pid -gt 0) {
      try {
        Stop-Process -Id $pid -Force -ErrorAction Stop
        Write-Host "Stopped $name PID=$pid"
      } catch {
        Write-Host "$name PID=$pid already stopped"
      }
    }
  }
  Remove-Item $pidsFile -Force
}

function Stop-PortProcess($port) {
  $connections = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
  if ($connections) {
    $pids = $connections | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($pid in $pids) {
      try {
        Stop-Process -Id $pid -Force -ErrorAction Stop
        Write-Host "Stopped PID=$pid on port $port"
      } catch {
        Write-Host "Could not stop PID=$pid on port $port"
      }
    }
  }
}

Stop-PortProcess 3000
Stop-PortProcess 8000
