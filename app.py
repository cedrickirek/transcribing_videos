import os
import streamlit as st
from dotenv import load_dotenv
from database import VideoDatabase
from video_processor import extract_video_id, get_transcript, transcribe_with_whisper, generate_summary, get_video_metadata
from sheets_exporter import export_to_sheets

load_dotenv()

# Initialize database
db = VideoDatabase()

# Page config
st.set_page_config(
    page_title="YouTube Learning Repository",
    page_icon="📚",
    layout="wide"
)

# Title
st.title("📚 YouTube Learning Repository")
st.markdown("*Save and search your educational YouTube videos with AI-generated summaries*")

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")

    # Model selection for Ollama
    model = st.selectbox(
        "Ollama Model",
        ["llama3.2", "llama3.1", "mistral", "phi3", "gemma2"],
        help="Select the local model to use for summarization. Make sure it's pulled in Ollama."
    )

    st.markdown("---")
    st.markdown("### Setup")
    st.markdown("""
    1. Install [Ollama](https://ollama.ai)
    2. Run: `ollama pull llama3.2`
    3. Start: `ollama serve`
    """)
    st.markdown("**For videos without subtitles:**")
    st.markdown("Install [ffmpeg](https://ffmpeg.org/download.html) and run `pip install yt-dlp faster-whisper`")

    st.markdown("---")
    st.markdown("### Google Sheets Export")
    sheets_credentials = st.text_input(
        "Credentials JSON path",
        value=os.getenv("GOOGLE_CREDENTIALS_PATH", ""),
        help="Path to your Google service account JSON file."
    )
    sheets_id = st.text_input(
        "Spreadsheet ID",
        value=os.getenv("GOOGLE_SPREADSHEET_ID", ""),
        help="Found in the Google Sheets URL: .../spreadsheets/d/SPREADSHEET_ID/edit"
    )

    st.markdown("---")
    st.markdown("### About")
    st.markdown("This tool helps you save and organize educational YouTube content with AI-generated summaries.")

# Main tabs
tab1, tab2, tab3 = st.tabs(["➕ Add Video", "🔍 Search", "📋 All Videos"])

# TAB 1: Add New Video
with tab1:
    st.header("Add New Video")

    video_url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...")

    col1, col2 = st.columns([1, 4])
    with col1:
        process_button = st.button("Process Video", type="primary", use_container_width=True)

    if process_button:
        if not video_url:
            st.error("❌ Please enter a YouTube URL")
        else:
            # Check if video already exists
            existing = db.get_video_by_url(video_url)
            if existing:
                st.warning("⚠️ This video is already in your repository!")
                st.json(existing)
            else:
                with st.spinner("Processing video..."):
                    # Extract video ID
                    video_id = extract_video_id(video_url)
                    if not video_id:
                        st.error("❌ Invalid YouTube URL")
                    else:
                        # Fetch transcript
                        st.info("📝 Fetching transcript...")
                        transcript, error = get_transcript(video_id)

                        if not transcript:
                            st.warning(f"⚠️ No YouTube transcript: {error}")
                            st.info("🎙️ Downloading audio and transcribing with Whisper — this may take a few minutes...")
                            transcript, error = transcribe_with_whisper(video_id)
                            if transcript:
                                st.success("✅ Audio transcribed with Whisper!")

                        if not transcript:
                            st.error(f"❌ {error}")
                        else:
                            # Generate summary
                            st.info(f"🤖 Generating summary with {model}...")
                            summary, keywords = generate_summary(transcript, model)

                            # Get metadata (simplified for MVP)
                            title, channel = get_video_metadata(video_id)

                            # Save to database
                            success = db.add_video(
                                video_url=video_url,
                                video_id=video_id,
                                title=title,
                                channel=channel,
                                transcript=transcript,
                                summary=summary,
                                keywords=keywords
                            )

                            if success:
                                st.success("✅ Video added successfully!")

                                # Display results
                                st.markdown("### Summary")
                                st.markdown(summary)

                                st.markdown("### Keywords")
                                st.code(keywords)

                                # Show transcript (collapsible)
                                with st.expander("View Full Transcript"):
                                    st.text(transcript[:2000] + "..." if len(transcript) > 2000 else transcript)
                            else:
                                st.error("❌ Failed to save video to database")

# TAB 2: Search
with tab2:
    st.header("Search Your Videos")

    search_query = st.text_input("Search by keyword", placeholder="e.g., 'transformer', 'GAN', 'attention mechanism'")

    if search_query:
        results = db.search_by_keyword(search_query)

        st.markdown(f"### Found {len(results)} result(s)")

        if results:
            for video in results:
                with st.container():
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown(f"**{video['title']}**")
                        st.markdown(f"*{video['channel']}* • {video['date_added'][:10]}")

                    with col2:
                        st.link_button("Watch", video['video_url'], use_container_width=True)

                    # Summary
                    st.markdown("**Summary:**")
                    st.markdown(video['summary'])

                    # Keywords
                    if video['keywords']:
                        st.markdown(f"**Keywords:** `{video['keywords']}`")

                    st.markdown("---")
        else:
            st.info("No videos found matching your search.")

# TAB 3: All Videos
with tab3:
    st.header("All Saved Videos")

    all_videos = db.get_all_videos(limit=100)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### Total: {len(all_videos)} video(s)")
    with col2:
        export_button = st.button("Export to Google Sheets", use_container_width=True)

    if export_button:
        if not sheets_credentials or not sheets_id:
            st.error("❌ Set the credentials path and spreadsheet ID in the sidebar first.")
        elif not all_videos:
            st.warning("⚠️ No videos to export.")
        else:
            with st.spinner("Exporting to Google Sheets..."):
                success, message = export_to_sheets(all_videos, sheets_credentials, sheets_id)
            if success:
                st.success(f"✅ {message}")
            else:
                st.error(f"❌ {message}")

    if all_videos:
        for video in all_videos:
            with st.container():
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"**{video['title']}**")
                    st.markdown(f"*{video['channel']}* • {video['date_added'][:10]}")

                with col2:
                    st.link_button("Watch", video['video_url'], use_container_width=True)

                # Summary
                with st.expander("View Summary"):
                    st.markdown(video['summary'])
                    if video['keywords']:
                        st.markdown(f"**Keywords:** `{video['keywords']}`")

                st.markdown("---")
    else:
        st.info("No videos saved yet. Add your first video in the 'Add Video' tab!")

# Footer
st.markdown("---")
st.markdown("*Built with Streamlit • Store your learning journey* 🚀")
