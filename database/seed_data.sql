-- ================================================
-- Smart Library Self-Service System
-- Seed Data
-- ================================================

-- ================================================
-- Students
-- ================================================
INSERT INTO students (student_number, full_name, email) VALUES
('STU001', 'Ahmad Razif',       'ahmad.razif@university.edu.my'),
('STU002', 'Nurul Ain',         'nurul.ain@university.edu.my'),
('STU003', 'Wei Jian Lim',      'weijian.lim@university.edu.my'),
('STU004', 'Priya Nair',        'priya.nair@university.edu.my'),
('STU005', 'Haziq Syafiq',      'haziq.syafiq@university.edu.my'),
('STU006', 'Siti Mariam',       'siti.mariam@university.edu.my'),
('STU007', 'Chong Wei Kiat',    'chongwei.kiat@university.edu.my'),
('STU008', 'Kavitha Rajan',     'kavitha.rajan@university.edu.my'),
('STU009', 'Amirul Hakim',      'amirul.hakim@university.edu.my'),
('STU010', 'Mei Ling Tan',      'meiling.tan@university.edu.my');

-- ================================================
-- Books
-- ================================================
INSERT INTO books (isbn, title, author, category, total_copies) VALUES
('978-0132350884', 'Clean Code',                          'Robert C. Martin',     'Programming',  3),
('978-0201633610', 'Design Patterns',                     'Gang of Four',         'Programming',  2),
('978-0137903955', 'The Pragmatic Programmer',            'Andrew Hunt',          'Programming',  2),
('978-1491950357', 'Python Data Science Handbook',        'Jake VanderPlas',      'Data Science', 3),
('978-0134685991', 'Effective Java',                      'Joshua Bloch',         'Programming',  2),
('978-0321125217', 'Domain-Driven Design',                'Eric Evans',           'Programming',  1),
('978-1492056355', 'Hands-On Machine Learning',           'Aurélien Géron',       'Data Science', 2),
('978-0136042594', 'Computer Networks',                   'Andrew Tanenbaum',     'Networking',   2),
('978-0073523323', 'Database System Concepts',            'Silberschatz',         'Database',     3),
('978-0201895513', 'The Mythical Man-Month',              'Frederick Brooks',     'Management',   1);

-- ================================================
-- Book Copies (based on total_copies per book)
-- ================================================

-- Clean Code (3 copies)
INSERT INTO book_copies (book_id, copy_number, status) VALUES
(1, 'COPY-001', 'available'),
(1, 'COPY-002', 'available'),
(1, 'COPY-003', 'borrowed');

-- Design Patterns (2 copies)
INSERT INTO book_copies (book_id, copy_number, status) VALUES
(2, 'COPY-001', 'available'),
(2, 'COPY-002', 'borrowed');

-- The Pragmatic Programmer (2 copies)
INSERT INTO book_copies (book_id, copy_number, status) VALUES
(3, 'COPY-001', 'available'),
(3, 'COPY-002', 'available');

-- Python Data Science Handbook (3 copies)
INSERT INTO book_copies (book_id, copy_number, status) VALUES
(4, 'COPY-001', 'available'),
(4, 'COPY-002', 'available'),
(4, 'COPY-003', 'available');

-- Effective Java (2 copies)
INSERT INTO book_copies (book_id, copy_number, status) VALUES
(5, 'COPY-001', 'available'),
(5, 'COPY-002', 'available');

-- Domain-Driven Design (1 copy)
INSERT INTO book_copies (book_id, copy_number, status) VALUES
(6, 'COPY-001', 'available');

-- Hands-On Machine Learning (2 copies)
INSERT INTO book_copies (book_id, copy_number, status) VALUES
(7, 'COPY-001', 'available'),
(7, 'COPY-002', 'available');

-- Computer Networks (2 copies)
INSERT INTO book_copies (book_id, copy_number, status) VALUES
(8, 'COPY-001', 'available'),
(8, 'COPY-002', 'available');

-- Database System Concepts (3 copies)
INSERT INTO book_copies (book_id, copy_number, status) VALUES
(9, 'COPY-001', 'available'),
(9, 'COPY-002', 'available'),
(9, 'COPY-003', 'available');

-- The Mythical Man-Month (1 copy)
INSERT INTO book_copies (book_id, copy_number, status) VALUES
(10, 'COPY-001', 'available');

-- ================================================
-- Some existing borrowing records (realistic data)
-- ================================================
INSERT INTO borrowing_records (copy_id, student_id, borrowed_at, due_date, status) VALUES
(3,  1, CURRENT_TIMESTAMP - INTERVAL '5 days',  CURRENT_TIMESTAMP + INTERVAL '9 days',  'active'),
(5,  2, CURRENT_TIMESTAMP - INTERVAL '3 days',  CURRENT_TIMESTAMP + INTERVAL '11 days', 'active'),
(11, 3, CURRENT_TIMESTAMP - INTERVAL '10 days', CURRENT_TIMESTAMP + INTERVAL '4 days',  'active');