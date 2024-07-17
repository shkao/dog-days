import argparse
import logging
import os
import time
import yt_dlp
import whisper
from litellm import completion, completion_cost
from groq import Groq, RateLimitError

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


def download_audio(youtube_url, output_dir):
    """Download audio from YouTube and save as mp3."""
    logging.info(f"Downloading audio from {youtube_url}")
    audio_path = os.path.join(output_dir, "audio.mp3")

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

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    logging.info(f"Downloaded audio to {audio_path}")
    return audio_path


def process_audio(audio_path, output_dir):
    """Process the downloaded audio file with ffmpeg."""
    processed_audio_path = os.path.join(output_dir, "audio_processed.mp3")
    os.system(
        f'ffmpeg -i "{audio_path}" -ar 16000 -ac 1 -map 0:a "{processed_audio_path}"'
    )
    logging.info(f"Processed audio saved to {processed_audio_path}")
    return processed_audio_path


def transcribe_audio(audio_path, max_retries=3, initial_delay=60):
    """Transcribe audio using Groq's Whisper API with retry mechanism."""
    logging.info(f"Starting transcription for {audio_path}")
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    retries = 0
    while retries < max_retries:
        try:
            with open(audio_path, "rb") as file:
                transcription = client.audio.transcriptions.create(
                    file=(audio_path, file.read()),
                    model=WHISPER_MODEL_SIZE,
                    response_format="json",
                    language="en",
                    temperature=0.0,
                )
            logging.info(f"Transcription completed for {audio_path}")
            return transcription.text
        except RateLimitError as err:
            wait_time = initial_delay * (2**retries)  # Exponential backoff
            logging.warning(
                f"Rate limit reached: {err}. Retrying in {wait_time} seconds..."
            )
            time.sleep(wait_time)
            retries += 1

    logging.warning(
        "Max retries exceeded for Groq transcription due to rate limit. Falling back to local transcription."
    )
    model = whisper.load_model("medium")
    result = model.transcribe(audio_path)
    return result["text"]


def save_content(content, filepath):
    """Save content to a file."""
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(content)
    logging.info(f"Content saved to {filepath}")


def read_content(filepath):
    """Read content from a file."""
    logging.info(f"Reading content from {filepath}")
    with open(filepath, "r", encoding="utf-8") as file:
        return file.read()


def generate_summary(prompt):
    """Generate a summary using LiteLLM and convert cost from USD to TWD."""
    logging.info("Generating summary using LiteLLM")
    messages = [{"content": prompt, "role": "user"}]
    response = completion(model=MODEL_NAME, messages=messages)
    cost_usd = completion_cost(completion_response=response)

    # Conversion rate from USD to TWD
    conversion_rate_usd_to_twd = 31.0  # Example exchange rate
    cost_twd = float(cost_usd) * conversion_rate_usd_to_twd
    logging.info(
        f"\033[91mResponse cost: ${float(cost_usd):.2f} USD ({cost_twd:.2f} TWD)\033[0m"
    )
    return response["choices"][0]["message"]["content"]


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
    sanitized_url = youtube_url.replace("\\", "")
    logging.info(f"Processing YouTube audio for URL: {sanitized_url}")
    video_title = get_video_title(sanitized_url)
    sanitized_video_title = "".join(
        c for c in video_title if c.isalnum() or c in (" ", "_")
    ).rstrip()
    sanitized_video_title = " ".join(sanitized_video_title.split())
    output_dir = os.path.join(os.getcwd(), sanitized_video_title)

    if os.path.exists(output_dir):
        logging.info(
            f"Output directory {output_dir} already exists. Skipping processing."
        )
        return

    os.makedirs(output_dir)
    logging.info(f"Created directory {output_dir}")

    audio_path = download_audio(sanitized_url, output_dir)
    processed_audio_path = process_audio(audio_path, output_dir)

    transcript_path = os.path.join(output_dir, "transcript.txt")
    summary_path = os.path.join(output_dir, "summary.md")

    transcript = transcribe_audio(processed_audio_path)
    transcript_with_url = f"{transcript}\n\nSource URL: {sanitized_url}"
    save_content(transcript_with_url, transcript_path)

    summary = generate_summary(
        f"Please summarize the following transcript and generate detailed notes:\n\n{transcript}"
    )
    summary_with_url = f"{summary}\n\nSource URL: {sanitized_url}"
    save_content(summary_with_url, summary_path)

    # Remove audio files after all jobs are done
    if os.path.exists(audio_path):
        os.remove(audio_path)
        logging.info(f"Removed audio file {audio_path}")
    if os.path.exists(processed_audio_path):
        os.remove(processed_audio_path)
        logging.info(f"Removed processed audio file {processed_audio_path}")

    if os.path.exists(summary_path):
        os.system(f'code "{summary_path}"')


def process_youtube_playlist(file_path):
    """Process a text file containing YouTube URLs."""
    with open(file_path, "r") as file:
        urls = file.readlines()
    for url in urls:
        process_youtube_audio(url.strip())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download, transcribe, and summarize YouTube audio."
    )
    parser.add_argument(
        "input", help="URL of the YouTube video or path to a text file containing URLs"
    )
    args = parser.parse_args()

    if os.path.isfile(args.input):
        process_youtube_playlist(args.input)
    else:
        process_youtube_audio(args.input)
