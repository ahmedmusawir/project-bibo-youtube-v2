# VidGen - Windows Setup Guide

## What's in the Box

```
vidgen/
├── app/                    # The Streamlit web application
├── src/                    # Video pipeline modules
├── config/                 # App configuration (voices, models, etc.)
├── credentials/            # Google Cloud service account key (you provide)
├── tools/
│   ├── ffmpeg/             # ffmpeg.exe, ffplay.exe, ffprobe.exe
│   └── python/             # Embeddable Python 3.10 runtime
├── projects/               # Your video projects (created automatically)
├── .env                    # API keys and settings (created by INSTALL.bat)
├── INSTALL.bat             # One-time setup script
├── START.bat               # Daily launcher
└── requirements.txt        # Python dependencies
```

---

## First-Time Setup (One Time Only)

### Step 1: Unzip the Package

Unzip the VidGen folder to a location of your choice, for example:
```
C:\VidGen\
```

### Step 2: Add Your Credentials

1. Place the **Google Cloud service account key** file in the `credentials/` folder:
   ```
   credentials/cyberize-vertex-api.json
   ```

2. You should have received this file from your team. If not, ask for it.

### Step 3: Run the Installer

1. Double-click **`INSTALL.bat`**
2. Wait for it to finish (may take 3-5 minutes to install all Python packages)
3. When prompted, press any key to close

### Step 4: Edit Your API Keys

1. Open the `.env` file in Notepad (it was created by the installer)
2. Fill in your values:

   ```
   GOOGLE_APPLICATION_CREDENTIALS=credentials/cyberize-vertex-api.json
   GOOGLE_API_KEY=your-actual-gemini-api-key
   GOOGLE_CLOUD_PROJECT=your-gcp-project-id
   GOOGLE_CLOUD_REGION=us-central1
   GOOGLE_STT_BUCKET=your-gcs-bucket-name
   ```

3. Save and close the file

---

## Daily Usage

### Starting the App

1. Double-click **`START.bat`**
2. A browser window will open automatically with VidGen
3. Keep the black terminal window open while using the app

### Stopping the App

- Close the black terminal window, **or**
- Press `Ctrl+C` in the terminal window

---

## How to Use VidGen

### Creating a New Video Project

1. Click **"+ New Project"** in the sidebar and give it a name
2. Go to **Inputs** page:
   - **Paste Text:** Paste an article, blog post, or transcript → click "Save as Transcript"
   - **YouTube URL:** Paste a YouTube link → click "Transcribe Video" (takes 10-30 min)
3. Go to **Script** page → click "Create YouTube Script" to generate a polished script
4. Review, edit if needed, then **Approve**
5. Continue through each page in order:
   - **Audio** → Generate narration
   - **Metadata** → Generate titles, description, hashtags
   - **Images** → Generate AI images
   - **Video** → Compose final video
6. Each step must be **Approved** before the next one unlocks

### Tips

- **Long processes** (transcription, images, video) show real-time logs — be patient
- **Image generation** takes 5-10 minutes depending on video length
- **Video composition** takes 10-15 minutes for longer videos
- You can **regenerate** any step if you're not happy with the result
- Use the **copy button** on metadata titles/descriptions to copy them for YouTube

---

## Troubleshooting

### "Virtual environment not found"
Run `INSTALL.bat` first.

### "GOOGLE_API_KEY not set" or similar API errors
Check your `.env` file — make sure all values are filled in (no placeholder text).

### "Large audio file detected — set GOOGLE_STT_BUCKET"
Make sure `GOOGLE_STT_BUCKET` is set in your `.env` file.

### Images or audio fail to generate
- Check that `credentials/cyberize-vertex-api.json` exists
- Check that `GOOGLE_CLOUD_PROJECT` in `.env` matches your GCP project

### Video composition fails
- Make sure ffmpeg is in `tools/ffmpeg/` (ffmpeg.exe, ffprobe.exe)
- Try regenerating the video

### App won't start / blank page
- Make sure you're using `START.bat` (not running Python directly)
- Try closing the terminal and running `START.bat` again

---

## Support

Contact your development team if you run into issues not covered above.
