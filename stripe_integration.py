import os
import stripe
from flask import url_for, request

# Initialize Stripe with secret key
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'default_key')

def get_domain():
    """Get the current domain for Stripe redirects"""
    # Handle different deployment environments
    if os.environ.get('REPLIT_DEPLOYMENT'):
        return os.environ.get('REPLIT_DEV_DOMAIN')
    elif os.environ.get('REPLIT_DOMAINS'):
        return os.environ.get('REPLIT_DOMAINS').split(',')[0]
    else:
        # Local development fallback
        return request.host

def create_checkout_session(price_id, success_path='/success', cancel_path='/cancel'):
    """Create a Stripe checkout session"""
    try:
        domain = get_domain()
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': price_id,
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=f'https://{domain}{success_path}',
            cancel_url=f'https://{domain}{cancel_path}',
            automatic_tax={'enabled': True},
        )
        return checkout_session.url
    except Exception as e:
        print(f"Stripe checkout error: {str(e)}")
        return None

def create_subscription_session(price_id, success_path='/success', cancel_path='/cancel'):
    """Create a Stripe subscription checkout session"""
    try:
        domain = get_domain()
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': price_id,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=f'https://{domain}{success_path}',
            cancel_url=f'https://{domain}{cancel_path}',
            automatic_tax={'enabled': True},
        )
        return checkout_session.url
    except Exception as e:
        print(f"Stripe subscription error: {str(e)}")
        return None

def create_price(product_name, amount_cents, currency='usd', recurring=None):
    """Create a Stripe price object"""
    try:
        # Create product first
        product = stripe.Product.create(name=product_name)
        
        price_data = {
            'unit_amount': amount_cents,
            'currency': currency,
            'product': product.id,
        }
        
        if recurring:
            price_data['recurring'] = recurring
        
        price = stripe.Price.create(**price_data)
        return price.id
    except Exception as e:
        print(f"Stripe price creation error: {str(e)}")
        return None
