# Stripe Payment Gateway Integration Guide

## Overview
This guide will help you set up Stripe payment gateway for your Find My Worker application. The integration supports:
- Subscription payments (Basic, Premium, Annual plans)
- Service booking payments
- Webhook handling for payment confirmations
- Payment history tracking

## Prerequisites
1. A Stripe account (sign up at https://stripe.com)
2. Python 3.7 or higher
3. Flask application running

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Flask 3.0.0
- Werkzeug 3.0.1
- stripe 7.9.0

## Step 2: Get Your Stripe API Keys

1. Log in to your Stripe Dashboard: https://dashboard.stripe.com
2. Navigate to **Developers** → **API keys**
3. You'll see two types of keys:
   - **Publishable key** (starts with `pk_test_` for test mode)
   - **Secret key** (starts with `sk_test_` for test mode)

### For Development/Testing:
Use the **test mode** keys. Test cards won't charge real money.

### For Production:
Toggle to **live mode** and use the live keys (starts with `pk_live_` and `sk_live_`)

## Step 3: Configure Environment Variables

### Option A: Using Environment Variables (Recommended for Production)

**Windows (PowerShell):**
```powershell
$env:STRIPE_SECRET_KEY="sk_test_your_secret_key_here"
$env:STRIPE_PUBLISHABLE_KEY="pk_test_your_publishable_key_here"
$env:STRIPE_WEBHOOK_SECRET="whsec_your_webhook_secret_here"
```

**Windows (Command Prompt):**
```cmd
set STRIPE_SECRET_KEY=sk_test_your_secret_key_here
set STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
set STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

**Linux/Mac:**
```bash
export STRIPE_SECRET_KEY="sk_test_your_secret_key_here"
export STRIPE_PUBLISHABLE_KEY="pk_test_your_publishable_key_here"
export STRIPE_WEBHOOK_SECRET="whsec_your_webhook_secret_here"
```

### Option B: Direct Configuration in app.py (For Testing Only)

Open `app.py` and update these lines (around line 544-547):

```python
stripe.api_key = 'sk_test_YOUR_SECRET_KEY_HERE'
STRIPE_PUBLISHABLE_KEY = 'pk_test_YOUR_PUBLISHABLE_KEY_HERE'
STRIPE_WEBHOOK_SECRET = 'whsec_YOUR_WEBHOOK_SECRET_HERE'
```

**⚠️ IMPORTANT:** Never commit real API keys to version control!

## Step 4: Set Up Stripe Webhooks

Webhooks allow Stripe to notify your application about payment events.

### For Local Development (Using Stripe CLI):

1. **Install Stripe CLI:**
   - Download from: https://stripe.com/docs/stripe-cli
   - Or use package managers:
     ```bash
     # Windows (with Scoop)
     scoop install stripe
     
     # Mac (with Homebrew)
     brew install stripe/stripe-cli/stripe
     
     # Linux
     # Download from GitHub releases
     ```

2. **Login to Stripe CLI:**
   ```bash
   stripe login
   ```

3. **Forward webhooks to your local server:**
   ```bash
   stripe listen --forward-to localhost:5000/stripe-webhook
   ```
   
   This command will output a webhook signing secret (starts with `whsec_`). 
   Copy this and set it as your `STRIPE_WEBHOOK_SECRET`.

### For Production (Stripe Dashboard):

1. Go to **Developers** → **Webhooks** in Stripe Dashboard
2. Click **Add endpoint**
3. Enter your endpoint URL: `https://yourdomain.com/stripe-webhook`
4. Select events to listen to:
   - `checkout.session.completed`
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `customer.subscription.deleted`
5. Click **Add endpoint**
6. Copy the **Signing secret** and set it as `STRIPE_WEBHOOK_SECRET`

## Step 5: Test the Integration

### Test Cards (Use in Test Mode):

**Successful Payment:**
- Card Number: `4242 4242 4242 4242`
- Expiry: Any future date (e.g., 12/34)
- CVC: Any 3 digits (e.g., 123)
- ZIP: Any 5 digits (e.g., 12345)

**Payment Requires Authentication (3D Secure):**
- Card Number: `4000 0025 0000 3155`

**Payment Declined:**
- Card Number: `4000 0000 0000 9995`

More test cards: https://stripe.com/docs/testing

### Testing Flow:

1. **Start your Flask application:**
   ```bash
   python app.py
   ```

2. **Start Stripe CLI (in another terminal):**
   ```bash
   stripe listen --forward-to localhost:5000/stripe-webhook
   ```

3. **Test Subscription Payment:**
   - Navigate to: http://localhost:5000/subscription_plans
   - Click on any plan
   - Use test card: 4242 4242 4242 4242
   - Complete the payment

4. **Test Service Payment:**
   - Book a service
   - After booking is accepted, you can add payment functionality
   - Use test card for payment

5. **Verify in Stripe Dashboard:**
   - Go to **Payments** section
   - You should see your test payments

## Step 6: Payment Features

### Features Implemented:

1. **Subscription Payments:**
   - Basic Plan: ₹99/month
   - Premium Plan: ₹299/month
   - Annual Plan: ₹2999/year
   - Automatic premium status activation
   - Loyalty points award on subscription

2. **Service Booking Payments:**
   - Dynamic pricing based on demand
   - Surge pricing for peak hours
   - Group booking discounts (15%)
   - Premium member discounts (10%)
   - Detailed price breakdown

3. **Payment History:**
   - View all transactions
   - Filter by payment type
   - Transaction status tracking
   - Download receipts (future feature)

4. **Webhook Handling:**
   - Automatic payment confirmation
   - Subscription status updates
   - Failed payment handling
   - Subscription cancellation handling

### Available Routes:

- `/subscription_plans` - View and purchase subscription plans
- `/create-checkout-session` - Create Stripe checkout for subscriptions
- `/create-service-payment` - Create Stripe checkout for services
- `/payment-success` - Payment success page
- `/payment-cancel` - Payment cancellation page
- `/stripe-webhook` - Webhook endpoint for Stripe events
- `/payment-history` - View all payment transactions
- `/my-subscriptions` - Manage subscriptions

## Step 7: Currency Configuration

The application is configured for **INR (Indian Rupees)**. To change currency:

1. Update the currency in checkout session creation (app.py):
   ```python
   'currency': 'usd',  # Change from 'inr' to your currency
   ```

2. Update amount calculation (Stripe uses smallest currency unit):
   - For INR: multiply by 100 (paisa)
   - For USD: multiply by 100 (cents)
   - For JPY: use as-is (no decimal)

## Step 8: Security Best Practices

1. **Never expose secret keys:**
   - Use environment variables
   - Add `.env` to `.gitignore`
   - Never commit keys to version control

2. **Verify webhook signatures:**
   - Always validate webhook signatures
   - Use the webhook secret provided by Stripe

3. **Use HTTPS in production:**
   - Stripe requires HTTPS for webhooks
   - Use SSL certificates for your domain

4. **Implement proper error handling:**
   - Log payment errors
   - Show user-friendly error messages
   - Retry failed payments

5. **Test thoroughly:**
   - Use test mode extensively
   - Test all payment scenarios
   - Test webhook handling

## Step 9: Going Live

Before going live:

1. **Switch to Live Mode:**
   - Get live API keys from Stripe Dashboard
   - Update environment variables with live keys
   - Update webhook endpoint to production URL

2. **Business Verification:**
   - Complete Stripe account verification
   - Provide business details
   - Set up bank account for payouts

3. **Compliance:**
   - Review Stripe's terms of service
   - Implement required legal pages (Terms, Privacy Policy)
   - Display pricing clearly to customers

4. **Monitoring:**
   - Set up email notifications for payments
   - Monitor Stripe Dashboard regularly
   - Set up alerts for failed payments

## Troubleshooting

### Common Issues:

1. **"No such checkout session" error:**
   - Verify API keys are correct
   - Check if using test/live mode consistently

2. **Webhook signature verification failed:**
   - Ensure webhook secret is correct
   - Check if using the right secret for test/live mode

3. **Payment not reflecting in database:**
   - Check webhook endpoint is accessible
   - Verify webhook is being received (check Stripe Dashboard → Webhooks)
   - Check application logs for errors

4. **"Invalid API key" error:**
   - Verify secret key is set correctly
   - Check for extra spaces or quotes in key
   - Ensure using correct mode (test/live)

### Debug Mode:

Enable Stripe debug logging in app.py:

```python
import logging
stripe.log = 'debug'
logging.basicConfig(level=logging.DEBUG)
```

## Support

- **Stripe Documentation:** https://stripe.com/docs
- **Stripe Support:** https://support.stripe.com
- **Test Cards:** https://stripe.com/docs/testing
- **Webhook Testing:** https://stripe.com/docs/webhooks/test

## Additional Resources

- [Stripe Checkout Documentation](https://stripe.com/docs/payments/checkout)
- [Stripe Subscriptions Guide](https://stripe.com/docs/billing/subscriptions/overview)
- [Webhook Events Reference](https://stripe.com/docs/api/events/types)
- [Testing Guide](https://stripe.com/docs/testing)

---

**Note:** This integration is production-ready but should be thoroughly tested before deploying to live environment. Always start with test mode and verify all payment flows work as expected.
