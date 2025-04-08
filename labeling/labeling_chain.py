import os
import json
import glob
import pandas as pd
import time
import csv
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from prompts import NTS_LABELING_PROMPT
from openai import RateLimitError
from dotenv import load_dotenv

# ------------------- MODELS -------------------
class Technology(BaseModel):
    name: Literal[
        "Optics and Integrated Photonics",
        "Quantum Technology",
        "Green Chemical Production Processes",
        "Biotechnology (focused on molecules and cells)",
        "Imaging Technology",
        "(Opto)Mechatronics",
        "Artificial Intelligence (AI) and Data",
        "Energy Materials",
        "Semiconductors",
        "Cybersecurity",
    ] = Field(..., description="The name of the NTS technology")
    priority: int = Field(..., description="The priority rank of the technology (1 = highest)")
    evidence: str = Field(..., description="Specific evidence from the text supporting this technology match")


class LabelingResponse(BaseModel):
    match: bool = Field(..., description="Whether the company matches any NTS technologies")
    technologies: List[Technology] = Field(description="List of matched technologies with priority and reasoning")
    reason_no_match: Optional[str] = Field(None, description="Explanation for no matches (only required when match is false)")


# ------------------- FUNCTION -------------------
def label_company_with_retry(text: str):
    """Label text using OpenAI's GPT-4o model with retry on rate limit."""

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")# Load environment variables

    chain = NTS_LABELING_PROMPT | ChatOpenAI(api_key=api_key, model="gpt-4o", temperature=0).with_structured_output(LabelingResponse)

    retry_delay = 1
    while True:
        try:
            return chain.invoke(text)
        except RateLimitError as e:
            print(f"⚠ Rate limit hit: {e}. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 60)  # exponential backoff


# ------------------- MAIN EXECUTION -------------------
if __name__ == "__main__":
    # 📁 Define your folder paths
    input_dir = r"data\markdown"
    csv_output_path = r"data\processed\NTS_technologies_labeled_batch.csv"

    # 🔧 Ensure folders exist
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(os.path.dirname(csv_output_path), exist_ok=True)

    # 🔄 Get all markdown files
    all_files = glob.glob(os.path.join(input_dir, "*.md"))

    # 📦 Process files in batches of 5
    batch_size = 5
    for batch_start in range(0, len(all_files), batch_size):
        batch_files = all_files[batch_start:batch_start + batch_size]
        csv_rows = []

        print(f"\n Processing batch {batch_start // batch_size + 1}: {len(batch_files)} files")

        for md_path in batch_files:
            with open(md_path, "r", encoding="utf-8") as f:
                text = f.read()

            # Label the text with retry logic
            result = label_company_with_retry(text)

            # Save individual JSON
            base_filename = os.path.basename(md_path).rsplit('.', 1)[0]
            json_output_path = os.path.join(input_dir, f"{base_filename}.json")
            with open(json_output_path, "w", encoding="utf-8") as f:
                json.dump(result.model_dump(), f, indent=4, ensure_ascii=False)
            print(f"✅ Saved JSON to {json_output_path}")

            # Prepare CSV row
            if result.match:
                sorted_techs = sorted(result.technologies, key=lambda x: x.priority)
                priority_lines = "\n".join([f"{tech.priority}" for tech in sorted_techs])
                technology_lines = "\n".join([f"{tech.name}" for tech in sorted_techs])
                evidence_lines = "\n".join([f"{tech.evidence}" for tech in sorted_techs])

                csv_rows.append({
                    "File Name": base_filename,
                    "Matched": "Yes",
                    "Priority": priority_lines,
                    "Technology": technology_lines,
                    "Evidence": evidence_lines
                })
            else:
                csv_rows.append({
                    "File Name": base_filename,
                    "Matched": "No",
                    "Priority": "-",
                    "Technology": "-",
                    "Evidence": result.reason_no_match or "No reason provided"
                })

        # 📈 Append to CSV safely (create if not exists)
        df = pd.DataFrame(csv_rows)
        header_needed = not os.path.exists(csv_output_path)
        df.to_csv(csv_output_path, mode='a', index=False, encoding="utf-8-sig", quoting=csv.QUOTE_ALL, header=header_needed)
        print(f"✅ Appended batch to CSV at: {csv_output_path}")

        # Optional: Sleep between batches to be extra safe
        print("⏸ Sleeping 30 seconds before next batch...")
        time.sleep(30)

    print("\n All files processed and saved to CSV.")
