#!/usr/bin/env python3
"""Place two user-approved continuous sentences without altering their PCM."""
from pathlib import Path
import hashlib
import json
import wave
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SR = 48000
PATCHES = [
    {'scene': 11, 'file': 'assets/pmx21-scene11-approved.wav',
     'sha256': 'efef85936c396dbf46814ea0fa83f4a1858a0bbbad386f429615fdb3e1f7ea78',
     'start': 152.5925, 'patch': [152.55, 156.60],
     'display': 'PMX2.1のモデルにも対応しています。',
     'spoken': 'ぴーえむえっくす　にーてん　いちのモデルにも対応しています。',
     'main_speech_local_seconds': [0.3876041666666667, 3.6344791666666665]},
    {'scene': 12, 'file': 'assets/pmx21-scene12-approved.wav',
     'sha256': '03ae0b2c966174625dfc344c16831ba2d43d7d72256a33359f3d54da42e14ffb',
     'start': 160.36, 'patch': [160.35, 167.45],
     'display': 'PMX 2.1のQDEFは、ねじったときの形を保つための変形方式です。',
     'spoken': 'ぴーえむえっくす　にーてん　いちのキューデフは、ねじったときの形を保つための変形方式です。',
     'main_speech_local_seconds': [0.5493541666666667, 6.840583333333333]}
]

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''):
            h.update(b)
    return h.hexdigest()

def read_pcm(path, channels):
    with wave.open(str(path)) as w:
        assert (w.getframerate(), w.getsampwidth(), w.getnchannels()) == (SR, 2, channels)
        return np.frombuffer(w.readframes(w.getnframes()), dtype='<i2').reshape(-1, channels).copy()

def write_pcm(path, samples):
    assert samples.min() >= -32768 and samples.max() <= 32767
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(samples.astype('<i2').tobytes())

baseline = ROOT/'assets/narration-before-pmx21-pronunciation.wav'
baseline_mix = ROOT/'assets/with-bgm-before-pmx21-pronunciation.wav'
before_voice = read_pcm(baseline, 2).astype(np.int32)
before_mix = read_pcm(baseline_mix, 2).astype(np.int32)
assert before_voice.shape == before_mix.shape == (205*SR, 2)
voice, mix = before_voice.copy(), before_mix.copy()
outside = np.ones(len(voice), dtype=bool)
scenes_path = ROOT/'source/scenes.json'
scenes = json.loads(scenes_path.read_text())
caps = json.loads((ROOT/'source/captions.json').read_text())
alignment_path = ROOT/'source/audio-alignment.json'
alignment = json.loads(alignment_path.read_text())
patch_reports = []

for patch in PATCHES:
    path = ROOT/patch['file']
    assert sha(path) == patch['sha256'], f'Approved source changed: {path}'
    mono = read_pcm(path, 1)
    clip = np.repeat(mono, 2, axis=1)
    start = round(patch['start']*SR)
    end = start+len(clip)
    a, b = [round(t*SR) for t in patch['patch']]
    assert a <= start < end <= b
    voice[a:b] = 0
    voice[start:end] = clip
    mix[a:b] += voice[a:b]-before_voice[a:b]
    outside[a:b] = False
    assert np.array_equal(voice[start:end], clip)
    caption = next(c for c in caps if c['text'] == patch['display'])
    speech = [patch['start']+t for t in patch['main_speech_local_seconds']]
    assert caption['start'] <= speech[0] < speech[1] <= caption['end']
    scene = scenes[patch['scene']-1]
    scene['spoken'] = scene['spoken'].replace('ピーエムエックス にてんいち', 'ぴーえむえっくす　にーてん　いち')
    assert patch['spoken'] in scene['spoken']
    previous = alignment['scenes'][patch['scene']-1]
    segment = {'source_file': patch['file'], 'source_start': 0,
               'source_end': len(clip)/SR, 'start': start/SR, 'end': end/SR,
               'tempo': 1, 'pitch_shift_semitones': 0,
               'spoken': patch['spoken'], 'continuous_sentence': True,
               'approved_pcm_identical_per_channel': True}
    segments = [segment]
    if patch['scene'] == 11:
        segments.insert(0, {'source_file': str(baseline.relative_to(ROOT)),
                            'source_start': previous['start'], 'source_end': a/SR,
                            'start': previous['start'], 'end': a/SR, 'tempo': 1})
    alignment['scenes'][patch['scene']-1] = {
        'scene': patch['scene'], 'start': segments[0]['start'], 'end': end/SR,
        'script': scene['narration'], 'segments': segments}
    patch_reports.append({**patch, 'duration_seconds': len(clip)/SR,
                          'end': end/SR, 'main_speech_seconds': speech,
                          'caption_seconds': [caption['start'], caption['end']],
                          'tempo': 1, 'pitch_shift_semitones': 0,
                          'source_trim_seconds': [0, len(clip)/SR],
                          'continuous_sentence': True,
                          'approved_pcm_identical_per_channel': True})

assert np.array_equal(voice[outside], before_voice[outside])
assert np.array_equal(mix[outside], before_mix[outside])
assert np.array_equal(mix-voice, before_mix-before_voice)
write_pcm(ROOT/'assets/narration-only.wav', voice)
write_pcm(ROOT/'assets/with-bgm.wav', mix)
write_pcm(ROOT/'composition/assets/final-mix.wav', mix)
scenes_path.write_text(json.dumps(scenes, ensure_ascii=False, indent=2)+'\n')
alignment_path.write_text(json.dumps(alignment, ensure_ascii=False, indent=2)+'\n')
report = {
    'result': 'pass', 'duration_seconds': 205, 'pronunciation': 'ぴーえむえっくす　にーてん　いち',
    'user_adopted_listening_trial': True,
    'voice_method': 'Qwen3-TTS local reference-voice synthesis from saved HeyGen Jhenny narration',
    'voice_identity_equivalence_claimed': False, 'new_synthesis_in_this_edit': False,
    'patches': patch_reports,
    'main_speech_boundary_method': 'Independent -45 dBFS threshold audit; tiny early transient in scene 12 excluded from main speech',
    'narration_pcm_outside_patch_identical': True, 'with_bgm_pcm_outside_patch_identical': True,
    'bgm_contribution_preserved': True, 'previous_apurijou_fxdayo_yuka_fixes_preserved': True,
    'inputs': [{'file': str(p.relative_to(ROOT)), 'sha256': sha(p)} for p in (baseline, baseline_mix)],
    'unchanged_caption_sha256': sha(ROOT/'source/captions.json'),
    'unchanged_edit_decision_list_sha256': sha(ROOT/'source/edit-decision-list.json'),
    'pcm_preservation_is_before_aac_encoding': True
}
(ROOT/'checks/pmx21-local-voice-adoption-validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
print('PASS: both approved sentences placed without trimming, tempo, pitch, or PCM changes.')
print('PASS: audio outside both patches and the BGM contribution are sample-identical before AAC encoding.')
