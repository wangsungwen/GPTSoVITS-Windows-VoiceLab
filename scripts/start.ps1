param([ValidateSet('Doctor','WebUI','API','Batch','Video','Prepare')][string]$Task = 'WebUI')
. "$PSScriptRoot\common.ps1"
try {
    Set-Runtime
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
        'Video' { Run-Python -CommandArgs @("$PSScriptRoot\make_video.py",'--images',"$Kit\slides",'--audio',"$Kit\output_audio",'--output',"$Kit\ES0003_Presentation.mp4") }
        'Prepare' {
            $inputFile = Read-Host 'Input recording path (without surrounding quotes)'
            $start = Read-Host 'Start time in seconds'
            Run-Python -CommandArgs @("$PSScriptRoot\prepare_reference.py",$inputFile,'--start',$start,'--duration','7','--output',"$Kit\reference\reference.wav")
        }
    }
} catch { Write-Host $_ -ForegroundColor Red; exit 1 }
