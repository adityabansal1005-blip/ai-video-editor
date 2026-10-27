# Installs the video-editing tools on a Windows laptop.
# Safe to run more than once: it skips anything already installed.
#   powershell -ExecutionPolicy Bypass -File setup-windows.ps1          # tools + base model
#   powershell -ExecutionPolicy Bypass -File setup-windows.ps1 -Small   # also the small model (Hindi, ~490 MB)
param([switch]$Small)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
New-Item -ItemType Directory -Force tools | Out-Null

function Have($cmd) { [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }
function WingetInstall($id) {
    Write-Host "== installing $id"
    winget install --id $id -e --silent --accept-source-agreements --accept-package-agreements --disable-interactivity
}
function Download($url, $out) {
    if (Test-Path $out) { return }
    Write-Host "== downloading $out"
    curl.exe -L --fail --retry 3 -o "$out.part" $url
    Move-Item -Force "$out.part" $out
}

if (-not (Have ffmpeg)) { WingetInstall Gyan.FFmpeg }
if (-not (Have node))   { WingetInstall OpenJS.NodeJS.LTS }
if (-not (Have python) -or (python --version 2>&1) -notmatch "Python 3") { WingetInstall Python.Python.3.13 }
# pick up PATH changes from the installs above
$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")

# yt-dlp and whisper.cpp (GitHub downloads can be very slow on some networks;
# if one stalls, download the same URL in a browser and save it into tools\)
Download "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe" "tools\yt-dlp.exe"
if (-not (Test-Path "tools\whisper\Release\whisper-cli.exe")) {
    # newer v1.9.x tags ship no Windows files; b5454 is the latest build that does
    Download "https://github.com/ggml-org/whisper.cpp/releases/download/b5454/whisper-bin-x64.zip" "tools\whisper-bin-x64.zip"
    Expand-Archive -Force "tools\whisper-bin-x64.zip" "tools\whisper"
    Remove-Item "tools\whisper-bin-x64.zip"
}

$hf = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main"
Download "$hf/ggml-base.bin" "tools\ggml-base.bin"
if ($Small) { Download "$hf/ggml-small.bin" "tools\ggml-small.bin" }

# Node packages for each reel project (fonts + GSAP)
Get-ChildItem -Directory reel-* | ForEach-Object {
    if ((Test-Path "$_\package.json") -and -not (Test-Path "$_\node_modules")) {
        Push-Location $_; npm ci --no-audit --no-fund; Pop-Location
    }
}

Write-Host "== checks"
ffmpeg -version | Select-Object -First 1
& "tools\yt-dlp.exe" --version
& "tools\whisper\Release\whisper-cli.exe" --help *> $null; if ($?) { "whisper-cli ok" }
node --version
python --version
npx -y hyperframes --version
