"""
Worker dispatch system routes for Kynetik Electric
"""
import os
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

from firebase_service import firebase_service
from sms_service import sms_service
from worker_auth import authenticate_worker, Worker, admin_required, worker_required
from worker_forms import WorkerLoginForm, ServiceCallForm, JobStatusUpdateForm, FileUploadForm


def register_worker_routes(app):
    """Register all worker-related routes"""
    
    @app.route('/worker/login', methods=['GET', 'POST'])
    def worker_login():
        """Worker login page"""
        form = WorkerLoginForm()
        if form.validate_on_submit():
            worker = authenticate_worker(form.email.data, form.password.data)
            if worker:
                login_user(worker, remember=True)
                flash(f'Welcome back, {worker.name}!', 'success')
                
                # Redirect based on role
                if worker.is_admin():
                    return redirect(url_for('admin_dispatch'))
                else:
                    return redirect(url_for('worker_dashboard'))
            else:
                flash('Invalid email or password.', 'error')
        
        return render_template('worker/login.html', form=form)
    
    @app.route('/worker/logout')
    @worker_required
    def worker_logout():
        """Worker logout"""
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('worker_login'))
    
    @app.route('/admin/dispatch')
    @admin_required
    def admin_dispatch():
        """Admin dispatch dashboard"""
        service_calls = firebase_service.get_service_calls()
        workers = firebase_service.get_workers()
        
        return render_template('worker/admin_dispatch.html', 
                             service_calls=service_calls, 
                             workers=workers)
    
    @app.route('/admin/create-job', methods=['GET', 'POST'])
    @admin_required
    def create_service_call():
        """Create new service call"""
        form = ServiceCallForm()
        
        # Populate worker choices
        workers = firebase_service.get_workers()
        form.assigned_to.choices = [(w['id'], w['name']) for w in workers]
        
        if form.validate_on_submit():
            # Handle file uploads
            uploaded_files = []
            if form.attachments.data:
                for file in form.attachments.data:
                    if file and file.filename:
                        filename = secure_filename(file.filename)
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        file.save(filepath)
                        uploaded_files.append({
                            'filename': filename,
                            'path': filepath
                        })
            
            # Create service call
            call_data = {
                'title': form.title.data,
                'customer_name': form.customer_name.data,
                'location': form.location.data,
                'description': form.description.data,
                'priority': form.priority.data,
                'assigned_to': form.assigned_to.data,
                'attachments': uploaded_files
            }
            
            call_id = firebase_service.create_service_call(call_data)
            
            # Get assigned worker details
            assigned_worker = firebase_service.get_worker_by_id(form.assigned_to.data)
            
            # Send SMS notification
            if assigned_worker and assigned_worker.get('phone'):
                sms_service.send_job_assignment_sms(
                    worker_phone=assigned_worker['phone'],
                    job_title=form.title.data or "New Job",
                    location=form.location.data or "Location TBD",
                    job_id=call_id
                )
            
            flash(f'Service call created and assigned to {assigned_worker["name"] if assigned_worker else "worker"}!', 'success')
            return redirect(url_for('admin_dispatch'))
        
        return render_template('worker/create_job.html', form=form)
    
    @app.route('/dashboard')
    @worker_required
    def worker_dashboard():
        """Worker dashboard showing assigned jobs"""
        if current_user.is_admin():
            return redirect(url_for('admin_dispatch'))
        
        # Get jobs assigned to current worker
        service_calls = firebase_service.get_service_calls(worker_id=current_user.id)
        
        return render_template('worker/dashboard.html', service_calls=service_calls)
    
    @app.route('/job/<call_id>')
    @worker_required
    def job_detail(call_id):
        """Job detail page"""
        service_calls = firebase_service.get_service_calls()
        job = next((call for call in service_calls if call['id'] == call_id), None)
        
        if not job:
            flash('Job not found.', 'error')
            return redirect(url_for('worker_dashboard'))
        
        # Check if user has access to this job
        if not current_user.is_admin() and job['assigned_to'] != current_user.id:
            flash('Access denied.', 'error')
            return redirect(url_for('worker_dashboard'))
        
        uploads = firebase_service.get_uploads_for_call(call_id)
        status_form = JobStatusUpdateForm()
        upload_form = FileUploadForm()
        
        return render_template('worker/job_detail.html', 
                             job=job, 
                             uploads=uploads,
                             status_form=status_form,
                             upload_form=upload_form)
    
    @app.route('/job/update-status', methods=['POST'])
    @worker_required
    def update_job_status():
        """Update job status"""
        form = JobStatusUpdateForm()
        
        if form.validate_on_submit():
            success = firebase_service.update_service_call_status(
                call_id=form.call_id.data or "",
                status=form.status.data or "open",
                notes=form.notes.data or ""
            )
            
            if success:
                flash('Job status updated successfully!', 'success')
            else:
                flash('Failed to update job status.', 'error')
        
        return redirect(url_for('job_detail', call_id=form.call_id.data))
    
    @app.route('/job/upload', methods=['POST'])
    @worker_required
    def upload_job_files():
        """Upload files for a job"""
        form = FileUploadForm()
        
        if form.validate_on_submit():
            uploaded_files = []
            
            if form.files.data:
                for file in form.files.data:
                    if file and file.filename:
                        filename = secure_filename(file.filename)
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        file.save(filepath)
                        
                        # Record upload in Firebase
                        upload_data = {
                            'filename': filename,
                            'file_path': filepath,
                            'file_type': file.content_type,
                            'uploaded_by': current_user.id,
                            'note': form.note.data
                        }
                        
                        firebase_service.upload_file(form.call_id.data or "", upload_data)
                        uploaded_files.append(filename)
            
            if uploaded_files:
                flash(f'Uploaded {len(uploaded_files)} file(s) successfully!', 'success')
            else:
                flash('No files were uploaded.', 'warning')
        
        return redirect(url_for('job_detail', call_id=form.call_id.data))
    
    @app.route('/api/firebase-config')
    def firebase_config():
        """API endpoint to get Firebase configuration"""
        return jsonify(firebase_service.get_firebase_config())