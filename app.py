
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

            col1, col2 = st.columns(2)

            with col1:
                st.metric("Total Memories", len(memories))

            with col2:
                st.metric(
                    "Total Conversations",
                    len(conversations)
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

    # ADD MEMORIES

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
                                st.warning("No memory content was saved.")

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

                current_id = st.session_state.current_conversation_id

                st.session_state["conversation_selector"] = (
                    current_id
                    if current_id in conversation_options
                    else "new"
                )

            if st.button("➕ New Chat", key="create_new_chat"):

                st.session_state.current_conversation_id = None
                st.session_state["conversation_selector"] = "new"

                st.rerun()

            selected_chat = st.selectbox(
                "Previous Conversations",
                conversation_options,
                format_func=lambda chat_id:
                    "➕ New Chat"
                    if chat_id == "new"
                    else title_lookup.get(chat_id, "Previous Chat"),
                key="conversation_selector"
            )

            conversation_id = (
                None if selected_chat == "new"
                else selected_chat
            )

            st.session_state.current_conversation_id = conversation_id

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

                                st.success("Chat renamed successfully!")
                                st.rerun()

                            except Exception as e:
                                st.error(str(e))

                        else:
                            st.warning("Please enter a chat name.")

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

                                delete_conversation(conversation_id)

                                st.session_state.current_conversation_id = None
                                st.session_state["conversation_selector"] = "new"

                                st.success("Conversation deleted!")
                                st.rerun()

                            except Exception as e:
                                st.error(str(e))

                        else:
                            st.warning("Please confirm before deleting.")

            # DISPLAY CHAT HISTORY

            if conversation_id:

                messages = get_messages(conversation_id)

                for message in messages:

                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

            else:
                st.info("Start a new conversation!")

            
            # SAVE WEB ANSWER AND ORIGINAL SOURCES

            pending_answer = st.session_state.get(
                "pending_web_answer"
            )

            pending_results = st.session_state.get(
                "pending_web_results",
                []
            ) or []

            pending_conversation = st.session_state.get(
                "pending_web_answer_conversation"
            )

            if (
                pending_answer
                and conversation_id
                and pending_conversation == conversation_id
            ):

                st.divider()
                st.subheader("💾 Save Web Search Information")

                st.write(
                    "Choose what you want to save to your permanent memories."
                )

                if pending_results:

                    with st.expander("🌐 View Original Web Sources"):

                        for index, result in enumerate(
                            pending_results,
                            start=1
                        ):
                            st.markdown(
                                f"**{index}. {result.get('title', 'Untitled Source')}**"
                            )

                            st.write(
                                result.get("description", "")
                            )

                            url = result.get("url", "")

                            if url:
                                st.markdown(f"[Open Source]({url})")

                            st.divider()

                else:
                    st.warning(
                        "No original web sources were returned by the search."
                    )

                save_option = st.radio(
                    "Select what to save:",
                    ["AI Answer", "Web Sources", "Both"],
                    horizontal=True,
                    key="web_save_option"
                )

                save_category = st.selectbox(
                    "Choose Memory Category:",
                    MEMORY_CATEGORIES,
                    index=2,
                    key="web_save_category"
                )

                if st.button(
                    "💾 Save Selected Information",
                    key="save_web_information"
                ):

                    try:

                        documents_to_save = []

                        # SAVE AI ANSWER

                        if save_option in ["AI Answer", "Both"]:

                            if not memory_exists(pending_answer):

                                documents_to_save.append(
                                    Document(
                                        page_content=pending_answer,
                                        metadata={
                                            "source": "Web Search Answer",
                                            "category": save_category,
                                            "memory_type": "web_search_answer"
                                        }
                                    )
                                )

                        # SAVE ORIGINAL WEB SOURCES

                        if save_option in ["Web Sources", "Both"]:

                            for result in pending_results:

                                title = result.get("title", "Untitled Source")
                                description = result.get("description", "")
                                url = result.get("url", "")

                                source_content = (
                                    f"Title: {title}\n"
                                    f"Description: {description}\n"
                                    f"Source URL: {url}"
                                )

                                if description or url:

                                    documents_to_save.append(
                                        Document(
                                            page_content=source_content,
                                            metadata={
                                                "source": "Web Search Source",
                                                "category": save_category,
                                                "memory_type": "web_search_source",
                                                "title": title,
                                                "url": url
                                            }
                                        )
                                    )

                        # SAVE TO CHROMADB

                        if documents_to_save:

                            with st.spinner(
                                "Saving information to ChromaDB..."
                            ):

                                total_chunks = save_documents(
                                    documents_to_save
                                )

                            if total_chunks > 0:

                                st.success(
                                    f"Successfully saved {total_chunks} memory chunks!"
                                )

                            else:

                                st.warning(
                                    "No information was saved."
                                )

                        else:

                            st.warning(
                                "There is no new information to save."
                            )

                        # CLEAR PENDING DATA AFTER SAVE

                        st.session_state.pending_web_answer = None
                        st.session_state.pending_web_results = []
                        st.session_state.pending_web_answer_conversation = None

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Unable to save information: {str(e)}"
                        )


                    except Exception as e:

                        st.error(
                            f"Unable to save information: {str(e)}"
                        )

            st.divider()

            # ANSWER STYLE

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

            # CHAT INPUT FORM

            with st.form(
                key=form_key,
                clear_on_submit=True
            ):

                use_web = st.checkbox(
                    "🌐 Search the Web for latest information",
                    value=False
                )

                prompt = st.text_input(
                    "Your question:",
                    placeholder="Ask something about your memories..."
                )

                submitted = st.form_submit_button("Send")

            # PROCESS USER QUESTION

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
                            "Searching memories and the web..."
                            if use_web
                            else "Searching your memories..."
                        ):

                            result = ask_question(
                                prompt.strip(),
                                answer_style,
                                use_web=use_web
                            )

                        answer = result["answer"]
                        web_results = result["web_results"]

                        # ADD SOURCE LINKS TO CHAT HISTORY

                        chat_answer = answer

                        if web_results:

                            chat_answer += "\n\n### Web Sources\n"

                            for index, source in enumerate(
                                web_results,
                                start=1
                            ):

                                if source["url"]:

                                    chat_answer += (
                                        f"\n{index}. "
                                        f"[{source['title']}]"
                                        f"({source['url']})"
                                    )

                                else:

                                    chat_answer += (
                                        f"\n{index}. {source['title']}"
                                    )

                        save_message(
                            conversation_id,
                            "assistant",
                            chat_answer
                        )

                        # KEEP ANSWER AND SOURCES FOR SAVING

                        if use_web:

                            st.session_state.pending_web_answer = answer
                            st.session_state.pending_web_results = web_results

                            st.session_state.pending_web_answer_conversation = conversation_id

                        else:

                            st.session_state.pending_web_answer = None
                            st.session_state.pending_web_results = []
                            st.session_state.pending_web_answer_conversation = None

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
