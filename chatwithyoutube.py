import os
import boto3
from googleapiclient.discovery import build
from dotenv import load_dotenv
import streamlit as st
from streamlit_chat import message
import requests
# Load API keys and AWS credentials from .env file
load_dotenv("EnvVars.txt")
youtube_api_key = os.getenv("youtube_api_key")
aws_access_key = os.getenv("aws_access_key")
aws_secret_key = os.getenv("aws_secret_key")
aws_region = os.getenv("aws_region")

# Initialize AWS clients for Transcribe and Bedrock
transcribe_client = boto3.client('transcribe', 
                                 aws_access_key_id=aws_access_key, 
                                 aws_secret_access_key=aws_secret_key, 
                                 region_name=aws_region)

bedrock_client = boto3.client("bedrock-runtime", region_name="ap-south-1")
from botocore.exceptions import ClientError


# Function to get video transcript using AWS Transcribe (for audio-based input)
def transcribe_video(video_url, transcription_job_name):
    transcribe_client.start_transcription_job(
        TranscriptionJobName=transcription_job_name,
        Media={'MediaFileUri': video_url},
        MediaFormat='mp4',
        LanguageCode='en-US'
    )
    
    while True:
        status = transcribe_client.get_transcription_job(TranscriptionJobName=transcription_job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
    if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
        transcript_url = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
        response = requests.get(transcript_url)
        return response.json()['results']['transcripts'][0]['transcript']
    else:
        return None

# Function to get video details using the YouTube Data API
def get_video_details(video_id):
    youtube = build('youtube', 'v3', developerKey=youtube_api_key)
    request = youtube.videos().list(part='snippet', id=video_id)
    response = request.execute()
    return response['items'][0]['snippet'] if response['items'] else None
def extract_video_id(youtube_url):
    if 'youtu.be/' in youtube_url:  # Shortened YouTube URL
        return youtube_url.split('/')[-1].split('?')[0]  # Extract video ID after '/'
    elif 'v=' in youtube_url:  # Standard YouTube URL
        return youtube_url.split('v=')[-1].split('&')[0]  # Extract video ID after 'v='
    else:
        return None
# Function to get a response from AWS Bedrock (similar to GPT)
import json

# Function to get a response from AWS Bedrock (Mistral Model)
def get_bedrock_response(transcript, question):
    # Define the model ID for the Bedrock model (Mistral in this case)
    model_id = "mistral.mistral-large-2402-v1:0"

    # Define the prompt
    prompt = f"The following is a transcript of a YouTube video:\n\n{transcript}\n\nBased on this transcript, answer the following question:\n{question}\n\nAnswer:"

    # Format the request for the Mistral model (or another model)
    formatted_prompt = f"<s>[INST] {prompt} [/INST]"
    native_request = {
        "prompt": formatted_prompt,
        "max_tokens": 512,
        "temperature": 0.5,
    }

    # Convert the request to JSON
    request_payload = json.dumps(native_request)

    try:
        # Invoke the Bedrock model
        response = bedrock_client.invoke_model(modelId=model_id, body=request_payload)

        # Decode the response body
        model_response = json.loads(response["body"].read())
        response_text = model_response["outputs"][0]["text"]

        return response_text.strip()

    except (ClientError, Exception) as e:
        return f"Error processing query: {e}"

# Function to process the message
def process_message():
    user_input = st.session_state.user_input  # Access the user's input
    if user_input and st.session_state.transcript:  # Only process if there's input and a valid transcript
        answer = get_bedrock_response(st.session_state.transcript, user_input)
        st.session_state.history.append({"question": user_input, "answer": answer})  # Save question-answer pair
        
        # Clear input by setting session state back to empty string
        st.session_state.user_input = ""

import streamlit as st

# Main Streamlit app
def main():
    st.title("YouTube Video Chatbot (AWS Powered)")

    # Ensure history and transcript are in session state
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'transcript' not in st.session_state:
        st.session_state.transcript = ""
    if 'last_url' not in st.session_state:  # Track the last URL entered
        st.session_state.last_url = ""

    youtube_url = st.text_input("Enter YouTube video URL:")

    if st.button("Start Chat"):
        # Check if the new URL is different from the previous one
        if youtube_url != st.session_state.last_url:
            # Reset session state for new URL
            st.session_state.history = []  # Clear chat history
            st.session_state.transcript = ""  # Clear transcript
            st.session_state.last_url = youtube_url  # Update the last URL

        # Extract video ID from the YouTube URL
        video_id = extract_video_id(youtube_url)
        
        if video_id:
            # Get video details using YouTube Data API
            video_details = get_video_details(video_id)
            if video_details:
                title = video_details['title']
                description = video_details['description']
                transcript = f"Title: {title}\n\nDescription: {description}"  # Simple transcript creation
                st.session_state.transcript = transcript  # Save transcript to session state
                st.success("Transcript loaded. You can now ask questions.")
            else:
                st.error("Failed to retrieve video details.")
        else:
            st.error("Invalid YouTube URL. Please try again.")

    if 'transcript' in st.session_state and st.session_state.transcript:
        # Display chat history
        for index, chat in enumerate(st.session_state.history):  # Use enumerate to get index and chat dictionary
            if isinstance(chat, dict):  # Ensure each item in history is a dictionary
                message(chat["question"], is_user=True, key=f"user_{index}")  # Unique key for user messages
                message(chat["answer"], is_user=False, key=f"bot_{index}")    # Unique key for bot messages

        # Input box for typing a message at the bottom with callback
        st.text_input("Type a message:", key="user_input", on_change=process_message)

if __name__ == "__main__":
    main()