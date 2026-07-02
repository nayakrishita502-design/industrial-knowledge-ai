import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DEBUG = os.getenv("DEBUG", "True") == "True"

    PORT = int(os.getenv("PORT", 5000))

    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "..", "data", "uploads")

    CHROMA_DB_PATH = os.path.join(BASE_DIR, "..", "data", "chromadb")

    MAX_CONTENT_LENGTH = 50 * 1024 * 1024