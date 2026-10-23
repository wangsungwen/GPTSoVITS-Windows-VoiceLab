param(
    [ValidateSet('CU126','CU128')][string]$Device = 'CU128',
    [ValidateSet('HF','HF-Mirror','ModelScope')][string]$Source = 'HF',
    [switch]$DownloadUVR5
)
. "$PSScriptRoot\common.ps1"
try {
    if (![Environment]::Is64BitOperatingSystem) { throw '64-bit Windows is required.' }
    if ($Kit -match '[^\x00-\x7F\s]' -or $Kit.Contains(' ')) { throw 'Extract to a short ASCII path without spaces, e.g. D:\VoiceLab.' }
    if (!(Get-Command nvidia-smi -ErrorAction SilentlyContinue)) { throw 'NVIDIA driver not found. Install the NVIDIA driver and restart Windows.' }
    Write-Host '[1/6] Checking NVIDIA driver.'
    & nvidia-smi
    if ($LASTEXITCODE -ne 0) { throw 'NVIDIA driver check failed.' }
    New-Item -ItemType Directory -Force -Path "$Kit\logs","$Kit\.runtime","$Kit\downloads" | Out-Null
    Start-Transcript -Path "$Kit\logs\install-$(Get-Date -Format yyyyMMdd-HHmmss).log"
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    $ProgressPreference = 'SilentlyContinue'
    if (!(Test-Path $Conda)) {
        # Release asset names and SHA256 were verified against the official release API
        # and its versioned checksum file. Do not construct a checksum URL from an alias.
        $release = '26.9.4-0'
        $asset = "Miniforge3-$release-Windows-x86_64.exe"
        $uri = "https://github.com/conda-forge/miniforge/releases/download/$release/$asset"
        $expected = '43638698f5ee811debae27b0dc3ab5c0300129bd400a847376c4bd2f6be15ceb'
        $exe = "$Kit\downloads\Miniforge3-Windows-x86_64.exe"
        $cachedOK = $false
        if (Test-Path -LiteralPath $exe) {
            $cachedOK = ((Get-FileHash -LiteralPath $exe -Algorithm SHA256).Hash -eq $expected)
        }
        if ($cachedOK) {
            Write-Host '[2/6] Reusing verified Miniforge installer from downloads.'
        } else {
            Write-Host "[2/6] Downloading Miniforge $release (about 145 MiB). Please wait."
            $partial = "$exe.partial"
            try {
                Invoke-WebRequest -UseBasicParsing -Uri $uri -OutFile $partial -TimeoutSec 1800
            } catch {
                throw "Miniforge download failed: $($_.Exception.Message)"
            }
            if ((Get-FileHash -LiteralPath $partial -Algorithm SHA256).Hash -ne $expected) {
                throw 'Miniforge SHA256 mismatch. Download was not installed; retry on a reliable connection.'
            }
            Move-Item -LiteralPath $partial -Destination $exe -Force
        }
        Write-Host '[2/6] SHA256 passed. Installing isolated Miniforge runtime.'
        $proc = Start-Process -FilePath $exe -ArgumentList @('/InstallationType=JustMe','/RegisterPython=0','/AddToPath=0','/S',"/D=$Forge") -Wait -PassThru
        if ($proc.ExitCode -ne 0) { throw "Miniforge installer failed: $($proc.ExitCode)" }
    }
    Write-Host '[3/6] Checking Windows entry-point launcher files and metadata.'
    # Installer-created base environments may have empty paths_data for conda-launchers.
    # Upstream workaround: force-reinstall the package with safety checks enabled.
    $env:CONDA_SAFETY_CHECKS = 'warn'
    $launcherProbe = @'
import hashlib, json, sys
from pathlib import Path
root = Path(sys.argv[1])
relative = 'share/conda-launchers/cli-64.exe'
launcher = root / relative
valid = False
for record in (root / 'conda-meta').glob('conda-launchers-*.json'):
    try:
        data = json.loads(record.read_text(encoding='utf-8'))
        entries = data.get('paths_data', {}).get('paths', [])
        for entry in entries:
            if entry.get('_path', '').replace('\\', '/') == relative:
                digest = entry.get('sha256')
                valid = (launcher.is_file() and bool(digest) and
                         hashlib.sha256(launcher.read_bytes()).hexdigest() == digest)
                if valid:
                    break
        if valid:
            break
    except (OSError, ValueError, TypeError):
        pass
print('Windows launcher metadata and SHA256: ' + ('PASS' if valid else 'REPAIR NEEDED'))
sys.exit(0 if valid else 1)
'@
    & "$Forge\python.exe" -c $launcherProbe $Forge
    if ($LASTEXITCODE -ne 0) {
        Write-Host '[3/6] Repairing conda-launchers in the isolated base environment.'
        Run-Conda -CommandArgs @('install','-y','-p',$Forge,'--override-channels','-c','conda-forge','--force-reinstall','conda-launchers')
        & "$Forge\python.exe" -c $launcherProbe $Forge
        if ($LASTEXITCODE -ne 0) { throw 'Windows launcher verification still failed after reinstall. See install log.' }
    }
    Write-Host '[3/6] Preparing Python environment.'
    if (Test-Path (Join-Path $EnvDir 'conda-meta\history')) {
        # Complete an existing transaction rather than skipping a partially populated prefix.
        Run-Conda -CommandArgs @('install','-y','-p',$EnvDir,'--override-channels','-c','conda-forge','python=3.10','pip','ffmpeg','cmake')
    } else {
        if (Test-Path -LiteralPath $EnvDir) {
            $backup = "$EnvDir.incomplete-$(Get-Date -Format yyyyMMdd-HHmmss)-$PID"
            Write-Host "[3/6] Preserving incomplete environment at $backup"
            Move-Item -LiteralPath $EnvDir -Destination $backup
        }
        Run-Conda -CommandArgs @('create','-y','-p',$EnvDir,'--override-channels','-c','conda-forge','python=3.10','pip','ffmpeg','cmake')
    }
    Set-Runtime
    Write-Host '[4/6] Preparing pinned GPT-SoVITS source.'
    $commit = 'b4570b876f5c086819ba84e3215472733c6a7b70'
    if (!(Test-Path (Join-Path $Repo 'install.ps1'))) {
        $zip = "$Kit\downloads\GPT-SoVITS-$commit.zip"
        Invoke-WebRequest -UseBasicParsing -Uri "https://github.com/RVC-Boss/GPT-SoVITS/archive/$commit.zip" -OutFile $zip
        $stage = "$Kit\downloads\source-$commit"
        New-Item -ItemType Directory -Force -Path $stage | Out-Null
        Expand-Archive -Path $zip -DestinationPath $stage -Force
        # The complete kit includes empty model/data directories. Merge source into
        # that skeleton; directory existence alone does not mean source is installed.
        if (Test-Path -LiteralPath $Repo) {
            Copy-Item -Path "$stage\GPT-SoVITS-$commit\*" -Destination $Repo -Recurse -Force
        } else {
            Move-Item -Path "$stage\GPT-SoVITS-$commit" -Destination $Repo
        }
        Set-Content -Path "$Repo\.kit-source-commit" -Value $commit -Encoding ASCII
    }
    if (!(Test-Path "$Repo\.kit-source-commit") -or (Get-Content "$Repo\.kit-source-commit" -Raw).Trim() -ne $commit) { throw 'Source version mismatch. Use a new kit folder rather than overwriting existing work.' }
    Push-Location $Repo
    try {
        # v1.3: use the documented Windows PyTorch 2.7.1 + CUDA 12.8 pair.
        # This checkout uses torchaudio.load and does not directly import torchcodec.
        # Pin dependencies so requirements.txt cannot silently switch audio backends.
        $constraints = "$Kit\pip-constraints.txt"
        @('torch==2.7.1','torchaudio==2.7.1','torchvision==0.22.1','gradio==4.44.1','fastapi==0.115.6','starlette==0.41.3','pydantic==2.10.6','jinja2==3.1.6','huggingface-hub==0.36.0') | Set-Content -Path $constraints -Encoding ASCII
        $env:PIP_CONSTRAINT = $constraints
        $officialInstaller = "$Repo\install.ps1"
        $officialText = [System.IO.File]::ReadAllText($officialInstaller)
        $before = 'Invoke-Pip torch torchcodec --index-url'
        $after = 'Invoke-Pip "torch==2.7.1" "torchaudio==2.7.1" --index-url'
        if ($officialText.Contains($before)) {
            $backup = "$officialInstaller.before-kit-v1.3"
            if (!(Test-Path -LiteralPath $backup)) { Copy-Item -LiteralPath $officialInstaller -Destination $backup }
            $officialText = $officialText.Replace($before, $after)
            [System.IO.File]::WriteAllText($officialInstaller, $officialText, (New-Object System.Text.UTF8Encoding($true)))
            Write-Host '[5/6] Applied Windows audio dependency fix; upstream installer backup preserved.'
        } elseif (!$officialText.Contains($after)) {
            throw 'Unexpected upstream PyTorch installation command. Stop rather than patch an unknown installer.'
        }
        Write-Host '[5/6] Installing torch 2.7.1 + torchaudio 2.7.1. CUDA build follows Device option.'
        Write-Host '[5/6] Installing official dependencies and models. This step downloads large files.'
        $installArgs = @('run','--no-capture-output','-p',$EnvDir,'powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',"$Repo\install.ps1",'-Device',$Device,'-Source',$Source)
        if ($DownloadUVR5) { $installArgs += '-DownloadUVR5' }
        Run-Conda -CommandArgs $installArgs
        Write-Host '[6/6] Configuring and checking CUDA, dependencies and model files.'
        # Match torchaudio to the torch build installed by the official installer.
        Run-Python -CommandArgs @("$PSScriptRoot\finish_install.py",'--repo',$Repo,'--device',$Device)
        Run-Python -CommandArgs @("$PSScriptRoot\doctor.py",'--repo',$Repo,'--require-cuda')
        Run-Python -CommandArgs @("$PSScriptRoot\webui_smoke.py")
        Run-Python -CommandArgs @('-m','pip','freeze') | Set-Content -Encoding UTF8 "$Kit\logs\installed-packages.txt"
    } finally { Pop-Location }
    Write-Host 'INSTALL CHECKS PASSED. Next: 03_Start_WebUI.cmd' -ForegroundColor Green
    Stop-Transcript
} catch {
    Write-Host $_.Exception.Message -ForegroundColor Red
    try { Stop-Transcript | Out-Null } catch {}
    exit 1
}
