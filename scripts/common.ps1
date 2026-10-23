$ErrorActionPreference = 'Stop'
# Keep all installer, WebUI and API subprocesses out of the per-user Python site.
$env:PYTHONNOUSERSITE = '1'
$env:PYTHONPATH = ''
$Kit = Split-Path $PSScriptRoot -Parent
$Forge = Join-Path $Kit '.runtime\miniforge'
$Conda = Join-Path $Forge 'Scripts\conda.exe'
$EnvDir = Join-Path $Kit '.runtime\gptsovits'
$Repo = Join-Path $Kit 'GPT-SoVITS'
function Run-Conda {
    param([string[]]$CommandArgs)
    & $Conda @CommandArgs
    if ($LASTEXITCODE -ne 0) { throw "Conda command failed: $LASTEXITCODE" }
}
function Run-Python {
    param([string[]]$CommandArgs)
    Run-Conda -CommandArgs (@('run','--no-capture-output','-p',$EnvDir,'python') + $CommandArgs)
}
function Set-Runtime {
    if (!(Test-Path (Join-Path $EnvDir 'python.exe'))) { throw 'Run 01_Install.cmd first.' }
    $env:PATH = "$Forge\condabin;$Forge\Scripts;$EnvDir;$EnvDir\Library\bin;$EnvDir\Scripts;$env:PATH"
    $env:language = 'zh_TW'
    $env:is_share = 'False'
    $env:version = 'v2Pro'
}
