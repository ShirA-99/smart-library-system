# ================================================
# src/return_book.py
# Book Return Logic
# ================================================

import psycopg2
from src.db import get_cursor

# ================================================
# Return Book
# Marks a borrowed copy as returned
# Updates both borrowing_records and book_copies
# ================================================
def return_book(record_id, student_id):
    conn, cursor = get_cursor()
    try:
        # Begin transaction
        conn.autocommit = False

        # ----------------------------------------
        # STEP 1: Verify the record exists and
        # belongs to this student
        # ----------------------------------------
        cursor.execute("""
            SELECT
                br.record_id,
                br.copy_id,
                br.student_id,
                br.borrowed_at,
                br.due_date,
                br.status,
                bc.copy_number,
                bc.version,
                b.title
            FROM borrowing_records br
            JOIN book_copies bc ON br.copy_id = bc.copy_id
            JOIN books b ON bc.book_id = b.book_id
            WHERE br.record_id  = %s
              AND br.student_id = %s
              AND br.status     = 'active'
            FOR UPDATE
        """, (record_id, student_id))

        record = cursor.fetchone()

        # ----------------------------------------
        # STEP 2: If no record found, abort
        # ----------------------------------------
        if not record:
            conn.rollback()
            return {
                "success" : False,
                "message" : "No active borrowing record found."
            }

        # ----------------------------------------
        # STEP 3: Mark borrowing record as returned
        # ----------------------------------------
        cursor.execute("""
            UPDATE borrowing_records
            SET
                status      = 'returned',
                returned_at = CURRENT_TIMESTAMP
            WHERE record_id = %s
        """, (record_id,))

        # ----------------------------------------
        # STEP 4: Mark book copy as available again
        # Also increment version number
        # ----------------------------------------
        cursor.execute("""
            UPDATE book_copies
            SET
                status       = 'available',
                version      = version + 1,
                last_updated = CURRENT_TIMESTAMP
            WHERE copy_id = %s
              AND version  = %s
        """, (record["copy_id"], record["version"]))

        if cursor.rowcount == 0:
            conn.rollback()
            return {
                "success" : False,
                "message" : "Version conflict detected. Please try again."
            }

        # ----------------------------------------
        # STEP 5: Commit transaction
        # ----------------------------------------
        conn.commit()

        return {
            "success"     : True,
            "message"     : f"'{record['title']}' returned successfully!",
            "title"       : record["title"],
            "copy_number" : record["copy_number"],
            "borrowed_at" : record["borrowed_at"],
            "returned_at" : "Just now"
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
# Get Borrowing History
# Returns all past and active borrows for student
# ================================================
def get_borrow_history(student_id):
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
                br.returned_at,
                br.renewed_count,
                br.status
            FROM borrowing_records br
            JOIN book_copies bc ON br.copy_id = bc.copy_id
            JOIN books b ON bc.book_id = b.book_id
            WHERE br.student_id = %s
            ORDER BY br.borrowed_at DESC
        """, (student_id,))

        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()