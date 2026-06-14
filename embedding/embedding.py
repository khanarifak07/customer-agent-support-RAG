from pypdf import PdfReader
from client.chroma_client import collection
import os
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
load_dotenv()
from pathlib import Path
pdf_path = Path(__file__).parent / "FAQ_RAG_Dataset.pdf"

reader = PdfReader(pdf_path)
number_of_pages = len(reader.pages)

full_text = ""
for page in reader.pages:
    full_text += page.extract_text()

# Vector DB Setup
embedding_model = SentenceTransformer(os.getenv("EMBEDDING_MODEL"))
words = full_text.split()
chunks = [" ".join(words[i:i+100]) for i in range(0, len(words), 100)]

for i, chunk in enumerate(chunks):
    # convert text into vector, then numpy array to python list
    embedding = embedding_model.encode(chunk).tolist()
    collection.add(
        ids=[f"chunk{i}"],
        documents=[chunk],
        embeddings=[embedding]
    )

print("✅ Documents loaded into vector DB\n")

















