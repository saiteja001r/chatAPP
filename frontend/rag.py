from langchain_community.document_loaders import PyPDFLoader
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_mistralai import ChatMistralAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.cache import CacheBackedEmbeddings
from langchain.vectorstores import Chroma
from langchain.storage import LocalFileStore
from sentence_transformers import CrossEncoder  # For reranking
import streamlit as st
import os
import logging
from langchain.callbacks.manager import tracing_v2_enabled
from langchain.prompts import PromptTemplate

# Set LangSmith environment variables
os.environ["LANGCHAIN_TRACING_V2"] = "true"  # Enable LangSmith tracing
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"  # LangSmith API endpoint
os.environ["LANGCHAIN_API_KEY"] = "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"  # Replace with your LangSmith API key
os.environ["LANGCHAIN_PROJECT"] = "interview"  # Project name in LangSmith

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Log LangSmith environment variables
logger.debug(f"LANGCHAIN_TRACING_V2: {os.getenv('LANGCHAIN_TRACING_V2')}")
logger.debug(f"LANGCHAIN_ENDPOINT: {os.getenv('LANGCHAIN_ENDPOINT')}")
logger.debug(f"LANGCHAIN_API_KEY: {os.getenv('LANGCHAIN_API_KEY')}")
logger.debug(f"LANGCHAIN_PROJECT: {os.getenv('LANGCHAIN_PROJECT')}")

# Initialize qa_chain as a global variable
qa_chain = None

def initialize_rag():
    global qa_chain
    with tracing_v2_enabled(project_name="interview"):  # Explicitly enable tracing
        loader = PyPDFLoader(r"files/RAG_QA (4).pdf")
        docs = loader.load()
        text_splitter = CharacterTextSplitter(separator="\n\n", chunk_size=500, chunk_overlap=0, is_separator_regex=False)
        chunks = text_splitter.split_documents(docs)
        store = LocalFileStore("./cache/")
        core_embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

        # Use the cache-backed embedder with the Hugging Face model
        embedder = CacheBackedEmbeddings.from_bytes_store(core_embeddings_model, store, namespace=core_embeddings_model.model_name)
        # Store embeddings in the Chroma vector store
        vectorstore = Chroma.from_documents(chunks, embedder, persist_directory="./chroma_store")

        # Instantiate a retriever from the vector store
        retriever = vectorstore.as_retriever()

        # Initialize RetrievalQA
        llm = ChatMistralAI(model="mistral-large-latest", api_key="zQ6ahWHOHEZVbFepiki6pHLdDrsWEpeR")  # Replace with your Mistral API key
        qa_chain = RetrievalQA.from_chain_type(llm, retriever=retriever)

def rerank_documents(query, documents, top_k=3):
    """
    Rerank documents using a cross-encoder model.
    :param query: The user query.
    :param documents: List of documents to rerank.
    :param top_k: Number of top documents to return.
    :return: Reranked list of documents.
    """
    # Load a cross-encoder model for reranking
    reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")  # You can use other models like "cross-encoder/ms-marco-TinyBERT-L-2-v2"
    
    # Prepare pairs of (query, document) for reranking
    pairs = [(query, doc.page_content) for doc in documents]
    
    # Get scores for each pair
    scores = reranker.predict(pairs)
    
    # Sort documents based on scores
    sorted_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    reranked_documents = [documents[i] for i in sorted_indices[:top_k]]
    
    return reranked_documents

def get_ai_response(prompt):
    global qa_chain
    if qa_chain is None:
        st.error("RAG pipeline is not initialized. Please call initialize_rag() first.")
        return None
    
    # Retrieve documents using the retriever
    retriever = qa_chain.retriever
    documents = retriever.get_relevant_documents(prompt)
    
    # Rerank the retrieved documents
    reranked_documents = rerank_documents(prompt, documents, top_k=3)
    
    # Extract the content of the reranked documents
    context = "\n\n".join([doc.page_content for doc in reranked_documents])
    
    # Define a prompt template for the LLM
    prompt_template = PromptTemplate(
        input_variables=["context", "query"],
        template="""
        You are an intelligent assistant designed to answer questions based on the provided context. 
        Use the following context to answer the query at the end. If you don't know the answer, use your knolwede..."

        Context:
        {context}

        Query: {query}

        Answer:
        """
    )
    
    # Format the prompt with the context and query
    engineered_prompt = prompt_template.format(context=context, query=prompt)
    
    # Generate a response using the engineered prompt
    with st.spinner("Generating AI response..."):
        response = qa_chain.run({"query": engineered_prompt})
    
    return response