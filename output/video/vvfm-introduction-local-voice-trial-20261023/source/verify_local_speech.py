from pathlib import Path
import os,json
os.environ.setdefault('HF_HUB_OFFLINE','1')
os.environ.setdefault('HF_HOME','/private/tmp/vvfm-video-huggingface-20261021')
os.environ.setdefault('NUMBA_CACHE_DIR','/private/tmp/vvfm-video-numba-20261021')
import mlx_whisper
root=Path(__file__).resolve().parents[1]
for scene in (11,12):
 p=root/f'assets/scene{scene}-local-reference-trial.wav'
 result=mlx_whisper.transcribe(str(p),path_or_hf_repo='/private/tmp/vvfm-whisper-small-mlx',language='ja',word_timestamps=True,temperature=0,condition_on_previous_text=False,verbose=False)
 (root/f'checks/scene{scene}-transcript.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(scene,result['text'],flush=True)
