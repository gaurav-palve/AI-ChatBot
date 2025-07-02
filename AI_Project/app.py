import streamlit as st
from utils.pdf_reading import extract_text_from_pdfs, chunk_text
from utils.vector_store import build_vector_store
from services.chatbot import ChatbotService
from configs.settings import settings
import os

def main():
    st.set_page_config(page_title="Smart PDF Chatbot", layout="wide")
    st.title("📄 Chat with PDF + 🌐 Google Search")

    chatbot = None
    if os.path.exists(settings.FAISS_INDEX_PATH):
        chatbot = ChatbotService()

    user_question = st.text_input("Ask a question...")
    if user_question and chatbot:
        with st.spinner("Thinking..."):
            response = chatbot.query(user_question)
            st.write(response)

    with st.sidebar:
        st.header("Upload PDFs")
        pdfs = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)
        if st.button("Submit & Index"):
            with st.spinner("Processing..."):
                text = extract_text_from_pdfs(pdfs)
                if not text.strip():
                    st.error("No valid text extracted.")
                    return
                chunks = chunk_text(text)
                build_vector_store(chunks, settings.FAISS_INDEX_PATH)
                st.success("Vector store created. Refresh page to chat.")
                st.rerun()

if __name__ == "__main__":
    main()

