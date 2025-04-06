import os
import logging
from dotenv import load_dotenv
from operator import itemgetter
import json
import uuid
import openai

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Feedback

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableBranch, RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

load_dotenv()
logger = logging.getLogger(__name__)

VECTOR_STORE_PATH = "faiss_vector_store"
LLM_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
DEFAULT_ERROR_MESSAGE = "Sorry, I encountered an issue and couldn't process your request. Please try again later."

vectorstore = None
retriever = None
llm = None
embeddings_model = None
initialization_error = None
checked_openai_api_key = None

message_histories = {}

def get_session_history(session_id: str) -> ChatMessageHistory:
    if session_id not in message_histories:
        message_histories[session_id] = ChatMessageHistory()
    return message_histories[session_id]

def initialize_components():
    global vectorstore, retriever, llm, embeddings_model, initialization_error, checked_openai_api_key

    if llm and embeddings_model and (retriever or not os.path.exists(VECTOR_STORE_PATH)):
        return True, None
    if initialization_error:
        return False, initialization_error

    logger.info("Initializing base LangChain components...")

    if checked_openai_api_key is None:
        api_key_from_env = os.getenv("OPENAI_API_KEY")
        if not api_key_from_env:
            error_msg = "OpenAI API Key not found in environment variables."
            logger.critical(error_msg); initialization_error = error_msg; return False, error_msg
        if not api_key_from_env.startswith("sk-"):
             logger.warning(f"Loaded OpenAI key format warning. Key ends in ...{api_key_from_env[-4:]}")
        logger.info(f"OpenAI API Key loaded (ends in ...{api_key_from_env[-4:]}).")
        checked_openai_api_key = api_key_from_env
    else:
         logger.debug("Using previously checked OpenAI API Key.")

    try:
        if not llm:
            llm = ChatOpenAI(
                model_name=LLM_MODEL_NAME, temperature=0.7,
                api_key=checked_openai_api_key, max_retries=2,
            )
            logger.info("ChatOpenAI model initialized.")

        if not embeddings_model:
            embeddings_model = OpenAIEmbeddings(api_key=checked_openai_api_key)
            logger.info("OpenAI Embeddings model initialized.")

        if retriever is None and os.path.exists(VECTOR_STORE_PATH):
            vectorstore = FAISS.load_local(
                VECTOR_STORE_PATH, embeddings_model, allow_dangerous_deserialization=True
            )
            retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={'k': 3})
            logger.info("FAISS index and retriever loaded successfully.")
        elif not os.path.exists(VECTOR_STORE_PATH):
             logger.warning(f"FAISS index not found: {VECTOR_STORE_PATH}. RAG unavailable.")
             retriever = None

        initialization_error = None
        logger.info("Base component initialization successful.")
        return True, None

    except openai.AuthenticationError as auth_err:
         error_msg = f"OpenAI Auth Error during initialization: {auth_err}"
         logger.critical(error_msg); initialization_error = error_msg
         llm = None; embeddings_model = None; retriever = None; return False, error_msg
    except openai.RateLimitError as rate_err:
        error_msg = f"OpenAI Quota/Rate Limit Error during initialization: {rate_err}"
        logger.critical(error_msg); initialization_error = error_msg
        llm = None; embeddings_model = None; retriever = None; return False, error_msg
    except openai.APIConnectionError as conn_err:
        error_msg = f"OpenAI Connection Error during initialization: {conn_err}"
        logger.critical(error_msg); initialization_error = error_msg
        llm = None; embeddings_model = None; retriever = None; return False, error_msg
    except ImportError as ie:
        error_msg = f"Import error during initialization: {ie}."
        logger.critical(error_msg, exc_info=True); initialization_error = error_msg; return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error during component initialization: {e}"
        logger.critical(error_msg, exc_info=True); initialization_error = error_msg
        llm = None; embeddings_model = None; retriever = None; return False, error_msg


def get_core_chain():
    if not llm:
         raise Exception("Core LLM component is not ready.")

    logger.debug("Building core chain logic with refined FAQ handling...")
    FAQS = {
        "create_job": {
            "keywords": [
                "create job","create a job","post a job", "post job", "add project","make a project","make project", "new listing", "client post",
                "how do i post", "how to post a job", "steps to create job", "job posting instructions",
                "publish job", "list a project", "need to hire", "want to post work",
                "where to post job", "make job listing", "hiring process start",
                "انشاء وظيفة", "اضافة وظيفة", "نشر وظيفة", "اضافة مشروع", "اضافه مشروع",
                "كيف انشر وظيفة", "كيف اضيف وظيفة", "خطوات نشر وظيفة", "طريقة نشر عمل",
                "اعلان عن وظيفة", "عاوز اضيف شغل", "اريد نشر مشروع", "مكان نشر الوظائف",
                "عميل جديد نشر", "حساب عميل كيف انشر"
            ],
            "answer": "To create a job posting on Freelancia as a client:\n1. Log in to your client account.\n2. Navigate to the 'Post a Job' section (usually found in your dashboard).\n3. Fill out the job details form accurately (Title, detailed Description, required Skills, Budget - fixed or hourly, estimated Duration).\n4. Review your posting and click 'Submit' or 'Post Job'.",
            "topic": "faq_create_job"
        },
        "how_to_bid": {
            "keywords": [
                "how to bid", "submit proposal", "apply for job", "freelancer apply", "find work",
                "how do i apply", "steps to bid", "proposal submission", "bidding process",
                "applying for projects", "get hired", "where to apply", "send offer",
                "make a bid", "job application", "freelancer job search",
                "كيف اقدم عرض", "كيف اقدم على وظيفة", "تقديم عرض", "ارسال عرض سعر", "التقديم على وظيفة",
                "التقديم على مشروع", "طريقة التقديم", "خطوات ارسال العرض", "البحث عن عمل",
                "كيف الاقي شغل", "فريلانسر كيف اقدم", "تقديم مقترح", "عايز اشتغل", "التقديم للوظائف"
            ],
            "answer": "As a freelancer on Freelancia, to bid on a job (submit a proposal):\n1. Make sure your profile is complete and up-to-date.\n2. Browse the available job listings using search or categories.\n3. Click on a job title to view its full details and requirements.\n4. If you're a good fit, click the 'Submit Proposal' or 'Bid Now' button.\n5. Write a compelling proposal tailored to the job, highlighting your relevant skills and experience.\n6. Enter your bid amount (fixed price or hourly rate as requested) and estimated time to complete the project.\n7. Submit your proposal. Good luck!",
            "topic": "faq_how_to_bid"
        },
        "what_is_freelancia": {
             "keywords": [
                 "what is freelancia", "about this site", "about this platform", "purpose of this website",
                 "explain freelancia", "tell me about freelancia", "freelancia definition", "how freelancia works",
                 "site info", "platform overview", "what do you do",
                 "ما هو فريلانسيا", "ما هي منصة فريلانسيا", "عن الموقع", "عن المنصة", "ما هذا الموقع",
                 "معلومات عن فريلانسيا", "شرح فريلانسيا", "هدف الموقع", "كيف تعمل فريلانسيا",
                 "ايش هو فريلانسيا", "نبذة عن فريلانسيا"
            ],
             "answer": "Freelancia is an online freelance marketplace designed to connect clients who need projects completed with talented freelancers from around the world who have the skills to do the work. Clients can post jobs detailing their requirements, and freelancers can browse these jobs and submit proposals (bids) to get hired.",
             "topic": "faq_what_is_freelancia"
        }
    }

    def check_faq(input_dict):
        question = input_dict.get("question", "").lower()
        for faq_key, faq_data in FAQS.items():
            if any(keyword in question for keyword in faq_data["keywords"]):
                logger.info(f"FAQ detected: {faq_data['topic']}")
                return {"topic": faq_data["topic"], "answer": faq_data["answer"]}
        logger.debug("No FAQ keyword matched.")
        return input_dict

    faq_checker_and_answerer = RunnableLambda(check_faq)

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

    def classify_if_not_faq(input_dict_with_maybe_topic):
        if "faq" in input_dict_with_maybe_topic.get("topic", ""):
            return input_dict_with_maybe_topic
        else:
            classification = question_classifier.invoke(input_dict_with_maybe_topic)
            logger.info(f"Classifier result: {classification}")
            return {**input_dict_with_maybe_topic, "topic": classification.lower()}

    classifier_logic = RunnableLambda(classify_if_not_faq)

    def format_docs(docs): return "\n\n".join(doc.page_content for doc in docs)
    rag_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an AI assistant for Freelancia (freelancia.com). Answer based *only* on provided Freelancia Context and History. If info is missing, state that clearly. Do *not* use external knowledge. Refer to the platform as Freelancia."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "Context:\n{context}\n\nQuestion: {question}"),
    ])

    def safe_retriever_invoke(input_dict):
        question = input_dict.get("question", "")
        if not retriever: return "Context unavailable."
        try:
            docs = retriever.invoke(question)
            return format_docs(docs) if docs else "No relevant context found in Freelancia data."
        except openai.APIError as api_err: raise api_err
        except Exception as e: logger.exception(f"RAG retriever error: {e}"); return "Error retrieving context."

    rag_chain_logic = (
        RunnablePassthrough.assign(context=RunnableLambda(safe_retriever_invoke))
        | rag_prompt | llm | StrOutputParser()
    )

    general_prompt = ChatPromptTemplate.from_messages([
         ("system", "You are a helpful AI assistant for Freelancia (freelancia.com). Use chat history for context. Answer general questions and engage naturally. Refer to the platform as Freelancia."),
         MessagesPlaceholder(variable_name="history"),
         ("human", "{question}"),
     ])
    general_chain_logic = (general_prompt | llm | StrOutputParser())

    def route(info):
        if "answer" in info and "faq" in info.get("topic",""):
            logger.debug("Routing to: FAQ Answer")
            return RunnableLambda(lambda x: x["answer"])
        else:
            logger.debug("Routing based on classification...")
            classification_result = question_classifier.invoke(info).lower()
            logger.info(f"Classification for routing: {classification_result}")
            if "specific" in classification_result:
                logger.debug("Routing to: RAG Chain")
                return rag_chain_logic
            else:
                logger.debug("Routing to: General Chain")
                return general_chain_logic

    core_chain = faq_checker_and_answerer | RunnableLambda(route)
    logger.info("Core chain built.")
    return core_chain


@csrf_exempt
@require_POST
def ask_question_api(request):
    init_success, init_error = initialize_components()
    if not init_success:
        return JsonResponse({"error": f"Initialization failed: {init_error}", "error_type": "initialization_error"}, status=503)

    if request.content_type != 'application/json':
        return JsonResponse({"error": "Invalid content type.", "error_type": "invalid_content_type"}, status=400)

    try:
        data = json.loads(request.body)
        question = data.get('question')
        session_id = data.get('session_id')
        if not question or not isinstance(question, str) or not question.strip():
            return JsonResponse({"error": "Invalid question provided.", "error_type": "invalid_input"}, status=400)
        question = question.strip()
        if not session_id:
            session_id = str(uuid.uuid4())
            logger.info(f"Generated new session_id: {session_id}")
        elif not isinstance(session_id, str) or not session_id.strip():
            return JsonResponse({"error": "Invalid session_id provided.", "error_type": "invalid_input"}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format in request body.", "error_type": "invalid_json"}, status=400)

    logger.info(f"Processing request for session_id: {session_id}, Question: '{question[:100]}...'")

    try:
        core_chain = get_core_chain()
        chain_with_memory = RunnableWithMessageHistory(
            core_chain, get_session_history,
            input_messages_key="question", history_messages_key="history",
        )
        config = {"configurable": {"session_id": session_id}}
        answer = chain_with_memory.invoke({"question": question}, config=config)
        logger.info(f"[{session_id}] Answer generated: '{answer[:100]}...'")
        return JsonResponse({"question": question, "answer": answer, "session_id": session_id})

    except openai.RateLimitError as e:
        error_message = "Chatbot is temporarily unavailable due to high demand or API quota limits. Please check the OpenAI plan or try again later."; logger.error(f"[{session_id}] OpenAI Quota Exceeded: {e}"); return JsonResponse({"error": error_message, "error_type": "quota_exceeded"}, status=429)
    except openai.PermissionDeniedError as e:
         error_message = "Chatbot encountered a permission issue with the AI service (e.g., model access denied). Please check API key permissions."; logger.error(f"[{session_id}] OpenAI Permission Denied: {e}"); return JsonResponse({"error": error_message, "error_type": "permission_denied"}, status=403)
    except openai.AuthenticationError as e:
        error_message = "Chatbot authentication failed. Please ensure the OpenAI API Key is valid and active."; logger.error(f"[{session_id}] OpenAI Authentication Error: {e}"); return JsonResponse({"error": error_message, "error_type": "authentication_error"}, status=401)
    except openai.APIConnectionError as e:
         error_message = "Could not connect to the AI service. Please check network connectivity."; logger.error(f"[{session_id}] OpenAI Connection Error: {e}"); return JsonResponse({"error": error_message, "error_type": "connection_error"}, status=504)
    except openai.APIError as e:
        error_message = f"The AI service returned an error ({type(e).__name__}). Please try again later."; logger.error(f"[{session_id}] OpenAI API Error: {e}"); return JsonResponse({"error": error_message, "error_type": "openai_api_error"}, status=503)
    except Exception as e:
        logger.exception(f"[{session_id}] An unexpected internal error occurred: {e}"); return JsonResponse({"error": DEFAULT_ERROR_MESSAGE, "error_type": "internal_server_error"}, status=500)


@csrf_exempt
@require_POST
def submit_feedback_api(request):
    if request.content_type != 'application/json':
        return JsonResponse({"error": "Invalid content type. Expected 'application/json'.", "error_type": "invalid_content_type"}, status=400)
    try:
        data = json.loads(request.body)
        question = data.get('question'); response = data.get('response'); rating = data.get('rating'); comment = data.get('comment', '')
        required_fields = {'question': question, 'response': response, 'rating': rating}
        if not all(value is not None and (isinstance(value, str) and value.strip() or isinstance(value, int)) for value in required_fields.values()):
             return JsonResponse({"error": "Missing or invalid required fields: 'question', 'response', 'rating'.", "error_type": "invalid_input"}, status=400)
        try:
            rating = int(rating)
            if rating not in [1, -1]: raise ValueError("Rating must be 1 or -1")
        except (ValueError, TypeError):
            return JsonResponse({"error": "Invalid 'rating' value. Must be an integer: 1 (Positive) or -1 (Negative).", "error_type": "invalid_input"}, status=400)
        if comment is not None and not isinstance(comment, str):
             return JsonResponse({"error": "Invalid 'comment' value. Must be a string.", "error_type": "invalid_input"}, status=400)

        current_user = request.user if request.user.is_authenticated else None
        feedback_entry = Feedback.objects.create(question=question.strip(), response=response.strip(), rating=rating, user=current_user, comment=comment.strip() if comment else None)
        logger.info(f"Feedback saved: ID {feedback_entry.id}, Rating {rating}")
        return JsonResponse({"status": "success", "message": "Feedback received successfully."})
    except json.JSONDecodeError:
        logger.error("Invalid JSON received for feedback submission."); return JsonResponse({"error": "Invalid JSON format in request body.", "error_type": "invalid_json"}, status=400)
    except Exception as e:
        logger.exception(f"Error saving feedback to database: {e}"); return JsonResponse({"error": "An internal error occurred while saving feedback.", "error_type": "internal_server_error"}, status=500)