. "$PSScriptRoot\common.ps1"
try {
    Set-Runtime
    $constraints = Join-Path $Kit 'pip-constraints.txt'
    if (Test-Path -LiteralPath $constraints) {
        Copy-Item -LiteralPath $constraints -Destination "$constraints.before-webui-$(Get-Date -Format yyyyMMdd-HHmmss)"
    }
    @('torch==2.7.1','torchaudio==2.7.1','torchvision==0.22.1',
      'gradio==4.44.1','fastapi==0.115.6','starlette==0.41.3',
      'pydantic==2.10.6','jinja2==3.1.6','huggingface-hub==0.36.0') |
        Set-Content -Path $constraints -Encoding ASCII
    $env:PIP_CONSTRAINT = $constraints
    $log = Join-Path $Kit "logs\webui-repair-$(Get-Date -Format yyyyMMdd-HHmmss).log"
    New-Item -ItemType Directory -Force -Path (Join-Path $Kit 'logs') | Out-Null
    Push-Location $Repo
    try {
        Write-Host 'Repairing WebUI dependencies in the isolated environment. Models are unchanged.'
        # Invoke pip directly, outside the upstream stderr-capturing PowerShell helper.
        Run-Python -CommandArgs @('-m','pip','--log',$log,'install','-r','requirements.txt',
            'gradio==4.44.1','fastapi==0.115.6','starlette==0.41.3',
            'pydantic==2.10.6','jinja2==3.1.6','huggingface-hub==0.36.0')
        Run-Python -CommandArgs @("$PSScriptRoot\webui_smoke.py")
    } finally { Pop-Location }
    Write-Host 'WEBUI REPAIR CHECKS PASSED. Start 03_Start_WebUI.cmd.' -ForegroundColor Green
    Write-Host "Pip log: $log"
} catch {
    Write-Host $_.Exception.Message -ForegroundColor Red
    if ($log) { Write-Host "Pip log: $log" }
    exit 1
}
