from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os
app = Flask(__name__)
app.secret_key = "supersecretkey"

# Folders
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Fake databases
users = {
    "student": {},   # {username: password}
    "teacher": {}
}

# Example assignments added here
assignments = {
    1: {"title": "Math Assignment 1", "description": "Solve problems on algebra"},
    2: {"title": "English Essay", "description": "Write an essay about technology"},
    3: {"title": "Science Project", "description": "Submit a report on renewable energy"}
}

# Submissions = {student_username: {assignment_id: {"filename": "file", "grade": "A"}}}
submissions = {}

# ------------------- Home -------------------
@app.route("/")
def home():
    return render_template("home.html")

# ------------------- Signup -------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        role = request.form["role"]
        username = request.form["username"]
        password = request.form["password"]

        if username in users[role]:
            return "User already exists!"
        users[role][username] = password
        return redirect(url_for("login"))

    return render_template("signup.html")

# ------------------- Login -------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        role = request.form["role"]
        username = request.form["username"]
        password = request.form["password"]

        if username in users[role] and users[role][username] == password:
            session["username"] = username
            session["role"] = role
            if role == "student":
                return redirect(url_for("student_dashboard"))
            else:
                return redirect(url_for("teacher_dashboard"))
        else:
            return "Invalid username or password!"

    return render_template("login.html")

# ------------------- Logout -------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ------------------- Student Dashboard -------------------
@app.route("/student", methods=["GET", "POST"])
def student_dashboard():
    if "username" not in session or session["role"] != "student":
        return redirect(url_for("login"))

    if request.method == "POST":
        assignment_id = int(request.form["assignment_id"])
        file = request.files["file"]
        if file:
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)

            if session["username"] not in submissions:
                submissions[session["username"]] = {}
            submissions[session["username"]][assignment_id] = {
                "filename": file.filename,
                "grade": "Pending"
            }

    student_subs = submissions.get(session["username"], {})
    return render_template("student.html", assignments=assignments, student_subs=student_subs)

# ------------------- Teacher Dashboard -------------------
@app.route("/teacher", methods=["GET", "POST"])
def teacher_dashboard():
    if "username" not in session or session["role"] != "teacher":
        return redirect(url_for("login"))

    if request.method == "POST":
        if "title" in request.form:  # New assignment
            new_id = max(assignments.keys()) + 1 if assignments else 1
            assignments[new_id] = {
                "title": request.form["title"],
                "description": request.form["description"]
            }
        else:  # Grading
            student_name = request.form["student"]
            assignment_id = int(request.form["assignment_id"])
            grade = request.form["grade"]
            if student_name in submissions and assignment_id in submissions[student_name]:
                submissions[student_name][assignment_id]["grade"] = grade

    return render_template("teacher.html", assignments=assignments, submissions=submissions)

# ------------------- Download Submissions -------------------
@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

if __name__ == "__main__":
    app.run(debug=True)
