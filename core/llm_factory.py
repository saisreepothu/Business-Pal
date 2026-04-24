import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_deepseek import ChatDeepSeek
from config.settings import OPENAI_API_KEY, GOOGLE_API_KEY, DEEPSEEK_API_KEY


@st.cache_resource
def _openai_client(model_name: str):
    return ChatOpenAI(model=model_name, temperature=0.3, api_key=OPENAI_API_KEY)


@st.cache_resource
def _gemini_client():
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash", temperature=0.3, google_api_key=GOOGLE_API_KEY
    )


@st.cache_resource
def _deepseek_client():
    return ChatDeepSeek(
        model="deepseek-reasoner", temperature=0.3, api_key=DEEPSEEK_API_KEY
    )


def get_llm(model_name: str):
    if model_name.startswith("gpt"):
        return _openai_client(model_name)
    elif model_name == "gemini-1.5-flash":
        return _gemini_client()
    elif model_name == "deepseek-reasoner":
        return _deepseek_client()
    return _openai_client("gpt-4o")
