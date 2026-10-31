# Builds the Claude Desktop extensions (.mcpb) of the CSI MCP servers into dist\
# Each bundle gets its own entry point plus a copy of the shared modules of common\
# Usage : .\build.ps1            (both bundles)
#         .\build.ps1 ETABS      (one bundle)

param([string[]]$Products = @('SAP2000', 'ETABS'))

$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$dist = Join-Path $root 'dist'
$mcpb = '@anthropic-ai/mcpb@2.1.2'

New-Item -ItemType Directory -Force $dist | Out-Null

foreach ($p in $Products) {

    $src = Join-Path $root $p
    $manifest = Get-Content -Raw (Join-Path $src 'manifest.json') | ConvertFrom-Json
    $stage = Join-Path $dist "build\$p"

    # stage a clean copy : manifest, pyproject, icon, entry point and the shared modules side by side in src\

    if (Test-Path $stage) { Remove-Item -Recurse -Force $stage }

    New-Item -ItemType Directory -Force (Join-Path $stage 'src') | Out-Null
    Copy-Item (Join-Path $src 'manifest.json'), (Join-Path $src 'pyproject.toml'), (Join-Path $src 'icon.png'), (Join-Path $root 'LICENSE') $stage
    Copy-Item (Join-Path $src 'src\*.py') (Join-Path $stage 'src')
    Copy-Item (Join-Path $root 'common\*.py') (Join-Path $stage 'src')

    $out = Join-Path $dist "$($manifest.name)-$($manifest.version).mcpb"
    npx -y $mcpb validate (Join-Path $stage 'manifest.json')
    if ($LASTEXITCODE -ne 0) { throw "manifest of $p is not valid" }

    npx -y $mcpb pack $stage $out
    if ($LASTEXITCODE -ne 0) { throw "packing $p failed" }

    Write-Host "built $out"
}
