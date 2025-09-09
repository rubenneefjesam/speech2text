import streamlit as st

st.title("Speech-to-Text Demo")
st.write("Upload een audiobestand en krijg de transcriptie terug.")

audio_file = st.file_uploader("Upload audio", type=["wav", "mp3", "m4a"])

if audio_file:
    st.audio(audio_file)
    # Hier zou de API-call komen, bv. naar OpenAI Whisper
    transcript = "Dit is een test transcriptie van jouw audio."
    st.success(transcript)
