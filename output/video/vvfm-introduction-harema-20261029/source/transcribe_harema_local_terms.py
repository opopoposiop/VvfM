#!/usr/bin/env python3
"""Second local recognition pass with product vocabulary only, not the narration script."""
from pathlib import Path
import json,os
os.environ['HF_HUB_OFFLINE']='1';os.environ['HF_HOME']='/private/tmp/vvfm-harema-hf';os.environ['NUMBA_CACHE_DIR']='/private/tmp/vvfm-harema-numba'
import mlx_whisper
R=Path(__file__).resolve().parents[1]
prompt='用語: VMD Viewer for Mac, PMX, VMD, MMD, WAV, 3Dギズモ, モーフ, ToonShader HQ, リムライト, ブルーム, ディフュージョン, 被写界深度, DoF, fxdayo, ペンライト, QDEF, SoftBody, Bullet, 3.25, 2.75。'
q=mlx_whisper.transcribe(str(R/'checks/final-narration-aac.wav'),path_or_hf_repo='/private/tmp/vvfm-harema-whisper-medium-mlx',language='ja',word_timestamps=True,temperature=0,condition_on_previous_text=False,initial_prompt=prompt,verbose=False)
(R/'checks/final-narration-aac-terms-asr.json').write_text(json.dumps({'engine':'local mlx-whisper','model':'openai/whisper-medium converted locally','audio_uploaded':False,'vocabulary_hint':prompt,'whole_script_provided':False,'transcript':q},ensure_ascii=False,indent=2)+'\n');print(q['text'])
