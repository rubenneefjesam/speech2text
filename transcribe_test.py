import sys, os
import toml
from groq import Groq

# Secrets.toml in dezelfde map als .streamlit/secrets.toml
SECRETS_PATH = os.path.expanduser(".streamlit/secrets.toml")
if os.path.exists(SECRETS_PATH):
    data = toml.load(SECRETS_PATH)
    api_key = data.get("groq", {}).get("api_key", "").strip()
else:
    api_key = os.getenv("GROQ_API_KEY", "").strip()

assert api_key, "GROQ_API_KEY mist (export of in .streamlit/secrets.toml)"

client = Groq(api_key=api_key)

# Rest van je script…
