# test_groq.py

import os
from groq import Groq

print("🔑 Initialising Groq client…")
client = Groq(api_key=os.environ["GROQ_API_KEY"])
print("✅ Client initialized")

print("💬 Sending a test chat message…")
resp = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": "Hallo Groq! Antwoord met één woord."}]
)

print("📥 Response:")
print(resp.choices[0].message.content)
print("🎉 Done")
