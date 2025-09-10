print("Start script")
from groq import Groq
import os

# Haal je key uit de environment variabele
client = Groq(api_key=os.environ["GROQ_API_KEY"])
print("Client initialized")

# Maak een simpele chat completion
resp = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": "Hallo Groq! Antwoord met één woord."}]
)

print("Response:")
print(resp.choices[0].message["content"])
print("Done")
