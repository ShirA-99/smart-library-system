# ================================================
# app.py
# Smart Library Self-Service System
# Streamlit UI
# ================================================

import streamlit as st
import sys
sys.path.append(".")

from src.borrow      import search_books, get_all_books, borrow_book, get_student_borrows, get_student
from src.return_book import return_book, get_borrow_history
from src.renew       import renew_book

# ================================================
# Page Configuration
# ================================================
st.set_page_config(
    page_title = "University Library",
    page_icon  = "📚",
    layout     = "wide"
)

# ================================================
# Custom CSS
# ================================================
st.markdown("""
    <style>
        .main-header {
            background-color : #1a3c5e;
            padding          : 20px;
            border-radius    : 10px;
            margin-bottom    : 20px;
        }
        .main-header h1 {
            color       : white;
            text-align  : center;
            margin      : 0;
        }
        .main-header p {
            color       : #a0c4e8;
            text-align  : center;
            margin      : 5px 0 0 0;
        }
        .kiosk-badge {
            background-color : #e8f4f8;
            border           : 1px solid #1a3c5e;
            border-radius    : 5px;
            padding          : 5px 10px;
            font-size        : 12px;
            color            : #1a3c5e;
        }
        .available {
            color       : green;
            font-weight : bold;
        }
        .unavailable {
            color       : red;
            font-weight : bold;
        }
        .overdue {
            color       : red;
            font-weight : bold;
        }
        .due-soon {
            color       : orange;
            font-weight : bold;
        }
        .on-time {
            color       : green;
            font-weight : bold;
        }
    </style>
""", unsafe_allow_html=True)

# ================================================
# Session State Initialization
# Tracks login state across reruns
# ================================================
if "logged_in"  not in st.session_state:
    st.session_state.logged_in  = False
if "student"    not in st.session_state:
    st.session_state.student    = None
if "page"       not in st.session_state:
    st.session_state.page       = "browse"

# ================================================
# Header
# ================================================
st.markdown("""
    <div class="main-header">
        <h1>📚 University Library Self-Service Kiosk</h1>
        <p>Borrow · Return · Renew</p>
    </div>
""", unsafe_allow_html=True)

# ================================================
# LOGIN SECTION
# ================================================
if not st.session_state.logged_in:
    st.subheader("🔐 Student Login")
    st.write("Enter your student number to access the kiosk.")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        student_number = st.text_input(
            "Student Number",
            placeholder = "e.g. STU001",
            max_chars   = 20
        )

        if st.button("Login", use_container_width=True, type="primary"):
            if student_number.strip() == "":
                st.error("Please enter your student number.")
            else:
                student = get_student(student_number.strip().upper())
                if student:
                    st.session_state.logged_in = True
                    st.session_state.student   = dict(student)
                    st.success(f"Welcome, {student['full_name']}!")
                    st.rerun()
                else:
                    st.error("Student not found. Please check your student number.")

    st.divider()
    st.caption("💡 Test accounts: STU001 to STU010")

# ================================================
# MAIN APP (after login)
# ================================================
else:
    student = st.session_state.student

    # ----------------------------------------
    # Top bar: student info + logout
    # ----------------------------------------
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"""
            👤 **{student['full_name']}** &nbsp;|&nbsp;
            🎓 {student['student_number']} &nbsp;|&nbsp;
            ✉️ {student['email']}
        """)
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.student   = None
            st.session_state.page      = "browse"
            st.rerun()

    st.divider()

    # ----------------------------------------
    # Navigation Tabs
    # ----------------------------------------
    tab1, tab2, tab3, tab4 = st.tabs([
        "📖 Browse & Borrow",
        "↩️ Return",
        "🔄 Renew",
        "📋 History"
    ])

    # ============================================
    # TAB 1: BROWSE & BORROW
    # ============================================
    with tab1:
        st.subheader("📖 Browse Books")

        # Search bar
        search_query = st.text_input(
            "Search by title, author, or category",
            placeholder = "e.g. Python, Clean Code, Database..."
        )

        if search_query:
            books = search_books(search_query)
        else:
            books = get_all_books()

        if not books:
            st.warning("No books found.")
        else:
            st.write(f"Showing **{len(books)}** book(s)")
            st.divider()

            for book in books:
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])

                    with col1:
                        st.markdown(f"**📗 {book['title']}**")
                        st.caption(f"✍️ {book['author']}  |  🏷️ {book['category']}  |  ISBN: {book['isbn']}")

                    with col2:
                        available = int(book['available_copies'])
                        total     = int(book['total_copies'])

                        if available > 0:
                            st.markdown(f"<span class='available'>✅ {available}/{total} Available</span>",
                                        unsafe_allow_html=True)
                        else:
                            st.markdown(f"<span class='unavailable'>❌ 0/{total} Available</span>",
                                        unsafe_allow_html=True)

                    with col3:
                        if available > 0:
                            if st.button(
                                "Borrow",
                                key             = f"borrow_{book['book_id']}",
                                use_container_width = True,
                                type            = "primary"
                            ):
                                result = borrow_book(book['book_id'], student['student_id'])
                                if result["success"]:
                                    st.success(result["message"])
                                    st.info(f"📋 Copy: {result['copy_number']}  |  📅 Due: {result['due_date'].strftime('%d %b %Y')}")
                                    st.rerun()
                                else:
                                    st.error(result["message"])
                        else:
                            st.button(
                                "Unavailable",
                                key      = f"borrow_{book['book_id']}",
                                disabled = True,
                                use_container_width = True
                            )

                    st.divider()

    # ============================================
    # TAB 2: RETURN
    # ============================================
    with tab2:
        st.subheader("↩️ Return a Book")

        borrows = get_student_borrows(student['student_id'])

        if not borrows:
            st.info("You have no active borrows to return.")
        else:
            st.write(f"You have **{len(borrows)}** active borrow(s).")
            st.divider()

            for borrow in borrows:
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])

                    with col1:
                        st.markdown(f"**📗 {borrow['title']}**")
                        st.caption(f"✍️ {borrow['author']}  |  📋 {borrow['copy_number']}")
                        st.caption(f"📅 Borrowed: {borrow['borrowed_at'].strftime('%d %b %Y')}")

                    with col2:
                        due_status = borrow['due_status']
                        due_date   = borrow['due_date'].strftime('%d %b %Y')

                        if due_status == "Overdue":
                            st.markdown(f"<span class='overdue'>⚠️ OVERDUE<br>{due_date}</span>",
                                        unsafe_allow_html=True)
                        elif due_status == "Due Soon":
                            st.markdown(f"<span class='due-soon'>⏰ Due Soon<br>{due_date}</span>",
                                        unsafe_allow_html=True)
                        else:
                            st.markdown(f"<span class='on-time'>✅ On Time<br>{due_date}</span>",
                                        unsafe_allow_html=True)

                    with col3:
                        if st.button(
                            "Return",
                            key             = f"return_{borrow['record_id']}",
                            use_container_width = True,
                            type            = "primary"
                        ):
                            result = return_book(borrow['record_id'], student['student_id'])
                            if result["success"]:
                                st.success(result["message"])
                                st.rerun()
                            else:
                                st.error(result["message"])

                    st.divider()

    # ============================================
    # TAB 3: RENEW
    # ============================================
    with tab3:
        st.subheader("🔄 Renew a Book")

        borrows = get_student_borrows(student['student_id'])

        if not borrows:
            st.info("You have no active borrows to renew.")
        else:
            st.write(f"You have **{len(borrows)}** active borrow(s).")
            st.divider()

            for borrow in borrows:
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])

                    with col1:
                        st.markdown(f"**📗 {borrow['title']}**")
                        st.caption(f"✍️ {borrow['author']}  |  📋 {borrow['copy_number']}")
                        renewals_left = 2 - int(borrow['renewed_count'])
                        st.caption(f"🔄 Renewals left: {renewals_left}/2")

                    with col2:
                        due_date = borrow['due_date'].strftime('%d %b %Y')
                        st.markdown(f"📅 Due:<br>**{due_date}**",
                                    unsafe_allow_html=True)

                    with col3:
                        if renewals_left > 0:
                            if st.button(
                                "Renew +14 days",
                                key             = f"renew_{borrow['record_id']}",
                                use_container_width = True,
                                type            = "primary"
                            ):
                                result = renew_book(borrow['record_id'], student['student_id'])
                                if result["success"]:
                                    st.success(result["message"])
                                    st.info(f"📅 New due date: {result['new_due_date'].strftime('%d %b %Y')}  |  🔄 Renewals left: {result['renewals_left']}")
                                    st.rerun()
                                else:
                                    st.error(result["message"])
                        else:
                            st.button(
                                "Max Renewals",
                                key      = f"renew_{borrow['record_id']}",
                                disabled = True,
                                use_container_width = True
                            )

                    st.divider()

    # ============================================
    # TAB 4: HISTORY
    # ============================================
    with tab4:
        st.subheader("📋 Borrowing History")

        history = get_borrow_history(student['student_id'])

        if not history:
            st.info("No borrowing history found.")
        else:
            st.write(f"Total records: **{len(history)}**")
            st.divider()

            for record in history:
                with st.container():
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown(f"**📗 {record['title']}**")
                        st.caption(f"✍️ {record['author']}  |  📋 {record['copy_number']}")
                        st.caption(f"📅 Borrowed: {record['borrowed_at'].strftime('%d %b %Y')}  |  🔄 Renewed: {record['renewed_count']}x")

                    with col2:
                        if record['status'] == 'active':
                            st.markdown("🟢 **Active**")
                        elif record['status'] == 'returned':
                            returned = record['returned_at'].strftime('%d %b %Y') if record['returned_at'] else 'N/A'
                            st.markdown(f"✅ **Returned**")
                            st.caption(f"on {returned}")
                        else:
                            st.markdown("🔴 **Overdue**")

                    st.divider()