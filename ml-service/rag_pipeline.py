import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA

# Load environment variables
load_dotenv()

# Initialize global variables
VECTOR_DB_PATH = "./chroma_db"
COLLECTION_NAME = "museum_context"

def initialize_vector_db():
    """Initializes the Chroma vector database."""
    embeddings = OpenAIEmbeddings()
    vector_db = Chroma(
        persist_directory=VECTOR_DB_PATH,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME
    )
    return vector_db

def ingest_document(file_path):
    """Ingests a document (PDF or Text) into the vector database."""
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith(".txt"):
        loader = TextLoader(file_path)
    else:
        raise ValueError("Unsupported file format. Only PDF and TXT are supported.")

    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)

    vector_db = initialize_vector_db()
    vector_db.add_documents(texts)
    vector_db.persist()
    print(f"Successfully ingested {file_path}")

def query_rag(query, language="en"):
    """Queries the RAG system and returns a response."""
    vector_db = initialize_vector_db()
    retriever = vector_db.as_retriever(search_kwargs={"k": 3})
    
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)
    
    # Custom prompt could be added here to handle multi-lingual responses
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )
    
    result = qa_chain({"query": query})
    return result["result"]

if __name__ == "__main__":
    # Example usage
    # ingest_document("sample_museum_data.txt")
    # response = query_rag("Tell me about the King's Palace Museum.")
    # print(response)
    print("RAG Pipeline Initialized")
