#!/usr/bin/env python3
"""Flatten the pitch contour of newly synthesized whole sentences, then time/level them."""
from pathlib import Path
import hashlib,json,re,subprocess,wave
import numpy as np
import parselmouth
from parselmouth.praat import call
ROOT=Path(__file__).resolve().parents[1]
FF='/opt/homebrew/bin/ffmpeg';SR=48000
SETTINGS=[{'scene':5,'raw':'assets/flat-scene05-raw.wav','target_median_hz':190,'contour_scale':.35,'trim':[0,3.52],'tempo':1,'start':54.2,'patch':[54.18,57.925],'old_sentence':[54.65,57.82]}, {'scene':8,'raw':'assets/flat-scene08-raw.wav','target_median_hz':200,'contour_scale':.35,'trim':[.14,4.08],'tempo':1.16,'start':106.06,'patch':[105.90,109.55],'old_sentence':[106.16888888888892,109.50555555555556]}]
def run(a):return subprocess.run(a,text=True,capture_output=True,check=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def measure(p,extra=None):
 q=run([FF,'-hide_banner','-nostdin',*(extra or []),'-i',str(p),'-af','loudnorm=I=-16:TP=-3:LRA=7:print_format=json','-f','null','-'])
 return json.loads(re.findall(r'\{[^{}]+\}',q.stderr,re.S)[-1])
def stats(sound):
 pitch=sound.to_pitch_ac(time_step=.005,pitch_floor=100,pitch_ceiling=450)
 f=pitch.selected_array['frequency'];f=f[f>0]
 qs=np.quantile(f,[.1,.5,.9]);return {'p10_hz':float(qs[0]),'median_hz':float(qs[1]),'p90_hz':float(qs[2]),'p10_to_p90_semitones':float(12*np.log2(qs[2]/qs[0]))}
reports=[]
for q in SETTINGS:
 raw=ROOT/q['raw'];sound=parselmouth.Sound(str(raw));before=stats(sound)
 manipulation=call(sound,'To Manipulation',.005,100,450)
 old=call(manipulation,'Extract pitch tier');tier=call('Create PitchTier','flat_sentence',sound.xmin,sound.xmax)
 points=[]
 for i in range(1,call(old,'Get number of points')+1):
  t=call(old,'Get time from index',i);hz=call(old,'Get value at index',i)
  hz2=q['target_median_hz']*(hz/before['median_hz'])**q['contour_scale']
  call(tier,'Add point',t,hz2);points.append({'time':t,'input_hz':hz,'output_hz':hz2})
 call([tier,manipulation],'Replace pitch tier');flat=call(manipulation,'Get resynthesis (overlap-add)')
 assert flat.n_samples==sound.n_samples
 flattened=ROOT/f'assets/flat-scene{q["scene"]:02d}-contour.wav';flat.save(str(flattened),'WAV')
 timed=ROOT/f'assets/flat-scene{q["scene"]:02d}-timed.wav'
 af=f'atrim=start={q["trim"][0]}:end={q["trim"][1]},asetpts=PTS-STARTPTS,atempo={q["tempo"]}'
 run([FF,'-v','error','-nostdin','-n','-i',str(flattened),'-af',af,'-ac','1','-ar',str(SR),'-c:a','pcm_s16le',str(timed)])
 target=float(measure(ROOT/'assets/narration-before-flat-reread.wav',['-ss',str(q['old_sentence'][0]),'-t',str(q['old_sentence'][1]-q['old_sentence'][0])])['input_i'])
 meter=measure(timed)
 af=(f'loudnorm=I={target}:TP=-3:LRA=7:measured_I={meter["input_i"]}:measured_TP={meter["input_tp"]}:measured_LRA={meter["input_lra"]}:measured_thresh={meter["input_thresh"]}:linear=true,aresample=48000')
 output=ROOT/f'assets/flat-scene{q["scene"]:02d}-final.wav'
 run([FF,'-v','error','-nostdin','-n','-i',str(timed),'-af',af,'-ac','1','-ar',str(SR),'-c:a','pcm_s16le',str(output)])
 final=parselmouth.Sound(str(output));after=stats(final)
 assert after['p10_to_p90_semitones']<before['p10_to_p90_semitones']*.6
 assert q['start']+final.duration<=q['patch'][1]
 (ROOT/'checks'/f'flat-scene{q["scene"]:02d}-pitch-tier.json').write_text(json.dumps(points,indent=2)+'\n')
 reports.append({**q,'file':str(output.relative_to(ROOT)),'sha256':sha(output),'duration_seconds':final.duration,'end':q['start']+final.duration,'continuous_sentence':True,'word_splices':False,'pitch_before':before,'pitch_after':after,'target_lufs':target,'loudness':measure(output),'pitch_method':'whole-sentence Praat TD-PSOLA log-frequency contour compression','duration_preserved_by_pitch_adjustment':True})
 print(q['scene'],json.dumps(reports[-1],ensure_ascii=False),flush=True)
(ROOT/'checks/flat-sentence-preparation.json').write_text(json.dumps({'result':'pass','parselmouth_version':parselmouth.__version__,'sentences':reports},ensure_ascii=False,indent=2)+'\n')
