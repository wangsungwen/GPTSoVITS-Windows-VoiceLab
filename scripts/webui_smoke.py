"""Check local-only imports and Gradio template/schema endpoints without loading TTS models."""
import importlib
import json
import site
import sys
from pathlib import Path

import gradio as gr
from fastapi import FastAPI
from starlette.testclient import TestClient


def main():
    root = Path(sys.prefix).resolve()
    report = {'python': sys.executable, 'user_site_enabled': site.ENABLE_USER_SITE, 'packages': {}}
    for name in ['gradio', 'gradio_client', 'fastapi', 'starlette', 'pydantic', 'jinja2', 'huggingface_hub']:
        module = importlib.import_module(name)
        path = Path(module.__file__).resolve()
        report['packages'][name] = {'version': getattr(module, '__version__', 'unknown'), 'path': str(path)}
        if not path.is_relative_to(root):
            raise RuntimeError(f'{name} came from outside the environment: {path}')
    if site.ENABLE_USER_SITE:
        raise RuntimeError('User-site imports are still enabled.')
    with gr.Blocks(analytics_enabled=False) as blocks:
        gr.Markdown('VoiceLab WebUI compatibility test')
        audio = gr.Audio(type='filepath', label='Reference audio')
        text = gr.Textbox(label='Text')
        gr.Button('Test').click(lambda value: value, inputs=text, outputs=text)
    app = gr.mount_gradio_app(FastAPI(), blocks, path='/test')
    with TestClient(app) as client:
        for endpoint in ['/test/', '/test/config', '/test/info']:
            response = client.get(endpoint)
            if response.status_code != 200:
                raise RuntimeError(f'{endpoint}: HTTP {response.status_code}: {response.text[:500]}')
            report[endpoint] = response.status_code
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print('PASS: Gradio HTML, configuration and API schema. Next: start the actual GPT-SoVITS WebUI.')


if __name__ == '__main__':
    main()
