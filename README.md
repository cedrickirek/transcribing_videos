# 📚 YouTube Learning Repository

A simple tool to save, summarize, and search your educational YouTube videos using AI.

## Features

-  Paste any YouTube URL to fetch transcript automatically
-  AI-generated bullet-point summaries using OpenAI
-  Keyword tagging for easy searching
-  SQLite database for local storage
-  Simple search functionality
-  Clean Streamlit interface

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up OpenAI API Key

**Option A: Environment Variable (Recommended)**
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your OpenAI API key
# Get your key from: https://platform.openai.com/api-keys
```

**Option B: Enter in App**
You can also enter your API key directly in the sidebar when running the app.

### 3. Run the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage

### Adding Videos

1. Go to the "Add Video" tab
2. Paste a YouTube URL
3. Click "Process Video"
4. Wait for the transcript and summary to be generated
5. The video is now saved in your repository!

### Searching

1. Go to the "Search" tab
2. Type any keyword (e.g., "transformer", "neural network", "backpropagation")
3. View all matching videos with their summaries

### Browsing All Videos

1. Go to the "All Videos" tab
2. Browse all your saved videos in chronological order
3. Click "Watch" to open the video on YouTube

## Project Structure

```
youtube_learning_repo/
├── app.py                 # Main Streamlit app
├── database.py            # SQLite database operations
├── video_processor.py     # YouTube transcript & AI summary logic
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment variables
├── learning_repo.db      # SQLite database (created on first run)
└── README.md             # This file
```

## Database Schema

```sql
CREATE TABLE videos (
    id INTEGER PRIMARY KEY,
    video_url TEXT UNIQUE,
    video_id TEXT,
    title TEXT,
    channel TEXT,
    transcript TEXT,
    summary TEXT,
    keywords TEXT,
    date_added TIMESTAMP
)
```

## Future Enhancements

- [ ] Flashcard generation mode
- [ ] Vector embeddings for semantic search
- [ ] Export to Markdown/Notion
- [ ] YouTube Data API integration for better metadata
- [ ] Tags/categories system
- [ ] Spaced repetition for review

## Requirements

- Python 3.8+
- OpenAI API key (costs ~$0.002 per summary with GPT-3.5-turbo)
- Internet connection for fetching transcripts

## Notes

- Only works with videos that have captions/subtitles available
- Transcript fetching is free (no YouTube API key needed)
- AI summaries use OpenAI API (minimal cost, ~$0.002 per video)
- Database is stored locally in `learning_repo.db`

## Troubleshooting

**"Could not fetch transcript"**
- Make sure the video has captions enabled
- Try a different video
- Check if the URL is correct

**"API key error"**
- Verify your OpenAI API key is correct
- Check you have credits in your OpenAI account

## License

MIT - Feel free to use and modify for your own learning!
