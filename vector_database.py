import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_cohere import CohereEmbeddings
from langchain_community.vectorstores import FAISS
import streamlit as st

# Load .env
load_dotenv()

# Constants
TXT_DIRECTORY = 'txt/'
FILE_PATH = os.path.join(TXT_DIRECTORY, '.txt')
FAISS_DB_PATH = "vectorstore"
INDEX_FILE = os.path.join(FAISS_DB_PATH, "index.faiss")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")


# Step 1: Load text file
def load_txt(file_path):
    if not os.path.exists(file_path):
        st.error("❌ Text file not found. Please check the file path.")
        return []
    loader = TextLoader(file_path, encoding='utf-8')
    return loader.load()


# Step 2: Split documents into chunks
def create_chunks(documents): 
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.split_documents(documents)


# Step 3: Get Cohere embeddings
def get_embedding_model():
    return CohereEmbeddings(model="embed-english-v3.0")  # or embed-multilingual-v3.0


# Step 4: Build or update vector DB
def build_or_update_vector_db(txt_path=None):
    try:
        st.info("📄 Loading and chunking documents...")
        documents = load_txt(txt_path or FILE_PATH)
        if not documents:
            return False  # Exit early if document loading failed

        chunks = create_chunks(documents)
        st.success("✅ Text successfully split into chunks!")

        st.info("🧠 Generating embeddings with Cohere...")
        embeddings = get_embedding_model()

        # Ensure vectorstore directory exists
        os.makedirs(FAISS_DB_PATH, exist_ok=True)

        # Check if index file exists
        if os.path.exists(INDEX_FILE):
            # Load and update existing FAISS index
            faiss_db = FAISS.load_local(
                FAISS_DB_PATH,
                embeddings,
                allow_dangerous_deserialization=True
            )
            faiss_db.add_documents(chunks)
            st.success("🔄 Vector DB updated!")
        else:
            # Create a new FAISS index from documents
            faiss_db = FAISS.from_documents(chunks, embeddings)
            st.success("🆕 Vector DB created!")

        # Save the FAISS vectorstore
        faiss_db.save_local(FAISS_DB_PATH)
        st.success(f"📦 Vector DB saved at `{FAISS_DB_PATH}`")

        return True

    except Exception as e:
        st.error(f"❌ Embedding failed: {e}")
        return False


# Run if executed directly
if __name__ == "__main__":
    build_or_update_vector_db()
