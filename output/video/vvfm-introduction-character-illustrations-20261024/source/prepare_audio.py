#!/usr/bin/env python3
"""Align the verified Jhenny speech, create two mixes, and caption sidecars."""
from pathlib import Path
import re,json,difflib,subprocess,wave
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
SR=48000;TOTAL=198
scenes=json.loads((ROOT/'source/scenes.json').read_text())
asr=json.loads((ROOT/'checks/jhenny-transcript.json').read_text())
# Normalization changes spelling only, never the delivered script.
replacements=[('VMD Viewer for Mac','ブイエムディービューアーフォーマック'),('VMDビューワーfor Mac','ブイエムディービューアーフォーマック'),('VMD','ブイエムディー'),('PMX','ピーエムエックス'),('MMD','エムエムディー'),('WAV','ウェーブ'),('Mac','マック'),('Windows','ウィンドウズ'),('3D','スリーディー'),('3.25','さんてんにご'),('2.75','にてんななご'),('2.1','にてんいち'),('HQ','エイチキュー'),('DoF','ディーオーエフ'),('DOF','ディーオーエフ'),('CPU','シーピーユー'),('GPU','ジーピーユー')]
def norm(t):
 for a,b in replacements:t=re.sub(re.escape(a),b,t,flags=re.I)
 return re.sub(r'[\s、。・,.!?！？「」『』：:<>/ー\-]','',t).lower()
# Word alignment from a separate local speech-recognition pass.
actual=[];char_times=[]
for seg in asr['segments']:
 words=seg.get('words') or [{'word':seg['text'],'start':seg['start'],'end':seg['end']}]
 for word in words:
  txt=norm(word['word']);n=len(txt)
  for i,c in enumerate(txt):
   actual.append(c);char_times.append((word['start']+(word['end']-word['start'])*i/max(1,n),word['start']+(word['end']-word['start'])*(i+1)/max(1,n)))
expected=''.join(norm(s['spoken'])for s in scenes);actual=''.join(actual)
matcher=difflib.SequenceMatcher(None,expected,actual,autojunk=False)
mapidx={}
for a,b,n in matcher.get_matching_blocks():
 for k in range(n):mapidx[a+k]=b+k
coverage=len(mapidx)/len(expected)
print(f'Normalized recognized-text match: {coverage:.3%}')
if coverage<.75:raise SystemExit('ASR match too low; review transcript before alignment')
known=np.array(sorted(mapidx));vals=np.array([mapidx[k]for k in known])
def where(i,edge=0):
 idx=int(round(float(np.interp(i,known,vals))));return char_times[max(0,min(len(char_times)-1,idx))][edge]
# A manual override can refine known recognition spelling errors or pause cuts.
override_file=ROOT/'source/audio-boundaries.json'
overrides=json.loads(override_file.read_text())if override_file.exists()else{}
with wave.open(str(ROOT/'assets/jhenny-original.wav'),'rb')as w:
 assert w.getnchannels()==1 and w.getsampwidth()==2 and w.getframerate()==SR
 original=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float32)/32768
raw=[];cursor=0
for s in scenes:
 length=len(norm(s['spoken']));a=where(cursor);b=where(cursor+length-1,1)
 if str(s['id'])in overrides:a,b=overrides[str(s['id'])]
 raw.append((max(0,a-.09),min(len(original)/SR,b+.13)));cursor+=length
# Never cross a neighboring spoken paragraph.
for i in range(len(raw)-1):
 if raw[i][1]>raw[i+1][0]:
  cut=(raw[i][1]+raw[i+1][0])/2;raw[i]=(raw[i][0],cut);raw[i+1]=(cut,raw[i+1][1])
full=np.zeros(TOTAL*SR,np.float32);captions=[];alignment=[];cursor=0
for s,(a,b)in zip(scenes,raw):
 source=ROOT/'assets/jhenny-original.wav'
 sentence_where=where;sentence_cursor=cursor
 if s['id']==6:
  source=ROOT/'assets/jhenny-scene06-original.wav'
  with wave.open(str(source),'rb')as w:a,b=0,w.getnframes()/w.getframerate()
  repair=json.loads((ROOT/'checks/jhenny-scene06-transcript.json').read_text())
  repair_chars=[];repair_times=[]
  for seg in repair['segments']:
   for word in seg['words']:
    txt=norm(word['word']);n=len(txt)
    for i,c in enumerate(txt):
     repair_chars.append(c);repair_times.append((word['start']+(word['end']-word['start'])*i/max(1,n),word['start']+(word['end']-word['start'])*(i+1)/max(1,n)))
  repair_expected=norm(s['spoken']);repair_map={}
  for x,y,n in difflib.SequenceMatcher(None,repair_expected,''.join(repair_chars),autojunk=False).get_matching_blocks():
   for k in range(n):repair_map[x+k]=y+k
  if len(repair_map)/len(repair_expected)<.95:raise SystemExit('Repair speech needs review')
  repair_known=np.array(sorted(repair_map));repair_vals=np.array([repair_map[k]for k in repair_known])
  def repair_where(i,edge=0):
   idx=int(round(float(np.interp(i,repair_known,repair_vals))));return repair_times[max(0,min(len(repair_times)-1,idx))][edge]
  sentence_where=repair_where;sentence_cursor=0
 maxdur=s['duration']-1.2
 tempo=max(1.0 if s['id']==6 else .90,(b-a)/maxdur)
 if tempo>1.14:raise SystemExit(f'Scene {s["id"]} needs a boundary review: tempo {tempo:.2f}')
 offset=s['start']+.65
 pcm=subprocess.check_output(['/opt/homebrew/bin/ffmpeg','-hide_banner','-loglevel','error','-ss',str(a),'-t',str(b-a),'-i',str(source),'-af',f'atempo={tempo:.8f},afade=t=in:d=0.015,afade=t=out:st={(b-a)/tempo-.03:.5f}:d=0.03','-f','f32le','-ac','1','-ar',str(SR),'-'])
 clip=np.frombuffer(pcm,dtype='<f4');idx=int(offset*SR)
 if idx+len(clip)>int((s['start']+s['duration']-.2)*SR):raise SystemExit('Speech crosses a scene boundary')
 full[idx:idx+len(clip)]+=clip
 entry={'scene':s['id'],'source_file':str(source.relative_to(ROOT)),'source_start':a,'source_end':b,'start':offset,'end':offset+len(clip)/SR,'tempo':tempo,'script':s['narration']};alignment.append(entry)
 # Sentence text remains the original Markdown wording; timing follows speech.
 displayparts=[p for p in re.findall(r'[^。]+。?',s['narration'])if p]
 spokenparts=[p for p in re.findall(r'[^。]+。?',s['spoken'])if p]
 if len(displayparts)!=len(spokenparts):raise SystemExit('Sentence count mismatch')
 for txt,sp in zip(displayparts,spokenparts):
  length=len(norm(sp));t0=offset+(sentence_where(sentence_cursor)-a)/tempo;t1=offset+(sentence_where(sentence_cursor+length-1,1)-a)/tempo
  t0=max(offset,t0-.07);t1=min(s['start']+s['duration']-.35,max(t0+.4,t1+.2))
  captions.append({'scene':s['id'],'text':txt,'start':t0,'end':t1});cursor+=length;sentence_cursor+=length
# Resolve overlaps with a short, clean boundary.
for i in range(len(captions)-1):captions[i]['end']=min(captions[i]['end'],captions[i+1]['start']-.04)
def writewav(p,x):
 x=np.clip(x,-1,1)
 with wave.open(str(p),'wb')as w:w.setnchannels(1 if x.ndim==1 else x.shape[1]);w.setsampwidth(2);w.setframerate(SR);w.writeframes((x*32767).astype('<i2').tobytes())
writewav(ROOT/'assets/narration-aligned-raw.wav',full)
(ROOT/'source/audio-alignment.json').write_text(json.dumps({'recognition_match':coverage,'scenes':alignment},ensure_ascii=False,indent=2)+'\n')
(ROOT/'source/captions.json').write_text(json.dumps(captions,ensure_ascii=False,indent=2)+'\n')
def timefmt(t,srt=False):
 unit=1000 if srt else 100;tick=round(t*unit);h,tick=divmod(tick,3600*unit);m,tick=divmod(tick,60*unit);sec,frac=divmod(tick,unit)
 return f'{h:02}:{m:02}:{sec:02},{frac:03}'if srt else f'{h}:{m:02}:{sec:02}.{frac:02}'
def wrap(t):
 if len(t)<=37:return t
 mid=len(t)/2;lo=max(8,len(t)-42);hi=min(len(t)-7,43)
 k=min(range(lo,hi),key=lambda k:(0 if t[k-1]in'、。' else 100)+abs(k-mid))
 return t[:k]+'\n'+t[k:]
srt=[];events=[]
for i,c in enumerate(captions,1):
 text=wrap(c['text']);srt.append(f'{i}\n{timefmt(c["start"],True)} --> {timefmt(c["end"],True)}\n{text}\n')
 text=text.replace('\n',r'\N')
 events.append(f'Dialogue: 0,{timefmt(c["start"])},{timefmt(c["end"])},Default,,0,0,0,,{text}')
(ROOT/'VvfM_紹介動画_日本語字幕.srt').write_text('\n'.join(srt))
ass='''[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nWrapStyle: 2\nScaledBorderAndShadow: yes\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,Hiragino Maru Gothic ProN,39,&H00322620,&H00322620,&H00F6FAFA,&H00F6FAFA,-1,0,0,0,100,100,0,0,1,0,0,2,80,80,25,1\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'''
(ROOT/'source/captions.ass').write_text(ass+'\n'.join(events)+'\n')
meta=[';FFMETADATA1','title=VMD Viewer for Mac 紹介動画','artist=VMD Viewer for Mac','comment=AI narration: HeyGen Jhenny']
for s in scenes:meta+=['[CHAPTER]','TIMEBASE=1/1000',f'START={s["start"]*1000}',f'END={(s["start"]+s["duration"])*1000}',f'title={s["id"]:02} {s["title"]}']
(ROOT/'source/chapters.ffmeta').write_text('\n'.join(meta)+'\n')
print('Aligned 13 scenes and wrote',len(captions),'Japanese subtitle cues')
for a in alignment:print(f'{a["scene"]:02}: {a["source_start"]:.2f}–{a["source_end"]:.2f} -> {a["start"]:.2f}–{a["end"]:.2f}, tempo {a["tempo"]:.3f}')
