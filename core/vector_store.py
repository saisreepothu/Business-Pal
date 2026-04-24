import hashlib
import time

import streamlit as st
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import (
    OPENAI_API_KEY,
    PINECONE_API_KEY,
    PINECONE_INDEX_NAME,
    PINECONE_CLOUD,
    PINECONE_REGION,
    EMBEDDING_MODEL,
    EMBEDDING_DIMENSION,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    MIN_CONTEXT_CHARS,
    RAG_TOP_K,
)


@st.cache_resource
def _pinecone_client():
    return Pinecone(api_key=PINECONE_API_KEY)


def _wait_for_ready(pc: Pinecone, index_name: str, timeout: int = 90) -> None:
    start = time.time()
    while time.time() - start < timeout:
        status = pc.describe_index(index_name).status
        if status.get("ready"):
            return
        time.sleep(3)
    raise TimeoutError(f"Pinecone index '{index_name}' not ready after {timeout}s")


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), reraise=True)
def _upsert_texts(chunks, embeddings, namespace: str):
    return PineconeVectorStore.from_texts(
        chunks,
        embeddings,
        index_name=PINECONE_INDEX_NAME,
        namespace=namespace,
    )


def get_or_create_pinecone_index(context_text: str):
    """
    Idempotent: creates the Pinecone index once, then reuses content-addressed
    namespaces. Never deletes the index; same document skips all API calls.
    """
    if not context_text or len(context_text) < MIN_CONTEXT_CHARS:
        return None, None

    namespace = hashlib.md5(context_text.encode()).hexdigest()

    # Skip entirely if this exact context is already indexed in this session
    if st.session_state.get("context_hash") == namespace:
        return st.session_state.pinecone_index, namespace

    pc = _pinecone_client()
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL, api_key=OPENAI_API_KEY)
    existing = pc.list_indexes().names()

    if PINECONE_INDEX_NAME not in existing:
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=EMBEDDING_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(cloud=PINECONE_CLOUD, region=PINECONE_REGION),
        )
        _wait_for_ready(pc, PINECONE_INDEX_NAME)
    else:
        # Check if this namespace already has vectors — skip embedding if so
        index = pc.Index(PINECONE_INDEX_NAME)
        stats = index.describe_index_stats()
        if namespace in stats.get("namespaces", {}):
            vector_store = PineconeVectorStore(
                index=index, embedding=embeddings, namespace=namespace
            )
            return vector_store, namespace

    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    chunks = splitter.split_text(context_text)
    vector_store = _upsert_texts(chunks, embeddings, namespace)
    return vector_store, namespace


def retrieve_relevant_context(query: str, k: int = RAG_TOP_K) -> str:
    if not st.session_state.pinecone_index:
        return st.session_state.business_context[:3000]
    try:
        results = st.session_state.pinecone_index.similarity_search(query, k=k)
        return "\n\n".join(doc.page_content for doc in results)
    except Exception as e:
        st.error(f"Context retrieval error: {e}")
        return st.session_state.business_context[:3000]
