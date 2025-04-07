import os
import sys
import django
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "freelancia.settings") # Adjust if your settings module is different

try:
    print("Initializing Django...")
    django.setup()
    print("Django initialized successfully.")
except Exception as e:
    print(f"Error initializing Django: {e}")
    sys.exit(1)

# --- Langchain and Project Model Imports ---
try:
    from freelancia_back_end.models import Project, Skill # Adjust import path if needed
    from reviews.models import Review
    from portfolio.models import Portfolio
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain_core.documents import Document
    print("Required libraries and models imported successfully.")
except ImportError as e:
    print(f"Error importing libraries or models: {e}")
    print("Ensure required packages like langchain-community, faiss-cpu, sentence-transformers, torch, accelerate are installed.")
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred during imports: {e}")
    sys.exit(1)

# --- Constants ---
VECTOR_STORE_PATH = "faiss_vector_store"

# --- Initialize Local Embeddings Model ---
print("Initializing LOCAL Embeddings model...")
try:
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    device_to_use = 'cpu'
    model_kwargs = {'device': device_to_use}
    encode_kwargs = {'normalize_embeddings': False}
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    print(f"Successfully initialized local embeddings model: '{model_name}' on device: '{device_to_use}'")
except Exception as e:
    print(f"ERROR initializing local Embeddings model: {e}")
    print("Troubleshooting: Check installations (sentence-transformers, torch, accelerate), model name, internet (first run), resources.")
    sys.exit(1)

# --- Function to Create Documents from Database ---
def create_documents_from_db():
    documents = []
    print("Starting data fetching from database...")
    try:
        projects = Project.objects.all()
        print(f"Found {projects.count()} projects.")
        for project in projects:
            skills_str = ', '.join(
                skill.skill for skill in project.skills.all())
            content = (
                f"Project Name: {project.project_name}\n"
                f"Description: {project.project_description}\n"
                f"Required Skills: {skills_str}\n"
                f"Status: {project.project_state}"
            )
            metadata = {
                "source": "project", "project_id": project.id, "project_name": project.project_name,
                "created_at": project.created_at.isoformat() if project.created_at else None,
            }
            documents.append(Document(page_content=content, metadata=metadata))

        portfolios = Portfolio.objects.all()
        print(f"Found {portfolios.count()} portfolio items.")
        for portfolio in portfolios:
            content = (
                f"Portfolio Title: {portfolio.title}\n"
                f"Description: {portfolio.description}"
            )
            user_id = portfolio.user.id if hasattr(
                portfolio, 'user') and portfolio.user else None
            metadata = {
                "source": "portfolio", "portfolio_id": portfolio.id, "portfolio_title": portfolio.title,
                "user_id": user_id, "created_at": portfolio.created_at.isoformat() if portfolio.created_at else None,
            }
            documents.append(Document(page_content=content, metadata=metadata))

        reviews = Review.objects.all()
        print(f"Found {reviews.count()} reviews.")
        for review in reviews:
            content = (
                f"Review Message: {review.message}\n"
                f"Rating: {review.rate}"
            )
            metadata = {
                "source": "review", "review_id": review.id,
                "created_at": review.created_at.isoformat() if review.created_at else None,
            }
            documents.append(Document(page_content=content, metadata=metadata))

        print(f"Total documents created: {len(documents)}")
        return documents
    except Exception as e:
        print(f"Error fetching data from database: {e}")
        sys.exit(1)

# --- Function to Build and Save Local FAISS Index ---
def build_and_save_index(documents, embeddings_model):
    if not documents:
        print("No documents provided to build the index. Exiting.")
        return

    print(f"Starting FAISS index build for {len(documents)} documents using LOCAL embeddings...")
    try:
        vectorstore = FAISS.from_documents(documents, embeddings_model)
        vectorstore.save_local(VECTOR_STORE_PATH)
        print(f"FAISS index built and saved successfully to directory: '{VECTOR_STORE_PATH}' using local embeddings.")
    except ImportError:
        print("Error: FAISS library not found. Install faiss-cpu or faiss-gpu.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred during LOCAL FAISS index build or save: {e}")
        print("Troubleshooting: Check permissions, disk space, system resources.")
        sys.exit(1)

# --- Main Script Execution ---
if __name__ == "__main__":
    print("\n--- Starting Index Build Process (Using Local Embeddings) ---")
    all_documents = create_documents_from_db()
    build_and_save_index(all_documents, embeddings)
    print("\n--- Index Build Process Finished Successfully (Using Local Embeddings) ---")
