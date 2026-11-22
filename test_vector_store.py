
from utils.vector_store import get_vector_store

try:
    vector_store = get_vector_store()

    vector_store.add_texts(
        texts=[
            "RecallBridge AI stores and retrieves personal memories.",
            "I am learning Python and Generative AI."
        ],
        ids=["memory1", "memory2"]
    )

    results = vector_store.similarity_search(
        "What am I learning?",
        k=1
    )

    print("Vector database working successfully!")

    for result in results:
        print("Retrieved memory:", result.page_content)

except Exception as e:
    print("Vector database test failed:", str(e))