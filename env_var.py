from dotenv import load_dotenv
load_dotenv()
import os

api_key = os.getenv("API_KEY")
base_url = os.getenv("BASE_URL")
model = os.getenv("MODEL")
embedding_model = os.getenv("EMBEDDING_MODEL")