
from utils.document_loader import load_document
from utils.text_splitter import split_documents

try:
    documents = load_document("sample.txt")

    chunks = split_documents(documents)

    print("Text splitting successful!")
    print("Total chunks:", len(chunks))

    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i + 1}:")
        print(chunk.page_content)

except Exception as e:
    print("Text splitting failed:", str(e))
