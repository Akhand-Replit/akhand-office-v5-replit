import streamlit as st
import os
from datetime import datetime
from sqlalchemy.orm import Session
from models.database import get_db, engine
from models.models import Base, User, UserRole
from utils.auth import (
    init_session_state,
    authenticate_user,
    check_admin_auth,
    check_company_auth,
    logout
)
from views import (
    render_admin_dashboard,
    render_company_dashboard,
    render_employee_dashboard
)
import base64

# Initialize database
Base.metadata.create_all(bind=engine)

# Initialize session state
init_session_state()
st.session_state.today = datetime.now().date()

# Custom CSS
def load_css():
    with open('styles.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Page config
st.set_page_config(
    page_title="Company Management System",
    page_icon="🏢",
    layout="wide"
)

load_css()

def main():
    db = Session(engine)

    # Login page if not logged in
    if not st.session_state.logged_in:
        st.title("Welcome to Company Management System")

        login_container = st.container()
        with login_container:
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                st.subheader("Please Login")
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")

                if st.button("Login"):
                    user = authenticate_user(db, username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.session_state.role = user.role
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
        return

    # Header with user info and logout
    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        if st.session_state.user.profile_pic:
            st.image(st.session_state.user.profile_pic, width=50)
    with col2:
        st.write(f"Welcome, {st.session_state.user.name}")
    with col3:
        if st.button("Logout"):
            logout()
            st.rerun()

    st.divider()

    # Render appropriate dashboard based on role
    if check_admin_auth():
        render_admin_dashboard(db)
    elif check_company_auth():
        render_company_dashboard(db)
    else:
        render_employee_dashboard(db)

if __name__ == "__main__":
    main()