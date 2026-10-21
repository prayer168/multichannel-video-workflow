# motion-explainer-workflow：Windows 安裝（PowerShell 版，與 setup_windows.bat 同流程）
# 執行：powershell -NoExit -ExecutionPolicy Bypass -File "<motion-explainer>\install_windows.ps1"
# 規則：不刪檔、已裝好就跳過、每步輸出附加寫入 安裝紀錄.log、任何一步失敗就停下並提示修法
$ErrorActionPreference = 'Continue'
$Root = if ($env:ROOT) { $env:ROOT } else { Join-Path $env:USERPROFILE 'AI-Video-Tools\motion-explainer' }
$Log = Join-Path $Root '安裝紀錄.log'
$HFVER = '0.8.183'
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Log([string]$msg) {
    Write-Host $msg
    Add-Content -Path $Log -Value $msg -Encoding UTF8
}
function Run([string]$label, [string]$cmd, [string]$dir = $Root) {
    Log "`n>>> [$label] $cmd  （位置：$dir）"
    Push-Location $dir
    $out = cmd /c "$cmd 2>&1"
    $code = $LASTEXITCODE
    Pop-Location
    if ($out) { $out | ForEach-Object { Write-Host $_ }; Add-Content -Path $Log -Value $out -Encoding UTF8 }
    Log "<<< 結束代碼 $code"
    return $code
}
function Fail([string]$why, [string]$fix) {
    Log "`n[失敗] $why"
    Log "[建議修法] $fix"
    Log "[停止] $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    exit 1
}

Add-Content -Path $Log -Value "`n===== install_windows.ps1 開始 $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') =====" -Encoding UTF8
Log "根目錄：$Root"

# 1. Node / npm / FFmpeg
Log "`n[1/5] 檢查 Node.js、npm、FFmpeg"
if (-not (Get-Command node -ErrorAction SilentlyContinue)) { Fail '找不到 node' '執行 winget install OpenJS.NodeJS.LTS，裝完開新的 PowerShell 視窗再重跑本腳本' }
Run 'node' 'node -v' | Out-Null
$major = [int]((node -v).TrimStart('v').Split('.')[0])
if ($major -lt 22) { Fail "Node 版本 $major 低於 22" '執行 winget install OpenJS.NodeJS.LTS，裝完開新視窗重跑' }
Log "Node 主版本 $major ≥ 22，跳過安裝"
if ((Run 'npm' 'npm -v') -ne 0) { Fail 'npm 無法執行' '重新安裝 Node 22 LTS（npm 隨附）' }
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) { Fail '找不到 ffmpeg' '執行 winget install Gyan.FFmpeg，裝完開新視窗讓 PATH 生效後重跑' }
$ff = (cmd /c 'ffmpeg -version 2>&1' | Select-Object -First 1)
Log "ffmpeg：$ff（已安裝，跳過）"

# 2. Remotion
Log "`n[2/5] Remotion"
$rdir = Join-Path $Root 'remotion'
if (-not (Test-Path (Join-Path $rdir 'package.json'))) { Fail "$rdir\package.json 不存在" '從技能 repo 重新建立 remotion 專案' }
if (Test-Path (Join-Path $rdir 'node_modules\remotion\package.json')) {
    Log 'remotion\node_modules 已存在，跳過 npm install'
} else {
    if ((Run 'npm install' 'npm install' $rdir) -ne 0) { Fail 'Remotion npm install 失敗' '檢查網路或代理設定，看上方 npm 錯誤訊息；必要時刪除 remotion\node_modules 後重跑（需你手動刪除）' }
}
if ((Run 'remotion browser' 'npx remotion browser ensure' $rdir) -ne 0) { Fail 'npx remotion browser ensure 失敗' '檢查網路能否下載 Chrome Headless Shell；看上方錯誤訊息' }

# 3. HyperFrames
Log "`n[3/5] HyperFrames $HFVER"
$hdir = Join-Path $Root 'hyperframes'
if ((Run 'hyperframes browser' "npx --yes hyperframes@$HFVER browser ensure" $hdir) -ne 0) { Fail 'hyperframes browser ensure 失敗' '確認 Node ≥22 與網路；看上方錯誤訊息' }

# 4. Claude Code 外掛
Log "`n[4/5] HyperFrames Claude Code 外掛"
if (Get-Command claude -ErrorAction SilentlyContinue) {
    $list = cmd /c 'claude plugin list 2>&1'
    if ($list -match 'hyperframes') {
        Log '外掛 hyperframes 已安裝，跳過'
    } else {
        if ((Run 'marketplace' 'claude plugin marketplace add heygen-com/hyperframes') -ne 0) { Fail '新增 HyperFrames marketplace 失敗' '看上方錯誤訊息；可在 Claude Code 內用 /plugin 手動加入' }
        if ((Run 'plugin install' 'claude plugin install hyperframes@hyperframes') -ne 0) { Fail '安裝 hyperframes 外掛失敗' '看上方錯誤訊息；可在 Claude Code 內用 /plugin 手動安裝' }
    }
} else {
    Log '[略過] 找不到 claude 指令'
}
# 4b. 補抓外掛市集的 Git LFS 檔案（Claude Code 新增市集時只會取得 LFS 佔位檔；失敗不中斷）
$mp = Join-Path $env:USERPROFILE '.claude\plugins\marketplaces\hyperframes'
if (Test-Path (Join-Path $mp '.git')) {
    if ((cmd /c 'git lfs version 2>&1') -match 'git-lfs') {
        if ((Run 'lfs pull' "git -C `"$mp`" lfs pull") -ne 0) { Log '[注意] LFS 補抓失敗，外掛仍可用；之後可手動執行：git -C C:/Users/<使用者>/.claude/plugins/marketplaces/hyperframes lfs pull' }
    } else {
        Log '[注意] 找不到 git-lfs（Git for Windows 通常內建）；外掛可用，但範例素材是佔位檔'
    }
}

# 5. preflight
Log "`n[5/5] preflight 檢查"
$pf = Run 'preflight' 'python preflight.py --root .'
cmd /c 'python preflight.py --root . --json > preflight.json 2>nul' | Out-Null
Log '已輸出 preflight.json'

# 字體
$fonts = Get-ChildItem (Join-Path $Root 'fonts') -Filter 'NotoSansTC*' -ErrorAction SilentlyContinue
$ofl = Test-Path (Join-Path $Root 'fonts\OFL.txt')
Log ("字體：" + $(if ($fonts) { ($fonts.Name -join '、') } else { '❌ 沒有 NotoSansTC' }) + "；OFL.txt：" + $(if ($ofl) { '✅' } else { '❌' }))

if ($pf -ne 0) { Fail 'preflight 有必要項目未通過' '看上方 ❌ 項目與 → 提示' }
Log "`n[完成] $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') 環境已就緒"
