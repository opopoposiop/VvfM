from pathlib import Path
import json, subprocess, hashlib
ROOT=Path(__file__).resolve().parents[1]
FF='/opt/homebrew/bin/ffmpeg';FP='/opt/homebrew/bin/ffprobe'
source=ROOT/'VvfM_紹介動画_締めイラスト追加版_3分25秒_BGMあり_1080p.mp4'
preview=ROOT/'VvfM_締めイラスト配置_8秒プレビュー.mp4'
def run(args): return subprocess.run(args,capture_output=True,text=True,check=True)
p=run([FF,'-hide_banner','-nostdin','-n','-ss','197','-i',str(source),'-t','8','-map','0:v:0','-map','0:a:0','-map_metadata','-1','-map_chapters','-1','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(preview)])
(ROOT/'checks/ending-preview-render.log').write_text(p.stderr)
probe=json.loads(run([FP,'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(preview)]).stdout)
(ROOT/'checks/ending-preview-ffprobe.json').write_text(json.dumps(probe,ensure_ascii=False,indent=2)+'\n')
v=next(s for s in probe['streams'] if s['codec_type']=='video')
a=next(s for s in probe['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'],int(v['nb_read_frames']))==(1920,1080,192)
assert abs(float(v['duration'])-8)<.001 and abs(float(a['duration'])-8)<.025
run([FF,'-hide_banner','-v','error','-xerror','-nostdin','-i',str(preview),'-map','0:v:0','-map','0:a:0','-f','null','-'])
report={'result':'pass','file':preview.name,'source_file':source.name,'source_interval_seconds':[197,205],'duration_seconds':float(probe['format']['duration']),'frames':int(v['nb_read_frames']),'resolution':[v['width'],v['height']],'sha256':hashlib.sha256(preview.read_bytes()).hexdigest(),'full_video_audio_decode':'pass','scene':15,'illustrations':2,'audio_edition':'BGMあり','human_full_video_listening_claimed':False}
(ROOT/'checks/ending-preview-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('PASS: 8-second ending-character preview verified.',flush=True)
