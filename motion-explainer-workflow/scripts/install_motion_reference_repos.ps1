# Install the two Awesome AI Motion source/reference repositories outside the skill Git repo.
# Safe behavior: skip existing Git checkouts, refuse to overwrite any other existing path.
$ErrorActionPreference = 'Stop'
$Root = if ($env:MOTION_REFERENCE_ROOT) {
    $env:MOTION_REFERENCE_ROOT
} else {
    Join-Path $env:USERPROFILE 'AI-Video-Tools\motion-explainer\ecosystem\awesome-ai-motion'
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw '找不到 git。請先安裝 Git for Windows，重新開啟 PowerShell 後再執行。'
}

New-Item -ItemType Directory -Path $Root -Force | Out-Null
$Repos = @(
    @{ Name = 'guanmo-ai'; Url = 'https://github.com/guanmo-ai/awesome-ai-motion.git' },
    @{ Name = 'gongnyang'; Url = 'https://github.com/gongnyang/awesome-ai-motion.git' }
)

foreach ($Repo in $Repos) {
    $Destination = Join-Path $Root $Repo.Name
    if (Test-Path $Destination) {
        if (-not (Test-Path (Join-Path $Destination '.git'))) {
            throw "目標已存在且不是 Git checkout，為避免覆寫已停止：$Destination"
        }
        $ExistingUrl = (& git -C $Destination remote get-url origin 2>$null | Select-Object -First 1)
        if ([string]::IsNullOrWhiteSpace([string]$ExistingUrl) -or $ExistingUrl.Trim().TrimEnd('/') -ne $Repo.Url.TrimEnd('/')) {
            throw "目標 repo 的 origin 與預期不同，為避免改動已停止：$Destination"
        }
        if (-not (Test-Path (Join-Path $Destination 'README.md'))) {
            throw "找到不完整的既有 checkout；未修改或刪除：$Destination"
        }
        Write-Host "[已存在，保留不更新] $Destination"
        continue
    }

    Write-Host "[Clone] $($Repo.Url) -> $Destination"
    & git clone --depth 1 $Repo.Url $Destination
    if ($LASTEXITCODE -ne 0) {
        throw "Clone 失敗；請檢查網路與上方 Git 訊息：$Destination"
    }
    if (-not (Test-Path (Join-Path $Destination 'README.md'))) {
        throw "Clone 後未找到 README.md，請檢查 checkout：$Destination"
    }
}

Write-Host "`n完成。已安裝的上游 repo 位於：$Root"
Write-Host '本腳本不安裝 npm／Playwright／Chromium；只有執行 Gongnyang 本機渲染時才按其 README 安裝相依。'
