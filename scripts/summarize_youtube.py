import argparse
import logging
import os
import yt_dlp
from litellm import completion, completion_cost
from groq import Groq

# Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Constants
MODEL_NAME = "gpt-4o"
WHISPER_MODEL_SIZE = "whisper-large-v3"
DEFAULT_AUDIO_PATH = "audio.mp3"

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize Groq client
client = Groq()


def download_and_process_audio(youtube_url, output_dir):
    """Download and process audio from YouTube using yt-dlp and ffmpeg."""
    logging.info(f"Downloading audio from {youtube_url}")
    audio_path = os.path.join(output_dir, "audio.mp3")
    processed_audio_path = os.path.join(output_dir, "audio_processed.mp3")

    # yt-dlp options for downloading the best audio format and extracting as mp3
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": audio_path.replace(".mp3", ""),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    # Download audio from YouTube
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    logging.info(f"Downloaded audio to {audio_path}")

    # Process the audio file with ffmpeg to required format
    os.system(
        f'ffmpeg -i "{audio_path}" -ar 16000 -ac 1 -map 0:a "{processed_audio_path}"'
    )
    logging.info(f"Processed audio saved to {processed_audio_path}")

    return processed_audio_path


def transcribe_audio(processed_audio_path):
    """Transcribe audio using Groq's Whisper API."""
    logging.info(f"Starting transcription for {processed_audio_path}")

    # Open the processed audio file for reading
    with open(processed_audio_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(processed_audio_path, file.read()),
            model=WHISPER_MODEL_SIZE,
            response_format="json",  # Optional
            language="en",  # Optional
            temperature=0.0,  # Optional
        )

    transcript_text = transcription.text

    logging.info(f"Transcription completed for {processed_audio_path}")
    return transcript_text


def save_to_file(content, filename):
    """Save content to a file."""
    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)
    logging.info(f"Content saved to {filename}")


def read_from_file(filename):
    """Read content from a file."""
    logging.info(f"Reading content from {filename}")
    with open(filename, "r", encoding="utf-8") as file:
        return file.read()


def generate_response(prompt):
    """Generate a response using LiteLLM."""
    logging.info("Generating response from LiteLLM")
    messages = [{"content": prompt, "role": "user"}]
    response = completion(model=MODEL_NAME, messages=messages)

    # Calculate and log the cost of the response
    cost = completion_cost(completion_response=response)
    logging.info(f"Response cost: ${float(cost):.5f}")

    return response["choices"][0]["message"]["content"]


def summarize_transcript(transcript):
    """Summarize the transcript and generate notes."""
    logging.info("Summarizing transcript")
    summary = generate_response(
        f"Please summarize the following transcript and generate detailed notes:\n\n{transcript}"
    )
    return summary


def get_video_title(youtube_url):
    """Get the YouTube video title."""
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=False)
        return info_dict.get("title", "output").replace("/", "_")


def process_youtube_audio(youtube_url):
    """Main function to handle the workflow."""
    logging.info(f"Processing YouTube audio for URL: {youtube_url}")
    video_title = get_video_title(youtube_url)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "../output", video_title)

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.info(f"Created directory {output_dir}")

    # Download and process the audio
    processed_audio_path = download_and_process_audio(youtube_url, output_dir)

    transcript_path = os.path.join(output_dir, "transcript.txt")
    srt_path = os.path.join(output_dir, "transcript.srt")

    # Transcribe audio if transcript and SRT files do not exist
    if not os.path.exists(transcript_path) or not os.path.exists(srt_path):
        transcript = transcribe_audio(processed_audio_path)
        save_to_file(transcript, transcript_path)
    else:
        logging.info(f"Transcript already exists at {transcript_path}")
        logging.info(f"SRT file already exists at {srt_path}")
        transcript = read_from_file(transcript_path)

    summary_path = os.path.join(output_dir, "summary.txt")
    # Summarize transcript if summary file does not exist
    if not os.path.exists(summary_path):
        summary = summarize_transcript(transcript)
        save_to_file(summary, summary_path)
    else:
        logging.info(f"Summary already exists at {summary_path}")


if __name__ == "__main__":
    # Argument parser for command-line interface
    parser = argparse.ArgumentParser(
        description="Download, transcribe, and summarize YouTube audio."
    )
    parser.add_argument("youtube_url", help="URL of the YouTube video")
    args = parser.parse_args()

    # Process YouTube audio based on provided URL
    process_youtube_audio(args.youtube_url)
