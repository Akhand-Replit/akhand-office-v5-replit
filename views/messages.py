import streamlit as st
from models.models import Message, User
from datetime import datetime

def render_messages(db):
    st.header("Messages")
    
    # Get user's role and ID
    current_user = st.session_state.user
    
    # Get messages
    received_messages = db.query(Message).filter(
        Message.receiver_id == current_user.id,
        Message.is_deleted == False
    ).all()
    
    sent_messages = db.query(Message).filter(
        Message.sender_id == current_user.id,
        Message.is_deleted == False
    ).all()
    
    tab1, tab2 = st.tabs(["Inbox", "Send Message"])
    
    with tab1:
        st.subheader("Received Messages")
        for msg in received_messages:
            sender = db.query(User).filter(User.id == msg.sender_id).first()
            with st.expander(f"From: {sender.name} - {msg.created_at.strftime('%Y-%m-%d %H:%M')}"):
                st.write(msg.content)
                if msg.attachment_url:
                    st.markdown(f"[Attachment]({msg.attachment_url})")
                if st.button("Reply", key=f"reply_{msg.id}"):
                    st.session_state.reply_to = msg.sender_id
    
    with tab2:
        st.subheader("Send New Message")
        
        # Get potential recipients based on user's role
        if current_user.role == "admin":
            recipients = db.query(User).filter(User.role == "company").all()
        elif current_user.role == "company":
            recipients = db.query(User).filter(
                User.company_id == current_user.company_id
            ).all()
        else:
            recipients = db.query(User).filter(
                User.branch_id == current_user.branch_id
            ).all()
        
        with st.form("send_message"):
            recipient = st.selectbox(
                "To",
                options=recipients,
                format_func=lambda x: x.name
            )
            content = st.text_area("Message")
            attachment = st.text_input("Attachment URL (optional)")
            
            if st.form_submit_button("Send"):
                message = Message(
                    sender_id=current_user.id,
                    receiver_id=recipient.id,
                    content=content,
                    attachment_url=attachment if attachment else None
                )
                db.add(message)
                db.commit()
                st.success("Message sent successfully!")
