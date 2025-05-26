# rag_pipeline.py

import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_cohere import CohereEmbeddings, ChatCohere
from langchain_core.prompts import ChatPromptTemplate

# Load environment
load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# Paths & models
FAISS_DB_PATH = "vectorstore"
EMBEDDING_MODEL = CohereEmbeddings(model="embed-english-v3.0")

# LLM + Prompt chain
llm = ChatCohere(model="command-r-plus", temperature=0.3)
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
    index_file = os.path.join(FAISS_DB_PATH, "index.faiss")
    if not os.path.exists(index_file):
        raise FileNotFoundError(
            f"❌ FAISS index not found at {index_file}. "
            "Please run the embedding pipeline first."
        )
    return FAISS.load_local(
        FAISS_DB_PATH,
        EMBEDDING_MODEL,
        allow_dangerous_deserialization=True
    )


def get_rag_response(query: str, session_id: str, user_id: str):
    """
    Process a query using RAG and session-based memory from MongoDB.

    Args:
        query (str): User's query
        session_id (str): Unique session identifier
        user_id (str): Unique user identifier

    Returns:
        tuple: (Generated response string, list of retrieved documents)
    """
    # (1) Load FAISS index
    faiss_db = load_faiss_db()

    # (2) Get top relevant documents from the DB
    docs = faiss_db.similarity_search(query)
    context = "\n\n".join(d.page_content for d in docs)

    # (3) Fetch recent chat history from MongoDB
    from utils.mongo_utils import store_chat, fetch_chat_history  # Import here to avoid circular imports
    chat_history = fetch_chat_history(user_id=user_id, session_id=session_id, limit=5)

    # (4) Call LLM with context + history + new question
    response = chain.invoke({
        "question": query,
        "context": context,
        "chat_history": chat_history
    })

    # (5) Store current interaction
    store_chat(user_id, session_id, query, response.content)

    return response.content, docs
