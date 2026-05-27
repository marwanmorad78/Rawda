$ErrorActionPreference = "Stop"

$mariadbRoot = "C:\Program Files\MariaDB 12.2"
$mysqld = Join-Path $mariadbRoot "bin\mysqld.exe"

$processes = Get-Process -ErrorAction SilentlyContinue |
    Where-Object { $_.ProcessName -eq "mysqld" -and $_.Path -eq $mysqld }

if (-not $processes) {
    "MariaDB is not running."
    exit 0
}

$processes | Stop-Process -Force
"MariaDB stopped."
