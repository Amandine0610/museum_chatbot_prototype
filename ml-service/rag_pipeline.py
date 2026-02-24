import os
from dotenv import load_dotenv

load_dotenv()

# Only import RAG deps if API key is available
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

vector_store = None
qa_chain = None

def initialize_rag():
    global vector_store, qa_chain

    if not OPENAI_API_KEY:
        print("WARNING: OPENAI_API_KEY not set. Running in mock mode.")
        return

    try:
        from langchain_community.document_loaders import TextLoader
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_openai import OpenAIEmbeddings, ChatOpenAI
        from langchain_chroma import Chroma
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.runnables import RunnablePassthrough
        from langchain_core.output_parsers import StrOutputParser

        # 1. Load museum data
        loader = TextLoader("museum_data.txt", encoding="utf-8")
        documents = loader.load()

        # 2. Split into chunks
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        chunks = splitter.split_documents(documents)

        # 3. Embed and store in ChromaDB
        embeddings = OpenAIEmbeddings()
        vector_store = Chroma.from_documents(chunks, embeddings, collection_name="museum")

        # 4. Build LCEL chain
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

        prompt = ChatPromptTemplate.from_template(
            """You are a culturally knowledgeable guide for Rwandan museums.
Use the following context to answer the visitor's question in a warm, engaging way.
If you don't know the answer from the context, say so politely.

Context: {context}

Question: {question}

Answer:"""
        )

        qa_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        print("✅ RAG Pipeline initialized successfully.")

    except Exception as e:
        print(f"❌ RAG init error: {e}")
        qa_chain = None


def get_answer(query: str) -> str:
    if qa_chain is None:
        # Mock response when no API key / RAG not initialized
        return (
            f"[Demo Mode] You asked: '{query}'. "
            "In production, the RAG pipeline retrieves answers from verified museum archives. "
            "Please set OPENAI_API_KEY in ml-service/.env to enable live responses."
        )
    try:
        return qa_chain.invoke(query)
    except Exception as e:
        return f"Error generating response: {str(e)}"
