import streamlit as st
from datetime import datetime, timedelta
from src.database.models import User, Payment, SubscriptionTier
from src.database.database import get_db

# Pricing Configuration
PRICING_PLANS = {
    SubscriptionTier.FREE: {
        'name': 'Free Tier',
        'price': 0,
        'duration': 'Forever',
        'models': 3,
        'storage': '1 GB',
        'compute': '5 hours/month',
        'features': ['Basic Model Training', 'Model Upload', 'Basic Dashboard'],
        'color': '#6c757d'
    },
    SubscriptionTier.DEVELOPER: {
        'name': 'Developer',
        'price': 15,
        'duration': '3 months',
        'models': 15,
        'storage': '25 GB',
        'compute': '100 hours/month',
        'features': ['AutoML', 'Advanced Monitoring', 'API Access', 'Team Collaboration', 'Email Support'],
        'color': '#007bff'
    },
    SubscriptionTier.ELITE: {
        'name': 'Elite Developer',
        'price': 55,
        'duration': '12 months',
        'models': 100,
        'storage': '500 GB',
        'compute': '1000 hours/month',
        'features': ['All Features', 'Priority Support', 'Custom Deployment', 'White Label', 'Phone Support'],
        'color': '#28a745'
    }
}

def show_subscription_page():
    st.title("⚡ ZipIt Subscription Plans")
    st.markdown("Choose the perfect plan for your ML journey")
    
    # Current user info
    if 'user' in st.session_state:
        user = st.session_state.user
        current_tier = user.subscription_tier
        
        # Show current plan
        st.info(f"Current Plan: **{PRICING_PLANS[current_tier]['name']}**")
        
        if current_tier != SubscriptionTier.FREE:
            if user.subscription_expires:
                days_left = (user.subscription_expires - datetime.utcnow()).days
                if days_left > 0:
                    st.success(f"✅ Active until {user.subscription_expires.strftime('%B %d, %Y')} ({days_left} days left)")
                else:
                    st.error("❌ Subscription expired - Please renew to continue using premium features")
    
    # Pricing cards
    cols = st.columns(3)
    
    for i, (tier, plan) in enumerate(PRICING_PLANS.items()):
        with cols[i]:
            # Card styling
            is_popular = tier == SubscriptionTier.DEVELOPER
            border_color = plan['color']
            
            st.markdown(f"""
            <div style="
                border: 2px solid {border_color};
                border-radius: 10px;
                padding: 20px;
                margin: 10px 0;
                background: {'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' if is_popular else 'white'};
                color: {'white' if is_popular else 'black'};
                position: relative;
            ">
                {'<div style="position: absolute; top: -10px; right: 10px; background: #ff6b6b; color: white; padding: 5px 10px; border-radius: 15px; font-size: 12px;">POPULAR</div>' if is_popular else ''}
                
                <h3 style="color: {plan['color'] if not is_popular else 'white'}; margin-top: 0;">
                    {plan['name']}
                </h3>
                
                <div style="font-size: 2.5em; font-weight: bold; margin: 15px 0;">
                    {'FREE' if plan['price'] == 0 else f"${plan['price']}"}
                </div>
                
                <div style="margin-bottom: 20px; opacity: 0.8;">
                    {plan['duration']}
                </div>
                
                <div style="text-align: left; margin: 20px 0;">
                    <div>📊 <strong>{plan['models']}</strong> ML Models</div>
                    <div>💾 <strong>{plan['storage']}</strong> Storage</div>
                    <div>⚡ <strong>{plan['compute']}</strong> Compute</div>
                </div>
                
                <div style="text-align: left; margin: 20px 0;">
                    <strong>Features:</strong><br>
                    {'<br>'.join([f"✅ {feature}" for feature in plan['features']])}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Action button
            if 'user' in st.session_state:
                current_tier = st.session_state.user.subscription_tier
                
                if tier == current_tier:
                    st.success("✅ Current Plan")
                elif tier == SubscriptionTier.FREE:
                    if st.button(f"Downgrade to Free", key=f"btn_{tier.value}"):
                        downgrade_subscription(st.session_state.user.id)
                        st.rerun()
                else:
                    if st.button(f"Upgrade to {plan['name']}", key=f"btn_{tier.value}", type="primary" if is_popular else "secondary"):
                        show_payment_form(tier, plan)
            else:
                st.button("Sign Up Required", disabled=True)

def show_payment_form(tier: SubscriptionTier, plan: dict):
    st.subheader(f"💳 Upgrade to {plan['name']}")
    
    with st.form(f"payment_form_{tier.value}"):
        st.write(f"**Total: ${plan['price']} for {plan['duration']}**")
        
        payment_method = st.selectbox("Payment Method", ["UPI (India)", "Credit Card", "PayPal", "Bank Transfer"])
        
        if payment_method == "UPI (India)":
            st.info("🇮🇳 Pay via UPI - Instant & Secure")
            st.code("UPI ID: 8660735943@ybl")
            st.write("**Instructions:**")
            st.write("1. Open any UPI app (GPay, PhonePe, Paytm)")
            st.write("2. Send payment to: **8660735943@ybl**")
            st.write(f"3. Amount: ₹{int(plan['price'] * 83)} (${plan['price']} USD)")
            st.write("4. Add note: Your username + ZipIt subscription")
            
            transaction_id = st.text_input("UPI Transaction ID", placeholder="Enter 12-digit transaction ID")
            
        elif payment_method == "Credit Card":
            col1, col2 = st.columns(2)
            with col1:
                card_number = st.text_input("Card Number", placeholder="1234 5678 9012 3456")
            with col2:
                expiry = st.text_input("MM/YY", placeholder="12/25")
            
            col3, col4 = st.columns(2)
            with col3:
                cvv = st.text_input("CVV", placeholder="123", type="password")
            with col4:
                name = st.text_input("Cardholder Name")
                
        elif payment_method == "PayPal":
            st.info("💙 PayPal - Secure International Payments")
            paypal_email = st.text_input("PayPal Email", placeholder="your@email.com")
            st.write("You will be redirected to PayPal to complete payment")
            
        elif payment_method == "Bank Transfer":
            st.info("🏦 Bank Transfer - For Enterprise Customers")
            st.write("**Bank Details:**")
            st.code("""
Account Name: ZipIt Technologies
Account Number: [Will be provided after form submission]
IFSC Code: [Will be provided]
Bank: [Will be provided]
            """)
            reference_number = st.text_input("Reference Number (if already transferred)")
        
        terms = st.checkbox("I agree to the Terms of Service and Privacy Policy")
        
        submit_text = {
            "UPI (India)": "Verify UPI Payment",
            "Credit Card": "Process Payment", 
            "PayPal": "Pay with PayPal",
            "Bank Transfer": "Submit Transfer Details"
        }
        
        if st.form_submit_button(submit_text[payment_method], type="primary"):
            if terms:
                if payment_method == "UPI (India)" and transaction_id:
                    process_upi_payment(st.session_state.user.id, tier, plan, transaction_id)
                elif payment_method == "Credit Card":
                    process_payment(st.session_state.user.id, tier, plan, payment_method)
                elif payment_method == "PayPal":
                    process_paypal_payment(st.session_state.user.id, tier, plan, paypal_email)
                elif payment_method == "Bank Transfer":
                    process_bank_transfer(st.session_state.user.id, tier, plan)
                else:
                    st.error("Please fill all required fields")
            else:
                st.error("Please accept the terms and conditions")

def process_payment(user_id: int, tier: SubscriptionTier, plan: dict, payment_method: str):
    """Process subscription payment"""
    db = next(get_db())
    
    try:
        # Create payment record
        payment = Payment(
            user_id=user_id,
            amount=plan['price'],
            tier=tier,
            duration_months=3 if tier == SubscriptionTier.DEVELOPER else 12,
            payment_method=payment_method.lower().replace(" ", "_"),
            transaction_id=f"txn_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}",
            status="completed"
        )
        db.add(payment)
        
        # Update user subscription
        user = db.query(User).filter(User.id == user_id).first()
        user.subscription_tier = tier
        
        if tier == SubscriptionTier.DEVELOPER:
            user.subscription_expires = datetime.utcnow() + timedelta(days=90)
        elif tier == SubscriptionTier.ELITE:
            user.subscription_expires = datetime.utcnow() + timedelta(days=365)
        
        user.subscription_active = True
        
        db.commit()
        
        # Update session state
        st.session_state.user = user
        
    except Exception as e:
        db.rollback()
        st.error(f"Payment failed: {str(e)}")
    finally:
        db.close()

def downgrade_subscription(user_id: int):
    """Downgrade to free tier"""
    db = next(get_db())
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        user.subscription_tier = SubscriptionTier.FREE
        user.subscription_expires = None
        user.subscription_active = True
        
        db.commit()
        st.session_state.user = user
        
    except Exception as e:
        db.rollback()
        st.error(f"Downgrade failed: {str(e)}")
    finally:
        db.close()

def check_feature_access(user: User, feature: str) -> bool:
    """Check if user has access to specific feature"""
    return user.has_feature(feature)

def show_upgrade_prompt(feature_name: str):
    """Show upgrade prompt for premium features"""
    st.warning(f"🔒 **{feature_name}** is a premium feature")
    st.info("Upgrade to Developer or Elite plan to unlock this feature")
    
    if st.button("View Pricing Plans"):
        st.session_state.page = "subscription"
        st.rerun()

def process_upi_payment(user_id: int, tier: SubscriptionTier, plan: dict, transaction_id: str):
    """Process UPI payment verification"""
    db = next(get_db())
    
    try:
        # Create payment record for manual verification
        payment = Payment(
            user_id=user_id,
            amount=plan['price'],
            tier=tier,
            duration_months=3 if tier == SubscriptionTier.DEVELOPER else 12,
            payment_method="upi",
            transaction_id=transaction_id,
            status="pending_verification"
        )
        db.add(payment)
        db.commit()
        
        st.success("🔄 UPI payment submitted for verification!")
        st.info("Your subscription will be activated within 24 hours after payment verification.")
        st.info("You will receive an email confirmation once verified.")
        
    except Exception as e:
        db.rollback()
        st.error(f"Payment submission failed: {str(e)}")
    finally:
        db.close()

def process_paypal_payment(user_id: int, tier: SubscriptionTier, plan: dict, email: str):
    """Process PayPal payment"""
    db = next(get_db())
    
    try:
        payment = Payment(
            user_id=user_id,
            amount=plan['price'],
            tier=tier,
            duration_months=3 if tier == SubscriptionTier.DEVELOPER else 12,
            payment_method="paypal",
            transaction_id=f"pp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}",
            status="pending"
        )
        db.add(payment)
        db.commit()
        
        st.success("🔄 Redirecting to PayPal...")
        st.info("You will be redirected to PayPal to complete your payment.")
        
    except Exception as e:
        db.rollback()
        st.error(f"PayPal setup failed: {str(e)}")
    finally:
        db.close()

def process_bank_transfer(user_id: int, tier: SubscriptionTier, plan: dict):
    """Process bank transfer request"""
    db = next(get_db())
    
    try:
        payment = Payment(
            user_id=user_id,
            amount=plan['price'],
            tier=tier,
            duration_months=3 if tier == SubscriptionTier.DEVELOPER else 12,
            payment_method="bank_transfer",
            transaction_id=f"bt_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}",
            status="pending_bank_details"
        )
        db.add(payment)
        db.commit()
        
        st.success("🏦 Bank transfer request submitted!")
        st.info("Bank details will be sent to your registered email within 2 hours.")
        st.info("Please complete the transfer and notify us with the reference number.")
        
    except Exception as e:
        db.rollback()
        st.error(f"Bank transfer setup failed: {str(e)}")
    finally:
        db.close()