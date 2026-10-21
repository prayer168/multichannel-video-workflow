@echo off
chcp 65001 >nul
rem motion-explainer-workflow 第 1 步：在 Windows 安裝 Remotion／HyperFrames 環境並跑 preflight
rem 流程：檢查 Node(>=22)、FFmpeg → remotion\npm install → HyperFrames 無頭 Chrome → (選擇性) Claude Code 外掛 → preflight.py
rem 全程寫入 %ROOT%\安裝紀錄.log；雲端的 Claude 可直接讀這份紀錄
setlocal
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
if "%ROOT%"=="" set "ROOT=%USERPROFILE%\AI-Video-Tools\motion-explainer"
set "HERE=%~dp0"
set "LOG=%ROOT%\安裝紀錄.log"
set "HFVER=0.8.183"
if not exist "%ROOT%" mkdir "%ROOT%"
echo [開始] %date% %time% > "%LOG%"
echo 根目錄：%ROOT%

echo [1/5] 檢查 Node.js 與 FFmpeg...
where node >> "%LOG%" 2>&1 || (echo [缺] 找不到 Node.js，請安裝 Node 22 LTS：winget install OpenJS.NodeJS.LTS & goto fail)
node -e "process.exit(+process.versions.node.split('.')[0]>=22?0:1)" || (echo [缺] Node 版本低於 22，請升級 Node 22 LTS & goto fail)
node -v >> "%LOG%" 2>&1
where ffmpeg >> "%LOG%" 2>&1 || (echo [缺] 找不到 FFmpeg，請安裝：winget install Gyan.FFmpeg & goto fail)

echo [2/5] Remotion：npm install（第一次約 1–3 分鐘）...
if not exist "%ROOT%\remotion\package.json" (echo [缺] %ROOT%\remotion\package.json 不存在 & goto fail)
pushd "%ROOT%\remotion"
call npm install >> "%LOG%" 2>&1
if errorlevel 1 (popd & echo [錯誤] Remotion npm install 失敗 & goto fail)
call npx remotion browser ensure >> "%LOG%" 2>&1
popd

echo [3/5] HyperFrames %HFVER%：安裝渲染用無頭 Chrome...
pushd "%ROOT%\hyperframes"
call npx --yes hyperframes@%HFVER% browser ensure >> "%LOG%" 2>&1
if errorlevel 1 (popd & echo [錯誤] HyperFrames browser ensure 失敗 & goto fail)
popd

echo [4/5] HyperFrames Claude Code 外掛（找不到 claude 指令就略過）...
where claude >nul 2>&1 && (
  call claude plugin marketplace add heygen-com/hyperframes >> "%LOG%" 2>&1
  call claude plugin install hyperframes@hyperframes >> "%LOG%" 2>&1
) || echo [略過] 沒有 claude 指令 >> "%LOG%"
set "MP=%USERPROFILE%\.claude\plugins\marketplaces\hyperframes"
if exist "%MP%\.git" (
  echo [4b] 補抓 HyperFrames 外掛市集的 Git LFS 檔案...
  git -C "%MP%" lfs pull >> "%LOG%" 2>&1 || echo [注意] LFS 補抓失敗，外掛仍可用 >> "%LOG%"
)

echo [5/5] preflight 檢查...
python "%HERE%preflight.py" --root "%ROOT%" >> "%LOG%" 2>&1
set "PF=%errorlevel%"
python "%HERE%preflight.py" --root "%ROOT%" --json > "%ROOT%\preflight.json" 2>nul
type "%LOG%" | findstr /b /c:"✅" /c:"❌" /c:"⚠" /c:"結果"
if not "%PF%"=="0" goto fail
echo [完成] >> "%LOG%"
echo [完成] 環境已就緒，紀錄在 %LOG%
pause
exit /b 0

:fail
echo [失敗] >> "%LOG%"
echo 安裝未完成，請把 %LOG% 交給 Claude 查看。
pause
exit /b 1
