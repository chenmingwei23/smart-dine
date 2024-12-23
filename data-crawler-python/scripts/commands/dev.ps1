param(
    [Parameter(Position=0)]
    [string]$Command
)

$ErrorActionPreference = "Stop"

function Show-Help {
    Write-Host "`nAvailable commands:"
    Write-Host "  run       - Run the crawler (cleans DB first)"
    Write-Host "  clean     - Clean the database only"
    Write-Host "  help      - Show this help message`n"
}

function Run-Crawler {
    Write-Host "`nCleaning database..."
    python scripts/clean_db.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Database cleanup failed"
        exit $LASTEXITCODE
    }

    Write-Host "`nRunning crawler..."
    python -m src.main
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Crawler execution failed"
        exit $LASTEXITCODE
    }

    Write-Host "`nDone!`n"
}

function Clean-Database {
    Write-Host "`nCleaning database..."
    python scripts/clean_db.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Database cleanup failed"
        exit $LASTEXITCODE
    }
    Write-Host "Done!`n"
}

switch ($Command) {
    "run" { Run-Crawler }
    "clean" { Clean-Database }
    default { Show-Help }
} 