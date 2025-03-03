import streamlit as st
from models.models import Branch, User, UserRole
from utils.auth import get_password_hash
from utils.pdf import generate_report_pdf

def render_company_dashboard(db):
    st.title("Company Dashboard")
    
    tabs = st.tabs(["Branches", "Employees", "Reports", "Profile"])
    
    with tabs[0]:
        st.header("Manage Branches")
        
        # Create new branch
        with st.form("create_branch"):
            branch_name = st.text_input("Branch Name")
            if st.form_submit_button("Create Branch"):
                branch = Branch(
                    name=branch_name,
                    company_id=st.session_state.user.company_id
                )
                db.add(branch)
                db.commit()
                st.success("Branch created successfully!")
        
        # List branches
        branches = db.query(Branch).filter(
            Branch.company_id == st.session_state.user.company_id
        ).all()
        
        for branch in branches:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader(branch.name)
                st.write(f"Status: {'Active' if branch.is_active else 'Inactive'}")
            with col2:
                if branch.is_active:
                    if st.button("Deactivate", key=f"deact_branch_{branch.id}"):
                        branch.is_active = False
                        db.commit()
                        st.rerun()
                else:
                    if st.button("Activate", key=f"act_branch_{branch.id}"):
                        branch.is_active = True
                        db.commit()
                        st.rerun()
    
    with tabs[1]:
        st.header("Manage Employees")
        
        # Create new employee
        with st.form("create_employee"):
            emp_name = st.text_input("Employee Name")
            emp_username = st.text_input("Username")
            emp_password = st.text_input("Password", type="password")
            emp_role = st.selectbox(
                "Role",
                ["manager", "asst_manager", "employee"]
            )
            emp_branch = st.selectbox(
                "Branch",
                [b.name for b in branches]
            )
            emp_pic = st.text_input("Profile Picture URL")
            
            if st.form_submit_button("Create Employee"):
                branch_id = next(b.id for b in branches if b.name == emp_branch)
                employee = User(
                    username=emp_username,
                    password=get_password_hash(emp_password),
                    name=emp_name,
                    role=UserRole[emp_role.upper()],
                    profile_pic=emp_pic,
                    company_id=st.session_state.user.company_id,
                    branch_id=branch_id
                )
                db.add(employee)
                db.commit()
                st.success("Employee created successfully!")
    
    with tabs[2]:
        st.header("Reports")
        report_type = st.selectbox(
            "Report Type",
            ["Branch Reports", "Employee Reports"]
        )
        date_range = st.date_input(
            "Date Range",
            value=(st.session_state.today, st.session_state.today)
        )
        
        if st.button("Generate Report"):
            # Generate report logic here
            report_data = []  # This would be filled with actual data
            pdf = generate_report_pdf(report_data, f"{report_type} - {date_range}")
            st.download_button(
                "Download Report",
                pdf,
                "report.pdf",
                "application/pdf"
            )
    
    with tabs[3]:
        st.header("Company Profile")
        company = st.session_state.user
        with st.form("update_company_profile"):
            new_name = st.text_input("Company Name", value=company.name)
            new_pic = st.text_input("Profile Picture URL", value=company.profile_pic)
            
            if st.form_submit_button("Update Profile"):
                company.name = new_name
                company.profile_pic = new_pic
                db.commit()
                st.success("Profile updated successfully!")
