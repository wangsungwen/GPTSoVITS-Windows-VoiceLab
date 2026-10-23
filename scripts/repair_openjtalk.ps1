. "$PSScriptRoot\common.ps1"
try {
    Set-Runtime
    New-Item -ItemType Directory -Force -Path (Join-Path $Kit 'logs') | Out-Null
    $env:PIP_CONSTRAINT = Join-Path $Kit 'pip-constraints.txt'
    if (!(Test-Path -LiteralPath $env:PIP_CONSTRAINT)) {
        throw 'Run 01_Install.cmd first so the environment and constraints exist.'
    }
    Write-Host 'Opt-in repair: pyopenjtalk-plus replaces the unbuilt original pyopenjtalk.'
    Write-Host 'The fork bundles a different Japanese dictionary. Existing models are unchanged.'
    Run-Python -CommandArgs @("$PSScriptRoot\openjtalk_plus.py",'apply','--repo',$Repo)
    $log = Join-Path $Kit "logs\openjtalk-plus-$(Get-Date -Format yyyyMMdd-HHmmss).log"
    Run-Python -CommandArgs @('-m','pip','--log',$log,'install','--only-binary=:all:',
        'pyopenjtalk-plus==0.4.1.post10','numpy==1.26.4')
    Run-Python -CommandArgs @("$PSScriptRoot\openjtalk_plus.py",'check')
    Write-Host 'OPENJTALK REPAIR CHECKS PASSED. Next: 01_Install.cmd to finish all dependencies.' -ForegroundColor Green
    Write-Host "Pip log: $log"
} catch {
    Write-Host $_.Exception.Message -ForegroundColor Red
    if ($log) { Write-Host "Pip log: $log" }
    exit 1
}
