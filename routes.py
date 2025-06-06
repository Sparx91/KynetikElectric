import os
import json
import uuid
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import stripe

from app import app, db
from models import Service, BidRequest, Product, TrainingVideo, Admin, ChatConversation, Testimonial
from forms import BidRequestForm, AdminLoginForm, ProductForm, TrainingVideoForm
from ai_assistant import ToolieAI

# Initialize Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_your_stripe_key')
YOUR_DOMAIN = os.environ.get('REPLIT_DEV_DOMAIN', 'localhost:5000')

# Initialize Toolie AI
toolie = ToolieAI()

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    services = Service.query.limit(6).all()
    testimonials = Testimonial.query.filter_by(is_featured=True).limit(3).all()
    return render_template('index.html', services=services, testimonials=testimonials)

@app.route('/services')
def services():
    all_services = Service.query.all()
    return render_template('services.html', services=all_services)

@app.route('/bid-request', methods=['GET', 'POST'])
def bid_request():
    form = BidRequestForm()
    
    if form.validate_on_submit():
        # Handle file uploads
        uploaded_files = []
        if form.files.data:
            for file in form.files.data:
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{filename}")
                    file.save(file_path)
                    uploaded_files.append(file_path)
        
        # Create bid request
        bid = BidRequest(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            job_type=form.job_type.data,
            project_size=form.project_size.data,
            location=form.location.data,
            description=form.description.data,
            uploaded_files=json.dumps(uploaded_files)
        )
        
        db.session.add(bid)
        db.session.commit()
        
        flash('Your bid request has been submitted successfully! We will contact you within 24 hours.', 'success')
        return redirect(url_for('index'))
    
    return render_template('bid_request.html', form=form)

@app.route('/training')
def training():
    free_videos = TrainingVideo.query.filter_by(is_premium=False).all()
    premium_videos = TrainingVideo.query.filter_by(is_premium=True).all()
    return render_template('training.html', free_videos=free_videos, premium_videos=premium_videos)

@app.route('/store')
def store():
    digital_products = Product.query.filter_by(product_type='digital', is_active=True).all()
    physical_products = Product.query.filter_by(product_type='physical', is_active=True).all()
    return render_template('store.html', digital_products=digital_products, physical_products=physical_products)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product.html', product=product)

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        product_id = request.form.get('product_id')
        product = Product.query.get_or_404(product_id)
        
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': product.stripe_price_id,
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=f'https://{YOUR_DOMAIN}/checkout-success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'https://{YOUR_DOMAIN}/checkout-cancel',
            automatic_tax={'enabled': False},
        )
    except Exception as e:
        flash(f'Error creating checkout session: {str(e)}', 'error')
        return redirect(url_for('store'))
    
    return redirect(checkout_session.url, code=303)

@app.route('/checkout-success')
def checkout_success():
    session_id = request.args.get('session_id')
    return render_template('checkout_success.html', session_id=session_id)

@app.route('/checkout-cancel')
def checkout_cancel():
    return render_template('checkout_cancel.html')

@app.route('/quote-estimator', methods=['GET', 'POST'])
def quote_estimator():
    if request.method == 'POST':
        project_details = {
            'job_type': request.form.get('job_type'),
            'project_size': request.form.get('project_size'),
            'description': request.form.get('description'),
            'location': request.form.get('location'),
            'square_footage': request.form.get('square_footage'),
            'device_count': request.form.get('device_count')
        }
        
        estimate = toolie.generate_quick_quote(project_details)
        return render_template('quote_estimator.html', estimate=estimate, project_details=project_details)
    
    return render_template('quote_estimator.html')

@app.route('/troubleshooting', methods=['GET', 'POST'])
def troubleshooting():
    if request.method == 'POST':
        issue_description = request.form.get('issue_description')
        symptoms = request.form.getlist('symptoms')
        
        analysis = toolie.analyze_troubleshooting_issue(issue_description, symptoms)
        return render_template('troubleshooting.html', analysis=analysis, issue_description=issue_description)
    
    return render_template('troubleshooting.html')

@app.route('/testimonials')
def testimonials():
    all_testimonials = Testimonial.query.order_by(Testimonial.created_at.desc()).all()
    return render_template('testimonials.html', testimonials=all_testimonials)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message')
    context = data.get('context', 'customer-facing')
    
    # Get or create session ID
    if 'chat_session' not in session:
        session['chat_session'] = str(uuid.uuid4())
    
    session_id = session['chat_session']
    
    # Get conversation history
    history = ChatConversation.query.filter_by(session_id=session_id).order_by(ChatConversation.created_at.desc()).limit(5).all()
    
    # Get AI response
    response = toolie.get_response(message, context, [{"message": h.message, "response": h.response} for h in history])
    
    # Save conversation
    conversation = ChatConversation(
        session_id=session_id,
        message=message,
        response=response,
        context=context
    )
    db.session.add(conversation)
    db.session.commit()
    
    return jsonify({'response': response})

# Admin routes
@app.route('/admin')
def admin_dashboard():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    recent_bids = BidRequest.query.order_by(BidRequest.created_at.desc()).limit(5).all()
    total_products = Product.query.count()
    total_bids = BidRequest.query.count()
    
    return render_template('admin/dashboard.html', 
                         recent_bids=recent_bids, 
                         total_products=total_products, 
                         total_bids=total_bids)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    form = AdminLoginForm()
    
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        
        if admin and check_password_hash(admin.password_hash, form.password.data):
            session['admin_logged_in'] = True
            session['admin_id'] = admin.id
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin/login.html', form=form)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_id', None)
    return redirect(url_for('index'))

@app.route('/admin/products')
def admin_products():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    products = Product.query.all()
    return render_template('admin/products.html', products=products)

@app.route('/admin/bids')
def admin_bids():
    if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
    
    bids = BidRequest.query.order_by(BidRequest.created_at.desc()).all()
    return render_template('admin/bids.html', bids=bids)

# Initialize default data
@app.before_first_request
def create_default_data():
    if Service.query.count() == 0:
        default_services = [
            Service(name="Industrial Installations", description="Complete electrical installations for industrial facilities", icon="fas fa-industry", category="industrial"),
            Service(name="3D LiDAR Scanning", description="Advanced 3D scanning for electrical planning and documentation", icon="fas fa-camera", category="technology"),
            Service(name="Electrical Troubleshooting", description="Expert diagnosis and repair of electrical issues", icon="fas fa-tools", category="repair"),
            Service(name="Panel Upgrades", description="Electrical panel modernization and upgrades", icon="fas fa-th-large", category="upgrade"),
            Service(name="Emergency Services", description="24/7 emergency electrical services", icon="fas fa-exclamation-triangle", category="emergency"),
            Service(name="Maintenance Contracts", description="Ongoing electrical maintenance and support", icon="fas fa-calendar-check", category="maintenance")
        ]
        
        for service in default_services:
            db.session.add(service)
    
    # Create default admin user if none exists
    if Admin.query.count() == 0:
        admin = Admin(
            username='admin',
            email='admin@kynetikelectric.com',
            password_hash=generate_password_hash('admin123')
        )
        db.session.add(admin)
    
    # Create sample testimonials
    if Testimonial.query.count() == 0:
        testimonials = [
            Testimonial(client_name="ABC Manufacturing", content="Kynetik Electric completed our facility upgrade on time and under budget. Exceptional work!", rating=5, project_type="Industrial Installation", is_featured=True),
            Testimonial(client_name="Tech Solutions Inc", content="The 3D LiDAR scanning service was incredibly detailed and helped us plan our expansion perfectly.", rating=5, project_type="3D LiDAR Scan", is_featured=True),
            Testimonial(client_name="Downtown Office Complex", content="Fast, professional emergency service. They had our power restored in under 2 hours.", rating=5, project_type="Emergency Service", is_featured=True)
        ]
        
        for testimonial in testimonials:
            db.session.add(testimonial)
    
    db.session.commit()
