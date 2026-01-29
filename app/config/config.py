import os
from dotenv import load_dotenv
load_dotenv()


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

HF_TOKEN = os.environ.get("HF_TOKEN")
BEDROCK_EMBEDDING_ID = os.getenv("BEDROCK_EMBEDDING_ID")


DB_FAISS_PATH = os.path.join(BASE_DIR, "vectorstore", "db_faiss")
DATA_PATH = os.path.join(BASE_DIR, "data", "pdfs")

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
