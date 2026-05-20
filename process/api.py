import os
from pathlib import Path
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

CHROMA_DIR = PROJECT_ROOT / "data" / "chroma"
COLLECTION_NAME = "stardew_chunks_bge"
EMBED_MODEL = "BAAI/bge-small-en-v1.5"

# Initialize FastAPI App
app = FastAPI(title="Stardew Valley AI API")

# Enable CORS for the Netlify frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for easy development (change this for production!)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Variables for AI setup
vector_store = None
retriever = None
llm = None
prompt = None

@app.on_event("startup")
async def startup_event():
    global vector_store, retriever, llm, prompt
    print("Loading Embeddings and Vector Store...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    
    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR)
    )
    
    # Retrieve top 20 chunks
    retriever = vector_store.as_retriever(search_kwargs={"k": 20})
    
    print("Initializing Groq LLM...")
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

    # Create the prompt
    system_prompt = (
        "You are an expert Stardew Valley assistant. Use the following pieces of retrieved context to answer the user's question. "
        "If the answer is not contained in the context, say that you don't know based on the provided information. "
        "Keep your answer concise, friendly, and accurate to the game. When asked about loved gifts, list them clearly."
        "\n\n"
        "Context:\n"
        "{context}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    print("API is ready to accept connections!")


# Define Request and Response Models
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # 1. Retrieve documents
        docs = retriever.invoke(request.message)
        context = "\n\n".join(doc.page_content for doc in docs)
        
        # 2. Format prompt
        messages = prompt.format_messages(context=context, input=request.message)
        
        # 3. Generate response
        response = llm.invoke(messages)
        
        return ChatResponse(answer=response.content)
    except Exception as e:
        print(f"Error during chat processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))
