# Payment Flow Guide - Stripe Integration

## 🔄 Payment Flow Diagrams

### 1. Subscription Payment Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                     SUBSCRIPTION PAYMENT FLOW                        │
└─────────────────────────────────────────────────────────────────────┘

User                    Frontend                Backend               Stripe
  │                        │                       │                    │
  │  1. Visit Plans Page   │                       │                    │
  ├───────────────────────>│                       │                    │
  │                        │                       │                    │
  │  2. Click "Choose Plan"│                       │                    │
  ├───────────────────────>│                       │                    │
  │                        │                       │                    │
  │                        │  3. Create Session    │                    │
  │                        ├──────────────────────>│                    │
  │                        │                       │                    │
  │                        │                       │  4. Create Checkout│
  │                        │                       ├───────────────────>│
  │                        │                       │                    │
  │                        │                       │  5. Session ID     │
  │                        │                       │<───────────────────│
  │                        │                       │                    │
  │                        │  6. Return Session ID │                    │
  │                        │<──────────────────────│                    │
  │                        │                       │                    │
  │  7. Redirect to Stripe │                       │                    │
  ├───────────────────────────────────────────────────────────────────>│
  │                        │                       │                    │
  │  8. Enter Card Details │                       │                    │
  ├───────────────────────────────────────────────────────────────────>│
  │                        │                       │                    │
  │  9. Process Payment    │                       │                    │
  │<───────────────────────────────────────────────────────────────────│
  │                        │                       │                    │
  │                        │                       │  10. Webhook Event │
  │                        │                       │<───────────────────│
  │                        │                       │                    │
  │                        │                       │  11. Update DB     │
  │                        │                       │  - Create payment  │
  │                        │                       │  - Activate sub    │
  │                        │                       │  - Award points    │
  │                        │                       │  - Set premium     │
  │                        │                       │                    │
  │  12. Success Page      │                       │                    │
  │<───────────────────────────────────────────────│                    │
  │                        │                       │                    │
```

### 2. Service Booking Payment Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                   SERVICE BOOKING PAYMENT FLOW                       │
└─────────────────────────────────────────────────────────────────────┘

User                    Frontend                Backend               Stripe
  │                        │                       │                    │
  │  1. Book Service       │                       │                    │
  ├───────────────────────>│                       │                    │
  │                        │                       │                    │
  │                        │  2. Submit Booking    │                    │
  │                        ├──────────────────────>│                    │
  │                        │                       │                    │
  │                        │                       │  3. Calculate Price│
  │                        │                       │  - Base price      │
  │                        │                       │  - Surge pricing   │
  │                        │                       │  - Discounts       │
  │                        │                       │  - Tax             │
  │                        │                       │                    │
  │                        │  4. Booking Created   │                    │
  │                        │<──────────────────────│                    │
  │                        │                       │                    │
  │  5. View Booking       │                       │                    │
  ├───────────────────────>│                       │                    │
  │                        │                       │                    │
  │  6. Click "Pay Now"    │                       │                    │
  ├───────────────────────>│                       │                    │
  │                        │                       │                    │
  │                        │  7. Create Payment    │                    │
  │                        ├──────────────────────>│                    │
  │                        │                       │                    │
  │                        │                       │  8. Create Checkout│
  │                        │                       ├───────────────────>│
  │                        │                       │                    │
  │  9. Redirect & Pay     │                       │                    │
  ├───────────────────────────────────────────────────────────────────>│
  │                        │                       │                    │
  │                        │                       │  10. Webhook       │
  │                        │                       │<───────────────────│
  │                        │                       │                    │
  │                        │                       │  11. Update Status │
  │                        │                       │  - Mark as paid    │
  │                        │                       │  - Award points    │
  │                        │                       │                    │
  │  12. Success           │                       │                    │
  │<───────────────────────────────────────────────│                    │
```

### 3. Webhook Processing Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                      WEBHOOK PROCESSING FLOW                         │
└─────────────────────────────────────────────────────────────────────┘

Stripe                  Backend                 Database
  │                        │                       │
  │  1. Payment Event      │                       │
  ├───────────────────────>│                       │
  │  (checkout.session.    │                       │
  │   completed)           │                       │
  │                        │                       │
  │                        │  2. Verify Signature  │
  │                        │  (webhook secret)     │
  │                        │                       │
  │                        │  3. Parse Event       │
  │                        │  - Get user_id        │
  │                        │  - Get payment_type   │
  │                        │  - Get metadata       │
  │                        │                       │
  │                        │  4. Process Payment   │
  │                        │                       │
  │                        │  If Subscription:     │
  │                        ├──────────────────────>│
  │                        │  - Insert payment     │
  │                        │  - Create subscription│
  │                        │  - Set premium status │
  │                        │  - Award points       │
  │                        │                       │
  │                        │  If Service:          │
  │                        ├──────────────────────>│
  │                        │  - Insert payment     │
  │                        │  - Update request     │
  │                        │  - Award points       │
  │                        │                       │
  │  5. Return 200 OK      │                       │
  │<───────────────────────│                       │
  │                        │                       │
```

---

## 🎯 Key Integration Points

### 1. Frontend Integration
**File**: `templates/subscription_plans.html`

```javascript
// Stripe.js loaded
<script src="https://js.stripe.com/v3/"></script>

// Initialize Stripe
let stripe = Stripe(publishableKey);

// Create checkout session
fetch('/create-checkout-session', {
    method: 'POST',
    body: JSON.stringify({ plan_type: planName })
})

// Redirect to Stripe Checkout
stripe.redirectToCheckout({ sessionId: sessionId })
```

### 2. Backend Session Creation
**File**: `app.py`

```python
@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    # Create Stripe checkout session
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[...],
        mode='subscription',
        success_url=url_for('payment_success', _external=True),
        cancel_url=url_for('payment_cancel', _external=True),
        metadata={'user_id': user_id, 'plan_type': plan_type}
    )
    return jsonify({'sessionId': checkout_session.id})
```

### 3. Webhook Handler
**File**: `app.py`

```python
@app.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    # Verify signature
    event = stripe.Webhook.construct_event(
        payload, sig_header, STRIPE_WEBHOOK_SECRET
    )
    
    # Handle event
    if event['type'] == 'checkout.session.completed':
        handle_checkout_session_completed(session)
    
    return jsonify({'status': 'success'})
```

---

## 💳 Payment Methods Supported

### Via Stripe Checkout:
1. **Credit/Debit Cards**
   - Visa
   - Mastercard
   - American Express
   - Discover
   - Diners Club
   - JCB

2. **Digital Wallets** (if enabled)
   - Apple Pay
   - Google Pay

3. **Bank Transfers** (India)
   - UPI
   - Net Banking
   - Wallets (Paytm, PhonePe, etc.)

---

## 🔐 Security Measures

### 1. API Key Protection
```python
# Environment variables (not in code)
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
```

### 2. Webhook Signature Verification
```python
# Verify every webhook
event = stripe.Webhook.construct_event(
    payload, sig_header, STRIPE_WEBHOOK_SECRET
)
```

### 3. User Authentication
```python
@login_required  # Must be logged in
def create_checkout_session():
    user_id = session['user_id']  # Verified user
```

### 4. HTTPS Required
- Stripe requires HTTPS for webhooks
- All payment data encrypted in transit
- PCI DSS compliant via Stripe

---

## 📊 Database Updates

### On Successful Payment:

1. **payments table**:
   ```sql
   INSERT INTO payments (
       user_id, stripe_checkout_session_id, 
       amount, status, payment_type
   )
   ```

2. **subscriptions table**:
   ```sql
   INSERT INTO subscriptions (
       user_id, plan_type, start_date, 
       end_date, stripe_subscription_id
   )
   ```

3. **users table**:
   ```sql
   UPDATE users 
   SET is_premium = 1, 
       loyalty_points = loyalty_points + bonus
   WHERE id = user_id
   ```

4. **service_requests table** (for service payments):
   ```sql
   UPDATE service_requests 
   SET status = 'paid' 
   WHERE id = service_request_id
   ```

---

## 🧪 Testing Scenarios

### Test Case 1: Successful Subscription
1. Navigate to `/subscription_plans`
2. Click "Choose Premium"
3. Enter card: 4242 4242 4242 4242
4. Complete payment
5. ✅ Verify: Premium status activated
6. ✅ Verify: Payment recorded in database
7. ✅ Verify: Loyalty points awarded

### Test Case 2: Failed Payment
1. Navigate to `/subscription_plans`
2. Click "Choose Basic"
3. Enter card: 4000 0000 0000 9995
4. Payment declined
5. ✅ Verify: No subscription created
6. ✅ Verify: User redirected to cancel page

### Test Case 3: Webhook Processing
1. Make a payment
2. Check webhook logs
3. ✅ Verify: Webhook received
4. ✅ Verify: Signature verified
5. ✅ Verify: Database updated
6. ✅ Verify: 200 OK returned

---

## 🚦 Status Flow

### Payment Status:
```
pending → processing → completed/failed
```

### Subscription Status:
```
inactive → active → cancelled/expired
```

### Service Request Status:
```
pending → accepted → paid → in_progress → completed
```

---

## 📱 User Experience Flow

### Happy Path:
1. User selects plan
2. Redirected to Stripe (secure)
3. Enters payment details
4. Payment processed
5. Redirected to success page
6. Benefits activated immediately
7. Confirmation email sent (future)

### Error Path:
1. User selects plan
2. Redirected to Stripe
3. Payment fails/cancelled
4. Redirected to cancel page
5. Can try again
6. Original plan still available

---

## 🔄 Recurring Payments

### Subscription Renewals:
- Handled automatically by Stripe
- Webhook notifies on renewal
- Database updated automatically
- User charged on renewal date
- Email notification (future)

### Cancellation:
- User can cancel in Stripe portal
- Webhook notifies cancellation
- Premium status removed
- Access until end of period

---

## 📈 Analytics & Tracking

### Metrics Available:
1. Total revenue
2. Subscription count
3. Payment success rate
4. Average transaction value
5. Popular plans
6. Failed payment reasons

### Stripe Dashboard:
- Real-time payment monitoring
- Revenue charts
- Customer analytics
- Dispute management
- Refund processing

---

## 🆘 Error Handling

### Common Errors:

1. **Invalid API Key**
   - Check environment variables
   - Verify test/live mode

2. **Webhook Signature Failed**
   - Verify webhook secret
   - Check endpoint URL

3. **Payment Declined**
   - User notified
   - Can retry
   - Different card option

4. **Session Expired**
   - Create new session
   - User redirected

---

**For detailed setup instructions, see: STRIPE_SETUP_GUIDE.md**
**For quick start, see: QUICK_START_STRIPE.md**
