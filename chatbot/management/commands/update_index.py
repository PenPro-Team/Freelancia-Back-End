# chatbot/management/commands/update_index.py

import os
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from dotenv import load_dotenv

try:
    from freelancia_back_end.models import Project, Skill
    from reviews.models import Review
    from portfolio.models import Portfolio
    from langchain_openai import OpenAIEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain_core.documents import Document
    import openai
except ImportError as e:
    raise ImportError(f"Error importing libraries or models: {e}. Ensure requirements are installed and apps are in INSTALLED_APPS.") from e

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

VECTOR_STORE_PATH = getattr(settings, 'VECTOR_STORE_PATH', "faiss_vector_store")

class Command(BaseCommand):
    help = 'Rebuilds the FAISS vector store index from database content.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("--- Starting FAISS Index Rebuild via Management Command ---"))

        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            logger.error("OPENAI_API_KEY environment variable not found.")
            self.stderr.write(self.style.ERROR("Error: OPENAI_API_KEY not found. Set it in your environment or .env file."))
            return

        if not openai_api_key.startswith("sk-"):
            logger.warning("Warning: OPENAI_API_KEY does not seem to start with 'sk-'. Please verify its validity.")

        try:
            logger.info("Initializing OpenAI Embeddings model...")
            embeddings = OpenAIEmbeddings(api_key=openai_api_key)
            logger.info("Successfully initialized OpenAI Embeddings model.")

            documents = self.create_documents_from_db()

            self.build_and_save_index(documents, embeddings)

            self.stdout.write(self.style.SUCCESS("--- FAISS Index Rebuild Finished Successfully ---"))

        except openai.AuthenticationError as auth_err:
             logger.critical(f"OpenAI Authentication Error: {auth_err}. Check your API key.")
             self.stderr.write(self.style.ERROR(f"OpenAI Authentication Error: {auth_err}. Check API key."))
        except openai.RateLimitError as rate_err:
            logger.critical(f"OpenAI Rate Limit/Quota Error: {rate_err}")
            self.stderr.write(self.style.ERROR(f"OpenAI Rate Limit/Quota Error: {rate_err}"))
        except openai.APIConnectionError as conn_err:
             logger.critical(f"OpenAI API Connection Error: {conn_err}.")
             self.stderr.write(self.style.ERROR(f"OpenAI API Connection Error: {conn_err}"))

        except ImportError as ie:
             logger.critical(f"Import error during index build: {ie}.")
             self.stderr.write(self.style.ERROR(f"Import error during index build: {ie}"))
        except Exception as e:
            logger.exception(f"An unexpected error occurred during index build: {e}")
            self.stderr.write(self.style.ERROR(f"An unexpected error occurred: {e}"))

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

    def build_and_save_index(self, documents, embeddings_model):
        if not documents:
            logger.warning("No documents provided to build the index. Skipping save.")
            return

        logger.info(f"Starting FAISS index build for {len(documents)} documents...")
        try:
            vectorstore = FAISS.from_documents(documents, embeddings_model)
            os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
            vectorstore.save_local(VECTOR_STORE_PATH)
            logger.info(f"FAISS index built and saved successfully to directory: '{VECTOR_STORE_PATH}'")
            self.stdout.write(self.style.SUCCESS(f"FAISS index saved to '{VECTOR_STORE_PATH}'"))
        except Exception as e:
            logger.exception(f"An error occurred during FAISS index build or save: {e}")
            raise