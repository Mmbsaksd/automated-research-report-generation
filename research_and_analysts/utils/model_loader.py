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
            "GOOGLE_API_KEY":os.getenv()
        }
