#!/bin/bash

# Set up main structure (no extra folder prefix!)
mkdir -p 1-transcribe 2-summarize 3-synthesize 4-title-desc 5-visualize 6-video output utils

# Step folders and files
for STEP in 1-transcribe 2-summarize 3-synthesize 4-title-desc 5-visualize 6-video; do
  touch $STEP/README.md
done

touch 1-transcribe/transcriber.py
touch 2-summarize/summarizer.py
touch 3-synthesize/synthesizer.py
touch 4-title-desc/title_desc_generator.py
touch 5-visualize/img_prompt_generator.py
touch 5-visualize/image_generator.py
touch 6-video/video_builder.py

# Utility files
touch utils/logger.py
touch utils/timer.py
touch utils/youtube_helpers.py
touch utils/config.py
touch utils/.gitkeep

# Main files
touch main.py
touch .env
touch requirements.txt
touch README.md

# Example video output structure (change the video ID if you want to visualize another)
VID="xQUPXeYGsYk"
mkdir -p output/$VID/{transcript,summary,audio,title_desc,images,video,logs}
touch output/$VID/transcript/.gitkeep
touch output/$VID/summary/.gitkeep
touch output/$VID/audio/.gitkeep
touch output/$VID/title_desc/.gitkeep
touch output/$VID/images/.gitkeep
touch output/$VID/video/.gitkeep
touch output/$VID/logs/.gitkeep
touch output/$VID/meta.json

# Fill README.md files
echo "# Transcriber Module" > 1-transcribe/README.md
echo "# Summarizer Module" > 2-summarize/README.md
echo "# Synthesizer Module" > 3-synthesize/README.md
echo "# Title & Description Module" > 4-title-desc/README.md
echo "# Visualization/Image Generation Module" > 5-visualize/README.md
echo "# Video Builder Module" > 6-video/README.md
echo "# Utilities for Common Functions" > utils/.gitkeep
echo "# CyberVids Project v2  
Modular YouTube video generation pipeline for automation and course content.
" > README.md

echo "# .env file  
Add your API keys and other secret variables here.
" > .env

echo "# requirements.txt  
List of Python dependencies for the whole project.
" > requirements.txt

# Done
echo "✅ Stark Industries v2 folder structure created, boss!"
