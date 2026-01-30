import os
import sys
from pathlib import Path
import json
from dotenv import load_dotenv
from research_and_analysts.utils.config_loader import load_config
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from research_and_analysts.logger import GLOBAL_LOGGER as log
from research_and_analysts.exceptions.custom_exception import ResearchAnalystException
import asyncio


env_path = Path(__file__).resolve().parents[2] / ".env" # <-- CHANGE if .env is in a different location
if env_path.exists():
    load_dotenv(env_path)
else:
# fallback: try loading default .env in current working directory
    load_dotenv()

class ApiKeyManager:
    def __init__(self):
        self.api_keys = {
            "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
            "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),

            # Azure (FIXED)
            "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY"),
            "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT"),
            "AZURE_OPENAI_API_VERSION": os.getenv("AZURE_OPENAI_API_VERSION"),
            "AZURE_OPENAI_DEPLOYMENT_NAME": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            "AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME": os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"),
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
            embedding_cfg = self.config["embedding_model"]
            deployment_env = embedding_cfg["deployment_name_env"]
            deployment_name = os.getenv(deployment_env)

            if not deployment_name:
                raise ValueError(f"Missing embedding deployment env: {deployment_env}")

            return AzureOpenAIEmbeddings(
                azure_deployment=deployment_name,
                azure_endpoint=self.api_key_mgr.get("AZURE_OPENAI_ENDPOINT"),
                api_key=self.api_key_mgr.get("AZURE_OPENAI_API_KEY"),
                api_version=self.api_key_mgr.get("AZURE_OPENAI_API_VERSION"),
            )

        except Exception as e:
            log.error("Error loading Azure embedding model", error=str(e))
            raise ResearchAnalystException("Failed to load Azure embedding model", sys)


        
    def load_llm(self):
        llm_block = self.config["llm"]
        provider_key = os.getenv("LLM_PROVIDER","openai")

        if provider_key not in llm_block:
            log.error("LLM provider not found in config", provider = provider_key)
            raise ValueError(f"LLM provider '{provider_key}' not found in config")
        
        llm_config = llm_block[provider_key]
        provider = llm_config.get("provider")
        model_name = llm_config.get("model_name")
        temperature = llm_config.get("temperature",0.2)
        max_tokens = llm_config.get("max_output_tokens", 2048)

        log.info("Loading LLM", provider=provider, model=model_name)
        if provider == "azure":
            deployment_env = llm_config["deployment_name_env"]
            deployment_name = os.getenv(deployment_env)

            if not deployment_name:
                raise ValueError(f"Missing Azure deployment env: {deployment_env}")

            return AzureChatOpenAI(
                azure_deployment=deployment_name,
                azure_endpoint=self.api_key_mgr.get("AZURE_OPENAI_ENDPOINT"),
                api_key=self.api_key_mgr.get("AZURE_OPENAI_API_KEY"),
                api_version=self.api_key_mgr.get("AZURE_OPENAI_API_VERSION"),
                temperature=temperature,
            )


        elif provider=="google":
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
        elif provider == "openai":
            return ChatOpenAI(
                model=model_name,
                api_key=self.api_key_mgr.get("OPENAI_API_KEY"),
                temperature=temperature,
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
        
        


