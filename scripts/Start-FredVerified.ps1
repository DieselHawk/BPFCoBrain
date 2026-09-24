# Start the verified, read-only Fred comparison on localhost:5002.
$ErrorActionPreference = 'Stop'
try {
    $repo = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
    $runner = Join-Path $repo 'scripts\run_fred_compare.py'
    $live = if ($env:BPFCO_LIVE_ROOT) { $env:BPFCO_LIVE_ROOT } else { 'C:\BPFCo\BPFCoBrain-layering' }
    if ($env:BPFCO_DOCUMENTS_ROOT) {
        $documents = $env:BPFCO_DOCUMENTS_ROOT
    } elseif ($env:OneDrive) {
        $documents = Join-Path $env:OneDrive 'Documents\New All Docs'
    } else {
        $documents = Join-Path $env:USERPROFILE 'OneDrive\Documents\New All Docs'
    }
    if (-not (Test-Path -LiteralPath $runner -PathType Leaf)) { throw "Preview runner missing: $runner" }
    if (-not (Test-Path -LiteralPath (Join-Path $live '.vault-index.json') -PathType Leaf)) {
        throw "Live vault index missing: $live"
    }
    if (-not (Test-Path -LiteralPath $documents -PathType Container)) {
        throw "Document source unavailable: $documents"
    }
    $runner = (Resolve-Path -LiteralPath $runner).Path
    $live = (Resolve-Path -LiteralPath $live).Path
    $documents = (Resolve-Path -LiteralPath $documents).Path

    function Assert-PreviewOwner {
        $listeners = @(Get-NetTCPConnection -LocalPort 5002 -State Listen -ErrorAction SilentlyContinue)
        if (-not $listeners.Count) { return $false }
        $owners = @($listeners | Select-Object -ExpandProperty OwningProcess -Unique)
        if ($owners.Count -ne 1) { throw 'Port 5002 has multiple listeners; preview left untouched.' }
        $ownerProcess = Get-CimInstance Win32_Process -Filter "ProcessId = $($owners[0])"
        if (-not $ownerProcess -or
            $ownerProcess.CommandLine -notlike "*run_fred_compare.py*" -or
            $ownerProcess.CommandLine -notlike "*$runner*" -or
            $ownerProcess.CommandLine -notlike "*$live*") {
            throw "Port 5002 belongs to an unrecognized process $($owners[0]); preview left untouched."
        }
        return $true
    }

    $url = 'http://127.0.0.1:5002/super'
    if (-not (Assert-PreviewOwner)) {
        $pythonExe = (& py -3 -c 'import sys; print(sys.executable)')
        if ($LASTEXITCODE -ne 0 -or -not $pythonExe) { throw 'Python 3 is unavailable.' }
        $pythonExe = ($pythonExe | Select-Object -Last 1).Trim()
        $arguments = @(
            '"' + $runner + '"', '--live', '"' + $live + '"',
            '--documents', '"' + $documents + '"', '--no-browser'
        ) -join ' '
        $stamp = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmss')
        $outLog = Join-Path $env:TEMP "fred-verified-$stamp-out.log"
        $errLog = Join-Path $env:TEMP "fred-verified-$stamp-err.log"
        $process = Start-Process -FilePath $pythonExe -ArgumentList $arguments -WorkingDirectory $repo `
            -WindowStyle Hidden -RedirectStandardOutput $outLog -RedirectStandardError $errLog -PassThru
        $ready = $false
        for ($i = 0; $i -lt 20; $i++) {
            Start-Sleep -Seconds 1
            if ($process.HasExited) { break }
            if (-not (Assert-PreviewOwner)) { continue }
            try {
                $response = Invoke-WebRequest 'http://127.0.0.1:5002/api/brain-graph' -UseBasicParsing -TimeoutSec 5
                if ($response.StatusCode -eq 200) { $ready = $true; break }
            } catch { }
        }
        if (-not $ready) {
            $detail = if (Test-Path -LiteralPath $errLog) {
                (Get-Content -LiteralPath $errLog -Tail 8 -ErrorAction SilentlyContinue) -join ' '
            } else { '' }
            throw "Preview did not become ready. $detail Logs: $outLog ; $errLog"
        }
    }
    Start-Process $url
    Write-Host "Fred Verified Preview: $url"
    Write-Host 'Read-only, offline; live queue remains untouched.'
} catch {
    Write-Host "Fred preview stopped: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host 'Press Enter to close'
    exit 1
}
