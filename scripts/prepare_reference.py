"""Extract one clean reference segment; transcript must describe this exact segment."""
import argparse
import subprocess
import wave
from pathlib import Path

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('input', type=Path)
    p.add_argument('--start', type=float, default=0)
    p.add_argument('--duration', type=float, default=7)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--overwrite', action='store_true')
    a = p.parse_args()
    if not a.input.is_file() or a.start < 0 or not 3 <= a.duration <= 10:
        p.error('Need an existing recording, start >= 0 and duration between 3 and 10 seconds.')
    if a.output.exists() and not a.overwrite:
        p.error('Output exists. Use --overwrite only when replacing intentionally.')
    a.output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['ffmpeg', '-y' if a.overwrite else '-n', '-ss', str(a.start), '-i', str(a.input),
                    '-t', str(a.duration), '-vn', '-ac', '1', '-ar', '32000', '-c:a', 'pcm_s16le', str(a.output)], check=True)
    with wave.open(str(a.output)) as f:
        duration = f.getnframes() / f.getframerate()
    if not 3 <= duration <= 10:
        a.output.unlink()
        raise SystemExit(f'Extracted segment is {duration:.2f}s. Choose a longer source segment.')
    print(f'Ready: {a.output} ({duration:.2f}s). Listen and transcribe it into reference.txt.')

if __name__ == '__main__':
    main()
