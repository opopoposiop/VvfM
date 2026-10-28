#!/usr/bin/env python3
"""Mux and verify both Harema editions, retaining the original video bitstream."""
from pathlib import Path
import subprocess,json,re,hashlib
R=Path(__file__).resolve().parents[1];BASE=R.with_name('vvfm-introduction-harema-20261029');FF='/opt/homebrew/bin/ffmpeg';FP='/opt/homebrew/bin/ffprobe'
def run(a):return subprocess.run(a,capture_output=True,text=True,check=True)
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def bitsha(p):return run([FF,'-v','error','-nostdin','-i',str(p),'-map','0:v:0','-c','copy','-f','hash','-hash','sha256','-']).stdout.strip()
immutable=['source/scenes.json','source/captions.json','source/captions.ass','source/chapters.ffmeta','source/edit-decision-list.json','source/character-placement.json','final-render.mp4']
proof=[]
for path in immutable:
 assert sha(R/path)==sha(BASE/path),path
 proof.append({'file':path,'sha256':sha(R/path),'identical_to_baseline':True})
assert sha(R/'VvfM_紹介動画_Haremaテンポ音程調整版_日本語字幕.srt')==sha(BASE/'VvfM_紹介動画_Harema版_日本語字幕.srt')
# The rendered video already contains the unchanged illustrations and subtitles.
vhash=bitsha(R/'final-render.mp4');editions=[]
for edition,wav in [('BGMあり','with-bgm.wav'),('BGMなし','narration-only.wav')]:
 out=R/f'VvfM_紹介動画_Haremaテンポ音程調整版_3分25秒_{edition}_1080p.mp4'
 if not out.exists():
  p=run([FF,'-v','error','-nostdin','-n','-i',str(R/'final-render.mp4'),'-i',str(R/'assets'/wav),'-i',str(R/'source/chapters.ffmeta'),'-map','0:v:0','-map','1:a:0','-map_metadata','2','-map_chapters','2','-c:v','copy','-c:a','aac','-b:a','192k','-metadata:s:a:0','language=jpn','-metadata','comment=AI-generated source: OpenAI GPT-Live Harema; local steady tempo and bounded pitch; '+edition,'-t','205','-movflags','+faststart',str(out)])
 probe=json.loads(run([FP,'-v','error','-count_frames','-show_streams','-show_format','-show_chapters','-of','json',str(out)]).stdout);save(R/'checks'/f'{edition}-ffprobe.json',probe)
 v=next(x for x in probe['streams']if x['codec_type']=='video');a=next(x for x in probe['streams']if x['codec_type']=='audio')
 assert(v['width'],v['height'],v['avg_frame_rate'],int(v['nb_read_frames']))==(1920,1080,'24/1',4920)
 assert(a['codec_name'],int(a['sample_rate']),a['channels'])==('aac',48000,2)
 assert abs(float(v['duration'])-205)<.001 and abs(float(a['duration'])-205)<.025 and len(probe['chapters'])==15
 assert float(v['start_time'])==0 and float(a['start_time'])==0
 decoded=run([FF,'-v','error','-xerror','-nostdin','-i',str(out),'-map','0:v:0','-map','0:a:0','-f','null','-']);(R/'checks'/f'{edition}-full-decode.log').write_text(decoded.stderr or 'PASS: full video/audio decode.\n')
 loud=run([FF,'-v','info','-nostdin','-i',str(out),'-vn','-af','loudnorm=I=-17:TP=-2:LRA=7:print_format=json','-f','null','-']);meter=json.loads(re.findall(r'\{[^{}]+\}',loud.stderr,re.S)[-1]);save(R/'checks'/f'{edition}-loudness.json',meter)
 assert float(meter['input_tp'])<-1.0
 vh=bitsha(out);assert vh==vhash
 editions.append({'file':out.name,'bytes':out.stat().st_size,'sha256':sha(out),'duration_seconds':float(probe['format']['duration']),'resolution':[1920,1080],'frames':4920,'fps':24,'chapters':15,'audio':'AAC 48 kHz stereo 192 kbps','video_bitstream_hash':vh,'video_bitstream_identical_to_baseline':True,'full_decode':'pass','integrated_lufs':float(meter['input_i']),'true_peak_dbtp':float(meter['input_tp'])})
 print(edition,'PASS',meter['input_i'],'LUFS',meter['input_tp'],'dBTP',flush=True)
run([FF,'-v','error','-nostdin','-n','-i',str(R/'assets/narration-only.wav'),'-c:a','libmp3lame','-b:a','192k',str(R/'VvfM_ナレーション_Haremaテンポ音程調整版_3分25秒.mp3')])
report={'result':'pass','editions':editions,'voice':'Harema','model':'gpt-live-1','all_narration_tempo_and_pitch_adjusted':True,'ai_generated':True,'same_video_both_editions':True,'immutable_baseline_assets':proof,'subtitle_count':41,'bgm_contribution_preserved_before_aac_encoding':True,'human_listening_acceptance':'not asserted','local_asr':'pending'}
report['steady_audio_validation']=json.loads((R/'checks/steady-audio-validation.json').read_text())
save(R/'checks/delivery-validation.json',report)
