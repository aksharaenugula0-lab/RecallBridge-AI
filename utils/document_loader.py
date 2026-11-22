
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader
)

import os

def load_document(file_path):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError("File not found!")

        if file_path.lower().endswith(".pdf"):
            loader = PyPDFLoader(file_path)

        elif file_path.lower().endswith(".txt"):
            loader = TextLoader(file_path, encoding="utf-8")

        else:
            raise ValueError("Only PDF and TXT files are supported.")

        documents = loader.load()
        return documents

    except Exception as e:
        raise RuntimeError(f"Document loading failed: {str(e)}")
