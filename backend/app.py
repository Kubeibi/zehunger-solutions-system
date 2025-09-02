from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_from_directory, abort
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Regexp
from werkzeug.security import generate_password_hash, check_password_hash
from database import DatabaseConnection
import logging
from datetime import datetime, timedelta
import json
import os
import re
import secrets
from waste_management_routes import waste_management
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, ADMIN_EMAIL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
            static_folder='../frontend',
            template_folder='../frontend')
CORS(app, supports_credentials=True)  # Enable CORS for all routes and allow credentials

# Configure Flask app
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # Session timeout

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.session_protection = 'strong'

# Initialize database connection
db = DatabaseConnection()

# Register blueprints
app.register_blueprint(waste_management)

# Route to serve static files
@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files from the frontend folder"""
    # Only serve CSS and JS files
    if filename.endswith(('.css', '.js')):
        return send_from_directory('../frontend', filename)
    else:
        # For other files, let Flask handle them normally
        return app.send_static_file(filename)

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_id, username, email, password_hash, full_name=None, last_login=None, is_active=True):
        self.id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.full_name = full_name
        self.last_login = last_login
        self._is_active = is_active  # Store as private variable

    @property
    def is_active(self):
        return self._is_active

    def get_id(self):
        return str(self.id)

# Enhanced Login form with security
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(), 
        Email(message='Please enter a valid email address')
    ])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

# Enhanced Registration form with security
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=3, max=20, message='Username must be between 3 and 20 characters'),
        Regexp(r'^[a-zA-Z0-9_]+$', message='Username can only contain letters, numbers, and underscores')
    ])
    full_name = StringField('Full Name', validators=[
        DataRequired(),
        Length(min=2, max=100, message='Full name must be between 2 and 100 characters')
    ])
    email = StringField('Email', validators=[
        DataRequired(), 
        Email(message='Please enter a valid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long'),
        Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]', 
               message='Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')

    def validate_username(self, username):
        result = db.fetch_one("SELECT user_id FROM users WHERE username = %s", (username.data,))
        if result:
            raise ValidationError('Username already taken. Please choose another one.')

    def validate_email(self, email):
        result = db.fetch_one("SELECT user_id FROM users WHERE email = %s", (email.data,))
        if result:
            raise ValidationError('Email already registered. Please use another email.')

# Database helper functions
def get_user_by_email(email):
    """Get user by email from database"""
    result = db.fetch_one("""
        SELECT user_id, username, email, password_hash, full_name, last_login, is_active
        FROM users WHERE email = %s
    """, (email,))
    
    if result:
        return User(
            user_id=result['user_id'],
            username=result['username'],
            email=result['email'],
            password_hash=result['password_hash'],
            full_name=result['full_name'],
            last_login=result['last_login'],
            is_active=result['is_active']
        )
    return None

def get_user_by_id(user_id):
    """Get user by ID from database"""
    result = db.fetch_one("""
        SELECT user_id, username, email, password_hash, full_name, last_login, is_active
        FROM users WHERE user_id = %s
    """, (user_id,))
    
    if result:
        return User(
            user_id=result['user_id'],
            username=result['username'],
            email=result['email'],
            password_hash=result['password_hash'],
            full_name=result['full_name'],
            last_login=result['last_login'],
            is_active=result['is_active']
        )
    return None

def create_user(username, full_name, email, password):
    """Create a new user in the database"""
    password_hash = generate_password_hash(password)
    
    query = """
        INSERT INTO users (username, full_name, email, password_hash, role, created_at)
        VALUES (%s, %s, %s, %s, %s, NOW())
    """
    user_id = db.execute_query(query, (username, full_name, email, password_hash, 'viewer'))
    return user_id

def update_last_login(user_id):
    """Update user's last login time"""
    db.execute_query("""
        UPDATE users SET last_login = NOW()
        WHERE user_id = %s
    """, (user_id,))

@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(int(user_id))

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        password = form.password.data
        
        # Verify credentials
        user = get_user_by_email(email)
        if user and user.is_active and check_password_hash(user.password_hash, password):
            # Successful login
            login_user(user, remember=form.remember.data)
            update_last_login(user.id)
            
            next_page = request.args.get('next')
            if next_page and not next_page.startswith('/'):
                next_page = None
            return redirect(next_page or url_for('dashboard'))
        else:
            # Failed login
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            username = form.username.data.strip()
            full_name = form.full_name.data.strip()
            email = form.email.data.lower().strip()
            password = form.password.data
            
            user_id = create_user(username, full_name, email, password)
            flash('Registration successful! Please login with your new account.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Registration failed. Please try again.', 'danger')
            logger.error(f'Registration error: {e}')
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

# API routes for AJAX requests
@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """API endpoint for AJAX login requests"""
    data = request.get_json()
    email = data.get('username', '').lower().strip()  # Frontend sends username field
    password = data.get('password', '')
    remember_me = data.get('rememberMe', False)
    
    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password are required'}), 400
    
    # Verify credentials
    user = get_user_by_email(email)
    if user and user.is_active and check_password_hash(user.password_hash, password):
        # Successful login
        login_user(user, remember=remember_me)
        update_last_login(user.id)
        return jsonify({'success': True, 'message': 'Login successful'})
    else:
        # Failed login
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    """API endpoint for AJAX registration requests"""
    data = request.get_json()
    username = data.get('username', '').strip()
    full_name = data.get('fullName', '').strip()
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')
    confirm_password = data.get('confirmPassword', '')
    
    # Simple validation
    if not all([username, full_name, email, password, confirm_password]):
        return jsonify({'success': False, 'message': 'All fields are required'}), 400
    if password != confirm_password:
        return jsonify({'success': False, 'message': 'Passwords do not match'}), 400
        
    # Check if user already exists
    if get_user_by_email(email):
        return jsonify({'success': False, 'message': 'Email is already registered'}), 409

    try:
        create_user(username, full_name, email, password)
        return jsonify({'success': True, 'message': 'Registration successful'}), 201
    except Exception as e:
        logger.error(f"API Registration error: {e}")
        return jsonify({'success': False, 'message': 'Registration failed due to a server error'}), 500

@app.route('/')
@login_required
def index():
    """Serve the main dashboard page"""
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Serve the main dashboard page"""
    # Assuming index.html is your main dashboard file
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/waste-sourcing', methods=['POST'])
@login_required
def handle_waste_sourcing():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400

    # Normalize keys from camelCase to snake_case
    normalized_data = normalize_keys(data)

    required_fields = ['collection_date', 'collection_time', 'source_type', 'source_name', 'waste_type', 'waste_weight', 'segregation_status', 'collection_personnel', 'recorded_by']
    missing_fields = [field for field in required_fields if field not in normalized_data or not normalized_data.get(field)]
    if missing_fields:
        return jsonify({'success': False, 'message': f'Missing required fields: {", ".join(missing_fields)}'}), 400

    try:
        # Contaminants might be a list, so convert to a comma-separated string if necessary
        contaminants = normalized_data.get('contaminants_found', [])
        if isinstance(contaminants, list):
            contaminants = ','.join(contaminants)

        query = """
            INSERT INTO waste_sourcing (
                collection_date, collection_time, source_type, source_name, waste_type, waste_weight, 
                segregation_status, contaminants_found, collection_notes, collection_personnel, recorded_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            normalized_data['collection_date'],
            normalized_data['collection_time'],
            normalized_data['source_type'],
            normalized_data['source_name'],
            normalized_data['waste_type'],
            normalized_data['waste_weight'],
            normalized_data['segregation_status'],
            contaminants,
            normalized_data.get('collection_notes', ''),
            normalized_data['collection_personnel'],
            normalized_data['recorded_by']
        )
        db.execute_query(query, params)
        return jsonify({'success': True, 'message': 'Waste sourcing data recorded successfully'}), 201
    except Exception as e:
        logger.error(f"Error handling waste sourcing: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while saving data.'}), 500

@app.route('/api/storage-records', methods=['POST'])
@login_required
def handle_storage_records():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400
    
    normalized_data = normalize_keys(data)

    required_fields = ['storage_date', 'storage_method', 'storage_conditions', 'storage_duration', 'planned_utilization']
    missing_fields = [field for field in required_fields if field not in normalized_data or not normalized_data.get(field)]
    if missing_fields:
        return jsonify({'success': False, 'message': f'Missing required fields: {", ".join(missing_fields)}'}), 400

    try:
        query = """
            INSERT INTO storage_records (
                storage_date, storage_method, storage_conditions, storage_duration, 
                planned_utilization, storage_observations, recorded_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            normalized_data['storage_date'],
            normalized_data['storage_method'],
            normalized_data['storage_conditions'],
            normalized_data['storage_duration'],
            normalized_data['planned_utilization'],
            normalized_data.get('storage_observations', ''),
            current_user.username
        )
        db.execute_query(query, params)
        return jsonify({'success': True, 'message': 'Storage record saved successfully'}), 201
    except Exception as e:
        logger.error(f"Error saving storage record: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred.'}), 500


@app.route('/api/processing-records', methods=['POST'])
@login_required
def handle_processing_records():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400

    normalized_data = normalize_keys(data)
    
    required_fields = ['processing_date', 'processing_type', 'processing_method', 'waste_processed']
    missing_fields = [field for field in required_fields if field not in normalized_data or not normalized_data.get(field)]
    if missing_fields:
        return jsonify({'success': False, 'message': f'Missing required fields: {", ".join(missing_fields)}'}), 400

    try:
        query = """
            INSERT INTO processing_records (
                processing_date, processing_type, processing_method, waste_processed, 
                by_products, waste_reduction, processing_remarks, recorded_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            normalized_data['processing_date'],
            normalized_data['processing_type'],
            normalized_data['processing_method'],
            normalized_data['waste_processed'],
            normalized_data.get('by_products', ''),
            normalized_data.get('waste_reduction'),
            normalized_data.get('processing_remarks', ''),
            current_user.username
        )
        db.execute_query(query, params)
        return jsonify({'success': True, 'message': 'Processing record saved successfully'}), 201
    except Exception as e:
        logger.error(f"Error saving processing record: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred.'}), 500

@app.route('/api/environmental-monitoring', methods=['POST'])
@login_required
def handle_environmental_monitoring():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400

    normalized_data = normalize_keys(data)
    
    required_fields = ['monitoring_date', 'monitoring_time', 'temperature', 'humidity', 'odor_level', 'pest_presence']
    missing_fields = [field for field in required_fields if field not in normalized_data or not normalized_data.get(field)]
    if missing_fields:
        logger.error(f"Missing required fields: {missing_fields}")
        missing_str = ', '.join(missing_fields)
        return jsonify({'success': False, 'message': f'Missing required fields: {missing_str}'}), 400

    try:
        query = """
            INSERT INTO environmental_monitoring_waste (
                monitoring_date, monitoring_time, temperature, humidity, 
                odor_level, pest_presence, pest_details, mitigation_actions, remarks, recorded_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            normalized_data['monitoring_date'],
            normalized_data['monitoring_time'],
            normalized_data['temperature'],
            normalized_data['humidity'],
            normalized_data['odor_level'],
            normalized_data['pest_presence'],
            normalized_data.get('pest_details', ''),
            normalized_data.get('mitigation_actions', ''),
            normalized_data.get('remarks', ''),
            current_user.username
        )
        db.execute_query(query, params)
        return jsonify({'success': True, 'message': 'Environmental monitoring record saved successfully'}), 201
    except Exception as e:
        logger.error(f"Error saving environmental monitoring record: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred.'}), 500

@app.route('/api/substrate-preparation', methods=['POST'])
@login_required
def handle_substrate_preparation():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400

    normalized_data = normalize_keys(data)
    
    required_fields = ['batch_no', 'prep_date', 'organic_waste_source', 'moisture_percentage', 'waste_particle_size', 'foreign_matter', 'handler_operator']
    missing_fields = [field for field in required_fields if field not in normalized_data or not normalized_data.get(field)]
    if missing_fields:
        return jsonify({'success': False, 'message': f'Missing required fields: {", ".join(missing_fields)}'}), 400

    try:
        query = """
            INSERT INTO substrate_preparation (
                batch_no, prep_date, organic_waste_source, moisture_percentage, 
                waste_particle_size, foreign_matter, handler_operator, notes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            normalized_data['batch_no'],
            normalized_data['prep_date'],
            normalized_data['organic_waste_source'],
            normalized_data['moisture_percentage'],
            normalized_data['waste_particle_size'],
            normalized_data['foreign_matter'],
            normalized_data['handler_operator'],
            normalized_data.get('notes', '')
        )
        db.execute_query(query, params)
        return jsonify({'success': True, 'message': 'Substrate preparation record saved successfully'}), 201
    except Exception as e:
        logger.error(f"Error saving substrate preparation record: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred.'}), 500

@app.route('/api/environmental-monitoring-waste', methods=['POST'])
@login_required
def handle_waste_environmental_monitoring():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400

    normalized_data = normalize_keys(data)
    required_fields = ['monitoring_date', 'monitoring_time', 'temperature', 'humidity', 'odor_level', 'pest_presence']
    
    missing_fields = [field for field in required_fields if field not in normalized_data or not normalized_data.get(field)]
    if missing_fields:
        return jsonify({'success': False, 'message': f'Missing or empty required fields: {", ".join(missing_fields)}'}), 400

    query = """
        INSERT INTO environmental_monitoring_waste (
            monitoring_date, monitoring_time, temperature, humidity, odor_level, 
            pest_presence, pest_details, mitigation_actions, remarks, recorded_by
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        normalized_data.get('monitoring_date'),
        normalized_data.get('monitoring_time'),
        normalized_data.get('temperature'),
        normalized_data.get('humidity'),
        normalized_data.get('odor_level'),
        normalized_data.get('pest_presence'),
        normalized_data.get('pest_details'),
        normalized_data.get('mitigation_actions'),
        normalized_data.get('remarks'),
        current_user.username
    )

    try:
        db.execute_query(query, params)
        logger.info(f"Waste environmental monitoring data saved for {normalized_data.get('monitoring_date')}")
        return jsonify({'success': True, 'message': 'Environmental monitoring record created successfully'})
    except Exception as e:
        logger.error(f"Error creating waste environmental monitoring record: {e}")
        return jsonify({'success': False, 'message': 'Failed to create environmental monitoring record'}), 500


# --- Statistics & Reporting ---
@app.route('/api/statistics/waste-processing', methods=['GET'])
@login_required
def get_waste_processing_stats():
    try:
        query = """
            SELECT 
                DATE(processing_date) as date,
                SUM(waste_processed) as total_processed,
                SUM(by_products) as total_by_products
            FROM processing_records
            GROUP BY DATE(processing_date)
            ORDER BY date DESC
            LIMIT 30;
        """
        stats = db.fetch_all(query)
        # Convert decimal and date objects to string/float for JSON serialization
        for row in stats:
            for key, value in row.items():
                if isinstance(value, (datetime,)):
                    row[key] = value.isoformat()
                elif isinstance(value, float):
                    row[key] = float(value)
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error fetching waste processing stats: {e}")
        return jsonify([]), 500


@app.route('/api/statistics/environmental', methods=['GET'])
@login_required
def get_environmental_stats():
    try:
        query = """
            SELECT 
                DATE(monitoring_date) as date,
                AVG(temperature) as avg_temp,
                AVG(humidity) as avg_humidity
            FROM environmental_monitoring_waste
            GROUP BY DATE(monitoring_date)
            ORDER BY date DESC
            LIMIT 30;
        """
        stats = db.fetch_all(query)
        for row in stats:
            for key, value in row.items():
                if isinstance(value, (datetime,)):
                    row[key] = value.isoformat()
                elif isinstance(value, float):
                    row[key] = float(value)
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error fetching environmental stats: {e}")
        return jsonify([]), 500

@app.route('/api/statistics/larval-growth', methods=['GET'])
@login_required
def get_larval_growth_stats():
    try:
        query = """
            SELECT 
                DATE(feeding_date) as date,
                AVG(larvae_weight) as avg_weight,
                AVG(consumption) as avg_consumption
            FROM feeding_schedule
            GROUP BY DATE(feeding_date)
            ORDER BY date DESC
            LIMIT 30;
        """
        stats = db.fetch_all(query)
        for row in stats:
            for key, value in row.items():
                if isinstance(value, (datetime,)):
                    row[key] = value.isoformat()
                elif isinstance(value, float):
                    row[key] = float(value)
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error fetching larval growth stats: {e}")
        return jsonify([]), 500

@app.route('/api/statistics/system-efficiency', methods=['GET'])
@login_required
def get_system_efficiency():
    try:
        query_waste = """
            SELECT SUM(waste_weight) as total_waste_in
            FROM waste_sourcing;
        """
        total_waste_in = db.fetch_one(query_waste)['total_waste_in'] or 0

        query_larvae = """
            SELECT SUM(larvae_collected_kg) as total_larvae_out
            FROM feeding_harvest_yield;
        """
        total_larvae_out = db.fetch_one(query_larvae)['total_larvae_out'] or 0
        
        query_compost = """
            SELECT SUM(by_products) as total_compost_out
            FROM processing_records;
        """
        total_compost_out = db.fetch_one(query_compost)['total_compost_out'] or 0

        efficiency = (total_larvae_out + total_compost_out) / total_waste_in if total_waste_in > 0 else 0

        return jsonify({
            'total_waste_in': float(total_waste_in),
            'total_larvae_out': float(total_larvae_out),
            'total_compost_out': float(total_compost_out),
            'overall_efficiency': efficiency
        })
    except Exception as e:
        logger.error(f"Error calculating system efficiency: {e}")
        return jsonify({}), 500

@app.route('/api/statistics/daily-report', methods=['GET'])
@login_required
def get_daily_report():
    today = datetime.now().date()
    try:
        # Waste Sourced Today
        waste_sourced_query = "SELECT SUM(waste_weight) as total FROM waste_sourcing WHERE DATE(collection_date) = %s"
        waste_sourced = db.fetch_one(waste_sourced_query, (today,))['total'] or 0

        # Larvae Harvested Today
        larvae_harvested_query = "SELECT SUM(larvae_collected_kg) as total FROM feeding_harvest_yield WHERE DATE(harvest_date) = %s"
        larvae_harvested = db.fetch_one(larvae_harvested_query, (today,))['total'] or 0

        # Feed Given Today
        feed_given_query = "SELECT SUM(feed_quantity_kg) as total FROM feeding_schedule WHERE DATE(feeding_date) = %s"
        feed_given = db.fetch_one(feed_given_query, (today,))['total'] or 0

        # Eggs Collected Today
        eggs_collected_query = "SELECT SUM(eggs_collected) as total FROM fly_facility_egg_collection WHERE DATE(collection_date) = %s"
        eggs_collected = db.fetch_one(eggs_collected_query, (today,))['total'] or 0

        return jsonify({
            'waste_sourced_today': float(waste_sourced),
            'larvae_harvested_today': float(larvae_harvested),
            'feed_given_today': float(feed_given),
            'eggs_collected_today': float(eggs_collected)
        })
    except Exception as e:
        logger.error(f"Error fetching daily report: {e}")
        return jsonify({}), 500

@app.route('/api/statistics/harvest-efficiency', methods=['GET'])
@login_required
def get_harvest_efficiency():
    try:
        query = """
            SELECT
                di.batch_id,
                MAX(do.created_at) as output_date,
                SUM(di.wet_placed) AS total_wet_weight,
                SUM(do.dried_produced) AS total_dried_weight
            FROM drying_input di
            JOIN drying_output do ON di.batch_id = do.batch_id
            GROUP BY di.batch_id
            ORDER BY output_date ASC;
        """
        results = db.fetch_all(query)
        
        efficiency_data = []
        target_ratio = 3.0

        for row in results:
            batch_id = row['batch_id']
            date = row['output_date'].isoformat() if row['output_date'] else None
            total_wet = float(row['total_wet_weight']) if row['total_wet_weight'] is not None else None
            total_dried = float(row['total_dried_weight']) if row['total_dried_weight'] is not None else None

            if total_wet is not None and total_dried is not None and total_dried > 0:
                actual_ratio_val = total_wet / total_dried
                actual_ratio = f"{actual_ratio_val:.2f}:1"
                efficiency_percentage = (target_ratio / actual_ratio_val) * 100
            else:
                actual_ratio = "N/A"
                efficiency_percentage = 0

            efficiency_data.append({
                'batch_id': batch_id,
                'date': date,
                'actual_ratio': actual_ratio,
                'target_ratio': "3:1",
                'efficiency_percentage': round(efficiency_percentage, 2)
            })
        return jsonify(efficiency_data)
    except Exception as e:
        logger.error(f"Error fetching harvest efficiency: {e}")
        return jsonify({'error': 'Could not fetch harvest efficiency data'}), 500


def camel_to_snake(name):
  pattern = re.compile(r'(?<!^)(?=[A-Z])')
  return pattern.sub('_', name).lower()

def normalize_keys(data):
    if isinstance(data, dict):
        return {camel_to_snake(k): normalize_keys(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [normalize_keys(i) for i in data]
    else:
        return data

def validate_fields(data, required_fields):
    missing_fields = [field for field in required_fields if field not in data]
    return missing_fields

@app.route('/api/drying/batch', methods=['POST'])
@login_required
def create_drying_batch():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON format'}), 400

    data = normalize_keys(data)
    required_fields = ['batch_id', 'drying_date', 'drying_method', 'personnel', 'status']
    if any(field not in data for field in required_fields):
        missing_fields = [field for field in required_fields if field not in data]
        return jsonify({'success': False, 'message': f'Missing required fields: {", ".join(missing_fields)}'}), 400

    try:
        query = """INSERT INTO drying_batches (batch_id, drying_date, drying_method, personnel, status) 
                   VALUES (%s, %s, %s, %s, %s)"""
        params = (data['batch_id'], data['drying_date'], data['drying_method'], data['personnel'], data['status'])
        db.execute_query(query, params)
        logger.info(f"Drying batch {data['batch_id']} created.")
        return jsonify({'success': True, 'message': 'Drying batch created successfully'}), 201
    except Exception as e:
        logger.error(f"Error creating drying batch: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/drying/input', methods=['POST'])
@login_required
def create_drying_input():
    data = request.get_json()
    data = normalize_keys(data)
    
    # Basic validation
    required_fields = ['batch_id', 'wet_harvested', 'wet_placed', 'dried_by_personnel', 'sand_used']
    if any(f not in data for f in required_fields):
        return jsonify({'success': False, 'message': 'Missing required fields.'}), 400

    query = """INSERT INTO drying_input (batch_id, wet_harvested_kg, wet_placed_for_drying_kg, dried_by_personnel_kg, sand_used_kg, sand_reused_kg, notes, recorded_by) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
    params = (
        data['batch_id'], data['wet_harvested'], data['wet_placed'], 
        data['dried_by_personnel'], data['sand_used'], data.get('sand_reused'), data.get('notes'), current_user.username
    )
    db.execute_query(query, params)
    return jsonify({'success': True, 'message': 'Drying input recorded successfully.'})

@app.route('/api/drying/output', methods=['POST'])
@login_required
def create_drying_output():
    data = request.get_json()
    data = normalize_keys(data)
    required = ['batch_id', 'dried_produced']
    if any(field not in data for field in required):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    try:
        # Fetch the wet weight from drying_input to calculate ratio and yield
        input_query = "SELECT SUM(wet_placed_for_drying_kg) as total_wet FROM drying_input WHERE batch_id = %s"
        input_result = db.fetch_one(input_query, (data['batch_id'],))
        total_wet_weight = input_result['total_wet'] if input_result and input_result['total_wet'] else 0

        dried_produced = float(data['dried_produced'])
        actual_ratio = f"{total_wet_weight}:{dried_produced}" if dried_produced > 0 else "N/A"
        yield_percentage = (dried_produced / total_wet_weight) * 100 if total_wet_weight > 0 else 0

        query = """INSERT INTO drying_output (batch_id, dried_produced_kg, solar_drying_taken_kg, stored_in_silo_bag_kg, sold_kg, actual_ratio, yield_percentage, notes, recorded_by) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        params = (
            data['batch_id'],
            dried_produced,
            data.get('solar_drying_taken'),
            data.get('silo_bag_stored'),
            data.get('dried_sold'),
            actual_ratio,
            yield_percentage,
            data.get('notes'),
            current_user.username
        )
        db.execute_query(query, params)
        logger.info(f"Drying output recorded for batch {data['batch_id']}")
        return jsonify({'success': True, 'message': 'Drying output recorded successfully', 'actual_ratio': actual_ratio, 'yield_percentage': yield_percentage}), 201
    except Exception as e:
        logger.error(f"Error in create_drying_output: {e}")
        return jsonify({'success': False, 'message': 'An error occurred'}), 500

@app.route('/api/drying/qc', methods=['POST'])
@login_required
def create_drying_qc():
    data = request.get_json()
    data = normalize_keys(data)
    required = ['batch_id', 'qc_date', 'sand_removal', 'color_quality', 'moisture_level', 'qc_personnel']
    if any(field not in data for field in required):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    # Handle multiple selection for contaminants
    contaminants = data.get('contaminants_found', [])
    contaminants_str = ','.join(contaminants) if isinstance(contaminants, list) else contaminants

    query = """INSERT INTO drying_quality_control (batch_id, qc_date, sand_removal, contaminants_found, color_quality, moisture_level, qc_personnel, notes, recorded_by) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    params = (data['batch_id'], data['qc_date'], data['sand_removal'], contaminants_str, data['color_quality'], data['moisture_level'], data['qc_personnel'], data.get('notes'), current_user.username)
    db.execute_query(query, params)
    return jsonify({'success': True, 'message': 'Drying QC recorded successfully.'})

@app.route('/api/drying/quality-control', methods=['POST'])
@login_required
def deprecated_create_drying_quality_control():
    # This is a deprecated route name, redirecting logic to the new one.
    return create_drying_qc()

@app.route('/api/drying/remarks', methods=['POST'])
@login_required
def create_drying_remarks():
    # This route seems to be unused based on frontend JS.
    # If it were to be used, it would likely add remarks to an existing batch.
    return jsonify({'success': False, 'message': 'This route is not implemented.'}), 404

@app.route('/api/drying/review', methods=['POST'])
@login_required
def create_drying_review():
    data = request.get_json()
    data = normalize_keys(data)
    required = ['batch_id', 'reviewed_by', 'review_date', 'approval_status']
    if any(field not in data for field in required):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    query = """INSERT INTO drying_review_approval (batch_id, reviewed_by, review_date, approval_status, comments, recorded_by) 
               VALUES (%s, %s, %s, %s, %s, %s)"""
    params = (data['batch_id'], data['reviewed_by'], data['review_date'], data['approval_status'], data.get('comments'), current_user.username)
    db.execute_query(query, params)
    return jsonify({'success': True, 'message': 'Drying review recorded successfully.'})

# --- GET ALL (for potential future table views) ---
@app.route('/api/waste-sourcing/all', methods=['GET'])
@login_required
def get_all_waste_sourcing():
    query = "SELECT * FROM waste_sourcing ORDER BY collection_date DESC"
    records = db.fetch_all(query)
    return jsonify(records)

@app.route('/api/drying/input/all', methods=['GET'])
@login_required
def get_all_drying_input():
    query = "SELECT * FROM drying_input ORDER BY created_at DESC"
    records = db.fetch_all(query)
    return jsonify(records)

@app.route('/api/drying/output/all', methods=['GET'])
@login_required
def get_all_drying_output():
    query = "SELECT * FROM drying_output ORDER BY created_at DESC"
    records = db.fetch_all(query)
    return jsonify(records)

@app.route('/api/drying/qc/all', methods=['GET'])
@login_required
def get_all_drying_qc():
    query = "SELECT * FROM drying_quality_control ORDER BY qc_date DESC"
    records = db.fetch_all(query)
    return jsonify(records)

@app.route('/api/drying/remarks/all', methods=['GET'])
@login_required
def get_all_drying_remarks():
    # This table doesn't exist, so this is a placeholder
    return jsonify([])

@app.route('/api/drying/review/all', methods=['GET'])
@login_required
def get_all_drying_review():
    query = "SELECT * FROM drying_review_approval ORDER BY review_date DESC"
    records = db.fetch_all(query)
    return jsonify(records)

@app.route('/api/feeding/harvest/all', methods=['GET'])
@login_required
def get_all_feeding_harvest():
    # Assuming this should get from larval_harvest_yield
    query = "SELECT * FROM feeding_harvest_yield ORDER BY harvest_date DESC"
    records = db.fetch_all(query)
    return jsonify(records)


# --- Feeding Section ---
@app.route('/api/feeding/environmental-monitoring', methods=['POST'])
@login_required
def create_feeding_environmental_monitoring():
    data = request.get_json()
    if not data:
        logger.error('No JSON data provided in request')
        return jsonify({'success': False, 'message': 'Invalid JSON format'}), 400

    data = normalize_keys(data)

    required_fields = ['monitoring_date', 'monitoring_time', 'tray_facility_id', 'temperature', 'humidity', 'ammonia_odor']
    missing = [f for f in required_fields if f not in data or data[f] in (None, "")]
    if missing:
        logger.error(f"Missing required fields: {missing}")
        missing_str = ', '.join(missing)
        return jsonify({'success': False, 'message': f'Missing required fields: {missing_str}'}), 400

    try:
        query = """
            INSERT INTO feeding_environmental_monitoring (monitoring_date, monitoring_time, tray_facility_id, temperature, humidity, ammonia_odor, notes, recorded_by) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            data['monitoring_date'], data['monitoring_time'], data['tray_facility_id'],
            data['temperature'], data['humidity'], data['ammonia_odor'],
            data.get('notes'), current_user.username
        )
        db.execute_query(query, params)
        logger.info(f"Larval env monitoring recorded for {data['tray_facility_id']}")
        return jsonify({'success': True, 'message': 'Environmental monitoring data saved successfully'}), 201
    except Exception as e:
        logger.error(f"Error saving larval env monitoring data: {e}", exc_info=True)
        return jsonify({'success': False, 'message': f'Failed to save data: {str(e)}'}), 500

@app.route('/api/feeding/health-intervention', methods=['POST'])
@login_required
def create_feeding_health_intervention():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON format'}), 400
    
    data = normalize_keys(data)

    required_fields = ['health_date', 'tray_batch_id', 'observed_issue', 'severity', 'action_taken']
    if any(field not in data for field in required_fields):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    try:
        query = """
            INSERT INTO feeding_health_intervention (health_check_date, tray_batch_id, observed_issue, severity, action_taken, follow_up_date, resolved, comments, recorded_by) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (data['health_date'], data['tray_batch_id'], data['observed_issue'], data['severity'], data['action_taken'], data.get('follow_up_date'), data.get('resolved'), data.get('comments'), current_user.username)
        db.execute_query(query, params)
        logger.info(f"Health intervention recorded for {data['tray_batch_id']}")
        return jsonify({'success': True, 'message': 'Health intervention data saved successfully'}), 201
    except Exception as e:
        logger.error(f"Error saving health intervention data: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred.'}), 500

@app.route('/api/feeding/harvest-yield', methods=['POST'])
@login_required
def create_feeding_harvest_yield():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON format'}), 400

    data = normalize_keys(data)

    required_fields = ['harvest_date', 'tray_batch_id', 'instar_stage', 'larvae_collected_kg', 'processing_method']
    if any(field not in data for field in required_fields):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    try:
        query = """
            INSERT INTO feeding_harvest_yield (harvest_date, tray_batch_id, instar_stage, larvae_collected_kg, processing_method, storage_temperature_celsius, notes, recorded_by) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (data['harvest_date'], data['tray_batch_id'], data['instar_stage'], data['larvae_collected_kg'], data['processing_method'], data.get('storage_temperature_celsius'), data.get('notes'), current_user.username)
        db.execute_query(query, params)
        logger.info(f"Harvest/yield recorded for {data['tray_batch_id']}")
        return jsonify({'success': True, 'message': 'Harvest & Yield data saved successfully'}), 201
    except Exception as e:
        logger.error(f"Error saving harvest/yield data: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred.'}), 500

@app.route('/api/feeding/schedule', methods=['POST'])
@login_required
def create_feeding_schedule():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON format'}), 400

    data = normalize_keys(data)

    required_fields = ['feeding_date', 'tray_batch_id', 'larvae_age_days', 'larvae_weight_g', 'feed_type', 'feed_quantity_kg', 'operator']
    if any(field not in data for field in required_fields):
        logger.error(f"Missing required fields: {[f for f in required_fields if f not in data]}")
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    try:
        query = """
            INSERT INTO feeding_schedule (feeding_date, tray_batch_id, larvae_age_days, larvae_weight_g, feed_type, feed_quantity_kg, start_weight_g, end_weight_kg, consumption_g, operator, recorded_by) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            data['feeding_date'],
            data['tray_batch_id'],
            data['larvae_age_days'],
            data['larvae_weight_g'],
            data['feed_type'],
            data['feed_quantity_kg'],
            data.get('start_weight_g'),
            data.get('end_weight_kg'),
            data.get('consumption_g'),
            data['operator'],
            current_user.username
        )
        logger.debug(f"About to execute feeding schedule insert with params: {params}")
        db.execute_query(query, params)
        logger.debug("Feeding schedule insert executed successfully.")
        logger.info(f"Feeding schedule recorded for {data['tray_batch_id']}")
        return jsonify({'success': True, 'message': 'Feeding schedule saved successfully'}), 201
    except Exception as e:
        logger.error(f"Error saving feeding schedule: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred.'}), 500

# --- Fly Facility Section ---
@app.route('/api/facility/cage-monitoring', methods=['POST'])
@login_required
def create_cage_monitoring():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON format'}), 400

    data = normalize_keys(data)
    
    required_fields = ['date', 'cage_id', 'temperature', 'humidity', 'lighting_hours', 'ventilation_ok', 'cage_cleaned', 'dead_flies_removed', 'cage_damage']
    if any(field not in data for field in required_fields):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    try:
        query = """
            INSERT INTO fly_facility_cage_monitoring (
                monitoring_date, cage_id, temperature, humidity, lighting_hours, ventilation_ok, 
                cage_cleaned, dead_flies_removed, cage_damage, damage_notes, additional_notes, recorded_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            data['date'], data['cage_id'], data['temperature'], data['humidity'], data['lighting_hours'],
            data['ventilation_ok'], data['cage_cleaned'], data['dead_flies_removed'], data['cage_damage'],
            data.get('damage_notes'), data.get('additional_notes'), current_user.username
        )
        db.execute_query(query, params)
        logger.info(f"Cage monitoring recorded for {data['cage_id']}")
        return jsonify({'success': True, 'message': 'Cage monitoring data saved successfully'}), 201
    except Exception as e:
        logger.error(f"Error saving cage monitoring data: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred.'}), 500

@app.route('/api/facility/maintenance', methods=['POST'])
@login_required
def create_facility_maintenance():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON format'}), 400
    
    data = normalize_keys(data)

    required_fields = ['date', 'moat_check', 'ants_present', 'rodents_present', 'bird_net_ok', 'trench_refilled', 'maintenance_notes']
    if any(field not in data for field in required_fields):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    try:
        query = """
            INSERT INTO fly_facility_maintenance (
                maintenance_date, moat_check, ants_present, rodents_present, bird_net_ok, 
                trench_refilled, maintenance_notes, recorded_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            data['date'], data['moat_check'], data['ants_present'], data['rodents_present'],
            data['bird_net_ok'], data['trench_refilled'], data['maintenance_notes'], current_user.username
        )
        db.execute_query(query, params)
        logger.info(f"Facility maintenance recorded for {data['date']}")
        return jsonify({'success': True, 'message': 'Facility maintenance data saved successfully'}), 201
    except Exception as e:
        logger.error(f"Error saving facility maintenance data: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred.'}), 500

@app.route('/api/facility/pupae-transition', methods=['POST'])
@login_required
def create_pupae_transition():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON format'}), 400

    data = normalize_keys(data)
    
    required_fields = ['date', 'love_cage_id', 'pupae_weight_added_kg', 'old_pupae_removed_kg', 'dead_flies_removed', 'water_points_checked', 'new_egg_crates_installed']
    if any(field not in data for field in required_fields):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    try:
        query = """
            INSERT INTO fly_facility_pupae_transition (
                transition_date, love_cage_id, pupae_weight_added_kg, old_pupae_removed_kg, dead_flies_removed, 
                water_points_checked, new_egg_crates_installed, number_of_crates, notes, recorded_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            data['date'], data['love_cage_id'],
            data['pupae_weight_added_kg'], data['old_pupae_removed_kg'],
            data['dead_flies_removed'], data['water_points_checked'], data['new_egg_crates_installed'],
            data.get('number_of_crates'), data.get('notes'), current_user.username
        )
        db.execute_query(query, params)
        logger.info(f"Pupae transition recorded for {data['love_cage_id']}")
        return jsonify({'success': True, 'message': 'Pupae transition data saved successfully'}), 201
    except Exception as e:
        logger.error(f"Error saving pupae transition data: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred.'}), 500

@app.route('/api/facility/egg-collection', methods=['POST'])
@login_required
def create_egg_collection():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON format'}), 400

    data = normalize_keys(data)

    required_fields = ['date', 'time', 'cage_id', 'eggs_collected', 'bait_replaced', 'eggs_intact', 'collector_name', 'collection_method']
    if any(field not in data for field in required_fields):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    try:
        query = """
            INSERT INTO fly_facility_egg_collection (
                collection_date, collection_time, cage_id, eggs_collected_g, bait_replaced, 
                eggs_intact, collector_name, collection_method, notes, recorded_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            data['date'], data['time'], data['cage_id'], data['eggs_collected'], data['bait_replaced'],
            data['eggs_intact'], data['collector_name'], data['collection_method'], data.get('notes'), current_user.username
        )
        db.execute_query(query, params)
        logger.info(f"Egg collection recorded for {data['cage_id']}")
        return jsonify({'success': True, 'message': 'Egg collection data saved successfully'}), 201
    except Exception as e:
        logger.error(f"Error saving egg collection data: {e}")
        return jsonify({'success': False, 'message': 'An internal error occurred.'}), 500

@app.route('/api/facility/bait-preparation', methods=['POST'])
@login_required
def create_bait_preparation():
    data = request.get_json()
    normalized_data = normalize_keys(data)
    required_fields = ['barrel_id', 'bait_type', 'ingredients_added', 'start_date', 'ready_date']
    
    missing_fields = [field for field in required_fields if field not in normalized_data or not normalized_data.get(field)]
    if missing_fields:
        return jsonify({'success': False, 'message': f'Missing or empty required fields: {", ".join(missing_fields)}'}), 400
        
    query = """
        INSERT INTO fly_facility_bait_preparation (barrel_id, bait_type, ingredients_added, start_date, ready_date, used_in_cage_ids, notes, recorded_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        normalized_data.get('barrel_id'),
        normalized_data.get('bait_type'),
        normalized_data.get('ingredients_added'),
        normalized_data.get('start_date'),
        normalized_data.get('ready_date'),
        normalized_data.get('used_in_cage_ids'),
        normalized_data.get('notes'),
        current_user.username
    )
    
    try:
        db.execute_query(query, params)
        logger.info(f"Bait preparation data saved for barrel {normalized_data.get('barrel_id')}")
        return jsonify({'success': True, 'message': 'Bait preparation record created successfully'})
    except Exception as e:
        logger.error(f"Error creating bait preparation record: {e}")
        return jsonify({'success': False, 'message': 'Failed to create bait preparation record'}), 500

@app.route('/api/records', methods=['GET'])
@login_required
def get_records_by_date_and_section():
    target_date_str = request.args.get('date')
    section = request.args.get('section')

    if not target_date_str:
        return jsonify({'success': False, 'message': 'Date parameter is required'}), 400

    try:
        target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid date format. Please use YYYY-MM-DD.'}), 400

    # Map sections to tables and their respective date columns
    section_tables = {
        'waste': {
            'Waste Sourcing': ('waste_sourcing', 'collection_date'),
            'Storage Records': ('storage_records', 'storage_date'),
            'Processing Records': ('processing_records', 'processing_date'),
            'Waste Environmental Monitoring': ('environmental_monitoring_waste', 'monitoring_date'),
        },
        'hatchery': {
            'Batch Information': ('hatchery_batches', 'batch_date'),
            'Feeding Records': ('hatchery_feeding', 'feeding_date'),
            'Environmental Monitoring': ('hatchery_monitoring', 'monitoring_date'),
            'Cleaning & Sanitation': ('hatchery_cleaning', 'cleaning_date'),
            'Problems & Solutions': ('hatchery_problems', 'problem_date'),
        },
        'feeding': {
            'Environmental Monitoring': ('feeding_environmental_monitoring', 'monitoring_date'),
            'Health & Intervention': ('feeding_health_intervention', 'health_check_date'),
            'Harvest & Yield': ('feeding_harvest_yield', 'harvest_date'),
            'Feeding Schedule': ('feeding_schedule', 'feeding_date'),
        },
        'drying': {
            'Batch Information': ('drying_batches', 'drying_date'),
            'Input Records': ('drying_input', 'created_at'),
            'Output Records': ('drying_output', 'created_at'),
            'Quality Control': ('drying_quality_control', 'qc_date'),
            'Review & Approval': ('drying_review_approval', 'review_date'),
        },
        'facility': {
            'Cage Monitoring': ('fly_facility_cage_monitoring', 'monitoring_date'),
            'Facility Maintenance': ('fly_facility_maintenance', 'maintenance_date'),
            'Pupae Transition': ('fly_facility_pupae_transition', 'transition_date'),
            'Egg Collection': ('fly_facility_egg_collection', 'collection_date'),
            'Bait Preparation': ('fly_facility_bait_preparation', 'start_date'),
        }
    }

    tables_to_query = {}
    if section == 'all':
        for sec in section_tables:
            tables_to_query.update(section_tables[sec])
    elif section in section_tables:
        tables_to_query = section_tables[section]
    else:
        return jsonify({'success': False, 'message': 'Invalid section specified'}), 400

    all_records = {}
    try:
        for display_name, (table_name, date_col) in tables_to_query.items():
            # The DATE() function is used to ignore the time part of datetime columns
            query = f"SELECT * FROM {table_name} WHERE DATE({date_col}) = %s"
            records = db.fetch_all(query, (target_date,))
            if records:
                # Convert datetime and timedelta objects to strings for JSON serialization
                for record in records:
                    for key, value in record.items():
                        if isinstance(value, (datetime, timedelta)):
                            record[key] = str(value)
                all_records[display_name] = records
        
        return jsonify({'success': True, 'records': all_records})

    except Exception as e:
        logger.error(f"Error fetching records for date {target_date_str} and section {section}: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while fetching records.'}), 500

# --- Hatchery Routes ---

@app.route('/api/hatchery/batch', methods=['POST'])
@login_required
def create_hatchery_batch():
    try:
        data = request.get_json()
        required_fields = [
            'batch_number', 'batch_date', 'egg_incubation_date',
            'total_eggs_grams', 'expected_hatch_date', 'supervisor_name'
        ]
        if any(f not in data for f in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        query = '''INSERT INTO hatchery_batches (
            batch_number, batch_date, egg_incubation_date, total_eggs_grams,
            expected_hatch_date, actual_hatch_date, hatch_days, supervisor_name, notes
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        params = (
            data['batch_number'], data['batch_date'], data['egg_incubation_date'],
            float(data['total_eggs_grams']), data['expected_hatch_date'],
            data.get('actual_hatch_date'), data.get('hatch_days'),
            data['supervisor_name'], data.get('notes')
        )
        db.execute_query(query, params)
        return jsonify({'message': 'Batch information saved successfully'}), 201
    except Exception as e:
        logger.error(f'Error saving hatchery batch: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/hatchery/feeding', methods=['POST'])
@login_required
def create_hatchery_feeding():
    try:
        data = request.get_json()
        required_fields = [
            'batch_id', 'feeding_date', 'feed_per_5g_eggs_grams',
            'total_feed_used_grams', 'days_to_utilize', 'feed_type', 'feed_source', 'distribution_method'
        ]
        if any(f not in data for f in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        query = '''INSERT INTO hatchery_feeding (
            batch_id, feeding_date, feed_per_5g_eggs_grams, total_feed_used_grams,
            days_to_utilize, feed_type, feed_source, distribution_method, notes
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        params = (
            data['batch_id'], data['feeding_date'], float(data['feed_per_5g_eggs_grams']),
            float(data['total_feed_used_grams']), int(data['days_to_utilize']),
            data['feed_type'], data['feed_source'], data['distribution_method'], data.get('notes')
        )
        db.execute_query(query, params)
        return jsonify({'message': 'Feeding record saved successfully'}), 201
    except Exception as e:
        logger.error(f'Error saving feeding record: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/hatchery/monitoring', methods=['POST'])
@login_required
def create_hatchery_monitoring():
    try:
        data = request.get_json()
        required_fields = ['monitoring_date', 'temperature_c', 'humidity_percent']
        if any(f not in data for f in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        query = '''INSERT INTO hatchery_monitoring (
            monitoring_date, temperature_c, humidity_percent, adjustments_made
        ) VALUES (%s, %s, %s, %s)'''
        params = (
            data['monitoring_date'], float(data['temperature_c']), float(data['humidity_percent']), data.get('adjustments_made')
        )
        db.execute_query(query, params)
        return jsonify({'message': 'Monitoring record saved successfully'}), 201
    except Exception as e:
        logger.error(f'Error saving monitoring record: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/hatchery/cleaning', methods=['POST'])
@login_required
def create_hatchery_cleaning():
    try:
        data = request.get_json()
        required_fields = ['cleaning_date', 'areas_cleaned', 'cleaning_materials', 'cleaning_personnel']
        if any(f not in data for f in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        query = '''INSERT INTO hatchery_cleaning (
            cleaning_date, areas_cleaned, cleaning_materials, cleaning_personnel, remarks
        ) VALUES (%s, %s, %s, %s, %s)'''
        params = (
            data['cleaning_date'], data['areas_cleaned'], data['cleaning_materials'], data['cleaning_personnel'], data.get('remarks')
        )
        db.execute_query(query, params)
        return jsonify({'message': 'Cleaning record saved successfully'}), 201
    except Exception as e:
        logger.error(f'Error saving cleaning record: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/hatchery/problems', methods=['POST'])
@login_required
def create_hatchery_problem():
    try:
        data = request.get_json()
        required_fields = ['problem_date', 'problem_identified', 'proposed_solution', 'responsible_person']
        if any(f not in data for f in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        query = '''INSERT INTO hatchery_problems (
            problem_date, problem_identified, proposed_solution, responsible_person,
            days_to_implement, resolution_status, additional_comments
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)'''
        params = (
            data['problem_date'], data['problem_identified'], data['proposed_solution'],
            data['responsible_person'], data.get('days_to_implement'), data.get('resolution_status'), data.get('additional_comments')
        )
        db.execute_query(query, params)
        return jsonify({'message': 'Problem record saved successfully'}), 201
    except Exception as e:
        logger.error(f'Error saving problem record: {e}')
        return jsonify({'error': str(e)}), 500

# Add missing hatchery endpoints that frontend is calling
@app.route('/api/hatchery/health', methods=['POST'])
@login_required
def create_hatchery_health():
    try:
        # Debug: Check if request has JSON content
        if not request.is_json:
            logger.error(f"Request is not JSON. Content-Type: {request.content_type}")
            return jsonify({'error': 'Request must be JSON'}), 400
        
        data = request.get_json()
        if data is None:
            logger.error("Failed to parse JSON data")
            return jsonify({'error': 'Invalid JSON data'}), 400
            
        required_fields = ['health_date', 'health_issue', 'severity', 'action_taken']
        if any(f not in data for f in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        query = '''INSERT INTO hatchery_health_interventions (
            health_date, health_issue, severity, action_taken, follow_up_date, resolved, comments
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)'''
        params = (
            data['health_date'], data['health_issue'], data['severity'], data['action_taken'],
            data.get('follow_up_date'), data.get('resolved'), data.get('comments')
        )
        db.execute_query(query, params)
        return jsonify({'message': 'Health intervention record saved successfully'}), 201
    except Exception as e:
        logger.error(f'Error saving health intervention record: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/hatchery/batch-information', methods=['POST'])
@login_required
def create_hatchery_batch_information():
    # Alias for the existing batch endpoint
    return create_hatchery_batch()

@app.route('/api/hatchery/feeding-records', methods=['POST'])
@login_required
def create_hatchery_feeding_records():
    # Alias for the existing feeding endpoint
    return create_hatchery_feeding()

@app.route('/api/hatchery/environmental-monitoring', methods=['POST'])
@login_required
def create_hatchery_environmental_monitoring():
    # Alias for the existing monitoring endpoint
    return create_hatchery_monitoring()

# --- Customers CRUD ---
@app.route('/api/customers', methods=['GET'])
@login_required
def get_customers():
    customers = db.fetch_all("SELECT * FROM customers")
    return jsonify(customers)

@app.route('/api/customers', methods=['POST'])
@login_required
def add_customer():
    data = request.get_json()
    # Check for existing customer with same name and email
    existing = db.fetch_one("SELECT id FROM customers WHERE name=%s AND email=%s", (data['name'], data.get('email')))
    if existing:
        return jsonify({'success': False, 'error': 'Customer with this name and email already exists.'}), 409
    query = "INSERT INTO customers (name, contact, email, address) VALUES (%s, %s, %s, %s)"
    customer_id = db.execute_query(query, (data['name'], data.get('contact'), data.get('email'), data.get('address')))
    return jsonify({'success': True, 'id': customer_id})

@app.route('/api/customers/<int:customer_id>', methods=['PUT'])
@login_required
def edit_customer(customer_id):
    data = request.get_json()
    query = "UPDATE customers SET name=%s, contact=%s, email=%s, address=%s WHERE id=%s"
    db.execute_query(query, (data['name'], data.get('contact'), data.get('email'), data.get('address'), customer_id))
    return jsonify({'success': True})

# --- Sales CRUD ---
@app.route('/api/sales', methods=['GET'])
@login_required
def get_sales():
    sales = db.fetch_all("SELECT s.*, c.name as customer_name FROM sales s JOIN customers c ON s.customer_id = c.id")
    return jsonify(sales)

@app.route('/api/sales', methods=['POST'])
@login_required
def add_sale():
    data = request.get_json()
    print("[DEBUG] Full request data (sales):", data)
    customer_id = data.get('customer_id') or data.get('customer')
    if not customer_id:
        print("[DEBUG] customer_id missing in request data (sales):", data)
        return jsonify({'success': False, 'error': 'customer_id is required'}), 400
    query = "INSERT INTO sales (date, customer_id, product, quantity, amount) VALUES (%s, %s, %s, %s, %s)"
    sale_id = db.execute_query(query, (data['date'], customer_id, data.get('product'), data.get('quantity'), data['amount']))
    # Send email notification for sale
    customer = db.fetch_one("SELECT name, email, address FROM customers WHERE id=%s", (customer_id,))
    print("[DEBUG] Customer fetched from DB (sale):", customer)
    if customer and customer.get('email'):
        subject = f"Sale Confirmation for {customer['name']}"
        body = (
            f"Dear {customer['name']},\n\n"
            f"Thank you for your purchase! Here are your sale details:\n"
            f"Date: {data['date']}\n"
            f"Product/Service: {data.get('product', '')}\n"
            f"Quantity: {data.get('quantity', '')}\n"
            f"Amount: {data.get('amount', '')}\n"
            f"Delivery Address: {customer.get('address', '')}\n\n"
            f"Best regards,\nBSF Farm Manager"
        )
        send_email(subject, body, [customer['email'], ADMIN_EMAIL])
    return jsonify({'success': True, 'id': sale_id})

@app.route('/api/sales/<int:sale_id>', methods=['PUT'])
@login_required
def edit_sale(sale_id):
    data = request.get_json()
    print("[DEBUG] Full request data (sales):", data)
    customer_id = data.get('customer_id') or data.get('customer')
    if not customer_id:
        print("[DEBUG] customer_id missing in request data (sales):", data)
        return jsonify({'success': False, 'error': 'customer_id is required'}), 400
    query = "UPDATE sales SET date=%s, customer_id=%s, product=%s, quantity=%s, amount=%s WHERE id=%s"
    db.execute_query(query, (data['date'], customer_id, data.get('product'), data.get('quantity'), data['amount'], sale_id))
    return jsonify({'success': True})

# --- Deliveries CRUD ---
@app.route('/api/deliveries', methods=['GET'])
@login_required
def get_deliveries():
    deliveries = db.fetch_all("SELECT d.*, c.name as customer_name FROM deliveries d JOIN customers c ON d.customer_id = c.id")
    return jsonify(deliveries)

@app.route('/api/deliveries', methods=['POST'])
@login_required
def add_delivery():
    data = request.get_json()
    print("[DEBUG] Full request data:", data)
    customer_id = data.get('customer_id') or data.get('customer')
    if not customer_id:
        print("[DEBUG] customer_id missing in request data:", data)
        return jsonify({'success': False, 'error': 'customer_id is required'}), 400
    query = "INSERT INTO deliveries (date, customer_id, product, quantity, status, notes) VALUES (%s, %s, %s, %s, %s, %s)"
    delivery_id = db.execute_query(query, (data['date'], customer_id, data.get('product'), data.get('quantity'), data['status'], data.get('notes')))
    # Send email for any status
    customer = db.fetch_one("SELECT name, email, address FROM customers WHERE id=%s", (customer_id,))
    print("[DEBUG] Customer fetched from DB (delivery):", customer)
    if customer and customer.get('email'):
        subject = f"Delivery Update for {customer['name']}"
        body = (
            f"Dear {customer['name']},\n\n"
            f"Your delivery status is now: {data['status']}\n"
            f"Date of Delivery: {data['date']}\n"
            f"Product/Service: {data.get('product', '')}\n"
            f"Quantity: {data.get('quantity', '')}\n"
            f"Delivery Address: {customer.get('address', '')}\n\n"
            f"Best regards,\nBSF Farm Manager"
        )
        send_email(subject, body, [customer['email'], ADMIN_EMAIL])
    return jsonify({'success': True, 'id': delivery_id})

@app.route('/api/deliveries/<int:delivery_id>', methods=['PUT'])
@login_required
def edit_delivery(delivery_id):
    data = request.get_json()
    print("[DEBUG] Full request data:", data)
    customer_id = data.get('customer_id') or data.get('customer')
    if not customer_id:
        print("[DEBUG] customer_id missing in request data:", data)
        return jsonify({'success': False, 'error': 'customer_id is required'}), 400
    # Fetch previous status
    prev = db.fetch_one("SELECT status FROM deliveries WHERE id=%s", (delivery_id,))
    prev_status = prev['status'] if prev else None
    query = "UPDATE deliveries SET date=%s, customer_id=%s, product=%s, quantity=%s, status=%s, notes=%s WHERE id=%s"
    db.execute_query(query, (data['date'], customer_id, data.get('product'), data.get('quantity'), data['status'], data.get('notes'), delivery_id))
    print("[DEBUG] Delivery status received:", data['status'])
    # Send email if status is Delivered and was not previously Delivered
    if data['status'].strip().lower() == 'delivered' and (not prev_status or prev_status.strip().lower() != 'delivered'):
        customer = db.fetch_one("SELECT name, email, address FROM customers WHERE id=%s", (customer_id,))
        print("[DEBUG] Customer fetched from DB:", customer)
        if customer and customer.get('email'):
            subject = f"Delivery Confirmation for {customer['name']}"
            body = (
                f"Dear {customer['name']},\n\n"
                f"Your delivery has been completed. Here are your delivery details:\n"
                f"Date of Delivery: {data['date']}\n"
                f"Product/Service: {data.get('product', '')}\n"
                f"Quantity: {data.get('quantity', '')}\n"
                f"Delivery Address: {customer.get('address', '')}\n\n"
                f"Best regards,\nBSF Farm Manager"
            )
            send_email(subject, body, [customer['email'], ADMIN_EMAIL])
    return jsonify({'success': True})

# --- Customer Feedback CRUD ---
@app.route('/api/feedback', methods=['GET'])
@login_required
def get_feedback():
    feedback = db.fetch_all("SELECT f.*, c.name as customer_name FROM customer_feedback f JOIN customers c ON f.customer_id = c.id")
    return jsonify(feedback)

@app.route('/api/feedback', methods=['POST'])
@login_required
def add_feedback():
    data = request.get_json()
    query = "INSERT INTO customer_feedback (date, customer_id, feedback, rating) VALUES (%s, %s, %s, %s)"
    feedback_id = db.execute_query(query, (data['date'], data['customer_id'], data['feedback'], data['rating']))
    return jsonify({'success': True, 'id': feedback_id})

@app.route('/api/feedback/<int:feedback_id>', methods=['PUT'])
@login_required
def edit_feedback(feedback_id):
    data = request.get_json()
    query = "UPDATE customer_feedback SET date=%s, customer_id=%s, feedback=%s, rating=%s WHERE id=%s"
    db.execute_query(query, (data['date'], data['customer_id'], data['feedback'], data['rating'], feedback_id))
    return jsonify({'success': True})

@app.errorhandler(400)
def bad_request(e):
    # Custom error response for 400
    return jsonify(error=str(e), success=False), 400

@app.errorhandler(404)
def not_found(e):
    # Custom error response for 404
    return jsonify(error="Resource not found", success=False), 404
    
@app.errorhandler(409)
def conflict(e):
    # Custom error response for 409
    return jsonify(error=str(e), success=False), 409

@app.errorhandler(500)
def internal_server_error(e):
    # Custom error response for 500
    logger.error(f"Internal Server Error: {e}")
    return jsonify(error="Internal server error", success=False), 500

@app.errorhandler(Exception)
def handle_general_exception(e):
    # This will catch any exception not already handled
    logger.error(f"An unhandled exception occurred: {e}")
    return jsonify(error="An unexpected error occurred", success=False), 500

def send_email(subject, body, to_emails):
    print(f"[DEBUG] Preparing to send email to: {to_emails}")
    msg = MIMEMultipart()
    msg['From'] = EMAIL_HOST_USER
    msg['To'] = ', '.join(to_emails) if isinstance(to_emails, list) else to_emails
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        print("[DEBUG] Logged in to SMTP server.")
        server.sendmail(EMAIL_HOST_USER, to_emails, msg.as_string())
        print("[DEBUG] Email sent successfully.")
        server.quit()
        logger.info(f"Email sent to {to_emails}")
    except Exception as e:
        print(f"[DEBUG] Failed to send email: {e}")
        logger.error(f"Failed to send email: {e}")

@app.route('/api/send-harvest-report', methods=['POST'])
@login_required
def send_harvest_report():
    # Perform the same analysis as /api/statistics/harvest-efficiency
    try:
        # Query to get harvest yield data with correct column names
        query = "SELECT tray_batch_id, harvest_date, larvae_collected_kg, processing_method, storage_temperature_celsius FROM feeding_harvest_yield ORDER BY harvest_date DESC"
        data = db.fetch_all(query)
        if not data:
            summary = "No harvest yield records found."
        else:
            summary = f"Harvest Yield Report ({datetime.now().date()}):\n\n"
            for item in data:
                summary += (
                    f"Tray/Batch ID: {item.get('tray_batch_id', '')}, "
                    f"Date: {item.get('harvest_date', '')}, "
                    f"Larvae Collected: {item.get('larvae_collected_kg', '')} kg, "
                    f"Processing Method: {item.get('processing_method', '')}, "
                    f"Storage Temp: {item.get('storage_temperature_celsius', 'N/A')}°C\n"
                )
        subject = f"Harvest Yield Report ({datetime.now().date()})"
        send_email(subject, summary, ADMIN_EMAIL)
        return jsonify({'success': True, 'message': 'Harvest report sent to admin.'})
    except Exception as e:
        print(f"[DEBUG] Failed to send harvest report: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # It's recommended to use a production-ready WSGI server like Gunicorn or Waitress
    # For development, Flask's built-in server is fine.
    app.run(debug=True, port=5000) 