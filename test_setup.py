"""
Simple test script to verify your setup works
Run this before launching the full Streamlit app
"""

import os
from dotenv import load_dotenv
from video_processor import extract_video_id, get_transcript

# Load environment variables
load_dotenv()

def test_setup():
    print("🧪 Testing YouTube Learning Repository Setup\n")
    
    # Test 1: Check API key
    print("1. Checking OpenAI API key...")
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"   ✅ API key found: {api_key[:8]}...")
    else:
        print("   ⚠️  No API key in .env (you can add it in the app later)")
    
    # Test 2: Check dependencies
    print("\n2. Checking dependencies...")
    try:
        import streamlit
        import youtube_transcript_api
        import openai
        print("   ✅ All dependencies installed")
    except ImportError as e:
        print(f"   ❌ Missing dependency: {e}")
        print("   Run: pip install -r requirements.txt")
        return
    
    # Test 3: Test video ID extraction
    print("\n3. Testing video ID extraction...")
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    video_id = extract_video_id(test_url)
    if video_id:
        print(f"   ✅ Extracted video ID: {video_id}")
    else:
        print("   ❌ Failed to extract video ID")
        return
    
    # Test 4: Test transcript fetching
    print("\n4. Testing transcript fetching...")
    print("   (Testing with a known video with captions)")
    test_video = "dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up (has captions)
    transcript = get_transcript(test_video)
    if transcript:
        print(f"   ✅ Transcript fetched! Length: {len(transcript)} characters")
        print(f"   Preview: {transcript[:100]}...")
    else:
        print("   ⚠️  Could not fetch transcript (this might be normal)")
    
    # Test 5: Test database creation
    print("\n5. Testing database...")
    try:
        from database import VideoDatabase
        db = VideoDatabase("test_db.db")
        print("   ✅ Database initialized successfully")
        # Clean up test database
        os.remove("test_db.db")
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return
    
    print("\n" + "="*50)
    print("✅ Setup test complete!")
    print("\nYou're ready to run: streamlit run app.py")
    print("="*50)

if __name__ == "__main__":
    test_setup()
