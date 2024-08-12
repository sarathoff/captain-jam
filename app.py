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

def analyse_audio(audio_file_path):
    """Analyze the speech audio using Google's Generative API."""
    model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
    audio_file = genai.upload_file(path=audio_file_path)
    response = model.generate_content(
        [
            "You are an advanced English communication coach utilizing the JAM (Just A Minute) technique. Analyze the user's one-minute speech recording focusing on clarity, coherence, articulation, pronunciation, pace, timing, engagement, and expression. Identify mistakes in the speech and provide constructive feedback on how to improve. Offer specific suggestions for each identified mistake and actionable tips for enhancing the speech. Encourage the user with positive reinforcement and practical advice for their continuous improvement. and give a table for statistical data about speech by analysing using test",
            audio_file
        ]
    )
    return response.text

def summarize_audio(audio_file_path):
    """Summarize the audio using Google's Generative API."""
    model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
    audio_file = genai.upload_file(path=audio_file_path)
    with st.spinner('Summarizing audio...'):
        response = model.generate_content(
            [
                "Please summarize the speech and highlight the main plot or ideas covered. Include brief notes on vocabulary suggestions to enhance future speeches.",
                audio_file
            ]
        )
    return response.text

def save_audio_file(audio_bytes):
    """Save recorded audio bytes to a temporary file and return the path."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_file_path = tmp_file.name
            return tmp_file_path
    except Exception as e:
        st.error(f"Error handling recorded audio: {e}")
        return None

def get_today_topic():
    """Generate a topic for Just a Minute practice using Gemini API."""
    model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
    response = model.generate_content(
        ["give me one topic for me to speak for one minute , like this examples  which is your favourite mode of transport and why , which is your favourite habit and why/, who is your best best friend and why, what is your opinion about AI impact on education"]
    )
    return response.text

def start_chat_session():
    """Initialize a new chat session."""
    return genai.GenerativeModel('gemini-1.5-pro').start_chat(history=[])

# Configure Streamlit page settings
st.set_page_config(
    page_title="Captain Jam - Communication Coach",
    page_icon=":brain:",
    layout="centered",
)

# Inject custom CSS to apply Poppins font and style containers
streamlit_style = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Poppins', sans-serif;
    }
    </style>
    """
st.markdown(streamlit_style, unsafe_allow_html=True)

# Initialize topic and reports if not already present
if "today_topic" not in st.session_state:
    st.session_state.today_topic = ""
if "analysis_report" not in st.session_state:
    st.session_state.analysis_report = ""
if "summary" not in st.session_state:
    st.session_state.summary = ""

# Initialize chat session if not already present
if "chat_session" not in st.session_state:
    st.session_state.chat_session = start_chat_session()

# Display the app title and description
st.title("Captain Jam - English Communication Coach🎙️")
st.write("""
    Your Co-captain to Supercharge Your English and Communication 🚀 - Speak. Learn. Grow. 🌟 Improve your high-demand communication skills every day for one minute - grow by compound effect 📈
""")
st.write("Speak. Record. Improve.")

st.write("1. Click Generate Topic to get a new JAM speech topic or use the same one 🔄.")
st.write("2. Record your speech for 1 minute; it stops automatically ⏳.")
st.write("3. Speak continuously, with breaks no longer than 3 seconds ⏱️")
st.write("4. For another way, you can upload an audio file 📂.")
st.write("5. Start speaking and grow today! 🌱🎯")

# Button to generate or refresh topic
if st.button('Generate New Topic'):
    with st.spinner('Generating topic...'):
        st.session_state.today_topic = get_today_topic()

# Display the topic for Just a Minute practice
if st.session_state.today_topic:
    st.write(st.session_state.today_topic)
else:
    st.write("Click the button above to generate a topic.")

# Record audio
audio_bytes = audio_recorder(
    text="Click to record ",
    recording_color="#e8b62c",
    neutral_color="#6aa36f",
    icon_size="3x",
    energy_threshold=(-1.0, 1.0),
    pause_threshold=70.0,
)
if audio_bytes:
    audio_path = save_audio_file(audio_bytes)
    if audio_path and os.path.exists(audio_path):
        st.audio(audio_path, format="audio/wav")
    else:
        st.error("Audio file could not be saved or accessed.")

    if st.button('Analyse Recorded Audio'):
        with st.spinner('Analyzing and Summarizing...'):
            st.session_state.analysis_report = analyse_audio(audio_path)
            st.session_state.summary = summarize_audio(audio_path)
            
            # Show the analysis report
            st.info("### Analysis Report")
            st.write(st.session_state.analysis_report)
            
            # Show the summary
            st.info("### Summary")
            st.write(st.session_state.summary)

            # Reset chat session for new analysis
            st.session_state.chat_session = start_chat_session()

# Upload audio
uploaded_file = st.file_uploader("Upload Audio File", type=['wav', 'mp3', 'mpeg'])
if uploaded_file is not None:
    audio_path = save_audio_file(uploaded_file.getvalue())
    st.audio(audio_path)

    if st.button('Analyse Uploaded Audio'):
        with st.spinner('Analyzing and Summarizing...'):
            st.session_state.analysis_report = analyse_audio(audio_path)
            st.session_state.summary = summarize_audio(audio_path)
            
            # Show the analysis report
            st.info("### Analysis Report")
            st.write(st.session_state.analysis_report)
            
            # Show the summary
            st.info("### Summary")
            st.write(st.session_state.summary)

            # Reset chat session for new analysis
            st.session_state.chat_session = start_chat_session()

# Display the chat history
if "chat_session" in st.session_state:
    for message in st.session_state.chat_session.history:
        with st.chat_message("assistant" if message.role == "model" else "user"):
            st.markdown(message.parts[0].text)

# Input field for user's message
user_prompt = st.chat_input("Ask your Communication Coach...")
if user_prompt:
    # Add user's message to chat and display it
    st.chat_message("user").markdown(user_prompt)

    # Prepare the context for the chatbot based on the reports
    context = f"Analysis Report: {st.session_state.analysis_report}\n\nSummary: {st.session_state.summary}\n\nUser's Question: {user_prompt}"
    
    # Send user's message with context to Gemini-Pro and get the response
    gemini_response = st.session_state.chat_session.send_message(context)

    # Display Gemini-Pro's response
    with st.chat_message("assistant"):
        st.markdown(gemini_response.text)
