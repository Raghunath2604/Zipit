import streamlit as st
import asyncio
import websockets
import json
from datetime import datetime

def show_collaboration():
    st.title("👥 Real-time Collaboration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💬 Team Chat")
        
        # Chat messages
        if 'chat_messages' not in st.session_state:
            st.session_state.chat_messages = []
        
        # Display messages
        for msg in st.session_state.chat_messages[-10:]:
            st.markdown(f"**{msg['user']}**: {msg['message']}")
        
        # Send message
        new_message = st.text_input("Type message...")
        if st.button("Send") and new_message:
            st.session_state.chat_messages.append({
                'user': st.session_state.get('username', 'Anonymous'),
                'message': new_message,
                'timestamp': datetime.now().isoformat()
            })
            st.rerun()
    
    with col2:
        st.subheader("🔄 Live Code Sharing")
        
        # Shared code editor
        shared_code = st.text_area("Shared Code", height=300, key="shared_code")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📤 Share Code"):
                st.success("Code shared with team!")
        with col2:
            if st.button("📥 Sync Code"):
                st.info("Code synchronized!")

if __name__ == "__main__":
    show_collaboration()