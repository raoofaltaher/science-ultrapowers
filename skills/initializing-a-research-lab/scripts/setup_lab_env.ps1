# Completes the lab set-up on this machine for the adopted figure and poster skills and for Jev:
#   1. a Python environment, .venv-lab-skills in the project root, with the packages the bundled scripts need;
#   2. Tesseract OCR, which figure-qa uses for its raster text checks;
#   3. the Jev key, TYPESAFE_API_KEY, from hidden input.
# Run it with:
#   pwsh -File "<plugin>/skills/initializing-a-research-lab/scripts/setup_lab_env.ps1" -ProjectRoot <project> [-DryRun] [-SetUserEnv]
# -ProjectRoot defaults to the Git repository you are in, else the current directory.
# -DryRun previews: it changes nothing, starts no installer and asks nothing, and prints what each step would do.
# -SetUserEnv lets the script set TESSDATA_PREFIX, your Path entry and TYPESAFE_API_KEY for your Windows account.
# Every change outside the project folder asks first, each behind its own yes.
# The key is read as hidden input, never printed, never written to a file and never taken as a parameter.
param([string]$ProjectRoot, [switch]$DryRun, [switch]$SetUserEnv, [switch]$SkipTesseract)
$ErrorActionPreference = 'Stop'
$onWindows = if ($null -ne $IsWindows) { [bool]$IsWindows } else { $true }

if (-not $ProjectRoot) {
  $ProjectRoot = $null
  if (Get-Command git -ErrorAction SilentlyContinue) {
    # Windows PowerShell 5.1 turns a native command's stderr into a terminating error under 'Stop',
    # and a folder that is not a repository makes git write there: let the call fail quietly.
    $top = $null
    $savedPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try { $top = & git rev-parse --show-toplevel 2>$null } catch { $top = $null }
    $gitExit = $LASTEXITCODE
    $ErrorActionPreference = $savedPreference
    if ($gitExit -eq 0 -and $top) { $ProjectRoot = "$top".Trim() }
  }
  if (-not $ProjectRoot) { $ProjectRoot = (Get-Location).ProviderPath }
}
if (-not (Test-Path -LiteralPath $ProjectRoot -PathType Container)) { throw "ProjectRoot does not exist: $ProjectRoot" }
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).ProviderPath
# .FullName expands an 8.3 short path (e.g. C:\Users\<name>~1), which some tools cannot resolve
$ProjectRoot = (Get-Item -LiteralPath $ProjectRoot).FullName

$venv = Join-Path $ProjectRoot '.venv-lab-skills'
$vpy  = if ($onWindows) { Join-Path (Join-Path $venv 'Scripts') 'python.exe' } else { Join-Path (Join-Path $venv 'bin') 'python' }
function Confirm-Step([string]$q) { return ((Read-Host "$q [y/N]") -match '^(y|yes)$') }

# The two environment lines the dry run and the manual steps share
if ($onWindows) {
  $tessLine = 'TESSDATA_PREFIX: set for your Windows user only with -SetUserEnv and a separate yes'
  $keyLine  = 'TYPESAFE_API_KEY: set for your Windows user only with -SetUserEnv and a separate yes (hidden input, never written to a file)'
} else {
  $tessLine = 'TESSDATA_PREFIX: set it in your shell profile (user environment variables exist only on Windows, where -SetUserEnv sets them after a separate yes)'
  $keyLine  = 'TYPESAFE_API_KEY: set it in your shell profile (user environment variables exist only on Windows, where -SetUserEnv sets them after a separate yes) (hidden input, never written to a file)'
}
function Assert-Native([string]$what) { if ($LASTEXITCODE -ne 0) { throw "$what failed with exit code $LASTEXITCODE" } }
$wingetArgs = @('install', '-e', '--id', 'tesseract-ocr.tesseract', '--accept-package-agreements')
$wingetAlt  = @('install', '-e', '--id', 'UB-Mannheim.TesseractOCR', '--accept-package-agreements')
$std = 'C:/Program Files/Tesseract-OCR/tesseract.exe'

# 1) Python environment for the bundled scripts (exact pins required by pptx-posters)
# Pins checked against PyPI on 2026-11-08 (python -m pip index versions <name>); re-check them when the plugin updates.
$pkgs = @('python-pptx==1.0.2', 'Pillow==12.3.0', 'lxml==6.1.1', 'jsonschema==4.26.0', 'shapely==2.2.0', 'svgelements==1.9.6',
          'drawsvg==2.4.2', 'fonttools==4.68.0', 'svgpathtools==1.8.0', 'pytesseract==0.3.13', 'pytest==9.2.0',
          'pyyaml==6.0.3', 'numpy==2.5.4', 'matplotlib==3.11.2')
$haveUv = [bool](Get-Command uv -ErrorAction SilentlyContinue)
$havePython = [bool](Get-Command python -ErrorAction SilentlyContinue)
if ($DryRun) {
  if (Test-Path -LiteralPath $venv) { Write-Host "exists $venv" } else { Write-Host "would create $venv" }
  if ($haveUv) { $tool = 'uv pip install' } elseif ($havePython) { $tool = 'python -m venv, then pip install' } else { $tool = 'none available: neither uv nor python is on PATH' }
  Write-Host ("would install: " + ($pkgs -join ' ') + " (with $tool)")
} else {
  if ($haveUv) {
    # The pinned packages were tested on Python 3.13; the plugin's own scripts need only Python 3.11+.
    if (-not (Test-Path -LiteralPath $vpy)) { & uv venv --python 3.13 $venv; Assert-Native 'uv venv' }
    & uv pip install --python $vpy @pkgs; Assert-Native 'uv pip install'
  } elseif ($havePython) {
    if (-not (Test-Path -LiteralPath $vpy)) { & python -m venv $venv; Assert-Native 'python -m venv' }
    & $vpy -m pip install @pkgs; Assert-Native 'pip install'
  } else { throw 'Neither uv nor python is on PATH; install uv and re-run.' }
  Write-Host "Python environment ready: $vpy (cairosvg is optional: PNG export in svg-primitives needs the native Cairo library)"
}

# 2) Tesseract OCR for figure-qa's raster text checks
$tessExe = $null
if ($SkipTesseract) {
  Write-Host 'Tesseract: skipped (-SkipTesseract).'
} else {
  $found = Get-Command tesseract -ErrorAction SilentlyContinue
  if ($found) { $tessExe = $found.Source } elseif (Test-Path -LiteralPath $std) { $tessExe = $std }
  $haveWinget = [bool](Get-Command winget -ErrorAction SilentlyContinue)
  if ($DryRun) {
    if ($tessExe) { Write-Host "Tesseract found: $tessExe" }
    else {
      Write-Host 'Tesseract not found.'
      if ($haveWinget) { Write-Host ('would offer: winget ' + ($wingetArgs -join ' ')) }
      else { Write-Host 'would offer: nothing (winget is not available); install Tesseract with your package manager' }
    }
  } else {
    if (-not $tessExe -and $haveWinget -and (Confirm-Step 'Tesseract OCR not found. Install it with winget?')) {
      & winget @wingetArgs
      if ($LASTEXITCODE -ne 0) { & winget @wingetAlt }
      if (Test-Path -LiteralPath $std) { $tessExe = $std }
    }
    if ($tessExe) { Write-Host "Tesseract found: $tessExe" }
    else { Write-Host 'Tesseract not configured: figure-qa reports OCR as skipped (information only).' }
  }
}

# 3) Environment variables for your Windows user: only with -SetUserEnv, each behind its own yes
if ($DryRun -or -not $SetUserEnv) {
  Write-Host $tessLine
  Write-Host $keyLine
  if (-not $DryRun) {
    if ($tessExe) { Write-Host ("Manual step: set TESSDATA_PREFIX to " + (Join-Path (Split-Path -Parent $tessExe) 'tessdata') + " and add " + (Split-Path -Parent $tessExe) + " to your Path.") }
    Write-Host 'Manual step: set TYPESAFE_API_KEY in your user environment variables, or re-run with -SetUserEnv.'
  }
} elseif (-not $onWindows) {
  Write-Host 'User environment variables exist only on Windows. Put TESSDATA_PREFIX and TYPESAFE_API_KEY in your shell profile instead; nothing was set.'
} else {
  if ($tessExe) {
    $tdir = Split-Path -Parent $tessExe; $tdata = Join-Path $tdir 'tessdata'
    if ((Test-Path -LiteralPath $tdata) -and (Confirm-Step "Set TESSDATA_PREFIX=$tdata for your Windows user?")) {
      [Environment]::SetEnvironmentVariable('TESSDATA_PREFIX', $tdata, 'User'); $env:TESSDATA_PREFIX = $tdata
    }
    $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    if (-not ($userPath -split ';' | Where-Object { $_ -eq $tdir }) -and (Confirm-Step "Add $tdir to your user PATH?")) {
      [Environment]::SetEnvironmentVariable('Path', ($userPath.TrimEnd(';') + ';' + $tdir), 'User')
      $env:Path = $env:Path + ';' + $tdir
    }
  }
  # Jev key for Claude Code (value is never displayed or stored in a file)
  if ([Environment]::GetEnvironmentVariable('TYPESAFE_API_KEY', 'User')) { Write-Host 'TYPESAFE_API_KEY is already set for your user (value not shown).' }
  elseif (Confirm-Step 'Set TYPESAFE_API_KEY for your Windows user now? Input is hidden') {
    $sec = Read-Host 'Paste the key' -AsSecureString
    $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec)
    try { $plain = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr) } finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr) }
    if ($plain) { [Environment]::SetEnvironmentVariable('TYPESAFE_API_KEY', $plain, 'User'); Write-Host 'Set. Restart Claude Code to pick it up.' }
    Remove-Variable plain -ErrorAction SilentlyContinue
  }
}

if ($DryRun) { Write-Host 'Preview: nothing was changed. Run the script again without -DryRun to complete the lab set-up.' }
else { Write-Host 'Done: the lab set-up on this machine is complete. Restart Claude Code so new user environment variables take effect.' }
