# 安裝音樂 MV／藝術動畫工具（mv-director、huashu-art-motion、lemo-opuscar，皆 MIT）到技能 repo 之外，釘選已審閱版本。
# 用法：在 PowerShell 執行
#   & "<repo>\motion-explainer-workflow\scripts\install_mv_tools.ps1"                 # 三個 repo＋共用 venv（不含 torch）
#   & "<repo>\motion-explainer-workflow\scripts\install_mv_tools.ps1" -WithStems      # 加 demucs 分軌（含 torch）
#   & "<repo>\motion-explainer-workflow\scripts\install_mv_tools.ps1" -WithAligner    # 加逐字對齊（torch＋transformers 5.x）
# 安全行為：既有 checkout 不覆寫、不 reset；origin 不符或不是 Git 資料夾就停止。
# 不會下載對齊模型（約 1.8 GB）；結尾只印出下載指令，由使用者決定何時下載。
# 不用 lemo-opuscar 的 plugin 安裝（會建 ~/lemo-opuscar 並在「做片」時觸發），只 clone 當風格參考。
param(
    [switch]$WithStems,
    [switch]$WithAligner,
    [string]$PythonVersion = '3.12',   # torch 對最新版 Python 常還沒有 wheel，固定用 3.12
    [string]$TorchIndex = ''           # 空白＝有 NVIDIA 顯示卡用 cu128，沒有用 cpu
)
$ErrorActionPreference = 'Stop'
# 換版前先重新審閱再改這裡（2026-11-10 審閱）
$Repos = @(
    @{ Name = 'mv-director';       Url = 'https://github.com/Yari-tuber/mv-director.git';       Pinned = '79af43a' },
    @{ Name = 'huashu-art-motion'; Url = 'https://github.com/alchaincyf/huashu-art-motion.git'; Pinned = '8a0d7d7' },
    @{ Name = 'lemo-opuscar';      Url = 'https://github.com/lemomo-ai/lemo-opuscar.git';       Pinned = '143f387' }
)
$Root = if ($env:MOTION_REFERENCE_ROOT) { Split-Path $env:MOTION_REFERENCE_ROOT -Parent } else {
    Join-Path $env:USERPROFILE 'AI-Video-Tools\motion-explainer\ecosystem'
}
$Venv = Join-Path $Root 'mv-venv'
$Py = Join-Path $Venv 'Scripts\python.exe'
$Log = Join-Path $Root 'mv-tools-安裝紀錄.log'

# PowerShell 5.1 在 Stop 模式下會把原生程式寫到 stderr 的進度訊息當成錯誤（uv、git 都會寫）；
# 原生指令一律經這裡執行，只看結束碼。
function Native([scriptblock]$cmd) {
    $prev = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
    try { & $cmd 2>&1 | ForEach-Object { $s = "$_"; Write-Host $s; Add-Content -Path $Log -Value $s -Encoding UTF8 } }
    finally { $ErrorActionPreference = $prev }
    return $LASTEXITCODE   # 輸出只寫到畫面與紀錄檔，管線上只有結束碼
}

foreach ($cmd in 'git', 'ffmpeg', 'ffprobe') {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) { throw "找不到 $cmd。請先安裝後重新開啟 PowerShell。" }
}
New-Item -ItemType Directory -Path $Root -Force | Out-Null

foreach ($r in $Repos) {
    $dest = Join-Path $Root $r.Name
    $slug = ($r.Url -replace '^https://github.com/', '' -replace '\.git$', '')
    if (Test-Path $dest) {
        if (-not (Test-Path (Join-Path $dest '.git'))) { throw "目標已存在且不是 Git checkout，停止：$dest" }
        $origin = (& git -C $dest remote get-url origin 2>$null | Select-Object -First 1)
        if ([string]$origin -notmatch [regex]::Escape($slug)) { throw "origin 不是 $slug，停止：$dest" }
        $head = (& git -C $dest rev-parse --short=7 HEAD).Trim()
        if ($head -ne $r.Pinned) { Write-Host "[注意] $($r.Name) 在 $head，不是釘選版 $($r.Pinned)；保留不動。要換版請先審閱後手動 checkout。" }
        else { Write-Host "[已存在] $dest @ $head" }
    } else {
        Write-Host "[Clone] $($r.Url) -> $dest"
        # 樣片與大型 GIF 不需要；大於 5 MB 的檔案用到時才下載
        if ((Native { git clone --filter=blob:limit=5m $r.Url $dest }) -ne 0) { throw "Clone $($r.Name) 失敗，請看上方訊息。" }
        if ((Native { git -C $dest -c advice.detachedHead=false checkout $r.Pinned }) -ne 0) { throw "找不到 $($r.Name) 的釘選版 $($r.Pinned)。" }
    }
}

# 共用 venv：mv-director 與 huashu 的 Python 腳本都用它；uv 會自動下載指定版本的 Python
if (-not (Test-Path $Py)) {
    if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
        throw "找不到 uv。請先執行  winget install astral-sh.uv  後重新開啟 PowerShell，再跑一次本腳本。"
    }
    # 踩坑（2026-11-10，uv 0.13.7）：uv python install 在這台 Windows 建「次版本連結」時報
    # Missing expected target directory for Python minor version link，但直譯器本身已裝好。
    # 所以不看 install 的結束碼，改用 uv python find 找到實際路徑再建 venv。
    Native { uv python install $PythonVersion } | Out-Null
    $base = (& uv python find $PythonVersion 2>$null | Select-Object -First 1)
    if (-not $base -or -not (Test-Path $base)) { throw "找不到 Python $PythonVersion，uv python install 失敗，請看 $Log。" }
    if ((Native { uv venv --python $base $Venv }) -ne 0) { throw '建立 venv 失敗。' }
} else { Write-Host "[已存在] $Venv" }

function Pip([string[]]$pkgs) {
    if ((Native { uv pip install --python $Py @pkgs }) -ne 0) { throw "安裝失敗：$($pkgs -join ' ')" }
}
Pip @('numpy', 'scipy', 'matplotlib', 'pillow', 'playwright', 'opencv-python-headless')
if ((Native { & $Py -m playwright install chromium }) -ne 0) { throw 'Playwright Chromium 安裝失敗。' }

if ($WithStems -or $WithAligner) {
    if (-not $TorchIndex) {
        $TorchIndex = if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) { 'https://download.pytorch.org/whl/cu128' } else { 'https://download.pytorch.org/whl/cpu' }
    }
    Write-Host "[torch] 來源 $TorchIndex（CUDA 版約 2.5 GB）"
    if ((Native { uv pip install --python $Py torch torchaudio --index-url $TorchIndex }) -ne 0) {
        throw 'torch 安裝失敗；可用 -TorchIndex https://download.pytorch.org/whl/cpu 改裝 CPU 版。'
    }
}
if ($WithStems) { Pip @('demucs') }
if ($WithAligner) { Pip @('transformers>=5') }

$Mv = Join-Path $Root 'mv-director'
Push-Location $Mv
try {
    # 踩坑：-I 會忽略 PYTHONUTF8 等環境變數，上游說的「設 PYTHONUTF8=1」無效，
    # 繁中 Windows（cp950）印 ✓ 會 UnicodeEncodeError；要改用 -X utf8。
    Native { & $Py -I -X utf8 scripts\doctor.py } | Out-Null
} finally { Pop-Location }

Write-Host "`n完成。venv：$Venv"
Write-Host "mv-director：& `"$Py`" -I -X utf8 `"$Mv\scripts\new_project.py`" <專案> --song 歌.wav --lyrics 歌詞.lrc"
Write-Host "huashu 片段：& `"$Py`" `"$Root\huashu-art-motion\scripts\engine\render.py`" --spec <clip.json> --out 片段.mp4"
if ($WithAligner) {
    Write-Host "`n對齊模型尚未下載（約 1.8 GB）。要下載時執行："
    Write-Host "  & `"$Py`" -c `"from huggingface_hub import snapshot_download; print(snapshot_download('Qwen/Qwen3-ForcedAligner-0.6B-hf'))`""
    Write-Host '  下載後可設  $env:MV_ALIGNER_MODEL = <印出的資料夾>'
}
Write-Host '歌曲只能用原創或已取得授權的音樂；用法與優先規則見 motion-explainer-workflow/references/music-mv-tools-integration.md。'
