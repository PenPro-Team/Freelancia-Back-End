# --- Imports for Django Command and Langchain ---
import os
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from dotenv import load_dotenv

try:
    from freelancia_back_end.models import Project, Skill # Adjust import path if needed
    from reviews.models import Review
    from portfolio.models import Portfolio
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain_core.documents import Document
except ImportError as e:
    raise ImportError(f"Error importing libraries or models for update_index: {e}. Ensure requirements are installed.") from e

# --- Logging Setup ---
load_dotenv()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Constants ---
VECTOR_STORE_PATH = getattr(settings, 'VECTOR_STORE_PATH', "faiss_vector_store")

# --- Django Management Command Definition ---
class Command(BaseCommand):
    help = 'Rebuilds the FAISS vector store index using LOCAL embeddings.'

    # --- Command Execution Logic ---
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("--- Starting FAISS Index Rebuild (Using Local Embeddings) via Management Command ---"))

        try:
            # --- Initialize Local Embeddings Model ---
            logger.info("Initializing LOCAL Embeddings model...")
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            device_to_use = 'cpu'
            model_kwargs = {'device': device_to_use}
            encode_kwargs = {'normalize_embeddings': False}
            embeddings = HuggingFaceEmbeddings(
                model_name=model_name,
                model_kwargs=model_kwargs,
                encode_kwargs=encode_kwargs
            )
            logger.info(f"Successfully initialized local embeddings model: '{model_name}' on device: '{device_to_use}'")

            # --- Fetch Data and Build Index ---
            documents = self.create_documents_from_db()
            self.build_and_save_index(documents, embeddings)

            self.stdout.write(self.style.SUCCESS("--- FAISS Index Rebuild Finished Successfully (Using Local Embeddings) ---"))

        # --- Error Handling for Local Operations ---
        except ImportError as ie:
            logger.critical(f"Import error during index build: {ie}.")
            self.stderr.write(self.style.ERROR(f"Import error during index build: {ie}"))
        except Exception as e:
            logger.exception(f"An unexpected error occurred during LOCAL index build: {e}")
            self.stderr.write(self.style.ERROR(f"An unexpected error occurred: {e}"))

    # --- Function to Create Documents from Database ---
    def create_documents_from_db(self):
        documents = []
        logger.info("Starting data fetching from database...")
        try:
            projects = Project.objects.prefetch_related('skills').all()
            logger.info(f"Found {projects.count()} projects.")
            for project in projects:
                skills_list = [skill.skill for skill in project.skills.all()]
                skills_str = ', '.join(skills_list) if skills_list else 'No skills listed'
                content = f"Project Name: {project.project_name}\nDescription: {project.project_description}\nRequired Skills: {skills_str}\nStatus: {project.project_state}"
                metadata = {"source": "project", "project_id": project.id, "project_name": project.project_name, "created_at": project.created_at.isoformat() if project.created_at else None}
                documents.append(Document(page_content=content, metadata=metadata))

            portfolios = Portfolio.objects.select_related('user').all()
            logger.info(f"Found {portfolios.count()} portfolio items.")
            for portfolio in portfolios:
                content = f"Portfolio Title: {portfolio.title}\nDescription: {portfolio.description}"
                user_id = portfolio.user.id if portfolio.user else None
                metadata = {"source": "portfolio", "portfolio_id": portfolio.id, "portfolio_title": portfolio.title, "user_id": user_id, "created_at": portfolio.created_at.isoformat() if portfolio.created_at else None}
                documents.append(Document(page_content=content, metadata=metadata))

            reviews = Review.objects.all()
            logger.info(f"Found {reviews.count()} reviews.")
            for review in reviews:
                content = f"Review Message: {review.message}\nRating: {review.rating}"
                metadata = {"source": "review", "review_id": review.id, "created_at": review.created_at.isoformat() if review.created_at else None}
                documents.append(Document(page_content=content, metadata=metadata))

            logger.info(f"Total documents created: {len(documents)}")
            if not documents:
                self.stdout.write(self.style.WARNING("No documents found in the database to index."))
            return documents
        except Exception as e:
            logger.exception(f"Error while fetching data from database: {e}")
            raise

    # --- Function to Build and Save Local FAISS Index ---
    def build_and_save_index(self, documents, embeddings_model):
        if not documents:
            logger.warning("No documents provided to build the index. Skipping save.")
            return

        logger.info(f"Starting FAISS index build for {len(documents)} documents using LOCAL embeddings...")
        try:
            os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
            vectorstore = FAISS.from_documents(documents, embeddings_model)
            vectorstore.save_local(VECTOR_STORE_PATH)
            logger.info(f"FAISS index built and saved successfully to directory: '{VECTOR_STORE_PATH}'")
            self.stdout.write(self.style.SUCCESS(f"FAISS index saved to '{VECTOR_STORE_PATH}' using local embeddings."))
        except Exception as e:
            logger.exception(f"An error occurred during LOCAL FAISS index build or save: {e}")
            raise