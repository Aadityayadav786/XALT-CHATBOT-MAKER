# app.py

import os
import time
import uuid
import shutil
import streamlit as st
from dotenv import load_dotenv

from utils.session_utils import init_user_session, get_user_and_session
from tools.scrap_and_filter import crawl_website
from vector_database import build_or_update_vector_db
from rag_pipeline import get_rag_response
from agents.deployment_agent import DeploymentAgent
from utils.load_env import load_env_file

from PyPDF2 import PdfReader
import docx

# --- Setup ---
load_dotenv()
env_vars = load_env_file()
RENDER_API_KEY = env_vars.get("RENDER_API_KEY")
COHERE_API_KEY = env_vars.get("COHERE_API_KEY")

init_user_session()
user_id, session_id = get_user_and_session()

st.set_page_config(page_title="Auto AI Chatbot Builder", page_icon="🤖")
st.title("🤖 Auto Chatbot Builder from Website or Files")

# Directories
TXT_DIR = "txt"
VECTORSTORE_DIR = "vectorstore"
os.makedirs(TXT_DIR, exist_ok=True)
os.makedirs(VECTORSTORE_DIR, exist_ok=True)

web_txt_path = os.path.join(TXT_DIR, "webscraper.txt")
file_txt_path = os.path.join(TXT_DIR, "filedata.txt")
merged_txt_path = os.path.join(TXT_DIR, "merged.txt")

# Session state
if "qa_chain_ready" not in st.session_state:
    st.session_state.qa_chain_ready = False
if "webscraped" not in st.session_state:
    st.session_state.webscraped = False
if "files_uploaded" not in st.session_state:
    st.session_state.files_uploaded = False
if "redirected_after_deploy" in st.session_state:
    del st.session_state["redirected_after_deploy"]
    st.experimental_rerun()

# --- Inputs ---
url = st.text_input("🔗 Enter Website URL")

if st.button("🌐 Start Web Scraping"):
    if not url:
        st.warning("Please enter a website URL to scrape.")
        st.stop()
    with st.spinner("Scraping website..."):
        scraped_txt_path = crawl_website(url)
        if os.path.abspath(scraped_txt_path) != os.path.abspath(web_txt_path):
             shutil.copy(scraped_txt_path, web_txt_path)
        st.session_state.webscraped = True
        st.success(f"✅ Web scraping completed and saved to `{web_txt_path}`")

       

# Allow file upload ONLY after web scraping
if st.session_state.webscraped:
    st.markdown("---")
    st.subheader("📁 Upload Supporting Files (After Web Scraping)")

    uploaded_files = st.file_uploader(
        "Upload multiple files (PDF, TXT, DOCX)", 
        type=["pdf", "txt", "docx"], 
        accept_multiple_files=True
    )

    def extract_text(uploaded_file):
        try:
            if uploaded_file.name.endswith(".pdf"):
                reader = PdfReader(uploaded_file)
                return "\n".join([p.extract_text() or "" for p in reader.pages])
            elif uploaded_file.name.endswith(".txt"):
                return uploaded_file.read().decode("utf-8")
            elif uploaded_file.name.endswith(".docx"):
                doc = docx.Document(uploaded_file)
                return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            st.error(f"Error reading {uploaded_file.name}: {e}")
            return ""

    if uploaded_files and st.button("📤 Extract & Save Uploaded Text"):
        combined_text = ""
        for file in uploaded_files:
            text = extract_text(file)
            combined_text += f"\n\n--- Extracted from: {file.name} ---\n\n{text}"
        with open(file_txt_path, "w", encoding="utf-8") as f:
            f.write(combined_text)
        st.session_state.files_uploaded = True
        st.success(f"✅ Extracted file text saved to `{file_txt_path}`")

# Merge only after both are available
if st.session_state.webscraped and st.session_state.files_uploaded:
    st.markdown("---")
    st.subheader("📚 Merge Web + File Data")

    if st.button("🧩 Merge Text Files"):
        try:
            with open(web_txt_path, "r", encoding="utf-8") as w, open(file_txt_path, "r", encoding="utf-8") as f:
                merged_text = f"\n--- Webscraped Content ---\n{w.read()}\n\n--- Uploaded File Content ---\n{f.read()}"
            with open(merged_txt_path, "w", encoding="utf-8") as m:
                m.write(merged_text)
            st.success(f"✅ Files merged and saved as `{merged_txt_path}`")
        except Exception as e:
            st.error(f"❌ Merge error: {e}")

# Vector DB and chatbot
if os.path.exists(merged_txt_path) and st.button("🚀 Build Vector DB"):
    with st.spinner("Creating vector database..."):
        if build_or_update_vector_db(merged_txt_path):
            st.session_state.qa_chain_ready = True
            st.success("✅ Vector DB ready!")
        else:
            st.error("❌ Vector DB creation failed.")

# Chat Interface
if st.session_state.qa_chain_ready:
    st.markdown("---")
    st.subheader("💬 Chat with Your Bot")
    user_query = st.text_input("Ask a question:")
    if user_query:
        with st.spinner("🤖 Thinking..."):
            try:
                answer, docs = get_rag_response(user_query, session_id, user_id)
                st.markdown(f"**🤖 Answer:**  {answer}")
                with st.expander("📄 Source Docs"):
                    for i, doc in enumerate(docs, 1):
                        st.markdown(f"**Doc {i}:**")
                        st.code(doc.page_content[:500], language="text")
            except Exception as e:
                st.error(f"Error: {e}")

    st.subheader("🚀 Deploy Chatbot")
    if st.button("💻 Deploy to Render"):
        with st.spinner("Pushing to GitHub..."):
            try:
                github_url = DeploymentAgent().deploy_now()
                st.success(f"✅ GitHub Ready: [🔗 {github_url}]({github_url})")
                st.success("Your repo has been created successfully.")


            # CLEANUP user data folders after repo creation
                try:
                    shutil.rmtree("vectorstore", ignore_errors=True)
                    os.makedirs("vectorstore", exist_ok=True)
                    shutil.rmtree("txt", ignore_errors=True)
                    os.makedirs("txt", exist_ok=True)
                    st.info("🧹 Your data (vectorstore and text files) have been cleared after repo creation.")
                except Exception as e:
                    st.error(f"⚠️ Error during cleanup: {e}")

                st.success("You can now proceed with the final deployment steps.")
            except Exception as e:
                st.error(f"GitHub Error: {e}")
                st.stop()



    
       

        # with st.spinner("Deploying to Render..."):
        #     try:
        #         render_url = deploy_to_render(github_url, RENDER_API_KEY)
        #         st.success(f"🌐 Live: [🔗 {render_url}]({render_url})")
        #         st.session_state["redirected_after_deploy"] = True
        #         time.sleep(3)
        #         st.experimental_rerun()
        #     except Exception as e:
        #         st.error(f"Render Error: {e}")

