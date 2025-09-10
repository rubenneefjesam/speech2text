#!/usr/bin/env python3
import os
import sys

try:
    import toml
except ImportError:
    print("❗️ Installeren eerst: pip install toml")
    sys.exit(1)

try:
    from groq import Groq
except ImportError:
    print("❗️ Installeren eerst: pip install groq")
    sys.exit(1)


def get_api_key():
    # 1) Probeer omgevingsvariabele
    key = os.getenv("GROQ_API_KEY", "").strip()
    if key:
        print("🔍 API key gevonden in env-var")
        return key

    # 2) Fallback: .streamlit/secrets.toml
    secrets_path = os.path.join(os.path.dirname(__file__), ".streamlit", "secrets.toml")
    if os.path.exists(secrets_path):
        data = toml.load(secrets_path)
        key = data.get("groq", {}).get("api_key", "").strip()
        if key:
            print(f"🔍 API key gevonden in {secrets_path}")
            return key

    # niet gevonden
    return None


def test_api(key):
    print("🧪 Initialiseren Groq-client…")
    client = Groq(api_key=key)

    print("📡 Testen models.list()…")
    try:
        resp = client.models.list()
        count = len(resp.data)
        print(f"✅ API werkt – {count} modellen beschikbaar")
        return True
    except Exception as e:
        print("❌ API-test mislukt:", e)
        return False


def main():
    key = get_api_key()
    if not key:
        print("🚨 Geen API key gevonden. Zet GROQ_API_KEY of vul `.streamlit/secrets.toml` in.")
        sys.exit(1)

    # dump repr om verborgen tekens te checken
    print("🔑 API_KEY (repr):", repr(key))

    ok = test_api(key)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
