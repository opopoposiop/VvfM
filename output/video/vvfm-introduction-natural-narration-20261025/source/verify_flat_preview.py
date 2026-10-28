#!/usr/bin/env python3
from pathlib import Path
import subprocess,json,hashlib
ROOT=Path(__file__).resolve().parents[1];FF='/opt/homebrew/bin/ffmpeg';FP='/opt/homebrew/bin/ffprobe'
source=ROOT/'VvfM_紹介動画_ナレーション調整版_3分25秒_BGMなし_1080p.mp4'
out=ROOT/'VvfM_腕とToonShader_ナレーション修正_23秒プレビュー.mp4'
def run(args):return subprocess.run(args,capture_output=True,text=True,check=True)
p=run([FF,'-hide_banner','-nostdin','-n','-ss','53','-t','9','-i',str(source),'-ss','99','-t','14','-i',str(source),'-filter_complex','[0:v]setpts=PTS-STARTPTS[v0];[0:a]asetpts=PTS-STARTPTS[a0];[1:v]setpts=PTS-STARTPTS[v1];[1:a]asetpts=PTS-STARTPTS[a1];[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]','-map','[v]','-map','[a]','-map_metadata','-1','-map_chapters','-1','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-r','24','-c:a','aac','-b:a','192k','-movflags','+faststart',str(out)])
(ROOT/'checks/flat-preview-render.log').write_text(p.stderr)
probe=json.loads(run([FP,'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(out)]).stdout)
(ROOT/'checks/flat-preview-ffprobe.json').write_text(json.dumps(probe,ensure_ascii=False,indent=2)+'\n')
v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'],int(v['nb_read_frames']))==(1920,1080,552)
assert abs(float(v['duration'])-23)<.001 and abs(float(a['duration'])-23)<.025
run([FF,'-hide_banner','-v','error','-xerror','-nostdin','-i',str(out),'-map','0:v:0','-map','0:a:0','-f','null','-'])
for name,start,dur in [('arm',54,8.3),('toon-rim',101.8,11.2)]:
 run([FF,'-v','error','-nostdin','-n','-ss',str(start),'-i',str(source),'-t',str(dur),'-vn','-ar','16000','-ac','1',str(ROOT/f'checks/flat-{name}-final-aac.wav')])
for t in [55.5,104,108]:
 run([FF,'-v','error','-nostdin','-ss',str(t),'-i',str(source),'-frames:v','1','-update','1',str(ROOT/f'checks/flat-final-at-{t}.png')])
report={'result':'pass','file':out.name,'source_file':source.name,'source_intervals_seconds':[[53,62],[99,113]],'preview_interval_map':[{'preview':[0,9],'source':[53,62]},{'preview':[9,23],'source':[99,113]}],'duration_seconds':float(probe['format']['duration']),'frames':552,'resolution':[1920,1080],'full_video_audio_decode':'pass','sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'audio_edition':'BGMなし','human_listening_acceptance':'not asserted; reviewable preview'}
(ROOT/'checks/flat-preview-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('PASS: 23-second two-region preview and final AAC excerpts saved.',flush=True)
