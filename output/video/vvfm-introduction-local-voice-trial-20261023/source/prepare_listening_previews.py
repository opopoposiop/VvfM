#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,subprocess,re,wave,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT.parent/'vvfm-introduction-sentence-reread-jhenny-20261022'
FF='/opt/homebrew/bin/ffmpeg'; FP='/opt/homebrew/bin/ffprobe'
SR=48000
def run(a): return subprocess.run(a,check=True,text=True,capture_output=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def measure(p):
 r=run([FF,'-hide_banner','-nostdin','-i',str(p),'-af','loudnorm=I=-16:TP=-3:LRA=7:print_format=json','-f','null','-'])
 return json.loads(re.findall(r'\{[^{}]+\}',r.stderr,re.S)[-1])
def read(p):
 with wave.open(str(p)) as w:
  assert w.getframerate()==SR and w.getnchannels()==1 and w.getsampwidth()==2
  return np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').copy()
def write(p,s):
 with wave.open(str(p),'wb') as w:w.setparams((1,2,SR,0,'NONE','not compressed'));w.writeframes(s.astype('<i2').tobytes())
font_path='/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc'
fonts={size:ImageFont.truetype(font_path,size) for size in [30,34,38,46,60]}
entries=[]; comparison=[]
for scene,start,end,clock,textlines in [
 (11,152.55,156.60,'2分34秒',['PMX 2.1のモデルにも','対応しています。']),
 (12,160.55,167.40,'2分43秒',['PMX 2.1のQDEFは、ねじったときの形を','保つための変形方式です。'])]:
 old=ROOT/f'assets/scene{scene}-original-context.wav'
 run([FF,'-v','error','-nostdin','-n','-ss',str(start),'-t',str(end-start),'-i',str(BASE/'assets/narration-only.wav'),'-ac','1','-ar',str(SR),'-c:a','pcm_s16le',str(old)])
 meter=measure(old); target_i=float(meter['input_i'])
 raw=ROOT/f'assets/scene{scene}-local-reference-trial.wav'; m=measure(raw)
 normalized=ROOT/f'VvfM_{clock}_PMX21_一文再合成候補.wav'
 af=(f'loudnorm=I={target_i}:TP=-3:LRA=7:measured_I={m["input_i"]}:measured_TP={m["input_tp"]}:'
     f'measured_LRA={m["input_lra"]}:measured_thresh={m["input_thresh"]}:linear=true,aresample=48000')
 run([FF,'-v','error','-nostdin','-n','-i',str(raw),'-af',af,'-ac','1','-ar',str(SR),'-c:a','pcm_s16le',str(normalized)])
 run([FF,'-v','error','-xerror','-i',str(normalized),'-f','null','-'])
 new_m=measure(normalized)
 assert float(new_m['input_tp'])<-1
 sample=read(normalized)
 entries.append({'scene':scene,'file':normalized.name,'duration':len(sample)/SR,'sha256':sha(normalized),'target_lufs':target_i,'measured_loudness':new_m,'tempo':1,'pitch_shift_semitones':0,'full_decode':'pass'})
 for label,p,color in [('元の音声',old,'#566876'),('ローカル再合成の候補',normalized,'#1a6c5c')]:
  n=len(comparison);samples=read(p)
  padded=np.concatenate([np.zeros(round(.45*SR),dtype='<i2'),samples,np.zeros(round(.60*SR),dtype='<i2')])
  frame_count=math.ceil(len(padded)/SR*24);padded=np.pad(padded,(0,frame_count*SR//24-len(padded)))
  wav=ROOT/f'assets/comparison-{n:02}.wav';write(wav,padded)
  im=Image.new('RGB',(1280,720),'#f5f4f0');draw=ImageDraw.Draw(im)
  draw.rectangle((0,0,1280,16),fill=color)
  draw.text((70,64),'VvfM ナレーション比較',font=fonts[34],fill='#344047')
  draw.text((70,135),clock+'付近',font=fonts[46],fill='#20292d')
  draw.text((70,218),label,font=fonts[60],fill=color)
  for i,line in enumerate(textlines):draw.text((70,340+56*i),line,font=fonts[38],fill='#20292d')
  draw.text((70,515),'指定の読み：ぴーえむえっくす　にーてん　いち',font=fonts[30],fill='#344047')
  draw.text((70,620),'AI生成音声・試聴用／完成動画には未反映',font=fonts[30],fill='#5b6468')
  img=ROOT/f'assets/comparison-{n:02}.png';im.save(img)
  segment=ROOT/f'assets/comparison-{n:02}.mp4'
  run([FF,'-v','error','-nostdin','-n','-loop','1','-framerate','24','-i',str(img),'-i',str(wav),'-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-t',str(frame_count/24),'-movflags','+faststart',str(segment)])
  comparison.append({'label':label,'source':str(p.relative_to(ROOT)),'duration':frame_count/24,'segment':segment.name,'frames':frame_count})
concat=ROOT/'source/comparison-concat.txt'
concat.write_text(''.join("file '../assets/"+x['segment']+"'\n" for x in comparison))
out=ROOT/'VvfM_PMX21_元音声と再合成候補_比較プレビュー.mp4'
run([FF,'-v','error','-nostdin','-n','-f','concat','-safe','0','-i',str(concat),'-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out)])
run([FF,'-v','error','-xerror','-i',str(out),'-map','0:v','-map','0:a','-f','null','-'])
probe=json.loads(run([FP,'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(out)]).stdout)
v=next(x for x in probe['streams'] if x['codec_type']=='video')
assert (v['width'],v['height'],v['r_frame_rate'])==(1280,720,'24/1')
assert int(v['nb_read_frames'])==sum(x['frames'] for x in comparison)
report={'candidates':entries,'comparison':comparison,'comparison_file':out.name,'comparison_sha256':sha(out),'comparison_duration':float(probe['format']['duration']),'comparison_full_decode':'pass','same_voice_perceptual_acceptance':'pending_user_listening','final_video_modified':False,'asr_notes':{'11':'PMX2.1のモデルにも対応しています。','12':'PMX2.1のQDFは、ねじった時の形を保つための変形方式です。','note':'Scene12 acronym recognized as QDF; supplied reading is キューデフ. ASR cannot prove vowel length or identical voice.'}}
(ROOT/'checks/listening-preview-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
