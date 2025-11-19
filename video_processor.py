from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
import re
from typing import Optional, Tuple
import openai
import os

def extract_video_id(url: str) -> Optional[str]:
    """Extract video ID from YouTube URL"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
        r'youtube\.com\/embed\/([^&\n?#]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_transcript(video_id: str) -> Tuple[Optional[str], Optional[str]]:
    """Fetch transcript for a YouTube video
    Returns: (transcript, error_message)
    """
    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.fetch(video_id)
        transcript = " ".join([entry.text for entry in transcript_list])
        return transcript, None
    except TranscriptsDisabled:
        return None, "Transcripts are disabled for this video by the creator."
    except (NoTranscriptFound, VideoUnavailable):
        # Try to list available transcripts
        try:
            api = YouTubeTranscriptApi()
            available_transcripts = api.list(video_id)
            available = [f"{t.language} ({t.language_code})" for t in available_transcripts]
            return None, f"No English transcript found. Available: {', '.join(available) if available else 'None'}"
        except:
            return None, "No transcripts found for this video."
    except Exception as e:
        return None, f"Error fetching transcript: {str(e)}"

def generate_summary(transcript: str, api_key: str) -> Tuple[str, str]:
    """
    Generate bullet point summary and keywords using OpenAI
    Returns: (summary, keywords)
    """
    openai.api_key = api_key
    
    # Truncate transcript if too long (roughly 3000 words = ~4000 tokens)
    words = transcript.split()
    if len(words) > 3000:
        transcript = " ".join(words[:3000]) + "..."
    
    prompt = f"""You are summarizing an educational video transcript for a data science master's student.

Transcript:
{transcript}

Please provide:
1. A concise bullet-point summary (5-10 key points) capturing the main concepts, techniques, and insights
2. A list of 5-10 relevant keywords/tags for easy searching later

Format your response as:

SUMMARY:
• [point 1]
• [point 2]
...

KEYWORDS:
keyword1, keyword2, keyword3, ..."""

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates clear, informative summaries of educational content."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=500
        )
        
        content = response.choices[0].message.content
        
        # Parse the response
        summary_split = content.split("KEYWORDS:")
        summary = summary_split[0].replace("SUMMARY:", "").strip()
        keywords = summary_split[1].strip() if len(summary_split) > 1 else ""
        
        return summary, keywords
    
    except Exception as e:
        error_msg = str(e)
        print(f"Error generating summary: {error_msg}")
        return f"Summary generation failed: {error_msg}", ""

def get_video_metadata(video_id: str) -> Tuple[str, str]:
    """
    Get basic video metadata (title, channel)
    Note: This is a simplified version. For production, use YouTube Data API
    """
    # For MVP, we'll return simple placeholders
    # You can enhance this later with youtube-dl or YouTube Data API
    return f"Video {video_id}", "Unknown Channel"
