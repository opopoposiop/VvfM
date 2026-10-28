from pathlib import Path
import json,re,subprocess,numpy as np,parselmouth
R=Path(__file__).resolve().parents[1];FF='/opt/homebrew/bin/ffmpeg'
items=[('arm-raw','assets/natural-arm-raw.wav',None),('toon-raw','assets/natural-toon-raw.wav',None),('rim-raw','assets/natural-rim-raw.wav',None),('arm-original','assets/narration-before-flat-reread.wav',[54.65,57.82]),('arm-after','assets/narration-before-flat-reread.wav',[57.925,61.98]),('toon-original','assets/narration-before-flat-reread.wav',[102.16,105.82]),('rim-original','assets/narration-before-flat-reread.wav',[106.16,109.55]),('shader-before','assets/narration-before-flat-reread.wav',[99.65,102.13]),('shader-after','assets/narration-before-flat-reread.wav',[109.55,112.91])]
report=[]
for name,path,bounds in items:
 p=R/path
 args=[FF,'-hide_banner','-nostdin']
 if bounds:args+=['-ss',str(bounds[0]),'-t',str(bounds[1]-bounds[0])]
 q=subprocess.run(args+['-i',str(p),'-af','aformat=channel_layouts=mono,loudnorm=I=-16:TP=-3:LRA=7:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
 meter=json.loads(re.findall(r'\{[^{}]+\}',q.stderr,re.S)[-1])
 snd=parselmouth.Sound(str(p))
 if bounds:snd=snd.extract_part(bounds[0],bounds[1],preserve_times=False)
 f=snd.to_pitch_ac(time_step=.005,pitch_floor=100,pitch_ceiling=450).selected_array['frequency'];f=f[f>0];qs=np.quantile(f,[.1,.5,.9])
 y=np.mean(snd.values,axis=0);sr=snd.sampling_frequency;n=round(sr*.01);env=np.array([np.sqrt(np.mean(y[i:i+n]**2)) for i in range(0,len(y),n)]);active=np.where(env>10**(-42/20))[0]
 item={'name':name,'duration':snd.duration,'mono_lufs':float(meter['input_i']),'tp':float(meter['input_tp']),'pitch_hz':list(qs),'pitch_span_semitones':float(12*np.log2(qs[2]/qs[0])),'active_10ms_above_minus42db':[float(active[0]/100),float((active[-1]+1)/100)]}
 report.append(item);print(item,flush=True)
(R/'checks/natural-source-metrics.json').write_text(json.dumps(report,indent=2)+'\n')
