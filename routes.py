import os
import json
import uuid
import csv
import io
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, jsonify, session, send_file
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import stripe
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from app import app, db
from models import Service, BidRequest, Product, TrainingVideo, Admin, ChatConversation, Testimonial, ObjectDetectionRecord, ElectricalPart
from forms import BidRequestForm, AdminLoginForm, ProductForm, TrainingVideoForm, ObjectDetectionForm
from ai_assistant import ToolieAI
from yolo_detect import ElectricalYOLODetector, toolie_summarize
from worker_routes import register_worker_routes

# Register worker dispatch routes
register_worker_routes(app)

# Initialize Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_your_stripe_key')
YOUR_DOMAIN = os.environ.get('REPLIT_DEV_DOMAIN', 'localhost:5000')

# Initialize Toolie AI and YOLOv8 Detector
toolie = ToolieAI()
detector = ElectricalYOLODetector()

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}  # JPG/PNG only for object detection
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
    
    # Pre-fill form with data from object detection if available
    if request.method == 'GET' and 'prefill_bid_request' in session:
        prefill_data = session.pop('prefill_bid_request')
        form.description.data = prefill_data.get('description', '')
        form.job_type.data = prefill_data.get('job_type', '')
    
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
    
    return redirect(checkout_session.url)

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

# Object Detection Routes
@app.route('/object-detect')
def object_detect():
    """Object detection landing page"""
    form = ObjectDetectionForm()
    return render_template('object_detect/index.html', form=form)

@app.route('/object-detect/upload', methods=['POST'])
def upload_and_detect():
    """Handle image upload and perform object detection"""
    form = ObjectDetectionForm()
    
    if form.validate_on_submit():
        # Save uploaded image
        image_file = form.image.data
        comment = form.comment.data or ""
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"upload_{timestamp}_{unique_id}.jpg"
        
        # Save to uploads directory
        upload_path = os.path.join('static/uploads', filename)
        image_file.save(upload_path)
        
        # Process image with YOLOv8-style object detection
        try:
            # Validate file size (10MB max)
            image_file.seek(0, 2)  # Seek to end
            file_size = image_file.tell()
            image_file.seek(0)  # Reset to beginning
            
            if file_size > 10 * 1024 * 1024:  # 10MB limit
                flash('File size must be less than 10MB', 'error')
                return redirect(url_for('object_detect'))
            
            # Perform YOLOv8-style object detection
            detected_objects = detector.detect_objects(upload_path)
            
            # Generate output image with bounding boxes
            output_filename = f"detected_{filename}"
            output_path = os.path.join('static/uploads', output_filename)
            detection_success = detector.save_detection_image(upload_path, output_path)
            
            # Generate Toolie AI summary
            toolie_summary = toolie_summarize(detected_objects)
            
            # Save detection record to database
            detection_record = ObjectDetectionRecord(
                original_filename=image_file.filename,
                uploaded_image_path=upload_path,
                detected_image_path=output_path if detection_success else upload_path,
                detected_objects=json.dumps(detected_objects),
                user_comment=comment,
                toolie_summary=toolie_summary
            )
            db.session.add(detection_record)
            db.session.commit()
            
            flash(f'Successfully detected {len(detected_objects)} electrical components!', 'success')
            return redirect(url_for('object_detect_results', record_id=detection_record.id))
            
        except Exception as e:
            flash(f'Error processing image: {str(e)}', 'error')
            return redirect(url_for('object_detect'))
    
    # Form validation failed
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{field}: {error}', 'error')
    
    return redirect(url_for('object_detect'))

@app.route('/object-detect/export/<int:record_id>/<format>')
def export_detection_results(record_id, format):
    """Export detection results as CSV or PDF"""
    record = ObjectDetectionRecord.query.get_or_404(record_id)
    detected_objects = json.loads(record.detected_objects) if record.detected_objects else []
    component_matches = detector.get_component_matches(detected_objects)
    
    if format == 'csv':
        # Create CSV export
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(['Component Type', 'Part Number', 'Vendor', 'Description', 'Confidence'])
        
        # Write data
        for match in component_matches:
            part_numbers = ', '.join(match.get('part_numbers', []))
            writer.writerow([
                match.get('name', ''),
                part_numbers,
                match.get('vendor', ''),
                match.get('description', ''),
                f"{match.get('confidence', 0):.0%}"
            ])
        
        output.seek(0)
        
        # Create response
        csv_data = io.BytesIO()
        csv_data.write(output.getvalue().encode('utf-8'))
        csv_data.seek(0)
        
        return send_file(csv_data, 
                        mimetype='text/csv',
                        as_attachment=True,
                        download_name=f'electrical_components_{record_id}.csv')
    
    elif format == 'pdf':
        # Create PDF export
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Title
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, height - 50, "Electrical Components Detection Report")
        
        # Date and file info
        p.setFont("Helvetica", 12)
        p.drawString(50, height - 80, f"Date: {record.created_at.strftime('%Y-%m-%d %H:%M')}")
        p.drawString(50, height - 100, f"Original File: {record.original_filename}")
        
        if record.user_comment:
            p.drawString(50, height - 120, f"Comment: {record.user_comment}")
        
        # Components table
        y_position = height - 160
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y_position, "Detected Components:")
        
        y_position -= 30
        p.setFont("Helvetica", 10)
        
        for match in component_matches:
            if y_position < 100:  # Start new page if needed
                p.showPage()
                y_position = height - 50
            
            p.drawString(50, y_position, f"• {match.get('name', '')}")
            y_position -= 15
            p.drawString(70, y_position, f"Part Numbers: {', '.join(match.get('part_numbers', []))}")
            y_position -= 15
            p.drawString(70, y_position, f"Vendor: {match.get('vendor', '')}")
            y_position -= 15
            p.drawString(70, y_position, f"Confidence: {match.get('confidence', 0):.0%}")
            y_position -= 25
        
        # Toolie summary
        if record.toolie_summary:
            if y_position < 150:
                p.showPage()
                y_position = height - 50
            
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, y_position, "Toolie AI Analysis:")
            y_position -= 20
            
            p.setFont("Helvetica", 10)
            # Wrap text for summary
            summary_lines = record.toolie_summary.split('. ')
            for line in summary_lines:
                if y_position < 50:
                    p.showPage()
                    y_position = height - 50
                p.drawString(50, y_position, line)
                y_position -= 15
        
        p.save()
        buffer.seek(0)
        
        return send_file(buffer,
                        mimetype='application/pdf',
                        as_attachment=True,
                        download_name=f'electrical_components_{record_id}.pdf')
    
    else:
        flash('Invalid export format', 'error')
        return redirect(url_for('object_detect'))

@app.route('/object-detect/quote-request/<int:record_id>')
def quote_request_from_detection(record_id):
    """Pre-fill bid request form with detected components"""
    record = ObjectDetectionRecord.query.get_or_404(record_id)
    detected_objects = json.loads(record.detected_objects) if record.detected_objects else []
    component_matches = detector.get_component_matches(detected_objects)
    
    # Create description with detected components
    components_list = [match.get('name', '') for match in component_matches]
    description = f"Based on object detection analysis:\n\nDetected components: {', '.join(components_list)}\n\n"
    if record.user_comment:
        description += f"Additional notes: {record.user_comment}\n\n"
    if record.toolie_summary:
        description += f"AI Analysis: {record.toolie_summary}"
    
    # Pre-fill form data in session
    session['prefill_bid_request'] = {
        'description': description,
        'job_type': 'other'  # Default since it's from detection
    }
    
    flash('Bid request form pre-filled with detected components!', 'info')
    return redirect(url_for('bid_request'))

@app.route('/object-detect/history')
def detection_history():
    """View detection history"""
    records = ObjectDetectionRecord.query.order_by(ObjectDetectionRecord.created_at.desc()).limit(20).all()
    return render_template('object_detect/history.html', records=records)
