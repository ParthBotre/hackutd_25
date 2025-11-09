# PowerShell script to create .env file for Windows

Write-Host "🚀 PM Mockup Generator - Environment Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$envPath = Join-Path $PSScriptRoot ".env"

if (Test-Path $envPath) {
    Write-Host "⚠️  .env file already exists at: $envPath" -ForegroundColor Yellow
    Write-Host ""
    $overwrite = Read-Host "Do you want to overwrite it? (y/N)"
    if ($overwrite -ne "y" -and $overwrite -ne "Y") {
        Write-Host "ℹ️  Skipping .env file creation" -ForegroundColor Blue
        exit 0
    }
}

Write-Host "📝 Creating .env file..." -ForegroundColor Green

$envContent = @"
# NVIDIA Nemotron API Configuration
# Get your API key from: https://build.nvidia.com/
NVIDIA_API_KEY=your_nvidia_api_key_here
NVIDIA_API_URL=https://integrate.api.nvidia.com/v1/chat/completions

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
"@

$envContent | Out-File -FilePath $envPath -Encoding utf8

Write-Host "✅ .env file created at: $envPath" -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  IMPORTANT: Edit the .env file and replace 'your_nvidia_api_key_here' with your actual API key!" -ForegroundColor Yellow
Write-Host "   Get your API key from: https://build.nvidia.com/" -ForegroundColor Yellow
Write-Host ""
Write-Host "📝 To edit the file, run: notepad $envPath" -ForegroundColor Cyan

