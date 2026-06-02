# Razorpay Integration Setup Guide

## Overview
This application now supports **Razorpay** payment gateway alongside Stripe for processing payments in India. Razorpay is optimized for Indian customers and supports multiple payment methods including UPI, Cards, Net Banking, and Wallets.

## Features Implemented
- ✅ Subscription payments via Razorpay
- ✅ Service booking payments via Razorpay
- ✅ Payment verification and signature validation
- ✅ Webhook support for payment notifications
- ✅ Dual gateway support (Stripe + Razorpay)

## Setup Instructions

### 1. Create Razorpay Account
1. Go to [https://razorpay.com](https://razorpay.com)
2. Sign up for a free account
3. Complete the KYC verification (required for live mode)

### 2. Get API Keys

#### Test Mode Keys (for development)
1. Log in to [Razorpay Dashboard](https://dashboard.razorpay.com)
2. Go to **Settings** → **API Keys**
3. In **Test Mode**, click **Generate Test Key**
4. You'll get:
   - **Key ID**: `rzp_test_xxxxxxxxxxxxx`
   - **Key Secret**: `xxxxxxxxxxxxx`

#### Live Mode Keys (for production)
1. Complete your account activation and KYC
2. Switch to **Live Mode** in the dashboard
3. Generate Live API Keys
4. You'll get:
   - **Key ID**: `rzp_live_xxxxxxxxxxxxx`
   - **Key Secret**: `xxxxxxxxxxxxx`

### 3. Configure Environment Variables

#### Option 1: Using Environment Variables (Recommended)

**Windows (PowerShell):**
```powershell
$env:RAZORPAY_KEY_ID = "rzp_test_xxxxxxxxxxxxx"
$env:RAZORPAY_KEY_SECRET = "xxxxxxxxxxxxx"
$env:RAZORPAY_WEBHOOK_SECRET = "whsec_xxxxxxxxxxxxx"
```

**Windows (Command Prompt):**
```cmd
set RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxxx
set RAZORPAY_KEY_SECRET=xxxxxxxxxxxxx
set RAZORPAY_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
```

**Linux/Mac:**
```bash
export RAZORPAY_KEY_ID="rzp_test_xxxxxxxxxxxxx"
export RAZORPAY_KEY_SECRET="xxxxxxxxxxxxx"
export RAZORPAY_WEBHOOK_SECRET="whsec_xxxxxxxxxxxxx"
```

#### Option 2: Directly in app.py (Not recommended for production)
Edit `app.py` and replace the placeholder values:
```python
RAZORPAY_KEY_ID = 'rzp_test_xxxxxxxxxxxxx'  # Your actual Key ID
RAZORPAY_KEY_SECRET = 'xxxxxxxxxxxxx'  # Your actual Key Secret
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

The requirements.txt now includes:
- Flask
- stripe
- razorpay

### 5. Test Payment Flow

#### Test Mode Credentials
Use these test card details in test mode:
- **Card Number**: 4111 1111 1111 1111
- **CVV**: Any 3 digits
- **Expiry**: Any future date
- **OTP**: Any 6 digits (when prompted)

#### UPI Testing
- Use any UPI ID format: `success@razorpay`
- For failure testing: `failure@razorpay`

### 6. Set Up Webhooks (Optional but Recommended)

Webhooks allow Razorpay to notify your application about payment events.

#### Local Development (using ngrok)
1. Install ngrok: [https://ngrok.com/download](https://ngrok.com/download)
2. Start your Flask app:
   ```bash
   python app.py
   ```
3. In another terminal, expose your local server:
   ```bash
   ngrok http 5000
   ```
4. Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

#### Configure Webhook in Razorpay
1. Go to [Razorpay Dashboard](https://dashboard.razorpay.com)
2. Navigate to **Settings** → **Webhooks**
3. Click **Add New Webhook**
4. Enter your webhook URL: `https://your-domain.com/razorpay-webhook`
   - For local testing: `https://abc123.ngrok.io/razorpay-webhook`
5. Select events to listen for:
   - ✅ `payment.captured`
   - ✅ `payment.failed`
   - ✅ `order.paid`
6. Save and copy the **Webhook Secret**
7. Add the webhook secret to your environment variables:
   ```bash
   export RAZORPAY_WEBHOOK_SECRET="whsec_xxxxxxxxxxxxx"
   ```

### 7. Go Live Checklist

Before going live with real payments:

- [ ] Complete Razorpay KYC verification
- [ ] Switch to Live Mode API keys
- [ ] Update environment variables with live keys
- [ ] Test all payment flows thoroughly
- [ ] Set up production webhook URL
- [ ] Enable HTTPS on your production server
- [ ] Review Razorpay's pricing and fees
- [ ] Set up proper error logging and monitoring

## Payment Flow

### Subscription Payment Flow
1. User selects a subscription plan
2. User clicks "Pay with Razorpay"
3. Razorpay order is created on server
4. Razorpay checkout modal opens
5. User completes payment
6. Payment signature is verified on server
7. Subscription is activated
8. User receives loyalty points

### Service Booking Payment Flow
1. User books a service
2. Price is calculated dynamically
3. User proceeds to payment
4. Razorpay order is created
5. User completes payment via Razorpay
6. Payment is verified
7. Service request status updated
8. Worker is notified

## API Endpoints

### Frontend Endpoints
- `POST /create-razorpay-order` - Create order for subscription
- `POST /create-razorpay-service-order` - Create order for service
- `POST /razorpay-payment-success` - Verify payment

### Webhook Endpoint
- `POST /razorpay-webhook` - Receive payment notifications

## Supported Payment Methods

Razorpay supports multiple payment methods popular in India:
- 💳 **Credit/Debit Cards** (Visa, Mastercard, Rupay, Amex)
- 📱 **UPI** (Google Pay, PhonePe, Paytm, etc.)
- 🏦 **Net Banking** (All major banks)
- 👛 **Wallets** (Paytm, PhonePe, Amazon Pay, etc.)
- 💵 **EMI** (3, 6, 9, 12 months)
- 🏪 **Cardless EMI**

## Currency Support
- Primary: **INR (₹)** - Indian Rupee
- Razorpay automatically handles currency conversion if needed

## Security Features
- ✅ PCI DSS Level 1 Compliant
- ✅ Payment signature verification
- ✅ Webhook signature verification
- ✅ SSL/TLS encryption
- ✅ 3D Secure authentication
- ✅ Fraud detection system

## Pricing (Razorpay)
- **Domestic Cards**: 2% per transaction
- **International Cards**: 3% per transaction
- **UPI**: 0% (zero fee) up to ₹2000, then 0.70%
- **Net Banking**: 1.5% to 2.5%
- **Wallets**: 1.5% to 2%

**Note**: Pricing may vary. Check latest pricing at [Razorpay Pricing](https://razorpay.com/pricing/)

## Testing Credentials

### Test Payment Success Scenarios
```
Card Number: 4111 1111 1111 1111
CVV: 123
Expiry: 12/25
Name: Test User
```

### Test Payment Failure
```
Card Number: 4000 0000 0000 0002
```

### Test UPI
- Success: `success@razorpay`
- Failure: `failure@razorpay`

## Troubleshooting

### Issue: "Invalid API Key"
**Solution**: Check that your API keys are correct and match the mode (test/live)

### Issue: "Signature Verification Failed"
**Solution**: Ensure you're using the correct Key Secret for signature verification

### Issue: Webhook not receiving events
**Solution**: 
- Verify webhook URL is publicly accessible
- Check webhook secret is configured correctly
- Ensure HTTPS is being used (required for webhooks)

### Issue: Payment succeeds but subscription not activated
**Solution**: 
- Check application logs for errors
- Verify payment verification endpoint is working
- Ensure database connection is stable

## Support & Resources

- **Razorpay Documentation**: [https://razorpay.com/docs/](https://razorpay.com/docs/)
- **API Reference**: [https://razorpay.com/docs/api/](https://razorpay.com/docs/api/)
- **Support**: [https://razorpay.com/support/](https://razorpay.com/support/)
- **Developer Forum**: [https://razorpay.com/forum/](https://razorpay.com/forum/)

## Compliance & Legal
- Ensure you comply with RBI guidelines for digital payments
- Display proper refund and cancellation policies
- Include terms and conditions for subscriptions
- Maintain transaction records as per legal requirements

## Next Steps

1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Get Razorpay API keys
3. ✅ Configure environment variables
4. ✅ Test in test mode
5. ✅ Set up webhooks
6. ✅ Complete KYC for live mode
7. ✅ Switch to live keys
8. ✅ Go live!

---

**Need Help?** 
- Check the Razorpay documentation
- Contact Razorpay support
- Review application logs for detailed error messages
