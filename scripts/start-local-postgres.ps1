$pgCtl = 'C:\Program Files\PostgreSQL\16\bin\pg_ctl.exe'
$dataDir = Join-Path $PSScriptRoot '..\.local-postgres\data'
$logFile = Join-Path $PSScriptRoot '..\.local-postgres\postgres.log'

if (-not (Test-Path $dataDir)) {
    Write-Error "Local PostgreSQL data directory not found: $dataDir"
    exit 1
}

& $pgCtl -D $dataDir -l $logFile -o "-p 5433" start
