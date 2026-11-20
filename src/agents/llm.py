import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEndpoint
from langchain_openrouter import ChatOpenRouter
# gemma-4-31b-it
# gemini-3.1-flash-lite
def instanciar_llm(model="gemini-3.1-flash-lite"):
    return ChatGoogleGenerativeAI(
        model=model,
        api_key=os.getenv("GEMINI"),
    )
    
def instanciar_llm_hug(model="deepseek-ai/DeepSeek-R1-0528"):
    return HuggingFaceEndpoint(
       model="google/gemma-4-12B-it",
        task="text-generation",
        # task="text-generation",
        max_new_tokens=1024,
        do_sample=False,
        # model=model,
        repetition_penalty=1.03,
        # provider="auto",  # let Hugging Face choose the best provider for you
    )


def instanciar_llm_open_router(model="google/gemma-4-31b-it:free"):
    return ChatOpenRouter(
        model=model,
        temperature=0,
        # max_tokens=1024,
        # max_retries=2,
        # other params...
    )
