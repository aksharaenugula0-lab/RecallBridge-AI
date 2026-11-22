
from utils.rag_pipeline import ask_question

try:
    question = "What is my project?"

    answer = ask_question(question)

    print("Question:", question)
    print("\nAI Answer:", answer)

except Exception as e:
    print("RAG test failed:", str(e))
