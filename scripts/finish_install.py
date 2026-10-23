import argparse
import importlib.metadata
import re
import shutil
import subprocess
import sys
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--repo', type=Path, required=True)
p.add_argument('--device', choices=['CU126', 'CU128'], required=True)
a = p.parse_args()
# The source also exposes a portable-runtime FFmpeg path used by API encoders.
(a.repo / 'runtime').mkdir(exist_ok=True)
for binary in ('ffmpeg', 'ffprobe'):
    source = shutil.which(binary)
    if source is None:
        raise RuntimeError(f'{binary} not found in the activated Conda environment')
    shutil.copy2(source, a.repo / 'runtime' / f'{binary}.exe')
if (Path(sys.prefix) / 'nltk_data').is_dir():
    shutil.copytree(Path(sys.prefix) / 'nltk_data', a.repo / 'runtime/nltk_data', dirs_exist_ok=True)
torch_version = importlib.metadata.version('torch').split('+')[0]
subprocess.run([sys.executable, '-m', 'pip', 'install', f'torchaudio=={torch_version}',
                '--index-url', f'https://download.pytorch.org/whl/{a.device.lower()}'], check=True)
# Keep the original models and algorithms. Only bind Gradio UIs to loopback.
changed = []
for file in a.repo.rglob('*.py'):
    original = file.read_text(encoding='utf-8-sig')
    patched = re.sub(r'''server_name\s*=\s*(["'])0\.0\.0\.0\1''', 'server_name="127.0.0.1"', original)
    if patched != original:
        file.write_text(patched, encoding='utf-8')
        changed.append(str(file.relative_to(a.repo)))
(a.repo.parent / 'logs' / 'loopback-patches.txt').write_text('\n'.join(changed), encoding='utf-8')
cfg = '''custom:
  device: cuda
  is_half: true
  version: v2Pro
  t2s_weights_path: GPT_SoVITS/pretrained_models/s1v3.ckpt
  vits_weights_path: GPT_SoVITS/pretrained_models/v2Pro/s2Gv2Pro.pth
  bert_base_path: GPT_SoVITS/pretrained_models/chinese-roberta-wwm-ext-large
  cnhuhbert_base_path: GPT_SoVITS/pretrained_models/chinese-hubert-base
'''
config = a.repo.parent / 'tts_local.yaml'
if not config.exists():
    config.write_text(cfg, encoding='utf-8')
print('Local API configuration ready. Model loading still requires a startup test.')
