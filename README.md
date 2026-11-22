# RecallBridge AI 🧠

### Your Personal AI Memory Assistant

RecallBridge AI is an AI-powered personal memory assistant that helps users store, organize, search, and retrieve personal memories and uploaded documents using Retrieval-Augmented Generation (RAG).

## 🚀 Project Overview

RecallBridge AI allows users to save personal information and upload documents. It uses vector embeddings and semantic search to retrieve relevant information and generates answers using an AI language model.

The goal is to make stored information easy to access through natural language conversations.

## ✨ Key Features

- **Add Memories:** Save personal memories with categories.
- **Document Upload:** Upload and process documents such as PDFs.
- **Memory Dashboard:** View memory and document statistics.
- **View Memories:** Browse stored memories and document chunks.
- **Semantic Search:** Search stored information using natural language.
- **AI Chat:** Ask questions about saved memories and uploaded documents.
- **RAG Pipeline:** Retrieve relevant information before generating answers.
- **Duplicate Detection:** Prevent saving identical memories.
- **Category Management:** Update memory categories.
- **Delete Memories:** Remove unwanted stored memories.
- **Chat History:** Access previous conversations.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Streamlit | User interface |
| LangChain | LLM and RAG integration |
| Groq | Large Language Model |
| FastEmbed | Text embeddings |
| ChromaDB | Vector database |
| Retrieval-Augmented Generation | Context-based question answering |

## 🏗️ System Architecture

1. User adds personal memories or uploads documents.
2. Documents are processed and split into chunks.
3. FastEmbed generates vector embeddings.
4. ChromaDB stores the vectors and associated information.
5. User asks a question through the chat interface.
6. Relevant information is retrieved using semantic search.
7. Retrieved context is passed to the Groq language model.
8. The AI generates an answer based on the retrieved information.

## 📂 Project Structure

```text
AI_UseCase/
│
├── app.py
├── models/
│   └── embeddings.py
│
├── utils/
│   ├── vector_store.py
│   └── rag_pipeline.py
│
├── chroma_db/
├── requirements.txt
└── README.md
```

*Note: Update this structure if your project contains additional folders or files.*

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### 2. Navigate to the Project Folder

```bash
cd AI_UseCase
```

### 3. Create a Virtual Environment

```bash
python -m venv .venv
```

### 4. Activate the Environment

For Linux:

```bash
source .venv/bin/activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure API Key

Configure your Groq API key using the environment variable expected by your project. Never upload API keys or secrets to GitHub.

### 7. Run the Application

```bash
streamlit run app.py
```

## 💡 Example Use Case

A user uploads a PDF containing project information and asks:

**"What is this document about?"**

RecallBridge AI retrieves relevant document chunks and generates an answer using the retrieved context.

If the stored information does not contain an answer, the AI responds cautiously instead of inventing information.

## 🔮 Future Enhancements

- Voice-based memory interaction
- Improved memory organization
- Advanced conversation retrieval
- More document format support

## 👩‍💻 Project

**Project Name:** RecallBridge AI

**Domain:** Artificial Intelligence / Generative AI / RAG

**Purpose:** Personal AI-powered memory management and information retrieval.

---

*RecallBridge AI — Remember better. Retrieve smarter.*