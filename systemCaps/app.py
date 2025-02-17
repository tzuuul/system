from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong, random secret key

# Function to get a database connection
def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',          # XAMPP default user; update if necessary
        password='',          # XAMPP default is empty; update if necessary
        database='mydatabase' # Replace with your actual database name
    )
    return connection

# Redirect the root URL to login page
@app.route('/')
def home():
    return redirect(url_for('login'))

# Login route: handles both GET (display form) and POST (process form)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Retrieve form data (make sure the input names match those in your HTML)
        email = request.form.get('login-email')
        password = request.form.get('login-password')
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE email = %s AND password = %s"
        cursor.execute(query, (email, password))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if user:
            session['user_id'] = user['id']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('login'))
    
    # GET request: render the login page
    return render_template('login.html')

# Register route: handles both GET and POST
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('register-email')
        password = request.form.get('register-password')
        confirm_password = request.form.get('confirm-password')
        
        # Basic check for password confirmation
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for('register'))
        
        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
            cursor.execute(query, (name, email, password))
            connection.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            flash("Error: " + str(err), "danger")
            return redirect(url_for('register'))
        finally:
            cursor.close()
            connection.close()
    
    # GET request: render the register page
    return render_template('register.html')

# Simple dashboard page for logged-in users
@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return "Welcome to your dashboard!"
    else:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))

# Logout route to clear the session
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
