from pathlib import Path
from langchain_community.document_loaders import TextLoader
from langchain_openai import ChatOpenAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Setup GPT-4.5 preview model
# llm = ChatOpenAI(model="o1")
llm = ChatOpenAI(model="gpt-4.1")
# llm = ChatOpenAI(model="gpt-4.5-preview-2025-02-27")

# File paths
TRANSCRIPT_PATH = Path("text/transcript.txt")
SUMMARY_PATH = Path("text/summary.txt")

def summarize_transcript():
    loader = TextLoader(str(TRANSCRIPT_PATH))
    docs = loader.load()

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            (
                "You are an expert YouTube script editor.\n"
                "Goal: transform raw transcripts into a compelling, documentary-style narration script "
                "that delivers **maximum information in minimum time**.\n\n"
                "🔒 HARD CONSTRAINTS (obey 100%):\n"
                "1. Final script length = 920-950 words (aim ~900). **IF draft > 950 words, TRIM until ≤920.**\n"
                "2. Remove ads, sponsorship pitches, or meta chatter.\n"
                "3. No framing language (e.g., ‘Here is your script’).\n"
                "4. Finish with a conclusive, satisfying statement.\n\n"
                "📑 STRUCTURE:\n"
                "- 1-sentence HOOK that sparks curiosity.\n"
                "- 2-3 short CONTEXT blocks (each ≤120 words) explaining core ideas.\n"
                "- BULLETED ‘Key Takeaways’ section (3-5 bullets, ≤40 words each).\n"
                "- 1-sentence CLOSING that ties everything together.\n\n"
                "🎯 STYLE: concise, vivid, accessible—think ‘mini-doc for busy tech lovers’. "
                "Sprinkle critical stats or comparisons only when they sharpen understanding.\n"
                "TARGET VIEWER: on-the-go professionals who value dense, five-minute knowledge bites.\n"
                "Present clean text because this will be converted into voice audio ... so no [context block 1 ... 2 etc.] or anything like that. add nothing in the text other than the content summary ... no extra instructions at all! "
            )
        ),
        (
            "user",
            "{context}\n\n"
            "REMINDER: 920-950 words total. Trim ruthlessly if longer. But remember 900 should be minimum.Also remember, 900 words NOT tokens. So push it as close to 900 as you can. Do your Best\n"
        )
    ])


    print(f"✅ Starting Summary Chain ... ")
    chain = create_stuff_documents_chain(llm, prompt)
    print(f"✅ Starting to Summarize ...")
    result = chain.invoke({"context": docs})
    SUMMARY_PATH.write_text(result, encoding='utf-8')
    print(f"✅ Summary saved to {SUMMARY_PATH}")

if __name__ == "__main__":
    summarize_transcript()
