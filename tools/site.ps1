param([Parameter(Mandatory=$true)][ValidateSet('Setup','Validate','Build','Preview')][string]$Action)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot
try {
    if ($Action -eq 'Validate') {
        python tools/site.py validate
        if ($LASTEXITCODE -ne 0) { throw 'Content validation failed' }
        python -m unittest discover -s tests -v
        if ($LASTEXITCODE -ne 0) { throw 'Content tests failed' }
        return
    }
    $windowsRoot = $projectRoot.Replace('\','/')
    $linuxResult = & wsl -d Ubuntu -- wslpath -a $windowsRoot
    if ($LASTEXITCODE -ne 0 -or -not $linuxResult) { throw 'Ubuntu unavailable. See README environment prerequisites.' }
    $linuxRoot = $linuxResult.Trim()
    & wsl -d Ubuntu -u root --cd $linuxRoot -- service docker start
    if ($LASTEXITCODE -ne 0) { throw 'Docker daemon did not start' }
    if ($Action -eq 'Setup') {
        & wsl -d Ubuntu -u root --cd $linuxRoot -- docker compose build
    } else {
        & wsl -d Ubuntu -u root --cd $linuxRoot -- docker compose run --rm site
    }
    if ($LASTEXITCODE -ne 0) { throw 'Container operation failed' }
    if ($Action -eq 'Preview') {
        Write-Host 'Preview: http://127.0.0.1:8080 (Ctrl+C to stop)'
        python -m http.server 8080 --bind 127.0.0.1 --directory _site
    }
} finally { Pop-Location }
