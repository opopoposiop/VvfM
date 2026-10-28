#!/usr/bin/env python3
"""Record the requested Harema narration through the official OpenAI Live SDK.
One bounded session per scene; retain original PCM and transcripts, and close each session.
No microphone audio, reference audio, custom voices, or backend delegation are used.
"""
from pathlib import Path
import argparse,asyncio,base64,hashlib,importlib.metadata,json,os,time,wave
import numpy as np
from openai import AsyncOpenAI
R=Path(__file__).resolve().parents[1];SR=24000
REQUEST=json.loads((R/'source/harema-narration-request.json').read_text())
INSTRUCTIONS=('あなたは日本語の紹介動画のナレーターです。標準的な日本語の自然なアクセントで、落ち着いて親しみやすく、明瞭に読みます。'
 '原稿の抑揚は自然に保ち、語頭だけを強く高くしません。速さと声量を一定にし、文と文の間には短い間を入れます。'
 '仕事は原稿の朗読だけです。提供された原稿を最初から最後まで正確に、一度だけ読み上げてください。'
 '挨拶、相づち、説明、感想、質問、見出し、原稿の引用符を追加しません。原稿の語句を省略、言い換え、補足、繰り返ししません。'
 'ひらがなとカタカナで示した名称と数字の読みを、そのまま発声します。英語に置き換えません。'
 'ツールや別のエージェントを呼ばず、自分で読み上げます。読み終えた後は無言で待ってください。')

def savejson(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def safe(s):
 key=os.environ.get('OPENAI_API_KEY','')
 return str(s).replace(key,'[REDACTED]')if key else str(s)

async def record(client,scene):
 sid=scene['scene'];stem=f'harema-scene{sid:02d}';out=R/'assets'/f'{stem}-raw.wav';proof=R/'checks'/f'{stem}-live.json'
 if out.exists()or proof.exists():raise RuntimeError(f'Refusing to overwrite {stem}')
 prompt='録音を開始します。今すぐ次の原稿だけを、一度、全文読み上げてください。原稿：\n'+scene['spoken']
 config={'model':'gpt-live-1','instructions':INSTRUCTIONS,'input':[{'type':'message','role':'developer','content':[{'type':'input_text','text':prompt}]}], 'audio':{'format':{'type':'audio/pcm','rate':SR},'output':{'voice':'harema'}},'delegation':{'type':'client'},'store':False}
 savejson(R/'source'/f'{stem}-session.json',config)
 pcm=bytearray();events=[];fragments=[];ready=False;closed=False;closing=False;started_meta=None;final_meta=None;sender=None;error=None;stop_reason=None
 t0=time.monotonic();last_voice=None;last_text=None;voice_detected=False
 eventlog=(R/'checks'/f'{stem}-events.jsonl').open('x',encoding='utf-8')
 try:
  async with client.live.connect(max_retries=0,websocket_connection_options={'open_timeout':15,'close_timeout':5}) as conn:
   async def send_silence():
    zero=base64.b64encode(bytes(4800)).decode('ascii');deadline=time.monotonic()
    while not closing:
     await conn.session.input_audio.append(audio=zero)
     deadline+=.1
     await asyncio.sleep(max(0,deadline-time.monotonic()))
   async def request_close(why):
    nonlocal closing,stop_reason
    if not closing:
     closing=True;stop_reason=why
     if sender:sender.cancel()
     await conn.session.close(event_id=f'close_scene_{sid:02d}')
   await conn.session.start(session=config,event_id=f'start_scene_{sid:02d}')
   close_time=None
   while True:
    now=time.monotonic();elapsed=now-t0
    if not closing:
     if elapsed>45:await request_close('maximum_session_duration');close_time=now
     elif not voice_detected and elapsed>18:await request_close('no_speech_timeout');close_time=now
     elif voice_detected and now-last_voice>2.5 and (last_text is None or now-last_text>1.5):
      await request_close('speech_followed_by_silence');close_time=now
    if closing and close_time is None:close_time=now
    if closing and now-close_time>10:raise RuntimeError('Session close was not confirmed within 10 seconds')
    try:event=await asyncio.wait_for(conn.recv(),timeout=.25)
    except asyncio.TimeoutError:continue
    data=event.model_dump(mode='json',exclude_none=True);kind=event.type
    if kind=='session.output_audio.delta':
     chunk=base64.b64decode(event.delta);pcm.extend(chunk)
     if len(chunk)%2:raise RuntimeError('Odd-length PCM delta')
     y=np.frombuffer(chunk,'<i2').astype(np.float64)
     if len(y)and np.sqrt(np.mean(y*y))>90 and np.max(np.abs(y))>250:last_voice=time.monotonic();voice_detected=True
    else:
     data['received_elapsed_seconds']=round(time.monotonic()-t0,4);data['captured_audio_seconds']=len(pcm)/(2*SR)
     eventlog.write(json.dumps(data,ensure_ascii=False)+'\n');eventlog.flush();events.append(kind)
     if kind=='session.started':
      ready=True;started_meta=data
      resolved=data.get('session',{}).get('audio',{}).get('output',{}).get('voice')
      if resolved is not None and resolved!='harema':raise RuntimeError(f'Unexpected resolved voice: {resolved}')
      sender=asyncio.create_task(send_silence())
      await asyncio.sleep(.1)
      await conn.session.commentary.append(content=prompt,delegation_id=None,event_id=f'read_scene_{sid:02d}')
      print(f'Scene {sid:02d}: Harema session started',flush=True)
     elif kind=='session.output_transcript.delta':
      fragments.append(data);last_text=time.monotonic();print(event.delta,end='',flush=True)
     elif kind=='error':
      error=data
      if ready:await request_close('server_error')
      else:raise RuntimeError(safe(data))
     elif kind=='session.closed':closed=True;final_meta=data;break
   if sender:
    sender.cancel();await asyncio.gather(sender,return_exceptions=True)
 except BaseException as e:
  error=error or {'exception':type(e).__name__,'message':safe(e)}
 finally:
  if sender:
   sender.cancel();await asyncio.gather(sender,return_exceptions=True)
  eventlog.close()
  if pcm:
   with wave.open(str(out),'wb')as w:w.setparams((1,2,SR,0,'NONE','not compressed'));w.writeframes(pcm)
  report={'scene':sid,'model':'gpt-live-1','voice_requested':'harema','input':scene['spoken'],'request_file':f'source/{stem}-session.json','audio_file':str(out.relative_to(R))if pcm else None,'audio_seconds':len(pcm)/(2*SR),'audio_sha256':sha(out)if pcm else None,'elapsed_seconds':time.monotonic()-t0,'session_started':started_meta,'session_closed':final_meta,'graceful_close_confirmed':closed,'stop_reason':stop_reason,'transcript':''.join(d['delta']for d in fragments),'transcript_fragments':fragments,'events':events,'error':error,'external_audio_uploaded':'synthetic silence only; no user audio','exact_script_validation':'pending','sdk_version':importlib.metadata.version('openai')}
  report['capture_result']='pass'if ready and closed and voice_detected and pcm and not error and stop_reason=='speech_followed_by_silence'else'fail'
  savejson(proof,report);print(f'\nScene {sid:02d}: {report["capture_result"]}, {report["audio_seconds"]:.2f}s captured, closed={closed}',flush=True)
 if report['capture_result']!='pass':raise RuntimeError(f'Scene {sid:02d} capture failed: {safe(error or stop_reason)}')
 return report

async def main(ids):
 assert os.environ.get('OPENAI_API_KEY'),'OPENAI_API_KEY is required'
 async with AsyncOpenAI(max_retries=0,timeout=20) as client:
  for scene in REQUEST['scenes']:
   if scene['scene']in ids:await asyncio.wait_for(record(client,scene),timeout=65)
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--scenes',required=True,help='Comma-separated scene numbers');args=parser.parse_args()
 asyncio.run(main({int(x)for x in args.scenes.split(',')}))
