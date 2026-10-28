#!/usr/bin/env python3
"""Place Harema sentence audio and preserve the exact baseline BGM contribution."""
from pathlib import Path
import subprocess,json,re,wave,hashlib
import numpy as np
R=Path(__file__).resolve().parents[1];FF='/opt/homebrew/bin/ffmpeg';SR=48000;N=205*SR
plan=json.loads((R/'source/harema-alignment-plan.json').read_text())
def run(a):return subprocess.run(a,capture_output=True,check=True)
def meter(p):
 s=run([FF,'-v','info','-nostdin','-i',str(p),'-af','loudnorm=I=-17:TP=-3:LRA=7:print_format=json','-f','null','-']).stderr.decode()
 return json.loads(re.findall(r'\{[^{}]+\}',s,re.S)[-1])
def read(p):
 with wave.open(str(p))as w:
  assert w.getframerate()==SR and w.getnchannels()==2 and w.getsampwidth()==2
  return np.frombuffer(w.readframes(w.getnframes()),'<i2').astype(np.int32).reshape(-1,2)
def write(p,y):
 with wave.open(str(p),'wb')as w:w.setparams((2,2,SR,0,'NONE','not compressed'));w.writeframes(y.astype('<i2').tobytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
voice=np.zeros((N,2),np.int32);report=[];previous_end=0
for q in plan:
 out=R/'assets'/f'harema-cue{q["cue"]:02d}-prepared.wav';a,b=q['trim'];tempo=q['tempo'];available=q['target_end']-q['start']
 for attempt in range(3):
  af=f'atrim=start={a}:end={b},asetpts=PTS-STARTPTS,atempo={tempo:.10f},aresample={SR},pan=stereo|c0=c0|c1=c0'
  pcm=run([FF,'-v','error','-nostdin','-i',str(R/q['source']),'-af',af,'-f','f32le','-']).stdout
  y=np.frombuffer(pcm,'<f4').reshape(-1,2).astype(np.float64);duration=len(y)/SR
  if duration<=available+.005:break
  tempo*=duration/available*1.004
 else:raise RuntimeError(f'Cannot fit cue {q["cue"]}')
 # Only constant gain and 4 ms boundary ramps, without pitch modification.
 ramp=min(192,len(y)//4);y[:ramp]*=np.linspace(0,1,ramp)[:,None];y[-ramp:]*=np.linspace(1,0,ramp)[:,None]
 write(out,np.rint(y*32768));m=meter(out)
 gain=min(-17-float(m['input_i']),-3.5-float(m['input_tp']));samples=np.rint(y*32768*10**(gain/20)).astype(np.int32)
 assert np.max(np.abs(samples))<32767
 write(out,samples);start=round(q['start']*SR);end=start+len(samples)
 assert start>=previous_end and end<=N,(q['cue'],'overlap');voice[start:end]=samples;previous_end=end
 record={**q,'prepared':str(out.relative_to(R)),'prepared_sha256':sha(out),'actual_start':start/SR,'actual_end':end/SR,'duration':len(samples)/SR,'tempo':tempo,'gain_db':gain,'gain_method':'constant gain, target -17 stereo LUFS, at most -3.5 dBTP','boundary_ramp_seconds':.004}
 report.append(record);print('Cue',q['cue'],'tempo',round(tempo,3),'gain',round(gain,2),flush=True)
oldvoice=read(R/'assets/narration-only-before-harema.wav');oldmix=read(R/'assets/with-bgm-before-harema.wav');assert oldvoice.shape==voice.shape==oldmix.shape
bgm=oldmix-oldvoice;mix=voice+bgm
assert np.max(np.abs(mix))<32767
write(R/'assets/narration-only.wav',voice);write(R/'assets/with-bgm.wav',mix);write(R/'assets/bgm-contribution-preserved.wav',bgm);write(R/'composition/assets/final-mix.wav',mix)
assert np.array_equal(read(R/'assets/with-bgm.wav')-read(R/'assets/narration-only.wav'),bgm)
json.dump(report,(R/'source/harema-audio-alignment.json').open('w'),ensure_ascii=False,indent=2)
validation={'result':'pass','duration_seconds':205,'cues':len(report),'scenes':15,'all_narration_replaced':True,'voice':'Harema','provider':'OpenAI GPT-Live','model':'gpt-live-1','ai_generated':True,'bgm_contribution_identical_all_pcm_samples':True,'pitch_shift_semitones':0,'max_abs_narration_sample':int(np.abs(voice).max()),'max_abs_mix_sample':int(np.abs(mix).max()),'tempo_range':[min(q['tempo']for q in report),max(q['tempo']for q in report)],'subtitle_cues_unchanged':True,'local_asr_validation':'pending','human_listening_acceptance':'not asserted','note':'BGM identity applies to WAV PCM before lossy AAC encoding.'}
json.dump(validation,(R/'checks/harema-audio-validation.json').open('w'),ensure_ascii=False,indent=2)
