# 安裝 Motion Showreel（ConardLi/garden-skills，MIT）到技能 repo 之外，釘選已審閱版本。
# 用法：在 PowerShell 執行  & "<repo>\motion-explainer-workflow\scripts\install_motion_showreel.ps1"
# 安全行為：既有 checkout 不覆寫、不 reset；origin 不符或不是 Git 資料夾就停止。
# 注意：上游 scripts/package-lock.json 指向 bnpm.byted.org（非公開鏡像），照上游 setup.sh 會 403。
#       本腳本把它改名保留為 package-lock.upstream.json，改從公開 registry.npmjs.org 安裝。
$ErrorActionPreference = 'Stop'
$Pinned = '2b9a893'   # 2026-10-25，motion-showreel 0.2.0；換版前先重新審閱再改這裡
$Url = 'https://github.com/ConardLi/garden-skills.git'
$Root = if ($env:MOTION_REFERENCE_ROOT) { Split-Path $env:MOTION_REFERENCE_ROOT -Parent } else {
    Join-Path $env:USERPROFILE 'AI-Video-Tools\motion-explainer\ecosystem'
}
$Dest = Join-Path $Root 'garden-skills'
$Skill = Join-Path $Dest 'skills\motion-showreel'
$Log = Join-Path $Root 'motion-showreel-安裝紀錄.log'

foreach ($cmd in 'git', 'node', 'npm', 'ffmpeg') {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) { throw "找不到 $cmd。請先安裝後重新開啟 PowerShell。" }
}
$nodeMajor = [int]((node -v).TrimStart('v').Split('.')[0])
if ($nodeMajor -lt 18) { throw "Motion Showreel 需要 Node 18 以上（目前 $(node -v)）。" }

New-Item -ItemType Directory -Path $Root -Force | Out-Null
if (Test-Path $Dest) {
    if (-not (Test-Path (Join-Path $Dest '.git'))) { throw "目標已存在且不是 Git checkout，停止：$Dest" }
    $origin = (& git -C $Dest remote get-url origin 2>$null | Select-Object -First 1)
    if ([string]$origin -notmatch 'ConardLi/garden-skills') { throw "origin 不是 ConardLi/garden-skills，停止：$Dest" }
    $head = (& git -C $Dest rev-parse --short=7 HEAD).Trim()
    if ($head -ne $Pinned) { Write-Host "[注意] 既有 checkout 在 $head，不是釘選版 $Pinned；保留不動。要換版請先審閱後手動 checkout。" }
    else { Write-Host "[已存在] $Dest @ $head" }
} else {
    Write-Host "[Clone] $Url -> $Dest"
    & git clone $Url $Dest 2>&1 | Tee-Object -FilePath $Log -Append
    if ($LASTEXITCODE -ne 0) { throw 'Clone 失敗，請看上方訊息。' }
    & git -C $Dest -c advice.detachedHead=false checkout $Pinned 2>&1 | Tee-Object -FilePath $Log -Append
    if ($LASTEXITCODE -ne 0) { throw "找不到釘選版 $Pinned。" }
}

$Scripts = Join-Path $Skill 'scripts'
$Lock = Join-Path $Scripts 'package-lock.json'
if ((Test-Path $Lock) -and (Select-String -Path $Lock -Pattern 'bnpm.byted.org' -Quiet)) {
    Move-Item $Lock (Join-Path $Scripts 'package-lock.upstream.json') -Force
    Write-Host '[修正] 上游 lockfile 指向非公開鏡像，已改名保留並改用公開 registry。'
}
Push-Location $Scripts
try {
    if (-not (Test-Path (Join-Path $Scripts 'node_modules\playwright'))) {
        & npm install --no-audit --no-fund --loglevel=error --registry=https://registry.npmjs.org 2>&1 | Tee-Object -FilePath $Log -Append
        if ($LASTEXITCODE -ne 0) { throw 'npm install 失敗。' }
    } else { Write-Host '[已存在] node_modules' }
    & npx --yes playwright install chromium 2>&1 | Tee-Object -FilePath $Log -Append
    & node check-env.mjs 2>&1 | Tee-Object -FilePath $Log -Append
} finally { Pop-Location }

Write-Host "`n完成。SKILL 路徑（S）：$Scripts"
Write-Host '用法與本頻道的優先規則見 motion-explainer-workflow/references/motion-showreel-integration.md。'
Write-Host '不要用它的 TTS 產生正式配音；黑熊老師聲線一律依 fixed-settings.md（Achird＋固定 Style）。'
