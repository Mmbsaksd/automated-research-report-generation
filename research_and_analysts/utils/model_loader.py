import os
import sys
import json
from dotenv import load_dotenv
from utils.config_loader import load_config
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from logger import GLOBAL_LOGGER as log
from exceptions.custom_exception import ResearchAnalystException
import asyncio

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
                log.info(f"{key} loaded fom enviroment")
            else:
                log.warning(f"{key} is missing from enviroment")

    def get(self,key:str):
        return self.api_keys.get(key)
    
class ModelLoader:
    def __init__(self):
        self.api_key_mgr = ApiKeyManager()
        self.config = load_config()
        log.info("YMAL config loaded", config_keys=list(self.config.keys()))

    def load_embeddings(self):
        try:
            model_name = self.config["embedding_model"]["model_name"]
            log.info("Loading embedding model", model=model_name)

            try:
                asyncio.get_event_loop()
            except Exception as e:
                asyncio.set_event_loop(asyncio.new_event_loop)

            return GoogleGenerativeAIEmbeddings(
                model=model_name,
                google_api_key = self.api_key_mgr.get("GOOGLE_API_KEY")
            )
        
        except Exception as e:
            log.error("Error loading embedding model", error=str(e))
            raise ResearchAnalystException("Failed to load embedding model",sys)
        
    def load_llm(self):
        llm_block = self.config["llm"]
        provider_key = os.getenv("LLM_PROVIDER","gemini")
        
        
        


