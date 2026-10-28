#!/usr/bin/env python3
"""Offline local ASR of the generated audio; no audio is uploaded."""
from pathlib import Path
import os,json,hashlib,argparse
os.environ['HF_HUB_OFFLINE']='1'
os.environ['HF_HOME']='/private/tmp/vvfm-harema-hf'
os.environ['NUMBA_CACHE_DIR']='/private/tmp/vvfm-harema-numba'
import mlx_whisper
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--prepared',action='store_true');p.add_argument('--final',action='store_true');a=p.parse_args()
inputs=sorted((R/'assets').glob('harema-cue*-prepared.wav'if a.prepared else'harema-scene*-raw.wav'))
if a.final:inputs=[R/'checks/final-narration-aac.wav']
for f in inputs:
 out=R/'checks'/f'{f.stem}-asr.json'
 if out.exists():continue
 result=mlx_whisper.transcribe(str(f),path_or_hf_repo='/private/tmp/vvfm-harema-whisper-medium-mlx',language='ja',word_timestamps=True,temperature=0,condition_on_previous_text=False,verbose=False)
 q={'engine':'local mlx-whisper','model':'openai/whisper-medium converted locally to MLX','audio_uploaded':False,'source':str(f.relative_to(R)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'transcript':result}
 out.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n');print(f.name,result['text'],flush=True)
