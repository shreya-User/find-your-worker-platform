# 🎉 Razorpay Payment Integration Added!

Your Flask Service Portal now supports Razorpay payments alongside Stripe!

## 🚀 Quick Start

### Option 1: Automatic Setup (Windows)

**PowerShell:**
```powershell
.\setup_razorpay.ps1
```

**Command Prompt:**
```cmd
setup_razorpay.bat
```

### Option 2: Manual Setup

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get Razorpay Keys:**
   - Go to https://dashboard.razorpay.com
   - Sign up / Log in
   - Navigate to Settings → API Keys
   - Generate Test Keys

3. **Set Environment Variables:**
   
   **PowerShell:**
   ```powershell
   $env:RAZORPAY_KEY_ID = "rzp_test_xxxxxxxxxxxxx"
   $env:RAZORPAY_KEY_SECRET = "xxxxxxxxxxxxx"
   ```
   
   **Command Prompt:**
   ```cmd
   set RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxxx
   set RAZORPAY_KEY_SECRET=xxxxxxxxxxxxx
   ```

4. **Run the Application:**
   ```bash
   python app.py
   ```

5. **Access the App:**
   Open http://127.0.0.1:5000 in your browser

## ✨ What's New?

### For Users
- 💳 **Multiple Payment Options**: Choose between Stripe or Razorpay
- 🇮🇳 **India-Optimized**: UPI, Net Banking, Cards, Wallets
- 💰 **Lower Fees**: UPI payments have 0% fees (up to ₹2000)
- ⚡ **Faster Checkout**: Familiar payment interface for Indian users

### For Developers
- 📦 New Package: `razorpay==2.0.0`
- 🔧 New Routes:
  - `POST /create-razorpay-order`
  - `POST /create-razorpay-service-order`
  - `POST /razorpay-payment-success`
  - `POST /razorpay-webhook`
- 🎨 Updated Template: `subscription_plans.html`
- 📚 Documentation: 
  - `RAZORPAY_SETUP_GUIDE.md` (detailed setup)
  - `RAZORPAY_INTEGRATION_SUMMARY.md` (technical details)

## 🎯 Payment Flow

### Subscription Payments
1. User navigates to **Subscription Plans** page
2. Selects a plan (Basic, Premium, or Annual)
3. Clicks **"Pay with Razorpay"** button
4. Razorpay checkout modal opens
5. User completes payment (UPI/Card/NetBanking/Wallet)
6. Payment is verified
7. Subscription activated + Loyalty points awarded

### Service Payments
1. User books a service
2. Selects payment method (Razorpay)
3. Completes payment
4. Service booking confirmed

## 💳 Test Payment Methods

### Test Cards
```
Success Card:
Card Number: 4111 1111 1111 1111
CVV: 123
Expiry: 12/30
Name: Test User

Failure Card:
Card Number: 4000 0000 0000 0002
```

### Test UPI
```
Success: success@razorpay
Failure: failure@razorpay
```

### Test Net Banking
Select any bank and use:
- Username: `razorpay`
- Password: `razorpay`

## 📋 Features

### Payment Methods Supported
✅ Credit/Debit Cards (Visa, Mastercard, Rupay, Amex)  
✅ UPI (Google Pay, PhonePe, Paytm, etc.)  
✅ Net Banking (50+ banks)  
✅ Wallets (Paytm, PhonePe, Amazon Pay, etc.)  
✅ EMI (Credit Card & Cardless)

### Security Features
✅ Payment signature verification  
✅ Webhook signature verification  
✅ PCI DSS Level 1 Compliant  
✅ 3D Secure authentication  
✅ Encrypted transactions

## 📁 Files Modified/Added

### Modified Files
- ✏️ `app.py` - Added Razorpay integration
- ✏️ `requirements.txt` - Added razorpay dependency
- ✏️ `templates/subscription_plans.html` - Added Razorpay payment option

### New Files
- ➕ `RAZORPAY_SETUP_GUIDE.md` - Comprehensive setup guide
- ➕ `RAZORPAY_INTEGRATION_SUMMARY.md` - Technical documentation
- ➕ `README_RAZORPAY.md` - This file
- ➕ `setup_razorpay.ps1` - PowerShell setup script
- ➕ `setup_razorpay.bat` - Batch setup script

## 🔧 Configuration

### Environment Variables
```bash
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxxx          # Your Razorpay Key ID
RAZORPAY_KEY_SECRET=xxxxxxxxxxxxx               # Your Razorpay Key Secret
RAZORPAY_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx     # Your Webhook Secret (optional)
```

### In app.py
```python
# Razorpay Configuration
RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', 'rzp_test_xxxxxxxxxxxxx')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', 'xxxxxxxxxxxxx')
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
```

## 🎬 Demo Flow

1. **Start Application:**
   ```bash
   python app.py
   ```

2. **Register/Login:**
   - Create a new user account or login

3. **Test Subscription Payment:**
   - Go to "Subscription Plans"
   - Click "Pay with Razorpay" on any plan
   - Use test card: `4111 1111 1111 1111`
   - Complete payment
   - Verify subscription is activated

4. **Check Database:**
   - Payment recorded in `payments` table
   - Subscription created in `subscriptions` table
   - User's `is_premium` flag updated
   - Loyalty points awarded

## 📊 Pricing Comparison

| Feature | Stripe | Razorpay |
|---------|--------|----------|
| **Indian Cards** | 2.9% + ₹2.5 | 2% |
| **UPI** | Not supported | 0% (up to ₹2000) |
| **Net Banking** | Not supported | 1.5-2.5% |
| **International Cards** | 3.9% | 3% |
| **Best For** | International | Indian customers |

## 🐛 Troubleshooting

### Issue: "Invalid API Key"
**Solution:** Check your API keys match the mode (test/live)

### Issue: Razorpay button doesn't work
**Solution:** Ensure Razorpay SDK is loaded in the HTML template

### Issue: Payment succeeds but not recorded
**Solution:** Check application logs and database connection

### Issue: Webhook not working
**Solution:** Ensure webhook URL is publicly accessible and HTTPS

## 📞 Support

- **Razorpay Docs:** https://razorpay.com/docs/
- **Dashboard:** https://dashboard.razorpay.com
- **Support:** https://razorpay.com/support/

## 📈 Next Steps

### For Development
- ✅ Test all payment flows
- ✅ Verify payment recording
- ✅ Test error scenarios
- ⬜ Set up webhooks (optional)

### For Production
- ⬜ Complete Razorpay KYC
- ⬜ Get live API keys
- ⬜ Update environment variables
- ⬜ Set up production webhooks
- ⬜ Enable HTTPS
- ⬜ Go live!

## 🎓 Documentation

For more detailed information, check:

- **Setup Guide:** `RAZORPAY_SETUP_GUIDE.md`
- **Technical Details:** `RAZORPAY_INTEGRATION_SUMMARY.md`
- **Razorpay API Docs:** https://razorpay.com/docs/api/

## 🎉 You're All Set!

Your application now supports dual payment gateways:
- **Stripe** for international customers
- **Razorpay** for Indian customers

Both work seamlessly with your existing subscription and service booking system!

---

**Questions?** Check the documentation files or contact Razorpay support.

**Happy Coding! 💻🚀**
