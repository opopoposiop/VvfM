from pathlib import Path
import json, subprocess, hashlib
ROOT=Path(__file__).resolve().parents[1]
FF='/opt/homebrew/bin/ffmpeg';FP='/opt/homebrew/bin/ffprobe'
source=ROOT/'VvfM_紹介動画_キャラクターイラスト版_3分25秒_BGMあり_1080p.mp4'
preview=ROOT/'VvfM_キャラクター配置_14秒プレビュー.mp4'
def run(args): return subprocess.run(args,capture_output=True,text=True,check=True)
p=run([FF,'-hide_banner','-nostdin','-n','-ss','12','-i',str(source),'-t','14','-map','0:v:0','-map','0:a:0','-map_metadata','-1','-map_chapters','-1','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(preview)])
(ROOT/'checks/character-preview-render.log').write_text(p.stderr)
probe=json.loads(run([FP,'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(preview)]).stdout)
(ROOT/'checks/character-preview-ffprobe.json').write_text(json.dumps(probe,ensure_ascii=False,indent=2)+'\n')
v=next(s for s in probe['streams'] if s['codec_type']=='video')
a=next(s for s in probe['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'],int(v['nb_read_frames']))==(1920,1080,336)
assert abs(float(v['duration'])-14)<.001 and abs(float(a['duration'])-14)<.025
run([FF,'-hide_banner','-v','error','-xerror','-nostdin','-i',str(preview),'-map','0:v:0','-map','0:a:0','-f','null','-'])
report={'result':'pass','file':preview.name,'source_file':source.name,'source_interval_seconds':[12,26],'duration_seconds':float(probe['format']['duration']),'frames':int(v['nb_read_frames']),'resolution':[v['width'],v['height']],'sha256':hashlib.sha256(preview.read_bytes()).hexdigest(),'full_video_audio_decode':'pass','scene':2,'illustrations':2,'audio_edition':'BGMあり','human_full_video_listening_claimed':False}
(ROOT/'checks/character-preview-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('PASS: 14-second character-placement preview verified.',flush=True)
