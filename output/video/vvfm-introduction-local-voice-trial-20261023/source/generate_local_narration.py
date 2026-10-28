#!/usr/bin/env python3
"""Synthesize two complete sentences locally using a saved Jhenny reference.
This is an alternative-engine trial, not proof of an identical HeyGen voice.
"""
from pathlib import Path
import hashlib
import importlib.metadata
import json
import os
import time

os.environ.setdefault('HF_HUB_OFFLINE', '1')
os.environ.setdefault('HF_HOME', '/private/tmp/vvfm-local-tts-hf-20261023')
os.environ.setdefault('NUMBA_CACHE_DIR', '/private/tmp/vvfm-local-tts-numba-20261023')
import mlx.core as mx
from mlx_audio.tts.utils import load_model
from mlx_audio.tts.generate import generate_audio

ROOT = Path(__file__).resolve().parents[1]
MODEL = Path('/private/tmp/vvfm-qwen3-tts-base-4bit-20261023')
config = json.loads((ROOT/'source/local-tts-request.json').read_text())
model = load_model(str(MODEL))
report = {'model': config['model'], 'inference': 'local', 'audio_uploaded': False,
          'exact_voice_match_verified': False, 'generations': [],
          'package_versions': {name: importlib.metadata.version(name)
                               for name in ['mlx-audio', 'mlx', 'transformers']}}
for sentence in config['sentences']:
    scene = sentence['scene']
    prefix = f'scene{scene:02d}-local-reference-trial'
    assert not list((ROOT/'assets').glob(prefix+'*.wav'))
    mx.random.seed(42)
    started = time.time()
    generate_audio(text=sentence['spoken'], model=model,
                   ref_audio=str(ROOT/config['reference_audio']),
                   ref_text=config['reference_text'], lang_code='Japanese',
                   max_tokens=300, temperature=0.7, top_p=0.9,
                   output_path=str(ROOT/'assets'), file_prefix=prefix,
                   audio_format='wav', join_audio=True, play=False, verbose=True)
    outputs = list((ROOT/'assets').glob(prefix+'*.wav'))
    assert len(outputs)==1, outputs
    p = outputs[0]
    report['generations'].append({'scene': scene, 'text': sentence['spoken'],
       'file': str(p.relative_to(ROOT)), 'elapsed_seconds': time.time()-started,
       'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
    (ROOT/'checks/local-generation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('Saved', p, flush=True)
print('Local synthesis complete. Speech and similarity validation still required.', flush=True)
