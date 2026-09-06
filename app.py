from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_

app = Flask(__name__)

app.secret_key = "student-job-portal-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///jobportal.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# =========================
# Student Table
# =========================
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


# =========================
# Application Table
# =========================
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), default="Applied")
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    skills = db.Column(db.String(200), nullable=False)
    reason = db.Column(db.Text, nullable=False)


# =========================
# Job Table
# =========================
class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    skills = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)


# =========================
# Create Database
# =========================
with app.app_context():
    db.create_all()

    # Add some sample jobs if they don't already exist
    sample_jobs = [
        {
            "title": "Python Developer",
            "company": "ABC Technologies",
            "location": "Chennai, India",
            "type": "Full Time",
            "skills": "Python, Flask, SQL",
            "description": "Develop and maintain Python web applications."
        },
        {
            "title": "Web Developer",
            "company": "Tech Solutions",
            "location": "Bangalore, India",
            "type": "Full Time",
            "skills": "HTML, CSS, JavaScript",
            "description": "Build and maintain modern websites."
        },
        {
            "title": "Data Analyst",
            "company": "Data Corp",
            "location": "Chennai, India",
            "type": "Full Time",
            "skills": "Python, Pandas, SQL",
            "description": "Analyze data and create useful business insights."
        },
        {
            "title": "Software Developer",
            "company": "Innovate Labs",
            "location": "Hyderabad, India",
            "type": "Full Time",
            "skills": "Python, Java, SQL",
            "description": "Develop software applications and solve technical problems."
        }
    ]

    for data in sample_jobs:
        existing_job = Job.query.filter_by(
            title=data["title"],
            company=data["company"]
        ).first()

        if not existing_job:
            db.session.add(Job(**data))

    db.session.commit()


# =========================
# Home
# =========================
@app.route("/")
def home():
    return render_template("index.html")


# =========================
# Jobs
# =========================
@app.route("/jobs")
def jobs():
    search = request.args.get("search", "").strip()

    if search:
        pattern = f"%{search}%"

        jobs = Job.query.filter(
            or_(
                Job.title.ilike(pattern),
                Job.company.ilike(pattern),
                Job.skills.ilike(pattern)
            )
        ).all()
    else:
        jobs = Job.query.all()

    return render_template("jobs.html", jobs=jobs)


# =========================
# Job Details
# =========================
@app.route("/job/<int:job_id>")
def job_details(job_id):
    job = db.session.get(Job, job_id)

    if job is None:
        return "Job not found", 404

    return render_template("job_details.html", job=job)


# =========================
# Login
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        student = Student.query.filter_by(email=email).first()

        if student and student.password == password:
            session["student_id"] = student.id
            session["student_name"] = student.name

            return redirect(url_for("dashboard"))

        return "Invalid email or password"

    return render_template("login.html")


# =========================
# Register
# =========================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        existing_student = Student.query.filter_by(email=email).first()

        if existing_student:
            return "Email already registered"

        student = Student(
            name=name,
            email=email,
            password=password
        )

        db.session.add(student)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


# =========================
# Dashboard
# =========================
@app.route("/dashboard")
def dashboard():
    if "student_id" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html")


# =========================
# Profile
# =========================
@app.route("/profile")
def profile():
    if "student_id" not in session:
        return redirect(url_for("login"))

    student = db.session.get(Student, session["student_id"])

    return render_template("profile.html", student=student)


# =========================
# Apply for Job
# =========================
@app.route("/apply", methods=["GET", "POST"])
def apply():
    if "student_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        job_title = request.form.get("job_title", "")

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        skills = request.form["skills"]
        reason = request.form["reason"]

        application = Application(
            job_title=job_title,
            name=name,
            email=email,
            phone=phone,
            skills=skills,
            reason=reason
        )

        db.session.add(application)
        db.session.commit()

        return "Application submitted successfully!"

    return render_template("apply.html")


# =========================
# My Applications
# =========================
@app.route("/applications")
def applications():
    if "student_id" not in session:
        return redirect(url_for("login"))

    applications = Application.query.filter_by(
        email=Student.query.get(session["student_id"]).email
    ).all()

    return render_template(
        "applications.html",
        applications=applications
    )


# =========================
# Logout
# =========================
@app.route("/logout")
def logout():
    session.clear()

    return redirect(url_for("login"))


# =========================
# Admin Login
# =========================
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            session["admin"] = True

            return redirect(url_for("admin_dashboard"))

        return "Invalid admin username or password"

    return render_template("admin_login.html")


# =========================
# Admin Dashboard
# =========================
@app.route("/admin/dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    return render_template("admin_dashboard.html")


# =========================
# Admin Applications
# =========================
@app.route("/admin/applications")
def admin_applications():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    applications = Application.query.all()

    return render_template(
        "admin_applications.html",
        applications=applications
    )


# =========================
# Update Application Status
# =========================
@app.route(
    "/admin/application/<int:application_id>/status",
    methods=["POST"]
)
def update_status(application_id):
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    application = db.session.get(Application, application_id)

    if application:
        application.status = request.form["status"]

        db.session.commit()

    return redirect(url_for("admin_applications"))


# =========================
# Add Job
# =========================
@app.route("/admin/add-job", methods=["GET", "POST"])
def add_job():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        title = request.form["title"]
        company = request.form["company"]
        location = request.form["location"]
        job_type = request.form["type"]
        skills = request.form["skills"]
        description = request.form["description"]

        job = Job(
            title=title,
            company=company,
            location=location,
            type=job_type,
            skills=skills,
            description=description
        )

        db.session.add(job)
        db.session.commit()

        return "Job added successfully!"

    return render_template("add_job.html")


# =========================
# Run Application
# =========================
if __name__ == "__main__":
    app.run(debug=True)