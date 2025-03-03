import streamlit as st
from models.models import Report, Task
from datetime import datetime
from utils.pdf import generate_report_pdf

def render_employee_dashboard(db):
    st.title("Employee Dashboard")
    
    tabs = st.tabs(["Daily Report", "Tasks", "History", "Profile"])
    
    with tabs[0]:
        st.header("Submit Daily Report")
        with st.form("daily_report"):
            report_date = st.date_input("Date", value=datetime.now())
            report_content = st.text_area("What did you do today?")
            
            if st.form_submit_button("Submit Report"):
                report = Report(
                    user_id=st.session_state.user.id,
                    date=report_date,
                    content=report_content
                )
                db.add(report)
                db.commit()
                st.success("Report submitted successfully!")
    
    with tabs[1]:
        st.header("Tasks")
        tasks = db.query(Task).filter(
            Task.assigned_to == st.session_state.user.id
        ).all()
        
        for task in tasks:
            with st.expander(f"Task: {task.title}"):
                st.write(task.description)
                st.write(f"Status: {task.status}")
                if task.status != "completed":
                    if st.button("Mark as Complete", key=f"complete_task_{task.id}"):
                        task.status = "completed"
                        task.completed_at = datetime.now()
                        db.commit()
                        st.success("Task marked as complete!")
                        st.rerun()
    
    with tabs[2]:
        st.header("History")
        date_range = st.date_input(
            "Select Date Range",
            value=(datetime.now(), datetime.now())
        )
        
        if st.button("Generate Report"):
            reports = db.query(Report).filter(
                Report.user_id == st.session_state.user.id,
                Report.date.between(date_range[0], date_range[1])
            ).all()
            
            report_data = [
                {
                    "Date": r.date.strftime("%Y-%m-%d"),
                    "Content": r.content
                }
                for r in reports
            ]
            
            pdf = generate_report_pdf(report_data, "Activity Report")
            st.download_button(
                "Download Report",
                pdf,
                "activity_report.pdf",
                "application/pdf"
            )
    
    with tabs[3]:
        st.header("Profile")
        user = st.session_state.user
        with st.form("update_profile"):
            new_name = st.text_input("Name", value=user.name)
            new_pic = st.text_input("Profile Picture URL", value=user.profile_pic)
            
            if st.form_submit_button("Update Profile"):
                user.name = new_name
                user.profile_pic = new_pic
                db.commit()
                st.success("Profile updated successfully!")
