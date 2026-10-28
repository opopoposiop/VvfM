#!/usr/bin/env python3
"""Create matched narration-only and music versions without another TTS request."""
from pathlib import Path
import subprocess,json,re,wave
import numpy as np
ROOT=Path(__file__).resolve().parents[1];SR=48000;N=205*SR
FF='/opt/homebrew/bin/ffmpeg'
def normalise(src,dst,lufs,peak):
 cmd=[FF,'-hide_banner','-nostdin','-i',str(src),'-af',f'loudnorm=I={lufs}:TP={peak}:LRA=7:print_format=json','-f','null','-']
 p=subprocess.run(cmd,capture_output=True,text=True,check=True)
 values=json.loads(re.findall(r'\{[^{}]+\}',p.stderr,re.S)[-1])
 (ROOT/'checks'/f'{dst.stem}-normalization.json').write_text(json.dumps(values,indent=2)+'\n')
 f=f'loudnorm=I={lufs}:TP={peak}:LRA=7:measured_I={values["input_i"]}:measured_TP={values["input_tp"]}:measured_LRA={values["input_lra"]}:measured_thresh={values["input_thresh"]}:offset={values["target_offset"]}:linear=true,aresample=48000'
 subprocess.run([FF,'-hide_banner','-nostdin','-loglevel','error','-y','-i',str(src),'-af',f,'-ac','2','-ar',str(SR),'-t','205','-c:a','pcm_s16le',str(dst)],check=True)
def read(p):
 with wave.open(str(p),'rb')as w:
  assert w.getsampwidth()==2 and w.getframerate()==SR
  x=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,w.getnchannels()).astype(np.float32)/32768
 return x[:N]
def write(p,x):
 with wave.open(str(p),'wb')as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((np.clip(x,-1,1)*32767).astype('<i2').tobytes())
normalise(ROOT/'assets/narration-aligned-raw.wav',ROOT/'assets/narration-only.wav',-16.0,-2.0)
normalise(ROOT/'assets/bgm-original.wav',ROOT/'assets/bgm-normalized.wav',-25.5,-5.0)
voice=read(ROOT/'assets/narration-only.wav');bgm=read(ROOT/'assets/bgm-normalized.wav')
if len(voice)!=N or len(bgm)!=N:raise SystemExit('Audio duration is not exactly 205 seconds')
block=2400;rms=np.sqrt(np.mean(voice.reshape(-1,block,2)**2,axis=(1,2)))
active=rms>.01
# Pre-duck before a phrase; retain it through short pauses.
hold=np.convolve(active.astype(float),np.ones(11),mode='same')>0
state=1.;gains=[]
for on in hold:
 target=.38 if on else 1.;state+= (target-state)*(.5 if target<state else .09);gains.append(state)
env=np.interp(np.arange(N),np.arange(len(gains))*block,gains).astype(np.float32)
mix=voice+bgm*env[:,None]
# Preserve the narration gain between the two editions; a shared safety ceiling.
peak=max(float(np.max(abs(mix))),float(np.max(abs(voice))))
gain=min(1.,.86/max(peak,1e-9));mix*=gain;voice*=gain
write(ROOT/'assets/narration-only.wav',voice);write(ROOT/'assets/with-bgm.wav',mix)
write(ROOT/'composition/assets/final-mix.wav',mix)
(ROOT/'checks/audio-mix.json').write_text(json.dumps({'duration':205,'sample_rate':SR,'channels':2,'narration_target_lufs':-16,'music_target_lufs':-25.5,'music_gain_during_speech':.38,'shared_gain':gain,'bgm_version_peak_dbfs':float(20*np.log10(np.max(abs(mix)))),'narration_version_peak_dbfs':float(20*np.log10(np.max(abs(voice))))},indent=2)+'\n')
print('Created narration-only.wav and with-bgm.wav, both exactly 205 seconds')
