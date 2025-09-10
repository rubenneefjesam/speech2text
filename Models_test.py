# kort scriptje modelstest.py
import os
from groq import Groq

key = os.getenv("GROQ_API_KEY", "")
print(f"API_KEY repr: {key!r}")     # toont ook onzichtbare karakters
client = Groq(api_key=key)
models = client.models.list()
print("✅ models.list() werkte, aantal modellen:", len(models.data))