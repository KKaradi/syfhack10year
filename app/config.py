import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    MODEL_NAME = "gemini-2.0-flash-exp"
    MAX_OUTPUT_TOKENS = 8192
    TEMPERATURE = 0.7
    
    # File paths
    CONFLUENCE_DOCS_PATH = "confluence_docs"
    
    @classmethod
    def validate_config(cls):
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is required") 