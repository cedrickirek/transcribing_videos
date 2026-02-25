from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
import re
from typing import Optional, Tuple
import requests
import os
import tempfile


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
    """Fetch transcript via YouTube's transcript API.
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
        try:
            api = YouTubeTranscriptApi()
            available_transcripts = api.list(video_id)
            available = [f"{t.language} ({t.language_code})" for t in available_transcripts]
            return None, f"No English transcript found. Available: {', '.join(available) if available else 'None'}"
        except:
            return None, "No transcripts found for this video."
    except Exception as e:
        return None, f"Error fetching transcript: {str(e)}"


def transcribe_with_whisper(video_id: str) -> Tuple[Optional[str], Optional[str]]:
    """Download audio with yt-dlp and transcribe with faster-whisper.
    Returns: (transcript, error_message)
    """
    try:
        import yt_dlp
        from faster_whisper import WhisperModel
    except ImportError as e:
        return None, f"Missing dependency: {e}. Install with: pip install yt-dlp faster-whisper"

    url = f"https://www.youtube.com/watch?v={video_id}"

    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = os.path.join(tmpdir, "audio")
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': audio_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }],
            'quiet': True,
            'no_warnings': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            return None, f"Failed to download audio: {str(e)}"

        actual_path = audio_path + ".mp3"
        if not os.path.exists(actual_path):
            return None, "Audio download failed: output file not found. Make sure ffmpeg is installed."

        try:
            model = WhisperModel("base", device="cpu", compute_type="int8")
            segments, _ = model.transcribe(actual_path)
            transcript = " ".join([seg.text.strip() for seg in segments])
            return transcript, None
        except Exception as e:
            return None, f"Transcription failed: {str(e)}"


def estimate_duration_minutes(transcript: str) -> int:
    """Estimate video duration from transcript word count (~150 words/minute)."""
    return max(1, len(transcript.split()) // 150)


def generate_summary(transcript: str, model: str = "llama3.2") -> Tuple[str, str]:
    """Generate a summary and keywords using Ollama.
    Summary length and detail adapt based on estimated video duration.
    Returns: (summary, keywords)
    """
    duration = estimate_duration_minutes(transcript)

    if duration < 10:
        overview_instruction = "1. **Overview** (1-2 sentences): What is this video about?"
        keypoints_instruction = "2. **Key Points** (3-5 bullets): The most important facts or takeaways."
        extra_sections = ""
        format_body = (
            "**Overview**\n[Your overview here]\n\n"
            "**Key Points**\n• [point 1]\n• [point 2]\n..."
        )
    elif duration < 30:
        overview_instruction = "1. **Overview** (2-3 sentences): What is this video about? What's the main topic or argument?"
        keypoints_instruction = (
            "2. **Key Points** (5-8 bullets): The most important facts, insights, or arguments. Include:\n"
            "   - Main concepts explained\n"
            "   - Any statistics or data mentioned\n"
            "   - Conclusions or takeaways"
        )
        extra_sections = "\n3. **Context**: Any relevant background information mentioned"
        format_body = (
            "**Overview**\n[Your overview here]\n\n"
            "**Key Points**\n• [point 1]\n• [point 2]\n...\n\n"
            "**Context**\n[Context information]"
        )
    else:
        overview_instruction = "1. **Overview** (3-4 sentences): What is this video about? What's the main topic, argument, or narrative arc?"
        keypoints_instruction = (
            "2. **Key Points** (8-12 bullets): The most important facts, insights, or arguments. Include:\n"
            "   - Any statistics or data mentioned\n"
            "   - Main concepts explained\n"
            "   - Personal stories or examples used\n"
            "   - Conclusions or takeaways"
        )
        extra_sections = (
            "\n3. **Context**: Relevant background information, historical or social context"
            "\n4. **Conclusions**: Key takeaways and actionable insights"
        )
        format_body = (
            "**Overview**\n[Your overview here]\n\n"
            "**Key Points**\n• [point 1]\n• [point 2]\n...\n\n"
            "**Context**\n[Context information]\n\n"
            "**Conclusions**\n[Key takeaways]"
        )

    prompt = f"""Analyze this video transcript and create a summary appropriate for a ~{duration}-minute video.

Transcript:
{transcript}

Create a summary with these sections:
{overview_instruction}

{keypoints_instruction}{extra_sections}

Format your response EXACTLY as:

SUMMARY:
{format_body}

KEYWORDS:
keyword1, keyword2, keyword3, ..."""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.5
                }
            },
            timeout=None
        )

        if response.status_code != 200:
            return f"Summary generation failed: Ollama returned status {response.status_code}", ""

        content = response.json().get("response", "")

        if not content:
            return "Summary generation failed: Empty response from Ollama", ""

        summary_split = content.split("KEYWORDS:")
        summary = summary_split[0].replace("SUMMARY:", "").strip()
        keywords = summary_split[1].strip() if len(summary_split) > 1 else ""

        return summary, keywords

    except requests.exceptions.ConnectionError:
        return "Summary generation failed: Cannot connect to Ollama. Make sure Ollama is running (ollama serve)", ""
    except requests.exceptions.Timeout:
        return "Summary generation failed: Ollama request timed out. Try a smaller model.", ""
    except Exception as e:
        return f"Summary generation failed: {str(e)}", ""


def get_video_metadata(video_id: str) -> Tuple[str, str]:
    """Get basic video metadata (title, channel)"""
    return f"Video {video_id}", "Unknown Channel"
