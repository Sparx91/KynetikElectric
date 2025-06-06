#!/usr/bin/env python3
"""
Script to create Stripe products and prices for the Kynetik Electric store
"""
import os
import stripe
from app import app, db
from models import Product

# Set up Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

def create_stripe_products():
    """Create Stripe products and add them to the database"""
    
    products_to_create = [
        {
            'name': 'Electrical Safety Checklist',
            'description': 'Comprehensive safety checklist for electrical work. Includes pre-work inspection, PPE requirements, and hazard identification protocols.',
            'price': 19.99,
            'product_type': 'digital'
        },
        {
            'name': 'Industrial Wiring Guide',
            'description': 'Complete guide to industrial electrical installations. Covers conduit systems, motor controls, and panel layouts with detailed diagrams.',
            'price': 49.99,
            'product_type': 'digital'
        },
        {
            'name': 'Code Compliance Forms Pack',
            'description': 'Essential forms for electrical inspections and code compliance. Includes inspection checklists, test reports, and documentation templates.',
            'price': 29.99,
            'product_type': 'digital'
        },
        {
            'name': 'Troubleshooting Manual',
            'description': 'Advanced electrical troubleshooting techniques and diagnostic procedures. Step-by-step guide for common electrical problems.',
            'price': 39.99,
            'product_type': 'digital'
        }
    ]
    
    with app.app_context():
        for product_data in products_to_create:
            try:
                # Create Stripe product
                stripe_product = stripe.Product.create(
                    name=product_data['name'],
                    description=product_data['description'],
                )
                
                # Create Stripe price
                stripe_price = stripe.Price.create(
                    product=stripe_product.id,
                    unit_amount=int(product_data['price'] * 100),  # Convert to cents
                    currency='usd',
                )
                
                # Create database product
                db_product = Product(
                    name=product_data['name'],
                    description=product_data['description'],
                    price=product_data['price'],
                    product_type=product_data['product_type'],
                    stripe_price_id=stripe_price.id,
                    is_active=True
                )
                
                db.session.add(db_product)
                print(f"Created product: {product_data['name']} with Stripe price ID: {stripe_price.id}")
                
            except Exception as e:
                print(f"Error creating product {product_data['name']}: {str(e)}")
        
        try:
            db.session.commit()
            print("All products saved to database successfully!")
        except Exception as e:
            print(f"Error saving to database: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    create_stripe_products()