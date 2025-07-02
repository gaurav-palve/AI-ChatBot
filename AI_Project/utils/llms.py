from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from configs.settings import settings

def build_qa_chain(vector_store):
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        model_provider="google_genai",
        temperature=0.3,
        google_api_key=settings.GEMINI_API_KEY
    )

    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vector_store.as_retriever(),
        chain_type="stuff",
        return_source_documents=False
    )
