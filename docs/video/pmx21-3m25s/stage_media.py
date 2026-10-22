#!/usr/bin/env python3
"""Validate and stage explicitly supplied local media without downloading anything."""
from pathlib import Path
import argparse,hashlib,json,shutil
root=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--from-directory',type=Path,required=True,help='Local 205-second production output directory')
parser.add_argument('--check-only',action='store_true')
args=parser.parse_args()
manifest=json.loads((root/'media-manifest.json').read_text())
for item in manifest:
 relative=Path(item['file'])
 if relative.is_absolute()or'..'in relative.parts:raise SystemExit('Invalid media path')
 source=args.from_directory/relative
 digest=hashlib.sha256()
 with source.open('rb')as f:
  for block in iter(lambda:f.read(1048576),b''):digest.update(block)
 if source.stat().st_size!=item['bytes']or digest.hexdigest()!=item['sha256']:raise SystemExit(f'Media mismatch: {relative}')
print(f'Verified {len(manifest)} media files')
if not args.check_only:
 for item in manifest:
  destination=root/item['file'];destination.parent.mkdir(parents=True,exist_ok=True)
  shutil.copy2(args.from_directory/item['file'],destination)
 print('Media staged. Run the preparation commands in README.md.')
