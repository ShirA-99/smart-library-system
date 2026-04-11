-- ================================================
-- Smart Library Self-Service System
-- Schema Definition
-- ================================================

-- Drop tables if they exist (for clean resets)
DROP TABLE IF EXISTS borrowing_records;
DROP TABLE IF EXISTS book_copies;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS students;

-- ================================================
-- Students Table
-- ================================================
CREATE TABLE students (
    student_id      SERIAL PRIMARY KEY,
    student_number  VARCHAR(20) UNIQUE NOT NULL,
    full_name       VARCHAR(100) NOT NULL,
    email           VARCHAR(100) UNIQUE NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ================================================
-- Books Table (title-level info)
-- ================================================
CREATE TABLE books (
    book_id         SERIAL PRIMARY KEY,
    isbn            VARCHAR(20) UNIQUE NOT NULL,
    title           VARCHAR(200) NOT NULL,
    author          VARCHAR(100) NOT NULL,
    category        VARCHAR(50),
    total_copies    INTEGER DEFAULT 1,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ================================================
-- Book Copies Table (each physical copy)
-- This is the key table for concurrency control
-- ================================================
CREATE TABLE book_copies (
    copy_id         SERIAL PRIMARY KEY,
    book_id         INTEGER REFERENCES books(book_id),
    copy_number     VARCHAR(10) NOT NULL,   -- e.g. "COPY-001"
    status          VARCHAR(20) DEFAULT 'available'
                    CHECK (status IN ('available', 'borrowed', 'reserved')),
    version         INTEGER DEFAULT 1,      -- for optimistic locking
    last_updated    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ================================================
-- Borrowing Records Table
-- ================================================
CREATE TABLE borrowing_records (
    record_id       SERIAL PRIMARY KEY,
    copy_id         INTEGER REFERENCES book_copies(copy_id),
    student_id      INTEGER REFERENCES students(student_id),
    borrowed_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date        TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '14 days'),
    returned_at     TIMESTAMP,
    renewed_count   INTEGER DEFAULT 0,
    status          VARCHAR(20) DEFAULT 'active'
                    CHECK (status IN ('active', 'returned', 'overdue'))
);

-- ================================================
-- Indexes for Performance
-- ================================================
CREATE INDEX idx_book_copies_status ON book_copies(status);
CREATE INDEX idx_book_copies_book_id ON book_copies(book_id);
CREATE INDEX idx_borrowing_student ON borrowing_records(student_id);
CREATE INDEX idx_borrowing_copy ON borrowing_records(copy_id);
CREATE INDEX idx_borrowing_status ON borrowing_records(status);
CREATE INDEX idx_books_title ON books(title);