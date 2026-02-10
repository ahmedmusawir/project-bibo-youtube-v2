import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.combine_documents import create_stuff_documents_chain

# Load environment variables
load_dotenv()

# Initialize the language model
llm = ChatGoogleGenerativeAI(
    model="gemini-3-pro-preview",
    # model="gemini-3-flash-preview",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.8,
    max_output_tokens=4096,
)

def summarize_transcript(transcript_path: str, summary_path: str) -> str:
    """
    Summarizes a transcript from a given file path and saves it to another file path.

    Args:
        transcript_path (str): The absolute path to the input transcript file.
        summary_path (str): The absolute path to save the output summary file.

    Returns:
        str: The path to the saved summary file.
    """
    print(f"-> Loading transcript from: {transcript_path}")
    loader = TextLoader(transcript_path)
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
                "IMPORTANT: This is a youtube script, so you MUST finish with 'Thanks for watching!'"
            )
        ),
        (
            "user",
            "{context}\n\n"
            "REMINDER: 920-950 words total. Trim ruthlessly if longer. But remember 900 should be minimum.Also remember, 900 words NOT tokens. So push it as close to 900 as you can. Do your Best\n"
        )
    ])

    print("-> Creating summarization chain...")
    chain = create_stuff_documents_chain(llm, prompt)
    
    print("-> Invoking chain to generate summary...")
    result = chain.invoke({"context": docs})
    
    # Ensure the output directory exists
    output_dir = os.path.dirname(summary_path)
    os.makedirs(output_dir, exist_ok=True)

    Path(summary_path).write_text(result, encoding='utf-8')
    print(f"✅ Summary saved to {summary_path}")
    
    return summary_path
