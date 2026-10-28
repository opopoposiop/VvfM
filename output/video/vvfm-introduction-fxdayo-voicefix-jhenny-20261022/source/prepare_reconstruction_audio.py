#!/usr/bin/env python3
"""Retain existing Jhenny speech and insert the two new PMX 2.1 explanations."""
from pathlib import Path
import json,re,wave,subprocess
import numpy as np
ROOT=Path(__file__).resolve().parents[1];SR=48000
scenes=json.loads((ROOT/'source/scenes.json').read_text());TOTAL=sum(s['duration']for s in scenes)
old=json.loads((ROOT/'source/reference-198s/scenes.json').read_text())
oldcaps=json.loads((ROOT/'source/reference-198s/captions.json').read_text())
oldalign=json.loads((ROOT/'source/reference-198s/audio-alignment.json').read_text())['scenes']
with wave.open(str(ROOT/'assets/narration-198s-reference.wav'),'rb')as w:
 assert w.getnchannels()==1 and w.getframerate()==SR
 original=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float32)/32768
out=np.zeros(TOTAL*SR,np.float32);caps=[];alignment=[]
for s in scenes:
 if s['id']in(12,13):continue
 oldid=s['id']if s['id']<12 else s['id']-2
 prev=old[oldid-1];delta=s['start']-prev['start']
 a=oldalign[oldid-1].copy();assert a['end']<prev['start']+s['duration']-.2
 length=s['duration']*SR;start=s['start']*SR;src=prev['start']*SR
 out[start:start+length]=original[src:src+length]
 a['scene']=s['id'];a['start']+=delta;a['end']+=delta;a['reused_from_scene']=oldid
 alignment.append(a)
 for c in oldcaps:
  if c['scene']==oldid:caps.append({**c,'scene':s['id'],'start':c['start']+delta,'end':c['end']+delta})
# The cut lies in the measured pause between the two paragraphs.
for n,a,b,sentences in [(12,0,6.50,[(0,6.20)]),(13,6.50,14.994285714285715,[(6.76,10.38),(10.38,14.32)])]:
 s=scenes[n-1];tempo=.95;offset=s['start']+.55
 pcm=subprocess.check_output(['/opt/homebrew/bin/ffmpeg','-v','error','-ss',str(a),'-t',str(b-a),'-i',str(ROOT/'assets/jhenny-pmx21-original.wav'),'-af',f'atempo={tempo},afade=t=in:d=0.015,afade=t=out:st={(b-a)/tempo-.03}:d=0.03','-f','f32le','-ac','1','-ar',str(SR),'-'])
 clip=np.frombuffer(pcm,dtype='<f4');index=round(offset*SR)
 assert index+len(clip)<(s['start']+s['duration']-.2)*SR
 out[index:index+len(clip)]=clip
 alignment.append({'scene':n,'source_file':'assets/jhenny-pmx21-original.wav','source_start':a,'source_end':b,'start':offset,'end':offset+len(clip)/SR,'tempo':tempo,'script':s['narration']})
 parts=re.findall(r'[^。]+。?',s['narration']);assert len(parts)==len(sentences)
 for text,(x,y)in zip(parts,sentences):caps.append({'scene':n,'text':text,'start':max(offset,offset+(x-a)/tempo-.07),'end':min(s['start']+s['duration']-.25,offset+(y-a)/tempo+.2)})
caps.sort(key=lambda c:c['start']);alignment.sort(key=lambda a:a['scene'])
for i in range(len(caps)-1):caps[i]['end']=min(caps[i]['end'],caps[i+1]['start']-.04)
with wave.open(str(ROOT/'assets/narration-aligned-raw.wav'),'wb')as w:
 w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((np.clip(out,-1,1)*32767).astype('<i2').tobytes())
(ROOT/'source/captions.json').write_text(json.dumps(caps,ensure_ascii=False,indent=2)+'\n')
(ROOT/'source/audio-alignment.json').write_text(json.dumps({'duration':TOTAL,'original_voice_reused':True,'scenes':alignment},ensure_ascii=False,indent=2)+'\n')
def stamp(t):
 ms=round(t*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
 return f'{h:02}:{m:02}:{s:02},{ms:03}'
def wrap(text):
 if len(text)<=37:return text
 k=min(range(max(8,len(text)-42),min(len(text)-7,43)),key=lambda k:(0 if text[k-1]in'、。'else 100)+abs(k-len(text)/2))
 return text[:k]+'\n'+text[k:]
(ROOT/'VvfM_紹介動画_PMX21追加_日本語字幕.srt').write_text('\n'.join(f'{i}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{wrap(c["text"])}\n'for i,c in enumerate(caps,1)))
meta=[';FFMETADATA1','title=VMD Viewer for Mac 紹介動画 PMX 2.1追加版','artist=VMD Viewer for Mac','comment=AI narration: HeyGen Jhenny']
for s in scenes:meta+=['[CHAPTER]','TIMEBASE=1/1000',f'START={s["start"]*1000}',f'END={(s["start"]+s["duration"])*1000}',f'title={s["id"]:02} {s["title"]}']
(ROOT/'source/chapters.ffmeta').write_text('\n'.join(meta)+'\n')
print(f'{TOTAL}s; {len(scenes)} scenes; {len(caps)} subtitle cues')
for a in alignment:print(f'Scene {a["scene"]:02}: speech {a["start"]:.2f}–{a["end"]:.2f}s')
