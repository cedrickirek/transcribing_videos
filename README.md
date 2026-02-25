# YouTube Learning Repository

A tool to save, summarize, and search your educational YouTube videos using local AI — no API keys or cloud costs.

## Features

- Paste any YouTube URL to fetch its transcript automatically
- AI-generated summaries using a local Ollama model — summary length adapts to video duration
- Fallback audio transcription via Whisper for videos without subtitles
- Keyword tagging for easy searching
- SQLite database for local storage
- Clean Streamlit interface

## Setup

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Install and start Ollama

1. Download [Ollama](https://ollama.ai)
2. Pull a model:
   ```bash
   ollama pull llama3.2
   ```
3. Start the server:
   ```bash
   ollama serve
   ```

### 3. (Optional) Enable transcription for videos without subtitles

Install [ffmpeg](https://ffmpeg.org/download.html) and make sure it's on your PATH, then:

```bash
pip install yt-dlp faster-whisper
```

When a YouTube transcript is unavailable, the app will automatically download the audio and transcribe it locally using Whisper (`base` model, CPU).

### 4. Run the app

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage

### Adding a video

1. Go to the **Add Video** tab
2. Paste a YouTube URL
3. Select an Ollama model in the sidebar
4. Click **Process Video**
5. The app fetches the transcript (or transcribes the audio if needed), generates a summary, and saves everything locally

### Searching

Go to the **Search** tab and type any keyword — the app searches across summaries and keywords.

### Browsing

Go to the **All Videos** tab to browse all saved videos in chronological order.

## Adaptive summaries

Summary detail scales with estimated video length (derived from transcript word count at ~150 words/minute):

| Duration | Summary |
|---|---|
| < 10 min | 1-2 sentence overview, 3-5 key points |
| 10–30 min | 2-3 sentence overview, 5-8 key points, context section |
| > 30 min | 3-4 sentence overview, 8-12 key points, context + conclusions |

## Project structure

```
├── app.py               # Streamlit UI
├── database.py          # SQLite operations
├── video_processor.py   # Transcript fetching, Whisper fallback, summary generation
├── requirements.txt     # Python dependencies
└── learning_repo.db     # Local database (created on first run)
```

## Google Sheets export

You can sync all your saved videos to a Google Sheet directly from the **All Videos** tab.

### One-time setup

1. Go to [Google Cloud Console](https://console.cloud.google.com) and create a project
2. Enable the **Google Sheets API** and **Google Drive API**
3. Go to **IAM & Admin → Service Accounts**, create a service account, and download its JSON key file
4. Create a Google Sheet, then share it with the service account's email address (e.g. `my-bot@my-project.iam.gserviceaccount.com`) with **Editor** access
5. Copy the spreadsheet ID from the URL: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`

### Configure the app

Either set environment variables in a `.env` file:

```
GOOGLE_CREDENTIALS_PATH=path/to/credentials.json
GOOGLE_SPREADSHEET_ID=your_spreadsheet_id
```

Or enter the values directly in the sidebar when running the app.

Each export does a **full sync** — it clears the sheet and rewrites all videos. Columns: Title, Channel, URL, Date Added, Summary, Keywords.

## Requirements

- Python 3.8+
- [Ollama](https://ollama.ai) running locally
- Internet connection for fetching YouTube transcripts
- (Optional) [ffmpeg](https://ffmpeg.org/download.html) for Whisper audio transcription
- (Optional) Google Cloud service account for Sheets export

## Troubleshooting

**"Cannot connect to Ollama"**
- Make sure Ollama is running: `ollama serve`
- Check the selected model is pulled: `ollama pull llama3.2`

**"Audio download failed"**
- Make sure `ffmpeg` is installed and available on your PATH

**"No transcripts found"**
- If the optional Whisper dependencies are installed, the app will attempt audio transcription automatically
- If not installed, install them: `pip install yt-dlp faster-whisper` (and ffmpeg)

## Future ideas

- [ ] Flashcard generation mode
- [ ] Vector embeddings for semantic search
- [ ] Export to Markdown / Notion
- [ ] YouTube Data API for real video titles and channel names
- [ ] Tags / categories system
