## ChatWithYouTubeURLs

## YouTube Video Chatbot (AWS Powered)

This project is a chatbot built using Streamlit, AWS services (Transcribe, Bedrock), and the YouTube Data API. It allows users to input a YouTube video URL, extract basic information about the video, and interact with it by asking questions related to the video transcript. The chatbot provides responses powered by AWS Bedrock (Mistral model).

## Features

- Accepts YouTube video URLs and extracts video details.
- Uses AWS Transcribe to process the video for audio-based transcriptions.
- Interacts with AWS Bedrock (Mistral model) to answer user questions based on video content.
- Built with Streamlit for a simple web-based interface.

## Prerequisites

1. **AWS Account**: Ensure you have an active AWS account with access to Transcribe and Bedrock services.
2. **YouTube API Key**: You need to have access to the YouTube Data API for fetching video details.
3. **AWS Credentials**: Access key and secret key for AWS services.
4. **Python Environment**: Ensure Python 3.8+ is installed along with the following libraries.

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/SAIRAMREDDY25/chatwithyoutube.git
cd chatwithyoutube
```

### Step 2: Install Dependencies

```bash
pip install streamlit boto3 google-api-python-client requests python-dotenv
```

### Step 3: Set Up Environment Variables

Create an `EnvVars.txt` file in the project root with your API keys and AWS credentials:

```txt
youtube_api_key=YOUR_YOUTUBE_API_KEY
aws_access_key=YOUR_AWS_ACCESS_KEY
aws_secret_key=YOUR_AWS_SECRET_KEY
aws_region=YOUR_AWS_REGION
```

### Step 4: Run the Application

```bash
streamlit run chatwithyoutube.py
```

## How It Works

1. **YouTube URL Input**: Enter a YouTube video URL in the provided text box.
2. **Transcript and Interaction**:
    - The application fetches video details (title, description) and prepares a simple transcript.
    - Users can interact by asking questions related to the transcript, and the chatbot will respond using the Mistral model from AWS Bedrock.
3. **Real-time Chat**: The application maintains a chat history, displaying user questions and corresponding bot responses.

## Accessing YouTube on AWS

When running this application locally, you can use tools like `yt_dlp` to fetch video content directly from YouTube. However, when deploying on AWS (e.g., SageMaker or EC2), it’s necessary to use the **YouTube Data API** to access YouTube video metadata.

In this project, the YouTube Data API is used for fetching video details (e.g., title, description) and enabling further processing. This ensures that the application complies with YouTube's data access rules when running on cloud platforms.

### Why Use the YouTube API?

- **Compliance**: Accessing YouTube content via API ensures you comply with YouTube's Terms of Service, especially for server-side and cloud applications.
- **Cloud Access**: AWS environments, including EC2 and SageMaker, may not easily allow direct download methods such as `yt_dlp`. The YouTube API is the recommended approach for accessing video metadata and related information on cloud platforms.

## AWS Services Used

- **AWS Transcribe**: Used to process video URLs and transcribe the audio content (if needed).
- **AWS Bedrock (Mistral Model)**: Provides AI-powered responses to questions based on video transcripts.


## Example Code

Below is an example of how the main components are utilized:

```python
# Example usage of transcription and Bedrock response
transcript = transcribe_video("https://youtube.com/example_video_url", "example_transcription_job")
answer = get_bedrock_response(transcript, "What is this video about?")
print("Chatbot Answer:", answer)
```

## Troubleshooting

1. **Invalid YouTube URL**: Ensure the URL is correct and is a valid YouTube video.
2. **Transcript Issues**: If the transcript fails to load, check AWS Transcribe permissions and make sure the video URL is accessible.
3. **Bedrock Response Issues**: Check if the AWS Bedrock runtime is accessible and correctly set up in your AWS region.

## License

This project is licensed under the MIT License.

---

Feel free to customize any sections further or let me know if you need additional changes!
