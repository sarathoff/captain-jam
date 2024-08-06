import streamlit as st
import tempfile
import os
from pydub import AudioSegment
import google.generativeai as genai
from dotenv import load_dotenv
from audio_recorder_streamlit import audio_recorder

load_dotenv()

# Configure Google API for audio summarization
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

def summarize_audio(audio_file_path):
    """analyse the speech audio using Google's Generative API."""
    model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
    audio_file = genai.upload_file(path=audio_file_path)
    response = model.generate_content(
        [
            "Please analyse the speech and give some tips to improve the speech",
            audio_file
        ]
    )
    return response.text

def save_audio_file(audio_bytes):
    """Save recorded audio bytes to a temporary file and return the path."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_file.write(audio_bytes)
            return tmp_file.name
    except Exception as e:
        st.error(f"Error handling recorded audio: {e}")
        return None

def start_chat_session():
    """Initialize chat session."""
    return genai.GenerativeModel('gemini-1.5-pro').start_chat(history=[])

# Configure Streamlit page settings
st.set_page_config(
    page_title="Captain Jam - Communication Coach",
    page_icon=":brain:",  # Favicon emoji
    layout="centered",  # Page layout option
)

# Initialize chat session if not already present
if "chat_session" not in st.session_state:
    st.session_state.chat_session = start_chat_session()

# Display the app title and description
st.title("Captain Jam")
st.write("""
    Record or upload an audio file to get a concise summary, then chat with Gemini-Pro about the summary.
""")

# Record audio
audio_bytes = audio_recorder(
    text="Click to record",
    recording_color="#e8b62c",
    neutral_color="#6aa36f",
    icon_size="3x",
    energy_threshold=(-1.0, 1.0),
    pause_threshold=60.0,
)

if audio_bytes:
    audio_path = save_audio_file(audio_bytes)
    st.audio(audio_path, format="audio/wav")

    if st.button('Analyse Recorded Audio'):
        with st.spinner('Analysizing...'):
            summary_text = summarize_audio(audio_path)
            st.info(summary_text)

            # Start chat with the summary
            if st.session_state.chat_session:
                st.session_state.chat_session.send_message(f"The summary report of speech analysis is: {summary_text}")

# Upload audio
uploaded_file = st.file_uploader("Upload Audio File", type=['wav', 'mp3'])
if uploaded_file is not None:
    audio_path = save_audio_file(uploaded_file.getvalue())  # Save the uploaded file and get the path
    st.audio(audio_path)

    if st.button('Analyse Uploaded Audio'):
        with st.spinner('Analyzing...'):
            summary_text = summarize_audio(audio_path)
            st.info(summary_text)

            # Start chat with the summary
            if st.session_state.chat_session:
                st.session_state.chat_session.send_message(f"The audio summary is: {summary_text}")

# Display the chat history
for message in st.session_state.chat_session.history:
    with st.chat_message("assistant" if message.role == "model" else "user"):
        st.markdown(message.parts[0].text)

# Input field for user's message
user_prompt = st.chat_input("Ask communication coach...")
if user_prompt:
    # Add user's message to chat and display it
    st.chat_message("user").markdown(user_prompt)

    # Send user's message to Gemini-Pro and get the response
    gemini_response = st.session_state.chat_session.send_message(user_prompt)

    # Display Gemini-Pro's response
    with st.chat_message("assistant"):
        st.markdown(gemini_response.text)
