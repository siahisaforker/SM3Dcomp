param(
    [string]$Destination = (Join-Path $PSScriptRoot "..\.local\toolchains\ghs5.3.22")
)

$ErrorActionPreference = "Stop"

$archiveName = "ghs5.3.22.tar.gz"
$downloadUrl = "https://github.com/decompme/compilers/releases/download/compilers/$archiveName"
$expectedSha256 = "41CD0A4723ACFBDDF8F70A9C3FF84BCE7E85087B1D1CCEF8BBF5F03D82C2B520"
$downloadDir = Join-Path $PSScriptRoot "..\.local\downloads"
$archivePath = Join-Path $downloadDir $archiveName

New-Item -ItemType Directory -Force -Path $downloadDir, $Destination | Out-Null

if (!(Test-Path -LiteralPath $archivePath -PathType Leaf)) {
    Invoke-WebRequest -Uri $downloadUrl -OutFile $archivePath
}

$actualSha256 = (Get-FileHash -LiteralPath $archivePath -Algorithm SHA256).Hash
if ($actualSha256 -ne $expectedSha256) {
    throw "GHS archive digest mismatch: expected $expectedSha256, got $actualSha256"
}

$tar = Join-Path $env:SystemRoot "System32\tar.exe"
if (!(Test-Path -LiteralPath $tar -PathType Leaf)) {
    $tar = "tar"
}

& $tar -xzf $archivePath -C $Destination
if ($LASTEXITCODE -ne 0) {
    throw "Failed to extract $archivePath"
}

$compiler = Join-Path $Destination "bin\cxppc.exe"
if (!(Test-Path -LiteralPath $compiler -PathType Leaf)) {
    throw "Compiler was not found after extraction: $compiler"
}

Write-Host "Installed GHS 5.3.22: $Destination"
