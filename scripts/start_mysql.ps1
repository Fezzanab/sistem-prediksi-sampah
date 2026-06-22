<#
PowerShell helper: Force project to use MySQL only, run seeding, and start Flask app.

Usage:
  Open PowerShell in project root and run:
    .\.venv\Scripts\Activate.ps1
    .\scripts\start_mysql.ps1

What it does:
  - Loads `.env` values if present
  - Constructs or uses `DATABASE_URL` (URL-encodes password if needed)
  - Exports `DATABASE_URL` into the current process environment
  - Runs `python scripts/seed_db.py` to inject seed data into MySQL
  - If seeding succeeds, runs `python app.py` to start the Flask server

Note: This script assumes `mysql` server is reachable and credentials in `.env` are correct.
#>

function Read-DotEnv {
    param([string]$Path = '.env')
    $result = @{}
    if (Test-Path $Path) {
        Get-Content $Path | ForEach-Object {
            if ($_ -match '^(?<k>[^#=]+)=(?<v>.*)$') {
                $k = $Matches['k'].Trim()
                $v = $Matches['v'].Trim()
                $result[$k] = $v
            }
        }
    }
    return $result
}

Write-Host "Loading .env values (if present)..."
$envMap = Read-DotEnv -Path ".env"

$dbUser = $envMap['DB_USER']  -or 'root'
$dbPass = $envMap['DB_PASSWORD'] -or ''
$dbHost = $envMap['DB_HOST'] -or 'localhost'
$dbPort = $envMap['DB_PORT'] -or '3306'
$dbName = $envMap['DB_NAME'] -or 'sistem_prediksi_sampah'
$databaseUrl = $envMap['DATABASE_URL']

if (-not $databaseUrl) {
    if ($dbPass -ne '') {
        $encPass = [System.Uri]::EscapeDataString($dbPass)
    } else { $encPass = '' }
    $databaseUrl = "mysql+pymysql://$dbUser:$encPass@$dbHost:$dbPort/$dbName"
}

Write-Host "Using DATABASE_URL:" ([regex]::Replace($databaseUrl, "://[^:]+:[^@]+@", '://$1:***@'))

$env:DATABASE_URL = $databaseUrl

Write-Host "Running DB seeding..."
$seed = & python scripts/seed_db.py
if ($LASTEXITCODE -ne 0) {
    Write-Error "Seeding failed. Fix errors and retry."
    exit $LASTEXITCODE
}

Write-Host "Starting Flask app..."
& python app.py
