from models.embeddings import get_embedding_model

try:
    embeddings = get_embedding_model()

    print("Embedding model initialized successfully!")

    vector = embeddings.embed_query(
        "RecallBridge AI stores personal memories."
    )

    print("Embedding dimensions:", len(vector))
    print("First 5 values:", vector[:5])

except Exception as e:
    print("Embedding test failed:", str(e))