
from langchain_chroma import Chroma
from models.embeddings import get_embedding_model


def get_vector_store():
    try:
        embedding_model = get_embedding_model()

        vector_store = Chroma(
            collection_name="recallbridge_memories",
            embedding_function=embedding_model,
            persist_directory="./chroma_db"
        )

        return vector_store

    except Exception as e:
        raise RuntimeError(
            f"Failed to initialize vector store: {str(e)}"
        )


def get_all_memories():
    try:
        vector_store = get_vector_store()

        results = vector_store.get(
            include=["documents", "metadatas"]
        )

        memories = []

        for i, document in enumerate(results["documents"]):
            memories.append({
                "id": results["ids"][i],
                "content": document,
                "metadata": results["metadatas"][i]
            })

        return memories

    except Exception as e:
        raise RuntimeError(
            f"Failed to retrieve memories: {str(e)}"
        )


def delete_memory(memory_id):
    try:
        vector_store = get_vector_store()

        vector_store.delete(ids=[memory_id])

        return True

    except Exception as e:
        raise RuntimeError(
            f"Failed to delete memory: {str(e)}"
        )


def search_memories(query):
    try:
        vector_store = get_vector_store()

        results = vector_store.similarity_search(
            query,
            k=5
        )

        return results

    except Exception as e:
        raise RuntimeError(
            f"Memory search failed: {str(e)}"
        )


def update_memory_category(memory_id, new_category):
    try:
        vector_store = get_vector_store()

        result = vector_store.get(
            ids=[memory_id],
            include=["metadatas"]
        )

        if not result["ids"]:
            raise ValueError("Memory not found.")

        metadata = result["metadatas"][0] or {}
        metadata["category"] = new_category

        vector_store._collection.update(
            ids=[memory_id],
            metadatas=[metadata]
        )

        return True

    except Exception as e:
        raise RuntimeError(
            f"Category update failed: {str(e)}"
        )


# EXACT + SEMANTIC DUPLICATE DETECTION



def memory_exists(content):
    try:
        vector_store = get_vector_store()

        normalized_content = content.strip().lower()

        if not normalized_content:
            return False

        results = vector_store.get(
            where={"source": "Personal Memory"},
            include=["documents"]
        )

        existing_memories = results.get("documents") or []

        for memory in existing_memories:
            if memory and memory.strip().lower() == normalized_content:
                return True

        return False

    except Exception as e:
        raise RuntimeError(
            f"Duplicate memory check failed: {str(e)}"
        )
