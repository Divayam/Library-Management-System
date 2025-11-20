import sys
from pathlib import Path

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from backend import services

st.set_page_config(page_title="Manage Books", page_icon="📘")


def require_admin() -> None:
    if not st.session_state.get("supabase_user"):
        st.error("Please log in via the Login page to access the admin dashboard.")
        st.stop()


require_admin()

st.title("📘 Manage Books")
st.caption("Bold controls for adding and reviewing library inventory.")

with st.form("add-book-form"):
    st.subheader("Add New Book")
    title = st.text_input("Title").strip()
    author = st.text_input("Author").strip()
    isbn = st.text_input("ISBN (optional)").strip() or None
    total_copies = st.number_input("Total Copies", min_value=1, value=1, step=1)

    submitted = st.form_submit_button("Add Book")
    if submitted:
        if not title or not author:
            st.error("Title and Author are required.")
        else:
            try:
                services.add_book(title, author, isbn, int(total_copies))
                st.success("Book added successfully.")
            except Exception as exc:  # pylint: disable=broad-except
                st.error(f"Failed to add book: {exc}")

st.divider()

st.subheader("Inventory Overview")
books = services.get_books()
st.dataframe(books, use_container_width=True, height=500)

