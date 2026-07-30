
from flask import Flask, request, render_template, redirect, url_for, jsonify
from extensions import db
import os
from werkzeug.utils import secure_filename
from flask import send_from_directory
from flask_migrate import Migrate

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

# Import models after db initialization
from models import Upload_System, Registration, feedback

# Create database tables
with app.app_context():
    db.create_all()


# ---------------- HOME ----------------
@app.route('/')
def home():
    return render_template('Home.html')


# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    uploads = Upload_System.query.order_by(Upload_System.id.desc()).all()
    notes = [upload for upload in uploads if upload.Note_sharing or upload.Note_writing]
    assignments = [upload for upload in uploads if upload.Assignment_Sharing]
    return render_template('Dashboard.html', uploads=uploads, notes=notes, assignments=assignments)


# ---------------- REGISTER PAGE ----------------
@app.route('/register')
def register():
    return render_template('Register.html')


# ---------------- STUDENT LOGIN ----------------
@app.route('/student_login', methods=['GET', 'POST'])
def student_login():

    if request.method == 'POST':
        email = request.form.get('username')
        password = request.form.get('password')

        student = Registration.query.filter_by(Email=email).first()

        if student and student.password == password:
            return redirect(url_for('dashboard'))
        else:
            return "Invalid Email or Password"

    return render_template('Student_Login.html')


# ---------------- STUDENT LOGOUT ----------------
@app.route('/student_logout')
def student_logout():
    return render_template('Student_Logout.html')


# ---------------- FORGOT PASSWORD ----------------
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    message = None

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        student = Registration.query.filter_by(Email=email).first()

        if not student:
            message = 'No account found with that email.'
        elif len(new_password) < 4:
            message = 'Password must be at least 4 characters long.'
        elif new_password != confirm_password:
            message = 'Passwords do not match.'
        else:
            student.password = new_password
            student.Confirm_password = new_password
            db.session.commit()
            message = 'Password updated successfully. Please log in again.'

    return render_template('forgot_password.html', message=message)


# ---------------- REGISTER STUDENT ----------------
@app.route('/register_students', methods=['POST'])
def register_students():

    new_student = Registration(
        First_Name=request.form.get('firstName'),
        Last_Name=request.form.get('lastName'),
        Email=request.form.get('email'),
        phone_number=request.form.get('Contact'),
        password=request.form.get('password'),
        Confirm_password=request.form.get('confirmPassword')
    )

    db.session.add(new_student)
    db.session.commit()

    return redirect(url_for('student_login'))


# ---------------- UPLOAD PAGE ----------------
@app.route('/upload_system')
def upload_system():
    data = Upload_System.query.all()
    print(data)  # Debugging statement to check the retrieved data
    return render_template('Upload_System.html', data=data)


# ---------------- SAVE UPLOAD ----------------
@app.route('/upload_data', methods=['POST'])
def upload_data():
    print("Form data received:", request.form)  # Debugging statement to check form data
    if request.method == 'POST':
        category = request.form.get('noteCategory')
        note_text = request.form.get('noteText')
        comments = request.form.get('assignmentComments')

    print("Category:", category)  # Debugging statement to check the category
    note_file = request.files.get('noteFile')
    assignment_file = request.files.get('assignmentFile')

    note_filename = None
    assignment_filename = None

    if note_file:
        note_filename = secure_filename(note_file.filename)
        note_file.save(
            os.path.join(app.config['UPLOAD_FOLDER'], note_filename)
        )

    if assignment_file:
        assignment_filename = secure_filename(assignment_file.filename)
        assignment_file.save(
            os.path.join(app.config['UPLOAD_FOLDER'], assignment_filename)
        )


    new_upload = Upload_System(
        Note_sharing=note_filename,
        Note_writing=note_text,
        Assignment_Sharing=assignment_filename,
        category=category,
        Comments=comments
    )

    db.session.add(new_upload)
    db.session.commit()

    return redirect(url_for('upload_system'))

# ---------------- FEEDBACK ----------------
@app.route('/feedback', methods=['POST'])
def submit_feedback():

    new_feedback = feedback(
        Name=request.form.get('name'),
        Email=request.form.get('email'),
        Message=request.form.get('message')
    )

    db.session.add(new_feedback)
    db.session.commit()

    return redirect(url_for('home'))

@app.route('/download/<filename>')
def download_file(filename):

    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename,
        as_attachment=True
    )


@app.route('/delete_upload/<int:upload_id>', methods=['POST'])
def delete_upload(upload_id):
    upload = Upload_System.query.get_or_404(upload_id)

    if upload.Note_sharing:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], upload.Note_sharing)
        if os.path.exists(file_path):
            os.remove(file_path)

    if upload.Assignment_Sharing:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], upload.Assignment_Sharing)
        if os.path.exists(file_path):
            os.remove(file_path)

    db.session.delete(upload)
    db.session.commit()

    return redirect(url_for('dashboard'))


@app.route('/update-password', methods=['POST'])
def update_password():
    data = request.get_json()

    email = data.get('email')
    new_password = data.get('new_password')

    user = Registration.query.filter_by(Email=email).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    user.password = new_password
    user.Confirm_password = new_password
    db.session.commit()

    return jsonify({"message": "Password updated successfully"}), 200

@app.route("/api")
def api():
    return jsonify({
        "message": "Success",
        "status": 200
    })

if __name__ == '__main__':
    app.run(debug=True)