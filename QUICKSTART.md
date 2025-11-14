# 🚀 Quick Start Guide

Get up and running in 5 minutes!

## Step 1: Install Dependencies

```bash
cd youtube_learning_repo
pip install -r requirements.txt
```

## Step 2: Get OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Create an account or sign in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-...`)

## Step 3: Add Your API Key

**Option A: Create .env file (Recommended)**
```bash
echo "OPENAI_API_KEY=sk-your-actual-key-here" > .env
```

**Option B: Enter in the app later**
Skip this step and enter it in the sidebar when you run the app.

## Step 4: Run the App

```bash
streamlit run app.py
```

Your browser will open to `http://localhost:8501`

## Step 5: Test It!

Try adding this video about transformers:
```
https://www.youtube.com/watch?v=kCc8FmEb1nY
```

Or any MIT/Stanford lecture you've been watching!

## Common Issues

### "ModuleNotFoundError"
```bash
# Make sure you're in the right directory
cd youtube_learning_repo
pip install -r requirements.txt
```

### "Could not fetch transcript"
- The video needs to have captions/subtitles
- Try a different video that you know has captions

### "OpenAI API Error"
- Check your API key is correct
- Verify you have credits: https://platform.openai.com/account/usage

## Cost Estimate

- Fetching transcripts: **FREE** ✅
- AI summaries: **~$0.002 per video** (using GPT-3.5-turbo)
- Example: 100 videos ≈ $0.20

## Tips

1. **Start simple**: Add 2-3 videos first to test it
2. **Use search**: Add videos from similar topics, then search by concept
3. **Keywords matter**: The AI auto-generates good keywords for searching
4. **Local storage**: Everything is saved in `learning_repo.db` on your machine

## Next Steps

Once you're comfortable, consider:
- Adding more videos from your favorite channels
- Searching by ML concepts you're studying
- Exporting summaries for exam prep
- Adding this to your GitHub portfolio!

---

**Need help?** Check the full README.md for detailed documentation.
