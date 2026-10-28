from pathlib import Path
import json,numpy as np
from scipy.optimize import minimize
R=Path(__file__).resolve().parents[1];data=json.loads((R/'checks/steady-baseline-measurements.json').read_text());scenes=json.loads((R/'source/scenes.json').read_text());rate=7.5;records=[]
for scene in scenes:
 cues=[q for q in data['cues']if q['scene']==scene['id']];dur=np.array([q['mora_count']/rate for q in cues]);starts=np.array([q['caption'][0]for q in cues]);ends=np.array([q['caption'][1]for q in cues]);gap=.08
 bounds=[(max(scene['start']+.30,q['caption'][0]-.75),min(scene['start']+scene['duration']-.25-d,q['caption'][0]+.5,q['caption'][1]+.4-d))for q,d in zip(cues,dur)]
 assert all(a<=b for a,b in bounds),bounds
 obj=lambda x:float(np.sum((x-starts)**2+.25*(x+dur-ends)**2))
 cons=[{'type':'ineq','fun':lambda x,i=i:x[i+1]-x[i]-dur[i]-gap}for i in range(len(cues)-1)]
 initial=np.array([np.clip(s,a,b)for s,(a,b)in zip(starts,bounds)])
 result=minimize(obj,initial,bounds=bounds,constraints=cons,method='SLSQP',options={'ftol':1e-12,'maxiter':300})
 assert result.success,(scene['id'],result.message)
 for q,d,t in zip(cues,dur,result.x):
  records.append({**q,'steady_start':float(t),'steady_duration':float(d),'steady_end':float(t+d),'steady_target_mora_per_second':rate,'old_start':q['actual_start'],'old_end':q['actual_end'],'subtitle_lead_seconds':max(0,q['caption'][0]-float(t)),'subtitle_overrun_seconds':max(0,float(t+d)-q['caption'][1])})
report={'target_mora_per_second':rate,'mora_count_method':'pykakasi reading, small vowels/ya/yu/yo excluded; a phrase-average pacing proxy, not phoneme alignment','minimum_inter_sentence_gap':gap,'pitch_center_hz':215,'pitch_log_contour_scale':.45,'pitch_soft_bound_semitones':3,'pitch_target_hz':[215*2**(-3/12),215*2**(3/12)],'pitch_mapping':'For each sentence, center on 215 Hz and compress deviations with 3*tanh(0.45*semitones/3).','maximum_subtitle_lead_seconds':max(q['subtitle_lead_seconds']for q in records),'maximum_subtitle_overrun_seconds':max(q['subtitle_overrun_seconds']for q in records),'cues':records}
(R/'source/steady-plan.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
q=json.loads((R/'source/steady-request.json').read_text());q['settings']={k:v for k,v in report.items()if k!='cues'};(R/'source/steady-request.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
print({k:v for k,v in report.items()if k!='cues'})
for q in records:print(q['cue'],round(q['steady_start'],3),round(q['steady_end'],3),'shift',round(q['steady_start']-q['old_start'],3))
