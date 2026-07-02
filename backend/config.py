import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DEBUG = os.getenv("DEBUG", "False") == "True"

    PORT = int(os.getenv("PORT", 5000))

    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    DATA_DIR = os.path.join(BASE_DIR, "..", "data")

    UPLOAD_FOLDER = os.path.join(DATA_DIR, "uploads")

    CHROMA_DB_PATH = os.path.join(DATA_DIR, "chromadb")

    MAX_CONTENT_LENGTH = 50 * 1024 * 1024