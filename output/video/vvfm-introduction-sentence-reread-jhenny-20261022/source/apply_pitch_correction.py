#!/usr/bin/env python3
"""Lower the isolated high phrase with PSOLA; preserve duration, BGM and all other audio."""
from pathlib import Path
import hashlib
import json
import wave
import numpy as np
import parselmouth
from parselmouth.praat import call

ROOT = Path(__file__).resolve().parents[1]
SR = 48000
START, END = 18.90, 19.94
WORK_START, WORK_END = 18.65, 21.15
SEMITONES = -4.0
FULL_SHIFT_START, FULL_SHIFT_END, RELEASE_END = 18.94, 19.68, 19.90

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''):
            h.update(b)
    return h.hexdigest()

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

def smoothstep(x):
    x = np.clip(x, 0, 1)
    return x*x*(3-2*x)

def shift_semitones(t):
    attack = smoothstep((t-START)/(FULL_SHIFT_START-START))
    release = 1-smoothstep((t-FULL_SHIFT_END)/(RELEASE_END-FULL_SHIFT_END))
    return SEMITONES*attack*release

def pitch_stats(samples, start, end):
    mono = samples[round(start*SR):round(end*SR)].mean(axis=1)/32768
    pitch = parselmouth.Sound(mono, sampling_frequency=SR).to_pitch_ac(
        time_step=.01, pitch_floor=100, pitch_ceiling=450)
    f = pitch.selected_array['frequency']
    f = f[f>0]
    return {'interval_seconds': [start, end], 'voiced_frames': len(f),
            'median_hz': round(float(np.median(f)), 2),
            'p25_hz': round(float(np.quantile(f,.25)), 2),
            'p75_hz': round(float(np.quantile(f,.75)), 2)}

voice_input = ROOT/'assets/narration-before-pitch-fix.wav'
mix_input = ROOT/'assets/with-bgm-before-pitch-fix.wav'
before_voice, before_mix = read_pcm(voice_input), read_pcm(mix_input)
assert before_voice.shape == before_mix.shape == (205*SR, 2)
assert np.array_equal(before_voice[:,0], before_voice[:,1])
w0, w1 = round(WORK_START*SR), round(WORK_END*SR)
mono = before_voice[w0:w1,0].astype(np.float64)/32768
sound = parselmouth.Sound(mono, sampling_frequency=SR)
manipulation = call(sound, 'To Manipulation', .01, 100, 450)
original_tier = call(manipulation, 'Extract pitch tier')
tier = call('Create PitchTier', 'local_pitch_match', sound.xmin, sound.xmax)
points = []
for i in range(1, call(original_tier,'Get number of points')+1):
    t = call(original_tier, 'Get time from index', i)
    hz = call(original_tier, 'Get value at index', i)
    shift = float(shift_semitones(t+WORK_START))
    out_hz = hz*2**(shift/12)
    call(tier, 'Add point', t, out_hz)
    points.append({'time': round(t+WORK_START,6), 'before_hz': hz,
                   'after_hz': out_hz, 'shift_semitones': shift})
call([tier, manipulation], 'Replace pitch tier')
resynth = call(manipulation, 'Get resynthesis (overlap-add)')
assert resynth.n_samples == len(mono)
rendered = resynth.values[0]*32768
a, b = round(START*SR), round(END*SR)
candidate = rendered[a-w0:b-w0]
original = before_voice[a:b,0].astype(np.float64)
# Match energy before blending to avoid a loudness bump from the resynthesis.
level_gain = float(np.sqrt(np.mean(original**2)/np.mean(candidate**2)))
candidate *= level_gain
blend = np.ones(b-a)
fade = round(.020*SR)
blend[:fade] = smoothstep(np.linspace(0,1,fade))
blend[-fade:] = smoothstep(np.linspace(1,0,fade))
patched = np.rint(original*(1-blend)+candidate*blend).astype(np.int32)
voice = before_voice.astype(np.int32)
voice[a:b] = patched[:,None]
mix = before_mix.astype(np.int32)
mix[a:b] += voice[a:b] - before_voice[a:b].astype(np.int32)
assert np.array_equal(voice[:a],before_voice[:a]) and np.array_equal(voice[b:],before_voice[b:])
assert np.array_equal(mix[:a],before_mix[:a]) and np.array_equal(mix[b:],before_mix[b:])
assert np.array_equal(mix-voice,before_mix.astype(np.int32)-before_voice.astype(np.int32))
write_pcm(ROOT/'assets/narration-only.wav',voice)
write_pcm(ROOT/'assets/with-bgm.wav',mix)
write_pcm(ROOT/'composition/assets/final-mix.wav',mix)
write_pcm(ROOT/'checks/pitch-narration-preview.wav',voice[16*SR:23*SR])
write_pcm(ROOT/'checks/pitch-before-preview.wav',before_voice[16*SR:23*SR])

regions={'preceding':[17.55,18.65],'apurijou':[18.94,19.52],
         'following_clause':[19.94,20.90],'following_sentence':[21.38,22.90]}
stats = {name:{'before':pitch_stats(before_voice,*times), 'after':pitch_stats(voice,*times)}
         for name,times in regions.items()}
assert 205 < stats['apurijou']['after']['median_hz'] < 235
assert stats['apurijou']['after']['median_hz'] < stats['apurijou']['before']['median_hz']
for name in ['preceding','following_clause','following_sentence']:
    assert stats[name]['before'] == stats[name]['after']
ratio_rms = np.sqrt(np.mean(patched.astype(float)**2)/np.mean(original**2))
assert abs(20*np.log10(ratio_rms)) < .15
report={'result':'pass','method':'Praat TD-PSOLA (overlap-add), local pitch-tier scaling',
        'parselmouth_version':parselmouth.__version__, 'maximum_shift_semitones':SEMITONES,
        'audio_patch_seconds':[START,END], 'full_shift_seconds':[FULL_SHIFT_START,FULL_SHIFT_END],
        'release_end_seconds':RELEASE_END,'boundary_crossfade_seconds':.020,
        'resynthesis_gain':level_gain,'patch_rms_change_db':float(20*np.log10(ratio_rms)),
        'duration_seconds':205,'duration_unchanged':True,'sample_rate':SR,
        'narration_pcm_outside_patch_identical':True,'with_bgm_pcm_outside_patch_identical':True,
        'bgm_contribution_preserved':True,'pitch_measurements':stats,
        'inputs':[{'file':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in [voice_input,mix_input]],
        'caption_sha256':sha(ROOT/'source/captions.json'),
        'edit_decision_list_sha256':sha(ROOT/'source/edit-decision-list.json'),
        'source_reference':'https://parselmouth.readthedocs.io/en/stable/examples/pitch_manipulation.html'}
alignment_path=ROOT/'source/audio-alignment.json'
alignment=json.loads(alignment_path.read_text())
alignment['scenes'][1]['postprocessing']={'script':'source/apply_pitch_correction.py','method':report['method'],'interval_seconds':[START,END],'maximum_shift_semitones':SEMITONES,'pitch_release_end_seconds':RELEASE_END}
alignment_path.write_text(json.dumps(alignment,ensure_ascii=False,indent=2)+'\n')
(ROOT/'checks/pitch-correction-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(ROOT/'checks/pitch-tier-points.json').write_text(json.dumps(points,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(stats,ensure_ascii=False,indent=2))
print(f'PASS: {START}–{END}s patched, pitch maximum {SEMITONES} semitones; other PCM and BGM identical.')
