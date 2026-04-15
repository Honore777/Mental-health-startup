$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$logsDir = Join-Path $repoRoot 'logs'
if (-not (Test-Path $logsDir)) {
  New-Item -ItemType Directory -Path $logsDir | Out-Null
}

function Stop-PortProcess($port) {
  $connections = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
  if ($connections) {
    $pids = $connections | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($pid in $pids) {
      try {
        Stop-Process -Id $pid -Force -ErrorAction Stop
      } catch {
        Write-Host "Could not stop process $pid on port $port"
      }
    }
  }
}

# Ensure no stale servers are holding required ports.
Stop-PortProcess 3000
Stop-PortProcess 8000

$backendOut = Join-Path $logsDir 'backend-dev.out.log'
$backendErr = Join-Path $logsDir 'backend-dev.err.log'
$frontendOut = Join-Path $logsDir 'frontend-dev.out.log'
$frontendErr = Join-Path $logsDir 'frontend-dev.err.log'

$backendCmd = 'Set-Location "' + $repoRoot + '"; uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000'
$frontendCmd = 'Set-Location "' + $repoRoot + '"; npm --prefix frontend run dev -- -p 3000'

$backendProc = Start-Process -FilePath 'powershell' -ArgumentList '-NoProfile', '-Command', $backendCmd -PassThru -RedirectStandardOutput $backendOut -RedirectStandardError $backendErr
$frontendProc = Start-Process -FilePath 'powershell' -ArgumentList '-NoProfile', '-Command', $frontendCmd -PassThru -RedirectStandardOutput $frontendOut -RedirectStandardError $frontendErr

$pidsFile = Join-Path $repoRoot '.dev-pids.json'
@{
  backend = $backendProc.Id
  frontend = $frontendProc.Id
  startedAt = (Get-Date).ToString('o')
} | ConvertTo-Json | Set-Content -Path $pidsFile -Encoding UTF8

Write-Host "Started backend PID=$($backendProc.Id) and frontend PID=$($frontendProc.Id)"
Write-Host "Logs: $logsDir"
