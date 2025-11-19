# Troubleshooting Log - YouTube Transcript App

## Summary
The app was failing to fetch video transcripts due to an outdated `youtube-transcript-api` library, compounded by significant API changes in the new version.

---

## Issue 1: Generic Error Message

**Error:**
```
❌ Could not fetch transcript. Make sure the video has captions available.
```

**Problem:** The `get_transcript()` function was silently returning `None` without any details about the actual failure.

**Fix:** Modified the function to return a tuple `(transcript, error_message)` with specific error messages for different failure cases (TranscriptsDisabled, NoTranscriptFound, etc.).

---

## Issue 2: XML Parsing Error

**Error:**
```
❌ Error fetching transcript: no element found: line 1, column 0
```

**Problem:** The `youtube-transcript-api` library version 0.6.1 was outdated. YouTube had changed their API, causing the library to receive empty/invalid responses.

**Fix:** Upgraded the library from version 0.6.1 to 1.2.3:
```bash
pip install --upgrade youtube-transcript-api
```

---

## Issue 3: Import Error for NoTranscriptAvailable

**Error:**
```
ImportError: cannot import name 'NoTranscriptAvailable' from 'youtube_transcript_api._errors'
```

**Problem:** The error class `NoTranscriptAvailable` doesn't exist in version 1.2.3. The available error classes changed between versions.

**What didn't work:** Initially tried to import `NoTranscriptAvailable` which doesn't exist.

**Fix:** Checked available error classes and used `VideoUnavailable` instead:
```python
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
```

---

## Issue 4: Missing get_transcript Attribute

**Error:**
```
❌ Error fetching transcript: type object 'YouTubeTranscriptApi' has no attribute 'get_transcript'
```

**Problem:** The API methods changed in version 1.x:
- `get_transcript()` → `fetch()`
- `list_transcripts()` → `list()`

**What didn't work:** Using the old method names with the new library version.

**Fix:** Updated method calls:
```python
# Old API (0.6.x)
transcript_list = YouTubeTranscriptApi.get_transcript(video_id)

# New API (1.x)
transcript_list = YouTubeTranscriptApi.fetch(video_id)
```

---

## Issue 5: Missing Positional Argument

**Error:**
```
❌ Error fetching transcript: fetch() missing 1 required positional argument: 'video_id'
```

**Problem:** In version 1.x, `YouTubeTranscriptApi` must be instantiated before calling methods. Also, the return type changed from dictionaries to objects.

**What didn't work:** Calling methods as static/class methods without instantiation.

**Fix:** Instantiate the API and access properties instead of dictionary keys:
```python
# Old API (0.6.x)
transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
transcript = " ".join([entry['text'] for entry in transcript_list])

# New API (1.x)
api = YouTubeTranscriptApi()
transcript_list = api.fetch(video_id)
transcript = " ".join([entry.text for entry in transcript_list])
```

---

## Issue 6: OpenAI Quota Exceeded

**Error:**
```
Summary generation failed: Error code: 429 - {'error': {'message': 'You exceeded your current quota, please check your plan and billing details...', 'type': 'insufficient_quota', 'param': None, 'code': 'insufficient_quota'}}
```

**Problem:** The OpenAI API key has no remaining credits/quota.

**Status:** Not a code issue. Requires either:
1. Adding billing to OpenAI account
2. Switching to a free/local model alternative (e.g., Ollama)

---

## Final Working Code Changes

### video_processor.py - get_transcript()

```python
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
        try:
            api = YouTubeTranscriptApi()
            available_transcripts = api.list(video_id)
            available = [f"{t.language} ({t.language_code})" for t in available_transcripts]
            return None, f"No English transcript found. Available: {', '.join(available) if available else 'None'}"
        except:
            return None, "No transcripts found for this video."
    except Exception as e:
        return None, f"Error fetching transcript: {str(e)}"
```

### app.py - Updated to handle tuple return

```python
transcript, error = get_transcript(video_id)

if not transcript:
    st.error(f"❌ {error}")
```

---

## Lessons Learned

1. **Always show detailed error messages** - Silent failures make debugging impossible
2. **Check library versions** - Major version upgrades often have breaking API changes
3. **Test API changes** - Use Python REPL to inspect available methods/classes when APIs change
4. **Read changelogs** - The youtube-transcript-api 1.0 release had significant breaking changes
