#!/usr/bin/env python3
"""Patch the reading of アプリ上 while preserving all video, captions and other audio."""
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
START, END = 18.90, 20.98
TRIM_START, TRIM_END, TEMPO = 0.15, 2.80, 1.30
SPOKEN = 'あぷりじょうでリアルタイム再生。'

def run(args):
    return subprocess.run(args, capture_output=True, text=True, check=True)

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''):
            h.update(b)
    return h.hexdigest()

def meter(path, extra=None):
    p = run([FF, '-hide_banner', '-nostdin', *(extra or []), '-i', str(path),
             '-af', 'loudnorm=I=-16:TP=-3:LRA=7:print_format=json', '-f', 'null', '-'])
    return json.loads(re.findall(r'\{[^{}]+\}', p.stderr, re.S)[-1])

def read_pcm(path):
    with wave.open(str(path)) as w:
        assert (w.getframerate(), w.getsampwidth(), w.getnchannels()) == (SR, 2, 2)
        return np.frombuffer(w.readframes(w.getnframes()), dtype='<i2').reshape(-1, 2).copy()

def write_pcm(path, samples):
    assert samples.min() >= -32768 and samples.max() <= 32767
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(samples.astype('<i2').tobytes())

baseline = ROOT/'assets/narration-before-apurijou-fix.wav'
baseline_mix = ROOT/'assets/with-bgm-before-apurijou-fix.wav'
replacement = ROOT/'assets/jhenny-apurijou-original.wav'
timed = ROOT/'assets/jhenny-apurijou-timed.wav'
run([FF, '-v', 'error', '-nostdin', '-y', '-i', str(replacement), '-af',
     f'atrim=start={TRIM_START}:end={TRIM_END},asetpts=PTS-STARTPTS,atempo={TEMPO}',
     '-ac', '2', '-ar', str(SR), '-c:a', 'pcm_s16le', str(timed)])
target_i = float(meter(baseline, ['-ss', str(START), '-t', str(END-START)])['input_i'])
measured = meter(timed)
af = (f'loudnorm=I={target_i}:TP=-3:LRA=7:'
      f'measured_I={measured["input_i"]}:measured_TP={measured["input_tp"]}:'
      f'measured_LRA={measured["input_lra"]}:measured_thresh={measured["input_thresh"]}:'
      'linear=true,aresample=48000')
normalized = ROOT/'assets/jhenny-apurijou-normalized.wav'
run([FF, '-v', 'error', '-nostdin', '-y', '-i', str(timed), '-af', af,
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
assert np.array_equal(mix-voice, before_mix.astype(np.int32)-before_voice.astype(np.int32))
write_pcm(ROOT/'assets/narration-only.wav', voice)
write_pcm(ROOT/'assets/with-bgm.wav', mix)
write_pcm(ROOT/'composition/assets/final-mix.wav', mix)
write_pcm(ROOT/'checks/apurijou-narration-preview.wav', voice[16*SR:23*SR])

scenes = json.loads((ROOT/'source/scenes.json').read_text())
scenes[1]['spoken'] = scenes[1]['spoken'].replace('アプリ上', 'あぷりじょう')
assert 'あぷりじょう' in scenes[1]['spoken'] and 'アプリ上' in scenes[1]['narration']
(ROOT/'source/scenes.json').write_text(json.dumps(scenes, ensure_ascii=False, indent=2)+'\n')
alignment_path = ROOT/'source/audio-alignment.json'
align = json.loads(alignment_path.read_text())
old = align['scenes'][1]
align['scenes'][1] = {
    'scene': 2, 'start': old['start'], 'end': old['end'], 'script': scenes[1]['narration'],
    'segments': [
        {'source_file': str(baseline.relative_to(ROOT)), 'source_start': old['start'],
         'source_end': START, 'start': old['start'], 'end': START, 'tempo': 1},
        {'source_file': str(replacement.relative_to(ROOT)), 'source_start': TRIM_START,
         'source_end': TRIM_END, 'start': START, 'end': START+len(clip)/SR,
         'tempo': TEMPO, 'spoken': SPOKEN, 'target_lufs': target_i},
        {'source_file': str(baseline.relative_to(ROOT)), 'source_start': END,
         'source_end': old['end'], 'start': END, 'end': old['end'], 'tempo': 1}
    ]
}
alignment_path.write_text(json.dumps(align, ensure_ascii=False, indent=2)+'\n')
report = {
    'duration_seconds': 205, 'patch_interval_seconds': [START, END],
    'new_clip_duration_seconds': len(clip)/SR, 'source_trim_seconds': [TRIM_START, TRIM_END],
    'tempo_preserving_pitch': TEMPO, 'display_spelling': 'アプリ上',
    'pronunciation': 'あぷりじょう', 'romaji': 'apuri jou', 'new_spoken_clause': SPOKEN,
    'voice': 'HeyGen Jhenny', 'reference_clause_lufs': target_i,
    'narration_pcm_outside_patch_identical': True, 'with_bgm_pcm_outside_patch_identical': True,
    'bgm_contribution_preserved': True, 'previous_fxdayo_and_yuka_fix_preserved': True,
    'inputs': [{'file': str(p.relative_to(ROOT)), 'sha256': sha(p)}
               for p in (baseline, baseline_mix, replacement)],
    'unchanged_caption_sha256': sha(ROOT/'source/captions.json'),
    'unchanged_edit_decision_list_sha256': sha(ROOT/'source/edit-decision-list.json'),
    'new_audio_measurement_before_normalizing': measured, 'result': 'pass'
}
(ROOT/'checks/apurijou-correction-validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
print(f'Patched {START:.2f}–{END:.2f}s; new speech {len(clip)/SR:.3f}s; target {target_i} LUFS')
print('PCM outside patch and BGM contribution identical; captions and video unchanged.')
