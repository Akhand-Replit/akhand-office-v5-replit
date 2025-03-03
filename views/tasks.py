import streamlit as st
from models.models import Task, User, Branch
from datetime import datetime

def render_tasks(db):
    st.header("Task Management")
    
    current_user = st.session_state.user
    
    tab1, tab2 = st.tabs(["Assign Tasks", "Track Tasks"])
    
    with tab1:
        st.subheader("Assign New Task")
        
        # Get potential assignees based on user's role
        if current_user.role == "company":
            branches = db.query(Branch).filter(
                Branch.company_id == current_user.company_id
            ).all()
            employees = db.query(User).filter(
                User.company_id == current_user.company_id
            ).all()
        elif current_user.role == "manager":
            employees = db.query(User).filter(
                User.branch_id == current_user.branch_id,
                User.role != "manager"
            ).all()
        else:  # asst_manager
            employees = db.query(User).filter(
                User.branch_id == current_user.branch_id,
                User.role == "employee"
            ).all()
        
        with st.form("assign_task"):
            title = st.text_input("Task Title")
            description = st.text_area("Task Description")
            
            if current_user.role == "company":
                assign_type = st.radio("Assign to:", ["Branch", "Individual"])
                if assign_type == "Branch":
                    assignee = st.selectbox(
                        "Select Branch",
                        options=branches,
                        format_func=lambda x: x.name
                    )
                else:
                    assignee = st.selectbox(
                        "Select Employee",
                        options=employees,
                        format_func=lambda x: x.name
                    )
            else:
                assignee = st.selectbox(
                    "Assign to",
                    options=employees,
                    format_func=lambda x: x.name
                )
            
            if st.form_submit_button("Assign Task"):
                if current_user.role == "company" and assign_type == "Branch":
                    # Assign to all employees in branch
                    branch_employees = db.query(User).filter(
                        User.branch_id == assignee.id
                    ).all()
                    for emp in branch_employees:
                        task = Task(
                            title=title,
                            description=description,
                            assigned_by=current_user.id,
                            assigned_to=emp.id,
                            branch_id=assignee.id,
                            status="pending"
                        )
                        db.add(task)
                else:
                    task = Task(
                        title=title,
                        description=description,
                        assigned_by=current_user.id,
                        assigned_to=assignee.id,
                        status="pending"
                    )
                    db.add(task)
                db.commit()
                st.success("Task assigned successfully!")
    
    with tab2:
        st.subheader("Task Status")
        
        # Get tasks based on user's role
        if current_user.role == "company":
            tasks = db.query(Task).filter(
                Task.assigned_by == current_user.id
            ).all()
        else:
            tasks = db.query(Task).filter(
                Task.assigned_to == current_user.id
            ).all()
        
        for task in tasks:
            with st.expander(f"Task: {task.title}"):
                st.write(f"Description: {task.description}")
                st.write(f"Status: {task.status}")
                st.write(f"Created: {task.created_at.strftime('%Y-%m-%d %H:%M')}")
                if task.completed_at:
                    st.write(f"Completed: {task.completed_at.strftime('%Y-%m-%d %H:%M')}")
                
                if task.status != "completed" and current_user.id == task.assigned_to:
                    if st.button("Mark Complete", key=f"complete_{task.id}"):
                        task.status = "completed"
                        task.completed_at = datetime.now()
                        db.commit()
                        st.success("Task marked as complete!")
                        st.rerun()
