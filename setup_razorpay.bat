@echo off
REM Razorpay Integration Setup Script for Windows
REM This script helps you set up Razorpay payment integration

echo ========================================
echo   RAZORPAY INTEGRATION SETUP
echo ========================================
echo.

echo Step 1: Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed successfully!
echo.

echo Step 2: Setting up environment variables...
echo.
echo Please enter your Razorpay credentials:
echo (Get them from https://dashboard.razorpay.com/app/keys)
echo.

set /p RAZORPAY_KEY_ID="Enter your Razorpay Key ID (e.g., rzp_test_xxxxx): "
set /p RAZORPAY_KEY_SECRET="Enter your Razorpay Key Secret: "

echo.
echo Setting environment variables for this session...
set RAZORPAY_KEY_ID=%RAZORPAY_KEY_ID%
set RAZORPAY_KEY_SECRET=%RAZORPAY_KEY_SECRET%

echo ✓ Environment variables set!
echo.

echo ========================================
echo   SETUP COMPLETE!
echo ========================================
echo.
echo Your Razorpay integration is ready!
echo.
echo To start the application:
echo   python app.py
echo.
echo To access the application:
echo   http://127.0.0.1:5000
echo.
echo NOTE: Environment variables are set for this session only.
echo For permanent setup, add them to your system environment variables.
echo.
echo For detailed instructions, see: RAZORPAY_SETUP_GUIDE.md
echo.
pause
