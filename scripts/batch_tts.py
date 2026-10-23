"""One UTF-8 text file per slide, using the official local API v2 /tts endpoint."""
import argparse
import csv
import io
import json
import re
import sys
import time
import urllib.error
import urllib.request
import wave
from pathlib import Path

def load_jobs(manifest, out, overwrite=False):
    jobs, seen = [], set()
    with manifest.open(encoding='utf-8-sig', newline='') as f:
        for row in csv.DictReader(f):
            name = row['id'].strip()
            if not re.fullmatch(r'[A-Za-z0-9_-]+', name) or name in seen:
                raise ValueError(f'Unsafe or duplicated id: {name}')
            seen.add(name)
            text_file = manifest.parent / row['text_file']
            text = text_file.read_text(encoding='utf-8-sig').strip()
            if not text or '[REPLACE' in text:
                raise ValueError(f'Fill in the real speech text: {text_file}')
            if row['text_lang'] not in {'en','zh','all_zh','ja','all_ja','ko','all_ko','yue','all_yue','auto'}:
                raise ValueError(f'Invalid language: {row["text_lang"]}')
            target = out / f'{name}.wav'
            if target.exists() and not overwrite:
                raise FileExistsError(f'{target}: use --overwrite to regenerate')
            jobs.append((name, text, row['text_lang'], target))
    if not jobs:
        raise ValueError('Manifest has no jobs.')
    return jobs

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest', required=True, type=Path)
    p.add_argument('--reference', required=True, type=Path)
    p.add_argument('--prompt', required=True, type=Path)
    p.add_argument('--prompt-lang', default='en')
    p.add_argument('--out', type=Path, default=Path('output_audio'))
    p.add_argument('--url', default='http://127.0.0.1:9880')
    p.add_argument('--speed', type=float, default=1)
    p.add_argument('--timeout', type=float, default=1800)
    p.add_argument('--overwrite', action='store_true')
    p.add_argument('--dry-run', action='store_true')
    a = p.parse_args()
    if not 0.5 <= a.speed <= 2:
        p.error('Speed must be between 0.5 and 2.')
    jobs = load_jobs(a.manifest.resolve(), a.out.resolve(), a.overwrite)
    if not a.reference.is_file():
        p.error('Reference WAV is missing.')
    with wave.open(str(a.reference)) as f:
        duration = f.getnframes() / f.getframerate()
    if not 3 <= duration <= 10:
        p.error(f'Reference must be 3-10s, got {duration:.2f}s.')
    prompt = a.prompt.read_text(encoding='utf-8-sig').strip()
    if not prompt or '[REPLACE' in prompt:
        p.error('Write the exact reference transcript in reference.txt.')
    if a.dry_run:
        print(f'Validated {len(jobs)} jobs and reference {duration:.2f}s; no inference performed.')
        return
    a.out.mkdir(parents=True, exist_ok=True)
    results = []
    for name, text, lang, target in jobs:
        payload = dict(text=text, text_lang=lang, ref_audio_path=str(a.reference.resolve()),
                       prompt_text=prompt, prompt_lang=a.prompt_lang, text_split_method='cut5',
                       batch_size=1, media_type='wav', streaming_mode=False, speed_factor=a.speed,
                       seed=233333, parallel_infer=True)
        request = urllib.request.Request(a.url.rstrip('/')+'/tts', data=json.dumps(payload).encode('utf-8'),
                                         headers={'Content-Type': 'application/json'}, method='POST')
        start = time.monotonic()
        try:
            with urllib.request.urlopen(request, timeout=a.timeout) as response:
                data = response.read()
            with wave.open(io.BytesIO(data)) as audio:
                seconds = audio.getnframes() / audio.getframerate()
                if seconds <= 0:
                    raise ValueError('Empty WAV returned by API.')
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f'{name}: API HTTP {exc.code}: {exc.read(4000).decode(errors="replace")}') from exc
        temp = target.with_suffix('.wav.tmp')
        temp.write_bytes(data)
        temp.replace(target)
        results.append(dict(id=name, audio_seconds=seconds, generation_seconds=time.monotonic()-start, file=str(target)))
        (a.out / 'generation_report.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
        print(f'{name}: {seconds:.2f}s -> {target}', flush=True)
    print(f'Total audio: {sum(r["audio_seconds"] for r in results)/60:.2f} minutes. Listen before submission.')

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'FAILED: {exc}', file=sys.stderr)
        sys.exit(1)
