import os
import yt_dlp
import whisper
from openai import OpenAI
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs
import streamlit as st
from streamlit_chat import message  # Import the message component

# Load API key from .env file
load_dotenv()
api_key = os.getenv("openai_api_key")
client = OpenAI(api_key=api_key)

# Helper function to clean the YouTube URL and get the base URL
def clean_youtube_url(url):
    parsed_url = urlparse(url)
    video_id = parse_qs(parsed_url.query).get("v")

    if video_id:
        return f"https://www.youtube.com/watch?v={video_id[0]}"
    elif "youtu.be" in parsed_url.netloc:
        video_id = parsed_url.path.lstrip("/")
        return f"https://www.youtube.com/watch?v={video_id}"

    return url

def download_youtube_video(url, output_path="audio"):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if os.path.exists(output_path):
            return output_path
        if os.path.exists(output_path + ".mp3"):
            return output_path + ".mp3"

        print("Audio file was not created correctly.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Transcribe the audio using Whisper
def transcribe_audio(audio_path):
    if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
        raise ValueError(f"Audio file {audio_path} is not valid.")

    model = whisper.load_model("base")
    result = model.transcribe(audio_path, fp16=False)
    return result["text"]

# Function to get a response from gpt-3.5-turbo
def get_gpt_response(transcript, question):
    prompt = f"The following is a transcript of a YouTube video:\n\n{transcript}\n\nBased on this transcript, answer the following question:\n{question}\n\nAnswer:"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()

# Function to process the message
def process_message():
    user_input = st.session_state.user_input  # Access the user's input
    if user_input and st.session_state.transcript:  # Only process if there's input and a valid transcript
        answer = get_gpt_response(st.session_state.transcript, user_input)
        st.session_state.history.append({"question": user_input, "answer": answer})  # Save question-answer pair

        # Clear input by setting session state back to empty string
        st.session_state.user_input = ""

# Main Streamlit app
def main():
    st.title("YouTube Video Chatbot")

    # Ensure history and transcript are in session state
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'transcript' not in st.session_state:
        st.session_state.transcript = ""

    youtube_url = st.text_input("Enter YouTube video URL:")

    if st.button("Start Chat"):
        clean_url = clean_youtube_url(youtube_url)
        audio_file = download_youtube_video(clean_url)

        if audio_file:
            st.success(f"Audio file downloaded: {audio_file}")
            transcript = transcribe_audio(audio_file)
            st.session_state.transcript = transcript  # Save transcript to session state
            st.session_state.history = []  # Clear previous chat history
            st.success("Transcript loaded. You can now ask questions.")
        else:
            st.error("Failed to download or process the video.")

    if 'transcript' in st.session_state and st.session_state.transcript:
        # Display chat history with unique keys
        for i, chat in enumerate(st.session_state.history):
            message(chat["question"], is_user=True, key=f"user_{i}")  # User message
            message(chat["answer"], is_user=False, key=f"ai_{i}")   # AI message

        # Input box for typing a message at the bottom with callback
        st.text_input("Type a message:", key="user_input", on_change=process_message)

if __name__ == "__main__":
    main()
