# Smart Library System

A Flask and PostgreSQL library self-service system for borrowing, returning, renewing, and viewing borrowing history. The project also includes a live concurrency demo that shows how row-level locking prevents duplicate borrows when multiple kiosks compete for the same book copy.

## Features

- Student login using seeded test accounts
- Browse and search the catalog
- Borrow available book copies
- Return active borrows
- Renew active borrows
- View borrowing history
- Run a live concurrency demo in the browser
- Run a threaded load test from the command line

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Flask 3.1 |
| Database | PostgreSQL |
| Templates | Jinja2 |
| Python | Python 3.8+ |
| DB Driver | `psycopg2-binary` |
| Environment Config | `python-dotenv` |
| UI | Server-rendered HTML + shared CSS |

## Project Structure

```text
smart-library-system/
|-- app.py
|-- requirements.txt
|-- README.md
|-- database/
|   |-- schema.sql
|   |-- seed_data.sql
|-- src/
|   |-- db.py
|   |-- borrow.py
|   |-- return_book.py
|   |-- renew.py
|-- static/
|   |-- editorial.css
|   |-- illustrations/
|   |   |-- library-reading-room-bg.png
|   |-- vendor/
|       |-- streamline/
|-- templates/
|   |-- base.html
|   |-- navbar.html
|   |-- dashboard.html
|   |-- returns.html
|   |-- renew.html
|   |-- history.html
|   |-- login_editorial.html
|   |-- demo_editorial.html
|   |-- _icons.html
|-- tests/
|   |-- load_test.py
```

## Prerequisites

- Python 3.8 or newer
- PostgreSQL
- Git

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/ShirA-99/smart-library-system.git
cd smart-library-system
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

Windows:

```powershell
venv\Scripts\activate
```

macOS / Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the database

Create a PostgreSQL database named `library_db`:

```bash
psql -U postgres -c "CREATE DATABASE library_db;"
```

Load the schema:

```bash
psql -U postgres -d library_db -f database/schema.sql
```

Load the seed data:

```bash
psql -U postgres -d library_db -f database/seed_data.sql
```

### 5. Configure environment variables

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=library_db
DB_USER=postgres
DB_PASSWORD=your_password_here
FLASK_SECRET_KEY=change-this-in-production
```

### 6. Run the application

```bash
python app.py
```

Open:

```text
http://localhost:5000
```

## Test Accounts

The seeded login accounts use student numbers:

```text
STU001 through STU010
```

## Application Pages

- `/login` - student login page
- `/dashboard` - browse and search books
- `/returns` - return active borrows
- `/renew` - renew active borrows
- `/history` - view borrowing history
- `/demo` - run the live concurrency demonstration

## Concurrency Demo

The demo page simulates multiple kiosk users trying to borrow the same book at the same time.

What it shows:

- Current available copies for the target book
- Parallel borrow requests from multiple seeded students
- Which requests succeed and which lose the race
- That successful borrows do not exceed the number of available copies

Relevant demo endpoints:

- `POST /api/demo/reset`
- `GET /api/demo/availability/<book_id>`
- `POST /api/demo/borrow`

## Load Test

Run the threaded load test with:

```bash
python tests/load_test.py
```

This script simulates concurrent borrowing attempts and helps validate that the locking logic behaves correctly under contention.

## Concurrency Control

The project uses PostgreSQL row-level locking during borrowing operations.

Primary approach:

- `SELECT ... FOR UPDATE` locks a specific book-copy row during a borrow transaction
- competing transactions must wait or fail safely instead of double-issuing the same copy

Secondary safeguard:

- the schema includes a `version` column for optimistic checks

## Notes

- This project is intended for academic and demonstration use.
- The current UI is server-rendered and styled through the shared `static/editorial.css` stylesheet.
- The login and demo pages use the editorial template variants currently wired in `app.py`.

## License

Academic use project.
