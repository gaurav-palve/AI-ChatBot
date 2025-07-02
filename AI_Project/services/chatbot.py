from utils.vector_store import load_vector_store
from utils.llms import build_qa_chain
from utils.search import search_google
from configs.settings import settings
import os

class ChatbotService:
    def __init__(self):
        self.vector_store = None
        self.qa_chain = None

        faiss_file = os.path.join(settings.FAISS_INDEX_PATH, "index.faiss")
        if os.path.exists(faiss_file):
            try:
                self.vector_store = load_vector_store(settings.FAISS_INDEX_PATH)
                self.qa_chain = build_qa_chain(self.vector_store)
            except Exception as e:
                print(f"[FAISS Load Error] {e}")
                self.vector_store = None

    def _is_unhelpful_answer(self, answer):
        # Basic filtering of vague/irrelevant responses
        bad_phrases = [
            "I am sorry", "I couldn't find", "not in the document", "no relevant information",
            "does not contain", "I don't know", "I'm not sure"
        ]
        return any(phrase.lower() in answer.lower() for phrase in bad_phrases) or len(answer.strip()) < 30

    def query(self, user_question):
        # Step 1: Try PDF semantic search
        if self.qa_chain:
            try:
                result = self.qa_chain.invoke({"query": user_question})
                answer = result.get('result', '') if isinstance(result, dict) else str(result)

                if answer and not self._is_unhelpful_answer(answer):
                    return f"📘 From PDF:\n\n{answer}"
            except Exception:
                pass

        # Step 2: Fallback to Google
        web_answer = search_google(user_question)
        return f"🌐 From Google:\n\n{web_answer}"

