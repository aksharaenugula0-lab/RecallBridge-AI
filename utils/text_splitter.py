
from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_documents(documents):
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )

        chunks = text_splitter.split_documents(documents)
        return chunks

    except Exception as e:
        raise RuntimeError(
            f"Text splitting failed: {str(e)}"
        )
