@echo off
rem 一鍵產生影片（Windows）：複製到影片專案資料夾後雙擊。CRLF 換行、UTF-8。
rem 流程：檢查套件 → build.py（Gemini 配音／Zhiwei 暫定）→ 黑熊老師講課疊加 → 接頻道核定片尾 → 單行字幕與燒錄版；全程寫入 產生紀錄.log
rem 片尾：set OUTRO=<相對 REPO 的路徑>，預設 AI Watch 趨勢片尾；自然教室改成 assets\brand-approved\v1\blackbear-science\outro.mp4
chcp 65001 >nul
setlocal
set "PROJ=%~dp0"
set "PROJ=%PROJ:~0,-1%"
set "LOG=%PROJ%\產生紀錄.log"
echo [開始] %date% %time% > "%LOG%"
if "%REPO%"=="" if exist "%USERPROFILE%\multichannel-video-workflow\scripts\build\build.py" set "REPO=%USERPROFILE%\multichannel-video-workflow"
if "%REPO%"=="" set "REPO=%USERPROFILE%\.claude\skills\multichannel-video-workflow"
if "%OUTRO%"=="" set "OUTRO=assets\brand-approved\v1\ai-watch\outros\trends\outro.mp4"
set "CHAR=%REPO%\assets\brand-approved\v1\blackbear-science\character"
echo REPO=%REPO% >> "%LOG%"
if not exist "%REPO%\scripts\build\build.py" goto norepo
echo [更新] 下載最新版技能（git pull）...
git -C "%REPO%" pull --ff-only >> "%LOG%" 2>&1
if defined GEMINI_API_KEY (echo [配音] Gemini Achird 正式配音) else (echo [配音] 沒有 GEMINI_API_KEY，改用 Windows Zhiwei 臺灣國語暫定配音)
if defined GEMINI_API_KEY (echo KEY=yes >> "%LOG%") else (echo KEY=no >> "%LOG%")
set PYTHONIOENCODING=utf-8
echo [準備] 檢查 Python 套件（第一次會自動安裝）...
python -m pip install --disable-pip-version-check -q numpy soundfile pyyaml pillow playwright >> "%LOG%" 2>&1
if errorlevel 1 goto fail
where ffmpeg >nul 2>&1
if errorlevel 1 (echo 找不到 ffmpeg >> "%LOG%" & echo [錯誤] 這台電腦找不到 ffmpeg & goto fail)
echo [進行中] 約 15-40 分鐘，進度寫在 產生紀錄.log，請不要關閉這個視窗...
python -u "%REPO%\scripts\build\build.py" "%PROJ%" >> "%LOG%" 2>&1
if errorlevel 1 goto fail
echo [黑熊老師] 疊加右下角講課角色...
python -m playwright install chromium >> "%LOG%" 2>&1
python -u "%REPO%\scripts\build\bear_presenter.py" "%PROJ%" --character "%CHAR%" >> "%LOG%" 2>&1
if errorlevel 1 (echo [注意] 黑熊老師疊加失敗，改用沒有角色的版本接片尾 >> "%LOG%" & echo [注意] 黑熊老師疊加失敗，先輸出沒有角色的版本)
set "AO=%REPO%\scripts\build\append_outro.py"
if not exist "%AO%" set "AO=%PROJ%\2_製作中\接片尾.py"
python -u "%AO%" "%PROJ%" "%REPO%\%OUTRO%" >> "%LOG%" 2>&1
if errorlevel 1 goto fail
echo [字幕] 產生單行字幕（白字黑框、置中、對齊旁白停頓）並燒錄...
python -u "%REPO%\scripts\build\subs_oneline.py" "%PROJ%" >> "%LOG%" 2>&1
if errorlevel 1 (echo [注意] 單行字幕燒錄失敗，完整版影片仍可使用 >> "%LOG%" & echo [注意] 單行字幕燒錄失敗，完整版影片仍可使用)
echo [完成] >> "%LOG%"
echo [完成] 影片在 3_製作後\輸出成品（_完整版.mp4＝無字幕；_完整版_單行字幕.mp4＝嵌入字幕；上傳 YouTube 用 2_製作中\字幕\字幕_zh-TW_單行.srt）
pause
exit /b 0
:norepo
echo 找不到技能資料夾：%REPO% >> "%LOG%"
echo 找不到技能資料夾：%REPO%（先 set REPO=你的 multichannel-video-workflow 路徑）
pause
exit /b 1
:fail
echo [錯誤] >> "%LOG%"
type "%LOG%"
echo [錯誤] 請把上面的訊息截圖給 Claude
pause
exit /b 1
