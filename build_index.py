import os
import sys
import django
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "freelancia.settings")

try:
    print("Initializing Django...")
    django.setup()
    print("Django initialized successfully.")
except Exception as e:
    print(f"Error initializing Django: {e}")
    print("Please ensure DJANGO_SETTINGS_MODULE is set correctly ('project_name.settings').")
    print("Also, make sure you are running this script from within your project environment.")
    sys.exit(1)

try:
    from freelancia_back_end.models import Project, Skill
    from reviews.models import Review
    from portfolio.models import Portfolio
    from langchain_openai import OpenAIEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain_core.documents import Document
except ImportError as e:
    print(f"Error importing libraries or models: {e}")
    print("Ensure all requirements are installed: pip install django python-dotenv langchain langchain-openai langchain-community faiss-cpu (or faiss-gpu) openai")
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred during imports: {e}")
    sys.exit(1)


VECTOR_STORE_PATH = "faiss_vector_store"

def get_openai_api_key():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not found.")
        print("Ensure you have a .env file in the project root containing:")
        print("OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        sys.exit(1)
    if not api_key.startswith("sk-"):
         print("Warning: OPENAI_API_KEY does not seem to start with 'sk-'. Please verify it's a valid OpenAI key.")
    return api_key

def create_documents_from_db():
    documents = []
    print("Starting data fetching from database...")

    try:
        projects = Project.objects.all()
        print(f"Found {projects.count()} projects.")
        for project in projects:
            skills_str = ', '.join(skill.skill for skill in project.skills.all())
            content = (
                f"Project Name: {project.project_name}\n"
                f"Description: {project.project_description}\n"
                f"Required Skills: {skills_str}\n"
                f"Status: {project.project_state}"
            )
            metadata = {
                "source": "project",
                "project_id": project.id,
                "project_name": project.project_name,
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
            user_id = portfolio.user.id if hasattr(portfolio, 'user') and portfolio.user else None
            metadata = {
                "source": "portfolio",
                "portfolio_id": portfolio.id,
                "portfolio_title": portfolio.title,
                "user_id": user_id,
                "created_at": portfolio.created_at.isoformat() if portfolio.created_at else None,
            }
            documents.append(Document(page_content=content, metadata=metadata))

        reviews = Review.objects.all()
        print(f"Found {reviews.count()} reviews.")
        for review in reviews:
            content = (
                f"Review Message: {review.message}\n"
                f"Rating: {review.rating}"
            )
            metadata = {
                "source": "review",
                "review_id": review.id,
                "created_at": review.created_at.isoformat() if review.created_at else None,
            }
            documents.append(Document(page_content=content, metadata=metadata))

        print(f"Total documents created: {len(documents)}")
        return documents

    except Exception as e:
        print(f"Error fetching data from database: {e}")
        sys.exit(1)


def build_and_save_index(documents, embeddings_model):
    if not documents:
        print("No documents provided to build the index. Exiting.")
        return

    print(f"Starting FAISS index build for {len(documents)} documents...")
    try:
        vectorstore = FAISS.from_documents(documents, embeddings_model)
        vectorstore.save_local(VECTOR_STORE_PATH)
        print(f"FAISS index built and saved successfully to directory: '{VECTOR_STORE_PATH}'")

    except ImportError:
        print("Error: FAISS library not found.")
        print("Please install it using: pip install faiss-cpu  OR  pip install faiss-gpu")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred during FAISS index build or save: {e}")
        print("Verify your internet connection and OpenAI API key validity/quota.")
        print(f"Ensure write permissions for the directory: '{VECTOR_STORE_PATH}'")
        sys.exit(1)

if __name__ == "__main__":
    print("--- Starting Index Build Process ---")

    openai_api_key = get_openai_api_key()

    print("Initializing OpenAI Embeddings model...")
    try:
        embeddings = OpenAIEmbeddings(api_key=openai_api_key)
    except Exception as e:
        print(f"Error initializing OpenAIEmbeddings: {e}")
        sys.exit(1)

    all_documents = create_documents_from_db()

    build_and_save_index(all_documents, embeddings)

    print("--- Index Build Process Finished Successfully ---")