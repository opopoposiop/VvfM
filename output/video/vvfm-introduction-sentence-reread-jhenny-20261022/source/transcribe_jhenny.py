#!/usr/bin/env python3
"""Local multilingual recognition solely for script and timing verification."""
import os,json,sys
from pathlib import Path
os.environ.setdefault('HF_HUB_DISABLE_XET','1')
os.environ.setdefault('HF_HOME','/private/tmp/vvfm-video-huggingface-20261021')
os.environ.setdefault('NUMBA_CACHE_DIR','/private/tmp/vvfm-video-numba-20261021')
import mlx_whisper
root=Path(__file__).resolve().parents[1]
input_path=root/(sys.argv[1] if len(sys.argv)>1 else 'assets/jhenny-original.wav')
output_path=root/(sys.argv[2] if len(sys.argv)>2 else 'checks/jhenny-transcript.json')
result=mlx_whisper.transcribe(str(input_path),path_or_hf_repo='/private/tmp/vvfm-whisper-small-mlx',language='ja',word_timestamps=True,temperature=0,condition_on_previous_text=False,initial_prompt='VMD Viewer for Mac。PMX、VMD、MMD、WAV。モーフ。ToonShader HQ。リムライト、ブルーム、ディフュージョン。DoF。fxdayo。Bullet 3.25、2.75互換。',verbose=False)
output_path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
for s in result['segments']:print(f'{s["start"]:7.2f} {s["end"]:7.2f} {s["text"]}',flush=True)
