import shutil
import uuid
import streamlit as st
import time
import os
import subprocess
import requests

from utils.session_utils import init_user_session, get_user_and_session
from tools.scrap_and_filter import crawl_website
from vector_database import build_or_update_vector_db
from rag_pipeline import get_rag_response
from agents.deployment_agent import DeploymentAgent
from utils.load_env import load_env_file
from render_deploy import deploy_to_render  # ✅ NEW: Render deployment logic

# --- Load Environment Variables ---
env_vars = load_env_file()
RENDER_API_KEY = env_vars.get("RENDER_API_KEY")

# --- Session Initialization ---
init_user_session()
user_id, session_id = get_user_and_session()

# --- Streamlit Page Config ---
st.set_page_config(page_title="Auto AI Chatbot Builder", page_icon="🤖")
st.title("🤖 Auto Chatbot Builder from Website")

# --- Session State Initialization ---
if "qa_chain_ready" not in st.session_state:
    st.session_state.qa_chain_ready = False

# --- Step 1: Input URL ---
url = st.text_input("🔗 Enter Website URL")

# --- Step 2: Scrape & Embed ---
if st.button("🚀 Start Process") and url:
    with st.status("⏳ Running pipeline...", expanded=True) as status:
        try:
            st.write(f"🔍 Scraping website: `{url}`")
            txt_path = crawl_website(url)
            st.success("✅ Web scraping completed!")

            st.write("📄 Saving text data...")
            time.sleep(0.5)
            st.success("✅ Data saved successfully!")

            st.write("📦 Generating vector embeddings...")
            build_or_update_vector_db(txt_path)
            st.success("✅ Vector database created!")

            st.session_state.qa_chain_ready = True
            status.update(label="🎉 Pipeline completed!", state="complete", expanded=True)

        except Exception as e:
            status.update(label=f"❌ Pipeline failed: {e}", state="error")

# --- Step 3: Chat Interface ---
if st.session_state.qa_chain_ready:
    st.markdown("---")
    st.subheader("💬 Chat with Us")

    user_query = st.text_input("Ask a question about the site:")
    if user_query:
        try:
            with st.spinner("🧠 Generating answer..."):
                session_id = st.session_state.get("session_id", str(uuid.uuid4()))
                user_id = st.session_state.get("user_id", str(uuid.uuid4()))
                st.session_state["session_id"] = session_id
                st.session_state["user_id"] = user_id

                answer, docs = get_rag_response(user_query, session_id, user_id)

            st.markdown(f"**🤖 Answer:**  {answer}")
            with st.expander("🔍 Sources"):
                for i, doc in enumerate(docs, start=1):
                    st.markdown(f"**Doc {i}:**")
                    st.code(doc.page_content[:500], language="text")

        except FileNotFoundError as err:
            st.error(str(err))

    st.markdown("---")
    st.subheader("Satisfied with the chatbot?")
    if st.button("🚀 Deploy it"):
        with st.status("📤 Pushing code to GitHub...", expanded=True) as status:
            try:
                deployment_agent = DeploymentAgent()
                github_repo_url = deployment_agent.deploy_now()
                st.write("✅ Code pushed to GitHub.")
                status.update(label="✅ Code pushed to GitHub!", state="complete")
                st.success(f"📦 GitHub Repo: [🔗 {github_repo_url}]({github_repo_url})")
            except Exception as e:
                status.update(label="❌ GitHub push failed", state="error")
                st.error(f"GitHub Error: {e}")
                st.stop()

        # --- Step 4: Deploy to Render ---
        with st.status("🚀 Deploying to Render...", expanded=True) as deploy_status:
            try:
                render_url = deploy_to_render(github_repo_url, RENDER_API_KEY)
                deploy_status.update(label="✅ Deployed to Render!", state="complete")
                st.success(f"🌐 Live Chatbot URL: [🔗 {render_url}]({render_url})")
            except Exception as e:
                deploy_status.update(label="❌ Render deployment failed", state="error")
                st.error(f"Render Error: {e}")

# --- If Vectorstore Not Available ---
elif not os.path.exists(os.path.join("vectorstore", "index.faiss")):
    st.warning("⚠️ Vectorstore not found — please run the pipeline above first.")
