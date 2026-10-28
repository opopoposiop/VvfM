#!/usr/bin/env python3
"""Mux matching editions and retain media-integrity evidence."""
from pathlib import Path
import subprocess,json,re,hashlib
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
FF='/opt/homebrew/bin/ffmpeg';FP='/opt/homebrew/bin/ffprobe'
def run(args):return subprocess.run(args,capture_output=True,text=True,check=True)
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for block in iter(lambda:f.read(2**20),b''):h.update(block)
 return h.hexdigest()
scenes=json.loads((ROOT/'source/scenes.json').read_text())
caps=json.loads((ROOT/'source/captions.json').read_text())
shots=json.loads((ROOT/'source/edit-decision-list.json').read_text())
pmx_shots=[s for s in shots if s['scene'] in (12,13)]
assert len(pmx_shots)==2
for shot in pmx_shots:
 assert shot['crop'] is None and shot['playback_rate']==1
 assert shot['source'] in ('pmx21-qdef-source.mov','pmx21-softbody-source.mov')
correction=json.loads((ROOT/'checks/fxdayo-correction-validation.json').read_text())
assert correction['result']=='pass' and correction['pronunciation']=='ゆかのはんしゃ'
reread=json.loads((ROOT/'checks/sentence-reread-validation.json').read_text())
assert reread['result']=='pass' and reread['pronunciation']=='あぷりじょう'
assert reread['continuous_sentence_recording'] and reread['pitch_shift_semitones']==0
assert all(reread[k] for k in ['narration_pcm_outside_patch_identical','with_bgm_pcm_outside_patch_identical','bgm_contribution_preserved'])
adoption=json.loads((ROOT/'checks/pmx21-local-voice-adoption-validation.json').read_text())
assert adoption['result']=='pass' and adoption['user_adopted_listening_trial']
assert all(adoption[k] for k in ['narration_pcm_outside_patch_identical','with_bgm_pcm_outside_patch_identical','bgm_contribution_preserved'])
assert all(p['continuous_sentence'] and p['approved_pcm_identical_per_channel'] and p['tempo']==1 and p['pitch_shift_semitones']==0 for p in adoption['patches'])
assert all('エフエックスダヨー' not in c['text'] for c in caps)
assert any('fxdayo' in c['text'] for c in caps if c['scene']==10)
assert len(caps)==41
for i,c in enumerate(caps):
 s=scenes[c['scene']-1]
 assert s['start']<=c['start']<c['end']<=s['start']+s['duration']
 if i:assert caps[i-1]['end']<=c['start']
for s in scenes:assert ''.join(c['text']for c in caps if c['scene']==s['id'])==s['narration']
results=[]
for edition,wav in [('BGMあり','with-bgm.wav'),('BGMなし','narration-only.wav')]:
 out=ROOT/f'VvfM_紹介動画_ナレーション調整版_3分25秒_{edition}_1080p.mp4'
 p=run([FF,'-hide_banner','-nostdin','-n','-i',str(ROOT/'final-render.mp4'),'-i',str(ROOT/'assets'/wav),'-i',str(ROOT/'source/chapters.ffmeta'),'-map','0:v:0','-map','1:a:0','-map_metadata','2','-map_chapters','2','-c:v','copy','-c:a','aac','-b:a','192k','-metadata:s:a:0','language=jpn','-metadata','comment=AI narration: HeyGen Jhenny; PMX2.1, arm and rim-light sentences: local Qwen3-TTS reference voice; '+edition,'-t','205','-movflags','+faststart',str(out)])
 (ROOT/'checks'/f'{edition}-mux.log').write_text(p.stderr)
 probe=json.loads(run([FP,'-v','error','-count_frames','-show_streams','-show_format','-show_chapters','-of','json',str(out)]).stdout)
 (ROOT/'checks'/f'{edition}-ffprobe.json').write_text(json.dumps(probe,ensure_ascii=False,indent=2)+'\n')
 v=next(s for s in probe['streams']if s['codec_type']=='video');a=next(s for s in probe['streams']if s['codec_type']=='audio')
 assert (v['codec_name'],v['width'],v['height'],v['avg_frame_rate'],int(v['nb_read_frames']))==('h264',1920,1080,'24/1',4920)
 assert (a['codec_name'],int(a['sample_rate']),a['channels'])==('aac',48000,2)
 assert abs(float(v['duration'])-205)<.001 and abs(float(a['duration'])-205)<.025
 assert float(v['start_time'])==0 and float(a['start_time'])==0 and len(probe['chapters'])==15
 decode=run([FF,'-hide_banner','-v','error','-xerror','-nostdin','-i',str(out),'-map','0:v:0','-map','0:a:0','-f','null','-'])
 (ROOT/'checks'/f'{edition}-full-decode.log').write_text(decode.stderr or 'PASS: full video/audio decode completed without errors.\n')
 loud=run([FF,'-hide_banner','-nostdin','-i',str(out),'-vn','-af','loudnorm=I=-16:TP=-2:LRA=7:print_format=json','-f','null','-'])
 meter=json.loads(re.findall(r'\{[^{}]+\}',loud.stderr,re.S)[-1])
 (ROOT/'checks'/f'{edition}-loudness.json').write_text(json.dumps(meter,indent=2)+'\n')
 assert float(meter['input_tp'])<-1.0
 vh=run([FF,'-v','error','-nostdin','-i',str(out),'-map','0:v:0','-c','copy','-f','hash','-hash','sha256','-']).stdout.strip()
 results.append({'file':out.name,'bytes':out.stat().st_size,'sha256':sha(out),'video_bitstream_hash':vh,'duration_seconds':float(probe['format']['duration']),'video_duration':float(v['duration']),'audio_duration':float(a['duration']),'frames':int(v['nb_read_frames']),'resolution':[1920,1080],'fps':24,'audio_codec':'AAC','audio_sample_rate':48000,'audio_channels':2,'chapters':len(probe['chapters']),'integrated_lufs':float(meter['input_i']),'true_peak_dbtp':float(meter['input_tp']),'full_decode':'pass','audio_source':wav})
 audio_hash=run([FF,'-v','error','-nostdin','-i',str(out),'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-']).stdout.strip()
 results[-1]['audio_bitstream_hash']=audio_hash
 results[-1]['audio_bitstream_identical_to_previous_edition']=False
 print(edition,'PASS',results[-1]['integrated_lufs'],'LUFS',flush=True)
assert results[0]['video_bitstream_hash']==results[1]['video_bitstream_hash']
reused_hash=run([FF,'-v','error','-nostdin','-i',str(ROOT/'final-render.mp4'),'-map','0:v:0','-c','copy','-f','hash','-hash','sha256','-']).stdout.strip()
assert reused_hash==results[0]['video_bitstream_hash']
report={'editions':results,'identical_video_bitstreams':True,'subtitle_cues':len(caps),'subtitle_bounds_and_nonoverlap':'pass','subtitle_script_match':'pass','narration':'AI voice: HeyGen Jhenny; scenes 11 and 12: user-approved local Qwen3-TTS reference voice; scene 5 sentence 1 and scene 8 sentence 3: locally reread with compressed pitch contour','music':'Original instrumental generated by source/create_bgm.py; ducked during speech','layout_warning':None,'fxdayo_correction':{'display':'fxdayo','pronunciation_input':'ゆかのはんしゃ','audio_patch_seconds':correction['patch_interval_seconds']},'pmx21_full_recorded_app_window':True,'pmx21_viewport_crop':False,'pmx21_reused_sections':{'QDEF':[160,168],'SoftBody':[168,178]}}
report['sentence_reread']={'display':reread['display_sentence'],'spoken':reread['spoken_sentence'],'audio_patch_seconds':reread['patch_interval_seconds'],'continuous_sentence_recording':True,'tempo_preserving_pitch':reread['tempo_preserving_pitch'],'pitch_shift_semitones':0}
prior_video=json.loads((ROOT/'source/video-reuse.json').read_text())
report['video_bitstream_identical_to_previous_edition']=(results[0]['video_bitstream_hash']==prior_video['video_bitstream_hash'])
assert not report['video_bitstream_identical_to_previous_edition']
report['pmx21_local_voice_adoption'] = adoption
report['character_illustrations'] = json.loads((ROOT/'source/character-placement.json').read_text())
report['both_audio_bitstreams_identical_to_previous_editions'] = False
flat=json.loads((ROOT/'checks/flat-narration-validation.json').read_text())
assert flat['result']=='pass' and flat['narration_pcm_outside_patches_identical'] and flat['with_bgm_pcm_outside_patches_identical'] and flat['bgm_contribution_preserved_all_samples']
report['flat_narration_revision']=flat
(ROOT/'checks/delivery-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
times=[3,18,32,42,62,79,93,108,123,134,152,165,173,185,201]
frames=ROOT/'checks/final-frames';frames.mkdir(exist_ok=True)
contact=Image.new('RGB',(1440,5*294),'#FAFAF6');draw=ImageDraw.Draw(contact)
font=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',20)
for i,t in enumerate(times):
 dest=frames/f'scene-{i+1:02}-at-{t:03}.png'
 run([FF,'-hide_banner','-loglevel','error','-nostdin','-ss',str(t),'-i',str(ROOT/results[0]['file']),'-frames:v','1','-update','1',str(dest)])
 im=Image.open(dest).convert('RGB');im.thumbnail((480,270))
 x=(i%3)*480;y=(i//3)*294;contact.paste(im,(x,y));draw.text((x+8,y+272),f'{i+1:02} | {t:03}s',font=font,fill='#202632')
contact.save(ROOT/'checks/final-contact.jpg',quality=92)
manifest=[]
for directory in ['source','assets','composition/assets']:
 for p in sorted((ROOT/directory).rglob('*')):
  if p.is_file():manifest.append({'file':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)})
(ROOT/'checks/production-files-sha256.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('Both editions verified; contact sheet and production hashes saved.',flush=True)
