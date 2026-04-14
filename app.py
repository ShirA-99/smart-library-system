# ================================================
# app.py
# Smart Library Self-Service System
# Flask Web Application
# ================================================

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sys
import os

sys.path.append(".")

from src.borrow      import search_books, get_all_books, borrow_book, get_student_borrows, get_student
from src.return_book  import return_book, get_borrow_history
from src.renew        import renew_book
from src.db           import get_cursor

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "smart-library-secret-key-2024")

# ================================================
# Routes
# ================================================

@app.route("/")
def index():
    """Redirect to login or dashboard based on session."""
    if "student" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """Student login page."""
    if request.method == "POST":
        student_number = request.form.get("student_number", "").strip().upper()
        if not student_number:
            flash("Please enter your student number.", "error")
            return redirect(url_for("login"))

        student = get_student(student_number)
        if student:
            session["student"] = dict(student)
            flash(f"Welcome, {student['full_name']}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Student not found. Please check your student number.", "error")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Log the student out."""
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    """Main dashboard — Browse & Borrow books."""
    if "student" not in session:
        return redirect(url_for("login"))

    student = session["student"]
    search_query = request.args.get("q", "").strip()

    if search_query:
        books = search_books(search_query)
    else:
        books = get_all_books()

    # Convert RealDictRow to plain dicts for the template
    books = [dict(b) for b in books] if books else []

    return render_template("dashboard.html",
                           student=student,
                           books=books,
                           search_query=search_query,
                           active_tab="browse")


@app.route("/borrow/<int:book_id>", methods=["POST"])
def borrow(book_id):
    """Borrow a book."""
    if "student" not in session:
        return redirect(url_for("login"))

    student = session["student"]
    result = borrow_book(book_id, student["student_id"])

    if result["success"]:
        flash(f"{result['message']} (Copy: {result['copy_number']}, Due: {result['due_date'].strftime('%d %b %Y')})", "success")
    else:
        flash(result["message"], "error")

    return redirect(url_for("dashboard"))


@app.route("/returns")
def returns():
    """Return books page."""
    if "student" not in session:
        return redirect(url_for("login"))

    student = session["student"]
    borrows = get_student_borrows(student["student_id"])
    borrows = [dict(b) for b in borrows] if borrows else []

    return render_template("returns.html",
                           student=student,
                           borrows=borrows,
                           active_tab="returns")


@app.route("/return/<int:record_id>", methods=["POST"])
def return_action(record_id):
    """Process a book return."""
    if "student" not in session:
        return redirect(url_for("login"))

    student = session["student"]
    result = return_book(record_id, student["student_id"])

    if result["success"]:
        flash(result["message"], "success")
    else:
        flash(result["message"], "error")

    return redirect(url_for("returns"))


@app.route("/renew")
def renew_page():
    """Renew books page."""
    if "student" not in session:
        return redirect(url_for("login"))

    student = session["student"]
    borrows = get_student_borrows(student["student_id"])
    borrows = [dict(b) for b in borrows] if borrows else []

    return render_template("renew.html",
                           student=student,
                           borrows=borrows,
                           active_tab="renew")


@app.route("/renew/<int:record_id>", methods=["POST"])
def renew_action(record_id):
    """Process a book renewal."""
    if "student" not in session:
        return redirect(url_for("login"))

    student = session["student"]
    result = renew_book(record_id, student["student_id"])

    if result["success"]:
        flash(f"{result['message']} (New due: {result['new_due_date'].strftime('%d %b %Y')}, Renewals left: {result['renewals_left']})", "success")
    else:
        flash(result["message"], "error")

    return redirect(url_for("renew_page"))


@app.route("/history")
def history():
    """Borrowing history page."""
    if "student" not in session:
        return redirect(url_for("login"))

    student = session["student"]
    records = get_borrow_history(student["student_id"])
    records = [dict(r) for r in records] if records else []

    return render_template("history.html",
                           student=student,
                           records=records,
                           active_tab="history")


# ================================================
# Concurrency Demo Routes
# ================================================

@app.route("/demo")
def demo_page():
    """Live Concurrency Simulation Demo Page."""
    if "student" not in session:
        return redirect(url_for("login"))
    
    student = session["student"]
    return render_template("demo.html", student=student, active_tab="demo")

@app.route("/api/demo/reset", methods=["POST"])
def demo_reset():
    """Reset database to initial state for demo."""
    conn, cursor = get_cursor()
    try:
        conn.autocommit = False
        cursor.execute("UPDATE borrowing_records SET status = 'returned', returned_at = CURRENT_TIMESTAMP WHERE status = 'active'")
        cursor.execute("UPDATE book_copies SET status = 'available', version = version + 1, last_updated = CURRENT_TIMESTAMP")
        conn.commit()
        return jsonify({"success": True, "message": "Database reset: All copies available."})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route("/api/demo/availability/<int:book_id>")
def demo_availability(book_id):
    """Get real-time availability of a book."""
    conn, cursor = get_cursor()
    try:
        cursor.execute("""
            SELECT
                COUNT(*) FILTER (WHERE status = 'available') AS available,
                COUNT(*) FILTER (WHERE status = 'borrowed')  AS borrowed,
                COUNT(*)                                      AS total
            FROM book_copies
            WHERE book_id = %s
        """, (book_id,))
        return jsonify(dict(cursor.fetchone()))
    finally:
        cursor.close()
        conn.close()

@app.route("/api/demo/borrow", methods=["POST"])
def demo_borrow():
    """Execute a borrow for a specific student and book."""
    data = request.get_json()
    book_id = data.get("book_id")
    student_id = data.get("student_id")
    
    if not book_id or not student_id:
        return jsonify({"success": False, "message": "Missing book_id or student_id"}), 400

    import time
    start_time = time.time()
    
    result = borrow_book(book_id, student_id)
    
    elapsed_ms = round((time.time() - start_time) * 1000, 2)
    result["elapsed_ms"] = elapsed_ms
    
    return jsonify(result)


# ================================================
# Run
# ================================================
if __name__ == "__main__":
    app.run(debug=True, port=5000)