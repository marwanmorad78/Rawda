$pgCtl = 'C:\Program Files\PostgreSQL\16\bin\pg_ctl.exe'
$dataDir = Join-Path $PSScriptRoot '..\.local-postgres\data'

if (-not (Test-Path $dataDir)) {
    Write-Error "Local PostgreSQL data directory not found: $dataDir"
    exit 1
}

& $pgCtl -D $dataDir stop
