#!/usr/bin/env python3
"""Build the 205-second VvfM composition from verified local media."""
from pathlib import Path
import json,html,re,sys
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
COMP=ROOT/'composition'
scenes=json.loads((ROOT/'source/scenes.json').read_text())
TOTAL=sum(s['duration']for s in scenes)
E=html.escape
# Each excerpt retains its original speed. Crop rectangles are in source pixels.
app=(85,24,1110,696)
viewport=(379,58,815,413)
shots={
1:[(0,3.8,'01-opening.jpg',None,None),(3.4,12,'demo01.mp4',0,app)],
2:[(0,5.2,'demo01.mp4',12,app),(4.8,9.7,'02-overview.png',None,None),(9.3,14,'demo02.mp4',10,app)],
3:[(0,6.3,'03-bone-gizmo.png',None,(1900,210,850,640)),(5.9,12,'04-morph-smile.png',None,None)],
4:[(0,6.3,'02-overview.png',None,None),(5.9,19,'demo01.mp4',20,app)],
5:[(0,6.5,'03-bone-gizmo.png',None,(1980,245,760,570)),(6.1,12.9,'03-bone-gizmo.png',None,(0,580,480,800)),(12.5,20,'demo02.mp4',25,app)],
6:[(0,5.1,'04-morph-smile.png',None,None),(4.7,10.3,'06-morph-timeline.jpg',None,(1400,1250,1624,650)),(9.9,14.0,'05-camera-timeline.png',None,None),(13.6,17,'demo02.mp4',40,app)],
7:[(0,5.4,'demo01.mp4',55,app),(5.0,10.3,'02-overview.png',None,None),(9.9,14,'demo02.mp4',60,viewport)],
8:[(0,7.2,'06-closeup-dof-on.png',None,None),(6.8,13.2,'demo02.mp4',45,viewport),(12.8,19,'demo01.mp4',75,viewport)],
9:[(0,5.2,'06-closeup-dof-on.png',None,None),(4.8,11.4,'07-dof-settings.png',None,(110,420,950,600)),(11.0,16,'06-closeup-dof-on.png',None,None)],
10:[(0,6.7,'demo01.mp4',30,app),(6.3,13,'demo02.mp4',65,viewport)],
11:[(0,5.3,'demo02.mp4',10,app),(4.9,10.7,'demo02.mp4',15,app),(10.3,15,'02-overview.png',None,None)],
12:[(0,5.5,'demo02.mp4',80,viewport),(5.1,12.9,'01-hero.png',None,None),(12.5,18,'demo01.mp4',85,viewport)],
13:[(0,4.4,'13-ending.jpg',None,None),(4.0,9,'demo02.mp4',88,app)]}
shots[14]=shots.pop(12);shots[15]=shots.pop(13)
shots[12]=[(0,8,'pmx21-qdef-source.mov',0,(1160,340,1370,880))]
shots[13]=[(0,10,'pmx21-softbody-source.mov',.15,(1100,420,1600,850))]
# Shorten only the final hold of existing shots to meet the 205-second edit.
for scene in scenes:
 n=scene['id'];dur=scene['duration']
 shots[n]=[(a,min(b,dur),f,o,c)for a,b,f,o,c in shots[n]if a<dur]
copy={
1:('いつものMacで、','VMDを\nリアルタイム\n再生。','好きなキャラクターが、\nその場で動き出す。','PLAY YOUR FAVORITE'),
2:('VMD Viewer','for Mac','読み込んで、再生。\nそこから、自分好みに。','MEET VvfM'),
3:('出先のMacでも、','ちょっと調整。','気になる表情も、\nポーズも、手元のMacで。','ANYWHERE WITH YOUR MAC'),
4:('素材を読み込んで、','再生するだけ。','モデル・動き・音楽を\nひとつのシーンに。','LOAD → PLAY'),
5:('腕の角度から、','お気に入りの\nポーズへ。','ボーンを選ぶ。\n3Dギズモで動かす。','MAKE IT YOURS'),
6:('表情と構図で、','お気に入りの\n瞬間へ。','モーフの変化が、\nタイムラインで見える。','EXPRESSION + CAMERA'),
7:('動きを確認したら、','作品として\n残そう。','作業を保存。\n音声付きの動画へ。','SAVE YOUR SCENE'),
8:('ToonShader HQ','光も、輪郭も、\n自分好みに。','キャラクターの魅力を、\n見た目から引き出す。','FINISH THE LOOK'),
9:('DoF / 被写界深度','表情に、\nピントを。','顔を引き立て、\n背景はふんわり。','FOCUS ON YOUR FAVORITE'),
10:('.fxdayo 一部対応','ステージにも、\n演出を。','ペンライトや床反射で、\nシーンの楽しみを広げる。','BRING THE STAGE TO LIFE'),
11:('動きを支えるしくみ','CPU × Metal','姿勢・物理の計算と、\nGPUによる描画。','BEHIND THE MOTION'),
12:('Bulletの物理演算','髪や衣装に、\n自然な揺れ。','選べる、二つのモード。','PHYSICS IN MOTION'),
13:('VMD Viewer for Mac','Macで、\n気軽にMMD。','VMDをリアルタイム再生。','LET’S PLAY')}
copy[14]=copy.pop(12);copy[15]=copy.pop(13)
copy[12]=('PMX 2.1 / QDEF','ねじっても、\n形を保つ。','左：BDEF（PMX 2.0）\n右3本：QDEF（PMX 2.1）','PMX 2.1 — QDEF')
copy[13]=('PMX 2.1 / ソフトボディ','布も、ロープも、\nしなやかに。','固定した部分を支点に、\n柔らかく揺れる動き。','PMX 2.1 — SOFT BODY')
# Simple original vector doodles echo the reference without copying its artwork.
icons='''<svg class="doodle laptop" viewBox="0 0 180 140" aria-hidden="true"><path d="M25 15 Q82 10 150 19 L155 104 23 104Z" fill="#D5EDE0" stroke="#202632" stroke-width="4"/><path d="M36 29 L137 31 140 87 35 86Z" fill="#FAFAF6" stroke="#202632" stroke-width="3"/><path d="M23 104 L7 124 Q82 134 174 123 L155 104" fill="#F4CAD6" stroke="#202632" stroke-width="4"/><path d="M77 48 L103 61 77 76Z" fill="#285CDE" stroke="#202632" stroke-width="2"/></svg><svg class="doodle star" viewBox="0 0 100 100" aria-hidden="true"><path d="M50 5 61 35 95 38 69 60 76 94 49 75 20 93 27 59 5 37 38 34Z" fill="#F5D875" stroke="#202632" stroke-width="3"/></svg><svg class="doodle music" data-layout-ignore viewBox="0 0 100 110" aria-hidden="true"><path d="M34 80 L34 25 78 14 78 70 M35 40 L77 29" fill="none" stroke="#202632" stroke-width="6"/><ellipse cx="22" cy="84" rx="16" ry="12" fill="#F4CAD6" stroke="#202632" stroke-width="3"/><ellipse cx="66" cy="74" rx="16" ry="12" fill="#D5EDE0" stroke="#202632" stroke-width="3"/></svg>'''
css='''@font-face{font-family:"Hiragino Maru Gothic ProN";src:local("Hiragino Maru Gothic ProN")}@font-face{font-family:"Hiragino Sans";src:local("Hiragino Sans")}*{box-sizing:border-box;margin:0;padding:0}html,body{width:1920px;height:1080px;overflow:hidden;background:#FAFAF6;color:#202632}body{font-family:"Hiragino Maru Gothic ProN","Hiragino Sans",sans-serif}.scene{position:absolute;inset:0;width:1920px;height:1080px;background:#FAFAF6;overflow:hidden}.scene+.scene{opacity:0}.scene-content{width:100%;height:100%;padding:54px 72px 132px;display:flex;flex-direction:column;gap:28px;box-sizing:border-box}.header{display:flex;justify-content:space-between;align-items:center;height:52px;flex-shrink:0}.brand{font-size:26px;font-weight:700;letter-spacing:.02em}.chapter{font-family:Menlo,monospace;font-size:23px;letter-spacing:.07em;color:#4D5663}.page{border:2px solid #202632;border-radius:50%;width:48px;height:48px;display:flex;align-items:center;justify-content:center;background:#F5D875;font-family:Menlo;font-size:24px}.main{display:flex;gap:42px;align-items:center;flex:1;min-height:0}.copy{display:flex;flex-direction:column;gap:29px;width:515px;flex-shrink:0;padding-bottom:32px;position:relative;z-index:3}.eyebrow{font-size:34px;font-weight:700;line-height:1.5}.title{font-size:76px;font-weight:900;line-height:1.34;letter-spacing:-.045em;white-space:pre-line;overflow-wrap:normal}.lead{font-size:31px;font-weight:400;line-height:1.85;white-space:pre-line}.marker{background:linear-gradient(transparent 64%,#F5D875 64%,#F5D875 93%,transparent 93%);box-decoration-break:clone;-webkit-box-decoration-break:clone}.visual{position:relative;flex:1;min-width:0;height:726px;display:flex;align-items:center;justify-content:center;z-index:2}.paper-shadow{position:absolute;inset:30px -8px 20px 12px;border:3px solid #202632;border-radius:26px;background:#D5EDE0;transform:rotate(1.3deg);z-index:0}.shot{position:absolute;inset:19px 0 30px;display:flex;align-items:center;justify-content:center;background:#FAFAF6;border:3px solid #202632;border-radius:22px;overflow:hidden;z-index:1}.shot:not(:first-of-type){opacity:0}.media-crop{position:relative;overflow:hidden;flex-shrink:0;max-width:100%;max-height:100%;background:#202632}.media-crop img,.media-crop video{position:absolute;max-width:none;max-height:none;object-fit:fill}.detail-multi{gap:28px}.detail-multi .shot-label{left:auto;right:25px;bottom:36px}.shot-label{position:absolute;left:22px;bottom:21px;z-index:3;background:#FAFAF6;color:#202632;border:2px solid #202632;border-radius:10px;padding:9px 16px;font-size:23px;max-width:90%;font-weight:600}.annotation{position:absolute;z-index:8;right:30px;top:0;transform:rotate(2deg);padding:15px 22px;background:#F5D875;border:2px solid #202632;box-shadow:4px 4px 0 #202632;border-radius:10px;font-size:30px;font-weight:700}.badge{display:inline-flex;width:max-content;max-width:100%;background:#D5EDE0;border:2px solid #202632;padding:12px 20px;border-radius:14px;font-size:25px;line-height:1.5}.caption-track{position:absolute;left:72px;right:72px;bottom:18px;height:116px;display:flex;align-items:center;justify-content:center;border-top:2px solid #202632;z-index:90}.caption{position:absolute;inset:12px 0 0;display:flex;align-items:center;justify-content:center;text-align:center;font-size:38px;font-weight:600;line-height:1.35;white-space:pre-line;opacity:0;background:#FAFAF6}.doodle{position:absolute;z-index:1;pointer-events:none}.laptop{width:142px;left:425px;bottom:145px;transform:rotate(-12deg)}.star{width:75px;right:25px;top:120px;transform:rotate(12deg)}.music{width:70px;left:-15px;top:405px;transform:rotate(-12deg)}.paper-loop{position:absolute;width:240px;height:130px;border:2px solid #202632;border-radius:55% 45% 45% 55%;right:-110px;bottom:80px;transform:rotate(-23deg);background:#F4CAD6}.paper-tab{position:absolute;width:145px;height:76px;left:-65px;top:130px;background:#D5EDE0;border:2px solid #202632;border-radius:22px;transform:rotate(-10deg)}.step-list{display:flex;flex-direction:column;gap:16px;margin-top:4px}.step{font-size:29px;display:flex;align-items:center;gap:16px}.step b{font-family:Menlo,monospace;background:#F5D875;border:2px solid #202632;border-radius:12px;padding:8px 13px;min-width:106px;text-align:center}.tech-lines{display:flex;flex-direction:column;gap:18px}.tech-row{display:flex;gap:18px;align-items:center;font-size:28px}.tech-row strong{font-family:Menlo,monospace;display:flex;justify-content:center;align-items:center;background:#D5EDE0;border:2px solid #202632;border-radius:12px;min-width:112px;min-height:56px}.mode{display:flex;flex-direction:column;gap:9px;border:2px solid #202632;border-radius:15px;padding:18px;background:#D5EDE0;font-size:28px}.mode:nth-child(2){background:#F4CAD6}.mode small{font-size:22px}.footer-link{font-family:Menlo,monospace;font-size:25px;line-height:1.65;word-break:break-word;color:#285CDE}.ai-credit{font-size:20px;color:#4D5663}.scene-1 .title{font-size:77px}.scene-2 .eyebrow{font-size:49px}.scene-2 .title{font-size:92px}.scene-11 .title{font-size:72px}.scene-12 .title{font-size:73px}.scene-13 .title{font-size:68px}.scene-14 .title{font-size:68px}.scene-15 .title{font-size:74px}.scene-15 .copy{width:550px;gap:25px}.pmx-label{position:absolute;top:83%;transform:translateX(-50%);background:#FAFAF6;color:#202632;border:2px solid #202632;border-radius:8px;padding:8px 10px;font-size:21px;line-height:1.4;white-space:nowrap;text-align:center;z-index:6}.pmx-label small{font-size:18px;display:block}.small-note{font-size:20px;line-height:1.55;color:#4D5663}.progress-line{position:absolute;bottom:0;left:0;height:7px;width:1920px;background:#285CDE;transform-origin:left center;z-index:100}.full-feature .copy{width:440px}.full-feature .title{font-size:70px}.static-tag{font-size:19px;position:absolute;right:17px;bottom:9px;color:#4D5663;z-index:5}.arrow{font-size:38px;color:#285CDE;align-self:center}.workflow{display:flex;gap:12px;align-items:center;flex-wrap:wrap}.workflow span{font-size:26px;border:2px solid #202632;background:#D5EDE0;border-radius:12px;padding:14px}.workflow span:last-child{background:#F4CAD6}'''
# Every phrase is assigned a measured interval after audio preparation; a first
# authoring pass uses paragraph-proportional timings without generating audio.
cap_file=ROOT/'source/captions.json'
caps=json.loads(cap_file.read_text()) if cap_file.exists() else []
if not caps:
 for s in scenes:
  parts=[x for x in re.findall(r'[^。]+。?',s['narration']) if x]
  lengths=[len(x)for x in parts];avail=s['duration']-1.5;t=s['start']+.7
  for p,L in zip(parts,lengths):
   d=avail*L/sum(lengths);caps.append({'text':p,'start':t,'end':t+d-.08});t+=d
htmls=[];anim=[];shot_manifest=[]
for s in scenes:
 n=s['id'];base=s['start'];dur=s['duration'];ey,title,lead,chapter=copy[n];sid=f's{n}'
 extra=''
 if n==4:extra='<div class="step-list"><div class="step"><b>PMX</b>モデル</div><div class="step"><b>VMD</b>動き</div><div class="step"><b>WAV</b>音楽</div></div>'
 if n==5:extra='<div class="badge">選ぶ → 動かす → キー登録</div>'
 if n==6:extra='<div class="badge">横：フレーム　縦：値 0〜1</div>'
 if n==7:extra='<div class="workflow"><span>プロジェクト保存</span><i class="arrow">→</i><span>音声付き動画</span></div>'
 if n==8:extra='<div class="tech-lines"><div class="tech-row">輪郭線 / RimLight</div><div class="tech-row">Bloom / Diffusion</div></div>'
 if n==9:extra='<div class="badge">ToonShader HQ・透視投影</div>'
 if n==10:extra='<div class="tech-lines"><div class="tech-row">MobFesPenlight_3</div><div class="tech-row">MMDayo_SSR</div></div>'
 if n==11:extra='<div class="tech-lines"><div class="tech-row"><strong>CPU</strong>姿勢・物理</div><div class="tech-row"><strong>GPU</strong>Metal描画</div></div><div class="badge">PMX 2.0 / 2.1 対応</div><p class="small-note">収録画面内のモデルはPMX 2.0です。</p>'
 if n==14:extra='<div class="tech-lines"><div class="mode"><b>3.25 ネイティブ</b></div><div class="mode"><b>2.75 互換</b><small>既知の動きの違いを調整</small></div></div><p class="small-note">両モードともBullet 3.25を使用。</p>'
 if n==15:extra='<div class="footer-link"><span style="display:block">配布情報・使い方</span>github.com/opopoposiop/VvfM</div><p class="ai-credit">AIナレーション：HeyGen Jhenny</p>'
 if n==12:extra='<div class="badge">ねじり変形を比較</div><p class="small-note">PMX 2.1テストモデルによる実演。</p>'
 if n==13:extra='<div class="tech-lines"><div class="tech-row">頂点固定 / 剛体アンカー</div><div class="tech-row">両端固定のロープ</div></div><p class="small-note">PMX 2.1テストモデルによる実演。</p>'
 media=[]
 for j,(a,b,file,offset,crop) in enumerate(shots[n]):
  video=file.endswith(('.mp4','.mov'));iw,ih=((2926,1750)if file.startswith('pmx21-')else(1280,720))if video else Image.open(COMP/'assets'/file).size
  x,y,cw,ch=crop or (0,0,iw,ih)
  # Fit region without stretching; height caps at 660 px.
  maxw=1195 if n not in (1,15) else 1150
  maxh=660;scale=min(maxw/cw,maxh/ch);w=cw*scale;h=ch*scale
  id=f'{sid}m{j}'
  style=f'left:{-x/cw*100:.5f}%;top:{-y/ch*100:.5f}%;width:{iw/cw*100:.5f}%;height:{ih/ch*100:.5f}%;'
  attrs=f'id="{id}media" src="assets/{file}" style="{style}"'
  if video:
   attrs+=f' class="clip" data-start="{base+a:.3f}" data-duration="{b-a:.3f}" data-media-start="{offset}" data-track-index="{100+n*10+j}" muted playsinline preload="auto"'
   content=f'<video {attrs}></video>'
  else:
   attrs+=f' class="clip" data-start="{base+a:.3f}" data-duration="{b-a:.3f}" data-track-index="{100+n*10+j}"'
   content=f'<img {attrs} alt="{E(s["title"])}">'
  if n==12:
   content+=''.join(f'<div class="pmx-label" style="left:{x}%">{label}</div>'for x,label in [(16.1,'BDEF 2.0'),(38.3,'QDEF<small>ウェイト合計 1.0</small>'),(61.0,'QDEF<small>ウェイト合計 0.5</small>'),(83.2,'QDEF<small>ウェイト合計 4.0</small>')])
  if n==13:
   content+=''.join(f'<div class="pmx-label" style="left:{x}%">{label}</div>'for x,label in [(16,'頂点固定の布'),(47,'剛体アンカーの布'),(78,'両端固定ロープ')])
  label='';
  if n==5 and j==0:label='3Dギズモで腕の角度を調整'
  if n==5 and j==1:label='数値で調整 → キー登録'
  if n==6 and j==1:label='モーフの値と音声波形を見比べる'
  if n==9 and j==1:label='焦点ターゲットをキーに記録'
  companion=""
  if n==5 and j==1:
   companion='<div class="media-crop" style="width:700px;height:525px" data-layout-allow-overflow><img src="assets/03-bone-gizmo.png" alt="右腕の回転ギズモ" style="left:-260.526%;top:-42.982%;width:379.737%;height:307.368%"></div>'
  media.append(f'<div class="shot {"detail-multi" if companion else ""}" id="{id}" style="opacity:{1 if j==0 else 0}" data-layout-allow-overflow><div class="media-crop" style="width:{w:.2f}px;height:{h:.2f}px" data-layout-allow-overflow>{content}</div>{companion}{f"<div class=shot-label>{label}</div>" if label else ""}</div>')
  if j:
   prev=f'{sid}m{j-1}';t=base+a
   anim.append(f'tl.to("#{prev}",{{opacity:0,duration:.4,ease:"sine.inOut"}},{t});tl.fromTo("#{id}",{{opacity:0}},{{opacity:1,duration:.4,ease:"sine.inOut"}},{t});')
  if not video and n in(1,3,8,9,15):
   anim.append(f'tl.fromTo("#{id} .media-crop",{{scale:1}},{{scale:1.035,duration:{max(1,b-a-.4):.2f},ease:"sine.inOut"}},{base+a+.3});')
  shot_manifest.append({'scene':n,'start':base+a,'end':base+b,'source':file,'source_start':offset,'crop':crop,'playback_rate':1 if video else None})
 badge='VMDをリアルタイム再生'if n in(1,4) else ('お気に入りを、自分の手で'if n==2 else '')
 visual=f'<div class="visual"><div class="paper-shadow" data-layout-ignore></div>{"".join(media)}{f"<div class=annotation>{badge}</div>"if badge else ""}</div>'
 content=f'<div class="scene scene-{n}" id="{sid}" style="z-index:{n};opacity:{1 if n==1 else 0}"><div class="paper-loop" data-layout-ignore></div><div class="paper-tab" data-layout-ignore></div>{icons}<div class="scene-content"><div class="header"><div class="brand">VMD Viewer for Mac</div><div class="chapter">{E(chapter)}</div><div class="page">{n:02}</div></div><div class="main"><div class="copy"><div class="eyebrow">{E(ey)}</div><h1 class="title"><span class="marker">{E(title)}</span></h1><p class="lead">{E(lead)}</p>{extra}</div>{visual}</div></div></div>'
 htmls.append(content)
 if n>1:
  # Whole-scene crossfade is the exit; no child exits before the transition.
  anim.append(f'tl.to("#s{n-1}",{{opacity:0,duration:.5,ease:"power2.inOut"}},{base});tl.fromTo("#{sid}",{{opacity:0}},{{opacity:1,duration:.5,ease:"power2.inOut"}},{base});')
 for k,(sel,props,delay,length)in enumerate([
  ('.eyebrow','x:-22,opacity:0,ease:"power3.out"',.18,.45),
  ('.title','y:30,opacity:0,ease:"back.out(1.1)"',.3,.6),
  ('.lead','x:-15,opacity:0,ease:"sine.out"',.48,.5),
  ('.visual','scale:.97,opacity:0,ease:"power2.out"',.15,.65),
  ('.header','y:-8,opacity:0,ease:"sine.out"',.12,.4),
  ('.badge,.step-list,.tech-lines,.workflow,.footer-link,.small-note,.ai-credit','y:12,opacity:0,ease:"power3.out"',.62,.45),
  ('.doodle','scale:.7,opacity:0,ease:"back.out(1.6)"',.45,.55)]):
  anim.append(f'if(document.querySelector("#{sid} {sel.split(",")[0]}"))tl.from("#{sid} {sel.replace(",",",#"+sid+" ")}",{{{props},duration:{length},immediateRender:false}},{base+delay});')
 anim.append(f'tl.to("#{sid} .star",{{rotation:20,y:-8,duration:3.4,repeat:{max(1,int(dur/3.4)-1)},yoyo:true,ease:"sine.inOut"}},{base+.3});')
 anim.append(f'tl.to("#{sid} .music",{{rotation:-5,y:9,duration:4,repeat:{max(1,int(dur/4)-1)},yoyo:true,ease:"sine.inOut"}},{base+.2});')
if "--visual-only" in sys.argv:caps=[]
caption_html=[]
for i,c in enumerate(caps):
 text=c['text']
 # Balanced Japanese lines, keeping original punctuation.
 if len(text)>37:
  split=min(range(max(8,len(text)-42),min(len(text)-7,43)),key=lambda k:(0 if text[k-1]in'、。'else 100)+abs(k-len(text)/2))
  text=text[:split]+'\n'+text[split:]
 caption_html.append(f'<div id="cap{i}" class="caption">{E(text)}</div>')
 anim.append(f'tl.fromTo("#cap{i}",{{opacity:0,y:4}},{{opacity:1,y:0,duration:.15,ease:"sine.out"}},{c["start"]:.3f});tl.set("#cap{i}",{{opacity:0}},{c["end"]:.3f});')
anim.append('tl.fromTo(".progress-line",{scaleX:0},{scaleX:1,duration:205,ease:"none"},0);')
anim.append('tl.to("#s15",{opacity:0,duration:.65,ease:"sine.inOut"},204.35);')
audio='<audio id="final-audio" class="clip" src="assets/final-mix.wav" data-start="0" data-duration="205" data-track-index="300" data-volume="1"></audio>'if(COMP/'assets/final-mix.wav').exists() and '--visual-only' not in sys.argv else''
doc='<!doctype html><html lang="ja"><head><meta charset="UTF-8"><meta name="viewport" content="width=1920,height=1080"><script src="assets/gsap.min.js"></script><style>'+css+'</style></head><body><div id="root" data-composition-id="main" data-start="0" data-duration="205" data-width="1920" data-height="1080" data-fps="24">'+''.join(htmls)+'<div class="caption-track">'+''.join(caption_html)+'</div><div class="progress-line" data-layout-ignore></div>'+audio+'</div><script>window.__timelines=window.__timelines||{};const tl=gsap.timeline({paused:true});\n'+'\n'.join(anim)+'\nwindow.__timelines.main=tl;</script></body></html>'
(COMP/'index.html').write_text(doc)
(ROOT/'source/edit-decision-list.json').write_text(json.dumps(shot_manifest,ensure_ascii=False,indent=2)+'\n')
print(f'Built {len(scenes)} scenes, {len(shot_manifest)} shots, {len(caps)} captions; duration 205 s')
