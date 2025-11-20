import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

load_dotenv()

import backend.auth as auth  # noqa: E402

st.set_page_config(page_title="Admin Login", page_icon="🔐")

st.title("🔐 Admin Login")
st.caption("Authenticate with your Supabase credentials to access admin tools.")


def _serialize_user(user):
    if user is None:
        return None
    return {
        "id": getattr(user, "id", None),
        "email": getattr(user, "email", None),
        "role": getattr(user, "role", None),
        "app_metadata": getattr(user, "app_metadata", {}) or {},
        "user_metadata": getattr(user, "user_metadata", {}) or {},
    }


def _serialize_session(session):
    if session is None:
        return None
    return {
        "access_token": getattr(session, "access_token", None),
        "refresh_token": getattr(session, "refresh_token", None),
        "expires_at": getattr(session, "expires_at", None),
        "token_type": getattr(session, "token_type", None),
    }


current_user = st.session_state.get("supabase_user")
if current_user:
    st.success(f"Signed in as {current_user.get('email')}")
    if st.button("Sign Out"):
        access_token = st.session_state.get("supabase_session", {}).get("access_token")
        try:
            auth.sign_out(access_token)
        except Exception as exc:  # pylint: disable=broad-except
            st.warning(f"Sign-out issue: {exc}")
        st.session_state.pop("supabase_user", None)
        st.session_state.pop("supabase_session", None)
        st.rerun()
    st.stop()

login_tab, signup_tab = st.tabs(["Sign In", "Register"])

with login_tab:
    with st.form("supabase-login-form"):
        email = st.text_input("Email", placeholder="admin@library.com")
        password = st.text_input("Password", type="password")
        login_submit = st.form_submit_button("Sign In")

        if login_submit:
            if not email or not password:
                st.error("Email and password are required.")
            else:
                try:
                    auth_response = auth.sign_in(email.strip(), password)
                    user = _serialize_user(auth_response.get("user"))
                    session = _serialize_session(auth_response.get("session"))
                    if not user or not session:
                        raise ValueError("Missing user session data.")
                    st.session_state["supabase_user"] = user
                    st.session_state["supabase_session"] = session
                    st.success("Welcome back! Use the sidebar to open admin pages.")
                    st.rerun()
                except Exception as exc:  # pylint: disable=broad-except
                    st.error(f"Login failed: {exc}")

with signup_tab:
    with st.form("supabase-signup-form"):
        full_name = st.text_input("Full Name")
        signup_email = st.text_input("Email", placeholder="admin@library.com")
        signup_password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        signup_submit = st.form_submit_button("Create Account")

        if signup_submit:
            if not signup_email or not signup_password:
                st.error("Email and password are required.")
            elif signup_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                try:
                    metadata = {"full_name": full_name} if full_name else {}
                    auth.sign_up(signup_email.strip(), signup_password, **metadata)
                    st.success(
                        "Account created. Check your inbox for a verification email, "
                        "then sign in above."
                    )
                except Exception as exc:  # pylint: disable=broad-except
                    st.error(f"Registration failed: {exc}")

st.info(
    "Supabase Auth powers this login. Configure allowed admin emails or roles via "
    "Supabase dashboard for tighter control."
)

