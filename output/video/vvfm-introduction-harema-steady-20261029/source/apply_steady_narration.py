#!/usr/bin/env python3
"""Normalize phrase-average tempo and constrain F0 locally while preserving video/BGM."""
from pathlib import Path
import json,hashlib,subprocess,re,wave
import numpy as np,parselmouth
from parselmouth.praat import call
R=Path(__file__).resolve().parents[1];FF='/opt/homebrew/bin/ffmpeg';SR=48000;P=json.loads((R/'source/steady-plan.json').read_text())
def save(p,q):p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(a):return subprocess.run(a,capture_output=True,check=True)
def read(p):
 with wave.open(str(p))as w:
  assert(w.getframerate(),w.getsampwidth(),w.getnchannels())==(SR,2,2)
  return np.frombuffer(w.readframes(w.getnframes()),'<i2').astype(np.int32).reshape(-1,2)
def write(p,y):
 assert np.abs(y).max()<32767
 with wave.open(str(p),'wb')as w:w.setparams((2,2,SR,0,'NONE','not compressed'));w.writeframes(y.astype('<i2').tobytes())
def pitch(sound):
 f=sound.to_pitch_ac(time_step=.005,pitch_floor=90,pitch_ceiling=500).selected_array['frequency'];f=f[f>0]
 return f,{'p05':float(np.quantile(f,.05)),'p10':float(np.quantile(f,.1)),'median':float(np.median(f)),'p90':float(np.quantile(f,.9)),'p95':float(np.quantile(f,.95)),'p10_p90_semitones':float(12*np.log2(np.quantile(f,.9)/np.quantile(f,.1)))}
voice=np.zeros((205*SR,2),np.int32);records=[];all_after=[];last_end=0
for q in P['cues']:
 raw=parselmouth.Sound(str(R/q['source']));sound=raw.extract_part(q['trim'][0],q['trim'][1],preserve_times=False);f,before=pitch(sound)
 manip=call(sound,'To Manipulation',.005,90,500);old=call(manip,'Extract pitch tier');tier=call('Create PitchTier','steady',sound.xmin,sound.xmax);points=[]
 for i in range(1,call(old,'Get number of points')+1):
  t=call(old,'Get time from index',i);hz=call(old,'Get value at index',i);d=12*np.log2(hz/before['median']);out=P['pitch_center_hz']*2**(P['pitch_soft_bound_semitones']*np.tanh(P['pitch_log_contour_scale']*d/P['pitch_soft_bound_semitones'])/12)
  call(tier,'Add point',t,float(out));points.append([t,hz,float(out)])
 call([tier,manip],'Replace pitch tier');adjusted=call(manip,'Get resynthesis (overlap-add)');assert adjusted.n_samples==sound.n_samples
 shifted=R/'assets'/f'steady-cue{q["cue"]:02d}-pitch.wav';adjusted.save(str(shifted),'WAV')
 target=round(q['steady_duration']*SR);tempo=sound.duration/(q['steady_duration']-.012)
 for attempt in range(4):
  b=run([FF,'-v','error','-nostdin','-i',str(shifted),'-af',f'atempo={tempo:.10f},aresample={SR},pan=stereo|c0=c0|c1=c0','-f','f32le','-']).stdout
  y=np.frombuffer(b,'<f4').reshape(-1,2).astype(float)
  if target-round(.035*SR)<=len(y)<=target:break
  tempo*=len(y)/(target-round(.012*SR))
 else:raise RuntimeError(f'Cannot fit cue {q["cue"]}')
 actual_synthesized=len(y);pad=target-len(y);y=np.pad(y,((0,pad),(0,0)))
 # Short endpoint ramps only; no word-by-word splicing.
 ramp=192;y[:ramp]*=np.linspace(0,1,ramp)[:,None];end=actual_synthesized;y[max(0,end-ramp):end]*=np.linspace(1,0,min(ramp,end))[:,None]
 peak=np.max(np.abs(y));pre_gain=min(1.,.9/max(peak,1e-9));y*=pre_gain
 out=R/'assets'/f'steady-cue{q["cue"]:02d}-final.wav';write(out,np.rint(y*32768))
 log=run([FF,'-v','info','-nostdin','-i',str(out),'-af','loudnorm=I=-17:TP=-3.5:LRA=7:print_format=json','-f','null','-']).stderr.decode();m=json.loads(re.findall(r'\{[^{}]+\}',log,re.S)[-1]);gain=min(-17-float(m['input_i']),-3.5-float(m['input_tp']))
 y=np.rint(y*32768*10**(gain/20)).astype(np.int32);write(out,y);start=round(q['steady_start']*SR);end=start+len(y);assert start>=last_end and end<=len(voice);voice[start:end]=y;last_end=end
 snd=parselmouth.Sound(y[:,0].astype(float)/32768,sampling_frequency=SR);f,after=pitch(snd);all_after.extend(f)
 rec={**q,'final_file':str(out.relative_to(R)),'final_sha256':sha(out),'start':start/SR,'end':end/SR,'duration':len(y)/SR,'rate_mora_per_second':q['mora_count']/(len(y)/SR),'tempo_from_raw':tempo,'padding_seconds':pad/SR,'gain_db':gain+20*np.log10(pre_gain),'pitch_before':before,'pitch_after':after,'pitch_tier_target_min_max':[min(p[2]for p in points),max(p[2]for p in points)],'word_splices':False};records.append(rec)
 save(R/'checks'/f'steady-cue{q["cue"]:02d}-pitch-tier.json',{'columns':['time','original_hz','target_hz'],'points':points})
 print('cue',q['cue'],'rate',round(rec['rate_mora_per_second'],3),'F0 median',round(before['median'],1),'->',round(after['median'],1),'p10-p90',round(after['p10_p90_semitones'],2),'st',flush=True)
old_voice=read(R/'assets/narration-only-before-steady.wav');old_mix=read(R/'assets/with-bgm-before-steady.wav');bgm=old_mix-old_voice;mix=voice+bgm
write(R/'assets/narration-only.wav',voice);write(R/'assets/with-bgm.wav',mix);write(R/'composition/assets/final-mix.wav',mix)
assert np.array_equal(read(R/'assets/with-bgm.wav')-read(R/'assets/narration-only.wav'),bgm)
summary={'result':'pass','voice_source':'Harema recorded in the prior edition; no new generation','duration_seconds':205,'mora_rate_min_max':[min(q['rate_mora_per_second']for q in records),max(q['rate_mora_per_second']for q in records)],'global_pitch_p05_p10_p50_p90_p95':np.quantile(all_after,[.05,.1,.5,.9,.95]).tolist(),'cue_median_pitch_min_max':[min(q['pitch_after']['median']for q in records),max(q['pitch_after']['median']for q in records)],'target_pitch_hz':P['pitch_target_hz'],'bounded_target_pitch_tiers':True,'bgm_contribution_identical_all_pcm_samples':True,'video_and_subtitle_files':'unchanged; verified during finalization','maximum_subtitle_lead_seconds':P['maximum_subtitle_lead_seconds'],'maximum_subtitle_overrun_seconds':P['maximum_subtitle_overrun_seconds'],'max_abs_narration_sample':int(np.abs(voice).max()),'max_abs_mix_sample':int(np.abs(mix).max()),'human_listening_acceptance':'not asserted','external_audio_uploaded':False,'pitch_method':'Praat TD-PSOLA, sentence median centering and smooth log-frequency range compression','tempo_method':'whole-sentence pitch-preserving atempo, matched mora-count/duration; intra-word rhythm is not forced constant'}
save(R/'source/steady-audio-alignment.json',records);save(R/'checks/steady-audio-validation.json',summary);print('SUMMARY',summary,flush=True)
