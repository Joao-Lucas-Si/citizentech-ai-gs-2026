import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_openrouter import ChatOpenRouter

# gemma-4-31b-it
# gemini-3.1-flash-lite
def instanciar_llm(model="gemini-3.1-flash-lite"):
    return ChatGoogleGenerativeAI(
        model=model,
        api_key=os.getenv("GEMINI"),
    )
  