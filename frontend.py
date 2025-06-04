import streamlit as st
from rag_pipeline import get_rag_response
from utils.mongo_utils import store_chat, clear_chat
from utils.session_utils import init_user_session, get_user_and_session

# ------------------------ Streamlit Page Config ------------------------ #
st.set_page_config(page_title="Chatbot", page_icon="🤖")
st.title("🤖 AI Assistant")

# ------------------------ Session Setup ------------------------ #
# Automatically set user_id and session_id
init_user_session()
user_id, session_id = get_user_and_session()

# Display session and user IDs
st.markdown(f"🔑 **Session ID:** `{session_id}`")
st.markdown(f"🧑 **User ID:** `{user_id}`")

# ------------------------ Initialize Chat History ------------------------ #
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# ------------------------ Chat Interface ------------------------ #
user_input = st.chat_input("💬 Ask me anything...")

if user_input:
    try:
        with st.spinner("🧠 Thinking..."):
            # Get response from the model
            answer, sources = get_rag_response(user_input, session_id=session_id, user_id=user_id)

        # Append the conversation to session state
        st.session_state.conversation.append({"role": "user", "message": user_input})
        st.session_state.conversation.append({"role": "assistant", "message": answer})

        # Store the chat interaction in the database
        store_chat(user_id, session_id, user_input, answer)

    except Exception as e:
        st.error(f"❌ Error occurred: {str(e)}")

# ------------------------ Display Conversation ------------------------ #
for chat in st.session_state.conversation:
    if chat["role"] == "user":
        st.markdown(f"**You:** {chat['message']}")
    else:
        st.markdown(f"**Assistant:** {chat['message']}")

# ------------------------ Clear Chat Option ------------------------ #
if st.button("🗑️ Clear Chat"):
    clear_chat(user_id, session_id)
    st.session_state.conversation = []  # Clear conversation from session state
    st.success("✅ Chat history cleared.")
    st.rerun()  # Refresh the app

# ------------------------ Footer ------------------------ #
st.markdown("---")
st.markdown('<p style="text-align:center; font-size: 14px;">Powered by <strong>Xalt</strong></p>', unsafe_allow_html=True)
