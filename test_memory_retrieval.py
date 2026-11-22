
from utils.document_loader import load_document
from utils.text_splitter import split_documents
from utils.vector_store import get_vector_store

try:
    # Load the document
    documents = load_document("sample.txt")

    # Split into chunks
    chunks = split_documents(documents)

    # Connect to ChromaDB
    vector_store = get_vector_store()

    # Store document chunks
    vector_store.add_documents(chunks)

    print("Document stored successfully!")

    # Search for relevant memories
    results = vector_store.similarity_search(
        "What is my project?",
        k=2
    )

    print("\nRetrieved memories:")

    for result in results:
        print(result.page_content)

except Exception as e:
    print("Memory retrieval failed:", str(e))
