import streamlit as st
from PyPDF2 import PdfReader
from io import BytesIO
from dotenv import load_dotenv
import os

from langchain_google_genai import GoogleGenerativeAIEmbeddings,ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA

# Load environment variables
load_dotenv()

# Extract text from uploaded PDFs
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        if pdf is not None:
            reader = PdfReader(BytesIO(pdf.read()))
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
    return text

# Split text into manageable chunks
def get_text_chunks(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    return splitter.split_text(text)

# Create FAISS vector store with Gemini embeddings
def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=os.environ["GEMINI_API_KEY"]
    )
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

# Load QA chain using RetrievalQA and Gemini
def get_conversational_chain(vector_store):
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        model_provider="google_genai",
        temperature=0.3,
        google_api_key=os.environ["GEMINI_API_KEY"]
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vector_store.as_retriever(),
        chain_type="stuff",
        return_source_documents=False
    )
    return qa_chain

# Handle user question
def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=os.environ["GEMINI_API_KEY"]
    )
    db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    chain = get_conversational_chain(db)
    response = chain.invoke({"query": user_question})  # ✅ Use invoke instead of run
    st.write("Reply:", response)

# Streamlit app main function
def main():
    st.set_page_config(page_title="Chat with PDFs", layout="wide")
    st.header("Chat with Smart PDF AI")

    user_question = st.text_input("Ask a question about your documents...")
    if user_question:
        user_input(user_question)

    with st.sidebar:
        st.title("Upload PDFs")
        pdf_docs = st.file_uploader("Upload your PDF files", type=["pdf"], accept_multiple_files=True)

        if st.button("Submit & Process"):
            with st.spinner("Processing PDFs..."):
                raw_text = get_pdf_text(pdf_docs)

                if not raw_text.strip():
                    st.error("No text could be extracted from the uploaded PDFs.")
                    return

                text_chunks = get_text_chunks(raw_text)
                if not text_chunks:
                    st.error("Failed to split text into chunks.")
                    return

                get_vector_store(text_chunks)
                st.success("PDFs processed and ready for questions!")

if __name__ == "__main__":
    main()
