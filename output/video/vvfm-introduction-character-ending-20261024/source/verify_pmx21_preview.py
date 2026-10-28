from pathlib import Path
import json, subprocess, hashlib, os
ROOT=Path(__file__).resolve().parents[1]
FF='/opt/homebrew/bin/ffmpeg';FP='/opt/homebrew/bin/ffprobe'
source=ROOT/'VvfM_紹介動画_PMX21発音修正版_3分25秒_BGMなし_1080p.mp4'
preview=ROOT/'VvfM_PMX21発音修正_23秒プレビュー.mp4'
def run(args): return subprocess.run(args,capture_output=True,text=True,check=True)
p=run([FF,'-hide_banner','-nostdin','-n','-ss','145','-i',str(source),'-t','23','-map','0:v:0','-map','0:a:0','-map_metadata','-1','-map_chapters','-1','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(preview)])
(ROOT/'checks/pmx21-preview-render.log').write_text(p.stderr)
probe=json.loads(run([FP,'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(preview)]).stdout)
(ROOT/'checks/pmx21-preview-ffprobe.json').write_text(json.dumps(probe,ensure_ascii=False,indent=2)+'\n')
v=next(s for s in probe['streams'] if s['codec_type']=='video')
a=next(s for s in probe['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'],int(v['nb_read_frames']))==(1920,1080,552)
assert abs(float(v['duration'])-23)<.001 and abs(float(a['duration'])-23)<.025
run([FF,'-hide_banner','-v','error','-xerror','-nostdin','-i',str(preview),'-map','0:v:0','-map','0:a:0','-f','null','-'])
for scene,start,duration in [(11,152.55,4.05),(12,160.35,7.1)]:
 dest=ROOT/f'checks/pmx21-scene{scene}-final-aac.wav'
 run([FF,'-v','error','-nostdin','-n','-ss',str(start),'-i',str(source),'-t',str(duration),'-vn','-ar','16000','-ac','1',str(dest)])
report={'result':'pass','file':preview.name,'source_file':source.name,'source_interval_seconds':[145,168],'duration_seconds':float(probe['format']['duration']),'frames':int(v['nb_read_frames']),'resolution':[v['width'],v['height']],'sha256':hashlib.sha256(preview.read_bytes()).hexdigest(),'full_video_audio_decode':'pass','narration':'user-approved local reference-voice sentences; source playback speed 1','asr_checks':'separate pmx21-final-transcripts.json','human_full_video_listening_claimed':False}
(ROOT/'checks/pmx21-preview-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('PASS: 23-second final-output preview verified.',flush=True)
