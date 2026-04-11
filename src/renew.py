# ================================================
# src/renew.py
# Book Renewal Logic
# ================================================

import psycopg2
from datetime import timedelta
from src.db import get_cursor

# Max number of times a book can be renewed
MAX_RENEWALS = 2

# ================================================
# Renew Book
# Extends the due date by 14 more days
# Max 2 renewals allowed per borrow
# ================================================
def renew_book(record_id, student_id):
    conn, cursor = get_cursor()
    try:
        # Begin transaction
        conn.autocommit = False

        # ----------------------------------------
        # STEP 1: Fetch and lock the record
        # ----------------------------------------
        cursor.execute("""
            SELECT
                br.record_id,
                br.copy_id,
                br.due_date,
                br.renewed_count,
                br.status,
                bc.copy_number,
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
        # STEP 2: Validate record exists
        # ----------------------------------------
        if not record:
            conn.rollback()
            return {
                "success" : False,
                "message" : "No active borrowing record found."
            }

        # ----------------------------------------
        # STEP 3: Check renewal limit
        # ----------------------------------------
        if record["renewed_count"] >= MAX_RENEWALS:
            conn.rollback()
            return {
                "success" : False,
                "message" : f"Maximum renewals ({MAX_RENEWALS}) reached for this book."
            }

        # ----------------------------------------
        # STEP 4: Calculate new due date
        # Extends from current due date (not today)
        # ----------------------------------------
        new_due_date = record["due_date"] + timedelta(days=14)

        # ----------------------------------------
        # STEP 5: Update the borrowing record
        # ----------------------------------------
        cursor.execute("""
            UPDATE borrowing_records
            SET
                due_date      = %s,
                renewed_count = renewed_count + 1
            WHERE record_id = %s
        """, (new_due_date, record_id))

        # ----------------------------------------
        # STEP 6: Commit
        # ----------------------------------------
        conn.commit()

        return {
            "success"       : True,
            "message"       : f"'{record['title']}' renewed successfully!",
            "title"         : record["title"],
            "copy_number"   : record["copy_number"],
            "new_due_date"  : new_due_date,
            "renewals_left" : MAX_RENEWALS - (record["renewed_count"] + 1)
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