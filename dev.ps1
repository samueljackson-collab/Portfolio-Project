Write-Host "`n>>> Bootstrapping development environment"
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker is required to run the dev environment."
    exit 1
}

docker compose up --build
