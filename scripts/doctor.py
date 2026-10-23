import argparse
import importlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--repo', required=True, type=Path)
    p.add_argument('--require-cuda', action='store_true')
    a = p.parse_args()
    errors = []
    report = {'python': sys.version, 'repo': str(a.repo), 'imports': {}}
    for name in ['torch', 'torchaudio', 'gradio', 'transformers', 'librosa', 'fastapi', 'yaml', 'pyopenjtalk', 'g2p_en', 'opencc', 'pytorch_lightning']:
        try:
            mod = importlib.import_module(name)
            report['imports'][name] = getattr(mod, '__version__', 'OK')
        except Exception as exc:
            errors.append(f'{name}: {exc}')
    try:
        import torch
        report['cuda_available'] = torch.cuda.is_available()
        report['torch_cuda'] = torch.version.cuda
        if torch.cuda.is_available():
            report['gpu'] = torch.cuda.get_device_name(0)
            report['vram_gb'] = round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 2)
            # Actual CUDA operation catches incompatible driver / GPU architecture.
            report['cuda_test'] = (torch.ones((16,16), device='cuda') @ torch.ones((16,16), device='cuda')).sum().item()
        elif a.require_cuda:
            errors.append('CUDA unavailable: check driver and CUDA PyTorch build.')
    except Exception as exc:
        errors.append(f'CUDA test: {exc}')
    files = ['s1v3.ckpt', 'v2Pro/s2Gv2Pro.pth', 'v2Pro/s2Dv2Pro.pth',
             'chinese-hubert-base/config.json', 'chinese-roberta-wwm-ext-large/config.json']
    root = a.repo / 'GPT_SoVITS' / 'pretrained_models'
    for rel in files:
        if not (root / rel).is_file() or (root / rel).stat().st_size == 0:
            errors.append(f'Missing model file: {root / rel}')
    for name in ['chinese-hubert-base', 'chinese-roberta-wwm-ext-large']:
        if not any((root / name).glob('*.bin')) and not any((root / name).glob('*.safetensors')):
            errors.append(f'Missing model weights in {name}')
    if not (root / 'sv/pretrained_eres2netv2w24s4ep4.ckpt').is_file():
        errors.append('Missing sv/pretrained_eres2netv2w24s4ep4.ckpt.')
    if not (a.repo / 'GPT_SoVITS/text/G2PWModel').exists():
        errors.append('Missing G2PWModel.')
    report['ffmpeg'] = shutil.which('ffmpeg')
    if not report['ffmpeg']:
        errors.append('FFmpeg not found.')
    else:
        subprocess.run(['ffmpeg', '-version'], check=True, stdout=subprocess.DEVNULL)
    report['errors'] = errors
    log = a.repo.parent / 'logs'
    log.mkdir(exist_ok=True)
    (log / 'doctor.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print('PASS: dependencies, CUDA and required files. Next test: start WebUI/API and synthesize real audio.' if not errors else 'FAIL: see errors above.')
    return bool(errors)

if __name__ == '__main__':
    sys.exit(main())
