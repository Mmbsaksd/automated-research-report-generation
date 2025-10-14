import os
import sys
from pathlib import Path
import json
from dotenv import load_dotenv
from research_and_analysts.utils.config_loader import load_config
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from research_and_analysts.logger import GLOBAL_LOGGER as log
from research_and_analysts.exceptions.custom_exception import ResearchAnalystException
import asyncio


# env_path = Path(__file__).resolve().parents[2] / ".env" # <-- CHANGE if .env is in a different location
# if env_path.exists():
#     load_dotenv(env_path)
# else:
# # fallback: try loading default .env in current working directory
#     load_dotenv()

class ApiKeyManager:
    def __init__(self):
        self.api_keys = {
            "GOOGLE_API_KEY":os.getenv("GOOGLE_API_KEY"),
            "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
            "ASTRA_DB_API_ENDPOINT": os.getenv("ASTRA_DB_API_ENDPOINT"),
            "ASTRA_DB_APPLICATION_TOKEN": os.getenv("ASTRA_DB_APPLICATION_TOKEN"),
            "ASTRA_DB_KEYSPACE":os.getenv("ASTRA_DB_KEYSPACE")
        }
        for key,val in self.api_keys.items():
            if val:
                log.info(f"{key} loaded from environment")
            else:
                log.warning(f"{key} is missing from environment")

    def get(self,key:str):
        return self.api_keys.get(key)
    
class ModelLoader:
    def __init__(self):
        self.api_key_mgr = ApiKeyManager()
        self.config = load_config()
        log.info("YAML config loaded", config_keys=list(self.config.keys()))

    def load_embeddings(self):
        try:
            model_name = self.config["embedding_model"]["model_name"]
            log.info("Loading embedding model", model=model_name)

            try:
                asyncio.get_running_loop()
            except Exception as e:
                asyncio.set_event_loop(asyncio.new_event_loop())

            return GoogleGenerativeAIEmbeddings(
                model=model_name,
                google_api_key = self.api_key_mgr.get("GOOGLE_API_KEY")
            )
        
        except Exception as e:
            log.error("Error loading embedding model", error=str(e))
            raise ResearchAnalystException("Failed to load embedding model",sys)
        
    def load_llm(self):
        llm_block = self.config["llm"]
        provider_key = os.getenv("LLM_PROVIDER","google")

        if provider_key not in llm_block:
            log.error("LLM provider not found in config", provider = provider_key)
            raise ValueError(f"LLM provider '{provider_key}' not found in config")
        
        llm_config = llm_block[provider_key]
        provider = llm_config.get("provider")
        model_name = llm_config.get("model_name")
        temperature = llm_config.get("temperature",0.2)
        max_tokens = llm_config.get("max_output_tokens", 2048)

        log.info("Loading LLM", provider=provider, model=model_name)

        if provider=="google":
            return ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=self.api_key_mgr.get("GOOGLE_API_KEY"),
                temperature=temperature,
                max_output_tokens = max_tokens
            )
        elif provider == "groq":
            return ChatGroq(
                model=model_name,
                api_key=self.api_key_mgr.get("GROQ_API_KEY"),
                temperature=temperature
            )
        else:
            log.error("Unsupported LLM provider", provider=provider)
            raise ValueError(f"Unsupported LLM provider: {provider}")

if __name__ == "__main__":
    loader = ModelLoader()

    #Testing embedding
    embeddings = loader.load_embeddings()
    print(f"Embedding Model Loaded: {embeddings}")
    result = embeddings.embed_query("Hello, how are you")
    print(f"Embedding Result: {result}")

    #Test LLM
    llm = loader.load_llm()
    print(f"LLM Loaded: {llm}")
    result = llm.invoke("Hello, how are you")
    print(f"LLM Result: {result}")
        
        


