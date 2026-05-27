$ErrorActionPreference = "Stop"

$projectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$mariadbRoot = "C:\Program Files\MariaDB 12.2"
$mysqld = Join-Path $mariadbRoot "bin\mysqld.exe"
$dataDir = Join-Path $projectRoot ".local-mariadb\data"
$defaultsFile = Join-Path $dataDir "my.ini"
$outLog = Join-Path $projectRoot ".local-mariadb\mariadb.out.log"
$errLog = Join-Path $projectRoot ".local-mariadb\mariadb.err.log"

if (-not (Test-Path $mysqld)) {
    throw "MariaDB server was not found at $mysqld"
}

if (-not (Test-Path $defaultsFile)) {
    throw "MariaDB data directory was not initialized at $dataDir"
}

$alreadyRunning = Get-Process -ErrorAction SilentlyContinue |
    Where-Object { $_.ProcessName -eq "mysqld" -and $_.Path -eq $mysqld }

if ($alreadyRunning) {
    "MariaDB is already running. PID=$($alreadyRunning.Id -join ',')"
    exit 0
}

$process = Start-Process `
    -FilePath $mysqld `
    -ArgumentList @("--defaults-file=$defaultsFile") `
    -WorkingDirectory $projectRoot `
    -WindowStyle Hidden `
    -RedirectStandardOutput $outLog `
    -RedirectStandardError $errLog `
    -PassThru

Start-Sleep -Seconds 4
"MariaDB started. PID=$($process.Id)"
