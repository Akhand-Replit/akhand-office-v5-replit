import streamlit as st
from passlib.context import CryptContext
from models.models import User, UserRole
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(db, username: str, password: str):
    # Check if this is admin login
    if username == st.secrets.ADMIN_USERNAME:
        if password == st.secrets.ADMIN_PASSWORD:
            # Get or create admin user
            admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
            if not admin:
                admin = User(
                    username=username,
                    password=get_password_hash(password),
                    name="System Admin",
                    role=UserRole.ADMIN,
                    profile_pic="https://ui-avatars.com/api/?name=System+Admin"
                )
                db.add(admin)
                db.commit()
            return admin
        return None

    # Regular user authentication (company or employee)
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password):
        return None

    # Check if user is active
    if not user.is_active:
        return None

    return user

def init_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'role' not in st.session_state:
        st.session_state.role = None

def check_admin_auth():
    return st.session_state.logged_in and st.session_state.role == UserRole.ADMIN

def check_company_auth():
    return st.session_state.logged_in and st.session_state.role == UserRole.COMPANY

def check_manager_auth():
    return st.session_state.logged_in and st.session_state.role == UserRole.MANAGER

def logout():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.role = None