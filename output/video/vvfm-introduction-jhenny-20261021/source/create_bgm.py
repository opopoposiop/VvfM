#!/usr/bin/env python3
"""Original light instrumental bed, deterministically synthesized for this edit."""
import numpy as np,wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sr=48000;duration=198;out=np.zeros((duration*sr,2),np.float32);rng=np.random.default_rng(20261021)
def add(note,t,length,gain=.07,pan=0,kind='keys'):
 i=int(t*sr);n=min(int(length*sr),len(out)-i)
 if n<=0:return
 x=np.arange(n)/sr;f=440*2**((note-69)/12)
 if kind=='keys':
  env=(1-np.exp(-x/0.006))*np.exp(-x/0.75)*np.minimum(1,(length-x)/.12)
  y=(np.sin(2*np.pi*f*x)+.20*np.sin(2*np.pi*2*f*x)+.08*np.sin(2*np.pi*3*f*x))*env*gain
 elif kind=='bass':
  env=(1-np.exp(-x/.018))*np.exp(-x/1.0)*np.minimum(1,(length-x)/.12)
  y=(np.sin(2*np.pi*f*x)+.1*np.sin(2*np.pi*2*f*x))*env*gain
 else:return
 out[i:i+n,0]+=y*np.sqrt((1-pan)/2);out[i:i+n,1]+=y*np.sqrt((1+pan)/2)
beat=60/106;bar=beat*4
chords=[(48,[60,64,67,71]),(45,[57,60,64,67]),(53,[57,60,65,69]),(55,[59,62,67,69])]
melody=[76,79,81,79,76,74,72,74,76,79,74,72,71,74,76,72]
for b in range(int(190/bar)):
 t=b*bar;root,notes=chords[b%4]
 for j in range(4):
  add(root,t+j*beat,beat*1.5,.045,0,'bass')
  add(notes[j],t+j*beat,1.8,.038,(-.35 if j%2 else .35))
  if j in (1,3):
   for note in notes[:3]:add(note,t+j*beat+.02,1.2,.018,0)
 # Sparse high notes leave room for narration.
 if b%4 in (1,3):
  for j in [0,2]:add(melody[(b*2+j)%len(melody)],t+j*beat+.14,1.2,.025,.28)
 for j in range(8):
  ix=int((t+j*beat/2)*sr);n=int(.045*sr);noise=rng.normal(0,1,n);noise=np.concatenate([[0],np.diff(noise)])
  env=np.exp(-np.arange(n)/(sr*.009));v=noise*env*.006
  out[ix:ix+n,0]+=v;out[ix:ix+n,1]+=v*.82
for t in [190,192.3,194.6]:
 for note in [48,60,64,67,72]:add(note,t,3,.028,0,'bass'if note==48 else'keys')
# Subtle stereo delays; fade to a quiet resolved C major ending.
for delay,gain in[(.17,.16),(.29,.08)]:
 d=int(delay*sr);out[d:]+=out[:-d,::-1].copy()*gain
fade=np.ones(len(out),np.float32);fade[:sr*2]=np.linspace(0,1,sr*2);fade[-sr*3:]=np.linspace(1,0,sr*3)
out*=fade[:,None];out=np.clip(out,-1,1)
p=ROOT/'assets/bgm-original.wav'
with wave.open(str(p),'wb')as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes((out*32767).astype('<i2').tobytes())
print(f'Original instrumental: {duration}s, 106 BPM, stereo 48kHz')
