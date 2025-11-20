import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from backend import services

st.set_page_config(page_title="Library Dashboard", page_icon="📚", layout="wide")


def require_admin() -> None:
    if not st.session_state.get("supabase_user"):
        st.error("Please log in via the Login page to access the admin dashboard.")
        st.stop()


require_admin()

st.markdown(
    """
    <style>
    .metric-card {
        background-color: #f7f7f7;
        padding: 1.2rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }
    .metric-label {
        font-weight: bold;
        color: #444;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #2c3e50;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📚 Library Management – Admin Dashboard")
st.caption("Bold overview of books, students, and circulation activity.")

books = services.get_books()
students = services.get_students()
borrowed_records = services.list_borrow_records()

books_df = pd.DataFrame(books)
students_df = pd.DataFrame(students)
borrow_df = pd.DataFrame(borrowed_records)

active_loans = borrow_df[borrow_df["status"] == "borrowed"] if not borrow_df.empty else pd.DataFrame()

total_books = int(books_df["total_copies"].sum()) if not books_df.empty else 0
available_books = int(books_df["available_copies"].sum()) if not books_df.empty else 0

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Titles</div>
            <div class="metric-value">{len(books)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Total Copies</div>
            <div class="metric-value">{total_books}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Available Copies</div>
            <div class="metric-value">{available_books}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Active Loans</div>
            <div class="metric-value">{len(active_loans)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

col_a, col_b = st.columns(2)
with col_a:
    st.subheader("Inventory Snapshot")
    if books_df.empty:
        st.info("No book data yet.")
    else:
        top_titles = books_df.sort_values("available_copies", ascending=False)[["title", "author", "available_copies", "total_copies"]].head(10)
        st.dataframe(top_titles, use_container_width=True, height=320)
with col_b:
    st.subheader("Borrow Status Split")
    if borrow_df.empty:
        st.info("No borrow records yet.")
    else:
        status_counts = borrow_df["status"].value_counts()
        st.bar_chart(status_counts)

st.subheader("Top Borrowed Books")
if borrow_df.empty:
    st.info("No borrow data yet.")
else:
    book_lookup = {book["id"]: book["title"] for book in books}
    top_books = (
        borrow_df["book_id"]
        .map(book_lookup)
        .value_counts()
        .head(5)
        .rename_axis("Title")
        .reset_index(name="Borrows")
    )
    st.table(top_books)

st.subheader("Recent Borrow Activity")
if borrow_df.empty:
    st.info("No transactions yet.")
else:
    recent_activity = borrow_df.sort_values("borrow_date", ascending=False).head(15)
    st.dataframe(recent_activity, use_container_width=True, height=360)

