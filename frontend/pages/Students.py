import sys
from pathlib import Path

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from backend import services

st.set_page_config(page_title="Manage Students", page_icon="👥")


def require_admin() -> None:
    if not st.session_state.get("supabase_user"):
        st.error("Please log in via the Login page to access the admin dashboard.")
        st.stop()


require_admin()

st.title("👥 Manage Students")
st.caption("Bold administrative tools for student enrollment and tracking.")

with st.form("add-student-form"):
    st.subheader("Register Student")
    name = st.text_input("Full Name").strip()
    email = st.text_input("Email").strip()

    submitted = st.form_submit_button("Add Student")
    if submitted:
        if not name or not email:
            st.error("Both name and email are required.")
        else:
            try:
                services.add_student(name, email)
                st.success("Student added successfully.")
            except Exception as exc:  # pylint: disable=broad-except
                st.error(f"Failed to add student: {exc}")

st.divider()

st.subheader("Student Directory")
students = services.get_students()
st.dataframe(students, use_container_width=True, height=500)

