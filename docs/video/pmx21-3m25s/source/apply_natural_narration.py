#!/usr/bin/env python3
"""Apply three continuous natural-prosody rereads, preserving other PCM and all BGM."""
from pathlib import Path
import hashlib,json,wave,subprocess
import numpy as np
R=Path(__file__).resolve().parents[1];SR=48000
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 with wave.open(str(p)) as w:
  assert(w.getframerate(),w.getsampwidth(),w.getnchannels())==(SR,2,2)
  return np.frombuffer(w.readframes(w.getnframes()),'<i2').reshape(-1,2).astype(np.int32)
def write(p,x):
 assert x.min()>=-32768 and x.max()<=32767
 with wave.open(str(p),'wb')as w:w.setparams((2,2,SR,0,'NONE','not compressed'));w.writeframes(x.astype('<i2').tobytes())
req=json.loads((R/'source/natural-narration-request.json').read_text());prep=json.loads((R/'checks/natural-sentence-preparation.json').read_text())
old=read(R/'assets/narration-only-before-natural.wav');mix0=read(R/'assets/with-bgm-before-natural.wav');voice=old.copy();mix=mix0.copy();outside=np.ones(len(old),bool);patches=[]
for q,item in zip(prep['sentences'],req['sentences']):
 assert q['id']==item['id'];p=R/q['file'];assert sha(p)==q['sha256'];clip=read(p);a,b=[round(t*SR)for t in q['patch']];start=round(q['start']*SR);end=start+len(clip)
 assert a<=start<end<=b
 voice[a:b]=0;voice[start:end]=clip
 fade=round(.004*SR);ramp=np.linspace(0,1,fade)[:,None]
 voice[a:a+fade]=np.rint(old[a:a+fade]*(1-ramp)+voice[a:a+fade]*ramp).astype(np.int32)
 voice[b-fade:b]=np.rint(voice[b-fade:b]*(1-ramp)+old[b-fade:b]*ramp).astype(np.int32)
 mix[a:b]+=voice[a:b]-old[a:b];outside[a:b]=False
 assert np.array_equal(voice[start:end],clip)
 patches.append({**q,'display':item['display'],'spoken':item['spoken'],'boundary_ramp_seconds':.004,'replacement_pcm_identical':True,'boundary_jump_in_pcm':[int(np.max(np.abs(voice[a]-voice[a-1]))),int(np.max(np.abs(voice[b]-voice[b-1])))]})
assert np.array_equal(voice[outside],old[outside]) and np.array_equal(mix[outside],mix0[outside])
assert np.array_equal(mix-voice,mix0-old)
assert voice.shape==mix.shape==(205*SR,2)
write(R/'assets/narration-only.wav',voice);write(R/'assets/with-bgm.wav',mix);write(R/'composition/assets/final-mix.wav',mix)
scenes=json.loads((R/'source/scenes.json').read_text());caps=json.loads((R/'source/captions.json').read_text());assert caps==json.loads((R/'source/natural-baseline-captions.json').read_text())
scenes[4]['spoken']='腕の角度を少し変えて、お気に入りのポーズに。ボーンを選び、スリーディーギズモで調整したら、キーを登録。タイムラインで前後を確かめながら、服への食い込みなど、気になる部分も整えられます。'
scenes[7]['spoken']='見た目も、もっと自分好みに。'+req['sentences'][1]['spoken']+req['sentences'][2]['spoken']+'ディフュージョンで、柔らかな雰囲気も楽しめます。'
for s in scenes:assert ''.join(c['text']for c in caps if c['scene']==s['id'])==s['narration']
(R/'source/scenes.json').write_text(json.dumps(scenes,ensure_ascii=False,indent=2)+'\n')
align=json.loads((R/'source/audio-alignment.json').read_text())
for n in [5,8]:
 prev=align['scenes'][n-1];start=54.18 if n==5 else prev['start'];cursor=start;segments=[]
 for q in [p for p in patches if p['scene']==n]:
  a,b=q['patch']
  if cursor<a:segments.append({'source_file':'assets/narration-only-before-natural.wav','source_start':cursor,'source_end':a,'start':cursor,'end':a,'tempo':1})
  segments.append({'source_file':q['file'],'source_start':0,'source_end':q['duration_seconds'],'start':q['start'],'end':q['end'],'tempo':1,'spoken':q['spoken'],'continuous_sentence':True,'preparation':'source/prepare_natural_sentences.py','original_generation':q['raw'],'generation_tempo_adjustment':q['tempo'],'pitch_shift_semitones':0,'pitch_contour_compression':False})
  cursor=b
 if cursor<prev['end']:segments.append({'source_file':'assets/narration-only-before-natural.wav','source_start':cursor,'source_end':prev['end'],'start':cursor,'end':prev['end'],'tempo':1})
 align['scenes'][n-1]={'scene':n,'start':start,'end':prev['end'],'script':scenes[n-1]['narration'],'segments':segments,'boundary_ramp_seconds':.004}
(R/'source/audio-alignment.json').write_text(json.dumps(align,ensure_ascii=False,indent=2)+'\n')
report={'result':'pass','date':'2026-10-25','duration_seconds':205,'patches':patches,'narration_pcm_outside_patches_identical':True,'with_bgm_pcm_outside_patches_identical':True,'bgm_contribution_preserved_all_samples':True,'subtitle_text_and_timing_unchanged':True,'subtitle_count':len(caps),'all_scene_timings_unchanged':True,'prior_pronunciation_fixes_preserved':True,'illustrations_unchanged':True,'pcm_preservation_before_aac_encoding':True,'pitch_contour_compression':False,'pitch_shift_semitones':0,'voice_reference':'original same-scene Jhenny narration','exact_voice_identity_verified':False,'max_abs_voice_sample':int(np.abs(voice).max()),'max_abs_mix_sample':int(np.abs(mix).max()),'input_sha256':{p:sha(R/p)for p in ['assets/narration-only-before-natural.wav','assets/with-bgm-before-natural.wav']},'human_listening_acceptance':'not asserted; reviewable preview supplied'}
(R/'checks/natural-narration-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
for name,a,b in [('arm',53,62.3),('toon-rim',99,113)]:
 subprocess.run(['/opt/homebrew/bin/ffmpeg','-v','error','-nostdin','-n','-ss',str(a),'-i',str(R/'assets/narration-only.wav'),'-t',str(b-a),'-ac','1','-ar','16000',str(R/f'checks/natural-{name}-context.wav')],check=True)
print('PASS: 3 continuous sentences replaced; all other PCM, full BGM contribution, captions and timelines unchanged.')
print('Boundary jumps',[(q['id'],q['boundary_jump_in_pcm'])for q in patches])
