import uuid
import streamlit as st

def init_user_session():
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

def get_user_and_session():
    return st.session_state.get("user_id"), st.session_state.get("session_id")
