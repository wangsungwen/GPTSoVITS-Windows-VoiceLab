"""Opt-in prebuilt OpenJTalk fork for environments where upstream cannot build."""
import argparse
import importlib.metadata
from pathlib import Path
import re

SPEC = 'pyopenjtalk-plus==0.4.1.post10'
MARKER = '# VoiceLab OpenJTalk Plus bundled dictionary'


def apply(repo):
    try:
        version = importlib.metadata.version('pyopenjtalk')
    except importlib.metadata.PackageNotFoundError:
        pass
    else:
        raise RuntimeError(f'Original pyopenjtalk {version} is already installed. '
                           'This repair is for a failed fresh install; do not mix both providers.')
    req = repo / 'requirements.txt'
    installer = repo / 'install.ps1'
    r = req.read_text(encoding='utf-8-sig')
    s = installer.read_text(encoding='utf-8-sig')
    old = r'(?m)^pyopenjtalk>=0\.4\.1\s*$'
    if SPEC not in r:
        r, count = re.subn(old, '--only-binary=pyopenjtalk-plus\n' + SPEC, r)
        if count != 1:
            raise RuntimeError('Unexpected pyopenjtalk requirement; no files were changed.')
    if MARKER not in s:
        pattern = r'Write-Info "Downloading Open JTalk Dict\.\.\.".*?Write-Success "Open JTalk Dic Downloaded"'
        s, count = re.subn(pattern, MARKER + '\nWrite-Info "Using pyopenjtalk-plus bundled dictionary."', s, flags=re.S)
        if count != 1:
            raise RuntimeError('Unexpected upstream dictionary block; no files were changed.')
    for path, text in [(req, r), (installer, s)]:
        original = path.read_text(encoding='utf-8-sig')
        if original != text:
            backup = path.with_name(path.name + '.before-openjtalk-plus')
            if not backup.exists():
                backup.write_bytes(path.read_bytes())
            path.write_text(text, encoding='utf-8-sig')
    print('Opt-in OpenJTalk Plus requirements and bundled dictionary configured; backups preserved.')


def check():
    import pyopenjtalk
    version = importlib.metadata.version('pyopenjtalk-plus')
    if version != '0.4.1.post10':
        raise RuntimeError(f'Unexpected pyopenjtalk-plus version: {version}')
    for name in ['g2p', 'run_frontend', 'make_label', 'mecab_dict_index',
                 'update_global_jtalk_with_user_dict']:
        if not callable(getattr(pyopenjtalk, name, None)):
            raise RuntimeError(f'Missing required API: {name}')
    dictionary = pyopenjtalk.OPEN_JTALK_DICT_DIR
    if isinstance(dictionary, bytes):
        dictionary = dictionary.decode('utf-8')
    if not Path(dictionary).is_dir():
        raise RuntimeError(f'Bundled dictionary missing: {dictionary}')
    phonemes = pyopenjtalk.g2p('\u3053\u3093\u306b\u3061\u306f\u3002')
    labels = pyopenjtalk.make_label(pyopenjtalk.run_frontend('\u3053\u3093\u306b\u3061\u306f\u3002'))
    if not phonemes or not labels:
        raise RuntimeError('OpenJTalk frontend returned empty output.')
    print(f'PASS: pyopenjtalk-plus {version}; required API, dictionary and text frontend.')
    print(f'Phonemes: {phonemes}')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=['apply', 'check'])
    p.add_argument('--repo', type=Path)
    a = p.parse_args()
    if a.mode == 'apply':
        if a.repo is None:
            p.error('--repo required for apply')
        apply(a.repo)
    else:
        check()
