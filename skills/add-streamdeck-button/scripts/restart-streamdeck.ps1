$ErrorActionPreference = "Continue"

Write-Host "[restart-sd] Checking Stream Deck process..."
$proc = Get-Process StreamDeck -ErrorAction SilentlyContinue

if ($proc) {
    Write-Host "[restart-sd] Found running Stream Deck (PID $($proc.Id)). Closing..."
    foreach ($p in $proc) {
        try { $p.CloseMainWindow() | Out-Null } catch {}
    }
    Start-Sleep -Seconds 2

    $still = Get-Process StreamDeck -ErrorAction SilentlyContinue
    if ($still) {
        Write-Host "[restart-sd] Graceful close failed. Force killing..."
        Get-Process StreamDeck -ErrorAction SilentlyContinue | Stop-Process -Force
    }
    Start-Sleep -Seconds 3
} else {
    Write-Host "[restart-sd] Stream Deck not running."
}

$exePaths = @(
    "C:\Program Files\Elgato\StreamDeck\StreamDeck.exe",
    "C:\Program Files (x86)\Elgato\StreamDeck\StreamDeck.exe"
)
$exe = $null
foreach ($p in $exePaths) {
    if (Test-Path $p) { $exe = $p; break }
}

if (-not $exe) {
    Write-Error "[restart-sd] StreamDeck.exe not found. Searched: $($exePaths -join '; ')"
    exit 1
}

Write-Host "[restart-sd] Launching $exe ..."
Start-Process $exe

$timeout = 15
for ($i = 0; $i -lt $timeout; $i++) {
    Start-Sleep -Seconds 1
    $running = Get-Process StreamDeck -ErrorAction SilentlyContinue
    if ($running) {
        Write-Host "[restart-sd] Stream Deck running (PID $($running.Id)). OK."
        exit 0
    }
}

Write-Error "[restart-sd] Stream Deck did not start within $timeout seconds."
exit 1
