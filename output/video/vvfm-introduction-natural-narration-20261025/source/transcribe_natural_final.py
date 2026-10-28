from pathlib import Path
import os,json
os.environ.setdefault('HF_HUB_OFFLINE','1')
os.environ.setdefault('HF_HOME','/private/tmp/vvfm-video-huggingface-20261021')
os.environ.setdefault('NUMBA_CACHE_DIR','/private/tmp/vvfm-video-numba-20261021')
import mlx_whisper
root=Path(__file__).resolve().parents[1]
paths=['checks/natural-arm-final-aac.wav','checks/natural-toon-rim-final-aac.wav']
results=[]
for path in paths:
 result=mlx_whisper.transcribe(str(root/path),path_or_hf_repo='/private/tmp/vvfm-whisper-small-mlx',language='ja',word_timestamps=True,temperature=0,condition_on_previous_text=False,verbose=False)
 results.append({'source_file':path,'transcript':result})
 print(path,result['text'],flush=True)
(root/'checks/natural-final-transcripts.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
