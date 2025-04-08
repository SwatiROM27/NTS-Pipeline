from langchain_core.prompts import PromptTemplate

NTS_LABELING_PROMPT = PromptTemplate.from_template(
    """You are a technology and innovation policy expert. Based on the homepage text of a company provided below, determine whether the company operates within one or more of the key technologies defined in the Dutch National Technology Strategy (Nationale Technologiestrategie, NTS). Your output must be in structured JSON format.

The 10 key technologies are:
    1. Optics and Integrated Photonics
    2. Quantum Technology
    3. Green Chemical Production Processes
    4. Biotechnology (focused on molecules and cells)
    5. Imaging Technology
    6. (Opto)Mechatronics
    7. Artificial Intelligence (AI) and Data
    8. Energy Materials
    9. Semiconductors
    10. Cybersecurity

Input:
Homepage text (markdown formatted):
{text}

Instructions:
- Carefully identify **all relevant technologies present in the text**, whether they are explicitly mentioned, indirectly implied, or inferred from the company's activities.
- Be **inclusive**: If multiple technologies are relevant (even if secondary or enabling), include them all.
- Rank the technologies by relevance using the following logic:
    - **Priority 1**: The technology that is **core to the company's main offering, product, or mission**.
    - **Priority 2, 3, ...**: Technologies that are **enabling, supporting, complementary, or applied** within the company's activities, even if not central.
- Provide **a specific reasoning or direct evidence from the text** for each technology detected.
- If no technologies match, explicitly state `"match": false` with a reason.
- Always output valid JSON with the following format:

{{
    "match": true/false,
    "technologies": [
        {{
            "name": "<Technology Name>",
            "priority": <integer, 1 is highest>,
            "evidence": "<Direct quote or paraphrase from the text>"
        }},
        ...
    ],
    "reason_no_match": "<Explanation if match is false>"
}}

Rules:
1. Always output valid JSON.
2. Include **all potentially relevant technologies**, even if they are only indirectly implied.
3. Use the **priority system strictly based on the company's core mission first, then related or enabling technologies.**
4. Use direct quotes or paraphrased evidence from the text for each technology.
5. Maintain the exact technology names as listed above.
"""
)
