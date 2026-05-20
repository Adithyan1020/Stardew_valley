# 🐔 Stardew Valley AI Assistant (RAG Pipeline)

A full-stack AI Assistant for Stardew Valley that uses **Retrieval-Augmented Generation (RAG)** to provide highly accurate, hallucination-free answers about the game. It scrapes the Stardew Valley Wiki, embeds the data into a vector database, and uses LangChain + Groq to answer user queries through a modern web interface.

## 🌟 Features
* **Accurate Knowledge Base**: Answers are sourced directly from the Stardew Valley Wiki using RAG, preventing the AI from making up facts.
* **Modern Web Interface**: A beautiful, glassmorphism-styled frontend designed for Stardew Valley fans.
* **FastAPI Backend**: A lightweight and robust Python backend to handle embedding retrieval and LLM prompting.
* **Blazing Fast LLM**: Powered by Groq (`llama-3.1-8b-instant`) for instant responses.

## 🏗️ Architecture
1. **Data Pipeline**: Scrapes the wiki (using BeautifulSoup), cleans the text, chunks it, and embeds it using HuggingFace `BAAI/bge-small-en-v1.5`.
2. **Vector Database**: Stores the embeddings locally using **ChromaDB**.
3. **Backend API**: A **FastAPI** server that receives user questions, retrieves the top 20 relevant chunks from ChromaDB, and formats them into a LangChain prompt for Groq.
4. **Frontend**: A pure HTML/CSS/Vanilla JS web app that can be hosted statically on Netlify.

## 🚀 Local Setup Instructions

### 1. Prerequisites
* Python 3.10+
* A free [Groq API Key](https://console.groq.com/keys)

### 2. Installation
Clone the repository and create a virtual environment:
```bash
git clone https://github.com/yourusername/stardew-valley-ai.git
cd stardew-valley-ai
python -m venv newenv
newenv\Scripts\activate  # On Mac/Linux use: source newenv/bin/activate
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory and add your Groq API key:
```env
GROQ_API_KEY=your_api_key_here
```

### 4. Running the Application
The vector database is already pre-built in the `data/chroma` folder. To start the chat interface:

**Start the Backend Server:**
```bash
uvicorn process.api:app --reload
```
*The server will start at `http://127.0.0.1:8000`*

**Start the Frontend:**
Open the `frontend/index.html` file in any web browser!

## 🌐 Deployment Guide
Because the AI dependencies (PyTorch, ChromaDB) are quite large, the frontend and backend must be deployed separately.

**Backend (Render.com)**
1. Create a new Web Service on Render and connect this repository.
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `uvicorn process.api:app --host 0.0.0.0 --port 10000`
4. Add your `GROQ_API_KEY` in the Environment Variables section.

**Frontend (Netlify.com)**
1. Open `frontend/app.js` and change `API_URL` to your new Render URL (e.g., `https://your-app.onrender.com/chat`).
2. Drag and drop the `frontend/` folder into Netlify for free static hosting.

## 🛠️ Modifying the Knowledge Base
If you want to add new pages or update the wiki data:
1. Add the new page slugs to `ingest/seed.json`.
2. Run `python ingest/download_pages.py`.
3. Run `python process/clean_pages.py` and `python process/chunk_pages.py`.
4. Run `python process/build_index.py` to update the ChromaDB vector store.
