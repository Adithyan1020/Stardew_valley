import os
from pathlib import Path
from dotenv import load_dotenv

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

def main():
    print("Loading Embeddings and Vector Store...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    
    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR)
    )
    
    # Retrieve top 20 chunks to ensure we don't miss tables or infoboxes
    retriever = vector_store.as_retriever(search_kwargs={"k": 20})
    
    print("Initializing Groq LLM...")
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

    # Create the prompt
    system_prompt = (
        "You are an expert Stardew Valley assistant. Use the following pieces of retrieved context to answer the user's question. "
        "If the answer is not contained in the context, say that you don't know based on the provided information. "
        "Keep your answer concise and accurate to the game. When asked about loved gifts, list them clearly."
        "\n\n"
        "Context:\n"
        "{context}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    print("\n--- Stardew Valley Chat (Powered by LangChain & Groq) ---")
    print("Type 'exit' to quit.\n")

    while True:
        query = input("Ask something: ").strip()
        if not query:
            continue
        if query.lower() == "exit":
            break
            
        print("\nThinking...")
        
        # 1. Retrieve documents
        docs = retriever.invoke(query)
        context = "\n\n".join(doc.page_content for doc in docs)
        
        # 2. Format prompt
        messages = prompt.format_messages(context=context, input=query)
        
        # 3. Generate response
        response = llm.invoke(messages)
        
        print("\n" + "="*50)
        print(f"Answer: {response.content}")
        print("="*50 + "\n")

if __name__ == "__main__":
    main()
