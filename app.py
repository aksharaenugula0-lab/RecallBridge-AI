
import streamlit as st
import tempfile
import os
import uuid

from langchain_core.documents import Document

from utils.document_loader import load_document
from utils.text_splitter import split_documents

from utils.vector_store import (
    get_vector_store,
    get_all_memories,
    delete_memory,
    search_memories,
    update_memory_category,
    memory_exists
)

from utils.rag_pipeline import ask_question

from utils.chat_history import (
    initialize_database,
    create_conversation,
    save_message,
    get_conversations,
    get_messages,
    rename_conversation,
    delete_conversation
)


# PAGE CONFIGURATION

st.set_page_config(
    page_title="RecallBridge AI",
    page_icon="🧠",
    layout="wide"
)


MEMORY_CATEGORIES = [
    "Education",
    "Projects",
    "Personal Notes",
    "Skills",
    "Goals"
]


# SAVE DOCUMENTS TO VECTOR DATABASE

def save_documents(documents):

    chunks = split_documents(documents)

    if not chunks:
        return 0

    vector_store = get_vector_store()

    ids = [str(uuid.uuid4()) for _ in chunks]

    vector_store.add_documents(
        documents=chunks,
        ids=ids
    )

    return len(chunks)


# PROCESS UPLOADED FILE

def process_uploaded_file(uploaded_file):

    suffix = os.path.splitext(uploaded_file.name)[1].lower()

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as temp_file:

        temp_file.write(uploaded_file.getvalue())
        temp_path = temp_file.name

    try:

        documents = load_document(temp_path)

        for doc in documents:
            doc.metadata["source"] = uploaded_file.name

        return documents

    finally:

        if os.path.exists(temp_path):
            os.remove(temp_path)


# MAIN APPLICATION

def main():

    initialize_database()

    st.title("🧠 RecallBridge AI")

    st.markdown("### Your Personal AI Memory Assistant")

    st.write(
        "Upload documents, save personal notes, "
        "and ask questions about your memories."
    )

    # SIDEBAR NAVIGATION

    with st.sidebar:

        st.title("Navigation")

        page = st.radio(
            "Choose a page:",
            [
                "Home",
                "Memory Dashboard",
                "Upload Documents",
                "Add Memories",
                "View Memories",
                "Search Memories",
                "Chat"
            ]
        )

    # HOME PAGE

    if page == "Home":

        st.header("Welcome to RecallBridge AI")

        st.write(
            "RecallBridge AI helps you store and retrieve "
            "important information using "
            "Retrieval-Augmented Generation."
        )

        col1, col2 = st.columns(2)

        with col1:
            st.info("📁 Upload PDF and TXT documents")

        with col2:
            st.info("🧠 Save your personal memories")

        st.success("Your AI memory assistant is ready!")

    # MEMORY DASHBOARD

    elif page == "Memory Dashboard":

        st.header("📊 Memory Dashboard")

        try:

            memories = get_all_memories()
            conversations = get_conversations()

            total_memories = len(memories)
            total_conversations = len(conversations)

            col1, col2 = st.columns(2)

            with col1:
                st.metric("Total Memories", total_memories)

            with col2:
                st.metric(
                    "Total Conversations",
                    total_conversations
                )

            st.divider()

            st.subheader("📂 Category-wise Memories")

            category_counts = {
                category: 0
                for category in MEMORY_CATEGORIES
            }

            category_counts["Uncategorized"] = 0

            for memory in memories:

                metadata = memory.get("metadata") or {}

                category = metadata.get(
                    "category",
                    "Uncategorized"
                )

                if category not in category_counts:
                    category_counts[category] = 0

                category_counts[category] += 1

            for category, count in category_counts.items():

                st.write(f"**{category}:** {count}")

            st.divider()

            st.subheader("🕒 Recent Memories")

            if memories:

                for memory in memories[-5:][::-1]:

                    st.write(
                        f"• {memory['content'][:150]}"
                    )

            else:

                st.info("No memories saved yet.")

        except Exception as e:

            st.error(f"Dashboard error: {str(e)}")

    # UPLOAD DOCUMENTS

    elif page == "Upload Documents":

        st.header("📁 Your Documents")

        uploaded_files = st.file_uploader(
            "Choose PDF or TXT files",
            type=["pdf", "txt"],
            accept_multiple_files=True
        )

        if st.button("Process Documents"):

            if uploaded_files:

                with st.spinner("Processing documents..."):

                    total_chunks = 0

                    try:

                        for uploaded_file in uploaded_files:

                            documents = process_uploaded_file(
                                uploaded_file
                            )

                            chunks = save_documents(documents)

                            total_chunks += chunks

                        st.success(
                            f"Successfully stored {total_chunks} chunks!"
                        )

                    except Exception as e:

                        st.error(f"Error: {str(e)}")

            else:

                st.warning("Please upload a document first.")

    # ADD MEMORIES WITH DUPLICATE DETECTION

    elif page == "Add Memories":

        st.header("🧠 Add Personal Memories")

        memory_text = st.text_area(
            "Enter your memory:",
            placeholder="Write something you want RecallBridge AI to remember..."
        )

        category = st.selectbox(
            "Choose Memory Category:",
            MEMORY_CATEGORIES
        )

        if st.button("Save Memory"):

            if not memory_text.strip():

                st.warning("Please enter a memory.")

            else:

                try:

                    with st.spinner("Checking existing memories..."):

                        if memory_exists(memory_text.strip()):

                            st.warning(
                                "This memory already exists!"
                            )

                        else:

                            document = Document(
                                page_content=memory_text.strip(),
                                metadata={
                                    "source": "Personal Memory",
                                    "category": category
                                }
                            )

                            with st.spinner("Saving memory..."):

                                chunks = save_documents([document])

                            if chunks > 0:

                                st.success(
                                    f"Memory saved successfully! ({chunks} chunks)"
                                )

                            else:

                                st.warning(
                                    "No memory content was saved."
                                )

                except Exception as e:

                    st.error(
                        f"Error saving memory: {str(e)}"
                    )

    # VIEW MEMORIES

    elif page == "View Memories":

        st.header("🧠 Your Saved Memories")

        try:

            memories = get_all_memories()

            if memories:

                st.write(
                    f"Total stored chunks: {len(memories)}"
                )

                categories = [
                    "All",
                    *MEMORY_CATEGORIES,
                    "Uncategorized"
                ]

                selected_category = st.selectbox(
                    "Filter by Category:",
                    categories
                )

                filtered_memories = []

                for memory in memories:

                    metadata = memory.get("metadata") or {}

                    category = metadata.get(
                        "category",
                        "Uncategorized"
                    )

                    if (
                        selected_category == "All"
                        or selected_category == category
                    ):

                        filtered_memories.append(memory)

                st.write(
                    f"Showing {len(filtered_memories)} memories"
                )

                for index, memory in enumerate(
                    filtered_memories,
                    start=1
                ):

                    metadata = memory.get("metadata") or {}

                    with st.expander(f"Memory {index}"):

                        st.write(memory["content"])

                        source = metadata.get(
                            "source",
                            "Unknown"
                        )

                        current_category = metadata.get(
                            "category",
                            "Uncategorized"
                        )

                        st.caption(f"Source: {source}")

                        st.info(
                            f"Category: {current_category}"
                        )

                        current_index = (
                            MEMORY_CATEGORIES.index(current_category)
                            if current_category in MEMORY_CATEGORIES
                            else 0
                        )

                        new_category = st.selectbox(
                            "Change Category:",
                            MEMORY_CATEGORIES,
                            index=current_index,
                            key=f"category_{memory['id']}"
                        )

                        if st.button(
                            "Update Category",
                            key=f"update_{memory['id']}"
                        ):

                            try:

                                update_memory_category(
                                    memory["id"],
                                    new_category
                                )

                                st.success(
                                    "Category updated successfully!"
                                )

                                st.rerun()

                            except Exception as e:

                                st.error(str(e))

                        if st.button(
                            "🗑️ Delete Memory",
                            key=f"delete_{memory['id']}"
                        ):

                            try:

                                delete_memory(memory["id"])

                                st.success("Memory deleted!")

                                st.rerun()

                            except Exception as e:

                                st.error(str(e))

            else:

                st.info(
                    "No memories found. Add a memory first."
                )

        except Exception as e:

            st.error(
                f"Unable to manage memories: {str(e)}"
            )

    # SEARCH MEMORIES

    elif page == "Search Memories":

        st.header("🔍 Search Your Memories")

        query = st.text_input(
            "Enter your search query:",
            placeholder="Example: Python, education, projects..."
        )

        if st.button("Search"):

            if query.strip():

                try:

                    with st.spinner("Searching memories..."):

                        results = search_memories(query)

                    if results:

                        st.success(
                            f"Found {len(results)} relevant memories."
                        )

                        for index, document in enumerate(
                            results,
                            start=1
                        ):

                            with st.expander(
                                f"Search Result {index}"
                            ):

                                st.write(document.page_content)

                                metadata = document.metadata or {}

                                st.caption(
                                    f"Category: {metadata.get('category', 'Uncategorized')}"
                                )

                    else:

                        st.info("No relevant memories found.")

                except Exception as e:

                    st.error(
                        f"Search failed: {str(e)}"
                    )

            else:

                st.warning("Please enter a search query.")

    # CHAT

    elif page == "Chat":

        st.header("💬 Chat With Your Memories")

        if "current_conversation_id" not in st.session_state:

            st.session_state.current_conversation_id = None

        try:

            conversations = get_conversations()

            title_lookup = {
                chat["id"]: chat["title"]
                for chat in conversations
            }

            conversation_options = ["new"] + [
                chat["id"] for chat in conversations
            ]

            pending_id = st.session_state.pop(
                "pending_conversation_id",
                None
            )

            if pending_id in conversation_options:

                st.session_state["conversation_selector"] = pending_id

                st.session_state.current_conversation_id = pending_id

            if (
                st.session_state.get("conversation_selector")
                not in conversation_options
            ):

                current_id = (
                    st.session_state.current_conversation_id
                )

                st.session_state["conversation_selector"] = (
                    current_id
                    if current_id in conversation_options
                    else "new"
                )

            if st.button(
                "➕ New Chat",
                key="create_new_chat"
            ):

                st.session_state.current_conversation_id = None

                st.session_state["conversation_selector"] = "new"

                st.rerun()

            selected_chat = st.selectbox(
                "Previous Conversations",
                conversation_options,
                format_func=lambda chat_id:
                    "➕ New Chat"
                    if chat_id == "new"
                    else title_lookup.get(
                        chat_id,
                        "Previous Chat"
                    ),
                key="conversation_selector"
            )

            conversation_id = (
                None
                if selected_chat == "new"
                else selected_chat
            )

            st.session_state.current_conversation_id = (
                conversation_id
            )

            # RENAME AND DELETE CHAT

            if conversation_id:

                st.subheader("Manage Conversation")

                with st.expander("✏️ Rename Chat"):

                    new_title = st.text_input(
                        "Enter new conversation name:",
                        value=title_lookup.get(
                            conversation_id,
                            "Previous Chat"
                        ),
                        key=f"rename_{conversation_id}"
                    )

                    if st.button(
                        "Rename",
                        key=f"rename_button_{conversation_id}"
                    ):

                        if new_title.strip():

                            try:

                                rename_conversation(
                                    conversation_id,
                                    new_title.strip()
                                )

                                st.success(
                                    "Chat renamed successfully!"
                                )

                                st.rerun()

                            except Exception as e:

                                st.error(str(e))

                        else:

                            st.warning(
                                "Please enter a chat name."
                            )

                with st.expander("🗑️ Delete Chat"):

                    confirm_delete = st.checkbox(
                        "I confirm that I want to delete this conversation.",
                        key=f"confirm_{conversation_id}"
                    )

                    if st.button(
                        "Delete Conversation",
                        key=f"delete_chat_{conversation_id}"
                    ):

                        if confirm_delete:

                            try:

                                delete_conversation(
                                    conversation_id
                                )

                                st.session_state.current_conversation_id = None

                                st.session_state["conversation_selector"] = "new"

                                st.success(
                                    "Conversation deleted!"
                                )

                                st.rerun()

                            except Exception as e:

                                st.error(str(e))

                        else:

                            st.warning(
                                "Please confirm before deleting."
                            )

            # DISPLAY CHAT HISTORY

            if conversation_id:

                messages = get_messages(conversation_id)

                for message in messages:

                    with st.chat_message(message["role"]):

                        st.markdown(message["content"])

            else:

                st.info("Start a new conversation!")

            st.divider()

            answer_style = st.radio(
                "Choose Answer Style:",
                ["Concise", "Detailed"],
                horizontal=True,
                key="answer_style"
            )

            form_key = (
                f"chat_form_{conversation_id}"
                if conversation_id
                else "chat_form_new"
            )

            with st.form(
                key=form_key,
                clear_on_submit=True
            ):

                prompt = st.text_input(
                    "Your question:",
                    placeholder="Ask something about your memories..."
                )

                submitted = st.form_submit_button("Send")

            if submitted:

                if not prompt.strip():

                    st.warning("Please enter a question.")

                else:

                    try:

                        if not conversation_id:

                            conversation_id = create_conversation(
                                title=prompt.strip()[:50]
                            )

                        save_message(
                            conversation_id,
                            "user",
                            prompt.strip()
                        )

                        with st.spinner(
                            "Searching your memories..."
                        ):

                            answer = ask_question(
                                prompt.strip(),
                                answer_style
                            )

                        save_message(
                            conversation_id,
                            "assistant",
                            answer
                        )

                        st.session_state.current_conversation_id = conversation_id

                        st.session_state["pending_conversation_id"] = conversation_id

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Chat error: {str(e)}"
                        )

        except Exception as e:

            st.error(
                f"Chat history error: {str(e)}"
            )


if __name__ == "__main__":

    main()
