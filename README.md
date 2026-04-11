# 📚 Smart Library Self-Service System

A concurrency-safe university library self-service system built with
Python, PostgreSQL, and Streamlit. Designed to handle multiple kiosk
users simultaneously during peak hours (e.g., exam periods).

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | Python 3.8+ |
| Database | PostgreSQL |
| Concurrency Control | PostgreSQL Row-Level Locking (`SELECT FOR UPDATE`) |
| Version Control | Git + GitHub |

---

## ⚙️ Prerequisites

Make sure you have the following installed:

- [Python 3.8+](https://www.python.org/downloads/)
- [PostgreSQL](https://www.postgresql.org/download/)
- [Git](https://git-scm.com/)
- [VS Code](https://code.visualstudio.com/) *(recommended)*

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/ShirA-99/smart-library-system.git
cd smart-library-system
```

> ⚠️ Replace `YOUR_USERNAME` with the actual GitHub username.

---

### 2. Create and Activate Virtual Environment

```bash
# Create virtual environment
python -m venv venv
```

```bash
# Activate — Windows:
venv\Scripts\activate

# Activate — Mac/Linux:
source venv/bin/activate
```

You should see `(venv)` appear at the start of your terminal line.

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Add psql to PATH (Windows Only)

If `psql` is not recognized, run this in your terminal.
Replace `16` with your installed PostgreSQL version number:

```powershell
$env:Path += ";C:\Program Files\PostgreSQL\16\bin"
```

Verify it works:
```powershell
psql --version
```

> 💡 To make this permanent, add `C:\Program Files\PostgreSQL\16\bin`
> to your System Environment Variables under **Path**.

---

### 5. Set Up the Database

Make sure PostgreSQL is running, then run these commands one by one:

```bash
# Create the database
psql -U postgres -c "CREATE DATABASE library_db;"

# Create the tables
psql -U postgres -d library_db -f database/schema.sql

# Load sample data
psql -U postgres -d library_db -f database/seed_data.sql
```

It will ask for your PostgreSQL password each time.

Verify the data loaded correctly:
```bash
psql -U postgres -d library_db -c "\dt"
```

You should see 4 tables: `students`, `books`, `book_copies`, `borrowing_records`.

---

### 6. Configure Environment Variables

Create a `.env` file in the **root folder** of the project:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=library_db
DB_USER=postgres
DB_PASSWORD=your_password_here
```

> ⚠️ Replace `your_password_here` with your actual PostgreSQL password.
> The `.env` file is already in `.gitignore` — it will NOT be uploaded to GitHub.

---

### 7. Run the Application

```bash
streamlit run app.py
```

Then open your browser and go to:
```
http://localhost:8501
```

---

## 🖥️ Simulating Multiple Kiosks

Each browser tab acts as a **separate kiosk**.

To demonstrate concurrency:
1. Open `http://localhost:8501` in **two or more browser tabs**
2. Log in as different students in each tab
3. Try borrowing the **same book** from both tabs at the same time
4. Only **one tab will succeed** — the other will be blocked

This demonstrates the **race condition prevention** built into the system.

---

## 🧪 Running the Load Test

To simulate many kiosks operating at the same time:

```bash
python tests/load_test.py
```

This script will:
- Spawn multiple threads (each thread = one kiosk)
- Attempt to borrow the same books concurrently
- Print response times for each transaction
- Report any conflicts or errors detected

---

## 📁 Project Structure

```
smart-library-system/
│
├── README.md                  # This file
├── requirements.txt           # Python dependencies
├── .env                       # DB credentials (not on GitHub)
├── .gitignore                 # Files excluded from GitHub
│
├── database/
│   ├── schema.sql             # Table definitions and indexes
│   └── seed_data.sql          # Sample books and students
│
├── src/
│   ├── db.py                  # Database connection manager
│   ├── borrow.py              # Borrow logic with locking
│   ├── return_book.py         # Return logic
│   └── renew.py               # Renew logic
│
├── app.py                     # Streamlit UI (main entry point)
│
└── tests/
    └── load_test.py           # Concurrent kiosk load test
```

---

## 🔐 How Concurrency Control Works

This system prevents race conditions using two strategies:

**1. Pessimistic Locking (`SELECT FOR UPDATE`)**
- When a student borrows a book, the system locks that book copy's
  database row immediately
- Any other kiosk trying to borrow the same copy is forced to wait
- Once the transaction completes, the lock is released
- Guarantees no two students can borrow the same copy simultaneously

**2. Optimistic Locking (version numbers)**
- Each book copy has a `version` column
- Before updating, the system checks if the version has changed
- If another kiosk already updated it, the transaction is rejected
- Used as a secondary safety net

---

## 🗄️ Database Tables

| Table | Description |
|---|---|
| `students` | Student accounts and details |
| `books` | Book titles and metadata |
| `book_copies` | Individual physical copies (locked during borrow) |
| `borrowing_records` | Active and historical borrow transactions |

---

## 👥 Authors

| Name | Student ID |
|---|---|
| Your Name Here | YOUR_STUDENT_ID |
| Your Name Here | YOUR_STUDENT_ID |

---

## 📄 License

This project is developed for academic purposes only.