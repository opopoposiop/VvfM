#!/usr/bin/env python3
"""Replace one spoken sentence and separate display text from pronunciation."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import wave
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FF = '/opt/homebrew/bin/ffmpeg'
SR = 48000
START, END = 136.20, 143.10
FIRST = '対応するfxdayoで、ステージの演出も。'
SECOND = 'ペンライトや床の反射など、一部の対応エフェクトを使って、シーンの楽しみを広げられます。'
SPOKEN = 'ペンライトやゆかのはんしゃなど、一部の対応エフェクトを使って、シーンの楽しみを広げられます。'

def run(args):
    return subprocess.run(args, capture_output=True, text=True, check=True)

def meter(path, extra=None):
    p = run([FF, '-hide_banner', '-nostdin', *(extra or []), '-i', str(path),
             '-af', 'loudnorm=I=-16:TP=-3:LRA=7:print_format=json', '-f', 'null', '-'])
    return json.loads(re.findall(r'\{[^{}]+\}', p.stderr, re.S)[-1])

def read_pcm(path):
    with wave.open(str(path)) as w:
        assert (w.getframerate(), w.getsampwidth(), w.getnchannels()) == (SR, 2, 2)
        return np.frombuffer(w.readframes(w.getnframes()), dtype='<i2').reshape(-1, 2).copy()

def write_pcm(path, samples):
    assert samples.max() <= 32767 and samples.min() >= -32768
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(samples.astype('<i2').tobytes())

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()

baseline = ROOT/'assets/narration-before-fxdayo-fix.wav'
baseline_mix = ROOT/'assets/with-bgm-before-fxdayo-fix.wav'
replacement = ROOT/'assets/jhenny-fxdayo-yuka-original.wav'
target = meter(baseline, ['-ss', str(START), '-t', str(END-START)])
measured = meter(replacement)
target_i = float(target['input_i'])
af = (f'loudnorm=I={target_i}:TP=-3:LRA=7:'
      f'measured_I={measured["input_i"]}:measured_TP={measured["input_tp"]}:'
      f'measured_LRA={measured["input_lra"]}:measured_thresh={measured["input_thresh"]}:'
      'linear=true,aresample=48000')
normalized = ROOT/'assets/jhenny-fxdayo-yuka-normalized.wav'
run([FF, '-v', 'error', '-nostdin', '-y', '-i', str(replacement), '-af', af,
     '-ac', '2', '-ar', str(SR), '-c:a', 'pcm_s16le', str(normalized)])
before_voice, before_mix = read_pcm(baseline), read_pcm(baseline_mix)
assert before_voice.shape == before_mix.shape == (205*SR, 2)
clip = read_pcm(normalized).astype(np.float64)
fade = round(.006*SR)
clip[:fade] *= np.linspace(0, 1, fade)[:, None]
clip[-fade:] *= np.linspace(1, 0, fade)[:, None]
clip = np.rint(clip).astype(np.int32)
a, b = round(START*SR), round(END*SR)
assert len(clip) <= b-a
voice = before_voice.astype(np.int32)
voice[a:b] = 0
voice[a:a+len(clip)] = clip
mix = before_mix.astype(np.int32)
mix[a:b] += voice[a:b] - before_voice[a:b].astype(np.int32)
assert np.array_equal(voice[:a], before_voice[:a]) and np.array_equal(voice[b:], before_voice[b:])
assert np.array_equal(mix[:a], before_mix[:a]) and np.array_equal(mix[b:], before_mix[b:])
write_pcm(ROOT/'assets/narration-only.wav', voice)
write_pcm(ROOT/'assets/with-bgm.wav', mix)
write_pcm(ROOT/'composition/assets/final-mix.wav', mix)
write_pcm(ROOT/'checks/fxdayo-narration-preview.wav', voice[132*SR:145*SR])

scenes = json.loads((ROOT/'source/scenes.json').read_text())
scenes[9]['narration'] = FIRST + SECOND
scenes[9]['spoken'] = '対応するエフエックスダヨーで、ステージの演出も。' + SPOKEN
(ROOT/'source/scenes.json').write_text(json.dumps(scenes, ensure_ascii=False, indent=2)+'\n')
caps = json.loads((ROOT/'source/captions.json').read_text())
scene_caps = [c for c in caps if c['scene'] == 10]
assert len(scene_caps) == 2
scene_caps[0]['text'] = FIRST
scene_caps[1]['text'] = SECOND
scene_caps[1]['start'] = 136.40
scene_caps[1]['end'] = 142.75
(ROOT/'source/captions.json').write_text(json.dumps(caps, ensure_ascii=False, indent=2)+'\n')
align = json.loads((ROOT/'source/audio-alignment.json').read_text())
align['scenes'][9] = {
    'scene': 10, 'start': 132.65, 'end': START+len(clip)/SR, 'script': FIRST+SECOND,
    'segments': [
        {'source_file': 'assets/narration-before-fxdayo-fix.wav', 'source_start': 132.65,
         'source_end': START, 'start': 132.65, 'end': START, 'tempo': 1},
        {'source_file': 'assets/jhenny-fxdayo-yuka-original.wav', 'source_start': 0,
         'source_end': len(clip)/SR, 'start': START, 'end': START+len(clip)/SR,
         'tempo': 1, 'spoken': SPOKEN, 'target_lufs': target_i}
    ]
}
(ROOT/'source/audio-alignment.json').write_text(json.dumps(align, ensure_ascii=False, indent=2)+'\n')

def stamp(t):
    ms = round(t*1000)
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'

def wrap(text):
    if len(text) <= 37:
        return text
    k = min(range(max(8, len(text)-42), min(len(text)-7, 43)),
            key=lambda k: (0 if text[k-1] in '、。' else 100)+abs(k-len(text)/2))
    return text[:k]+'\n'+text[k:]

srt = '\n'.join(f'{i}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{wrap(c["text"])}\n'
                for i, c in enumerate(caps, 1))
(ROOT/'VvfM_紹介動画_fxdayo修正_日本語字幕.srt').write_text(srt)
report = {
    'duration_seconds': 205, 'patch_interval_seconds': [START, END],
    'new_clip_duration_seconds': len(clip)/SR, 'playback_rate': 1,
    'display_spelling': 'fxdayo', 'pronunciation': 'ゆかのはんしゃ',
    'romaji': 'yuka no hansha', 'new_spoken_sentence': SPOKEN,
    'voice': 'HeyGen Jhenny', 'reference_sentence_lufs': target_i,
    'narration_pcm_outside_patch_identical': True,
    'with_bgm_pcm_outside_patch_identical': True,
    'bgm_contribution_preserved': bool(np.array_equal(mix-voice,
        before_mix.astype(np.int32)-before_voice.astype(np.int32))),
    'inputs': [{'file': str(p.relative_to(ROOT)), 'sha256': sha(p)}
               for p in (baseline, baseline_mix, replacement)],
    'new_audio_measurement': measured, 'result': 'pass'
}
(ROOT/'checks/fxdayo-correction-validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
print(f'Patched {START:.2f}–{END:.2f}s; new speech {len(clip)/SR:.3f}s; target {target_i} LUFS')
print('Unchanged PCM outside patch; background music preserved; fxdayo captions updated.')
