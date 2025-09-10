import sys, os
from groq import Groq

if len(sys.argv) != 2:
    print("Usage: python transcribe_test.py <audio_file.mp3|wav|m4a>")
    sys.exit(1)

api_key = os.getenv("GROQ_API_KEY")
assert api_key, "GROQ_API_KEY mist (export of .secrets)"

client = Groq(api_key=api_key)

fname = sys.argv[1]
with open(fname, "rb") as f:
    res = client.audio.transcriptions.create(
        model="whisper-large-v3",             # of whisper-large-v3-turbo
        file=(os.path.basename(fname), f.read())
    )

print("OK ✅ Transcript:")
print(res.text)
