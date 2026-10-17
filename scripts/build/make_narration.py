# -*- coding: utf-8 -*-
"""用 Gemini（gemini-3.8-flash-tts／Achird＋固定 Style）在使用者的 Windows 電腦產生旁白，兩幕一組。

用法：把本檔、make_narration.bat、旁白資料.json 放在同一個資料夾，雙擊 make_narration.bat。
  python make_narration.py [--data 旁白資料.json] [--out 配音] [--model ...] [--voice Achird] [--wait 21]

旁白資料.json 格式（見 references/real-test-workflow.md 第四節）：
  {"style": "<fixed-settings.md 第一節 Style 全文，最後一行換成本片術語>",
   "scenes": {"S01": ["第一句", "第二句"], "S02": [...]},
   "pairs":  [["S01", "S02"], ["S03", "S04"]]}

- 需要環境變數 GEMINI_API_KEY（只在本機讀取，不寫進任何檔案；不要截圖或貼進對話）。
- 輸出 <out>/S01-S02.wav（24 kHz 單聲道 16-bit），檔名與 build.py 的 Gemini 配音資料夾相同。
- 已存在的組別會跳過；403／429（額度用完）就停下，隔天再執行會從缺的組接續。
- 只用標準函式庫，新電腦不必另外安裝套件。
"""
import os, sys, json, time, base64, wave, re, argparse, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=os.path.join(HERE, "旁白資料.json"))
    ap.add_argument("--out", default=os.path.join(HERE, "配音"))
    ap.add_argument("--model", default="gemini-3.8-flash-tts")
    ap.add_argument("--voice", default="Achird")
    ap.add_argument("--wait", type=float, default=21.0, help="兩次請求間隔秒數（免費方案每分鐘 3 次）")
    a = ap.parse_args()

    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        print("找不到 GEMINI_API_KEY。請先設定（setx GEMINI_API_KEY 你的金鑰），關掉視窗後重新雙擊。")
        return 1
    data = json.load(open(a.data, encoding="utf-8"))
    os.makedirs(a.out, exist_ok=True)
    todo = [(x, y) for x, y in data["pairs"] if not os.path.exists(os.path.join(a.out, f"{x}-{y}.wav"))]
    print(f"還要產生 {len(todo)} 組（模型 {a.model}，聲音 {a.voice}）")
    for k, (x, y) in enumerate(todo):
        text = "\n".join(data["scenes"].get(x, []) + data["scenes"].get(y, []))
        prompt = f"## Style:\n{data['style']}\n\n## Transcript:\n{text}"
        body = dict(contents=[dict(role="user", parts=[dict(text=prompt)])],
                    generationConfig=dict(temperature=1, responseModalities=["audio"],
                                          speechConfig=dict(voiceConfig=dict(prebuiltVoiceConfig=dict(voiceName=a.voice)))))
        req = urllib.request.Request(
            f"https://generativelanguage.googleapis.com/v1beta/models/{a.model}:generateContent",
            data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": key})
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                resp = json.load(r)
        except urllib.error.HTTPError as e:
            print(f"{x}-{y} 失敗：HTTP {e.code}")
            if e.code in (403, 429):
                print("額度用完或權限不足，先停在這裡；明天再雙擊會從缺的組接續。")
                return 2
            return 3
        part = resp["candidates"][0]["content"]["parts"][0]["inlineData"]
        m = re.search(r"rate=(\d+)", part.get("mimeType", ""))
        rate = int(m.group(1)) if m else 24000
        pcm = base64.b64decode(part["data"])
        with wave.open(os.path.join(a.out, f"{x}-{y}.wav"), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(pcm)
        print(f"{x}-{y}：{len(pcm) / 2 / rate:.1f} 秒")
        if k < len(todo) - 1:
            time.sleep(a.wait)
    print(f"全部完成，檔案在「{os.path.basename(a.out)}」資料夾。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
