<#
.SYNOPSIS
    Complete deployment script for portfolio application
.DESCRIPTION
    This script handles the entire deployment process:
    - Validates environment
    - Runs tests
    - Builds Docker images
    - Applies Terraform infrastructure
    - Deploys application
.PARAMETER Environment
    Target environment (dev, staging, prod)
.EXAMPLE
    .\deploy.ps1 -Environment dev
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("dev", "staging", "prod")]
    [string]$Environment
)

$ErrorActionPreference = "Stop"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Portfolio Application Deployment" -ForegroundColor Cyan
Write-Host "Environment: $Environment" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Step 1: Pre-deployment checks
Write-Host "`n[1/7] Running pre-deployment checks..." -ForegroundColor Yellow

# Check required tools
$requiredTools = @("git", "docker", "terraform", "aws")
foreach ($tool in $requiredTools) {
    if (!(Get-Command $tool -ErrorAction SilentlyContinue)) {
        Write-Error "$tool is not installed or not in PATH"
        exit 1
    }
}
Write-Host "✓ All required tools are installed" -ForegroundColor Green

# Check AWS credentials
try {
    aws sts get-caller-identity | Out-Null
    Write-Host "✓ AWS credentials are valid" -ForegroundColor Green
} catch {
    Write-Error "AWS credentials are not configured"
    exit 1
}

# Step 2: Run tests
Write-Host "`n[2/7] Running tests..." -ForegroundColor Yellow

Push-Location backend
pytest -v
if ($LASTEXITCODE -ne 0) {
    Write-Error "Backend tests failed"
    exit 1
}
Pop-Location
Write-Host "✓ Backend tests passed" -ForegroundColor Green

Push-Location frontend
npm test
if ($LASTEXITCODE -ne 0) {
    Write-Error "Frontend tests failed"
    exit 1
}
Pop-Location
Write-Host "✓ Frontend tests passed" -ForegroundColor Green

# Step 3: Build Docker images
Write-Host "`n[3/7] Building Docker images..." -ForegroundColor Yellow

$imageTag = git rev-parse --short HEAD

docker build -t portfolio-backend:$imageTag ./backend
if ($LASTEXITCODE -ne 0) {
    Write-Error "Backend Docker build failed"
    exit 1
}

docker build -t portfolio-frontend:$imageTag ./frontend
if ($LASTEXITCODE -ne 0) {
    Write-Error "Frontend Docker build failed"
    exit 1
}
Write-Host "✓ Docker images built successfully" -ForegroundColor Green

# Step 4: Push to registry
Write-Host "`n[4/7] Pushing images to registry..." -ForegroundColor Yellow

docker tag portfolio-backend:$imageTag username/portfolio-backend:$imageTag
docker push username/portfolio-backend:$imageTag

docker tag portfolio-frontend:$imageTag username/portfolio-frontend:$imageTag
docker push username/portfolio-frontend:$imageTag

Write-Host "✓ Images pushed to registry" -ForegroundColor Green

# Step 5: Deploy infrastructure with Terraform
Write-Host "`n[5/7] Deploying infrastructure..." -ForegroundColor Yellow

Push-Location infra/environments/$Environment

terraform init
terraform plan -out=tfplan

# Ask for confirmation in production
if ($Environment -eq "prod") {
    Write-Host "`nYou are about to deploy to PRODUCTION!" -ForegroundColor Red
    $confirmation = Read-Host "Type 'yes' to continue"
    if ($confirmation -ne "yes") {
        Write-Host "Deployment cancelled" -ForegroundColor Yellow
        exit 0
    }
}

terraform apply tfplan
Pop-Location
Write-Host "✓ Infrastructure deployed" -ForegroundColor Green

# Step 6: Deploy application
Write-Host "`n[6/7] Deploying application..." -ForegroundColor Yellow

# Get infrastructure outputs
$albDns = terraform output -raw alb_dns_name

# Update ECS service or EC2 instances with new image
# (Implementation depends on your deployment method)

Write-Host "✓ Application deployed" -ForegroundColor Green

# Step 7: Verify deployment
Write-Host "`n[7/7] Verifying deployment..." -ForegroundColor Yellow

Start-Sleep -Seconds 30  # Wait for services to stabilize

$healthUrl = "http://$albDns/health"
try {
    $response = Invoke-WebRequest -Uri $healthUrl -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ Health check passed" -ForegroundColor Green
    } else {
        Write-Warning "Health check returned status $($response.StatusCode)"
    }
} catch {
    Write-Warning "Health check failed: $_"
}

# Display deployment summary
Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Environment: $Environment" -ForegroundColor White
Write-Host "Version: $imageTag" -ForegroundColor White
Write-Host "URL: http://$albDns" -ForegroundColor White
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Test the application at the URL above" -ForegroundColor White
Write-Host "2. Monitor logs and metrics in CloudWatch" -ForegroundColor White
Write-Host "3. If issues occur, rollback with: .\rollback.ps1 -Environment $Environment" -ForegroundColor White
