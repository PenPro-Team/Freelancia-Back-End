import os
from dotenv import load_dotenv, find_dotenv
import openai
import sys

print("--- OpenAI API Key Test Script ---")

# محاولة إيجاد وتحميل ملف .env
# find_dotenv() يبحث في المجلد الحالي والمجلدات الأعلى
dotenv_path = find_dotenv()
if dotenv_path:
    print(f"Loading .env file from: {dotenv_path}")
    load_dotenv(dotenv_path)
else:
    print("WARNING: .env file not found. Relying on environment variables set elsewhere.")

# قراءة المفتاح من متغيرات البيئة
api_key = os.getenv("OPENAI_API_KEY")

# التحقق من وجود المفتاح
if not api_key:
    print("\nERROR: OPENAI_API_KEY not found in environment variables or .env file.")
    print("Please ensure:")
    print("  1. A .env file exists in the project root directory.")
    print(f"     (Project Root: {os.path.dirname(dotenv_path) if dotenv_path else 'Could not determine root'})")
    print("  2. The .env file contains the line: OPENAI_API_KEY=sk-xxxxxxxxxxxxx")
    print("  3. If not using .env, the environment variable is correctly set.")
    sys.exit(1) # الخروج من السكريبت لو المفتاح غير موجود

# طباعة جزء من المفتاح للتأكيد (آمن لأنه جزء صغير)
print(f"\nFound API Key starting with: {api_key[:8]} and ending with: {api_key[-4:]}")
print("(Please verify this matches the start/end of your NEW 'sk-...' key)")

print("\nAttempting to connect to OpenAI API and list models...")

try:
    # تهيئة عميل OpenAI بالمفتاح
    # استخدم الكلاس الجديد openai.OpenAI()
    client = openai.OpenAI(api_key=api_key)

    # إجراء استدعاء API بسيط لاختبار المفتاح (مثل قائمة الموديلات)
    models = client.models.list()

    # إذا نجح الاستدعاء، اطبع رسالة نجاح
    print("\n-----------------------------------------")
    print("SUCCESS! Successfully connected to OpenAI API.")
    print(f"Retrieved {len(models.data)} models.")
    print("Your API Key loaded by this script is VALID and working.")
    print("-----------------------------------------")

except openai.AuthenticationError as e:
    # خطأ محدد للمفتاح غير الصحيح (401)
    print("\n-----------------------------------------")
    print("ERROR: Authentication Failed (Invalid API Key).")
    print("OpenAI rejected the API key provided to this script.")
    print(f"Details from OpenAI: {e}")
    print("\nTroubleshooting:")
    print("  - Double-check the API key in your .env file is EXACTLY correct.")
    print("  - Ensure the key hasn't been deleted from your OpenAI account.")
    print("  - Make sure you copied the SECRET key (usually starts 'sk-'), not an ID.")
    print("  - Verify billing/payment method is set up correctly on OpenAI if needed.")
    print("-----------------------------------------")

except openai.RateLimitError as e:
    # خطأ محدد لمشاكل الكوتا (429)
    print("\n-----------------------------------------")
    print("ERROR: Rate Limit or Quota Exceeded.")
    print("Your OpenAI account associated with this key has issues (quota, limits, etc.).")
    print(f"Details from OpenAI: {e}")
    print("\nPlease check your usage and billing details at https://platform.openai.com/")
    print("-----------------------------------------")

except openai.APIConnectionError as e:
    # خطأ لمشاكل الاتصال بالشبكة
    print("\n-----------------------------------------")
    print("ERROR: Could not connect to OpenAI API.")
    print("Check your internet connection and OpenAI service status.")
    print(f"Details: {e}")
    print("-----------------------------------------")

except Exception as e:
    # التقاط أي أخطاء أخرى غير متوقعة
    print("\n-----------------------------------------")
    print(f"An unexpected error occurred: {e}")
    print(f"Error type: {type(e).__name__}")
    print("-----------------------------------------")

print("\n--- Test Script Finished ---")