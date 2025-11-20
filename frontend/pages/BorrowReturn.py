import sys
from pathlib import Path

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from backend import services

st.set_page_config(page_title="Borrow & Return", page_icon="🔄")


def require_admin() -> None:
    if not st.session_state.get("supabase_user"):
        st.error("Please log in via the Login page to access the admin dashboard.")
        st.stop()


require_admin()

st.title("🔄 Borrow & Return")
st.caption("Bold actions for circulation control.")

left, right = st.columns(2)

with left:
    st.subheader("Borrow Book")
    student_id = st.number_input("Student ID", min_value=1, step=1)
    book_id = st.number_input("Book ID", min_value=1, step=1)
    if st.button("Issue Book"):
        result = services.borrow_book(int(student_id), int(book_id))
        if result.get("success"):
            st.success(result.get("message"))
        else:
            st.error(result.get("error", "Unable to borrow book."))

with right:
    st.subheader("Return Book")
    record_id = st.number_input("Borrow Record ID", min_value=1, step=1)
    if st.button("Return Book"):
        result = services.return_book(int(record_id))
        if result.get("success"):
            st.success(result.get("message"))
        else:
            st.error(result.get("error", "Unable to return book."))

st.divider()

st.subheader("Active Loans")
active_loans = services.list_borrow_records(status="borrowed")
st.dataframe(active_loans, use_container_width=True, height=400)

