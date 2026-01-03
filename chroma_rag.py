from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader

CHROMA_DIR = "chroma_db"

def create_vector_db():
    loader = TextLoader("data/website_info.txt")
    documents = loader.load()


embeddings = HuggingFaceEmbeddings(
model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Persistence is automatic now
Chroma.from_documents(
documents,
embedding=embeddings,
persist_directory=CHROMA_DIR
)

print("✅ Chroma DB created successfully")

def get_retriever():
    embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"

    )

    vectordb = Chroma(
    persist_directory=CHROMA_DIR,
    embedding_function=embeddings 
    )

    return vectordb.as_retriever(search_kwargs={"k": 2})


if __name__ == "__main__":
    create_vector_db()
