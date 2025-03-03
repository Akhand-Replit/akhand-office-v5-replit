import streamlit as st
from models.models import Company, User, UserRole
from utils.auth import get_password_hash
from sqlalchemy.exc import IntegrityError

def render_admin_dashboard(db):
    st.title("Admin Dashboard")

    tab1, tab2, tab3 = st.tabs(["Create Company", "Manage Companies", "Profile"])

    with tab1:
        st.header("Create New Company")
        with st.form("create_company"):
            company_name = st.text_input("Company Name")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            profile_pic = st.text_input("Profile Picture URL")

            if st.form_submit_button("Create Company"):
                # Check if username already exists
                existing_user = db.query(User).filter(User.username == username).first()
                if existing_user:
                    st.error("Username already exists. Please choose a different username.")
                    return

                try:
                    # Create company
                    company = Company(name=company_name)
                    db.add(company)
                    db.flush()

                    # Create company admin user
                    user = User(
                        username=username,
                        password=get_password_hash(password),
                        name=company_name,
                        role=UserRole.COMPANY,
                        profile_pic=profile_pic,
                        company_id=company.id
                    )
                    db.add(user)
                    db.commit()
                    st.success("Company created successfully!")
                except IntegrityError:
                    db.rollback()
                    st.error("An error occurred. Please check your inputs and try again.")
                except Exception as e:
                    db.rollback()
                    st.error(f"An unexpected error occurred: {str(e)}")

    with tab2:
        st.header("Company List")
        companies = db.query(Company).all()
        for company in companies:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader(company.name)
                st.write(f"Status: {'Active' if company.is_active else 'Inactive'}")
            with col2:
                if company.is_active:
                    if st.button("Deactivate", key=f"deact_{company.id}"):
                        company.is_active = False
                        # Deactivate all related branches and employees
                        company_users = db.query(User).filter(User.company_id == company.id).all()
                        for user in company_users:
                            user.is_active = False
                        db.commit()
                        st.rerun()
                else:
                    if st.button("Activate", key=f"act_{company.id}"):
                        company.is_active = True
                        # Activate all related branches and employees
                        company_users = db.query(User).filter(User.company_id == company.id).all()
                        for user in company_users:
                            user.is_active = True
                        db.commit()
                        st.rerun()

    with tab3:
        st.header("Admin Profile")
        admin = st.session_state.user
        with st.form("update_profile"):
            new_name = st.text_input("Name", value=admin.name)
            new_pic = st.text_input("Profile Picture URL", value=admin.profile_pic)

            if st.form_submit_button("Update Profile"):
                admin.name = new_name
                admin.profile_pic = new_pic
                db.commit()
                st.success("Profile updated successfully!")