"""Match ES0003_Slide_01.png / slide_01.wav pairs and encode a narrated MP4."""
import argparse
import subprocess
import tempfile
import wave
from pathlib import Path

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--images', type=Path, required=True)
    p.add_argument('--audio', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--count', type=int, default=14)
    p.add_argument('--overwrite', action='store_true')
    a = p.parse_args()
    if a.count < 1:
        p.error('Count must be positive.')
    if a.output.exists() and not a.overwrite:
        p.error('Output exists. Use --overwrite to replace.')
    jobs = []
    for i in range(1,a.count+1):
        image, audio = a.images / f'ES0003_Slide_{i:02d}.png', a.audio / f'slide_{i:02d}.wav'
        if not image.is_file() or not audio.is_file():
            p.error(f'Missing image/audio pair for slide {i:02d}.')
        with wave.open(str(audio)) as w:
            duration = w.getnframes()/w.getframerate()
        if duration <= 0:
            p.error(f'Empty audio: {audio}')
        jobs.append((image.resolve(),audio.resolve(),duration))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='gsv_video_') as tmp:
        tmp = Path(tmp)
        for i,(image,audio,duration) in enumerate(jobs):
            subprocess.run(['ffmpeg','-v','error','-y','-loop','1','-framerate','30','-i',str(image),'-i',str(audio),
                '-vf','scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2',
                '-c:v','libx264','-tune','stillimage','-preset','fast','-crf','18','-pix_fmt','yuv420p',
                '-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-af','apad=pad_dur=0.5',
                '-t',str(duration+0.5),str(tmp/f'{i:03d}.mp4')], check=True)
        (tmp/'concat.txt').write_text(''.join(f"file '{i:03d}.mp4'\n" for i in range(len(jobs))),encoding='ascii')
        subprocess.run(['ffmpeg','-v','error','-y' if a.overwrite else '-n','-f','concat','-safe','0','-i',str(tmp/'concat.txt'),
                        '-c','copy','-movflags','+faststart',str(a.output.resolve())],check=True)
    print(f'Created: {a.output}; planned duration {sum(j[2]+0.5 for j in jobs)/60:.2f} min.')

if __name__ == '__main__':
    main()
