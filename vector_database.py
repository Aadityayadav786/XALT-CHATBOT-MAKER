import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_cohere import CohereEmbeddings
from langchain_community.vectorstores import FAISS
import streamlit as st

# Load environment variables
load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# Constants
TXT_DIRECTORY = "txt/"
FAISS_DB_PATH = "vectorstore"
INDEX_FILE = os.path.join(FAISS_DB_PATH, "index.faiss")

def load_txt(file_path):
    """Load documents from a text file."""
    if not os.path.exists(file_path):
        st.error(f"❌ File not found at path: {file_path}")
        return []
    loader = TextLoader(file_path, encoding="utf-8")
    return loader.load()

def create_chunks(documents):
    """Split documents into smaller chunks."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.split_documents(documents)

def get_embedding_model():
    """Initialize Cohere embedding model."""
    if not COHERE_API_KEY:
        st.error("❌ COHERE_API_KEY is missing. Please check your .env file.")
        return None
    return CohereEmbeddings(model="embed-english-v3.0", cohere_api_key=COHERE_API_KEY)

def build_or_update_vector_db(txt_path=None):
    """Build or update FAISS vector DB from text documents."""
    try:
        if txt_path is None or not os.path.exists(txt_path):
            st.error("❌ Valid `txt_path` is required for vector DB generation.")
            return False

        with st.spinner("📄 Loading and splitting documents..."):
            documents = load_txt(txt_path)
            if not documents:
                st.error("❌ No documents loaded.")
                return False
            chunks = create_chunks(documents)

        with st.spinner("🧠 Generating embeddings using Cohere..."):
            embeddings = get_embedding_model()
            if embeddings is None:
                st.error("❌ Cohere embedding model not loaded.")
                return False

            os.makedirs(FAISS_DB_PATH, exist_ok=True)
            if os.path.exists(INDEX_FILE):
                faiss_db = FAISS.load_local(
                    FAISS_DB_PATH, embeddings, allow_dangerous_deserialization=True
                )
                faiss_db.add_documents(chunks)
                st.success("🔄 Vector DB updated!")
            else:
                faiss_db = FAISS.from_documents(chunks, embeddings)
                st.success("🆕 Vector DB created!")

            faiss_db.save_local(FAISS_DB_PATH)
            st.success(f"📦 Vector DB saved to `{FAISS_DB_PATH}`")

        return True

    except Exception as e:
        st.error(f"❌ Error during vector DB creation: {e}")
        return False

if __name__ == "__main__":
    example_path = os.path.join(TXT_DIRECTORY, "example.txt")
    build_or_update_vector_db(example_path)
