Param(
    [Parameter(Position = 0)]
    [string]$OutputName = "portfolio_bootstrap_kit.zip"
)

$RootDir = (Resolve-Path (Join-Path $PSScriptRoot ".." )).Path
$DistDir = Join-Path $RootDir "dist"
$OutputPath = Join-Path $DistDir $OutputName

if (-not (Test-Path $DistDir)) {
    New-Item -ItemType Directory -Path $DistDir | Out-Null
}

Write-Host "Creating archive $OutputPath"
if (Test-Path $OutputPath) {
    Remove-Item $OutputPath
}

Add-Type -AssemblyName System.IO.Compression.FileSystem
$excludeSegments = @('node_modules', '__pycache__', '.terraform', 'dist', '.git')

$zip = [System.IO.Compression.ZipFile]::Open($OutputPath, [System.IO.Compression.ZipArchiveMode]::Create)
try {
    Get-ChildItem -LiteralPath $RootDir -Recurse -File -Force | Where-Object {
        $relative = [System.IO.Path]::GetRelativePath($RootDir, $_.FullName)
        $parts = $relative -split '[\\/]'
        -not ($parts | Where-Object { $excludeSegments -contains $_ })
    } | ForEach-Object {
        $relativePath = [System.IO.Path]::GetRelativePath($RootDir, $_.FullName)
        [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(
            $zip,
            $_.FullName,
            $relativePath,
            [System.IO.Compression.CompressionLevel]::Optimal
        ) | Out-Null
    }
}
finally {
    $zip.Dispose()
}

Write-Host "Archive created at $OutputPath"
