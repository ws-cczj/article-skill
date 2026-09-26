param(
    [string]$Message = '',
    [string]$Proxy = $env:ARTICLE_SKILL_GIT_PROXY
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$exitCode = 0

function Invoke-RepoGit {
    param([string[]]$Arguments)
    & git -C $repoRoot @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "git $($Arguments[0]) failed (exit $LASTEXITCODE). No force push or automatic reset was attempted."
    }
}

try {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        throw 'Git was not found. Install Git and sign in to your remote before retrying.'
    }
    $gitRoot = Invoke-RepoGit -Arguments @('rev-parse', '--show-toplevel')
    if ([IO.Path]::GetFullPath($gitRoot) -ne [IO.Path]::GetFullPath($repoRoot)) {
        throw 'This script must be inside the root of its own Git repository.'
    }
    $branch = Invoke-RepoGit -Arguments @('symbolic-ref', '--quiet', '--short', 'HEAD')
    $remote = Invoke-RepoGit -Arguments @('remote', 'get-url', '--push', 'origin')
    foreach ($marker in @('MERGE_HEAD', 'CHERRY_PICK_HEAD', 'REVERT_HEAD', 'rebase-merge', 'rebase-apply')) {
        $markerPath = Invoke-RepoGit -Arguments @('rev-parse', '--git-path', $marker)
        if (-not [IO.Path]::IsPathRooted($markerPath)) { $markerPath = Join-Path $repoRoot $markerPath }
        if (Test-Path -LiteralPath $markerPath) {
            throw "Finish the in-progress Git operation first ($marker)."
        }
    }
    Write-Host "Repository: $repoRoot"
    Write-Host "Pushing current branch: $branch -> origin/$branch"
    Invoke-RepoGit -Arguments @('status', '--short')
    Invoke-RepoGit -Arguments @('add', '--all')
    & git -C $repoRoot diff --cached --quiet
    $diffExit = $LASTEXITCODE
    if ($diffExit -eq 1) {
        if ([string]::IsNullOrWhiteSpace($Message)) {
            $Message = 'Update article-skill ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
        }
        Invoke-RepoGit -Arguments @('commit', '-m', $Message)
    } elseif ($diffExit -ne 0) {
        throw "Could not inspect staged changes (exit $diffExit)."
    } else {
        Write-Host 'No new changes to commit; pushing any existing local commits.'
    }
    $pushArgs = @()
    if (-not [string]::IsNullOrWhiteSpace($Proxy)) { $pushArgs += @('-c', "http.proxy=$Proxy") }
    $pushArgs += @('push', '--set-upstream', 'origin', "HEAD:refs/heads/$branch")
    Invoke-RepoGit -Arguments $pushArgs
    Write-Host 'Push completed successfully.' -ForegroundColor Green
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host 'Local files and commits are retained. Resolve the reported problem, then retry.'
    Write-Host 'For a proxy, set ARTICLE_SKILL_GIT_PROXY or use scripts/push.ps1 -Proxy <URL>.'
    $exitCode = 1
}
exit $exitCode
