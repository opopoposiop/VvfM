#!/usr/bin/env python3
"""Convert an already-cached OpenAI Whisper medium model for local MLX validation.
Weight/config mapping adapted from Apple mlx-examples whisper/convert.py:
https://github.com/ml-explore/mlx-examples/blob/main/whisper/convert.py
Copyright 2023-2024 Apple Inc., MIT license.
No network access or audio upload.
"""
from pathlib import Path
import json,hashlib
import mlx.core as mx
from mlx.utils import tree_flatten
from mlx_whisper.whisper import Whisper,ModelDimensions
R=Path(__file__).resolve().parents[1]
source=next(Path('/Users/minmin/.cache/huggingface/hub/models--openai--whisper-medium/snapshots').glob('*/model.safetensors')).parent
out=Path('/private/tmp/vvfm-harema-whisper-medium-mlx');out.mkdir(exist_ok=True)
c=json.loads((source/'config.json').read_text())
keys={'n_mels':'num_mel_bins','n_audio_ctx':'max_source_positions','n_audio_state':'d_model','n_audio_head':'encoder_attention_heads','n_audio_layer':'encoder_layers','n_vocab':'vocab_size','n_text_ctx':'max_target_positions','n_text_state':'d_model','n_text_head':'decoder_attention_heads','n_text_layer':'decoder_layers'}
config={k:c[v]for k,v in keys.items()}
mapping=[('model.',''),('.layers','.blocks'),('.self_attn','.attn'),('.attn_layer_norm','.attn_ln'),('.encoder_attn.','.cross_attn.'),('.encoder_attn_layer_norm','.cross_attn_ln'),('.final_layer_norm','.mlp_ln'),('.q_proj','.query'),('.k_proj','.key'),('.v_proj','.value'),('.out_proj','.out'),('.fc1','.mlp1'),('.fc2','.mlp2'),('embed_positions.weight','positional_embedding'),('decoder.embed_tokens','decoder.token_embedding'),('encoder.layer_norm','encoder.ln_post'),('decoder.layer_norm','decoder.ln')]
weights={}
for k,v in mx.load(str(source/'model.safetensors')).items():
 if k=='proj_out.weight':continue
 for a,b in mapping:k=k.replace(a,b)
 if k=='encoder.positional_embedding':continue
 if 'conv'in k and v.ndim==3:v=mx.swapaxes(v,1,2)
 weights[k]=v.astype(mx.float16)
model=Whisper(ModelDimensions(**config),mx.float16)
model.set_alignment_heads(b'ABzY8B0Jh+0{>%R7}kK1fFL7w6%<-Pf*t^=N)Qr&0RR9')
weights['alignment_heads']=model.alignment_heads
expected=dict(tree_flatten(model.parameters()));assert set(weights)==set(expected),(set(expected)-set(weights),set(weights)-set(expected))
assert all(v.shape==expected[k].shape for k,v in weights.items())
mx.save_safetensors(str(out/'weights.safetensors'),weights);(out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
proof={'source_model':'openai/whisper-medium','source_snapshot':source.name,'local_model_path':str(out),'weights':len(weights),'all_parameter_names_and_shapes_validated':True,'precision':'float16','network_used':False,'source_mapping_reference':'https://github.com/ml-explore/mlx-examples/blob/main/whisper/convert.py'}
(R/'checks/local-asr-model-provenance.json').write_text(json.dumps(proof,indent=2)+'\n');print(proof)
