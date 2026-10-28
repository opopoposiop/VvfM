#!/usr/bin/env python3
"""Derive sentence cuts from audio silence near streamed punctuation; review with local ASR."""
from pathlib import Path
import json,re,wave,numpy as np
R=Path(__file__).resolve().parents[1]
def save(p,q):p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
scenes=json.loads((R/'source/scenes.json').read_text());caps=json.loads((R/'source/captions.json').read_text());plan=[]
for scene in scenes:
 sid=scene['id'];q=json.loads((R/'checks'/f'harema-scene{sid:02d}-live.json').read_text())
 assert q['capture_result']=='pass'and q['graceful_close_confirmed']
 norm=lambda t:re.sub(r'[\s、。・,.!?]','',t.replace('アプリ上','あぷりじょう'))
 assert norm(q['input'])==norm(q['transcript']),(sid,'Text mismatch')
 cues=[c for c in caps if c['scene']==sid];sentences=[s+'。'for s in scene['spoken'].split('。')if s]
 periods=[d['captured_audio_seconds']for d in q['transcript_fragments']for _ in range(d['delta'].count('。'))]
 assert len(periods)==len(cues)==len(sentences),(sid,'Sentence count mismatch')
 with wave.open(str(R/q['audio_file']))as w:sr=w.getframerate();y=np.frombuffer(w.readframes(w.getnframes()),'<i2').astype(float)
 block=int(sr*.01);rms=np.array([np.sqrt(np.mean(y[i:i+block]**2))for i in range(0,len(y),block)])
 silent=np.where(rms<70)[0];runs=[]
 for i in silent:
  if not runs or i!=runs[-1][-1]+1:runs.append([i])
  else:runs[-1].append(i)
 pauses=[(z[0]*.01,(z[-1]+1)*.01)for z in runs if len(z)>=25]
 cuts=[]
 for t in periods:
  candidates=[p for p in pauses if t-.05<=p[0]<=t+1.5]
  assert candidates,(sid,t,'No sentence pause')
  p=max(candidates,key=lambda p:p[1]-p[0]);cuts.append(p)
 prev=0
 for n,(period,pause,cue,spoken)in enumerate(zip(periods,cuts,cues,sentences)):
  a=int(prev/.01);b=int(pause[0]/.01)+1;active=np.where(rms[a:b]>70)[0]+a
  assert len(active)>5
  trim=[max(0,active[0]*.01-.06),min(len(y)/sr,(active[-1]+1)*.01+.08)]
  start=cue['start']+.015;end=cue['end']-.02;length=trim[1]-trim[0]
  tempo=max(1,length/(end-start))
  # A brief lead-in for the short app-name caption keeps the full name intelligible.
  if tempo>1.65:
   lower=scene['start']+.35 if n==0 else cues[n-1]['end']+.02
   start=max(lower,end-length/1.65);tempo=max(1,length/(end-start))
  assert tempo<=1.9,(sid,n,tempo)
  plan.append({'cue':len(plan)+1,'scene':sid,'sentence':n+1,'display':cue['text'],'spoken':spoken,'source':q['audio_file'],'trim':[round(float(x),4)for x in trim],'punctuation_audio_seconds':period,'following_silence':pause,'caption':[cue['start'],cue['end']],'start':start,'target_end':end,'tempo':tempo,'pitch_shift_semitones':0,'boundary_method':'Streamed punctuation plus >=250ms measured silence; offline ASR pending'})
  prev=pause[1]
assert len(plan)==41
save(R/'source/harema-alignment-plan.json',plan)
for q in plan:print(q['cue'],q['scene'],q['trim'],round(q['tempo'],3),round(q['start']-q['caption'][0],3),q['display'])
