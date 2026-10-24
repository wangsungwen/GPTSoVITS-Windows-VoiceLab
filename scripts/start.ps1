param([ValidateSet('Doctor','WebUI','API','Batch','Video','Prepare')][string]$Task = 'WebUI')
. "$PSScriptRoot\common.ps1"
try {
    Set-Runtime
    if ($Task -in @('WebUI','API','Batch')) {
        & "$EnvDir\python.exe" -c "import resampy; resampy.filters.get_filter('kaiser_best')"
        if ($LASTEXITCODE -ne 0) {
            Write-Host 'Runtime dependency check failed. Close running TTS processes, then run:' -ForegroundColor Yellow
            Write-Host ('& "' + $EnvDir + '\python.exe" -m pip install "resampy==0.4.3" "numpy<2.0"')
            throw 'resampy import/filter check failed; repair the runtime and restart.'
        }
    }
    switch ($Task) {
        'Doctor' { Run-Python -CommandArgs @("$PSScriptRoot\doctor.py",'--repo',$Repo,'--require-cuda') }
        'WebUI' {
            Set-Location $Repo
            Run-Python -CommandArgs @('webui.py')
        }
        'API' {
            Set-Location $Repo
            Run-Python -CommandArgs @('api_v2.py','-a','127.0.0.1','-p','9880','-c',"$Kit\tts_local.yaml")
        }
        'Batch' { Run-Python -CommandArgs @("$PSScriptRoot\batch_tts.py",'--manifest',"$Kit\slides.csv",'--reference',"$Kit\reference\reference.wav",'--prompt',"$Kit\reference\reference.txt",'--prompt-lang','en','--out',"$Kit\output_audio") }
        'Video' {
            $videoOutput = Join-Path $Kit 'ES0003_Presentation.mp4'
            if (Test-Path -LiteralPath $videoOutput) {
                $videoOutput = Join-Path $Kit ('ES0003_Presentation_' + (Get-Date -Format 'yyyyMMdd_HHmmss') + '_' + [guid]::NewGuid().ToString('N').Substring(0,8) + '.mp4')
                Write-Host "Existing video preserved. New output: $videoOutput"
            }
            Run-Python -CommandArgs @("$PSScriptRoot\make_video.py",'--images',"$Kit\slides",'--audio',"$Kit\output_audio",'--output',$videoOutput)
        }
        'Prepare' {
            $inputFile = Read-Host 'Input recording path (without surrounding quotes)'
            $start = Read-Host 'Start time in seconds'
            Run-Python -CommandArgs @("$PSScriptRoot\prepare_reference.py",$inputFile,'--start',$start,'--duration','7','--output',"$Kit\reference\reference.wav")
        }
    }
} catch { Write-Host $_ -ForegroundColor Red; exit 1 }
