from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import psutil
import os
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from functools import wraps
import platform
from user_agents import parse

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///monitoring.db'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ==================== DATABASE MODELS ====================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    login_history = db.relationship('LoginHistory', backref='user', lazy=True, cascade='all, delete-orphan')
    system_data = db.relationship('SystemData', backref='user', lazy=True, cascade='all, delete-orphan')

class LoginHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    login_time = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(50))
    browser = db.Column(db.String(200))

class SystemData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cpu = db.Column(db.Float)
    ram = db.Column(db.Float)
    disk = db.Column(db.Float)
    health_score = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# ==================== HELPER FUNCTIONS ====================

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required!', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_system_health():
    """Get current system metrics"""
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    health_score = int((100 - ((cpu + ram + disk) / 3)))
    
    return {
        "cpu": round(cpu, 2),
        "ram": round(ram, 2),
        "disk": round(disk, 2),
        "health_score": health_score
    }

def send_email(recipient_email, subject, html_body):
    """Send email notification"""
    try:
        sender_email = os.environ.get('EMAIL_ADDRESS')
        sender_password = os.environ.get('EMAIL_PASSWORD')
        
        if not sender_email or not sender_password:
            print("Email credentials not configured")
            return False
        
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = recipient_email
        
        part = MIMEText(html_body, "html")
        message.attach(part)
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def get_user_browser_info():
    """Extract browser and OS information from user agent"""
    user_agent = parse(request.headers.get('User-Agent', ''))
    browser = f"{user_agent.browser.family} {user_agent.browser.version_string}"
    os_info = f"{user_agent.os.family} {user_agent.os.version_string}"
    return f"{browser} on {os_info}"

def get_user_ip():
    """Get client IP address"""
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        return request.environ.get('HTTP_X_FORWARDED_FOR').split(',')[0]
    return request.remote_addr

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not email or not password:
            flash('All fields are required!', 'danger')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        # Send welcome email to admin
        admin_email = os.environ.get('ADMIN_EMAIL')
        if admin_email:
            email_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; background-color: #f5f5f5;">
                    <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                        <h2 style="color: #003399;">🎉 New User Registration</h2>
                        <p>A new user has registered on the Smart System Monitoring Dashboard:</p>
                        <div style="background-color: #f5f7ff; padding: 15px; border-radius: 5px; margin: 15px 0;">
                            <p><strong>Username:</strong> {username}</p>
                            <p><strong>Email:</strong> {email}</p>
                            <p><strong>Registration Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                        </div>
                        <p><a href="#" style="background-color: #003399; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none;">View Admin Panel</a></p>
                    </div>
                </body>
            </html>
            """
            send_email(admin_email, f"New User Registration: {username}", email_body)
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            
            # Record login
            ip_address = get_user_ip()
            browser_info = get_user_browser_info()
            login_record = LoginHistory(user_id=user.id, ip_address=ip_address, browser=browser_info)
            db.session.add(login_record)
            db.session.commit()
            
            # Send email to admin
            admin = User.query.filter_by(is_admin=True).first()
            if admin:
                email_body = f"""
                <html>
                    <body style="font-family: Arial, sans-serif; background-color: #f5f5f5;">
                        <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                            <h2 style="color: #003399;">👤 User Login Detected</h2>
                            <div style="background-color: #f5f7ff; padding: 15px; border-radius: 5px; margin: 15px 0;">
                                <p><strong>User:</strong> {username}</p>
                                <p><strong>Email:</strong> {user.email}</p>
                                <p><strong>IP Address:</strong> {ip_address}</p>
                                <p><strong>Browser:</strong> {browser_info}</p>
                                <p><strong>Login Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                            </div>
                        </div>
                    </body>
                </html>
                """
                send_email(admin.email, f"User Login: {username}", email_body)
            
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out!', 'info')
    return redirect(url_for('login'))

# ==================== USER DASHBOARD ROUTES ====================

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/system-metrics')
@login_required
def get_metrics():
    """Get current system metrics and store in database"""
    data = get_system_health()
    
    # Store metrics in database
    system_record = SystemData(
        user_id=current_user.id,
        cpu=data['cpu'],
        ram=data['ram'],
        disk=data['disk'],
        health_score=data['health_score']
    )
    db.session.add(system_record)
    db.session.commit()
    
    return jsonify(data)

@app.route('/api/history')
@login_required
def get_history():
    """Get historical system data"""
    period = request.args.get('period', 'today')
    
    now = datetime.utcnow()
    
    if period == 'today':
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == 'weekly':
        start_time = now - timedelta(days=7)
    elif period == 'monthly':
        start_time = now - timedelta(days=30)
    else:
        start_time = now - timedelta(days=1)
    
    history = SystemData.query.filter(
        SystemData.user_id == current_user.id,
        SystemData.timestamp >= start_time
    ).order_by(SystemData.timestamp).all()
    
    data = {
        'timestamps': [h.timestamp.strftime('%H:%M:%S' if period == 'today' else '%Y-%m-%d') for h in history],
        'cpu': [h.cpu for h in history],
        'ram': [h.ram for h in history],
        'disk': [h.disk for h in history],
        'health_score': [h.health_score for h in history]
    }
    
    return jsonify(data)

# ==================== ADMIN ROUTES ====================

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    total_users = User.query.count()
    total_logins = LoginHistory.query.count()
    total_admins = User.query.filter_by(is_admin=True).count()
    
    users = User.query.all()
    recent_logins = LoginHistory.query.order_by(LoginHistory.login_time.desc()).limit(20).all()
    
    return render_template('admin_dashboard.html', 
                         total_users=total_users,
                         total_logins=total_logins,
                         total_admins=total_admins,
                         users=users,
                         recent_logins=recent_logins)

@app.route('/api/admin/user-details/<int:user_id>')
@login_required
@admin_required
def get_user_details(user_id):
    """Get detailed login history for a user"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    logins = LoginHistory.query.filter_by(user_id=user_id).order_by(LoginHistory.login_time.desc()).all()
    
    data = {
        'username': user.username,
        'email': user.email,
        'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'total_logins': len(logins),
        'logins': [
            {
                'time': login.login_time.strftime('%Y-%m-%d %H:%M:%S'),
                'ip': login.ip_address,
                'browser': login.browser
            } for login in logins
        ]
    }
    
    return jsonify(data)

@app.route('/api/admin/make-admin/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def make_admin(user_id):
    """Make a user an admin"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    user.is_admin = True
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'{user.username} is now an admin'})

@app.route('/api/admin/remove-admin/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def remove_admin(user_id):
    """Remove admin privileges from a user"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot remove admin privileges from yourself'}), 400
    
    user.is_admin = False
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'{user.username} is no longer an admin'})

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

# ==================== INITIALIZATION ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
