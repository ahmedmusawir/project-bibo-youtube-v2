import os
import json
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema.output_parser import StrOutputParser
from src.utils.config import get_prompting_llm

# Load environment variables
load_dotenv()

def parse_metadata_output(raw_text: str) -> dict:
    """Parses the raw LLM output into a structured dictionary."""
    metadata = {
        "titles": [],
        "description": "",
        "hashtags": []
    }
    mode = None
    description_lines = []

    for line in raw_text.splitlines():
        line_stripped = line.strip()
        if line_stripped.startswith("TITLES:"):
            mode = "titles"
            continue
        elif line_stripped.startswith("DESCRIPTION:"):
            mode = "description"
            # Handle case where description is on the same line
            if len(line_stripped) > len("DESCRIPTION:"):
                description_lines.append(line_stripped[len("DESCRIPTION:"):].strip())
            continue
        elif line_stripped.startswith("HASHTAGS:"):
            mode = "hashtags"
            # Handle case where hashtags are on the same line
            if len(line_stripped) > len("HASHTAGS:"):
                metadata["hashtags"].extend(tag for tag in line_stripped[len("HASHTAGS:"):].split() if tag.startswith("#"))
            continue

        if mode == "titles" and line_stripped.startswith("-"):
            metadata["titles"].append(line_stripped.lstrip("- ").strip())
        elif mode == "description":
            description_lines.append(line_stripped)
        elif mode == "hashtags":
            metadata["hashtags"].extend(tag for tag in line_stripped.split() if tag.startswith("#"))
    
    metadata["description"] = "\n".join(description_lines).strip()
    return metadata

def generate_metadata(summary_path: str, output_path: str) -> str:
    """
    Generates YouTube metadata from a summary and saves it to a JSON file.

    Args:
        summary_path (str): The absolute path to the input summary file.
        output_path (str): The absolute path to save the output JSON file.

    Returns:
        str: The path to the saved JSON file.
    """
    print(f"-> Loading summary from: {summary_path}")
    summary_text = Path(summary_path).read_text(encoding="utf-8").strip()

    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a YouTube content strategist. Based on a summary of a video, generate the following:\n"
            "1. Five SEO-friendly, clickable YouTube video titles.\n"
            "2. A YouTube video description that is engaging, informative, and around 100–300 words long.\n"
            "3. A list of 5 to 10 relevant hashtags starting with #.\n"
            "Format your response in this exact structure, with each section header on a new line:\n"
            "TITLES:\n- Title 1\n- Title 2\n\nDESCRIPTION:\nYour description here.\n\nHASHTAGS:\n#tag1 #tag2 #tag3 ..."
        )),
        ("user", "{context}")
    ])

    print("-> Creating metadata generation chain...")
    # Initialize LLM with config-driven model selection
    llm = ChatGoogleGenerativeAI(
        model=get_prompting_llm(),
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.8,
        max_output_tokens=8192,
    )
    chain = prompt | llm | StrOutputParser()

    print("-> Invoking chain to generate metadata...")
    raw_result = chain.invoke({"context": summary_text})

    print("-> Parsing LLM output...")
    parsed_metadata = parse_metadata_output(raw_result)

    # Ensure the output directory exists
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)

    print(f"-> Saving metadata as JSON to: {output_path}")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(parsed_metadata, f, indent=2, ensure_ascii=False)

    print(f"✅ Metadata generation complete. Saved to: {output_path}")
    return output_path

