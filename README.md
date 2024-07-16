# Domain Knowledge Learning Journey

This repository contains my notes and resources for learning domain knowledge in various fields related to AI and other technologies. The main focus areas are stored in the `domain-knowledge/` directory, which includes:

- AI
- AIDD (AI-Driven Drug Discovery)
- Bioinformatics
- Biology
- Cheminformatics
- Chemistry
- Informatics
- Mathematics
- Medicinal Chemistry

## Structure

Each subdirectory in `domain-knowledge/` contains a README.md file with specific information about that domain. As I progress in my learning journey, I'll be adding more detailed notes, resources, and possibly code examples to each area.

## Tools

### YouTube Video Summarizer

Located in `scripts/summarize_youtube.py`, this tool helps in my learning process by:

1. Downloading audio from a YouTube video
2. Transcribing the audio using Groq's Whisper API
3. Generating a summary of the transcript using LiteLLM (GPT-4)

Usage:

```
python scripts/summarize_youtube.py <youtube_url>
```

The script creates an output directory with the video title, containing:

- `transcript.txt`: Full transcription of the video
- `summary.md`: Detailed summary and notes generated from the transcript

Note: Make sure to set your OpenAI API key as an environment variable (`OPENAI_API_KEY`) before running the script.

## Future Additions

This repository will be continuously updated with more notes, resources, and tools as I progress in my learning journey across these domains.

## Sources

The materials and inspiration for this project come from various sources, including academic papers, textbooks, online courses, and expert talks. Specific sources will be cited within the notes for each domain.
