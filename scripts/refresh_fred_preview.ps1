param([switch]$AlreadyFetched, [string]$DocumentsPath)
$ErrorActionPreference = 'Stop'
$preview = 'C:\BPFCo\FredPreview'
$documents = $DocumentsPath
$branch = 'fix/fred-shared-memory-backup'
$files = @(
    'Dashboard/adapters/note_edges.py',
    'Dashboard/adapters/document_edges.py',
    'Dashboard/adapters/provenance_edges.py',
    'Dashboard/super_brain_3d.html',
    'run_fred_preview.py'
)
if (-not (Test-Path "$preview\.git")) { throw "Preview worktree unavailable: $preview" }
$indexPath = Join-Path $preview '.vault-index.json'
if (-not (Test-Path $indexPath)) { throw 'Preview vault index unavailable' }
$index = Get-Content $indexPath -Raw | ConvertFrom-Json
$actual = @($index.notes.PSObject.Properties).Count
$reported = $index.stats.total_notes
Write-Host "Indexed note records: $actual; index statistic: $reported"
if ($actual -ne 855 -or ($null -ne $reported -and [int]$reported -ne $actual)) {
    throw 'The current index is not the verified 855-note snapshot. Stop and inspect before changing the preview.'
}
if (-not $documents) {
    $roots = @('C:\Documents', (Join-Path $env:USERPROFILE 'Documents'),
               (Join-Path $env:USERPROFILE 'OneDrive'), $env:OneDrive,
               $env:OneDriveCommercial) | Where-Object { $_ -and (Test-Path $_ -PathType Container) } | Select-Object -Unique
    $folderCandidates = @($roots | ForEach-Object {
        $root = $_
        Get-ChildItem $root -Directory -Recurse -Depth 3 -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -in @('New All Docs', 'AllNew Docs', 'AllNew_Docs') }
    } | Select-Object -ExpandProperty FullName -Unique)
    if ($folderCandidates.Count -eq 0) {
        $folderCandidates = @('C:\BPFCo\BPFCoBrain\AllNew_Docs',
                              'C:\BPFCo\BPFCoBrain-layering\AllNew_Docs') |
            Where-Object { Test-Path $_ -PathType Container }
    }
    if ($folderCandidates.Count -ne 1) {
        Write-Host 'Candidate document folders:'
        $folderCandidates | ForEach-Object { Write-Host "  $_" }
        throw 'Provide the exact document path with -DocumentsPath. No preview files changed.'
    }
    $documents = $folderCandidates[0]
}
if (-not (Test-Path $documents -PathType Container)) { throw "Document source unavailable: $documents" }
$documents = (Resolve-Path $documents).Path
$samples = @(Get-ChildItem $documents -Recurse -File -ErrorAction Stop | Select-Object -First 201)
Write-Host "Document source: $documents"
$supported = @($samples | Where-Object { $_.Extension -in @('.md', '.txt', '.docx', '.pdf') }).Count
Write-Host "Documents sampled: $($samples.Count) (200+ if 201); supported text/DOCX/PDF: $supported"
$samples | Group-Object Extension | Sort-Object Name | ForEach-Object { Write-Host "  $($_.Name): $($_.Count)" }
if ($supported -eq 0) { throw 'No supported document in the sample. No preview files changed.' }
$origin = git -C $preview remote get-url origin
if ($LASTEXITCODE -ne 0 -or $origin -notmatch 'DieselHawk/BPFCoBrain(\.git)?$') { throw "Unexpected preview origin: $origin" }
$dirty = @(git -C $preview status --porcelain -- $files)
if ($dirty.Count) { throw "Preview graph files have local changes; no files were replaced: $($dirty -join ', ')" }
$route = Join-Path $preview 'ceo_dashboard.py'
$routeText = [System.IO.File]::ReadAllText($route)
$old = 'return jsonify(add_provenance_edges(build_brain_graph(), ROOT))'
$newer = 'return jsonify(add_note_edges(add_provenance_edges(build_brain_graph(), ROOT), ROOT))'
$plain = 'return jsonify(build_brain_graph())'
if (-not ($routeText.Contains($old) -or $routeText.Contains($newer) -or $routeText.Contains($plain) -or $routeText.Contains('graph = add_document_edges(graph, ROOT)'))) {
    throw 'The preview graph route differs from known versions; leave it intact for reconciliation.'
}
if (-not $AlreadyFetched) {
    git -C $preview fetch --no-tags origin $branch
    if ($LASTEXITCODE -ne 0) { throw 'Git fetch failed; preview unchanged' }
}
foreach ($file in $files) {
    git -C $preview cat-file -e "FETCH_HEAD`:$file" 2>$null
    if ($LASTEXITCODE -ne 0) { throw "Draft missing $file; preview unchanged" }
}
$listener = Get-NetTCPConnection -LocalAddress '127.0.0.1' -LocalPort 5002 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if ($listener) {
    $process = Get-CimInstance Win32_Process -Filter "ProcessId=$($listener.OwningProcess)"
    if ($process.CommandLine -notmatch 'FredPreview|run_fred_preview') {
        throw "Port 5002 belongs to an unrecognized process $($listener.OwningProcess); no restart attempted"
    }
}
$backup = Join-Path $env:TEMP ('fred-preview-route-' + [guid]::NewGuid().ToString('N') + '.py')
Copy-Item $route $backup
git -C $preview restore --source=FETCH_HEAD --worktree -- $files
if ($LASTEXITCODE -ne 0) { throw 'File restore failed; server has not been stopped' }
if (-not $routeText.Contains('graph = add_document_edges(graph, ROOT)')) {
    foreach ($line in @('    from Dashboard.adapters.provenance_edges import add_provenance_edges',
                       '    from Dashboard.adapters.note_edges import add_note_edges',
                       '    from Dashboard.adapters.document_edges import add_document_edges')) {
        if (-not $routeText.Contains($line)) {
            $marker = '    from Dashboard.adapters.brain_graph_adapter import build_brain_graph'
            $routeText = $routeText.Replace($marker, $marker + "`n" + $line)
        }
    }
    $replacement = "graph = add_note_edges(build_brain_graph(), ROOT)`n    graph = add_document_edges(graph, ROOT)`n    return jsonify(add_provenance_edges(graph, ROOT))"
    foreach ($candidate in @($old, $newer, $plain)) {
        if ($routeText.Contains($candidate)) { $routeText = $routeText.Replace($candidate, $replacement); break }
    }
    [System.IO.File]::WriteAllText($route, $routeText, (New-Object System.Text.UTF8Encoding($false)))
}
$check = @($route, (Join-Path $preview 'Dashboard\adapters\note_edges.py'),
           (Join-Path $preview 'Dashboard\adapters\document_edges.py'),
           (Join-Path $preview 'run_fred_preview.py'))
py -3 -m py_compile $check
if ($LASTEXITCODE -ne 0) {
    Copy-Item $backup $route -Force
    throw 'Syntax check failed; original route restored; server not stopped'
}
if ($listener) { Stop-Process -Id $listener.OwningProcess -ErrorAction Stop }
$env:BPFCO_DOCUMENTS_ROOT = $documents
$runner = Join-Path $preview 'run_fred_preview.py'
$stdout = Join-Path $env:TEMP 'fred-preview-5002.out.log'
$stderr = Join-Path $env:TEMP 'fred-preview-5002.err.log'
$started = Start-Process -FilePath 'py.exe' -ArgumentList @('-3', ('"' + $runner + '"')) -WorkingDirectory $preview -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
Write-Host "Preview PID $($started.Id), requested source: $documents"
$ready = $false
for ($attempt = 0; $attempt -lt 9; $attempt++) {
    Start-Sleep -Seconds 5
    try {
        $graph = Invoke-RestMethod 'http://127.0.0.1:5002/api/brain-graph' -TimeoutSec 5
        Write-Host "Live graph: notes=$($graph.stats.notes) documents=$($graph.stats.document_sources) exact-copy-groups=$($graph.stats.exact_duplicate_groups) suppressed-copies=$($graph.stats.document_duplicates_suppressed) hash-pending=$($graph.stats.document_unverified_hashes) extract-pending=$($graph.stats.document_pending) note-links=$($graph.stats.scanned_note_links) document-links=$($graph.stats.document_links) provenance=$($graph.stats.provenance_links)"
        $ready = $true
        break
    } catch { if ($started.HasExited) { break } }
}
if (-not $ready) { Write-Host "Preview not yet ready. Inspect $stderr; route backup: $backup"; return }
Write-Host 'Open http://127.0.0.1:5002/super and leave the Brain view open. Route backup:' $backup
