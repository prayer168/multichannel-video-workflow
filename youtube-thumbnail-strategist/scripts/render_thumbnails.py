#!/usr/bin/env python3
"""V1.1: Real video -> 3 legible Traditional Chinese YouTube thumbnails.
Optional OpenAI background generation is illustration-only and opt-in.
"""
import argparse, base64, io, json, os, shutil, subprocess, sys, urllib.request, urllib.error
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps, ImageStat

DEFAULT_TEXT = {'natural': ['為什麼？', '真的嗎？', '驚人現象'], 'aiwatch': ['AI實測', '做到了？', '成果揭曉']}
COLORS = {'natural': [(255,221,44),(255,255,255),(255,224,95)], 'aiwatch':[(68,255,205),(255,237,104),(255,255,255)]}

def cmd_run(args):
    p=subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if p.returncode: raise RuntimeError(f"Command failed: {' '.join(args[:3])}: {p.stderr.decode(errors='replace')[-600:]}")
    return p.stdout.decode(errors='replace')

def duration_seconds(video):
    raw=cmd_run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(video)])
    val=float(raw.strip());
    if val<=0: raise ValueError('Video duration must be > 0')
    return val

def extract_frame(video, timestamp, destination):
    destination.unlink(missing_ok=True)
    cmd_run([
        'ffmpeg', '-hide_banner', '-loglevel', 'error', '-ss', f'{timestamp:.6f}',
        '-i', str(video), '-frames:v', '1', '-q:v', '3', '-y', str(destination),
    ])
    with Image.open(destination) as image:
        return image.convert('RGB')


def sample(video, outdir, duration, count=18):
    frame_dir=outdir/'source_frames'; frame_dir.mkdir(parents=True,exist_ok=True)
    candidates=[]
    for i in range(count):
        t=max(0.0,min(max(0.0,duration-0.6), duration*(i+.5)/count))
        dest=frame_dir/f'frame_{i:02d}.jpg'
        try:
            frame = extract_frame(video, t, dest)
            small = frame.resize((256, 144))
            gray = ImageOps.grayscale(small)
            bright = ImageStat.Stat(gray).mean[0]
            edge = ImageStat.Stat(gray.filter(ImageFilter.FIND_EDGES)).stddev[0]
            saturation = ImageStat.Stat(small).stddev
            score = edge * 2 + sum(saturation) / 3 * .4 - abs(bright - 125) * .10
            candidates.append({'path':str(dest),'timestamp_sec':round(t,6),'quality_score':round(score,2),'segment':min(2,int(i*3/count))})
        except Exception as exc:
            print(f'WARNING skipped frame at {t:.2f}s: {exc}', file=sys.stderr)
    if len(candidates)<3: raise RuntimeError('Could not extract at least three real frames')
    selected=[]
    for segment in range(3):
        pool=[x for x in candidates if x['segment']==segment]
        if not pool: pool=candidates
        chosen=max(pool,key=lambda x:x['quality_score']); selected.append(chosen)
    return selected,candidates

def font_path(user_path):
    if user_path:
        if not Path(user_path).is_file(): raise FileNotFoundError(f'Font not found: {user_path}')
        return user_path
    for path in ['/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc','/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc','C:/Windows/Fonts/msjhbd.ttc','C:/Windows/Fonts/msyhbd.ttc','C:/Windows/Fonts/msjh.ttc','C:/Windows/Fonts/msyh.ttc']:
        if Path(path).is_file(): return path
    raise RuntimeError('Traditional Chinese CJK font missing: provide --font with licensed local font')

def fit_font(draw, txt, fontfile, maxwidth, maxheight, start=125):
    for size in range(start,23,-2):
        f=ImageFont.truetype(fontfile,size)
        b=draw.textbbox((0,0),txt,font=f,stroke_width=6)
        if b[2]-b[0]<=maxwidth and b[3]-b[1]<=maxheight: return f
    raise RuntimeError('Text does not fit safely; shorten thumbnail text')

def cover(image, size):
    return ImageOps.fit(image.convert('RGB'),size,method=Image.Resampling.LANCZOS,centering=(.5,.5))

def generate_openai_illustration(prompt, model, api_key):
    payload={'model':model,'prompt':prompt + '\nCreate artwork WITHOUT ANY text, letters, labels, numbers, logos or watermark. This is conceptual illustration, not a record of a real experiment.','size':'1536x1024','n':1}
    req=urllib.request.Request('https://api.openai.com/v1/images/generations',data=json.dumps(payload).encode(),headers={'Authorization':f'Bearer {api_key}','Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req,timeout=180) as resp: data=json.load(resp)
        item=data['data'][0]
        if item.get('b64_json'): raw=base64.b64decode(item['b64_json'])
        elif item.get('url'):
            with urllib.request.urlopen(item['url'],timeout=180) as r: raw=r.read()
        else: raise RuntimeError('Image API response lacked image bytes')
        return Image.open(io.BytesIO(raw)).convert('RGB')
    except (urllib.error.HTTPError,urllib.error.URLError,KeyError,ValueError) as e:
        raise RuntimeError(f'AI image generation failed: {e}') from e

def render_frame(src, outpath, text, channel, idx, fontfile, illustrated=False):
    w,h=1280,720
    im=cover(src,(w,h)); im=ImageEnhance.Contrast(im).enhance(1.12); im=ImageEnhance.Color(im).enhance(1.12)
    # Three visually different graphic treatments; footage timestamps are different too.
    layer=Image.new('RGBA',(w,h),(0,0,0,0)); ld=ImageDraw.Draw(layer)
    if idx in (0,1):
        for z in range(65):
            alpha=int(190*(1-z/65)**1.4)
            if idx==0: ld.rectangle((z*11,0,z*11+11,h),fill=(7,16,23,alpha))
            else: ld.rectangle((w-(z+1)*11,0,w-z*11,h),fill=(7,16,23,alpha))
    else:
        for z in range(37):
            alpha=int(185*(1-z/37)**1.1)
            ld.rectangle((0,h-(z+1)*8,w,h-z*8),fill=(7,16,23,alpha))
    im=Image.alpha_composite(im.convert('RGBA'),layer)
    d=ImageDraw.Draw(im)
    fill=COLORS[channel][idx]
    maxw=530 if idx<2 else 1000
    maxh=175
    f=fit_font(d,text,fontfile,maxw,maxh)
    bbox=d.textbbox((0,0),text,font=f,stroke_width=7)
    tw=bbox[2]-bbox[0]
    if idx==0: x=62; y=255
    elif idx==1: x=w-62-tw; y=255
    else: x=(w-tw)//2; y=522
    d.text((x,y),text,font=f,fill=fill,stroke_width=7,stroke_fill=(0,0,0,255))
    if illustrated:
        f2=ImageFont.truetype(fontfile,34)
        d.rounded_rectangle((26,20,166,73),radius=11,fill=(0,0,0,210))
        d.text((39,23),'示意圖',font=f2,fill=(255,255,255,255))
    im.convert('RGB').save(outpath,format='PNG',optimize=True)
    return im.convert('RGB')

def main():
    parser=argparse.ArgumentParser(description='Export three YouTube thumbnails from real video frames; optional illustrated AI background')
    parser.add_argument('--video',required=True,help='Path to finished MP4/MOV file')
    parser.add_argument('--title',required=True,help='Truthful working title for manifest')
    parser.add_argument('--channel',choices=['natural','aiwatch'],default='natural')
    parser.add_argument('--output',required=True)
    parser.add_argument('--concepts-json',help='JSON file containing {"candidates":[{"text":"...","visual_prompt":"..."}, ...]} (exactly 3)')
    parser.add_argument('--font',help='Path to licensed Traditional Chinese font (.ttf/.ttc/.otf)')
    parser.add_argument('--ai-provider',choices=['none','openai'],default='none',help='OpenAI mode requires explicit illustration consent')
    parser.add_argument('--allow-illustration',action='store_true',help='Explicitly permit AI-generated conceptual illustrations')
    parser.add_argument('--ai-model',default=os.environ.get('THUMBNAIL_IMAGE_MODEL','gpt-image-1.5'))
    parser.add_argument('--sample-count',type=int,default=18)
    args=parser.parse_args()
    if args.sample_count<6 or args.sample_count>120: parser.error('--sample-count must be from 6 to 120')
    video=Path(args.video).resolve(); out=Path(args.output).resolve()
    if not video.is_file(): parser.error('video file not found')
    if args.ai_provider!='none' and not args.allow_illustration: parser.error('AI generation requires --allow-illustration')
    if args.ai_provider=='openai' and not os.environ.get('OPENAI_API_KEY'): parser.error('OPENAI_API_KEY not configured')
    for dep in ['ffmpeg','ffprobe']:
        if not shutil.which(dep): parser.error(f'Missing dependency: {dep}')
    fp=font_path(args.font); out.mkdir(parents=True,exist_ok=True)
    concept_data=None
    if args.concepts_json:
        concept_data=json.loads(Path(args.concepts_json).read_text(encoding='utf-8'))
        if not isinstance(concept_data.get('candidates'),list) or len(concept_data['candidates'])!=3: parser.error('concepts JSON requires exactly three candidates')
    concepts=concept_data['candidates'] if concept_data else [{'text':t,'visual_prompt':''} for t in DEFAULT_TEXT[args.channel]]
    for c in concepts:
        if not isinstance(c.get('text'),str) or not 1<=len(c['text'])<=8: parser.error('Each thumbnail text must contain 1–8 characters')
    duration=duration_seconds(video)
    timestamps = [candidate.get('timestamp_sec') for candidate in concepts]
    for timestamp in timestamps:
        if timestamp is None:
            continue
        if type(timestamp) not in (int, float) or not 0 <= timestamp < duration:
            parser.error('Each timestamp_sec must be a number inside the video duration')

    selected, scored = [None] * len(concepts), []
    if any(timestamp is None for timestamp in timestamps):
        selected, scored = sample(video, out, duration, args.sample_count)
    for index, timestamp in enumerate(timestamps):
        if timestamp is None:
            continue
        frame_dir = out / 'source_frames'
        frame_dir.mkdir(exist_ok=True)
        destination = frame_dir / f'candidate_{"ABC"[index]}.jpg'
        extract_frame(video, timestamp, destination)
        selected[index] = {'path': str(destination), 'timestamp_sec': timestamp}
    rendered=[]; report={'version':'1.1','title':args.title,'channel':args.channel,'video_path':str(video),'video_duration_sec':round(duration,2),'image_source':'generated_illustration' if args.ai_provider!='none' else 'authentic_video_frames','ai_provider':args.ai_provider,'selection_method':'concept timestamps when supplied; heuristic sharpness/brightness fallback','human_review_required':True,'automatically_published':False,'source_frames':selected,'candidates':[],'warnings':['AI/agent should review factual correctness and actual footage before publishing.','Thumbnail quality scores are not CTR estimates.']}
    for i,(candidate,frame) in enumerate(zip(concepts,selected)):
        suffix='ABC'[i]; text=candidate['text']; prompt=candidate.get('visual_prompt') or f'Conceptual background related to: {args.title}. {text}. Clean cinematic image with a strong single subject.'
        if args.ai_provider=='openai':
            img=generate_openai_illustration(prompt,args.ai_model,os.environ['OPENAI_API_KEY'])
        else: img=Image.open(frame['path']).convert('RGB')
        filename=f'thumbnail_{suffix}.png'; visual=render_frame(img,out/filename,text,args.channel,i,fp,illustrated=args.ai_provider!='none')
        preview=visual.resize((160,90),Image.Resampling.LANCZOS)
        preview.save(out/f'thumbnail_{suffix}_mobile.jpg',quality=90)
        rendered.append(visual)
        report['candidates'].append({'id':suffix,'file':filename,'mobile_preview':f'thumbnail_{suffix}_mobile.jpg','thumbnail_text':text,'video_timestamp_sec':frame['timestamp_sec'],'source_frame':frame['path'],'visual_prompt':prompt if args.ai_provider!='none' else None,'width':1280,'height':720,'generated':True,'illustration_label':args.ai_provider!='none','review_status':'PENDING_HUMAN_REVIEW'})
    contact=Image.new('RGB',(660,3*402),(245,245,245)); d=ImageDraw.Draw(contact)
    for i,im in enumerate(rendered):
        contact.paste(im.resize((640,360)),(10,10+i*402)); d.text((12,371+i*402),f'Candidate {"ABC"[i]} - {concepts[i]["text"]}',fill='black',font=ImageFont.truetype(fp,22))
    contact.save(out/'thumbnail_contact_sheet.jpg',quality=90)
    report['sampled_frames']=len(scored)
    (out/'thumbnail_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'status':'RENDERED_REVIEW_REQUIRED','outputs':[str(out/f'thumbnail_{s}.png') for s in 'ABC'],'contact_sheet':str(out/'thumbnail_contact_sheet.jpg'),'report':str(out/'thumbnail_report.json')},ensure_ascii=False,indent=2))
if __name__=='__main__':
    try: main()
    except Exception as e:
        print(f'ERROR: {e}',file=sys.stderr)
        sys.exit(2)
