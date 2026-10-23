# This entry point runs even when Python is not installed.
param(
    [string]$PythonPath,
    [string]$RuntimePython,
    [string]$VenvPath,
    [switch]$CheckOnly
)
$ErrorActionPreference = 'Stop'
$probe = 'import sys; assert sys.version_info >= (3,10), "Python 3.10+ required"; import venv, ensurepip; print(sys.executable)'
$candidates = @()
if ($PythonPath) {
    $candidates += @{Exe=$PythonPath; Prefix=@()}
} else {
    $stateRoot = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path ([Environment]::GetFolderPath('UserProfile')) '.codex' }
    $environmentRoot = if ($VenvPath) { $VenvPath } else { Join-Path $stateRoot 'skill-state/article-skill/.venv' }
    $existing = Join-Path $environmentRoot 'Scripts/python.exe'
    if (Test-Path -LiteralPath $existing) { $candidates += @{Exe=$existing; Prefix=@()} }
    if ($RuntimePython) { $candidates += @{Exe=$RuntimePython; Prefix=@()} }
    foreach ($name in @('py','python3','python')) {
        $command = Get-Command $name -CommandType Application -ErrorAction SilentlyContinue
        if ($command) {
            $prefix = if ($name -eq 'py') { @('-3') } else { @() }
            $candidates += @{Exe=$command.Source; Prefix=$prefix}
        }
    }
}
foreach ($candidate in $candidates) {
    $exe = $candidate.Exe
    # Avoid Windows Store app-execution placeholders, which can open a GUI.
    if ($exe -match '\\Microsoft\\WindowsApps\\(?:python|python3)\.exe$') {
        [Console]::Error.WriteLine("Skipped Store execution alias: $exe")
        continue
    }
    try {
        if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) {
            [Console]::Error.WriteLine("Path unavailable (missing or inaccessible in this execution context): $exe")
            continue
        }
        $probeArgs = @($candidate.Prefix) + @('-')
        $ErrorActionPreference = 'Continue'
        $resolved = $probe | & $exe @probeArgs 2>&1
        $probeExit = $LASTEXITCODE
        $ErrorActionPreference = 'Stop'
        if ($probeExit -ne 0) {
            [Console]::Error.WriteLine("Interpreter probe failed ($exe), exit ${probeExit}: $resolved")
            continue
        }
        if (-not $resolved) {
            [Console]::Error.WriteLine("Interpreter returned no discovery output: $exe")
            continue
        }
        $resolved = ($resolved | Select-Object -Last 1).ToString().Trim()
        if (-not (Test-Path -LiteralPath $resolved -PathType Leaf)) { continue }
    } catch {
        $ErrorActionPreference = 'Stop'
        [Console]::Error.WriteLine("Cannot access or launch ${exe}: $($_.Exception.Message)")
        continue
    }
    if ($CheckOnly) {
        @{status='python_ready'; python=$resolved; note='Discovery only; packages, fonts and renderer not checked.'} | ConvertTo-Json -Compress
        exit 0
    }
    $setupArgs = @((Join-Path $PSScriptRoot 'setup_environment.py'))
    if ($VenvPath) { $setupArgs += @('--venv',$VenvPath) }
    & $resolved @setupArgs
    exit $LASTEXITCODE
}
[Console]::Error.WriteLine('No usable Python 3.10+ with venv and ensurepip was found. No packages were installed.')
[Console]::Error.WriteLine('This does NOT prove Python is uninstalled. Check the diagnostics and filesystem/sandbox access. In Codex, discover the runtime with load_workspace_dependencies and pass -RuntimePython <returned-path>; do not guess a cache path. Only if no compatible accessible runtime is available, install supported Python from https://www.python.org/downloads/ and rerun.')
exit 2
