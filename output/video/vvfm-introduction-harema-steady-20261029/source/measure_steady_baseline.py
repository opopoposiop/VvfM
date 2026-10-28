from pathlib import Path
import json,re,numpy as np,parselmouth,pykakasi
R=Path(__file__).resolve().parents[1];BASE=R.with_name('vvfm-introduction-harema-20261029');k=pykakasi.kakasi()
plan=json.loads((R/'source/harema-audio-alignment.json').read_text());result=[];all_f=[]
for q in plan:
 reading=''.join(z['hira']for z in k.convert(q['spoken']));mora=sum(1 for x in reading if ('ぁ'<=x<='ゖ'or x=='ー')and x not in'ぁぃぅぇぉゃゅょゎ')
 # Counts are a pacing proxy, not a forced phoneme alignment.
 sound=parselmouth.Sound(str(BASE/q['prepared']));mono=sound.convert_to_mono();pitch=mono.to_pitch_ac(time_step=.01,pitch_floor=90,pitch_ceiling=500);f=pitch.selected_array['frequency'];f=f[f>0];all_f.extend(f)
 p10,med,p90=np.quantile(f,[.1,.5,.9]);record={**q,'reading_for_measurement':reading,'mora_count':mora,'mora_per_second':mora/q['duration'],'pitch':{'p10':p10,'median':med,'p90':p90,'p10_p90_semitones':12*np.log2(p90/p10)}};result.append(record)
 print(q['cue'],mora,round(record['mora_per_second'],2),*[round(x,1)for x in [p10,med,p90]],reading)
summary={'mora_rate_p10_p50_p90':np.quantile([q['mora_per_second']for q in result],[.1,.5,.9]).tolist(),'rate_min_max':[min(q['mora_per_second']for q in result),max(q['mora_per_second']for q in result)],'pitch_p05_p10_p50_p90_p95':np.quantile(all_f,[.05,.1,.5,.9,.95]).tolist(),'cue_median_pitch_min_max':[min(q['pitch']['median']for q in result),max(q['pitch']['median']for q in result)]}
(R/'checks/steady-baseline-measurements.json').write_text(json.dumps({'summary':summary,'cues':result},ensure_ascii=False,indent=2)+'\n');print('SUMMARY',summary)
