# rag_pipeline.py

import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_cohere import CohereEmbeddings, ChatCohere
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

if not COHERE_API_KEY:
    raise ValueError("❌ Missing COHERE_API_KEY in environment. Please check your .env file.")

# Vector DB configuration
FAISS_DB_PATH = "vectorstore"
INDEX_FILE = os.path.join(FAISS_DB_PATH, "index.faiss")

# Embedding and LLM setup
EMBEDDING_MODEL = CohereEmbeddings(
    model="embed-english-v3.0",
    cohere_api_key=COHERE_API_KEY
)
llm = ChatCohere(
    model="command-r-plus",
    temperature=0.3,
    cohere_api_key=COHERE_API_KEY
)

# Prompt template
PROMPT = """
You are a helpful assistant in a multi-turn conversation. Use ONLY the chat history and the provided documents to answer the user's new question.

Chat History:  
{chat_history}

Relevant Documents:
{context}

New Question:
{question}

IMPORTANT:
- If the answer cannot be found in the provided documents, say: "I'm sorry, I don't have enough information to answer that."
- Do NOT use any external knowledge or make assumptions.
- Stay strictly within the information from the documents.

Answer:
"""
prompt = ChatPromptTemplate.from_template(PROMPT)
chain = prompt | llm


def load_faiss_db():
    """Load FAISS index from disk (raise if missing)."""
    if not os.path.exists(INDEX_FILE):
        raise FileNotFoundError(
            f"❌ FAISS index not found at {INDEX_FILE}. "
            "Run `vector_database.py` to generate the vectorstore."
        )
    return FAISS.load_local(
        FAISS_DB_PATH,
        EMBEDDING_MODEL,
        allow_dangerous_deserialization=True
    )


def get_rag_response(query: str, session_id: str, user_id: str):
    """
    Generate RAG-based response to a query with session-based context.

    Args:
        query (str): User question
        session_id (str): Unique session ID
        user_id (str): Unique user ID

    Returns:
        tuple: (response: str, documents: List[Document])
    """
    # Step 1: Load FAISS vector DB
    faiss_db = load_faiss_db()

    # Step 2: Retrieve top-matching documents
    docs = faiss_db.similarity_search(query, k=5)
    context = "\n\n".join(doc.page_content for doc in docs)

    # Step 3: Fetch previous conversation from MongoDB
    from utils.mongo_utils import store_chat, fetch_chat_history  # delayed import
    chat_history = fetch_chat_history(user_id=user_id, session_id=session_id, limit=5)

    # Step 4: Query LLM with context + history
    inputs = {
        "question": query,
        "context": context,
        "chat_history": chat_history
    }
    response = chain.invoke(inputs)

    # Step 5: Store this interaction to MongoDB
    store_chat(user_id, session_id, query, response.content)

    return response.content, docs
