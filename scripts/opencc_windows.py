"""Use the official OpenCC wheel instead of forced source builds on Windows."""
import argparse
from pathlib import Path
import re


def apply(repo):
    path = repo / 'requirements.txt'
    original = path.read_text(encoding='utf-8-sig')
    text, count = re.subn(r'(?m)^--no-binary\s*=\s*opencc[ \t]*\r?$',
                          '--only-binary=opencc', original)
    if count > 1:
        raise RuntimeError('Unexpected duplicate OpenCC binary directives; no changes made.')
    if count == 0 and '--only-binary=opencc' not in text:
        raise RuntimeError('Unknown OpenCC binary policy; no changes made.')
    text, specs = re.subn(r'(?m)^opencc[ \t]*\r?$', 'opencc==1.4.2', text)
    if specs > 1 or (specs == 0 and not re.search(r'(?m)^opencc==1\.4\.2[ \t]*\r?$', text)):
        raise RuntimeError('Unknown OpenCC requirement; no changes made.')
    if original != text:
        backup = path.with_name(path.name + '.before-opencc-wheel')
        if not backup.exists():
            backup.write_bytes(path.read_bytes())
        path.write_text(text, encoding='utf-8-sig')
    print('OpenCC configured: official opencc==1.4.2 wheel; source-build directive removed.')


def check():
    import opencc
    for config, source, expected in [('s2tw', '\u6c49\u5b57', '\u6f22\u5b57'),
                                     ('t2s', '\u6f22\u5b57', '\u6c49\u5b57')]:
        result = opencc.OpenCC(config).convert(source)
        if result != expected:
            raise RuntimeError(f'OpenCC conversion check failed: {config}')
    print('PASS: official OpenCC import, s2tw and t2s conversion.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['apply', 'check'])
    parser.add_argument('--repo', type=Path)
    args = parser.parse_args()
    if args.mode == 'apply':
        if args.repo is None:
            parser.error('--repo required for apply')
        apply(args.repo)
    else:
        check()
