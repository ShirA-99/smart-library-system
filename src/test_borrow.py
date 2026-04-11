# test_borrow.py — delete this after testing
import sys
sys.path.append(".")

from src.borrow import get_all_books, check_availability, get_student

# Test 1: Get all books
print("\n--- ALL BOOKS ---")
books = get_all_books()
for book in books:
    print(f"{book['title']} | Available: {book['available_copies']}/{book['total_copies']}")

# Test 2: Check availability of book 1
print("\n--- AVAILABILITY (Book ID 1) ---")
copies = check_availability(1)
for copy in copies:
    print(f"Copy: {copy['copy_number']} | Status: {copy['status']}")

# Test 3: Get student
print("\n--- STUDENT LOOKUP ---")
student = get_student("STU001")
print(f"Student: {student['full_name']} | Email: {student['email']}")