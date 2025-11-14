import streamlit as st
from database import VideoDatabase
from video_processor import extract_video_id, get_transcript, generate_summary, get_video_metadata
import os
from dotenv import load_dotenv

# Load environment variables
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

# Sidebar for API key (for first-time setup)
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
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
        if not api_key:
            st.error("❌ Please add your OpenAI API key in the sidebar")
        elif not video_url:
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
                        transcript = get_transcript(video_id)
                        
                        if not transcript:
                            st.error("❌ Could not fetch transcript. Make sure the video has captions available.")
                        else:
                            # Generate summary
                            st.info("🤖 Generating summary with AI...")
                            summary, keywords = generate_summary(transcript, api_key)
                            
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
    
    st.markdown(f"### Total: {len(all_videos)} video(s)")
    
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
