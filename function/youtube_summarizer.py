
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from transformers import pipeline
import torch
from concurrent.futures import ThreadPoolExecutor

def get_video_transcript(video_id):
    """
    Fetches the transcript of a YouTube video using its video ID.
    """
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_transcript(['en']).fetch()
        text = " ".join([entry['text'] for entry in transcript])
        return text
    except TranscriptsDisabled:
        return "Error: This video does not have a transcript available."
    except Exception as e:
        return f"Error fetching transcript: {str(e)}"

# Load Summarization Model with GPU support
device = 0 if torch.cuda.is_available() else -1
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6", device=device)

def chunk_text(text, max_tokens=300):
    """
    Splits the text into chunks of approximately `max_tokens` tokens.
    """
    words = text.split()
    chunks = [" ".join(words[i:i + max_tokens]) for i in range(0, len(words), max_tokens)]
    return chunks

def summarize_text(text, min_length=50):
    """
    Summarizes long transcript text by chunking if necessary.
    Uses parallel processing and returns the summarized text.
    """
    try:
        chunks = chunk_text(text, max_tokens=300)  # Smaller chunk size for better efficiency
        summaries = []
        
        with ThreadPoolExecutor() as executor:
            for summary in executor.map(lambda chunk: summarizer(chunk, max_length=max(50, int(len(chunk.split()) * 0.5)), min_length=min_length, do_sample=False)[0]['summary_text'], chunks):
                summaries.append(summary)
        
        return " ".join(summaries)  # Return summarized text instead of saving to a file
    except Exception as e:
        return f"Error summarizing text: {str(e)}"