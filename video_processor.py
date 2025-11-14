from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
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

def get_transcript(video_id: str) -> Optional[str]:
    """Fetch transcript for a YouTube video"""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([entry['text'] for entry in transcript_list])
        return transcript
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        return None
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None

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
        print(f"Error generating summary: {e}")
        return "Summary generation failed", ""

def get_video_metadata(video_id: str) -> Tuple[str, str]:
    """
    Get basic video metadata (title, channel)
    Note: This is a simplified version. For production, use YouTube Data API
    """
    # For MVP, we'll return simple placeholders
    # You can enhance this later with youtube-dl or YouTube Data API
    return f"Video {video_id}", "Unknown Channel"
