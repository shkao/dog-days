# AI Learning Journey

This repository contains toolkits and notes from my learning journey towards AI and other related technologies.

## Current Tools

### YouTube Video Summarizer

Located in `scripts/summarize_youtube.py`, this tool allows you to:

1. Download audio from a YouTube video
2. Transcribe the audio using Groq's Whisper API
3. Generate a summary of the transcript using LiteLLM (GPT-4)

Usage:
```
python scripts/summarize_youtube.py <youtube_url>
```

The script will create an output directory with the video title, containing:
- `transcript.txt`: Full transcription of the video
- `summary.md`: Detailed summary and notes generated from the transcript

Note: Make sure to set your OpenAI API key as an environment variable (`OPENAI_API_KEY`) before running the script.

## Future Additions

This repository will be updated with more tools, notes, and resources as I continue my AI learning journey.
