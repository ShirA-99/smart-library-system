# ================================================
# src/borrow.py
# Book Borrowing Logic with Concurrency Control
# ================================================

import psycopg2
from datetime import datetime, timedelta
from src.db import get_cursor

# ================================================
# Search Books
# Returns all books matching a title keyword
# ================================================
def search_books(keyword):
    conn, cursor = get_cursor()
    try:
        cursor.execute("""
            SELECT 
                b.book_id,
                b.title,
                b.author,
                b.category,
                b.isbn,
                COUNT(bc.copy_id) AS total_copies,
                SUM(CASE WHEN bc.status = 'available' THEN 1 ELSE 0 END) AS available_copies
            FROM books b
            JOIN book_copies bc ON b.book_id = bc.book_id
            WHERE LOWER(b.title) LIKE LOWER(%s)
               OR LOWER(b.author) LIKE LOWER(%s)
               OR LOWER(b.category) LIKE LOWER(%s)
            GROUP BY b.book_id, b.title, b.author, b.category, b.isbn
            ORDER BY b.title
        """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))

        results = cursor.fetchall()
        return results

    finally:
        cursor.close()
        conn.close()

# ================================================
# Get All Books
# Returns all books with availability
# ================================================
def get_all_books():
    conn, cursor = get_cursor()
    try:
        cursor.execute("""
            SELECT 
                b.book_id,
                b.title,
                b.author,
                b.category,
                b.isbn,
                COUNT(bc.copy_id) AS total_copies,
                SUM(CASE WHEN bc.status = 'available' THEN 1 ELSE 0 END) AS available_copies
            FROM books b
            JOIN book_copies bc ON b.book_id = bc.book_id
            GROUP BY b.book_id, b.title, b.author, b.category, b.isbn
            ORDER BY b.title
        """)
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

# ================================================
# Check Availability
# Returns available copies of a specific book
# ================================================
def check_availability(book_id):
    conn, cursor = get_cursor()
    try:
        cursor.execute("""
            SELECT 
                bc.copy_id,
                bc.copy_number,
                bc.status,
                bc.version
            FROM book_copies bc
            WHERE bc.book_id = %s
              AND bc.status = 'available'
            ORDER BY bc.copy_id
        """, (book_id,))

        copies = cursor.fetchall()
        return copies

    finally:
        cursor.close()
        conn.close()

# ================================================
# Borrow Book — PESSIMISTIC LOCKING
# Uses SELECT FOR UPDATE to lock the row
# Prevents two kiosks borrowing the same copy
# ================================================
def borrow_book(book_id, student_id):
    conn, cursor = get_cursor()
    try:
        # Begin transaction
        conn.autocommit = False

        # ----------------------------------------
        # STEP 1: Check if student already has
        # an active borrow for this book
        # ----------------------------------------
        cursor.execute("""
            SELECT br.record_id
            FROM borrowing_records br
            JOIN book_copies bc ON br.copy_id = bc.copy_id
            WHERE bc.book_id = %s
              AND br.student_id = %s
              AND br.status = 'active'
        """, (book_id, student_id))

        existing = cursor.fetchone()
        if existing:
            conn.rollback()
            return {
                "success" : False,
                "message" : "You already have an active borrow for this book."
            }

        # ----------------------------------------
        # STEP 2: Lock an available copy
        # SELECT FOR UPDATE locks the row so no
        # other transaction can touch it until
        # this transaction commits or rolls back
        # ----------------------------------------
        cursor.execute("""
            SELECT 
                bc.copy_id,
                bc.copy_number,
                bc.version
            FROM book_copies bc
            WHERE bc.book_id = %s
              AND bc.status = 'available'
            ORDER BY bc.copy_id
            LIMIT 1
            FOR UPDATE SKIP LOCKED
        """, (book_id,))

        copy = cursor.fetchone()

        # ----------------------------------------
        # STEP 3: If no copy available, abort
        # ----------------------------------------
        if not copy:
            conn.rollback()
            return {
                "success" : False,
                "message" : "Sorry, no copies are available right now."
            }

        # ----------------------------------------
        # STEP 4: Update copy status to borrowed
        # Also increment version (optimistic lock)
        # ----------------------------------------
        cursor.execute("""
            UPDATE book_copies
            SET 
                status       = 'borrowed',
                version      = version + 1,
                last_updated = CURRENT_TIMESTAMP
            WHERE copy_id = %s
              AND version  = %s
        """, (copy["copy_id"], copy["version"]))

        # If no rows updated, version mismatch
        # means another transaction already took it
        if cursor.rowcount == 0:
            conn.rollback()
            return {
                "success" : False,
                "message" : "Sorry, this copy was just taken. Please try again."
            }

        # ----------------------------------------
        # STEP 5: Create borrowing record
        # ----------------------------------------
        due_date = datetime.now() + timedelta(days=14)

        cursor.execute("""
            INSERT INTO borrowing_records 
                (copy_id, student_id, due_date, status)
            VALUES 
                (%s, %s, %s, 'active')
            RETURNING record_id, borrowed_at, due_date
        """, (copy["copy_id"], student_id, due_date))

        record = cursor.fetchone()

        # ----------------------------------------
        # STEP 6: Commit transaction
        # Lock is released here
        # ----------------------------------------
        conn.commit()

        return {
            "success"     : True,
            "message"     : "Book borrowed successfully!",
            "record_id"   : record["record_id"],
            "copy_number" : copy["copy_number"],
            "borrowed_at" : record["borrowed_at"],
            "due_date"    : record["due_date"]
        }

    except psycopg2.Error as e:
        conn.rollback()
        return {
            "success" : False,
            "message" : f"Transaction error: {str(e)}"
        }

    finally:
        cursor.close()
        conn.close()

# ================================================
# Get Student Active Borrows
# Returns all books currently borrowed by student
# ================================================
def get_student_borrows(student_id):
    conn, cursor = get_cursor()
    try:
        cursor.execute("""
            SELECT
                br.record_id,
                b.title,
                b.author,
                bc.copy_number,
                br.borrowed_at,
                br.due_date,
                br.renewed_count,
                br.status,
                CASE 
                    WHEN br.due_date < CURRENT_TIMESTAMP THEN 'Overdue'
                    WHEN br.due_date < CURRENT_TIMESTAMP + INTERVAL '3 days' THEN 'Due Soon'
                    ELSE 'On Time'
                END AS due_status
            FROM borrowing_records br
            JOIN book_copies bc ON br.copy_id = bc.copy_id
            JOIN books b ON bc.book_id = b.book_id
            WHERE br.student_id = %s
              AND br.status = 'active'
            ORDER BY br.due_date ASC
        """, (student_id,))

        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

# ================================================
# Get Student by Student Number
# ================================================
def get_student(student_number):
    conn, cursor = get_cursor()
    try:
        cursor.execute("""
            SELECT * FROM students
            WHERE student_number = %s
        """, (student_number,))
        return cursor.fetchone()

    finally:
        cursor.close()
        conn.close()