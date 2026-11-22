
from utils.document_loader import load_document

try:
    documents = load_document("sample.txt")

    print("Document loaded successfully!")

    for doc in documents:
        print("Content:", doc.page_content)

except Exception as e:
    print("Document loading failed:", str(e))
