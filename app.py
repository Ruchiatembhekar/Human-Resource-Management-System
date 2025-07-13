from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, send_file
import os
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image
import io
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Setup SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hrms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    department = db.Column(db.String(100))
    role = db.Column(db.String(20), default='employee')  # 'owner', 'hr', or 'employee'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.username}>'
        
    # Helper properties for role checking
    @property
    def is_owner(self):
        return self.role == 'owner'
        
    @property
    def is_hr(self):
        return self.role == 'hr'
        
    @property
    def is_admin(self):
        return self.role in ['owner', 'hr']

# Define Employee Model
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    designation = db.Column(db.String(100))
    department = db.Column(db.String(100))
    category = db.Column(db.String(50))  # 'technical', 'non_technical', or 'student'
    skills = db.Column(db.String(200))
    joining_date = db.Column(db.Date, default=datetime.utcnow)
    address = db.Column(db.String(200))
    salary = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    def __repr__(self):
        return f'<Employee {self.name}>'

# Role-based access control decorator
def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'username' not in session:
                flash('Please login to access this page', 'error')
                return redirect(url_for('login_page'))
                
            # Get the current user
            user = User.query.filter_by(username=session['username']).first()
            
            if not user or user.role not in roles:
                flash('You do not have permission to access this page', 'error')
                return redirect(url_for('dashboard'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/')
def login():
    return redirect(url_for('login_page'))

@app.route('/login', methods=['GET'])
def login_page():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')  # This is your login page

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('Please login to access the dashboard', 'error')
        return redirect(url_for('login_page'))
    
    username = session['username']
    user = User.query.filter_by(username=username).first()
    
    # Get counts for dashboard display
    tech_count = Employee.query.filter_by(category='technical').count()
    non_tech_count = Employee.query.filter_by(category='non_technical').count()
    student_count = Employee.query.filter_by(category='student').count()
    
    return render_template('dashboard.html', 
                          username=username, 
                          name=f"{user.first_name} {user.last_name}",
                          role=user.role,
                          tech_count=tech_count,
                          non_tech_count=non_tech_count,
                          student_count=student_count)

@app.route('/login', methods=['POST'])
def process_login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Find user in database
    user = User.query.filter_by(username=username).first()
    
    if user and check_password_hash(user.password, password):
        session['username'] = username
        session['role'] = user.role
        return redirect(url_for('dashboard'))
    
    flash('Invalid username or password', 'error')
    return redirect(url_for('login_page'))

@app.route('/register', methods=['POST'])
def register():
    first_name = request.form.get('firstName')
    last_name = request.form.get('lastName')
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')
    department = request.form.get('department')
    
    # Check if username already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        flash('Username already exists', 'error')
        return redirect(url_for('register_page'))
    
    # Create new user
    new_user = User(
        username=username,
        password=generate_password_hash(password),
        first_name=first_name,
        last_name=last_name,
        email=email,
        department=department,
        role='employee'  # Default role is employee
    )
    
    try:
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login_page'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error during registration: {str(e)}', 'error')
        return redirect(url_for('register_page'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login_page'))

# Employee Routes
@app.route('/employees')
@role_required('owner', 'hr')
def employees():
    # Get all employees
    employees = Employee.query.all()
    
    # Separate employees by category
    technical_employees = Employee.query.filter_by(category='technical').all()
    non_technical_employees = Employee.query.filter_by(category='non_technical').all()
    students = Employee.query.filter_by(category='student').all()
    
    return render_template('employees.html', 
                          technical_employees=technical_employees,
                          non_technical_employees=non_technical_employees,
                          students=students)

@app.route('/employees/technical')
@role_required('owner', 'hr')
def technical_employees():
    technical_employees = Employee.query.filter_by(category='technical').all()
    return render_template('technical_employees.html', employees=technical_employees)

@app.route('/employees/non_technical')
@role_required('owner', 'hr')
def non_technical_employees():
    non_technical_employees = Employee.query.filter_by(category='non_technical').all()
    return render_template('non_technical_employees.html', employees=non_technical_employees)

@app.route('/employees/students')
@role_required('owner', 'hr')
def student_employees():
    students = Employee.query.filter_by(category='student').all()
    return render_template('student_employees.html', employees=students)

@app.route('/employees/add', methods=['GET', 'POST'])
@role_required('owner', 'hr')
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        designation = request.form['designation']
        department = request.form['department']
        category = request.form['category']
        skills = request.form['skills']
        joining_date = datetime.strptime(request.form['joining_date'], '%Y-%m-%d') if request.form['joining_date'] else datetime.utcnow()
        address = request.form['address']
        salary = float(request.form['salary']) if request.form['salary'] else 0
        
        # Create new employee
        new_employee = Employee(
            name=name,
            email=email,
            phone=phone,
            designation=designation,
            department=department,
            category=category,
            skills=skills,
            joining_date=joining_date,
            address=address,
            salary=salary
        )
        
        # Check if we should also create a user account for this employee
        create_account = request.form.get('create_account')
        
        try:
            db.session.add(new_employee)
            db.session.commit()
            
            # Create user account if requested
            if create_account:
                # Generate username from email (part before @)
                username = email.split('@')[0]
                
                # Generate default password (can be changed later)
                default_password = f"{username}123"
                
                # Create user
                first_name, last_name = name.split(' ', 1) if ' ' in name else (name, "")
                
                new_user = User(
                    username=username,
                    password=generate_password_hash(default_password),
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    department=department,
                    role='employee'  # Default role for new users
                )
                
                db.session.add(new_user)
                db.session.commit()
                
                # Link employee to user
                new_employee.user_id = new_user.id
                db.session.commit()
                
                flash(f'Employee added with user account. Username: {username}, Password: {default_password}', 'success')
            else:
                flash('Employee added successfully!', 'success')
                
            return redirect(url_for('employees'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding employee: {str(e)}', 'danger')
    
    return render_template('add_employee.html')

@app.route('/employees/edit/<int:id>', methods=['GET', 'POST'])
@role_required('owner', 'hr')
def edit_employee(id):
    employee = Employee.query.get_or_404(id)
    
    if request.method == 'POST':
        employee.name = request.form['name']
        employee.email = request.form['email']
        employee.phone = request.form['phone']
        employee.designation = request.form['designation']
        employee.department = request.form['department']
        employee.category = request.form['category']
        employee.skills = request.form['skills']
        employee.joining_date = datetime.strptime(request.form['joining_date'], '%Y-%m-%d') if request.form['joining_date'] else employee.joining_date
        employee.address = request.form['address']
        employee.salary = float(request.form['salary']) if request.form['salary'] else employee.salary
        
        try:
            db.session.commit()
            
            # Update user info if there's a linked user
            if employee.user_id:
                user = User.query.get(employee.user_id)
                if user:
                    first_name, last_name = employee.name.split(' ', 1) if ' ' in employee.name else (employee.name, "")
                    user.first_name = first_name
                    user.last_name = last_name
                    user.email = employee.email
                    user.department = employee.department
                    db.session.commit()
            
            flash('Employee updated successfully!', 'success')
            return redirect(url_for('employees'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating employee: {str(e)}', 'danger')
    
    return render_template('edit_employee.html', employee=employee)

@app.route('/employees/delete/<int:id>')
@role_required('owner')  # Only owner can delete employees
def delete_employee(id):
    employee = Employee.query.get_or_404(id)
    
    try:
        # If employee has a user account, delete it too
        if employee.user_id:
            user = User.query.get(employee.user_id)
            if user:
                db.session.delete(user)
        
        db.session.delete(employee)
        db.session.commit()
        flash('Employee deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting employee: {str(e)}', 'danger')
    
    return redirect(url_for('employees'))

@app.route('/leave_management')
def leave_management():
    # Your leave management code here
    return render_template('leave_management.html')

@app.route('/payroll')
def payroll():
    # Your payroll code here
    return render_template('payroll.html')



# Create owner and HR users
def create_admin_users():
    # Check if owner already exists
    owner = User.query.filter_by(role='owner').first()
    if not owner:
        owner_user = User(
            username='owner',
            password=generate_password_hash('owner123'),
            first_name='Site',
            last_name='Owner',
            email='owner@example.com',
            department='Administration',
            role='owner'
        )
        
        try:
            db.session.add(owner_user)
            db.session.commit()
            print("Owner user created successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating owner user: {str(e)}")
    
    # Check if HR already exists
    hr = User.query.filter_by(role='hr').first()
    if not hr:
        hr_user = User(
            username='hr',
            password=generate_password_hash('hr123'),
            first_name='HR',
            last_name='Manager',
            email='hr@example.com',
            department='Human Resources',
            role='hr'
        )
        
        try:
            db.session.add(hr_user)
            db.session.commit()
            print("HR user created successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating HR user: {str(e)}")

@app.route('/attendance')
@role_required('owner', 'hr')
def attendance():
    # Your attendance tracking logic here
    return render_template('attendance.html')

@app.route('/reports')
@role_required('owner', 'hr')
def reports():
    # Basic reports functionality
    return render_template('reports.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin_users()
    app.run(debug=True)