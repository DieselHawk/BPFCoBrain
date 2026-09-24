$ErrorActionPreference = 'Stop'
$preview = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$candidates = @(@(
    $env:BPFCO_DOCUMENTS_ROOT,
    $(if ($env:OneDrive) { Join-Path $env:OneDrive 'Documents\New All Docs' }),
    (Join-Path $env:USERPROFILE 'OneDrive\Documents\New All Docs')
) | Where-Object { $_ -and (Test-Path $_ -PathType Container) } | Select-Object -Unique)
if ($candidates.Count -ne 1) { throw 'Select one valid BPFCO_DOCUMENTS_ROOT before launching Fred Preview' }
$documents = $candidates[0]
$runner = Join-Path $preview 'run_fred_preview.py'
if (-not (Test-Path $runner -PathType Leaf)) { throw "Fred preview launcher missing: $runner" }
if (-not (Test-Path $documents -PathType Container)) { throw "Document source unavailable: $documents" }
$env:BPFCO_DOCUMENTS_ROOT = $documents
$url = 'http://127.0.0.1:5002/super'
$listener = Get-NetTCPConnection -LocalAddress '127.0.0.1' -LocalPort 5002 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if ($listener) {
    $owner = Get-CimInstance Win32_Process -Filter "ProcessId=$($listener.OwningProcess)"
    if (-not $owner -or $owner.Name -ne 'python.exe' -or
        ($owner.CommandLine -notmatch 'run_fred_preview\.py' -and
         ($owner.CommandLine -notmatch 'ceo_dashboard' -or $owner.CommandLine -notmatch 'port=5002'))) {
        throw "Port 5002 is occupied by a different process ($($listener.OwningProcess)); no new process started"
    }
} else {
    $py = (Get-Command py.exe -ErrorAction Stop).Source
    $stdout = Join-Path $env:TEMP 'fred-preview-5002.out.log'
    $stderr = Join-Path $env:TEMP 'fred-preview-5002.err.log'
    $started = Start-Process -FilePath $py -ArgumentList @('-3', ('"' + $runner + '"')) `
        -WorkingDirectory $preview -RedirectStandardOutput $stdout `
        -RedirectStandardError $stderr -PassThru
    Write-Host "Fred Preview process started: $($started.Id)"
}
$ready = $false
for ($attempt = 0; $attempt -lt 12; $attempt++) {
    try {
        $response = Invoke-WebRequest 'http://127.0.0.1:5002/api/status' -UseBasicParsing -TimeoutSec 2
        if ($response.StatusCode -eq 200) { $ready = $true; break }
    } catch {}
    Start-Sleep -Seconds 2
}
if (-not $ready) {
    throw "Preview did not become ready. Check $env:TEMP\fred-preview-5002.err.log"
}
Start-Process $url
Write-Host "Fred Preview is open at $url"
