# Quick Start Guide - Stripe Integration

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Get Stripe Test Keys

1. Go to https://dashboard.stripe.com/test/apikeys
2. Copy your keys:
   - **Publishable key**: `pk_test_...`
   - **Secret key**: `sk_test_...`

### Step 3: Set Environment Variables

**Windows (PowerShell):**
```powershell
$env:STRIPE_SECRET_KEY="sk_test_YOUR_KEY_HERE"
$env:STRIPE_PUBLISHABLE_KEY="pk_test_YOUR_KEY_HERE"
```

**Or edit app.py directly (lines 544-547):**
```python
stripe.api_key = 'sk_test_YOUR_SECRET_KEY_HERE'
STRIPE_PUBLISHABLE_KEY = 'pk_test_YOUR_PUBLISHABLE_KEY_HERE'
```

### Step 4: Run the Application
```bash
python app.py
```

### Step 5: Test Payment

1. Open http://localhost:5000
2. Login or register as a user
3. Go to **Subscription Plans**
4. Click on any plan
5. Use test card: **4242 4242 4242 4242**
   - Expiry: Any future date (12/34)
   - CVC: Any 3 digits (123)
   - ZIP: Any 5 digits (12345)

## ✅ What's Included

### Payment Features:
- ✅ Subscription payments (Basic, Premium, Annual)
- ✅ Service booking payments
- ✅ Dynamic pricing with surge
- ✅ Group booking discounts
- ✅ Premium member discounts
- ✅ Payment history tracking
- ✅ Webhook handling

### New Routes:
- `/subscription_plans` - View and purchase plans
- `/payment-history` - View all transactions
- `/my-subscriptions` - Manage subscriptions
- `/stripe-webhook` - Webhook endpoint

### Database Tables Added:
- `payments` - Track all payment transactions
- Updated `subscriptions` - Added Stripe IDs

## 🧪 Test Cards

| Card Number | Result |
|-------------|--------|
| 4242 4242 4242 4242 | Success |
| 4000 0025 0000 3155 | Requires 3D Secure |
| 4000 0000 0000 9995 | Declined |

## 📝 For Production

1. Switch to live keys from https://dashboard.stripe.com/apikeys
2. Set up webhooks at https://dashboard.stripe.com/webhooks
3. Use HTTPS for your domain
4. Complete Stripe business verification

## 🆘 Need Help?

See `STRIPE_SETUP_GUIDE.md` for detailed documentation.

## 🔒 Security Note

**Never commit your real API keys to version control!**
- Use environment variables
- Add `.env` to `.gitignore`
- Keep secret keys secret

---

**That's it!** Your payment gateway is ready to use. 🎉
