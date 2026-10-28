#!/usr/bin/env python3
"""Prepare continuous rereads with their original pitch contour and local stereo loudness."""
from pathlib import Path
import hashlib,json,re,subprocess
import numpy as np,parselmouth
R=Path(__file__).resolve().parents[1];FF='/opt/homebrew/bin/ffmpeg'
SETTINGS=[{'id':'arm','scene':5,'raw':'assets/natural-arm-raw.wav','trim':[.04,3.30],'tempo':1.0,'start':54.56,'patch':[54.18,57.925],'target_stereo_lufs':-16.0,'reference_interval':[57.925,61.98]}, {'id':'toon','scene':8,'raw':'assets/natural-toon-v2-raw.wav','trim':[.34,4.24],'tempo':1.08,'start':102.18,'patch':[102.12,105.90],'target_stereo_lufs':-16.87,'reference_interval':[102.16,105.82]}, {'id':'rim','scene':8,'raw':'assets/natural-rim-raw.wav','trim':[.32,4.0],'tempo':1.10,'start':106.12,'patch':[105.90,109.55],'target_stereo_lufs':-16.8,'reference_interval':[109.55,112.91]}]
def run(a):return subprocess.run(a,text=True,capture_output=True,check=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def measure(p):
 q=run([FF,'-hide_banner','-nostdin','-i',str(p),'-af','loudnorm=I=-16:TP=-3:LRA=7:print_format=json','-f','null','-'])
 return json.loads(re.findall(r'\{[^{}]+\}',q.stderr,re.S)[-1])
def pitch(p):
 snd=parselmouth.Sound(str(p)); f=snd.to_pitch_ac(time_step=.005,pitch_floor=100,pitch_ceiling=450).selected_array['frequency'];f=f[f>0];qs=np.quantile(f,[.1,.5,.9]);return {'p10_hz':float(qs[0]),'median_hz':float(qs[1]),'p90_hz':float(qs[2]),'span_semitones':float(12*np.log2(qs[2]/qs[0]))}
reports=[]
for q in SETTINGS:
 raw=R/q['raw'];timed=R/f'assets/natural-{q["id"]}-timed.wav';out=R/f'assets/natural-{q["id"]}-final.wav'
 af=f'atrim=start={q["trim"][0]}:end={q["trim"][1]},asetpts=PTS-STARTPTS,atempo={q["tempo"]},pan=stereo|c0=c0|c1=c0,aresample=48000'
 run([FF,'-v','error','-nostdin','-n','-i',str(raw),'-af',af,'-c:a','pcm_s16le',str(timed)])
 m=measure(timed);gain=q['target_stereo_lufs']-float(m['input_i']);dur=parselmouth.Sound(str(timed)).duration
 af=f'volume={gain:.5f}dB,afade=t=in:d=0.004,afade=t=out:st={dur-.004:.8f}:d=0.004'
 run([FF,'-v','error','-nostdin','-n','-i',str(timed),'-af',af,'-c:a','pcm_s16le',str(out)])
 final=measure(out);assert abs(float(final['input_i'])-q['target_stereo_lufs'])<.15;assert float(final['input_tp'])<-1.0
 assert q['start']+dur<=q['patch'][1]
 reports.append({**q,'file':str(out.relative_to(R)),'sha256':sha(out),'duration_seconds':dur,'end':q['start']+dur,'continuous_sentence':True,'word_splices':False,'pitch_shift_semitones':0,'pitch_contour_compression':False,'stereo_channels':2,'gain_db':gain,'pitch_before':pitch(raw),'pitch_after':pitch(out),'loudness':final,'level_method':'constant gain measured after mono-to-identical-stereo conversion; no compressor or pitch resynthesis','voice_identity_verified':False})
 print(json.dumps(reports[-1],ensure_ascii=False),flush=True)
(R/'checks/natural-sentence-preparation.json').write_text(json.dumps({'result':'pass','sentences':reports},ensure_ascii=False,indent=2)+'\n')
