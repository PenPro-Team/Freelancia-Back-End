import os
import logging
from dotenv import load_dotenv
from operator import itemgetter
import json
import uuid
import openai # Required for ChatOpenAI and its specific errors

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Feedback

from langchain_community.embeddings import HuggingFaceEmbeddings # Local Embeddings
from langchain_openai import ChatOpenAI # OpenAI Chat Model
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableBranch, RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

# --- Load Environment Variables and Setup Logger ---
load_dotenv()
logger = logging.getLogger(__name__)

# --- Configuration Constants ---
VECTOR_STORE_PATH = "faiss_vector_store"
LLM_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
DEFAULT_ERROR_MESSAGE = "Sorry, I encountered an issue and couldn't process your request. Please try again later."

# --- Global Variables for Initialized Components ---
vectorstore = None
retriever = None
llm = None
embeddings_model = None
initialization_error = None
checked_openai_api_key_for_chat = None

# --- Chat History Management ---
message_histories = {}
def get_session_history(session_id: str) -> ChatMessageHistory:
    if session_id not in message_histories:
        message_histories[session_id] = ChatMessageHistory()
    return message_histories[session_id]

# --- Initialize Langchain Components ---
def initialize_components():
    global vectorstore, retriever, llm, embeddings_model, initialization_error, checked_openai_api_key_for_chat

    if llm and embeddings_model and (retriever or not os.path.exists(VECTOR_STORE_PATH)):
        logger.debug("Components already initialized.")
        return True, None
    if initialization_error and not llm: # Only return false if core chat model failed before
         logger.warning(f"Initialization previously failed critically: {initialization_error}")
         return False, initialization_error

    logger.info("Initializing LangChain components (Chat Model and Local Embeddings)...")
    current_init_error = None

    # 1. Initialize Chat Model (ChatOpenAI)
    if not llm:
        if checked_openai_api_key_for_chat is None:
            api_key_from_env = os.getenv("OPENAI_API_KEY")
            if not api_key_from_env:
                error_msg = "OpenAI API Key for CHAT MODEL not found."
                logger.critical(error_msg)
                initialization_error = error_msg; return False, error_msg
            logger.info(f"OpenAI API Key for Chat Model loaded (ends in ...{api_key_from_env[-4:]}).")
            checked_openai_api_key_for_chat = api_key_from_env
        try:
            llm = ChatOpenAI(
                model_name=LLM_MODEL_NAME, temperature=0.7,
                api_key=checked_openai_api_key_for_chat, max_retries=2,
            )
            logger.info(f"ChatOpenAI model ('{LLM_MODEL_NAME}') initialized.")
        except Exception as e:
            error_msg = f"Error initializing CHAT model: {e}"
            logger.critical(error_msg, exc_info=True)
            initialization_error = error_msg; llm = None; return False, error_msg

    # 2. Initialize Local Embeddings Model
    if not embeddings_model:
        logger.info("Initializing LOCAL Embeddings model for retrieval...")
        try:
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            device_to_use = 'cpu'
            model_kwargs = {'device': device_to_use}
            encode_kwargs = {'normalize_embeddings': False}
            embeddings_model = HuggingFaceEmbeddings(
                model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs
            )
            logger.info(f"Local embeddings model ('{model_name}') initialized on '{device_to_use}'.")
        except Exception as e:
            error_msg = f"Error initializing LOCAL Embeddings model: {e}"
            logger.error(error_msg, exc_info=True)
            current_init_error = f"{current_init_error + '; ' if current_init_error else ''}{error_msg}"
            embeddings_model = None

    # 3. Load FAISS Index using Local Embeddings
    if retriever is None and embeddings_model:
        if os.path.exists(VECTOR_STORE_PATH):
            logger.info(f"Attempting to load FAISS index from: {VECTOR_STORE_PATH}")
            try:
                vectorstore = FAISS.load_local(
                    VECTOR_STORE_PATH, embeddings_model, allow_dangerous_deserialization=True
                )
                retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={'k': 3})
                logger.info("FAISS index and retriever loaded successfully using local embeddings.")
            except Exception as e:
                error_msg = f"Error loading FAISS index: {e}"
                logger.error(error_msg, exc_info=True)
                current_init_error = f"{current_init_error + '; ' if current_init_error else ''}{error_msg}"
                retriever = None
        else:
            logger.warning(f"FAISS index not found at '{VECTOR_STORE_PATH}'. RAG features unavailable.")
            retriever = None
    elif not embeddings_model and retriever is None: # Ensure retriever is None if embeddings failed
         logger.warning("Local embeddings model failed to initialize. Cannot load FAISS index.")
         retriever = None

    # Final Check
    initialization_error = current_init_error # Store non-critical errors
    if llm:
        logger.info("Component initialization finished. Chat model ready.")
        if not retriever:
            logger.warning("RAG retriever is NOT available. Chatbot will rely on general knowledge.")
        return True, None
    else:
        logger.critical("Core Chat Model (LLM) failed to initialize after attempt. Chatbot cannot function.")
        # Return the critical error if available, otherwise a generic message
        return False, initialization_error if initialization_error else "Unknown LLM initialization failure."

# --- Build Core Langchain Chain ---
def get_core_chain():
    if not llm:
        success, error = initialize_components()
        if not success or not llm:
             raise Exception(f"Core LLM component failed to initialize before chain build: {error}")

    # FAQ Definitions
    FAQS = {
        "create_job": {
            "keywords": ["create job","create a job","post a job", "post job", "add project","make a project","make project", "new listing", "client post", "how do i post", "how to post a job", "steps to create job", "job posting instructions", "publish job", "list a project", "need to hire", "want to post work", "where to post job", "make job listing", "hiring process start", "انشاء وظيفة", "اضافة وظيفة", "نشر وظيفة", "اضافة مشروع", "اضافه مشروع", "كيف انشر وظيفة", "كيف اضيف وظيفة", "خطوات نشر وظيفة", "طريقة نشر عمل", "اعلان عن وظيفة", "عاوز اضيف شغل", "اريد نشر مشروع", "مكان نشر الوظائف", "عميل جديد نشر", "حساب عميل كيف انشر"],
            "answer": "To create a job posting on Freelancia as a client:\n1. Log in to your client account.\n2. Navigate to the 'Post a Job' section (usually found in your dashboard).\n3. Fill out the job details form accurately (Title, detailed Description, required Skills, Budget - fixed or hourly, estimated Duration).\n4. Review your posting and click 'Submit' or 'Post Job'.",
            "topic": "faq_create_job"
        },
        "how_to_bid": {
            "keywords": ["how to bid", "submit proposal", "apply for job", "freelancer apply", "find work", "how do i apply", "steps to bid", "proposal submission", "bidding process", "applying for projects", "get hired", "where to apply", "send offer", "make a bid", "job application", "freelancer job search", "كيف اقدم عرض", "كيف اقدم على وظيفة", "تقديم عرض", "ارسال عرض سعر", "التقديم على وظيفة", "التقديم على مشروع", "طريقة التقديم", "خطوات ارسال العرض", "البحث عن عمل", "كيف الاقي شغل", "فريلانسر كيف اقدم", "تقديم مقترح", "عايز اشتغل", "التقديم للوظائف"],
            "answer": "As a freelancer on Freelancia, to bid on a job (submit a proposal):\n1. Make sure your profile is complete and up-to-date.\n2. Browse the available job listings using search or categories.\n3. Click on a job title to view its full details and requirements.\n4. If you're a good fit, click the 'Submit Proposal' or 'Bid Now' button.\n5. Write a compelling proposal tailored to the job, highlighting your relevant skills and experience.\n6. Enter your bid amount (fixed price or hourly rate as requested) and estimated time to complete the project.\n7. Submit your proposal. Good luck!",
            "topic": "faq_how_to_bid"
        },
        "what_is_freelancia": {
             "keywords": ["what is freelancia", "about this site", "about this platform", "purpose of this website", "explain freelancia", "tell me about freelancia", "freelancia definition", "how freelancia works", "site info", "platform overview", "what do you do", "ما هو فريلانسيا", "ما هي منصة فريلانسيا", "عن الموقع", "عن المنصة", "ما هذا الموقع", "معلومات عن فريلانسيا", "شرح فريلانسيا", "هدف الموقع", "كيف تعمل فريلانسيا", "ايش هو فريلانسيا", "نبذة عن فريلانسيا"],
             "answer": "Freelancia is an online freelance marketplace designed to connect clients who need projects completed with talented freelancers from around the world who have the skills to do the work. Clients can post jobs detailing their requirements, and freelancers can browse these jobs and submit proposals (bids) to get hired.",
             "topic": "faq_what_is_freelancia"
        }
    }

    # FAQ Checking Function
    def check_faq(input_dict):
        question = input_dict.get("question", "").lower()
        history = input_dict.get("history", [])
        for faq_key, faq_data in FAQS.items():
            if any(keyword in question for keyword in faq_data["keywords"]):
                logger.info(f"FAQ detected: {faq_data['topic']}")
                return {"topic": faq_data["topic"], "answer": faq_data["answer"], "question": question, "history": history}
        logger.debug("No FAQ keyword matched.")
        return {"question": question, "history": history} # Pass through if no match
    faq_checker_and_answerer = RunnableLambda(check_faq)

    # Question Classifier
    classifier_template = """Given the user question and conversation history, classify the *latest* user question as either 'specific' or 'general'.
*   'specific' includes questions directly asking about the Freelancia platform's data (projects, skills, portfolios, reviews, listings, how to use the site, features, requirements). Also classify as 'specific' if the user refers to "this website", "here", "the platform", "on Freelancia", or asks about actions on the site.
*   'general' includes greetings, farewells, general knowledge queries, casual chat, or questions unrelated to the Freelancia platform.
Analyze the LATEST question in context. Respond only 'specific' or 'general'.
History: {history}
Latest User Question: {question}
Classification:"""
    classifier_prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}")
    ]).partial(template=classifier_template)
    question_classifier = (classifier_prompt | llm | StrOutputParser())

    # Document Formatting Function
    def format_docs(docs): return "\n\n".join(doc.page_content for doc in docs)

    # Safe Retriever Invocation Function
    def safe_retriever_invoke(input_dict):
        question = input_dict.get("question", "")
        if not retriever:
             logger.warning("Retriever unavailable in safe_retriever_invoke.")
             return "Context unavailable because the knowledge index is not loaded."
        try:
            docs = retriever.invoke(question)
            formatted_docs = format_docs(docs) if docs else "No relevant context found in Freelancia data."
            logger.debug(f"Retrieved context length: {len(formatted_docs)}")
            return formatted_docs
        except Exception as e:
             logger.exception(f"RAG retriever invocation error: {e}")
             return "Error retrieving context due to an internal issue."

    # RAG Chain Definition
    rag_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an AI assistant for Freelancia (freelancia.com). Answer based *only* on provided Freelancia Context and History. If info is missing, state that clearly. Do *not* use external knowledge. Refer to the platform as Freelancia."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "Context:\n{context}\n\nQuestion: {question}"),
    ])
    rag_chain_logic = (
        RunnablePassthrough.assign(context=RunnableLambda(safe_retriever_invoke))
        | rag_prompt | llm | StrOutputParser()
    )

    # General Chain Definition
    general_prompt = ChatPromptTemplate.from_messages([
         ("system", "You are a helpful AI assistant for Freelancia (freelancia.com). Use chat history for context. Answer general questions and engage naturally. Refer to the platform as Freelancia."),
         MessagesPlaceholder(variable_name="history"),
         ("human", "{question}"),
     ])
    general_chain_logic = (general_prompt | llm | StrOutputParser())

    # Routing Logic Function
    def route(info):
        if "answer" in info and "faq" in info.get("topic", ""):
            logger.debug("Routing to: FAQ Answer")
            return RunnableLambda(lambda x: x["answer"]) # Return FAQ answer directly

        logger.debug("Routing based on classification...")
        try:
            classification_input = {"question": info["question"], "history": info.get("history", [])}
            classification_result = question_classifier.invoke(classification_input).lower().strip()
            logger.info(f"Classification for routing: '{classification_result}'")

            if "specific" in classification_result and retriever:
                logger.debug("Routing to: RAG Chain")
                return rag_chain_logic
            else:
                if "specific" in classification_result and not retriever:
                    logger.warning("Classified as specific, but RAG unavailable. Falling back to General Chain.")
                logger.debug("Routing to: General Chain")
                return general_chain_logic
        except Exception as e:
             logger.exception(f"Error during routing classification or logic: {e}")
             logger.warning("Falling back to General Chain due to routing error.")
             return general_chain_logic

    # Final Chain Assembly
    core_chain = faq_checker_and_answerer | RunnableLambda(route)

    logger.info("Core chain built.")
    return core_chain

# --- API View for Asking Questions ---
@csrf_exempt
@require_POST
def ask_question_api(request):
    init_success, init_error = initialize_components()
    if not init_success:
        return JsonResponse({"error": f"Chatbot initialization failed: {init_error}", "error_type": "initialization_error"}, status=503)

    if request.content_type != 'application/json':
        return JsonResponse({"error": "Invalid content type.", "error_type": "invalid_content_type"}, status=400)
    try:
        data = json.loads(request.body)
        question = data.get('question')
        session_id = data.get('session_id')
        if not question or not isinstance(question, str) or not question.strip():
            return JsonResponse({"error": "Invalid question.", "error_type": "invalid_input"}, status=400)
        question = question.strip()
        if not session_id:
            session_id = str(uuid.uuid4()); logger.info(f"Generated new session_id: {session_id}")
        elif not isinstance(session_id, str) or not session_id.strip():
            return JsonResponse({"error": "Invalid session_id.", "error_type": "invalid_input"}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON.", "error_type": "invalid_json"}, status=400)

    logger.info(f"Processing request for session_id: {session_id}, Question: '{question[:100]}...'")

    try:
        core_chain = get_core_chain()
        chain_with_memory = RunnableWithMessageHistory(
            core_chain,
            get_session_history,
            input_messages_key="question",
            history_messages_key="history",
        )
        config = {"configurable": {"session_id": session_id}}

        result = chain_with_memory.invoke({"question": question}, config=config)

        if callable(getattr(result, 'invoke', None)):
             invoke_input = {
                 "question": question,
                 "history": get_session_history(session_id).messages # Get current history
             }             
             final_answer = result.invoke(invoke_input)
        else:
            final_answer = result # Assumed to be a string (e.g., from FAQ)

        logger.info(f"[{session_id}] Answer generated: '{str(final_answer)[:100]}...'")
        return JsonResponse({"question": question, "answer": str(final_answer), "session_id": session_id})

    # OpenAI API Error Handling (for Chat Model)
    except openai.RateLimitError as e:
        error_message = "Chatbot busy or quota limit reached. Try later."; logger.error(f"[{session_id}] OpenAI Quota Error: {e}"); return JsonResponse({"error": error_message, "error_type": "quota_exceeded"}, status=429)
    except openai.AuthenticationError as e:
        error_message = "Chatbot authentication failed (API Key issue)."; logger.error(f"[{session_id}] OpenAI Auth Error: {e}"); return JsonResponse({"error": error_message, "error_type": "authentication_error"}, status=401)
    except openai.PermissionDeniedError as e:
         error_message = "Chatbot permission issue with AI service."; logger.error(f"[{session_id}] OpenAI Permission Denied: {e}"); return JsonResponse({"error": error_message, "error_type": "permission_denied"}, status=403)
    except openai.APIConnectionError as e:
         error_message = "Could not connect to AI service."; logger.error(f"[{session_id}] OpenAI Connection Error: {e}"); return JsonResponse({"error": error_message, "error_type": "connection_error"}, status=504)
    except openai.APIError as e:
        error_message = f"AI service returned an error ({type(e).__name__})."; logger.error(f"[{session_id}] OpenAI API Error: {e}"); return JsonResponse({"error": error_message, "error_type": "openai_api_error"}, status=503)
    # General Error Handling
    except Exception as e:
        logger.exception(f"[{session_id}] An unexpected internal error occurred: {e}")
        return JsonResponse({"error": DEFAULT_ERROR_MESSAGE, "error_type": "internal_server_error"}, status=500)

# --- API View for Submitting Feedback ---
@csrf_exempt
@require_POST
def submit_feedback_api(request):
    if request.content_type != 'application/json':
        return JsonResponse({"error": "Invalid content type. Expected 'application/json'.", "error_type": "invalid_content_type"}, status=400)
    try:
        data = json.loads(request.body)
        question = data.get('question')
        response = data.get('response')
        rate_from_request = data.get('rate')
        comment = data.get('comment', '')

        required_fields = {'question': question, 'response': response, 'rate': rate_from_request}
        if not all(value is not None and (isinstance(value, str) and value.strip() or isinstance(value, int)) for value in required_fields.values()):
            return JsonResponse({"error": "Missing or invalid required fields: 'question', 'response', 'rate'.", "error_type": "invalid_input"}, status=400)

        try:
            rating_value = int(rate_from_request)
            if rating_value not in [1, -1]:
                raise ValueError("Rate value must be 1 or -1")
        except (ValueError, TypeError):
            return JsonResponse({"error": "Invalid 'rate' value received. Must be an integer: 1 (Positive) or -1 (Negative).", "error_type": "invalid_input"}, status=400)

        if comment is not None and not isinstance(comment, str):
            return JsonResponse({"error": "Invalid 'comment' value. Must be a string.", "error_type": "invalid_input"}, status=400)

        current_user = request.user if request.user.is_authenticated else None

        feedback_entry = Feedback.objects.create(
            question=question.strip(),
            response=response.strip(),
            rating=rating_value,
            user=current_user,
            comment=comment.strip() if comment else None
        )
        logger.info(f"Feedback saved: ID {feedback_entry.id}, Rating {rating_value}")
        return JsonResponse({"status": "success", "message": "Feedback received successfully."})

    except json.JSONDecodeError:
        logger.error("Invalid JSON received for feedback submission."); return JsonResponse({"error": "Invalid JSON format in request body.", "error_type": "invalid_json"}, status=400)
    except Exception as e:
        logger.exception(f"Error saving feedback to database: {e}")
        return JsonResponse({"error": "An internal error occurred while saving feedback.", "error_type": "internal_server_error"}, status=500)