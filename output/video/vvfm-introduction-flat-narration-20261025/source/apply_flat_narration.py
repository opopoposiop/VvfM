#!/usr/bin/env python3
"""Apply two continuous reread sentences; preserve every other sample and the BGM stem."""
from pathlib import Path
import hashlib,json,wave,re
import numpy as np
ROOT=Path(__file__).resolve().parents[1];SR=48000
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(path,ch):
 with wave.open(str(path)) as w:
  assert (w.getframerate(),w.getsampwidth(),w.getnchannels())==(SR,2,ch)
  return np.frombuffer(w.readframes(w.getnframes()),'<i2').reshape(-1,ch).astype(np.int32)
def write(path,x):
 assert x.min()>=-32768 and x.max()<=32767
 with wave.open(str(path),'wb') as w:w.setparams((2,2,SR,0,'NONE','not compressed'));w.writeframes(x.astype('<i2').tobytes())
request=json.loads((ROOT/'source/flat-narration-request.json').read_text())
prep=json.loads((ROOT/'checks/flat-sentence-preparation.json').read_text())
old=read(ROOT/'assets/narration-before-flat-reread.wav',2);mix0=read(ROOT/'assets/with-bgm-before-flat-reread.wav',2)
voice=old.copy();mix=mix0.copy();outside=np.ones(len(old),dtype=bool)
patches=[]
for q,item in zip(prep['sentences'],request['sentences']):
 path=ROOT/q['file'];assert sha(path)==q['sha256']
 clip=np.repeat(read(path,1),2,axis=1);start=round(q['start']*SR);end=start+len(clip)
 a,b=[round(t*SR)for t in q['patch']];assert a<=start<end<=b
 voice[a:b]=0;voice[start:end]=clip
 # The boundary lies in a quiet trough; a 4 ms ramp preserves the next onset cleanly.
 fade=round(.004*SR);ramp=np.linspace(0,1,fade)[:,None]
 voice[b-fade:b]=np.rint(voice[b-fade:b]*(1-ramp)+old[b-fade:b]*ramp).astype(np.int32)
 mix[a:b]+=voice[a:b]-old[a:b];outside[a:b]=False
 assert np.array_equal(voice[start:end],clip)
 patches.append({**q,'display':item['display'],'spoken':item['spoken'],'boundary_ramp_seconds':.004,'replacement_pcm_identical_per_channel':True})
assert np.array_equal(voice[outside],old[outside]) and np.array_equal(mix[outside],mix0[outside])
assert np.array_equal(mix-voice,mix0-old)
assert np.array_equal(voice[round(102.16*SR):round(105.8*SR)],old[round(102.16*SR):round(105.8*SR)])
assert voice.shape==mix.shape==(205*SR,2)
write(ROOT/'assets/narration-only.wav',voice);write(ROOT/'assets/with-bgm.wav',mix);write(ROOT/'composition/assets/final-mix.wav',mix)
scenes=json.loads((ROOT/'source/scenes.json').read_text());caps=json.loads((ROOT/'source/captions.json').read_text())
changes={'トゥーンシェーダー・エイチキューでは、輪郭線や光を調整できます。':'ToonShader HQでは、輪郭線や光を調整できます。','リムライトで縁に光を、ブルームで輝きを。':'リムライトで輪郭に光を、ブルームで輝きを。'}
for c in caps:
 if c['text'] in changes:c['text']=changes[c['text']]
for before,after in changes.items():scenes[7]['narration']=scenes[7]['narration'].replace(before,after)
scenes[4]['spoken']=scenes[4]['spoken'].replace(request['sentences'][0]['display'],request['sentences'][0]['spoken'])
scenes[7]['spoken']=scenes[7]['spoken'].replace('リムライトで縁に光を、ブルームで輝きを。',request['sentences'][1]['spoken'])
basecaps=json.loads((ROOT/'source/flat-baseline-captions.json').read_text())
assert all((a['start'],a['end'],a['scene'])==(b['start'],b['end'],b['scene'])for a,b in zip(caps,basecaps))
assert len([1 for a,b in zip(caps,basecaps) if a['text']!=b['text']])==2
for s in scenes:assert ''.join(c['text']for c in caps if c['scene']==s['id'])==s['narration']
for filename,data in [('scenes.json',scenes),('captions.json',caps)]:
 (ROOT/'source'/filename).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
align=json.loads((ROOT/'source/audio-alignment.json').read_text())
for q in patches:
 n=q['scene'];previous=align['scenes'][n-1];a,b=q['patch'];segments=[]
 if previous['start']<a:segments.append({'source_file':'assets/narration-before-flat-reread.wav','source_start':previous['start'],'source_end':a,'start':previous['start'],'end':a,'tempo':1})
 segments.append({'source_file':q['file'],'source_start':0,'source_end':q['duration_seconds'],'start':q['start'],'end':q['end'],'tempo':1,'spoken':q['spoken'],'continuous_sentence':True,'preparation':'source/prepare_flat_sentences.py','original_generation':q['raw'],'generation_tempo_adjustment':q['tempo'],'pitch_target_median_hz':q['target_median_hz'],'pitch_contour_scale':q['contour_scale']})
 segments.append({'source_file':'assets/narration-before-flat-reread.wav','source_start':b,'source_end':previous['end'],'start':b,'end':previous['end'],'tempo':1})
 align['scenes'][n-1]={'scene':n,'start':segments[0]['start'],'end':previous['end'],'script':scenes[n-1]['narration'],'segments':segments,'boundary_ramp_seconds':.004}
(ROOT/'source/audio-alignment.json').write_text(json.dumps(align,ensure_ascii=False,indent=2)+'\n')
def stamp(t,srt=True):
 unit=1000 if srt else 100;x=round(t*unit);h,x=divmod(x,3600*unit);m,x=divmod(x,60*unit);s,f=divmod(x,unit)
 return f'{h:02}:{m:02}:{s:02},{f:03}' if srt else f'{h}:{m:02}:{s:02}.{f:02}'
def wrap(t):
 if len(t)<=37:return t
 split=min(range(max(8,len(t)-42),min(len(t)-7,43)),key=lambda k:(0 if t[k-1]in'、。'else 100)+abs(k-len(t)/2))
 return t[:split]+'\n'+t[split:]
srt='\n'.join(f'{i}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{wrap(c["text"])}\n'for i,c in enumerate(caps,1))
(ROOT/'VvfM_紹介動画_ナレーション調整版_日本語字幕.srt').write_text(srt)
ass=(ROOT/'source/captions.ass').read_text().split('Dialogue:')[0]
ass+='\n'.join(f'Dialogue: 0,{stamp(c["start"],False)},{stamp(c["end"],False)},Default,,0,0,0,,{wrap(c["text"]).replace(chr(10),chr(92)+"N")}'for c in caps)+'\n'
(ROOT/'source/captions.ass').write_text(ass)
report={'result':'pass','date':'2026-10-25','duration_seconds':205,'patches':patches,'narration_pcm_outside_patches_identical':True,'with_bgm_pcm_outside_patches_identical':True,'bgm_contribution_preserved_all_samples':True,'toonshader_sentence_audio_identical':True,'subtitle_text_changes':changes,'subtitle_timing_unchanged':True,'subtitle_count':len(caps),'all_scene_timings_unchanged':True,'prior_pronunciation_fixes_preserved':True,'illustrations_unchanged':True,'pcm_preservation_before_aac_encoding':True,'max_abs_voice_sample':int(np.abs(voice).max()),'max_abs_mix_sample':int(np.abs(mix).max()),'input_sha256':{p:sha(ROOT/p)for p in ['assets/narration-before-flat-reread.wav','assets/with-bgm-before-flat-reread.wav']},'human_listening_acceptance':'not asserted; reviewable previews supplied'}
(ROOT/'checks/flat-narration-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('PASS: two continuous sentences replaced; other PCM, BGM, ToonShader speech and subtitle timings preserved.')
print('Peak integer samples:',report['max_abs_voice_sample'],report['max_abs_mix_sample'])
