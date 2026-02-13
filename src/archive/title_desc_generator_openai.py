# title_desc_generator.py

from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
import json

# === Load .env ===
load_dotenv()

# === Model Setup ===
llm = ChatOpenAI(model="o1")
# llm = ChatOpenAI(model="gpt-4.5-preview-2025-02-27")

# === File Paths ===
SUMMARY_PATH = Path("text/summary.txt")
OUTPUT_DIR = Path("stark_vision_tools/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TITLES_PATH = OUTPUT_DIR / "titles.json"
DESCRIPTION_PATH = OUTPUT_DIR / "description.txt"
HASHTAGS_PATH = OUTPUT_DIR / "hashtags.txt"

# === Prompt Template ===
prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "You are a YouTube content strategist. Based on a summary of a video, generate the following:\n"
        "1. Five SEO-friendly, clickable YouTube video titles.\n"
        "2. A YouTube video description that is engaging, informative, and around 100–300 words long.\n"
        "3. A list of 5 to 10 relevant hashtags starting with #.\n"
        "Format your response in this structure:\n"
        "TITLES:\n- ...\n- ...\n\nDESCRIPTION:\n...\n\nHASHTAGS:\n#tag1 #tag2 #tag3 ..."
    )),
    ("user", "{context}")
])

# === Load Summary ===
summary_text = SUMMARY_PATH.read_text(encoding="utf-8").strip()

# === Run LLM Chain ===
chain = prompt | llm | StrOutputParser()
result = chain.invoke({"context": summary_text})

# === Parse Output ===
titles = []
description = ""
hashtags = []

mode = None
for line in result.splitlines():
    line = line.strip()
    if line.startswith("TITLES"):
        mode = "titles"
        continue
    elif line.startswith("DESCRIPTION"):
        mode = "description"
        continue
    elif line.startswith("HASHTAGS"):
        mode = "hashtags"
        continue

    if mode == "titles" and line.startswith("-"):
        titles.append(line.lstrip("- ").strip())
    elif mode == "description":
        description += line + "\n"
    elif mode == "hashtags":
        hashtags.extend(tag for tag in line.split() if tag.startswith("#"))

# === Write Output Files ===
TITLES_PATH.write_text(json.dumps(titles, indent=2), encoding="utf-8")
DESCRIPTION_PATH.write_text(description.strip(), encoding="utf-8")
HASHTAGS_PATH.write_text(" ".join(hashtags), encoding="utf-8")

print("✅ title_desc_generator.py complete.")
