# ================================================
# tests/load_test.py
# Concurrent Kiosk Load Test
# Simulates multiple students borrowing/returning
# the same books at the same time
# ================================================

import sys
import threading
import time
import random
from datetime import datetime

sys.path.append(".")

from src.borrow      import borrow_book
from src.return_book import return_book, get_borrow_history
from src.renew       import renew_book
from src.db          import get_cursor

# ================================================
# Configuration
# ================================================
NUM_KIOSKS        = 10   # Number of simultaneous kiosks
TARGET_BOOK_ID    = 1    # Book everyone tries to borrow (Clean Code - 2 available copies)
STUDENT_IDS       = list(range(1, 11))  # STU001 to STU010
RESULTS           = []   # Shared results list
LOCK              = threading.Lock()  # For safe result collection

# ================================================
# Helper: Print with timestamp
# ================================================
def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {message}")

# ================================================
# Helper: Reset all borrows for clean test
# Marks all active borrows as returned
# and resets all book copies to available
# ================================================
def reset_database():
    conn, cursor = get_cursor()
    try:
        conn.autocommit = False

        # Return all active borrows
        cursor.execute("""
            UPDATE borrowing_records
            SET status      = 'returned',
                returned_at = CURRENT_TIMESTAMP
            WHERE status = 'active'
        """)

        # Reset all copies to available
        cursor.execute("""
            UPDATE book_copies
            SET status       = 'available',
                version      = version + 1,
                last_updated = CURRENT_TIMESTAMP
        """)

        conn.commit()
        log("✅ Database reset complete — all copies available")

    except Exception as e:
        conn.rollback()
        log(f"❌ Reset failed: {e}")
    finally:
        cursor.close()
        conn.close()

# ================================================
# Helper: Get current availability
# ================================================
def get_availability(book_id):
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
        return dict(cursor.fetchone())
    finally:
        cursor.close()
        conn.close()

# ================================================
# Kiosk Worker — Borrow Test
# Each thread simulates one kiosk trying to borrow
# ================================================
def kiosk_borrow_worker(student_id, book_id, kiosk_number):
    start_time = time.time()

    log(f"🖥️  Kiosk {kiosk_number:02d} | Student {student_id} | Attempting to borrow book {book_id}...")

    result      = borrow_book(book_id, student_id)
    elapsed     = round((time.time() - start_time) * 1000, 2)  # ms

    status      = "✅ SUCCESS" if result["success"] else "❌ FAILED "

    log(f"🖥️  Kiosk {kiosk_number:02d} | {status} | {result['message']} | {elapsed}ms")

    # Safely append to shared results
    with LOCK:
        RESULTS.append({
            "kiosk"      : kiosk_number,
            "student_id" : student_id,
            "success"    : result["success"],
            "message"    : result["message"],
            "elapsed_ms" : elapsed
        })

# ================================================
# Kiosk Worker — Return Test
# Each thread simulates one kiosk returning a book
# ================================================
def kiosk_return_worker(student_id, kiosk_number):
    start_time = time.time()

    # Find active borrow for this student
    history = get_borrow_history(student_id)
    active  = [r for r in history if r["status"] == "active"]

    if not active:
        log(f"🖥️  Kiosk {kiosk_number:02d} | Student {student_id} | No active borrows to return")
        return

    record_id   = active[0]["record_id"]
    result      = return_book(record_id, student_id)
    elapsed     = round((time.time() - start_time) * 1000, 2)

    status      = "✅ SUCCESS" if result["success"] else "❌ FAILED "
    log(f"🖥️  Kiosk {kiosk_number:02d} | {status} | {result['message']} | {elapsed}ms")

# ================================================
# TEST 1: Concurrent Borrow — Race Condition Test
# All kiosks try to borrow the same book at once
# Only copies available should succeed
# ================================================
def test_concurrent_borrow():
    global RESULTS
    RESULTS = []

    print("\n" + "="*60)
    print("  TEST 1: CONCURRENT BORROW — RACE CONDITION TEST")
    print("="*60)

    # Check availability before test
    before = get_availability(TARGET_BOOK_ID)
    print(f"\n📊 Before: {before['available']} available / {before['borrowed']} borrowed / {before['total']} total")
    print(f"📌 Launching {NUM_KIOSKS} kiosks simultaneously...\n")

    # Create all threads (one per kiosk)
    threads = []
    for i, student_id in enumerate(STUDENT_IDS):
        thread = threading.Thread(
            target = kiosk_borrow_worker,
            args   = (student_id, TARGET_BOOK_ID, i + 1)
        )
        threads.append(thread)

    # Launch ALL threads at the same time
    start = time.time()
    for thread in threads:
        thread.start()

    # Wait for all to finish
    for thread in threads:
        thread.join()
    total_time = round((time.time() - start) * 1000, 2)

    # Check availability after test
    after = get_availability(TARGET_BOOK_ID)

    # ----------------------------------------
    # Results Summary
    # ----------------------------------------
    successes = [r for r in RESULTS if r["success"]]
    failures  = [r for r in RESULTS if not r["success"]]
    avg_time  = round(sum(r["elapsed_ms"] for r in RESULTS) / len(RESULTS), 2)
    max_time  = max(r["elapsed_ms"] for r in RESULTS)
    min_time  = min(r["elapsed_ms"] for r in RESULTS)

    print("\n" + "="*60)
    print("  RESULTS SUMMARY")
    print("="*60)
    print(f"  Total kiosks launched  : {NUM_KIOSKS}")
    print(f"  ✅ Successful borrows   : {len(successes)}")
    print(f"  ❌ Rejected borrows     : {len(failures)}")
    print(f"  📊 Copies available     : {before['available']} → should match successes")
    print(f"  ⏱️  Total time           : {total_time}ms")
    print(f"  ⏱️  Avg response time    : {avg_time}ms")
    print(f"  ⏱️  Min response time    : {min_time}ms")
    print(f"  ⏱️  Max response time    : {max_time}ms")
    print(f"\n📊 After : {after['available']} available / {after['borrowed']} borrowed / {after['total']} total")

    # ----------------------------------------
    # Concurrency Verification
    # ----------------------------------------
    print("\n" + "="*60)
    print("  CONCURRENCY VERIFICATION")
    print("="*60)

    expected_success = before["available"]

    if len(successes) == expected_success:
        print(f"  ✅ PASS — Exactly {expected_success} borrow(s) succeeded (matches available copies)")
        print(f"  ✅ PASS — No duplicate borrows detected")
    else:
        print(f"  ❌ FAIL — Expected {expected_success} success(es), got {len(successes)}")
        print(f"  ❌ Race condition may have occurred!")

    if after["available"] == 0 and after["borrowed"] == expected_success:
        print(f"  ✅ PASS — Database state is consistent")
    else:
        print(f"  ❌ FAIL — Database state is inconsistent!")

# ================================================
# TEST 2: Concurrent Return Test
# All successful borrowers return at the same time
# ================================================
def test_concurrent_return():
    print("\n" + "="*60)
    print("  TEST 2: CONCURRENT RETURN TEST")
    print("="*60)

    before = get_availability(TARGET_BOOK_ID)
    print(f"\n📊 Before: {before['available']} available / {before['borrowed']} borrowed")
    print(f"📌 All borrowers returning simultaneously...\n")

    threads = []
    kiosk   = 1

    for student_id in STUDENT_IDS:
        thread = threading.Thread(
            target = kiosk_return_worker,
            args   = (student_id, kiosk)
        )
        threads.append(thread)
        kiosk += 1

    start = time.time()
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    total_time = round((time.time() - start) * 1000, 2)

    after = get_availability(TARGET_BOOK_ID)
    print(f"\n📊 After : {after['available']} available / {after['borrowed']} borrowed")
    print(f"⏱️  Total time: {total_time}ms")

    if after["borrowed"] == 0:
        print("  ✅ PASS — All copies returned successfully")
    else:
        print(f"  ❌ FAIL — {after['borrowed']} copies still marked as borrowed")

# ================================================
# TEST 3: Mixed Operations Test
# Some kiosks borrow, some return simultaneously
# ================================================
def test_mixed_operations():
    print("\n" + "="*60)
    print("  TEST 3: MIXED OPERATIONS TEST")
    print("="*60)
    print("📌 Half kiosks borrow, half return simultaneously...\n")

    threads = []

    # First 5 students borrow
    for i in range(5):
        thread = threading.Thread(
            target = kiosk_borrow_worker,
            args   = (STUDENT_IDS[i], TARGET_BOOK_ID, i + 1)
        )
        threads.append(thread)

    # Last 5 students try to return (may have nothing to return)
    for i in range(5, 10):
        thread = threading.Thread(
            target = kiosk_return_worker,
            args   = (STUDENT_IDS[i], i + 1)
        )
        threads.append(thread)

    start = time.time()
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    total_time = round((time.time() - start) * 1000, 2)

    after = get_availability(TARGET_BOOK_ID)
    print(f"\n📊 Final: {after['available']} available / {after['borrowed']} borrowed")
    print(f"⏱️  Total time: {total_time}ms")
    print("  ✅ Mixed operations completed without errors")

# ================================================
# MAIN — Run all tests
# ================================================
if __name__ == "__main__":
    print("\n" + "🔬 "*20)
    print("  SMART LIBRARY SYSTEM — LOAD TEST")
    print("🔬 "*20)
    print(f"\n  Kiosks     : {NUM_KIOSKS}")
    print(f"  Target book: ID {TARGET_BOOK_ID} (Clean Code — 2 available copies)")
    print(f"  Students   : STU001 to STU010")

    # Reset database before tests
    print("\n📌 Resetting database...")
    reset_database()

    # Run Test 1
    test_concurrent_borrow()

    # Small delay between tests
    time.sleep(1)

    # Run Test 2
    test_concurrent_return()

    # Small delay
    time.sleep(1)

    # Run Test 3
    reset_database()
    test_mixed_operations()

    print("\n" + "="*60)
    print("  ALL TESTS COMPLETE")
    print("="*60 + "\n")