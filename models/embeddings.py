from langchain_community.embeddings import FastEmbedEmbeddings

def get_embedding_model():
    try:
        embedding_model = FastEmbedEmbeddings(
            model_name="BAAI/bge-small-en-v1.5"
        )
        return embedding_model

    except Exception as e:
        raise RuntimeError(
            f"Failed to initialize embedding model: {str(e)}"
        )