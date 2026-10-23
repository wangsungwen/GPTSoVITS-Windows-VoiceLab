"""Run pip or Conda with logs, merging stderr before PowerShell can intercept it.

Called by patched Invoke-Pip, or Invoke-Conda with --voicelab-conda.
"""
import datetime
import os
from pathlib import Path
import subprocess
import sys


def main():
    log_dir = Path(os.environ['VOICELAB_INSTALL_LOG_DIR'])
    log_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    args = sys.argv[1:]
    is_conda = bool(args and args[0] == '--voicelab-conda')
    label = 'conda' if is_conda else 'pip'
    stem = log_dir / f'{label}-{stamp}-{os.getpid()}'
    detail_log = str(stem) + '.log'
    console_log = str(stem) + '-console.log'
    print(f'{label} console log: {console_log}', flush=True)
    if is_conda:
        executable = Path(os.environ['VOICELAB_CONDA_EXE'])
        if not executable.is_file():
            raise FileNotFoundError(f'Conda executable missing: {executable}')
        command = [str(executable), 'install', '-y', '-q', '-c', 'conda-forge', *args[1:]]
    else:
        print(f'pip detailed log: {detail_log}', flush=True)
        command = [sys.executable, '-m', 'pip', '--log', detail_log, 'install', *args]
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONUNBUFFERED'] = '1'
    with open(console_log, 'w', encoding='utf-8') as log:
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              text=True, encoding='utf-8', errors='replace', env=env,
                              bufsize=1) as proc:
            for line in proc.stdout:
                log.write(line)
                log.flush()
                # Emit only stdout; PS 5.1 must not stop on a stderr ErrorRecord
                # before the upstream function can read pip's actual exit code.
                print(line, end='', flush=True)
            code = proc.wait()
    print(f'{label} exit code: {code}', flush=True)
    print(f'{label} console log: {console_log}', flush=True)
    return code


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:
        print(f'VoiceLab installer runner failed: {exc}', flush=True)
        sys.exit(1)
