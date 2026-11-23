#!/usr/bin/env python3
"""Original geometric no-media smoke render for test projects. Not publishable science video.
Requires Pillow and ffmpeg/ffprobe installed separately; does NOT use commercial media/APIs.
"""
import argparse,csv,json,shutil,subprocess,hashlib,math
from pathlib import Path
try:from PIL import Image,ImageDraw,ImageFont
except ImportError:raise SystemExit('Install Pillow to run optional POC renderer (no third-party video assets).')
W,H,FPS=1280,720,30
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
def font(s):
 try:return ImageFont.truetype(FONT,s)
 except OSError:return ImageFont.load_default()
def run(cmd):
 p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 if p.returncode:raise RuntimeError('Tool failed '+repr(cmd)+'\n'+p.stderr[-2500:])
 return p.stdout

def image_for_shot(row,idx,num):
 img=Image.new('RGB',(W,H));pix=img.load()
 for y in range(H):
  t=y/(H-1)
  if idx%3==0:c=(int(7+65*t),int(33+125*t),int(72+132*t))
  elif idx%3==1:c=(int(5+13*t),int(21+73*t),int(65+116*t))
  else:c=(int(29+93*t),int(63+84*t),int(114+73*t))
  ImageDraw.Draw(img).line((0,y,W,y),fill=c)
 d=ImageDraw.Draw(img,'RGBA')
 if idx%3==0:
  d.ellipse((920,74,1060,214),fill=(255,230,148,240))
  d.ellipse((-270,415,1600,1050),fill=(8,83,121,225));d.arc((-200,400,1540,1030),205,340,fill=(137,229,249,130),width=7)
 elif idx%3==1:
  d.ellipse((130,300,385,555),fill=(245,204,91,255))
  for i in range(10):
   ang=i*math.pi/5
   x1=600+70*math.cos(ang);y1=372+70*math.sin(ang)
   x2=600+210*math.cos(ang);y2=372+210*math.sin(ang)
   d.line((x1,y1,x2,y2),fill=(82,191,255,245),width=9)
  d.ellipse((565,336,635,408),fill=(173,233,255,255))
  d.line((400,374,525,374),fill=(252,233,160,240),width=15)
 else:
  d.ellipse((900,115,1055,270),fill=(255,221,131,240))
  d.polygon([(0,560),(1280,440),(1280,720),(0,720)],fill=(26,105,151,200))
  for i in range(5):d.arc((-250+i*85,390-i*7,1460+i*50,930),189,342,fill=(147,212,242,160),width=3)
 title=row.get('onscreen_text','').strip() or row.get('visual_description','')
 title=title[:45]
 d.rounded_rectangle((55,58,890,170),radius=18,fill=(4,16,35,192))
 d.text((80,75),title,font=font(45),fill=(245,249,255,255))
 d.rounded_rectangle((55,565,1155,660),radius=16,fill=(5,20,39,215))
 d.text((78,580),f"{row['shot_id']}  |  Original geometric test  |  非正式發佈素材",font=font(24),fill=(255,231,193,255))
 d.text((75,680),'BLACKBEAR SCIENCE VIDEO V1.3 · ENGINEERING SMOKE ONLY',font=font(17),fill=(230,244,255,230))
 return img

def render(project,out=None):
 if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):raise RuntimeError('ffmpeg and ffprobe required')
 project=Path(project).resolve(); out=Path(out) if out else project/'production/poc/out/preview.mp4';out.parent.mkdir(parents=True,exist_ok=True)
 with (project/'shots.csv').open(encoding='utf-8-sig',newline='') as f:shots=list(csv.DictReader(f))
 if not shots:raise RuntimeError('shots.csv has no rows')
 segs=[];expected_frames=0
 for n,r in enumerate(shots):
  dur_ms=int(r['duration_ms']);duration=dur_ms/1000
  count=dur_ms*FPS/1000
  if count!=int(count):raise RuntimeError('Duration must map to exact frames: '+r['shot_id'])
  expected_frames+=int(count)
  frame_file=out.parent/f'scene_{n+1:02d}.png';image_for_shot(r,n,len(shots)).save(frame_file)
  seg=out.parent/f'seg_{n+1:02d}.mp4'
  run(['ffmpeg','-hide_banner','-loglevel','error','-y','-loop','1','-i',str(frame_file),'-t',str(duration),'-vf',f'fps={FPS},format=yuv420p','-c:v','libx264','-preset','ultrafast','-crf','29','-movflags','+faststart',str(seg)])
  segs.append(seg)
 listing=out.parent/'concat.txt';listing.write_text(''.join("file '%s'\n"%x.name for x in segs),encoding='utf-8')
 run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(listing),'-c','copy','-movflags','+faststart',str(out)])
 prob=json.loads(run(['ffprobe','-v','error','-select_streams','v:0','-count_frames','-show_entries','stream=width,height,r_frame_rate,nb_read_frames,duration:format=duration','-of','json',str(out)]))
 stream=prob['streams'][0];actual_frames=int(stream['nb_read_frames']);actual_duration=float(prob['format']['duration']);target=sum(int(r['duration_ms']) for r in shots)/1000
 if actual_frames!=expected_frames or abs(actual_duration-target)>0.05:raise RuntimeError(f'bad video frames or duration: {actual_frames}/{expected_frames}, {actual_duration}/{target}')
 evidence={'video':str(out.relative_to(project)) if out.is_relative_to(project) else str(out),'created_by':'BlackBear V1.3 offline original vector smoke renderer','NOT_A_FULL_PRODUCTION_RENDER':True,'publishable':False,'external_media_used':False,'external_claude_or_codex_used':False,'width':stream['width'],'height':stream['height'],'fps':FPS,'frames':actual_frames,'expected_frames':expected_frames,'duration_seconds':actual_duration,'expected_duration_seconds':target,'video_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'audio':'NONE','rights':'All geometry programmatically original, no external media','science_review':'NOT_VERIFIED_BY_THIS_RENDER'}
 with (out.parent/'poc_qa.json').open('w',encoding='utf-8') as f:json.dump(evidence,f,ensure_ascii=False,indent=2)
 return evidence

def main():
 ap=argparse.ArgumentParser();ap.add_argument('project');ap.add_argument('--out');args=ap.parse_args()
 try:print(json.dumps(render(args.project,args.out),ensure_ascii=False,indent=2))
 except Exception as ex:print('RENDER_SMOKE_ERROR:',str(ex));return 2
 return 0
if __name__=='__main__':raise SystemExit(main())
