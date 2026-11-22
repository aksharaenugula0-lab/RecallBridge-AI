
import sqlite3
import uuid


DB_NAME = "chat_history.db"


def get_connection():
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    try:
        with get_connection() as connection:

            connection.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            connection.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id)
                    REFERENCES conversations(id)
                    ON DELETE CASCADE
                )
            """)

    except Exception as e:
        raise RuntimeError(
            f"Database initialization failed: {str(e)}"
        )


def create_conversation(title="New Chat"):
    try:
        conversation_id = str(uuid.uuid4())

        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO conversations (id, title)
                VALUES (?, ?)
                """,
                (conversation_id, title)
            )

        return conversation_id

    except Exception as e:
        raise RuntimeError(
            f"Conversation creation failed: {str(e)}"
        )


def save_message(conversation_id, role, content):
    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO messages (conversation_id, role, content)
                VALUES (?, ?, ?)
                """,
                (conversation_id, role, content)
            )

    except Exception as e:
        raise RuntimeError(
            f"Message saving failed: {str(e)}"
        )


def get_conversations():
    try:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT * FROM conversations
                ORDER BY created_at DESC
                """
            ).fetchall()

        return [dict(row) for row in rows]

    except Exception as e:
        raise RuntimeError(
            f"Unable to retrieve conversations: {str(e)}"
        )


def get_messages(conversation_id):
    try:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT * FROM messages
                WHERE conversation_id = ?
                ORDER BY id ASC
                """,
                (conversation_id,)
            ).fetchall()

        return [dict(row) for row in rows]

    except Exception as e:
        raise RuntimeError(
            f"Unable to retrieve messages: {str(e)}"
        )

def rename_conversation(conversation_id, new_title):
    try:
        with get_connection() as connection:
            connection.execute(
                """
                UPDATE conversations
                SET title = ?
                WHERE id = ?
                """,
                (new_title, conversation_id)
            )

        return True

    except Exception as e:
        raise RuntimeError(
            f"Conversation rename failed: {str(e)}"
        )


def delete_conversation(conversation_id):
    try:
        with get_connection() as connection:
            connection.execute(
                """
                DELETE FROM conversations
                WHERE id = ?
                """,
                (conversation_id,)
            )

        return True

    except Exception as e:
        raise RuntimeError(
            f"Conversation deletion failed: {str(e)}"
        )
