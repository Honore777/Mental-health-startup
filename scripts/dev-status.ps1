$repoRoot = Split-Path -Parent $PSScriptRoot
$pidsFile = Join-Path $repoRoot '.dev-pids.json'

if (Test-Path $pidsFile) {
  $data = Get-Content $pidsFile | ConvertFrom-Json
  Write-Host "Started at: $($data.startedAt)"
  foreach ($name in @('backend', 'frontend')) {
    $pid = [int]$data.$name
    $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
    if ($proc) {
      Write-Host "$name: running (PID=$pid)"
    } else {
      Write-Host "$name: not running (PID=$pid)"
    }
  }
} else {
  Write-Host "No .dev-pids.json found."
}

$ports = @(3000, 8000)
foreach ($port in $ports) {
  $connections = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
  if ($connections) {
    $pids = ($connections | Select-Object -ExpandProperty OwningProcess -Unique) -join ', '
    Write-Host "Port $port listening (PID(s): $pids)"
  } else {
    Write-Host "Port $port not listening"
  }
}
