from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    topics = db.Column(db.Text, nullable=False)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password_hash, password):
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        return 'Invalid Credentials'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

@app.route('/guest', methods=['GET', 'POST'])
def guest():
    if request.method == 'POST':
        username = request.form['username']
        content = request.form['content']
        message = Message(username=username, content=content)
        db.session.add(message)
        db.session.commit()
        return redirect(url_for('guest'))
    return render_template('guest.html')

@app.route('/appointment', methods=['POST'])
def book_appointment():
    name = request.form['name']
    date = request.form['date']
    time = request.form['time']
    topics = request.form['topics']
    appointment = Appointment(name=name, date=date, time=time, topics=topics)
    db.session.add(appointment)
    db.session.commit()
    return redirect(url_for('guest'))

@app.route('/admin')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('login'))
    messages = Message.query.all()
    appointments = Appointment.query.all()
    return render_template('admin.html', messages=messages, appointments=appointments)

@app.route('/edit_admin', methods=['GET', 'POST'])
def edit_admin():
    if 'admin' not in session:
        return redirect(url_for('login'))
    admin = Admin.query.first()
    if request.method == 'POST':
        new_username = request.form['username']
        new_password = request.form['password']
        admin.username = new_username
        admin.password_hash = generate_password_hash(new_password)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_admin.html', admin=admin)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Admin.query.first():
            default_admin = Admin(username='admin', password_hash=generate_password_hash('password123'))
            db.session.add(default_admin)
            db.session.commit()
    app.run(debug=True)