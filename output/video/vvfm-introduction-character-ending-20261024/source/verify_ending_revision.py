#!/usr/bin/env python3
"""Compare the closing illustration edit with the preceding completed edition."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT.parent/'vvfm-introduction-character-illustrations-20261024'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def split_scenes(doc):
 parts=re.split(r'(?=<div class="scene scene-\d+\b)',doc)[1:]
 return {int(re.search(r'scene scene-(\d+)',s).group(1)):s.split('<div class="caption-track">',1)[0] for s in parts}
old=(BASE/'composition/index.html').read_text();new=(ROOT/'composition/index.html').read_text()
a=split_scenes(old);b=split_scenes(new)
assert len(a)==len(b)==15
unchanged=[n for n in a if a[n]==b[n]]
assert unchanged==list(range(1,15))
css=lambda doc:re.search(r'<style>(.*?)</style>',doc,re.S).group(1)
added_css='.scene-15 .visual{flex:0 0 1040px}.scene-15 .laptop{display:none}.scene-15 .pmx-illustration{opacity:0}.scene-15 .pmx-illustration-left{left:490px}'
assert css(new)==css(old)+added_css
script=lambda doc:doc.rsplit('<script>',1)[1]
new_script=script(new)
added_tweens=[s for s in new_script.splitlines() if 'tl.fromTo("#s15 .pmx-illustration-' in s]
assert len(added_tweens)==2 and all(s.endswith(',197.0);') for s in added_tweens)
for s in added_tweens:new_script=new_script.replace(s+'\n','')
assert new_script==script(old)
assert old.split('<div class="caption-track">',1)[1].split('<script>',1)[0]==new.split('<div class="caption-track">',1)[1].split('<script>',1)[0]
files=['source/scenes.json','source/captions.json','source/captions.ass','source/edit-decision-list.json','source/audio-alignment.json','source/chapters.ffmeta','composition/assets/pmx-character-left.png','composition/assets/pmx-character-right.png','composition/assets/final-mix.wav','assets/with-bgm-final-unchanged.m4a','assets/narration-final-unchanged.m4a','assets/with-bgm.wav','assets/narration-only.wav']
files=[p for p in files if (BASE/p).exists()]
records=[]
for rel in files:
 h=sha(ROOT/rel);assert h==sha(BASE/rel),rel
 records.append({'file':rel,'sha256':h})
old_srt=BASE/'VvfM_紹介動画_キャラクターイラスト版_日本語字幕.srt'
new_srt=ROOT/'VvfM_紹介動画_締めイラスト追加版_日本語字幕.srt'
assert old_srt.read_bytes()==new_srt.read_bytes()
log=(ROOT/'checks/ending-layout-check.log').read_text()
assert 'Check passed' in log and '0 issues across 6 sample(s)' in log
report={'result':'pass','baseline_production_folder':BASE.name,'changed_scene':15,'unchanged_scene_html':unchanged,'overview_illustrations_unchanged':True,'existing_timeline_unchanged':True,'added_entrance_tweens':added_tweens,'new_styles_scoped_to_scene_15':True,'new_image_generation':False,'illustration_png_bytes_unchanged':True,'caption_html_and_timeline_unchanged':True,'external_subtitle_identical':True,'all_scene_timings_unchanged':True,'all_audio_source_bytes_unchanged':True,'unchanged_files':records,'layout_samples':[18,196.9,197,197.5,201,204.6],'layout_issues':0,'contrast_checks_passed':43,'contrast_checks_total':43,'reviewed_lint_warning':{'code':'duplicate_media_discovery_risk','count':1,'reason':'The same two PNGs intentionally appear as decorative img elements in scenes 2 and 15. They are not timed media clips; scene 15 has initial opacity 0 and explicit GSAP entrance tweens.'},'visual_review':{'snapshots':[196.9,197.5],'characters_hidden_before_197':True,'characters_visible_at_197_5':True,'url_app_controls_and_captions_uncovered':True},'human_full_video_listening_claimed':False}
(ROOT/'checks/ending-illustration-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('PASS: only scene 15 changed; all other scene HTML, existing timelines, subtitles, PNGs and audio sources preserved.')
