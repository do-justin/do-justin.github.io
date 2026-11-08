param([switch]$Publish)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$publicRemote = 'https://github.com/do-justin/do-justin.github.io.git'

function Invoke-Git {
    & git @args
    if ($LASTEXITCODE -ne 0) { throw 'Git operation failed' }
}

Push-Location $projectRoot
try {
    if (Invoke-Git status --porcelain) { throw 'Commit or set aside source changes before preparing a release' }
    $revision = Invoke-Git rev-parse HEAD
    & "$PSScriptRoot/site.ps1" -Action Build
    if (Invoke-Git status --porcelain) { throw 'Build changed source files; review before releasing' }

    $stage = Join-Path $projectRoot ('.build/publish-' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $stage | Out-Null
    Get-ChildItem -LiteralPath (Join-Path $projectRoot '_site') -Force |
        Copy-Item -Destination $stage -Recurse
    python tools/site.py audit --site $stage
    if ($LASTEXITCODE -ne 0) { throw 'Staged artifact audit failed' }
    New-Item -ItemType File -Path (Join-Path $stage '.nojekyll') | Out-Null

    Invoke-Git -C $stage init --initial-branch=gh-pages | Out-Null
    $existing = Invoke-Git ls-remote --heads $publicRemote refs/heads/gh-pages
    if ($existing) {
        Invoke-Git -C $stage fetch --depth 1 $publicRemote gh-pages
        Invoke-Git -C $stage reset --mixed FETCH_HEAD | Out-Null
    }
    Invoke-Git -C $stage add --all
    & git -C $stage diff --cached --quiet
    if ($LASTEXITCODE -gt 1) { throw 'Cannot inspect staged changes' }
    if ($LASTEXITCODE -eq 1) {
        Invoke-Git -C $stage commit -m "Publish verified site from $revision" | Out-Null
    }
    Write-Host "Prepared artifact: $stage"
    if ($Publish) {
        Invoke-Git -C $stage push $publicRemote HEAD:refs/heads/gh-pages
        & gh api --method PUT repos/do-justin/do-justin.github.io/pages `
            -f build_type=legacy -f 'source[branch]=gh-pages' -f 'source[path]=/'
        if ($LASTEXITCODE -ne 0) { throw 'Pages configuration failed; inspect before retrying' }
        Write-Host 'Submitted to GitHub Pages. Verify the managed deployment and live site.'
    } else {
        Write-Host 'Preparation only. Use -Publish to upload the verified artifact.'
    }
} finally { Pop-Location }
