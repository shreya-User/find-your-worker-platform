# Razorpay Integration Setup Script for PowerShell
# This script helps you set up Razorpay payment integration

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   RAZORPAY INTEGRATION SETUP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Step 1: Installing dependencies..." -ForegroundColor Yellow
try {
    pip install -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Dependencies installed successfully!" -ForegroundColor Green
    } else {
        throw "Failed to install dependencies"
    }
} catch {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host ""

Write-Host "Step 2: Setting up environment variables..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Please enter your Razorpay credentials:" -ForegroundColor White
Write-Host "(Get them from https://dashboard.razorpay.com/app/keys)" -ForegroundColor Gray
Write-Host ""

$keyId = Read-Host "Enter your Razorpay Key ID (e.g., rzp_test_xxxxx)"
$keySecret = Read-Host "Enter your Razorpay Key Secret"

Write-Host ""
Write-Host "Setting environment variables for this session..." -ForegroundColor Yellow
$env:RAZORPAY_KEY_ID = $keyId
$env:RAZORPAY_KEY_SECRET = $keySecret

Write-Host "✓ Environment variables set!" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   SETUP COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your Razorpay integration is ready!" -ForegroundColor Green
Write-Host ""
Write-Host "To start the application:" -ForegroundColor Yellow
Write-Host "  python app.py" -ForegroundColor White
Write-Host ""
Write-Host "To access the application:" -ForegroundColor Yellow
Write-Host "  http://127.0.0.1:5000" -ForegroundColor White
Write-Host ""
Write-Host "NOTE: Environment variables are set for this session only." -ForegroundColor Yellow
Write-Host "For permanent setup, add them to your system environment variables." -ForegroundColor Yellow
Write-Host ""
Write-Host "For detailed instructions, see: RAZORPAY_SETUP_GUIDE.md" -ForegroundColor Cyan
Write-Host ""

# Ask if user wants to start the application now
$response = Read-Host "Would you like to start the application now? (y/n)"
if ($response -eq 'y' -or $response -eq 'Y') {
    Write-Host ""
    Write-Host "Starting Flask application..." -ForegroundColor Green
    python app.py
} else {
    Write-Host ""
    Write-Host "You can start the application anytime by running: python app.py" -ForegroundColor Cyan
    Read-Host "Press Enter to exit"
}
